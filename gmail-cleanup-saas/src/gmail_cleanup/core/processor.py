"""Email processing engine."""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from .client import GmailClient, BatchResult, EmailMessage
from ..rules.engine import RulesEngine, Rule
from ..rules.models import RuleExecutionResult

logger = logging.getLogger(__name__)


@dataclass
class ProcessingStats:
    """Statistics for email processing operations."""
    total_messages: int = 0
    processed_messages: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    skipped_messages: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    @property
    def success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.processed_messages == 0:
            return 0.0
        return (self.successful_operations / self.processed_messages) * 100


@dataclass
class ProcessingResult:
    """Result of email processing operation."""
    rule: Rule
    matched_messages: List[str]
    batch_result: BatchResult
    stats: ProcessingStats
    errors: List[str]


class EmailProcessor:
    """Main email processing engine."""
    
    def __init__(
        self,
        gmail_client: GmailClient,
        rules_engine: RulesEngine,
        max_workers: int = 4,
        batch_size: int = 100
    ):
        """Initialize email processor.
        
        Args:
            gmail_client: Gmail API client
            rules_engine: Rules processing engine
            max_workers: Maximum number of worker threads
            batch_size: Number of messages to process in each batch
        """
        self.gmail_client = gmail_client
        self.rules_engine = rules_engine
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._progress_callbacks: List[Callable[[ProcessingStats], None]] = []
    
    def add_progress_callback(self, callback: Callable[[ProcessingStats], None]) -> None:
        """Add a callback function to receive processing progress updates.
        
        Args:
            callback: Function to call with ProcessingStats updates
        """
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self, stats: ProcessingStats) -> None:
        """Notify all registered callbacks of progress update."""
        for callback in self._progress_callbacks:
            try:
                callback(stats)
            except Exception as e:
                logger.warning(f"Progress callback failed: {e}")
    
    async def process_all_rules(
        self,
        dry_run: bool = False,
        max_messages_per_rule: Optional[int] = None
    ) -> List[ProcessingResult]:
        """Process all rules in the rules engine.
        
        Args:
            dry_run: If True, only analyze without making changes
            max_messages_per_rule: Limit number of messages processed per rule
            
        Returns:
            List of processing results for each rule
        """
        rules = self.rules_engine.get_rules()
        if not rules:
            logger.warning("No rules found to process")
            return []
        
        logger.info(f"Processing {len(rules)} rules (dry_run={dry_run})")
        results = []
        
        for rule in rules:
            if not rule.enabled:
                logger.info(f"Skipping disabled rule: {rule.name}")
                continue
            
            try:
                result = await self.process_rule(
                    rule=rule,
                    dry_run=dry_run,
                    max_messages=max_messages_per_rule
                )
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to process rule '{rule.name}': {e}")
                # Create error result
                error_result = ProcessingResult(
                    rule=rule,
                    matched_messages=[],
                    batch_result=BatchResult(0, 0, 0, [str(e)]),
                    stats=ProcessingStats(),
                    errors=[str(e)]
                )
                results.append(error_result)
        
        return results
    
    async def process_rule(
        self,
        rule: Rule,
        dry_run: bool = False,
        max_messages: Optional[int] = None
    ) -> ProcessingResult:
        """Process a single rule.
        
        Args:
            rule: Rule to process
            dry_run: If True, only analyze without making changes
            max_messages: Limit number of messages to process
            
        Returns:
            ProcessingResult for the rule
        """
        stats = ProcessingStats(start_time=datetime.now())
        errors = []
        
        logger.info(f"Processing rule: {rule.name} (dry_run={dry_run})")
        
        try:
            # Build search query from rule criteria
            query = self._build_search_query(rule)
            logger.debug(f"Search query for rule '{rule.name}': {query}")
            
            # Search for matching messages
            matched_messages = await self._search_messages_async(
                query=query,
                max_results=max_messages
            )
            
            stats.total_messages = len(matched_messages)
            logger.info(f"Rule '{rule.name}' matched {stats.total_messages} messages")
            
            if not matched_messages:
                stats.end_time = datetime.now()
                return ProcessingResult(
                    rule=rule,
                    matched_messages=[],
                    batch_result=BatchResult(0, 0, 0, []),
                    stats=stats,
                    errors=[]
                )
            
            # Apply rule action to messages
            if dry_run:
                # In dry run, just count the messages that would be processed
                batch_result = BatchResult(
                    processed=stats.total_messages,
                    succeeded=stats.total_messages,
                    failed=0,
                    errors=[]
                )
                stats.successful_operations = stats.total_messages
            else:
                batch_result = await self._apply_rule_action(rule, matched_messages)
                stats.successful_operations = batch_result.succeeded
                stats.failed_operations = batch_result.failed
                errors.extend(batch_result.errors)
            
            stats.processed_messages = batch_result.processed
            stats.end_time = datetime.now()
            
            self._notify_progress(stats)
            
            logger.info(
                f"Rule '{rule.name}' completed: "
                f"{stats.successful_operations} succeeded, "
                f"{stats.failed_operations} failed"
            )
            
            return ProcessingResult(
                rule=rule,
                matched_messages=matched_messages,
                batch_result=batch_result,
                stats=stats,
                errors=errors
            )
            
        except Exception as e:
            stats.end_time = datetime.now()
            error_msg = f"Rule processing failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            return ProcessingResult(
                rule=rule,
                matched_messages=[],
                batch_result=BatchResult(0, 0, 0, [error_msg]),
                stats=stats,
                errors=errors
            )
    
    async def _search_messages_async(
        self,
        query: str,
        max_results: Optional[int] = None
    ) -> List[str]:
        """Asynchronously search for messages.
        
        Args:
            query: Gmail search query
            max_results: Maximum number of results
            
        Returns:
            List of message IDs
        """
        loop = asyncio.get_event_loop()
        
        def _search():
            all_messages = []
            page_token = None
            
            while True:
                batch_limit = min(500, max_results - len(all_messages)) if max_results else 500
                
                result = self.gmail_client.search_messages(
                    query=query,
                    max_results=batch_limit,
                    page_token=page_token
                )
                
                messages = result.get('messages', [])
                all_messages.extend([msg['id'] for msg in messages])
                
                page_token = result.get('nextPageToken')
                
                if not page_token or (max_results and len(all_messages) >= max_results):
                    break
            
            return all_messages[:max_results] if max_results else all_messages
        
        return await loop.run_in_executor(self.executor, _search)
    
    def _build_search_query(self, rule: Rule) -> str:
        """Build Gmail search query from rule criteria.
        
        Args:
            rule: Rule containing search criteria
            
        Returns:
            Gmail search query string
        """
        criteria = rule.criteria
        
        return self.gmail_client.build_search_query(
            sender=criteria.get('from'),
            recipient=criteria.get('to'),
            subject=criteria.get('subject'),
            has_words=criteria.get('has_words'),
            exclude_words=criteria.get('exclude_words'),
            older_than_days=criteria.get('older_than_days'),
            newer_than_days=criteria.get('newer_than_days'),
            is_unread=criteria.get('is_unread'),
            has_attachment=criteria.get('has_attachment'),
            labels=criteria.get('labels')
        )
    
    async def _apply_rule_action(
        self,
        rule: Rule,
        message_ids: List[str]
    ) -> BatchResult:
        """Apply rule action to messages.
        
        Args:
            rule: Rule containing action to apply
            message_ids: List of message IDs to process
            
        Returns:
            BatchResult with operation statistics
        """
        loop = asyncio.get_event_loop()
        action = rule.action.lower()
        
        def _apply_action():
            if action == 'delete' or action == 'move_to_trash':
                return self.gmail_client.move_to_trash(message_ids)
            
            elif action == 'mark_read':
                return self.gmail_client.mark_messages_read(message_ids)
            
            elif action == 'add_label':
                labels = rule.action_params.get('labels', [])
                return self.gmail_client.add_labels(message_ids, labels)
            
            elif action == 'remove_label':
                labels = rule.action_params.get('labels', [])
                return self.gmail_client.remove_labels(message_ids, labels)
            
            elif action == 'permanent_delete':
                return self.gmail_client.permanently_delete(message_ids)
            
            else:
                raise ValueError(f"Unknown action: {action}")
        
        return await loop.run_in_executor(self.executor, _apply_action)
    
    async def analyze_mailbox(
        self,
        max_messages: Optional[int] = None
    ) -> Dict[str, Any]:
        """Analyze mailbox to provide insights for rule creation.
        
        Args:
            max_messages: Limit analysis to N messages
            
        Returns:
            Dictionary with mailbox statistics and insights
        """
        logger.info("Starting mailbox analysis")
        
        # Get recent messages for analysis
        query = "in:inbox OR in:sent"
        message_ids = await self._search_messages_async(
            query=query,
            max_results=max_messages or 1000
        )
        
        if not message_ids:
            return {"error": "No messages found for analysis"}
        
        # Analyze message details in batches
        loop = asyncio.get_event_loop()
        
        def _get_message_batch(batch_ids):
            messages = []
            for msg_id in batch_ids:
                msg = self.gmail_client.get_message_details(msg_id)
                if msg:
                    messages.append(msg)
            return messages
        
        # Process in smaller batches to avoid rate limits
        all_messages = []
        batch_size = 50
        
        for i in range(0, len(message_ids), batch_size):
            batch_ids = message_ids[i:i + batch_size]
            batch_messages = await loop.run_in_executor(
                self.executor,
                _get_message_batch,
                batch_ids
            )
            all_messages.extend(batch_messages)
            
            # Brief pause to respect rate limits
            await asyncio.sleep(0.1)
        
        # Analyze the messages
        analysis = self._analyze_messages(all_messages)
        logger.info(f"Analyzed {len(all_messages)} messages")
        
        return analysis
    
    def _analyze_messages(self, messages: List[EmailMessage]) -> Dict[str, Any]:
        """Analyze messages to extract insights.
        
        Args:
            messages: List of EmailMessage objects
            
        Returns:
            Dictionary with analysis results
        """
        if not messages:
            return {}
        
        # Count messages by sender domain
        sender_domains = {}
        unread_count = 0
        old_messages = 0  # Older than 1 year
        
        now = datetime.now()
        one_year_ago = now.replace(year=now.year - 1)
        
        for msg in messages:
            # Extract domain from sender
            if '@' in msg.sender:
                domain = msg.sender.split('@')[-1].strip('>')
                sender_domains[domain] = sender_domains.get(domain, 0) + 1
            
            if msg.is_unread:
                unread_count += 1
            
            if msg.date and msg.date < one_year_ago:
                old_messages += 1
        
        # Sort sender domains by frequency
        top_senders = sorted(
            sender_domains.items(),
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        return {
            "total_messages": len(messages),
            "unread_messages": unread_count,
            "old_messages": old_messages,
            "top_sender_domains": top_senders,
            "unique_senders": len(sender_domains),
            "suggestions": self._generate_suggestions(
                total=len(messages),
                unread=unread_count,
                old=old_messages,
                top_senders=top_senders
            )
        }
    
    def _generate_suggestions(
        self,
        total: int,
        unread: int,
        old: int,
        top_senders: List[tuple]
    ) -> List[Dict[str, Any]]:
        """Generate cleanup suggestions based on analysis.
        
        Args:
            total: Total message count
            unread: Unread message count
            old: Old message count
            top_senders: List of (domain, count) tuples
            
        Returns:
            List of suggested rules
        """
        suggestions = []
        
        # Suggest cleaning old messages
        if old > 100:
            suggestions.append({
                "type": "cleanup_old",
                "title": "Clean up old messages",
                "description": f"You have {old} messages older than 1 year",
                "suggested_rule": {
                    "name": "Delete old messages",
                    "action": "delete",
                    "criteria": {"older_than_days": 365}
                }
            })
        
        # Suggest auto-reading notifications
        notification_domains = [
            domain for domain, count in top_senders
            if any(keyword in domain.lower() for keyword in [
                'notification', 'noreply', 'no-reply', 'donotreply'
            ])
        ]
        
        if notification_domains:
            suggestions.append({
                "type": "auto_read_notifications",
                "title": "Auto-read notification emails",
                "description": f"Automatically mark emails from {len(notification_domains)} notification domains as read",
                "suggested_rules": [
                    {
                        "name": f"Mark {domain} as read",
                        "action": "mark_read",
                        "criteria": {"from": f"@{domain}"}
                    }
                    for domain in notification_domains[:5]  # Limit to top 5
                ]
            })
        
        # Suggest cleaning high-volume senders
        high_volume_senders = [
            (domain, count) for domain, count in top_senders[:10]
            if count > 50
        ]
        
        if high_volume_senders:
            suggestions.append({
                "type": "high_volume_cleanup",
                "title": "Clean up high-volume senders",
                "description": f"Consider rules for domains sending {sum(count for _, count in high_volume_senders)} messages",
                "domains": high_volume_senders
            })
        
        return suggestions
    
    def close(self) -> None:
        """Clean up resources."""
        if self.executor:
            self.executor.shutdown(wait=True)