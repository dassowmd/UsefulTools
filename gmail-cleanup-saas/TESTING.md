# Testing Guide for Gmail Cleanup SaaS

This document describes the comprehensive testing setup for the Gmail Cleanup SaaS application.

## Overview

The testing suite includes:
- **Unit Tests**: Test individual components and functions
- **API Tests**: Test REST API endpoints
- **End-to-End Tests**: Test complete user workflows using Playwright
- **Integration Tests**: Test component interactions
- **Security Tests**: Automated security scanning

## Test Structure

```
tests/
├── conftest.py          # Test configuration and fixtures
├── test_rules_engine.py # Unit tests for rules engine
├── test_api.py          # API endpoint tests
├── test_e2e.py          # End-to-end tests with Playwright
└── __init__.py
```

## Prerequisites

1. Install test dependencies:
   ```bash
   pip install -e .[dev]
   ```

2. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Running Tests

### Quick Start

Use the provided test runner script:

```bash
# Install dependencies
./run_tests.sh install

# Run all tests
./run_tests.sh all

# Run specific test types
./run_tests.sh unit       # Unit tests only
./run_tests.sh api        # API tests only
./run_tests.sh e2e        # End-to-end tests only
./run_tests.sh coverage   # Tests with coverage report
./run_tests.sh lint       # Code quality checks
```

### Manual Testing

```bash
# Unit tests
pytest tests/test_rules_engine.py -v

# API tests
pytest tests/test_api.py -v

# E2E tests (requires running servers)
pytest tests/test_e2e.py -v --headed

# All tests with coverage
pytest tests/ --cov=src/gmail_cleanup --cov-report=html
```

## Test Types

### 1. Unit Tests (`test_rules_engine.py`)

Tests individual components in isolation:

- **RulesEngine**: Core rule management functionality
- **Rule Models**: Data validation and serialization
- **Rule Criteria**: Email matching logic
- **Rule Actions**: Email processing actions

Example:
```python
def test_rule_creation(self, sample_rule_data):
    """Test creating a rule from dict."""
    rule = create_rule_from_data(sample_rule_data)
    assert rule.name == sample_rule_data["name"]
    assert rule.enabled == sample_rule_data["enabled"]
```

### 2. API Tests (`test_api.py`)

Tests REST API endpoints:

- **Authentication**: Login, logout, status checks
- **Rules Management**: CRUD operations for rules
- **Templates**: Rule template functionality
- **Analysis**: Mailbox analysis endpoints
- **Processing**: Rule execution endpoints

Example:
```python
@pytest.mark.asyncio
async def test_create_rule_valid(self, async_client, sample_rule_data):
    """Test creating a valid rule."""
    response = await async_client.post("/api/rules/", json=sample_rule_data)
    assert response.status_code == status.HTTP_201_CREATED
```

### 3. End-to-End Tests (`test_e2e.py`)

Tests complete user workflows using Playwright:

- **Authentication Flow**: OAuth login process
- **Dashboard Navigation**: UI navigation and layout
- **Rules Management**: Creating, editing, deleting rules
- **Template Usage**: Using rule templates
- **Responsive Design**: Mobile and tablet layouts
- **Error Handling**: Network errors and edge cases

Example:
```python
@pytest.mark.asyncio
async def test_create_rule_modal(self, page: Page, base_url: str):
    """Test that the create rule modal opens and closes."""
    await page.goto(f"{base_url}/#/rules")
    await page.click("button", has_text="Create New Rule")
    await expect(page.locator("[role='dialog']")).to_be_visible()
```

## Test Configuration

### Pytest Configuration (`pytest.ini`)

- **Test Discovery**: Automatically finds test files and functions
- **Coverage**: Measures code coverage with 80% minimum threshold
- **Markers**: Categorizes tests (unit, integration, e2e, slow)
- **Async Support**: Handles async/await test functions

### Test Fixtures (`conftest.py`)

Provides reusable test components:

- **Database Fixtures**: Temporary test databases
- **Auth Mocking**: Mock authentication for testing
- **Sample Data**: Consistent test data across tests
- **Client Fixtures**: Test HTTP clients

## Test Data

### Sample Rule Data
```python
{
    "name": "Test Rule",
    "description": "A test rule for unit testing",
    "criteria": {
        "from_email": "test@example.com",
        "subject_contains": "Test"
    },
    "action": {
        "type": "delete"
    },
    "enabled": True,
    "priority": 1
}
```

## Continuous Integration

### GitHub Actions (`.github/workflows/test.yml`)

Automated testing on:
- **Multiple Python versions**: 3.9, 3.10, 3.11
- **Code Quality**: Black, isort, flake8
- **Security Scanning**: Safety, Bandit
- **Build Testing**: Package building and validation

### Test Jobs

1. **Lint Job**: Code formatting and style checks
2. **Test Job**: Unit and API tests with coverage
3. **E2E Job**: End-to-end browser testing
4. **Security Job**: Vulnerability scanning
5. **Build Job**: Package building

## Coverage Reports

Test coverage is measured and reported:

- **HTML Report**: Generated in `htmlcov/` directory
- **Terminal Report**: Shows missing lines
- **CI Integration**: Uploaded to Codecov

View coverage report:
```bash
# Generate coverage report
pytest tests/ --cov=src/gmail_cleanup --cov-report=html

# Open in browser
open htmlcov/index.html
```

## Debugging Tests

### Running Tests in Debug Mode

```bash
# Run with detailed output
pytest tests/test_api.py -v -s

# Run single test with debugging
pytest tests/test_rules_engine.py::TestRule::test_rule_creation -v -s

# Run E2E tests with browser visible
pytest tests/test_e2e.py --headed --slowmo=500
```

### Test Artifacts

E2E tests generate artifacts on failure:
- **Screenshots**: Visual state when test failed
- **Videos**: Recording of test execution
- **Test Results**: Detailed execution logs

## Writing New Tests

### Unit Test Example

```python
def test_new_functionality(self, sample_data):
    """Test description."""
    # Arrange
    component = Component(sample_data)
    
    # Act
    result = component.method()
    
    # Assert
    assert result.success is True
    assert result.value == expected_value
```

### API Test Example

```python
@pytest.mark.asyncio
async def test_new_endpoint(self, async_client: AsyncClient):
    """Test new API endpoint."""
    response = await async_client.post("/api/new-endpoint", json={
        "data": "test"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
```

### E2E Test Example

```python
@pytest.mark.asyncio
async def test_new_workflow(self, page: Page, base_url: str):
    """Test new user workflow."""
    await page.goto(base_url)
    
    # Navigate and interact
    await page.click("button:has-text('Start')")
    await page.fill("input[name='field']", "value")
    await page.click("button:has-text('Submit')")
    
    # Verify result
    await expect(page.locator(".success-message")).to_be_visible()
```

## Best Practices

1. **Test Naming**: Use descriptive test names that explain what is being tested
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Independent Tests**: Each test should be independent and not rely on others
4. **Mock External Dependencies**: Mock APIs, databases, and external services
5. **Test Data**: Use fixtures for consistent test data
6. **Error Testing**: Include negative test cases and error conditions
7. **Performance**: Mark slow tests and run them separately if needed

## Troubleshooting

### Common Issues

1. **Import Errors**: Check `PYTHONPATH` and module imports
2. **Fixture Scope**: Ensure fixture scopes match test requirements
3. **Async Tests**: Use `@pytest.mark.asyncio` for async tests
4. **Browser Tests**: Ensure servers are running for E2E tests
5. **Coverage Issues**: Check coverage configuration and file paths

### Getting Help

- Review test output for detailed error messages
- Check test logs for debugging information
- Run tests with `-v -s` flags for verbose output
- Use debugger breakpoints for step-by-step debugging

## Future Enhancements

- **Performance Tests**: Add load and performance testing
- **Database Tests**: Add database-specific tests
- **Mobile Testing**: Expand mobile device testing
- **Accessibility Tests**: Add accessibility compliance tests
- **Visual Regression**: Add screenshot comparison tests