#!/bin/bash

# Gmail Cleanup Test Runner
# This script runs different types of tests for the Gmail Cleanup application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install test dependencies
install_test_deps() {
    print_status "Installing test dependencies..."
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        print_error "Virtual environment not found. Run setup first."
        exit 1
    fi
    
    # Install dev dependencies
    pip install -e .[dev] --quiet
    
    # Install playwright browsers
    playwright install
}

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    source venv/bin/activate
    python -m pytest tests/test_rules_engine.py -v --tb=short -m "not e2e"
    
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed!"
    else
        print_error "Unit tests failed!"
        return 1
    fi
}

# Function to run API tests
run_api_tests() {
    print_status "Running API tests..."
    
    source venv/bin/activate
    python -m pytest tests/test_api.py -v --tb=short -m "not e2e"
    
    if [ $? -eq 0 ]; then
        print_success "API tests passed!"
    else
        print_error "API tests failed!"
        return 1
    fi
}

# Function to run E2E tests
run_e2e_tests() {
    print_status "Running E2E tests..."
    
    # Check if servers are running
    if ! curl -s http://localhost:8000/health > /dev/null; then
        print_error "Backend server is not running on port 8000"
        print_warning "Start the development server first: ./start-dev.sh"
        return 1
    fi
    
    if ! curl -s http://localhost:3000 > /dev/null; then
        print_error "Frontend server is not running on port 3000"
        print_warning "Start the development server first: ./start-dev.sh"
        return 1
    fi
    
    source venv/bin/activate
    python -m pytest tests/test_e2e.py -v --tb=short --headed --slowmo=500
    
    if [ $? -eq 0 ]; then
        print_success "E2E tests passed!"
    else
        print_error "E2E tests failed!"
        return 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    
    source venv/bin/activate
    python -m pytest tests/ -v --tb=short --cov=src/gmail_cleanup --cov-report=html --cov-report=term-missing
    
    if [ $? -eq 0 ]; then
        print_success "All tests passed!"
        print_status "Coverage report generated in htmlcov/"
    else
        print_error "Some tests failed!"
        return 1
    fi
}

# Function to run tests with coverage
run_coverage() {
    print_status "Running tests with coverage..."
    
    source venv/bin/activate
    python -m pytest tests/ --cov=src/gmail_cleanup --cov-report=html --cov-report=term-missing --cov-fail-under=80
    
    if [ $? -eq 0 ]; then
        print_success "Coverage tests passed!"
        print_status "Coverage report: htmlcov/index.html"
    else
        print_error "Coverage tests failed or coverage below 80%!"
        return 1
    fi
}

# Function to run linting and code quality checks
run_lint() {
    print_status "Running code quality checks..."
    
    source venv/bin/activate
    
    # Black formatting check
    print_status "Checking code formatting with Black..."
    black --check src/ tests/ || {
        print_warning "Code formatting issues found. Run 'black src/ tests/' to fix."
    }
    
    # Import sorting check
    print_status "Checking import sorting with isort..."
    isort --check-only src/ tests/ || {
        print_warning "Import sorting issues found. Run 'isort src/ tests/' to fix."
    }
    
    # Flake8 linting
    print_status "Running flake8 linting..."
    flake8 src/ tests/ || {
        print_warning "Linting issues found."
    }
    
    print_success "Code quality checks completed!"
}

# Function to show help
show_help() {
    echo "Gmail Cleanup Test Runner"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     Install test dependencies"
    echo "  unit        Run unit tests"
    echo "  api         Run API tests"
    echo "  e2e         Run end-to-end tests (requires running servers)"
    echo "  all         Run all tests"
    echo "  coverage    Run tests with coverage report"
    echo "  lint        Run code quality checks"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install       # Install dependencies"
    echo "  $0 unit          # Run only unit tests"
    echo "  $0 e2e           # Run E2E tests (start servers first)"
    echo "  $0 all           # Run all tests"
    echo ""
}

# Main script logic
case "${1:-help}" in
    install)
        install_test_deps
        ;;
    unit)
        run_unit_tests
        ;;
    api)
        run_api_tests
        ;;
    e2e)
        run_e2e_tests
        ;;
    all)
        run_all_tests
        ;;
    coverage)
        run_coverage
        ;;
    lint)
        run_lint
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac