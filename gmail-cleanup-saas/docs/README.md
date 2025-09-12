# Gmail Cleanup Documentation

Welcome to Gmail Cleanup - a modern, secure email management tool that helps you automate email cleanup, organize your inbox, and maintain better email hygiene.

## Table of Contents

- [Getting Started](getting-started.md)
- [Authentication](authentication.md)
- [Rules System](rules-system.md)
- [CLI Usage](cli-usage.md)
- [Web API](web-api.md)
- [Library Usage](library-usage.md)
- [Examples](examples/)
- [FAQ](faq.md)
- [Troubleshooting](troubleshooting.md)

## Quick Links

### For End Users
- [Installation Guide](getting-started.md#installation)
- [First-time Setup](getting-started.md#setup)
- [Common Use Cases](examples/common-use-cases.md)

### For Developers
- [API Reference](api-reference.md)
- [Library Documentation](library-usage.md)
- [Contributing Guide](contributing.md)

### For System Administrators
- [Deployment Guide](deployment.md)
- [Configuration](configuration.md)
- [Security Considerations](security.md)

## Features Overview

### 🔐 Secure Authentication
- OAuth2 integration with Google
- No password storage
- Token-based authentication

### 📝 Flexible Rules Engine
- JSON-based rule definitions
- Template-based rule creation
- Real-time rule validation

### 🌐 Multiple Interfaces
- Web dashboard for easy management
- Command-line interface for power users
- Python library for developers

### 📊 Analytics & Insights
- Mailbox analysis and statistics
- Cleanup suggestions
- Performance metrics

### 🔄 Batch Operations
- Process thousands of emails efficiently
- Safe dry-run mode
- Progress tracking

## Architecture

```
gmail-cleanup/
├── src/gmail_cleanup/
│   ├── core/           # Core email processing
│   ├── auth/           # Authentication system
│   ├── rules/          # Rules engine
│   ├── api/            # FastAPI web service
│   ├── cli/            # Command-line interface
│   └── lib/            # Public library interface
├── examples/           # Usage examples
├── docs/              # Documentation
└── tests/             # Test suite
```

## Support

- **Documentation**: This documentation site
- **Issues**: [GitHub Issues](https://github.com/yourusername/gmail-cleanup/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/gmail-cleanup/discussions)

## License

Gmail Cleanup is released under the MIT License. See [LICENSE](../LICENSE) for details.