import imaplib
import datetime
import json
import logging
import re
from collections import Counter
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Gmail IMAP OAuth2 scope - full mailbox access
SCOPES = ['https://mail.google.com/']

# Path to OAuth credentials and token
CREDENTIALS_FILE = Path(__file__).parent / 'credentials.json'
TOKEN_FILE = Path(__file__).parent / 'token.json'
CONFIG_FILE = Path(__file__).parent / 'gmail_cleanup_config.json'

# Default config structure (new format with metadata)
DEFAULT_CONFIG = {
    "trash_rules": {},        # {sender: {added, last_ran, last_hit}}
    "mark_read_rules": {},    # {sender: {added, last_ran, last_hit}}
    "exclude_senders": [],    # Simple list - no tracking needed
}

# Minimum hours between running the same rule
RULE_COOLDOWN_HOURS = 24


def migrate_config(config):
    """Migrate old list-based config to new dict-based format with metadata."""
    migrated = False
    now = datetime.datetime.now().isoformat()

    # Migrate trash_senders -> trash_rules
    if "trash_senders" in config and isinstance(config.get("trash_senders"), list):
        config["trash_rules"] = {}
        for sender in config["trash_senders"]:
            config["trash_rules"][sender] = {
                "added": now,
                "last_ran": None,
                "last_hit": None
            }
        del config["trash_senders"]
        migrated = True

    # Migrate mark_read_senders -> mark_read_rules
    if "mark_read_senders" in config and isinstance(config.get("mark_read_senders"), list):
        config["mark_read_rules"] = {}
        for sender in config["mark_read_senders"]:
            config["mark_read_rules"][sender] = {
                "added": now,
                "last_ran": None,
                "last_hit": None
            }
        del config["mark_read_senders"]
        migrated = True

    # Ensure new keys exist
    if "trash_rules" not in config:
        config["trash_rules"] = {}
    if "mark_read_rules" not in config:
        config["mark_read_rules"] = {}
    if "exclude_senders" not in config:
        config["exclude_senders"] = []

    return config, migrated


def load_config():
    """Load config from file, migrating if needed."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            config = json.load(f)
            config, migrated = migrate_config(config)
            if migrated:
                logger.info("Migrated config to new format with metadata")
                save_config(config)
            return config
    return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save config to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    logger.info(f"Config saved to {CONFIG_FILE}")


def get_oauth2_credentials():
    """Get OAuth2 credentials, refreshing or creating new ones as needed."""
    creds = None

    # Load existing token if available
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Refreshing OAuth2 token...")
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                logger.error(f"ERROR: {CREDENTIALS_FILE} not found!")
                print("\nTo set up OAuth2 authentication:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a new project (or select existing)")
                print("3. Enable the Gmail API")
                print("4. Go to APIs & Services > Credentials")
                print("5. Create OAuth 2.0 Client ID (Desktop app)")
                print("6. Download the JSON and save as 'credentials.json' in this folder")
                raise FileNotFoundError("credentials.json required for OAuth2")

            logger.info("Opening browser for Google OAuth2 authorization...")
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
            logger.info(f"Token saved to {TOKEN_FILE}")

    return creds


def generate_oauth2_string(username, access_token):
    """Generate XOAUTH2 authentication string for IMAP."""
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return auth_string


def connect_imap():
    """Connect to Gmail IMAP using OAuth2 authentication."""
    logger.info("Connecting to mailbox via IMAP...")

    # Get OAuth2 credentials
    creds = get_oauth2_credentials()

    # Get the email address from the token info
    # User needs to provide their email since it's not in the credentials
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE) as f:
            token_data = json.load(f)
            # Try to get email from token, otherwise ask
            username = token_data.get('_email')
    else:
        username = None

    if not username:
        username = input("Enter your Gmail address: ")
        # Save the email to token file for future use
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE) as f:
                token_data = json.load(f)
            token_data['_email'] = username
            with open(TOKEN_FILE, 'w') as f:
                json.dump(token_data, f)

    # Connect to Gmail IMAP
    m = imaplib.IMAP4_SSL("imap.gmail.com")

    # Authenticate using XOAUTH2
    auth_string = generate_oauth2_string(username, creds.token)
    m.authenticate('XOAUTH2', lambda x: auth_string.encode())

    logger.info(f"Successfully authenticated as {username}")
    return m


def mark_read(m, folder, from_string):
    try:
        m.select(f'"{folder}"')

        typ, data = m.search(
            None, '(FROM "{0}" UNSEEN)'.format(from_string)
        )

        if data[0]:
            msg_ids = data[0].decode() if isinstance(data[0], bytes) else data[0]
            count = len(msg_ids.split())
            logger.info(f"Found {count} unread messages from {from_string}")
            # Batch operation: comma-separated IDs
            msg_set = msg_ids.replace(' ', ',')
            m.store(msg_set, "+FLAGS", "\\Seen")
            logger.info(f"Marked {count} messages as read from {from_string}")
            return count
        else:
            logger.debug(f"No unread messages from {from_string}")
        return None
    except Exception as e:
        logger.error(f"Error processing {from_string}: {e}")


def move_to_trash_before_date(m, folder, days_before):
    try:
        no_of_msgs = int(
            m.select(f'"{folder}"')[1][0]
        )  # required to perform search, m.list() for all lables, '[Gmail]/Sent Mail'
        # print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

        before_date = (
            datetime.date.today() - datetime.timedelta(days_before)
        ).strftime(
            "%d-%b-%Y"
        )  # date string, 04-Jan-2013
        typ, data = m.search(
            None, "(BEFORE {0})".format(before_date)
        )  # search pointer for msgs before before_date

        if data != [""]:  # if not empty list means messages exist
            no_msgs_del = data[0].split()[-1]  # last msg id in the list
            # print("- Marked {0} messages for removal with dates before {1} in '{2}'.".format(no_msgs_del, before_date, folder))
            m.store(
                "1:{0}".format(no_msgs_del), "+X-GM-LABELS", "\\Trash"
            )  # move to trash
            # print("Deleted {0} messages.".format(no_msgs_del))
        # else:
        # print("- Nothing to remove.")

        return
    except Exception as e:
        logger.error(f"Error in move_to_trash_before_date: {e}")


def move_to_trash_from(m, folder, from_string):
    try:
        m.select(f'"{folder}"')

        typ, data = m.search(
            None, '(OR (TO "{0}") (FROM "{0}"))'.format(from_string)
        )

        if data[0]:
            msg_ids = data[0].decode() if isinstance(data[0], bytes) else data[0]
            count = len(msg_ids.split())
            logger.info(f"Found {count} messages matching {from_string}")
            # Batch operation: comma-separated IDs
            msg_set = msg_ids.replace(' ', ',')
            m.store(msg_set, "+X-GM-LABELS", "\\Trash")
            logger.info(f"Moved {count} messages to trash from {from_string}")
            return count
        else:
            logger.debug(f"No messages matching {from_string}")
        return None
    except Exception as e:
        logger.error(f"Error processing {from_string}: {e}")


def empty_folder(m, folder, do_expunge=True):
    # print("- Empty '{0}' & Expunge all mail...".format(folder))
    m.select(f'"{folder}"')  # select all trash
    m.store("1:*", "+FLAGS", "\\Deleted")  # Flag all Trash as Deleted
    if do_expunge:  # See Gmail Settings -> Forwarding and POP/IMAP -> Auto-Expunge
        m.expunge()  # not need if auto-expunge enabled
    # else:
    #     print("Expunge was skipped.")


def disconnect_imap(m):
    logger.info("Closing connection & logging out...")
    m.close()
    m.logout()
    logger.info("Disconnected from IMAP")
    return


# ============== Analysis Functions ==============

def extract_email_address(from_header):
    """Extract just the email address from a From header."""
    if not from_header:
        return "unknown"
    # Try to find email in angle brackets first
    match = re.search(r'<([^>]+)>', from_header)
    if match:
        return match.group(1).lower()
    # Otherwise treat the whole thing as an email
    return from_header.strip().lower()


def extract_domain(email_addr):
    """Extract domain from an email address."""
    if '@' in email_addr:
        return email_addr.split('@')[1]
    return email_addr


def get_sender_counts(m, folder, search_criteria="ALL", limit=50):
    """Fetch emails matching criteria and count by sender."""
    try:
        m.select(f'"{folder}"', readonly=True)
        typ, data = m.search(None, search_criteria)

        if data == [b''] or not data[0]:
            return [], 0

        msg_ids = data[0].split()
        total_count = len(msg_ids)
        sender_counter = Counter()

        logger.info(f"Analyzing {total_count} messages...")

        # Fetch headers for all messages (in batches for efficiency)
        batch_size = 500
        for i in range(0, len(msg_ids), batch_size):
            batch = msg_ids[i:i + batch_size]
            msg_set = b','.join(batch)
            typ, msg_data = m.fetch(msg_set, '(BODY.PEEK[HEADER.FIELDS (FROM)])')

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    header_data = response_part[1]
                    if isinstance(header_data, bytes):
                        header_data = header_data.decode('utf-8', errors='ignore')
                    # Parse the From header
                    from_match = re.search(r'From:\s*(.+)', header_data, re.IGNORECASE)
                    if from_match:
                        sender = extract_email_address(from_match.group(1))
                        sender_counter[sender] += 1

            if i + batch_size < len(msg_ids):
                logger.info(f"Processed {i + batch_size}/{total_count}...")

        # Return top senders
        return sender_counter.most_common(limit), total_count
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        return [], 0


def analyze_top_senders(m, folder="[Gmail]/All Mail", limit=50):
    """Analyze top senders by email volume."""
    print(f"\n{'='*60}")
    print("ANALYZING TOP SENDERS BY VOLUME")
    print(f"{'='*60}")
    results, total = get_sender_counts(m, folder, "ALL", limit)
    return results, total


def analyze_unread_by_sender(m, folder="[Gmail]/All Mail", limit=50):
    """Analyze senders with most unread emails."""
    print(f"\n{'='*60}")
    print("ANALYZING UNREAD EMAILS BY SENDER")
    print(f"{'='*60}")
    results, total = get_sender_counts(m, folder, "UNSEEN", limit)
    return results, total


def analyze_old_emails(m, folder="[Gmail]/All Mail", days_threshold=365, limit=50):
    """Analyze old emails by sender."""
    print(f"\n{'='*60}")
    print(f"ANALYZING EMAILS OLDER THAN {days_threshold} DAYS")
    print(f"{'='*60}")
    before_date = (datetime.date.today() - datetime.timedelta(days_threshold)).strftime("%d-%b-%Y")
    results, total = get_sender_counts(m, folder, f"BEFORE {before_date}", limit)
    return results, total


def print_analysis_report(results, total, title):
    """Print a formatted analysis report."""
    print(f"\n{title}")
    print(f"Total messages analyzed: {total}")
    print("-" * 60)
    print(f"{'Rank':<6}{'Count':<10}{'Sender'}")
    print("-" * 60)

    for i, (sender, count) in enumerate(results, 1):
        # Truncate long sender addresses
        display_sender = sender[:45] + "..." if len(sender) > 48 else sender
        print(f"{i:<6}{count:<10}{display_sender}")

    print("-" * 60)


def should_run_rule(rule_meta):
    """Check if a rule should run based on cooldown period."""
    if not rule_meta.get("last_ran"):
        return True

    try:
        last_ran = datetime.datetime.fromisoformat(rule_meta["last_ran"])
        hours_since = (datetime.datetime.now() - last_ran).total_seconds() / 3600
        return hours_since >= RULE_COOLDOWN_HOURS
    except (ValueError, TypeError):
        return True


def run_cleanup(m_con, config):
    """Run cleanup rules from config with cooldown and tracking."""
    folder = "[Gmail]/All Mail"
    now = datetime.datetime.now().isoformat()

    trash_rules = config.get("trash_rules", {})
    mark_read_rules = config.get("mark_read_rules", {})

    # Stats
    ran_count = 0
    skipped_count = 0
    hit_count = 0

    # Move to trash
    logger.info(f"Processing {len(trash_rules)} trash rules...")
    for sender, meta in trash_rules.items():
        if not should_run_rule(meta):
            skipped_count += 1
            logger.debug(f"Skipping {sender} (ran recently)")
            continue

        result = move_to_trash_from(m_con, folder, sender)
        meta["last_ran"] = now
        ran_count += 1

        if result and result > 0:
            meta["last_hit"] = now
            hit_count += 1

    # Mark as read
    logger.info(f"Processing {len(mark_read_rules)} mark-read rules...")
    for sender, meta in mark_read_rules.items():
        if not should_run_rule(meta):
            skipped_count += 1
            logger.debug(f"Skipping {sender} (ran recently)")
            continue

        result = mark_read(m_con, folder, sender)
        meta["last_ran"] = now
        ran_count += 1

        if result and result > 0:
            meta["last_hit"] = now
            hit_count += 1

    # Save updated metadata
    save_config(config)

    logger.info(f"Cleanup complete: {ran_count} rules ran, {skipped_count} skipped (cooldown), {hit_count} matched emails")


def filter_results_by_config(results, config):
    """Filter out senders that are already in any config list."""
    all_configured = set()
    all_configured.update(config.get("trash_rules", {}).keys())
    all_configured.update(config.get("mark_read_rules", {}).keys())
    all_configured.update(config.get("exclude_senders", []))

    filtered = [(sender, count) for sender, count in results if sender not in all_configured]
    return filtered


def print_filtered_results(results, config):
    """Print results filtered by config, showing only unconfigured senders."""
    filtered = filter_results_by_config(results, config)

    if not filtered:
        print("\nAll senders from the analysis are already in your config lists.")
        return []

    skipped = len(results) - len(filtered)
    if skipped > 0:
        print(f"\n(Hiding {skipped} senders already in your config)")

    print("-" * 60)
    print(f"{'#':<6}{'Count':<10}{'Sender'}")
    print("-" * 60)

    for i, (sender, count) in enumerate(filtered, 1):
        display_sender = sender[:45] + "..." if len(sender) > 48 else sender
        print(f"{i:<6}{count:<10}{display_sender}")

    print("-" * 60)
    return filtered


def add_senders_from_results(filtered_results, config, list_type="trash_rules"):
    """Let user select senders from filtered results to add to config."""
    if not filtered_results:
        return False

    print("\nEnter numbers to add (comma-separated), 'all' for all, or 'none' to skip:")
    print("Example: 1,3,5 or 1-10 or all")

    selection = input("Selection: ").strip().lower()

    if selection == "none" or selection == "":
        return False

    indices = set()
    if selection == "all":
        indices = set(range(len(filtered_results)))
    else:
        for part in selection.split(","):
            part = part.strip()
            if "-" in part:
                start, end = part.split("-")
                indices.update(range(int(start) - 1, int(end)))
            else:
                indices.add(int(part) - 1)

    added = 0
    now = datetime.datetime.now().isoformat()

    # Handle exclude_senders as a simple list
    if list_type == "exclude_senders":
        target_list = config.get(list_type, [])
        for idx in sorted(indices):
            if 0 <= idx < len(filtered_results):
                sender = filtered_results[idx][0]
                target_list.append(sender)
                added += 1
                print(f"  Added: {sender}")
        config[list_type] = target_list
    else:
        # Handle trash_rules and mark_read_rules as dicts with metadata
        target_dict = config.get(list_type, {})
        for idx in sorted(indices):
            if 0 <= idx < len(filtered_results):
                sender = filtered_results[idx][0]
                target_dict[sender] = {
                    "added": now,
                    "last_ran": None,
                    "last_hit": None
                }
                added += 1
                print(f"  Added: {sender}")
        config[list_type] = target_dict

    if added > 0:
        save_config(config)
        print(f"\nAdded {added} sender(s) to {list_type}")
    return added > 0


def format_date(iso_date):
    """Format ISO date for display, or return 'Never' if None."""
    if not iso_date:
        return "Never"
    try:
        dt = datetime.datetime.fromisoformat(iso_date)
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return "Unknown"


def print_rules_with_metadata(rules_dict, title):
    """Print rules with their metadata."""
    print(f"\n--- {title} ---")
    if not rules_dict:
        print("  (no rules)")
        return []

    print(f"{'#':<4} {'Sender':<40} {'Last Ran':<18} {'Last Hit':<18}")
    print("-" * 82)

    senders = list(rules_dict.keys())
    for i, sender in enumerate(senders, 1):
        meta = rules_dict[sender]
        display_sender = sender[:38] + ".." if len(sender) > 40 else sender
        last_ran = format_date(meta.get("last_ran"))
        last_hit = format_date(meta.get("last_hit"))
        print(f"{i:<4} {display_sender:<40} {last_ran:<18} {last_hit:<18}")

    return senders


def manage_rules(config):
    """Menu for managing cleanup rules."""
    while True:
        print("\n" + "="*60)
        print("MANAGE RULES")
        print("="*60)
        print(f"Trash rules: {len(config.get('trash_rules', {}))}")
        print(f"Mark-read rules: {len(config.get('mark_read_rules', {}))}")
        print(f"Excluded (protected): {len(config.get('exclude_senders', []))}")
        print("-"*60)
        print("1. View trash rules")
        print("2. View mark-read rules")
        print("3. View excluded senders")
        print("4. Add sender to trash list")
        print("5. Add sender to mark-read list")
        print("6. Add sender to exclude list")
        print("7. Remove sender from a list")
        print("8. View stale rules (no hits in 90+ days)")
        print("9. Return to main menu")
        print("-"*60)

        choice = input("Select option (1-9): ").strip()

        if choice == "1":
            print_rules_with_metadata(config.get("trash_rules", {}), "TRASH RULES")
        elif choice == "2":
            print_rules_with_metadata(config.get("mark_read_rules", {}), "MARK-READ RULES")
        elif choice == "3":
            print("\n--- EXCLUDED (PROTECTED) ---")
            for i, s in enumerate(config.get("exclude_senders", []), 1):
                print(f"{i}. {s}")
        elif choice == "4":
            sender = input("Enter sender/domain to trash: ").strip()
            if sender:
                now = datetime.datetime.now().isoformat()
                config.setdefault("trash_rules", {})[sender] = {
                    "added": now, "last_ran": None, "last_hit": None
                }
                save_config(config)
        elif choice == "5":
            sender = input("Enter sender to mark as read: ").strip()
            if sender:
                now = datetime.datetime.now().isoformat()
                config.setdefault("mark_read_rules", {})[sender] = {
                    "added": now, "last_ran": None, "last_hit": None
                }
                save_config(config)
        elif choice == "6":
            sender = input("Enter sender to protect (exclude): ").strip()
            if sender:
                config.setdefault("exclude_senders", []).append(sender)
                save_config(config)
        elif choice == "7":
            print("Which list? (1=trash, 2=mark-read, 3=exclude)")
            list_choice = input("List: ").strip()
            if list_choice == "1":
                senders = print_rules_with_metadata(config.get("trash_rules", {}), "TRASH RULES")
                if senders:
                    idx = input("Enter number to remove: ").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(senders):
                        removed = senders[int(idx) - 1]
                        del config["trash_rules"][removed]
                        save_config(config)
                        print(f"Removed: {removed}")
            elif list_choice == "2":
                senders = print_rules_with_metadata(config.get("mark_read_rules", {}), "MARK-READ RULES")
                if senders:
                    idx = input("Enter number to remove: ").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(senders):
                        removed = senders[int(idx) - 1]
                        del config["mark_read_rules"][removed]
                        save_config(config)
                        print(f"Removed: {removed}")
            elif list_choice == "3":
                items = config.get("exclude_senders", [])
                for i, s in enumerate(items, 1):
                    print(f"{i}. {s}")
                if items:
                    idx = input("Enter number to remove: ").strip()
                    if idx.isdigit() and 0 < int(idx) <= len(items):
                        removed = items.pop(int(idx) - 1)
                        save_config(config)
                        print(f"Removed: {removed}")
        elif choice == "8":
            # Find stale rules (no hits in 90+ days)
            print("\n--- STALE RULES (no hits in 90+ days) ---")
            stale_cutoff = datetime.datetime.now() - datetime.timedelta(days=90)
            stale_count = 0
            for rule_type in ["trash_rules", "mark_read_rules"]:
                for sender, meta in config.get(rule_type, {}).items():
                    last_hit = meta.get("last_hit")
                    if not last_hit:
                        print(f"  [{rule_type}] {sender} - Never hit")
                        stale_count += 1
                    else:
                        try:
                            hit_date = datetime.datetime.fromisoformat(last_hit)
                            if hit_date < stale_cutoff:
                                print(f"  [{rule_type}] {sender} - Last hit: {format_date(last_hit)}")
                                stale_count += 1
                        except (ValueError, TypeError):
                            pass
            if stale_count == 0:
                print("  No stale rules found!")
        elif choice == "9":
            break


def run_analysis_with_add(m, config):
    """Run analysis and offer to add results to config."""
    folder = "[Gmail]/All Mail"

    while True:
        print("\n" + "="*60)
        print("EMAIL ANALYSIS MENU")
        print("="*60)
        print("1. Top senders by volume")
        print("2. Top senders of unread emails")
        print("3. Top senders of old emails (>1 year)")
        print("4. Run all analyses")
        print("5. Return to main menu")
        print("-"*60)

        choice = input("Select analysis (1-5): ").strip()
        results = None

        if choice == "1":
            results, total = analyze_top_senders(m, folder)
            print_analysis_report(results, total, "TOP SENDERS BY VOLUME")
        elif choice == "2":
            results, total = analyze_unread_by_sender(m, folder)
            print_analysis_report(results, total, "TOP SENDERS OF UNREAD EMAILS")
        elif choice == "3":
            results, total = analyze_old_emails(m, folder, days_threshold=365)
            print_analysis_report(results, total, "TOP SENDERS OF OLD EMAILS (>1 YEAR)")
        elif choice == "4":
            results1, total1 = analyze_top_senders(m, folder)
            print_analysis_report(results1, total1, "TOP SENDERS BY VOLUME")
            results2, total2 = analyze_unread_by_sender(m, folder)
            print_analysis_report(results2, total2, "TOP SENDERS OF UNREAD EMAILS")
            results3, total3 = analyze_old_emails(m, folder, days_threshold=365)
            print_analysis_report(results3, total3, "TOP SENDERS OF OLD EMAILS (>1 YEAR)")
            results = None  # Don't prompt for combined
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please select 1-5.")
            continue

        # Offer to add results to config
        if results:
            print("\nAdd senders to cleanup rules?")
            print("1. Add to trash list")
            print("2. Add to mark-read list")
            print("3. Add to exclude (protect) list")
            print("4. Skip")
            add_choice = input("Choice: ").strip()
            if add_choice in ("1", "2", "3"):
                # Show filtered list (excludes senders already in any list)
                filtered = print_filtered_results(results, config)
                if filtered:
                    list_map = {"1": "trash_rules", "2": "mark_read_rules", "3": "exclude_senders"}
                    add_senders_from_results(filtered, config, list_map[add_choice])


if __name__ == "__main__":
    # Load config
    config = load_config()
    logger.info(f"Loaded config: {len(config.get('trash_rules', {}))} trash rules, "
                f"{len(config.get('mark_read_rules', {}))} mark-read rules, "
                f"{len(config.get('exclude_senders', []))} excluded")

    m_con = connect_imap()

    while True:
        print("\n" + "="*60)
        print("GMAIL CLEANUP TOOL")
        print("="*60)
        print("1. Analyze emails (find cleanup candidates)")
        print("2. Run cleanup (execute rules from config)")
        print("3. Manage rules")
        print("4. Exit")
        print("-"*60)

        choice = input("Select option (1-4): ").strip()

        if choice == "1":
            run_analysis_with_add(m_con, config)
        elif choice == "2":
            run_cleanup(m_con, config)
        elif choice == "3":
            manage_rules(config)
        elif choice == "4":
            break
        else:
            print("Invalid choice. Please select 1-4.")

    disconnect_imap(m_con)
