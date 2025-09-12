"""Gmail client for secure email operations."""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


@dataclass
class EmailMessage:
    """Represents an email message."""
    id: str
    thread_id: str
    sender: str
    recipient: str
    subject: str
    date: datetime
    labels: List[str]
    snippet: str
    is_unread: bool


@dataclass
class BatchResult:
    """Result of a batch operation."""
    processed: int
    succeeded: int
    failed: int
    errors: List[str]


class GmailClient:
    """Secure Gmail client using Google API."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self, credentials: Credentials):
        """Initialize Gmail client with OAuth2 credentials.
        
        Args:
            credentials: Google OAuth2 credentials
        """
        self.credentials = credentials
        self.service = None
        self._connect()
    
    def _connect(self) -> None:
        """Establish connection to Gmail API."""
        try:
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            
            self.service = build('gmail', 'v1', credentials=self.credentials)
            logger.info("Successfully connected to Gmail API")
        except Exception as e:
            logger.error(f"Failed to connect to Gmail API: {e}")
            raise
    
    def search_messages(
        self, 
        query: str, 
        max_results: int = 500,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Search for messages using Gmail search syntax.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results to return
            page_token: Token for pagination
            
        Returns:
            Dictionary with messages and next page token
        """
        try:
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                pageToken=page_token
            ).execute()
            
            messages = result.get('messages', [])
            next_page_token = result.get('nextPageToken')
            
            logger.info(f"Found {len(messages)} messages for query: {query}")
            return {
                'messages': messages,
                'nextPageToken': next_page_token,
                'resultSizeEstimate': result.get('resultSizeEstimate', 0)
            }
            
        except HttpError as e:
            logger.error(f"Failed to search messages: {e}")
            raise
    
    def get_message_details(self, message_id: str) -> Optional[EmailMessage]:
        """Get detailed information about a specific message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            EmailMessage object or None if not found
        """
        try:
            result = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in result['payload']['headers']}
            labels = result.get('labelIds', [])
            
            return EmailMessage(
                id=result['id'],
                thread_id=result['threadId'],
                sender=headers.get('From', ''),
                recipient=headers.get('To', ''),
                subject=headers.get('Subject', ''),
                date=self._parse_date(headers.get('Date', '')),
                labels=labels,
                snippet=result.get('snippet', ''),
                is_unread='UNREAD' in labels
            )
            
        except HttpError as e:
            logger.error(f"Failed to get message details for {message_id}: {e}")
            return None
    
    def mark_messages_read(self, message_ids: List[str]) -> BatchResult:
        """Mark messages as read.
        
        Args:
            message_ids: List of message IDs to mark as read
            
        Returns:
            BatchResult with operation statistics
        """
        return self._batch_modify_labels(
            message_ids=message_ids,
            add_labels=[],
            remove_labels=['UNREAD']
        )
    
    def move_to_trash(self, message_ids: List[str]) -> BatchResult:
        """Move messages to trash.
        
        Args:
            message_ids: List of message IDs to trash
            
        Returns:
            BatchResult with operation statistics
        """
        return self._batch_modify_labels(
            message_ids=message_ids,
            add_labels=['TRASH'],
            remove_labels=[]
        )
    
    def add_labels(self, message_ids: List[str], labels: List[str]) -> BatchResult:
        """Add labels to messages.
        
        Args:
            message_ids: List of message IDs
            labels: List of labels to add
            
        Returns:
            BatchResult with operation statistics
        """
        return self._batch_modify_labels(
            message_ids=message_ids,
            add_labels=labels,
            remove_labels=[]
        )
    
    def remove_labels(self, message_ids: List[str], labels: List[str]) -> BatchResult:
        """Remove labels from messages.
        
        Args:
            message_ids: List of message IDs  
            labels: List of labels to remove
            
        Returns:
            BatchResult with operation statistics
        """
        return self._batch_modify_labels(
            message_ids=message_ids,
            add_labels=[],
            remove_labels=labels
        )
    
    def _batch_modify_labels(
        self,
        message_ids: List[str],
        add_labels: List[str],
        remove_labels: List[str]
    ) -> BatchResult:
        """Batch modify labels for multiple messages.
        
        Args:
            message_ids: List of message IDs
            add_labels: Labels to add
            remove_labels: Labels to remove
            
        Returns:
            BatchResult with operation statistics
        """
        if not message_ids:
            return BatchResult(0, 0, 0, [])
        
        succeeded = 0
        failed = 0
        errors = []
        
        # Process in batches of 1000 (Gmail API limit)
        batch_size = 1000
        for i in range(0, len(message_ids), batch_size):
            batch_ids = message_ids[i:i + batch_size]
            
            try:
                body = {
                    'ids': batch_ids,
                    'addLabelIds': add_labels,
                    'removeLabelIds': remove_labels
                }
                
                self.service.users().messages().batchModify(
                    userId='me',
                    body=body
                ).execute()
                
                succeeded += len(batch_ids)
                logger.info(f"Successfully modified {len(batch_ids)} messages")
                
            except HttpError as e:
                failed += len(batch_ids)
                error_msg = f"Batch modify failed: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return BatchResult(
            processed=len(message_ids),
            succeeded=succeeded,
            failed=failed,
            errors=errors
        )
    
    def permanently_delete(self, message_ids: List[str]) -> BatchResult:
        """Permanently delete messages.
        
        Args:
            message_ids: List of message IDs to delete permanently
            
        Returns:
            BatchResult with operation statistics
        """
        succeeded = 0
        failed = 0
        errors = []
        
        for message_id in message_ids:
            try:
                self.service.users().messages().delete(
                    userId='me',
                    id=message_id
                ).execute()
                succeeded += 1
                
            except HttpError as e:
                failed += 1
                error_msg = f"Failed to delete message {message_id}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        logger.info(f"Permanently deleted {succeeded} messages, {failed} failed")
        return BatchResult(
            processed=len(message_ids),
            succeeded=succeeded,
            failed=failed,
            errors=errors
        )
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all available labels.
        
        Returns:
            List of label dictionaries
        """
        try:
            result = self.service.users().labels().list(userId='me').execute()
            return result.get('labels', [])
        except HttpError as e:
            logger.error(f"Failed to get labels: {e}")
            return []
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse email date string to datetime object.
        
        Args:
            date_str: Email date string
            
        Returns:
            Parsed datetime or None if parsing fails
        """
        if not date_str:
            return None
        
        # Try different date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S %Z',
            '%d %b %Y %H:%M:%S %z',
            '%a, %d %b %Y %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def build_search_query(
        self,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        subject: Optional[str] = None,
        has_words: Optional[str] = None,
        exclude_words: Optional[str] = None,
        older_than_days: Optional[int] = None,
        newer_than_days: Optional[int] = None,
        is_unread: Optional[bool] = None,
        has_attachment: Optional[bool] = None,
        labels: Optional[List[str]] = None
    ) -> str:
        """Build Gmail search query from parameters.
        
        Args:
            sender: Filter by sender email
            recipient: Filter by recipient email  
            subject: Filter by subject keywords
            has_words: Must contain these words
            exclude_words: Must not contain these words
            older_than_days: Messages older than N days
            newer_than_days: Messages newer than N days
            is_unread: Filter by read status
            has_attachment: Filter by attachment presence
            labels: Filter by labels
            
        Returns:
            Gmail search query string
        """
        query_parts = []
        
        if sender:
            query_parts.append(f'from:{sender}')
        
        if recipient:
            query_parts.append(f'to:{recipient}')
        
        if subject:
            query_parts.append(f'subject:"{subject}"')
        
        if has_words:
            query_parts.append(f'"{has_words}"')
        
        if exclude_words:
            query_parts.append(f'-"{exclude_words}"')
        
        if older_than_days:
            date = (datetime.now() - timedelta(days=older_than_days)).strftime('%Y/%m/%d')
            query_parts.append(f'before:{date}')
        
        if newer_than_days:
            date = (datetime.now() - timedelta(days=newer_than_days)).strftime('%Y/%m/%d')
            query_parts.append(f'after:{date}')
        
        if is_unread is not None:
            query_parts.append('is:unread' if is_unread else 'is:read')
        
        if has_attachment is not None:
            query_parts.append('has:attachment' if has_attachment else '-has:attachment')
        
        if labels:
            for label in labels:
                query_parts.append(f'label:{label}')
        
        return ' '.join(query_parts)