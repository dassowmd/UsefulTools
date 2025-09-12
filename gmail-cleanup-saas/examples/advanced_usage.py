"""Advanced usage examples for Gmail Cleanup library."""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from gmail_cleanup.lib import (
    CredentialsManager,
    GmailClient,
    RulesEngine,
    EmailProcessor,
    Rule,
    RuleCriteria,
    RuleAction,
    ActionType,
    RuleSet
)


class ProgressTracker:
    """Example progress tracker for processing operations."""
    
    def __init__(self):
        self.start_time = None
        self.last_update = None
    
    def on_progress(self, stats):
        """Progress callback function."""
        now = datetime.now()
        
        if self.start_time is None:
            self.start_time = now
            print(f"Processing started at {now.strftime('%H:%M:%S')}")
        
        if self.last_update is None or (now - self.last_update).seconds >= 5:
            elapsed = (now - self.start_time).total_seconds()
            print(f"[{elapsed:.1f}s] Processed: {stats.processed_messages}, "
                  f"Success: {stats.successful_operations}, "
                  f"Rate: {stats.success_rate:.1f}%")
            self.last_update = now


async def batch_operations_example():
    """Example of batch operations on messages."""
    
    # Setup
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        print("Please authenticate first")
        return
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    # Search for specific messages
    search_result = gmail_client.search_messages(
        query="from:noreply@example.com older_than:30d",
        max_results=50
    )
    
    message_ids = [msg['id'] for msg in search_result.get('messages', [])]
    
    if message_ids:
        print(f"Found {len(message_ids)} messages to process")
        
        # Batch mark as read
        read_result = gmail_client.mark_messages_read(message_ids)
        print(f"Marked {read_result.succeeded} messages as read")
        
        # Batch add label
        label_result = gmail_client.add_labels(message_ids, ["processed"])
        print(f"Added label to {label_result.succeeded} messages")
        
        # Batch move to trash (if needed)
        if input("Move to trash? (y/N): ").lower() == 'y':
            trash_result = gmail_client.move_to_trash(message_ids)
            print(f"Moved {trash_result.succeeded} messages to trash")


async def rule_management_example():
    """Example of advanced rule management."""
    
    # Create rules engine
    rules_engine = RulesEngine()
    rules_engine.create_empty_ruleset(
        "Advanced Rules",
        "Comprehensive email management rules"
    )
    
    # Create multiple rules programmatically
    email_domains = [
        ("newsletters.example.com", "Example Newsletters"),
        ("notifications.service.com", "Service Notifications"),
        ("alerts.monitoring.com", "Monitoring Alerts")
    ]
    
    for domain, name in email_domains:
        rule = Rule(
            id=f"auto_read_{domain.replace('.', '_')}",
            name=f"Auto-read {name}",
            description=f"Automatically mark emails from {domain} as read",
            criteria=RuleCriteria(
                from_domain=domain,
                is_unread=True
            ),
            action=RuleAction(type=ActionType.MARK_READ),
            priority=len(rules_engine.get_rules()) + 1
        )
        
        rules_engine.add_rule(rule)
    
    # Save rules to file
    rules_file = Path("my_rules.json")
    rules_engine.save_rules_to_file(str(rules_file))
    
    print(f"Created {len(rules_engine.get_rules())} rules")
    print(f"Saved to {rules_file}")
    
    # Load and modify rules
    loaded_engine = RulesEngine(str(rules_file))
    
    # Disable a specific rule
    for rule in loaded_engine.get_rules():
        if "monitoring" in rule.name.lower():
            rule.enabled = False
            loaded_engine.update_rule(rule.id, rule)
            print(f"Disabled rule: {rule.name}")
    
    # Export subset of rules
    export_file = Path("exported_rules.json")
    active_rule_ids = [r.id for r in loaded_engine.get_enabled_rules()]
    loaded_engine.export_rules(str(export_file), active_rule_ids)
    
    print(f"Exported {len(active_rule_ids)} active rules to {export_file}")


async def custom_processor_example():
    """Example with custom processing logic."""
    
    class CustomEmailProcessor(EmailProcessor):
        """Custom processor with additional functionality."""
        
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.custom_stats = {
                'rules_processed': 0,
                'high_impact_rules': 0,
                'errors_encountered': []
            }
        
        async def process_rule(self, rule, dry_run=False, max_messages=None):
            """Override to add custom logic."""
            
            # Pre-processing
            print(f"Starting rule: {rule.name}")
            
            # Call parent method
            result = await super().process_rule(rule, dry_run, max_messages)
            
            # Post-processing
            self.custom_stats['rules_processed'] += 1
            
            if len(result.matched_messages) > 100:
                self.custom_stats['high_impact_rules'] += 1
                print(f"High-impact rule: {rule.name} ({len(result.matched_messages)} messages)")
            
            if result.batch_result.errors:
                self.custom_stats['errors_encountered'].extend(result.batch_result.errors)
            
            return result
        
        def get_custom_stats(self):
            """Get custom processing statistics."""
            return self.custom_stats
    
    # Setup
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        print("Please authenticate first")
        return
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    # Load rules
    rules_engine = RulesEngine("examples/rules_examples.json")
    
    # Use custom processor
    processor = CustomEmailProcessor(gmail_client, rules_engine)
    
    # Add progress tracking
    tracker = ProgressTracker()
    processor.add_progress_callback(tracker.on_progress)
    
    # Process rules
    results = await processor.process_all_rules(dry_run=True, max_messages_per_rule=50)
    
    # Display custom stats
    custom_stats = processor.get_custom_stats()
    print(f"\nCustom Statistics:")
    print(f"Rules processed: {custom_stats['rules_processed']}")
    print(f"High-impact rules: {custom_stats['high_impact_rules']}")
    print(f"Errors encountered: {len(custom_stats['errors_encountered'])}")
    
    processor.close()


async def mailbox_monitoring_example():
    """Example of continuous mailbox monitoring."""
    
    # Setup
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        print("Please authenticate first")
        return
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    rules_engine = RulesEngine()
    rules_engine.create_empty_ruleset("Monitoring Rules", "Real-time cleanup")
    
    # Create rule for immediate processing
    immediate_cleanup_rule = Rule(
        id="immediate_cleanup",
        name="Immediate Spam Cleanup",
        description="Immediately delete obvious spam",
        criteria=RuleCriteria(
            has_words="URGENT ACTION REQUIRED",
            is_unread=True
        ),
        action=RuleAction(type=ActionType.DELETE),
        max_messages=10  # Limit for safety
    )
    
    rules_engine.add_rule(immediate_cleanup_rule)
    
    processor = EmailProcessor(gmail_client, rules_engine)
    
    # Simulate monitoring (in real app, this might run as a service)
    print("Starting mailbox monitoring (simulated)...")
    
    for cycle in range(3):  # Simulate 3 monitoring cycles
        print(f"\nMonitoring cycle {cycle + 1}")
        
        # Process rules
        results = await processor.process_all_rules(dry_run=True, max_messages_per_rule=10)
        
        for result in results:
            if result.matched_messages:
                print(f"  Found {len(result.matched_messages)} messages for rule: {result.rule.name}")
        
        # Wait before next cycle (in real app, this might be much longer)
        await asyncio.sleep(2)
    
    print("\nMonitoring stopped")
    processor.close()


async def data_analysis_example():
    """Example of advanced data analysis."""
    
    # Setup
    credentials_manager = CredentialsManager()
    if not credentials_manager.is_authenticated():
        print("Please authenticate first")
        return
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    rules_engine = RulesEngine()
    processor = EmailProcessor(gmail_client, rules_engine)
    
    # Comprehensive analysis
    print("Performing comprehensive mailbox analysis...")
    analysis = await processor.analyze_mailbox(max_messages=1000)
    
    # Generate detailed report
    report = {
        "timestamp": datetime.now().isoformat(),
        "analysis_summary": {
            "total_messages": analysis.get('total_messages', 0),
            "unread_messages": analysis.get('unread_messages', 0),
            "old_messages": analysis.get('old_messages', 0),
            "unique_senders": analysis.get('unique_senders', 0)
        },
        "sender_analysis": analysis.get('top_sender_domains', [])[:20],
        "suggestions": analysis.get('suggestions', []),
        "recommendations": []
    }
    
    # Add custom recommendations
    unread_ratio = analysis.get('unread_messages', 0) / analysis.get('total_messages', 1)
    if unread_ratio > 0.3:
        report["recommendations"].append({
            "priority": "high",
            "type": "unread_management",
            "message": f"High unread ratio ({unread_ratio:.1%}). Consider auto-read rules."
        })
    
    old_ratio = analysis.get('old_messages', 0) / analysis.get('total_messages', 1)
    if old_ratio > 0.5:
        report["recommendations"].append({
            "priority": "medium", 
            "type": "storage_cleanup",
            "message": f"Many old messages ({old_ratio:.1%}). Consider deletion rules."
        })
    
    # Save detailed report
    report_file = Path(f"mailbox_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Detailed report saved to {report_file}")
    
    processor.close()


if __name__ == "__main__":
    print("Gmail Cleanup Library - Advanced Examples")
    print("=" * 50)
    
    examples = [
        ("Batch Operations", batch_operations_example),
        ("Rule Management", rule_management_example),
        ("Custom Processor", custom_processor_example),
        ("Mailbox Monitoring", mailbox_monitoring_example),
        ("Data Analysis", data_analysis_example),
    ]
    
    for name, func in examples:
        print(f"\n--- {name} Example ---")
        try:
            await func()
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print(f"Error in {name}: {e}")
        
        input("\nPress Enter to continue to next example...")
    
    print("\nAll examples completed!")