"""FastAPI dependency providers."""

import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..auth.oauth import CredentialsManager, GoogleAuthManager
from ..core.client import GmailClient
from ..rules.engine import RulesEngine
from .models import ErrorResponse

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)

# Global instances (will be replaced with proper dependency injection in production)
_credentials_manager: Optional[CredentialsManager] = None
_gmail_client: Optional[GmailClient] = None
_rules_engine: Optional[RulesEngine] = None


@lru_cache()
def get_credentials_manager() -> CredentialsManager:
    """Get credentials manager instance."""
    global _credentials_manager
    if _credentials_manager is None:
        _credentials_manager = CredentialsManager()
    return _credentials_manager


def get_gmail_client() -> Optional[GmailClient]:
    """Get Gmail client instance if authenticated."""
    global _gmail_client
    
    try:
        credentials_manager = get_credentials_manager()
        
        if not credentials_manager.is_authenticated():
            return None
        
        if _gmail_client is None:
            auth_manager = credentials_manager.get_auth_manager()
            credentials = auth_manager.get_credentials()
            
            if credentials and credentials.valid:
                _gmail_client = GmailClient(credentials)
            
        return _gmail_client
    
    except Exception as e:
        logger.error(f"Failed to get Gmail client: {e}")
        return None


def get_rules_engine() -> RulesEngine:
    """Get rules engine instance."""
    global _rules_engine
    if _rules_engine is None:
        _rules_engine = RulesEngine()
    return _rules_engine


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user.
    
    For now, this is a simple implementation. In production, you'd verify
    JWT tokens or session tokens here.
    """
    try:
        credentials_manager = get_credentials_manager()
        
        if not credentials_manager.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated. Please log in first.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_info = credentials_manager.get_user_info()
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to retrieve user information",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_info
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


async def require_gmail_client(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> GmailClient:
    """Require authenticated Gmail client."""
    gmail_client = get_gmail_client()
    
    if gmail_client is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Gmail authentication required"
        )
    
    return gmail_client


def get_authenticated_rules_engine(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> RulesEngine:
    """Get rules engine for authenticated user."""
    return get_rules_engine()


# Error handlers

def create_error_response(
    message: str,
    details: Optional[Dict[str, Any]] = None,
    code: Optional[str] = None
) -> ErrorResponse:
    """Create standardized error response."""
    return ErrorResponse(
        message=message,
        details=details,
        code=code
    )


# Validation dependencies

async def validate_rule_id(rule_id: str) -> str:
    """Validate rule ID format."""
    if not rule_id or not rule_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rule ID cannot be empty"
        )
    return rule_id.strip()


async def validate_pagination(
    page: int = 1,
    per_page: int = 20
) -> Dict[str, int]:
    """Validate pagination parameters."""
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page number must be >= 1"
        )
    
    if per_page < 1 or per_page > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Per page must be between 1 and 100"
        )
    
    return {"page": page, "per_page": per_page}


# Rate limiting (placeholder - implement with Redis in production)
class RateLimiter:
    """Simple in-memory rate limiter for development."""
    
    def __init__(self):
        self._requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed under rate limit."""
        import time
        
        now = time.time()
        window_start = now - window
        
        if key not in self._requests:
            self._requests[key] = []
        
        # Clean old requests
        self._requests[key] = [
            req_time for req_time in self._requests[key] 
            if req_time > window_start
        ]
        
        if len(self._requests[key]) >= limit:
            return False
        
        self._requests[key].append(now)
        return True


_rate_limiter = RateLimiter()


async def rate_limit(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 100,
    window: int = 60
):
    """Apply rate limiting based on user email."""
    user_email = current_user.get('email', 'anonymous')
    
    if not _rate_limiter.is_allowed(user_email, limit, window):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {limit} requests per {window} seconds."
        )


# Cleanup function for global state
def cleanup_dependencies():
    """Cleanup global dependency instances."""
    global _gmail_client, _rules_engine
    
    if _gmail_client:
        # Gmail client doesn't need explicit cleanup
        _gmail_client = None
    
    if _rules_engine:
        # Rules engine doesn't need explicit cleanup
        _rules_engine = None