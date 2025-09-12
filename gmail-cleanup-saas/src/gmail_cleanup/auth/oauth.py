"""Google OAuth2 authentication for Gmail API."""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


class GoogleAuthManager:
    """Manages Google OAuth2 authentication for Gmail API."""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(
        self,
        client_config: Optional[Dict[str, Any]] = None,
        credentials_file: Optional[str] = None,
        token_file: Optional[str] = None
    ):
        """Initialize authentication manager.
        
        Args:
            client_config: Google OAuth2 client configuration dict
            credentials_file: Path to client credentials JSON file
            token_file: Path to store user tokens (default: ~/.gmail-cleanup/token.json)
        """
        self.client_config = client_config
        self.credentials_file = credentials_file
        
        # Set default token file location
        if token_file is None:
            config_dir = Path.home() / '.gmail-cleanup'
            config_dir.mkdir(exist_ok=True)
            self.token_file = str(config_dir / 'token.json')
        else:
            self.token_file = token_file
        
        self._credentials: Optional[Credentials] = None
    
    @classmethod
    def from_client_secrets_file(
        cls,
        client_secrets_file: str,
        token_file: Optional[str] = None
    ) -> 'GoogleAuthManager':
        """Create auth manager from client secrets file.
        
        Args:
            client_secrets_file: Path to client secrets JSON file
            token_file: Path to store user tokens
            
        Returns:
            GoogleAuthManager instance
        """
        return cls(
            credentials_file=client_secrets_file,
            token_file=token_file
        )
    
    @classmethod
    def from_client_config(
        cls,
        client_config: Dict[str, Any],
        token_file: Optional[str] = None
    ) -> 'GoogleAuthManager':
        """Create auth manager from client config dict.
        
        Args:
            client_config: Google OAuth2 client configuration
            token_file: Path to store user tokens
            
        Returns:
            GoogleAuthManager instance
        """
        return cls(
            client_config=client_config,
            token_file=token_file
        )
    
    def get_credentials(self, force_refresh: bool = False) -> Optional[Credentials]:
        """Get valid credentials, refreshing if necessary.
        
        Args:
            force_refresh: Force credential refresh even if valid
            
        Returns:
            Valid Credentials object or None if authentication fails
        """
        if self._credentials and not force_refresh and self._credentials.valid:
            return self._credentials
        
        # Try to load existing credentials
        self._credentials = self._load_credentials()
        
        if self._credentials:
            # Refresh if expired
            if self._credentials.expired and self._credentials.refresh_token:
                try:
                    self._credentials.refresh(Request())
                    self._save_credentials(self._credentials)
                    logger.info("Credentials refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh credentials: {e}")
                    self._credentials = None
        
        # If still no valid credentials, start OAuth flow
        if not self._credentials or not self._credentials.valid:
            self._credentials = self._authenticate_user()
        
        return self._credentials
    
    def _load_credentials(self) -> Optional[Credentials]:
        """Load credentials from token file.
        
        Returns:
            Credentials object or None if file doesn't exist or is invalid
        """
        if not os.path.exists(self.token_file):
            return None
        
        try:
            with open(self.token_file, 'r') as f:
                token_data = json.load(f)
            
            credentials = Credentials.from_authorized_user_info(
                token_data,
                self.SCOPES
            )
            
            logger.debug("Loaded credentials from token file")
            return credentials
            
        except Exception as e:
            logger.warning(f"Failed to load credentials: {e}")
            return None
    
    def _save_credentials(self, credentials: Credentials) -> None:
        """Save credentials to token file.
        
        Args:
            credentials: Credentials to save
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.token_file), exist_ok=True)
            
            # Convert credentials to dict and save
            token_data = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            # Set secure permissions (readable only by owner)
            os.chmod(self.token_file, 0o600)
            
            logger.debug("Saved credentials to token file")
            
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def _authenticate_user(self) -> Optional[Credentials]:
        """Start OAuth2 flow to authenticate user.
        
        Returns:
            Credentials object or None if authentication fails
        """
        try:
            if self.client_config:
                flow = InstalledAppFlow.from_client_config(
                    self.client_config,
                    self.SCOPES
                )
            elif self.credentials_file:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file,
                    self.SCOPES
                )
            else:
                raise ValueError("No client configuration or credentials file provided")
            
            # Run local server for OAuth callback
            credentials = flow.run_local_server(port=0)
            
            # Save credentials for future use
            self._save_credentials(credentials)
            
            logger.info("User authenticated successfully")
            return credentials
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test Gmail API connection with current credentials.
        
        Returns:
            True if connection successful, False otherwise
        """
        credentials = self.get_credentials()
        if not credentials:
            return False
        
        try:
            service = build('gmail', 'v1', credentials=credentials)
            
            # Make a simple API call to test connection
            profile = service.users().getProfile(userId='me').execute()
            
            logger.info(f"Connection test successful - Email: {profile.get('emailAddress')}")
            return True
            
        except HttpError as e:
            logger.error(f"Gmail API connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False
    
    def revoke_credentials(self) -> bool:
        """Revoke stored credentials and delete token file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            credentials = self._load_credentials()
            
            if credentials and credentials.token:
                # Revoke token with Google
                revoke = Request()
                revoke_url = f"https://oauth2.googleapis.com/revoke?token={credentials.token}"
                
                import urllib.request
                urllib.request.urlopen(revoke_url)
                
                logger.info("Credentials revoked with Google")
            
            # Delete local token file
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                logger.info("Local token file deleted")
            
            self._credentials = None
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke credentials: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user information.
        
        Returns:
            Dict with user info or None if not authenticated
        """
        credentials = self.get_credentials()
        if not credentials:
            return None
        
        try:
            service = build('gmail', 'v1', credentials=credentials)
            profile = service.users().getProfile(userId='me').execute()
            
            return {
                'email': profile.get('emailAddress'),
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0),
                'history_id': profile.get('historyId')
            }
            
        except HttpError as e:
            logger.error(f"Failed to get user info: {e}")
            return None
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated.
        
        Returns:
            True if authenticated with valid credentials
        """
        credentials = self.get_credentials()
        return credentials is not None and credentials.valid


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class CredentialsManager:
    """High-level credentials management for the application."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize credentials manager.
        
        Args:
            config_dir: Directory to store configuration files
        """
        if config_dir is None:
            self.config_dir = Path.home() / '.gmail-cleanup'
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(exist_ok=True)
        self.token_file = str(self.config_dir / 'token.json')
        self.client_secrets_file = str(self.config_dir / 'client_secrets.json')
        
        self._auth_manager: Optional[GoogleAuthManager] = None
    
    def setup_client_secrets(self, client_secrets_path: str) -> None:
        """Setup client secrets file.
        
        Args:
            client_secrets_path: Path to client secrets JSON file
        """
        import shutil
        shutil.copy2(client_secrets_path, self.client_secrets_file)
        os.chmod(self.client_secrets_file, 0o600)
        logger.info(f"Client secrets installed to {self.client_secrets_file}")
    
    def setup_client_config(self, client_config: Dict[str, Any]) -> None:
        """Setup client configuration.
        
        Args:
            client_config: Google OAuth2 client configuration dict
        """
        with open(self.client_secrets_file, 'w') as f:
            json.dump(client_config, f, indent=2)
        
        os.chmod(self.client_secrets_file, 0o600)
        logger.info("Client configuration saved")
    
    def get_auth_manager(self) -> GoogleAuthManager:
        """Get configured authentication manager.
        
        Returns:
            GoogleAuthManager instance
            
        Raises:
            AuthenticationError: If no client configuration found
        """
        if self._auth_manager is not None:
            return self._auth_manager
        
        if os.path.exists(self.client_secrets_file):
            self._auth_manager = GoogleAuthManager.from_client_secrets_file(
                self.client_secrets_file,
                self.token_file
            )
        else:
            raise AuthenticationError(
                f"No client secrets found at {self.client_secrets_file}. "
                "Please run 'gmail-cleanup auth setup' first."
            )
        
        return self._auth_manager
    
    def authenticate(self) -> bool:
        """Authenticate user and return success status.
        
        Returns:
            True if authentication successful
        """
        try:
            auth_manager = self.get_auth_manager()
            credentials = auth_manager.get_credentials()
            return credentials is not None and credentials.valid
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated.
        
        Returns:
            True if authenticated
        """
        try:
            auth_manager = self.get_auth_manager()
            return auth_manager.is_authenticated()
        except Exception:
            return False
    
    def logout(self) -> bool:
        """Logout user by revoking credentials.
        
        Returns:
            True if successful
        """
        try:
            auth_manager = self.get_auth_manager()
            return auth_manager.revoke_credentials()
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get authenticated user information.
        
        Returns:
            Dict with user info or None if not authenticated
        """
        try:
            auth_manager = self.get_auth_manager()
            return auth_manager.get_user_info()
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None