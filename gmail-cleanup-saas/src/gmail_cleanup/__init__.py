"""Gmail Cleanup - Modern email management tool."""

__version__ = "0.1.0"
__author__ = "Your Name"
__description__ = "Modern email cleanup and management tool"

from .core.processor import EmailProcessor
from .core.client import GmailClient
from .rules.engine import RulesEngine

__all__ = ["EmailProcessor", "GmailClient", "RulesEngine"]