# Gmail Cleanup - Modern Email Management SaaS

A comprehensive email cleanup and management tool with a Vue.js frontend and FastAPI backend. Features advanced filtering, grouping, and automated email processing with secure OAuth2 authentication.

## ✨ Features

### 🔐 **Secure Authentication**
- Google OAuth2 integration
- No password storage
- Secure token management

### 📊 **Advanced Email Analysis** 
- Deep mailbox insights with filtering and grouping
- Filter by sender, subject, attachment size, dates
- Group by sender domain, date, size, or labels
- Visual charts and statistics

### 📝 **Flexible Rules Engine**
- JSON-based rule configuration
- Pre-built templates for common scenarios
- Real-time rule validation and preview
- Batch processing with progress tracking

### 🌐 **Modern Web Interface**
- Vue 3 + Composition API
- TanStack Table for advanced data tables
- Chart.js for beautiful visualizations  
- Headless UI for accessible components
- Tailwind CSS for styling
- Toast notifications and tooltips

### 💻 **Developer-Friendly**
- FastAPI backend with automatic OpenAPI docs
- Comprehensive Python library
- CLI tool for power users
- Full TypeScript support

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Project with Gmail API enabled

### 1. Clone and Setup

```bash
git clone <your-repo>
cd gmail-cleanup-saas
```

### 2. Start Development Environment

```bash
./start-dev.sh
```

This will:
- Create Python virtual environment
- Install all dependencies
- Start both backend and frontend servers
- Open your browser to http://localhost:3000

### 3. Configure Google OAuth2

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Gmail API
3. Create OAuth2 credentials (Desktop Application)
4. Download the credentials JSON file
5. Use the web interface to upload your credentials

### 4. Start Using

- **Dashboard**: Overview of your email statistics
- **Analysis**: Deep dive into your email patterns with advanced filtering
- **Rules**: Create and manage cleanup rules
- **Processing**: Execute rules and monitor progress

## 🏗️ Architecture

### Backend (FastAPI + Python)
```
src/gmail_cleanup/
├── core/           # Email processing engine
├── auth/           # OAuth2 authentication
├── rules/          # Rules engine & templates
├── api/            # FastAPI REST API
├── cli/            # Command-line interface
└── lib/            # Public library interface
```

### Frontend (Vue 3 + Vite)
```
frontend/
├── src/
│   ├── components/   # Reusable UI components
│   ├── views/        # Page components
│   ├── stores/       # Pinia state management
│   └── utils/        # Helper functions
└── public/           # Static assets
```

## 📊 Advanced Filtering & Grouping

The Analysis page provides powerful email insights:

### **Filters**
- **Sender**: Filter by email address or domain
- **Subject**: Search subject lines
- **Attachments**: With/without attachments
- **Size**: Message size ranges
- **Date**: Time-based filtering

### **Grouping Options**
- **Sender Domain**: See which domains send you the most email
- **Date**: Group by day/month/year
- **Size**: Small, medium, large, very large
- **Labels**: Gmail labels and folders

### **Visualizations**
- Bar charts for sender domain analysis
- Progress bars for group comparisons
- Interactive data tables with sorting
- Real-time filtering and search

## 🔧 Popular Libraries Used

We use industry-standard, well-maintained libraries:

### **Frontend**
- **Vue 3**: Modern reactive framework
- **Vite**: Ultra-fast build tool
- **Pinia**: Intuitive state management
- **TanStack Table**: Powerful data tables
- **Chart.js**: Beautiful charts and graphs
- **Headless UI**: Accessible, unstyled components
- **VueUse**: Collection of essential Vue composables
- **Tailwind CSS**: Utility-first CSS framework
- **Vue Toastification**: Toast notifications
- **Floating Vue**: Tooltips and popovers

### **Backend**
- **FastAPI**: Modern, fast Python web framework
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Python SQL toolkit
- **Google Auth Libraries**: Official Google authentication
- **Click**: Command-line interface creation
- **Rich**: Beautiful terminal formatting

## 🛠️ Development

### Backend Development

```bash
# Activate virtual environment
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run backend only
python -m uvicorn src.gmail_cleanup.api.main:app --reload

# API Documentation: http://localhost:8000/docs
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### CLI Usage

```bash
# After installation
gmail-cleanup auth login
gmail-cleanup analyze mailbox
gmail-cleanup rules templates
gmail-cleanup run all --dry-run
```

## 📈 Monetization Ready

The architecture supports future monetization features:

- **User Management**: Authentication system ready
- **Usage Analytics**: Processing statistics tracked
- **API Rate Limiting**: Infrastructure in place
- **Subscription Management**: Database schema ready
- **Feature Tiers**: Modular component design

## 🔒 Security Features

- **No Password Storage**: OAuth2 tokens only
- **Secure Logging**: No sensitive data in logs  
- **Token Encryption**: Secure credential storage
- **API Rate Limiting**: Prevent abuse
- **Input Validation**: All user inputs validated

## 📝 Example Rules

```json
{
  "name": "Delete Old Newsletters",
  "description": "Delete newsletter emails older than 30 days",
  "criteria": {
    "has_words": "unsubscribe",
    "older_than_days": 30
  },
  "action": {
    "type": "delete"
  },
  "enabled": true
}
```

## 🚀 Deployment

### Development
```bash
./start-dev.sh
```

### Production
```bash
# Backend
gunicorn src.gmail_cleanup.api.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
npm run build
# Serve dist/ directory with nginx/apache
```

## 📚 Documentation

- **API Docs**: http://localhost:8000/docs (when running)
- **CLI Help**: `gmail-cleanup --help`
- **Library Docs**: See `/docs` directory

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ using Vue 3, FastAPI, and modern web technologies**