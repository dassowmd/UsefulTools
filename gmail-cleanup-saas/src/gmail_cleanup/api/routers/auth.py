"""Authentication API routes."""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse

from ..dependencies import get_credentials_manager
from ..models import AuthRequest, AuthResponse, UserResponse
from ...auth.oauth import CredentialsManager, AuthenticationError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=AuthResponse)
async def login(
    request: AuthRequest = None,
    credentials_manager: CredentialsManager = Depends(get_credentials_manager)
):
    """Initiate OAuth2 login flow."""
    try:
        # Check if already authenticated
        if credentials_manager.is_authenticated():
            user_info = credentials_manager.get_user_info()
            return AuthResponse(
                success=True,
                message="Already authenticated",
                user_info=user_info
            )
        
        # Start authentication flow
        success = credentials_manager.authenticate()
        
        if success:
            user_info = credentials_manager.get_user_info()
            return AuthResponse(
                success=True,
                message="Authentication successful",
                user_info=user_info
            )
        else:
            return AuthResponse(
                success=False,
                message="Authentication failed"
            )
    
    except AuthenticationError as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout(
    credentials_manager: CredentialsManager = Depends(get_credentials_manager)
):
    """Logout and revoke credentials."""
    try:
        success = credentials_manager.logout()
        
        if success:
            return AuthResponse(
                success=True,
                message="Logged out successfully"
            )
        else:
            return AuthResponse(
                success=False,
                message="Logout failed"
            )
    
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )


@router.get("/status", response_model=AuthResponse)
async def auth_status(
    credentials_manager: CredentialsManager = Depends(get_credentials_manager)
):
    """Check authentication status."""
    try:
        is_authenticated = credentials_manager.is_authenticated()
        
        if is_authenticated:
            user_info = credentials_manager.get_user_info()
            return AuthResponse(
                success=True,
                message="User is authenticated",
                user_info=user_info
            )
        else:
            return AuthResponse(
                success=False,
                message="User is not authenticated"
            )
    
    except Exception as e:
        logger.error(f"Auth status error: {e}")
        return AuthResponse(
            success=False,
            message="Unable to check authentication status"
        )


@router.get("/user", response_model=UserResponse)
async def get_user_info(
    credentials_manager: CredentialsManager = Depends(get_credentials_manager)
):
    """Get current user information."""
    try:
        if not credentials_manager.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        user_info = credentials_manager.get_user_info()
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unable to retrieve user information"
            )
        
        return UserResponse(
            email=user_info.get('email', 'Unknown'),
            is_authenticated=True,
            messages_total=user_info.get('messages_total', 0),
            threads_total=user_info.get('threads_total', 0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve user information"
        )


@router.post("/setup-client")
async def setup_client(
    client_config: Dict[str, Any],
    credentials_manager: CredentialsManager = Depends(get_credentials_manager)
):
    """Setup OAuth2 client configuration."""
    try:
        credentials_manager.setup_client_config(client_config)
        
        return {
            "success": True,
            "message": "Client configuration saved successfully"
        }
    
    except Exception as e:
        logger.error(f"Setup client error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save client configuration"
        )


@router.get("/test-connection")
async def test_connection(
    credentials_manager: CredentialsManager = Depends(get_credentials_manager)
):
    """Test Gmail API connection."""
    try:
        if not credentials_manager.is_authenticated():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        auth_manager = credentials_manager.get_auth_manager()
        connection_ok = auth_manager.test_connection()
        
        return {
            "success": connection_ok,
            "message": "Connection successful" if connection_ok else "Connection failed"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Test connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Connection test failed"
        )