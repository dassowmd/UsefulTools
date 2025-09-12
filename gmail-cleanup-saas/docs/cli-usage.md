# CLI Usage

The Gmail Cleanup command-line interface provides powerful tools for email management from the terminal.

## Installation and Setup

```bash
# Install Gmail Cleanup
pip install gmail-cleanup

# Setup authentication
gmail-cleanup auth setup

# Login
gmail-cleanup auth login
```

## Command Structure

```
gmail-cleanup [OPTIONS] COMMAND [ARGS]...
```

### Global Options

- `--verbose, -v`: Enable verbose logging
- `--config-dir`: Specify configuration directory path
- `--help`: Show help message

## Commands Overview

### Authentication Commands

```bash
gmail-cleanup auth [COMMAND]
```

#### `auth setup`
Setup OAuth2 authentication credentials.

```bash
# Interactive setup
gmail-cleanup auth setup

# Specify client secrets file
gmail-cleanup auth setup --client-secrets path/to/credentials.json
```

#### `auth login`
Login with Google OAuth2.

```bash
gmail-cleanup auth login
```

#### `auth logout`
Logout and revoke credentials.

```bash
gmail-cleanup auth logout
```

#### `auth status`
Check authentication status.

```bash
gmail-cleanup auth status
```

#### `auth test-connection`
Test Gmail API connection.

```bash
gmail-cleanup auth test-connection
```

### Rules Management

```bash
gmail-cleanup rules [COMMAND]
```

#### `rules list`
List all rules.

```bash
# List all rules
gmail-cleanup rules list

# List rules from specific file
gmail-cleanup rules list --file my-rules.json
```

#### `rules create`
Create a new rule.

```bash
# Create from template
gmail-cleanup rules create --template delete_old_emails

# Specify rules file
gmail-cleanup rules create --template auto_read_notifications --file my-rules.json
```

#### `rules delete`
Delete a rule.

```bash
# Delete by rule ID
gmail-cleanup rules delete rule-id-123

# From specific file
gmail-cleanup rules delete rule-id-123 --file my-rules.json
```

#### `rules templates`
List available rule templates.

```bash
gmail-cleanup rules templates
```

### Processing Commands

```bash
gmail-cleanup run [COMMAND]
```

#### `run all`
Process all enabled rules.

```bash
# Dry run (safe - shows what would happen)
gmail-cleanup run all --dry-run

# Process all rules
gmail-cleanup run all

# Process with limits
gmail-cleanup run all --max-messages 100

# Process specific rule
gmail-cleanup run all --rule-id rule-id-123

# Use specific rules file
gmail-cleanup run all --rules-file my-rules.json
```

**Options:**
- `--dry-run`: Show what would be done without executing
- `--rules-file, -f`: Specify rules file path
- `--rule-id`: Process specific rule only
- `--max-messages`: Limit messages per rule

### Analysis Commands

```bash
gmail-cleanup analyze [COMMAND]
```

#### `analyze mailbox`
Analyze mailbox and provide insights.

```bash
# Basic analysis
gmail-cleanup analyze mailbox

# Analyze more messages
gmail-cleanup analyze mailbox --max-messages 2000
```

**Options:**
- `--max-messages`: Maximum messages to analyze (default: 1000)

### Web Server

```bash
gmail-cleanup web
```

Start the web server for browser-based management.

```bash
# Start on default port (8000)
gmail-cleanup web

# Specify host and port
gmail-cleanup web --host 0.0.0.0 --port 8080

# Enable auto-reload for development
gmail-cleanup web --reload
```

**Options:**
- `--host`: Host to bind to (default: localhost)
- `--port`: Port to bind to (default: 8000)
- `--reload`: Enable auto-reload

## Usage Examples

### Basic Workflow

```bash
# 1. Setup and authenticate
gmail-cleanup auth setup --client-secrets credentials.json
gmail-cleanup auth login

# 2. Analyze your mailbox
gmail-cleanup analyze mailbox

# 3. Create rules from templates
gmail-cleanup rules templates
gmail-cleanup rules create --template delete_old_emails
gmail-cleanup rules create --template auto_read_notifications

# 4. Test rules safely
gmail-cleanup run all --dry-run

# 5. Execute rules
gmail-cleanup run all
```

### Advanced Usage

```bash
# Process specific rule with limits
gmail-cleanup run all --rule-id my-rule-123 --max-messages 50 --dry-run

# Use custom rules file
gmail-cleanup rules list --file /path/to/custom-rules.json
gmail-cleanup run all --rules-file /path/to/custom-rules.json

# Verbose logging for debugging
gmail-cleanup --verbose run all --dry-run

# Custom configuration directory
gmail-cleanup --config-dir /path/to/config auth login
```

### Batch Operations

```bash
# Create multiple rules from templates
for template in delete_old_emails auto_read_notifications delete_newsletters; do
    gmail-cleanup rules create --template $template
done

# Process rules in stages
gmail-cleanup run all --dry-run --max-messages 10  # Test small
gmail-cleanup run all --dry-run --max-messages 100 # Test medium
gmail-cleanup run all                               # Full run
```

## Output Examples

### Rules List Output

```
                    Email Cleanup Rules                     
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ ID       ┃ Name                   ┃ Status    ┃ Priority ┃ Action    ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ a1b2c3d4 │ Delete Old Newsletters │ ✓ Enabled │        1 │ delete    │
│ e5f6g7h8 │ Auto-read Notifications│ ✓ Enabled │        2 │ mark_read │
│ i9j0k1l2 │ Archive Old Receipts   │ ✗ Disabled│        3 │ add_label │
└──────────┴────────────────────────┴───────────┴──────────┴───────────┘
```

### Processing Results Output

```
Processing Results (Executed)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━┓
┃ Rule                          ┃ Matched ┃ Processed ┃ Succeeded ┃ Failed ┃ Duration ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━┩
│ Delete Old Newsletters        │      42 │        42 │        42 │      0 │    2.34s │
│ Auto-read Notifications       │     156 │       156 │       156 │      0 │    4.12s │
│ Archive Old Receipts          │      23 │        23 │        23 │      0 │    1.87s │
└───────────────────────────────┴─────────┴───────────┴───────────┴────────┴──────────┘

Summary:
Total matched: 221
Total processed: 221
Total succeeded: 221
Total failed: 0
```

### Mailbox Analysis Output

```
Mailbox Analysis Results
Analyzed messages: 1000
Unread messages: 234
Old messages (>1 year): 456
Unique senders: 127

Top Sender Domains:
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Domain                   ┃ Count ┃ Percentage ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ notifications.github.com │   145 │      14.5% │
│ newsletter.example.com   │    89 │       8.9% │
│ noreply@service.com      │    67 │       6.7% │
│ alerts@monitoring.com    │    45 │       4.5% │
│ updates@social.com       │    34 │       3.4% │
└──────────────────────────┴───────┴────────────┘

Cleanup Suggestions (3):
1. Auto-read emails from notifications.github.com
   You have 145 notification emails that could be auto-marked as read
2. Clean up emails from newsletter.example.com
   You have 89 newsletter emails. Consider cleaning them up.
3. Clean up old emails
   You have 456 emails older than 1 year
```

## Error Handling

The CLI provides clear error messages and exit codes:

### Exit Codes
- `0`: Success
- `1`: General error
- `2`: Authentication error
- `3`: Configuration error

### Common Error Messages

```bash
# Authentication required
✗ Not authenticated. Run 'gmail-cleanup auth login' first.

# Rule not found
✗ Rule not found: invalid-rule-id

# Rule validation failed
✗ Rule validation failed: Rule must have at least one criteria

# Connection test failed
✗ Connection test failed: Invalid credentials
```

## Configuration

### Environment Variables

```bash
export GMAIL_CLEANUP_CONFIG_DIR="~/.gmail-cleanup"
export GMAIL_CLEANUP_LOG_LEVEL="DEBUG"
export GMAIL_CLEANUP_MAX_WORKERS=8
```

### Config File

Create `~/.gmail-cleanup/config.json`:

```json
{
  "log_level": "INFO",
  "max_workers": 4,
  "default_rules_file": "~/.gmail-cleanup/rules.json",
  "web_host": "localhost",
  "web_port": 8000
}
```

## Tips and Best Practices

### Safety First

1. **Always start with `--dry-run`**:
   ```bash
   gmail-cleanup run all --dry-run
   ```

2. **Test with small limits**:
   ```bash
   gmail-cleanup run all --max-messages 10
   ```

3. **Verify authentication regularly**:
   ```bash
   gmail-cleanup auth status
   ```

### Performance Optimization

1. **Use specific rule IDs for faster processing**:
   ```bash
   gmail-cleanup run all --rule-id specific-rule
   ```

2. **Limit messages for large mailboxes**:
   ```bash
   gmail-cleanup run all --max-messages 500
   ```

3. **Use verbose mode for debugging**:
   ```bash
   gmail-cleanup --verbose run all --dry-run
   ```

### Automation

Create shell scripts for common workflows:

```bash
#!/bin/bash
# daily-cleanup.sh

echo "Starting daily email cleanup..."

# Check authentication
if ! gmail-cleanup auth status >/dev/null 2>&1; then
    echo "Authentication required"
    exit 1
fi

# Run cleanup with safety limits
gmail-cleanup run all --max-messages 100 --dry-run
read -p "Proceed with cleanup? (y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    gmail-cleanup run all --max-messages 100
    echo "Cleanup completed"
else
    echo "Cleanup cancelled"
fi
```

## Integration with Other Tools

### Cron Jobs

```bash
# Add to crontab for daily cleanup
0 9 * * * /usr/local/bin/gmail-cleanup run all --max-messages 50 >> /var/log/gmail-cleanup.log 2>&1
```

### Shell Aliases

```bash
# Add to ~/.bashrc or ~/.zshrc
alias gmc='gmail-cleanup'
alias gmc-status='gmail-cleanup auth status'
alias gmc-dry='gmail-cleanup run all --dry-run'
alias gmc-analyze='gmail-cleanup analyze mailbox'
```

### Systemd Service

Create `/etc/systemd/system/gmail-cleanup.service`:

```ini
[Unit]
Description=Gmail Cleanup Web Service
After=network.target

[Service]
Type=exec
User=gmail-cleanup
ExecStart=/usr/local/bin/gmail-cleanup web --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```