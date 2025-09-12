"""Gmail Cleanup Library - Core functionality for developers."""

from ..core.client import GmailClient, EmailMessage, BatchResult
from ..core.processor import EmailProcessor, ProcessingStats, ProcessingResult
from ..auth.oauth import GoogleAuthManager, CredentialsManager, AuthenticationError
from ..rules.engine import RulesEngine, RuleValidationError
from ..rules.models import (
    Rule, RuleCriteria, RuleAction, RuleSet, ActionType,
    RuleExecutionResult
)
from ..rules.templates import RuleTemplates

__all__ = [
    # Core client
    "GmailClient",
    "EmailMessage", 
    "BatchResult",
    
    # Email processor
    "EmailProcessor",
    "ProcessingStats",
    "ProcessingResult",
    
    # Authentication
    "GoogleAuthManager",
    "CredentialsManager",
    "AuthenticationError",
    
    # Rules engine
    "RulesEngine",
    "RuleValidationError",
    
    # Rules models
    "Rule",
    "RuleCriteria",
    "RuleAction",
    "RuleSet",
    "ActionType",
    "RuleExecutionResult",
    
    # Templates
    "RuleTemplates",
]