# Getting Started

This guide will help you install and set up Gmail Cleanup for the first time.

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
# Install the basic package
pip install gmail-cleanup

# Or install with web interface support
pip install gmail-cleanup[web]

# Or install with all optional dependencies
pip install gmail-cleanup[web,dev]
```

### Option 2: Install from Source

```bash
git clone https://github.com/yourusername/gmail-cleanup.git
cd gmail-cleanup
pip install -e .
```

## Prerequisites

### Google API Setup

Before using Gmail Cleanup, you need to set up a Google Cloud Project with Gmail API access:

1. **Create a Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Gmail API**
   - Navigate to "APIs & Services" → "Library"
   - Search for "Gmail API" and enable it

3. **Create OAuth2 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop application"
   - Download the JSON file

### System Requirements

- Python 3.8 or higher
- Internet connection for Gmail API access
- Web browser for OAuth2 authentication

## First-Time Setup

### 1. Install Gmail Cleanup

```bash
pip install gmail-cleanup
```

### 2. Setup Authentication

```bash
# Setup OAuth2 credentials
gmail-cleanup auth setup --client-secrets path/to/your/credentials.json

# Authenticate with Google
gmail-cleanup auth login
```

### 3. Verify Installation

```bash
# Check authentication status
gmail-cleanup auth status

# Test Gmail connection
gmail-cleanup auth test-connection
```

## Basic Usage

### CLI Quick Start

```bash
# Analyze your mailbox
gmail-cleanup analyze mailbox

# List available rule templates
gmail-cleanup rules templates

# Create a rule from template
gmail-cleanup rules create --template delete_old_emails

# Run all rules (dry run first)
gmail-cleanup run all --dry-run

# Execute rules
gmail-cleanup run all
```

### Web Interface Quick Start

```bash
# Start the web server
gmail-cleanup web --host localhost --port 8000

# Open http://localhost:8000 in your browser
```

## Configuration

### Configuration Files

Gmail Cleanup stores configuration in `~/.gmail-cleanup/`:

```
~/.gmail-cleanup/
├── client_secrets.json    # OAuth2 client configuration
├── token.json            # User authentication tokens
└── rules.json           # Email cleanup rules (optional)
```

### Environment Variables

You can customize behavior with environment variables:

```bash
export GMAIL_CLEANUP_CONFIG_DIR="~/.gmail-cleanup"
export GMAIL_CLEANUP_LOG_LEVEL="INFO"
export GMAIL_CLEANUP_MAX_WORKERS=4
```

## Your First Rule

Let's create your first email cleanup rule:

### Using the CLI

```bash
# Create a rule to delete old promotional emails
gmail-cleanup rules create --template delete_promotional
```

### Using Python Library

```python
from gmail_cleanup.lib import (
    CredentialsManager,
    GmailClient,
    RulesEngine,
    Rule,
    RuleCriteria,
    RuleAction,
    ActionType
)

# Setup authentication
credentials_manager = CredentialsManager()
credentials_manager.authenticate()

# Create Gmail client
auth_manager = credentials_manager.get_auth_manager()
credentials = auth_manager.get_credentials()
gmail_client = GmailClient(credentials)

# Create rules engine
rules_engine = RulesEngine()
rules_engine.create_empty_ruleset("My Rules", "Personal cleanup rules")

# Create a rule
rule = Rule(
    id="delete_old_newsletters",
    name="Delete Old Newsletters",
    description="Delete newsletter emails older than 30 days",
    criteria=RuleCriteria(
        has_words="unsubscribe",
        older_than_days=30
    ),
    action=RuleAction(type=ActionType.DELETE)
)

rules_engine.add_rule(rule)
```

## Next Steps

Now that you have Gmail Cleanup installed and configured:

1. **Explore Rule Templates**: Check out [Rule Templates](rules-system.md#templates) for common use cases
2. **Learn the Rules System**: Understand how to create powerful [custom rules](rules-system.md)
3. **Try the Web Interface**: Start the web server to manage rules visually
4. **Read Best Practices**: Learn [security best practices](security.md) and [optimization tips](optimization.md)

## Troubleshooting

### Common Issues

**Authentication Failed**
```bash
# Clear stored credentials and re-authenticate
gmail-cleanup auth logout
gmail-cleanup auth login
```

**Permission Denied**
- Make sure your Google Cloud Project has Gmail API enabled
- Check that your OAuth2 credentials are correct
- Verify you're using the downloaded client secrets file

**No Rules Found**
- Use rule templates to get started quickly
- Check the [rules examples](examples/) for inspiration

### Getting Help

- Check the [FAQ](faq.md) for common questions
- See [Troubleshooting](troubleshooting.md) for detailed solutions
- Create an [issue on GitHub](https://github.com/yourusername/gmail-cleanup/issues) if you need help

## Safety First

⚠️ **Important Safety Notes**:

1. **Always start with dry-run mode** to see what would be affected
2. **Test rules on a small subset** before applying to all emails
3. **Be careful with delete operations** - they are permanent
4. **Keep backups** of important emails before running cleanup

```bash
# Safe workflow
gmail-cleanup run all --dry-run          # See what would happen
gmail-cleanup run all --max-messages 10  # Test on small set
gmail-cleanup run all                     # Run for real
```