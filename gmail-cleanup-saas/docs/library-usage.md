# Library Usage

Gmail Cleanup provides a powerful Python library for developers who want to integrate email management capabilities into their applications.

## Installation

```bash
# Install the core library
pip install gmail-cleanup

# Install with web dependencies
pip install gmail-cleanup[web]
```

## Quick Start

```python
import asyncio
from gmail_cleanup.lib import (
    CredentialsManager,
    GmailClient,
    RulesEngine,
    EmailProcessor,
    Rule,
    RuleCriteria,
    RuleAction,
    ActionType
)

async def main():
    # Setup authentication
    credentials_manager = CredentialsManager()
    credentials_manager.authenticate()
    
    # Create Gmail client
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    
    # Create and process a simple rule
    rules_engine = RulesEngine()
    rules_engine.create_empty_ruleset("My Rules", "Library example")
    
    rule = Rule(
        id="example_rule",
        name="Delete Old Promotional Emails",
        description="Delete promotional emails older than 7 days",
        criteria=RuleCriteria(
            labels=["CATEGORY_PROMOTIONS"],
            older_than_days=7
        ),
        action=RuleAction(type=ActionType.DELETE)
    )
    
    rules_engine.add_rule(rule)
    
    # Process rules
    processor = EmailProcessor(gmail_client, rules_engine)
    results = await processor.process_all_rules(dry_run=True)
    
    for result in results:
        print(f"Rule '{result.rule.name}' would affect {len(result.matched_messages)} messages")
    
    processor.close()

# Run the example
asyncio.run(main())
```

## Core Components

### Authentication

#### CredentialsManager

The main class for handling Google OAuth2 authentication.

```python
from gmail_cleanup.lib import CredentialsManager, AuthenticationError

# Initialize with custom config directory
credentials_manager = CredentialsManager(config_dir="/path/to/config")

# Setup client configuration
client_config = {
    "installed": {
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
}

credentials_manager.setup_client_config(client_config)

# Authenticate user
try:
    success = credentials_manager.authenticate()
    if success:
        print("Authentication successful")
        user_info = credentials_manager.get_user_info()
        print(f"Logged in as: {user_info['email']}")
    else:
        print("Authentication failed")
except AuthenticationError as e:
    print(f"Authentication error: {e}")

# Check authentication status
if credentials_manager.is_authenticated():
    print("User is authenticated")

# Logout
credentials_manager.logout()
```

#### GoogleAuthManager

Lower-level authentication management.

```python
from gmail_cleanup.lib import GoogleAuthManager

# Create from client secrets file
auth_manager = GoogleAuthManager.from_client_secrets_file(
    "path/to/client_secrets.json"
)

# Get credentials
credentials = auth_manager.get_credentials()

# Test connection
if auth_manager.test_connection():
    print("Connection successful")

# Get user information
user_info = auth_manager.get_user_info()
print(f"Email: {user_info['email']}")
print(f"Total messages: {user_info['messages_total']}")
```

### Gmail Client

#### GmailClient

The main interface for Gmail API operations.

```python
from gmail_cleanup.lib import GmailClient

# Initialize with credentials
gmail_client = GmailClient(credentials)

# Search for messages
search_result = gmail_client.search_messages(
    query="from:noreply@example.com older_than:30d",
    max_results=100
)

message_ids = [msg['id'] for msg in search_result['messages']]
print(f"Found {len(message_ids)} messages")

# Get message details
for message_id in message_ids[:5]:  # First 5 messages
    details = gmail_client.get_message_details(message_id)
    if details:
        print(f"From: {details.sender}")
        print(f"Subject: {details.subject}")
        print(f"Date: {details.date}")

# Batch operations
mark_read_result = gmail_client.mark_messages_read(message_ids)
print(f"Marked {mark_read_result.succeeded} messages as read")

trash_result = gmail_client.move_to_trash(message_ids)
print(f"Moved {trash_result.succeeded} messages to trash")

# Add labels
label_result = gmail_client.add_labels(message_ids, ["processed", "archived"])
print(f"Added labels to {label_result.succeeded} messages")

# Build search queries
query = gmail_client.build_search_query(
    sender="newsletter@example.com",
    older_than_days=30,
    has_attachment=True,
    is_unread=False
)
print(f"Generated query: {query}")
```

#### EmailMessage

Data class representing an email message.

```python
# EmailMessage is returned by get_message_details()
message = gmail_client.get_message_details(message_id)

print(f"ID: {message.id}")
print(f"Thread ID: {message.thread_id}")
print(f"Sender: {message.sender}")
print(f"Recipient: {message.recipient}")
print(f"Subject: {message.subject}")
print(f"Date: {message.date}")
print(f"Labels: {message.labels}")
print(f"Snippet: {message.snippet}")
print(f"Is unread: {message.is_unread}")
```

### Rules System

#### RulesEngine

Manages email filtering rules.

```python
from gmail_cleanup.lib import RulesEngine, RuleValidationError

# Create from file
rules_engine = RulesEngine("rules.json")

# Create empty ruleset
rules_engine = RulesEngine()
rules_engine.create_empty_ruleset("My Rules", "Personal cleanup rules")

# Add rules
rule = Rule(
    id="cleanup_newsletters",
    name="Cleanup Newsletters",
    description="Delete newsletter emails older than 30 days",
    criteria=RuleCriteria(
        has_words="unsubscribe",
        older_than_days=30
    ),
    action=RuleAction(type=ActionType.DELETE)
)

try:
    rules_engine.add_rule(rule)
    print("Rule added successfully")
except RuleValidationError as e:
    print(f"Rule validation failed: {e}")

# List rules
all_rules = rules_engine.get_rules()
enabled_rules = rules_engine.get_enabled_rules()

# Update rule
rule.enabled = False
rules_engine.update_rule(rule.id, rule)

# Remove rule
rules_engine.remove_rule(rule.id)

# Save to file
rules_engine.save_rules_to_file("my_rules.json")

# Import/export
rules_engine.export_rules("exported_rules.json", [rule.id])
imported_count = rules_engine.import_rules("imported_rules.json")
print(f"Imported {imported_count} rules")
```

#### Rule Models

Define email filtering criteria and actions.

```python
from gmail_cleanup.lib import Rule, RuleCriteria, RuleAction, ActionType

# Create rule criteria
criteria = RuleCriteria(
    from_email="noreply@example.com",
    older_than_days=30,
    is_unread=True,
    has_attachment=False,
    labels=["INBOX"],
    exclude_labels=["IMPORTANT"]
)

# Create rule action
action = RuleAction(
    type=ActionType.ADD_LABEL,
    parameters={"labels": ["auto-processed"]}
)

# Create complete rule
rule = Rule(
    id="auto_process_notifications",
    name="Auto-process Notifications",
    description="Add label to unread notification emails",
    criteria=criteria,
    action=action,
    enabled=True,
    priority=5,
    max_messages=100
)

# Convert to/from dictionary
rule_dict = rule.to_dict()
rule_from_dict = Rule.from_dict(rule_dict)
```

#### Rule Templates

Pre-defined rule templates for common scenarios.

```python
from gmail_cleanup.lib import RuleTemplates

# List all templates
templates = RuleTemplates.get_all_templates()
for template in templates:
    print(f"{template['id']}: {template['name']}")

# Get templates by category
marketing_templates = RuleTemplates.get_template_by_category("marketing")
storage_templates = RuleTemplates.get_template_by_category("storage")

# Create rule from template
rule = RuleTemplates.create_rule_from_template(
    "delete_old_emails",
    criteria_older_than_days=180,  # Customize to 6 months
    name="Delete Very Old Emails"
)

# Customize template for specific domain
customized_template = RuleTemplates.customize_domain_template(
    "organize_by_domain",
    "github.com"
)
```

### Email Processing

#### EmailProcessor

High-level email processing with rules.

```python
from gmail_cleanup.lib import EmailProcessor

# Create processor
processor = EmailProcessor(
    gmail_client=gmail_client,
    rules_engine=rules_engine,
    max_workers=4,
    batch_size=100
)

# Add progress callback
def progress_callback(stats):
    print(f"Processed: {stats.processed_messages}")
    print(f"Success rate: {stats.success_rate:.1f}%")

processor.add_progress_callback(progress_callback)

# Process all rules
results = await processor.process_all_rules(
    dry_run=True,
    max_messages_per_rule=500
)

for result in results:
    print(f"Rule: {result.rule.name}")
    print(f"Matched: {len(result.matched_messages)}")
    print(f"Processed: {result.batch_result.processed}")
    print(f"Succeeded: {result.batch_result.succeeded}")
    print(f"Duration: {result.stats.duration}s")

# Process specific rule
rule = rules_engine.get_rule("specific_rule_id")
result = await processor.process_rule(
    rule=rule,
    dry_run=False,
    max_messages=100
)

# Analyze mailbox
analysis = await processor.analyze_mailbox(max_messages=1000)
print(f"Total messages: {analysis['total_messages']}")
print(f"Unread messages: {analysis['unread_messages']}")
print(f"Top senders: {analysis['top_sender_domains'][:5]}")

# Clean up
processor.close()
```

## Advanced Usage

### Custom Processing Logic

```python
class CustomEmailProcessor(EmailProcessor):
    """Custom processor with additional functionality."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_stats = {"high_impact_rules": 0}
    
    async def process_rule(self, rule, dry_run=False, max_messages=None):
        # Pre-processing
        print(f"Starting rule: {rule.name}")
        
        # Call parent method
        result = await super().process_rule(rule, dry_run, max_messages)
        
        # Post-processing
        if len(result.matched_messages) > 100:
            self.custom_stats["high_impact_rules"] += 1
            print(f"High-impact rule: {rule.name}")
        
        return result
```

### Batch Operations

```python
# Search and process in batches
def process_large_mailbox(gmail_client, query, batch_size=500):
    all_message_ids = []
    page_token = None
    
    while True:
        result = gmail_client.search_messages(
            query=query,
            max_results=batch_size,
            page_token=page_token
        )
        
        batch_ids = [msg['id'] for msg in result.get('messages', [])]
        all_message_ids.extend(batch_ids)
        
        # Process batch
        if batch_ids:
            batch_result = gmail_client.mark_messages_read(batch_ids)
            print(f"Processed batch: {batch_result.succeeded}/{len(batch_ids)}")
        
        page_token = result.get('nextPageToken')
        if not page_token:
            break
    
    return all_message_ids
```

### Error Handling

```python
from gmail_cleanup.lib import AuthenticationError, RuleValidationError

try:
    # Authentication
    credentials_manager = CredentialsManager()
    success = credentials_manager.authenticate()
    
    # Rule creation
    rules_engine = RulesEngine()
    rule = Rule(...)  # Invalid rule
    rules_engine.add_rule(rule)
    
    # Processing
    processor = EmailProcessor(gmail_client, rules_engine)
    results = await processor.process_all_rules()
    
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
except RuleValidationError as e:
    print(f"Rule validation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    if 'processor' in locals():
        processor.close()
```

### Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def gmail_processor(credentials_manager, rules_file=None):
    """Async context manager for Gmail processing."""
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    rules_engine = RulesEngine(rules_file)
    processor = EmailProcessor(gmail_client, rules_engine)
    
    try:
        yield processor
    finally:
        processor.close()

# Usage
async def process_emails():
    credentials_manager = CredentialsManager()
    
    async with gmail_processor(credentials_manager, "rules.json") as processor:
        results = await processor.process_all_rules(dry_run=True)
        return results
```

### Configuration Management

```python
import json
from pathlib import Path

class ConfigManager:
    """Manage Gmail Cleanup configuration."""
    
    def __init__(self, config_dir=None):
        self.config_dir = Path(config_dir or "~/.gmail-cleanup").expanduser()
        self.config_file = self.config_dir / "config.json"
    
    def load_config(self):
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file) as f:
                return json.load(f)
        return {}
    
    def save_config(self, config):
        """Save configuration to file."""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_credentials_manager(self):
        """Get configured credentials manager."""
        return CredentialsManager(str(self.config_dir))

# Usage
config_manager = ConfigManager()
config = config_manager.load_config()

# Use with custom settings
credentials_manager = config_manager.get_credentials_manager()
```

## Integration Examples

### Flask Web App

```python
from flask import Flask, jsonify, request
from gmail_cleanup.lib import CredentialsManager, GmailClient, RulesEngine

app = Flask(__name__)
credentials_manager = CredentialsManager()

@app.route('/api/rules')
def list_rules():
    rules_engine = RulesEngine("rules.json")
    rules = rules_engine.get_rules()
    return jsonify([rule.to_dict() for rule in rules])

@app.route('/api/process', methods=['POST'])
async def process_rules():
    if not credentials_manager.is_authenticated():
        return jsonify({"error": "Not authenticated"}), 401
    
    auth_manager = credentials_manager.get_auth_manager()
    credentials = auth_manager.get_credentials()
    gmail_client = GmailClient(credentials)
    rules_engine = RulesEngine("rules.json")
    
    processor = EmailProcessor(gmail_client, rules_engine)
    results = await processor.process_all_rules(dry_run=True)
    
    processor.close()
    
    return jsonify({
        "results": [
            {
                "rule_name": r.rule.name,
                "matched": len(r.matched_messages),
                "processed": r.batch_result.processed
            }
            for r in results
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)
```

### Celery Tasks

```python
from celery import Celery
from gmail_cleanup.lib import CredentialsManager, GmailClient, RulesEngine, EmailProcessor

app = Celery('gmail_cleanup_worker')

@app.task
async def process_user_rules(user_id, rules_config):
    """Background task to process user's email rules."""
    try:
        # Setup user-specific configuration
        credentials_manager = CredentialsManager(f"config/{user_id}")
        
        if not credentials_manager.is_authenticated():
            return {"error": "User not authenticated"}
        
        # Create components
        auth_manager = credentials_manager.get_auth_manager()
        credentials = auth_manager.get_credentials()
        gmail_client = GmailClient(credentials)
        
        rules_engine = RulesEngine()
        rules_engine.create_empty_ruleset("User Rules", "Background processing")
        
        # Add rules from config
        for rule_config in rules_config:
            rule = Rule.from_dict(rule_config)
            rules_engine.add_rule(rule)
        
        # Process
        processor = EmailProcessor(gmail_client, rules_engine)
        results = await processor.process_all_rules(
            dry_run=False,
            max_messages_per_rule=100
        )
        
        # Cleanup
        processor.close()
        
        return {
            "success": True,
            "processed_rules": len(results),
            "total_processed": sum(r.batch_result.processed for r in results)
        }
    
    except Exception as e:
        return {"error": str(e)}
```

### Jupyter Notebook

```python
# Gmail Cleanup in Jupyter
import asyncio
import pandas as pd
from gmail_cleanup.lib import *

# Setup
credentials_manager = CredentialsManager()
if not credentials_manager.is_authenticated():
    print("Please authenticate first")
    # credentials_manager.authenticate()  # Uncomment to authenticate

auth_manager = credentials_manager.get_auth_manager()
credentials = auth_manager.get_credentials()
gmail_client = GmailClient(credentials)

# Analyze mailbox
rules_engine = RulesEngine()
processor = EmailProcessor(gmail_client, rules_engine)

analysis = await processor.analyze_mailbox(max_messages=500)

# Convert to DataFrame for analysis
sender_data = analysis['top_sender_domains']
df = pd.DataFrame(sender_data, columns=['Domain', 'Count'])
df['Percentage'] = (df['Count'] / analysis['total_messages']) * 100

# Display results
print(f"Total messages analyzed: {analysis['total_messages']}")
display(df.head(10))

# Visualize
import matplotlib.pyplot as plt
plt.figure(figsize=(12, 6))
plt.bar(df.head(10)['Domain'], df.head(10)['Count'])
plt.title('Top 10 Email Domains')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

processor.close()
```

## Best Practices

### 1. Resource Management

Always clean up resources:

```python
# Use try/finally
processor = None
try:
    processor = EmailProcessor(gmail_client, rules_engine)
    results = await processor.process_all_rules()
finally:
    if processor:
        processor.close()

# Or use context managers
async with gmail_processor(credentials_manager) as processor:
    results = await processor.process_all_rules()
```

### 2. Error Handling

Handle different types of errors appropriately:

```python
from gmail_cleanup.lib import AuthenticationError, RuleValidationError
from googleapiclient.errors import HttpError

try:
    # Your code here
    pass
except AuthenticationError:
    # Handle authentication issues
    print("Please re-authenticate")
except RuleValidationError as e:
    # Handle rule validation errors
    print(f"Rule error: {e}")
except HttpError as e:
    # Handle Gmail API errors
    if e.resp.status == 429:
        print("Rate limit exceeded - wait and retry")
    else:
        print(f"Gmail API error: {e}")
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {e}")
```

### 3. Performance Optimization

```python
# Use appropriate batch sizes
processor = EmailProcessor(
    gmail_client=gmail_client,
    rules_engine=rules_engine,
    max_workers=4,  # Adjust based on system
    batch_size=100  # Gmail API optimal batch size
)

# Limit processing for testing
results = await processor.process_all_rules(
    max_messages_per_rule=50,  # Limit for testing
    dry_run=True  # Safe testing
)

# Use specific rules when possible
specific_rule = rules_engine.get_rule("target_rule_id")
if specific_rule:
    result = await processor.process_rule(specific_rule)
```

### 4. Security

```python
# Don't log sensitive information
import logging
logging.getLogger("gmail_cleanup").setLevel(logging.INFO)

# Use secure configuration storage
config_dir = Path.home() / ".gmail-cleanup"
config_dir.chmod(0o700)  # Owner only

# Validate user inputs
def validate_rule_data(rule_data):
    required_fields = ["name", "description", "criteria", "action"]
    for field in required_fields:
        if field not in rule_data:
            raise ValueError(f"Missing required field: {field}")
    return True
```

## API Reference

For complete API documentation, see the [API Reference](api-reference.md).

Key classes and methods:

- `CredentialsManager`: Authentication management
- `GmailClient`: Gmail API operations
- `RulesEngine`: Rule management
- `EmailProcessor`: High-level processing
- `Rule`, `RuleCriteria`, `RuleAction`: Rule definitions
- `RuleTemplates`: Pre-defined templates