"""Test configuration and fixtures."""

import asyncio
import os
import tempfile
from typing import Generator, AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient

from src.gmail_cleanup.api.main import app
from src.gmail_cleanup.rules.engine import RulesEngine
from src.gmail_cleanup.auth.oauth import GoogleAuthManager


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_rules_file():
    """Create a temporary rules file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write('{"name": "Test Rules", "description": "Test rule set", "rules": [], "version": "1.0"}')
        temp_file = f.name
    yield temp_file
    try:
        os.unlink(temp_file)
    except OSError:
        pass


@pytest.fixture
def rules_engine(temp_rules_file):
    """Create a RulesEngine instance for testing."""
    return RulesEngine(rules_file=temp_rules_file)


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_oauth_handler(monkeypatch):
    """Mock GoogleAuthManager for testing."""
    class MockGoogleAuthManager:
        def __init__(self, *args, **kwargs):
            pass
        
        def is_authenticated(self):
            return True
        
        def get_user_info(self):
            return {
                "email": "test@example.com",
                "name": "Test User"
            }
        
        def get_gmail_service(self):
            class MockGmailService:
                def users(self):
                    return self
                
                def getProfile(self, userId='me'):
                    return self
                
                def execute(self):
                    return {
                        "emailAddress": "test@example.com",
                        "messagesTotal": 1000,
                        "threadsTotal": 500
                    }
            return MockGmailService()
    
    monkeypatch.setattr("src.gmail_cleanup.auth.oauth.GoogleAuthManager", MockGoogleAuthManager)
    return MockGoogleAuthManager


@pytest.fixture
def sample_rule_data():
    """Sample rule data for testing."""
    return {
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


@pytest.fixture
def sample_template_data():
    """Sample template data for testing."""
    return {
        "id": "test_template",
        "name": "Test Template",
        "description": "A test template",
        "category": "testing",
        "risk_level": "low",
        "criteria": {
            "older_than_days": 30
        },
        "action": {
            "type": "archive"
        }
    }


# Playwright fixtures
@pytest.fixture(scope="session")
def base_url():
    """Base URL for E2E tests."""
    return "http://localhost:3000"


@pytest.fixture(scope="session")
def api_base_url():
    """API base URL for E2E tests."""
    return "http://localhost:8000"