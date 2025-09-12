"""Basic usage examples for Gmail Cleanup library."""

import asyncio
from gmail_cleanup.lib import (
    CredentialsManager,
    GmailClient, 
    RulesEngine,
    EmailProcessor,
    Rule,
    RuleCriteria,
    RuleAction,
    ActionType,
    RuleTemplates
)


async def basic_example():
    """Basic example of using Gmail Cleanup library."""
    
    # 1. Setup authentication
    credentials_manager = CredentialsManager()
    
    # Check if already authenticated
    if not credentials_manager.is_authenticated():
        print("Please authenticate first:")
        success = credentials_manager.authenticate()
        if not success:
            print("Authentication failed")
            return
    
    # 2. Create Gmail client
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    # 3. Create rules engine
    rules_engine = RulesEngine()
    rules_engine.create_empty_ruleset("My Rules", "Personal email cleanup rules")
    
    # 4. Create a simple rule
    rule = Rule(
        id="delete_old_newsletters",
        name="Delete old newsletters",
        description="Delete newsletter emails older than 30 days",
        criteria=RuleCriteria(
            has_words="unsubscribe",
            older_than_days=30
        ),
        action=RuleAction(
            type=ActionType.DELETE
        )
    )
    
    rules_engine.add_rule(rule)
    
    # 5. Process rules
    processor = EmailProcessor(gmail_client, rules_engine)
    
    # First, do a dry run to see what would happen
    print("Running dry run...")
    results = await processor.process_all_rules(dry_run=True)
    
    for result in results:
        print(f"Rule '{result.rule.name}' would affect {len(result.matched_messages)} messages")
    
    # Ask for confirmation before actual processing
    if input("Proceed with actual cleanup? (y/N): ").lower() == 'y':
        print("Processing rules...")
        results = await processor.process_all_rules(dry_run=False)
        
        for result in results:
            print(f"Rule '{result.rule.name}': {result.batch_result.succeeded} processed successfully")
    
    # Cleanup
    processor.close()


async def template_example():
    """Example using rule templates."""
    
    # Setup (same as basic example)
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        credentials_manager.authenticate()
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    rules_engine = RulesEngine()
    rules_engine.create_empty_ruleset("Template Rules", "Rules from templates")
    
    # Create rule from template
    rule = RuleTemplates.create_rule_from_template(
        "delete_old_emails",
        criteria_older_than_days=180,  # Customize to 6 months
        name="Delete very old emails"
    )
    
    rules_engine.add_rule(rule)
    
    # Process
    processor = EmailProcessor(gmail_client, rules_engine)
    results = await processor.process_all_rules(dry_run=True)
    
    for result in results:
        print(f"Template rule would process {len(result.matched_messages)} messages")
    
    processor.close()


async def analysis_example():
    """Example of mailbox analysis."""
    
    # Setup
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        credentials_manager.authenticate()
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    rules_engine = RulesEngine()
    processor = EmailProcessor(gmail_client, rules_engine)
    
    # Analyze mailbox
    print("Analyzing mailbox...")
    analysis = await processor.analyze_mailbox(max_messages=500)
    
    print(f"Total messages analyzed: {analysis.get('total_messages', 0)}")
    print(f"Unread messages: {analysis.get('unread_messages', 0)}")
    print(f"Old messages: {analysis.get('old_messages', 0)}")
    
    print("\nTop sender domains:")
    for domain, count in analysis.get('top_sender_domains', [])[:5]:
        print(f"  {domain}: {count} messages")
    
    # Get suggestions
    suggestions = analysis.get('suggestions', [])
    if suggestions:
        print(f"\nCleanup suggestions ({len(suggestions)}):")
        for suggestion in suggestions[:3]:
            print(f"  - {suggestion.get('title', 'Unknown suggestion')}")
    
    processor.close()


async def custom_search_example():
    """Example of custom message searching."""
    
    # Setup
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        credentials_manager.authenticate()
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    # Search for specific messages
    query = gmail_client.build_search_query(
        sender="noreply@github.com",
        older_than_days=30,
        is_unread=True
    )
    
    print(f"Search query: {query}")
    
    search_result = gmail_client.search_messages(
        query=query,
        max_results=10
    )
    
    message_ids = [msg['id'] for msg in search_result.get('messages', [])]
    print(f"Found {len(message_ids)} messages")
    
    # Get details for first few messages
    for message_id in message_ids[:3]:
        details = gmail_client.get_message_details(message_id)
        if details:
            print(f"  - {details.sender}: {details.subject}")


if __name__ == "__main__":
    print("Gmail Cleanup Library Examples")
    print("=" * 40)
    
    print("\n1. Basic Usage Example")
    asyncio.run(basic_example())
    
    print("\n2. Template Usage Example")
    asyncio.run(template_example())
    
    print("\n3. Mailbox Analysis Example") 
    asyncio.run(analysis_example())
    
    print("\n4. Custom Search Example")
    asyncio.run(custom_search_example())