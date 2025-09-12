"""Rules engine for processing email filtering rules."""

import logging
import re
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
from pathlib import Path
import json

from .models import Rule, RuleSet, RuleCriteria, ActionType, RuleExecutionResult

logger = logging.getLogger(__name__)


class RuleValidationError(Exception):
    """Raised when rule validation fails."""
    pass


class RulesEngine:
    """Engine for managing and executing email filtering rules."""
    
    def __init__(self, rules_file: Optional[str] = None):
        """Initialize rules engine.
        
        Args:
            rules_file: Path to rules JSON file
        """
        self.rules_file = rules_file
        self._rule_set: Optional[RuleSet] = None
        
        if rules_file:
            self.load_rules_from_file(rules_file)
    
    def load_rules_from_file(self, file_path: str) -> None:
        """Load rules from JSON file.
        
        Args:
            file_path: Path to rules JSON file
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file contains invalid JSON
            RuleValidationError: If rules are invalid
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Rules file not found: {file_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        self._rule_set = RuleSet.from_dict(data)
        self.rules_file = file_path
        
        # Validate all rules
        for rule in self._rule_set.rules:
            self.validate_rule(rule)
        
        logger.info(f"Loaded {len(self._rule_set.rules)} rules from {file_path}")
    
    def save_rules_to_file(self, file_path: Optional[str] = None) -> None:
        """Save current rules to JSON file.
        
        Args:
            file_path: Path to save file (uses current rules_file if None)
        """
        if not self._rule_set:
            raise ValueError("No rules loaded")
        
        save_path = file_path or self.rules_file
        if not save_path:
            raise ValueError("No file path specified")
        
        # Update timestamp
        self._rule_set.updated_at = datetime.now()
        
        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'w') as f:
            json.dump(self._rule_set.to_dict(), f, indent=2)
        
        logger.info(f"Saved {len(self._rule_set.rules)} rules to {save_path}")
    
    def create_empty_ruleset(self, name: str, description: str = "") -> None:
        """Create an empty rule set.
        
        Args:
            name: Name of the rule set
            description: Description of the rule set
        """
        self._rule_set = RuleSet(
            name=name,
            description=description,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def get_rules(self) -> List[Rule]:
        """Get all rules.
        
        Returns:
            List of all rules
        """
        if not self._rule_set:
            return []
        return self._rule_set.rules
    
    def get_enabled_rules(self) -> List[Rule]:
        """Get enabled rules sorted by priority.
        
        Returns:
            List of enabled rules sorted by priority (highest first)
        """
        if not self._rule_set:
            return []
        return self._rule_set.get_enabled_rules()
    
    def add_rule(self, rule: Rule) -> None:
        """Add a new rule.
        
        Args:
            rule: Rule to add
            
        Raises:
            RuleValidationError: If rule is invalid
        """
        if not self._rule_set:
            self.create_empty_ruleset("Default", "Default rule set")
        
        # Validate rule
        self.validate_rule(rule)
        
        # Check for duplicate ID
        if self._rule_set.get_rule(rule.id):
            raise RuleValidationError(f"Rule with ID '{rule.id}' already exists")
        
        # Set timestamps
        rule.created_at = datetime.now()
        rule.updated_at = datetime.now()
        
        self._rule_set.add_rule(rule)
        logger.info(f"Added rule: {rule.name}")
    
    def update_rule(self, rule_id: str, updated_rule: Rule) -> bool:
        """Update an existing rule.
        
        Args:
            rule_id: ID of rule to update
            updated_rule: Updated rule data
            
        Returns:
            True if rule was updated, False if not found
            
        Raises:
            RuleValidationError: If updated rule is invalid
        """
        if not self._rule_set:
            return False
        
        # Validate updated rule
        self.validate_rule(updated_rule)
        
        # Find and replace rule
        for i, rule in enumerate(self._rule_set.rules):
            if rule.id == rule_id:
                updated_rule.updated_at = datetime.now()
                if updated_rule.created_at is None:
                    updated_rule.created_at = rule.created_at
                
                self._rule_set.rules[i] = updated_rule
                self._rule_set.updated_at = datetime.now()
                
                logger.info(f"Updated rule: {updated_rule.name}")
                return True
        
        return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID.
        
        Args:
            rule_id: ID of rule to remove
            
        Returns:
            True if rule was removed, False if not found
        """
        if not self._rule_set:
            return False
        
        return self._rule_set.remove_rule(rule_id)
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get rule by ID.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule or None if not found
        """
        if not self._rule_set:
            return None
        return self._rule_set.get_rule(rule_id)
    
    def validate_rule(self, rule: Rule) -> None:
        """Validate a rule.
        
        Args:
            rule: Rule to validate
            
        Raises:
            RuleValidationError: If rule is invalid
        """
        if not rule.id:
            raise RuleValidationError("Rule ID cannot be empty")
        
        if not rule.name:
            raise RuleValidationError("Rule name cannot be empty")
        
        if not rule.description:
            raise RuleValidationError("Rule description cannot be empty")
        
        # Validate criteria has at least one condition
        criteria_dict = rule.criteria.to_dict()
        if not criteria_dict:
            raise RuleValidationError("Rule must have at least one criteria")
        
        # Validate regex patterns if present
        if rule.criteria.subject_regex:
            try:
                re.compile(rule.criteria.subject_regex)
            except re.error as e:
                raise RuleValidationError(f"Invalid subject regex: {e}")
        
        if rule.criteria.body_regex:
            try:
                re.compile(rule.criteria.body_regex)
            except re.error as e:
                raise RuleValidationError(f"Invalid body regex: {e}")
        
        # Validate action
        if rule.action.type == ActionType.ADD_LABEL or rule.action.type == ActionType.REMOVE_LABEL:
            if 'labels' not in rule.action.parameters or not rule.action.parameters['labels']:
                raise RuleValidationError(f"Action {rule.action.type} requires 'labels' parameter")
        
        # Validate date ranges
        if (rule.criteria.older_than_days is not None and 
            rule.criteria.newer_than_days is not None and
            rule.criteria.older_than_days <= rule.criteria.newer_than_days):
            raise RuleValidationError("older_than_days must be greater than newer_than_days")
        
        # Validate size ranges
        if (rule.criteria.size_larger_than is not None and
            rule.criteria.size_smaller_than is not None and
            rule.criteria.size_larger_than >= rule.criteria.size_smaller_than):
            raise RuleValidationError("size_larger_than must be less than size_smaller_than")
    
    def build_gmail_query(self, criteria: RuleCriteria) -> str:
        """Build Gmail search query from criteria.
        
        Args:
            criteria: Rule criteria
            
        Returns:
            Gmail search query string
        """
        query_parts = []
        
        # Basic email fields
        if criteria.from_email:
            query_parts.append(f'from:"{criteria.from_email}"')
        elif criteria.from_domain:
            query_parts.append(f'from:@{criteria.from_domain}')
        
        if criteria.to_email:
            query_parts.append(f'to:"{criteria.to_email}"')
        
        # Subject
        if criteria.subject_contains:
            query_parts.append(f'subject:"{criteria.subject_contains}"')
        
        # Body content
        if criteria.body_contains:
            query_parts.append(f'"{criteria.body_contains}"')
        
        if criteria.has_words:
            query_parts.append(f'"{criteria.has_words}"')
        
        if criteria.exclude_words:
            query_parts.append(f'-"{criteria.exclude_words}"')
        
        # Attachment
        if criteria.has_attachment is not None:
            query_parts.append('has:attachment' if criteria.has_attachment else '-has:attachment')
        
        # Read status
        if criteria.is_unread is not None:
            query_parts.append('is:unread' if criteria.is_unread else 'is:read')
        
        # Date ranges
        if criteria.older_than_days is not None:
            query_parts.append(f'older_than:{criteria.older_than_days}d')
        
        if criteria.newer_than_days is not None:
            query_parts.append(f'newer_than:{criteria.newer_than_days}d')
        
        # Size
        if criteria.size_larger_than is not None:
            query_parts.append(f'size:{criteria.size_larger_than}')
        
        if criteria.size_smaller_than is not None:
            query_parts.append(f'-size:{criteria.size_smaller_than}')
        
        # Labels
        if criteria.labels:
            for label in criteria.labels:
                query_parts.append(f'label:{label}')
        
        if criteria.exclude_labels:
            for label in criteria.exclude_labels:
                query_parts.append(f'-label:{label}')
        
        return ' '.join(query_parts)
    
    def get_rule_suggestions(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate rule suggestions based on mailbox analysis.
        
        Args:
            analysis_data: Mailbox analysis results
            
        Returns:
            List of suggested rules
        """
        suggestions = []
        
        # Get top sender domains from analysis
        top_senders = analysis_data.get('top_sender_domains', [])
        
        # Suggest auto-read rules for notification domains
        notification_keywords = [
            'notification', 'noreply', 'no-reply', 'donotreply',
            'alert', 'update', 'newsletter'
        ]
        
        for domain, count in top_senders:
            domain_lower = domain.lower()
            
            if any(keyword in domain_lower for keyword in notification_keywords):
                suggestions.append({
                    'type': 'auto_read',
                    'title': f'Auto-read emails from {domain}',
                    'description': f'Automatically mark {count} emails from {domain} as read',
                    'rule': {
                        'name': f'Auto-read {domain}',
                        'description': f'Automatically mark emails from {domain} as read',
                        'criteria': {'from_domain': domain},
                        'action': {'type': 'mark_read'}
                    }
                })
        
        # Suggest cleanup for high-volume senders
        high_volume_threshold = 50
        for domain, count in top_senders:
            if count > high_volume_threshold:
                suggestions.append({
                    'type': 'high_volume_cleanup',
                    'title': f'Clean up emails from {domain}',
                    'description': f'You have {count} emails from {domain}. Consider cleaning them up.',
                    'rule': {
                        'name': f'Delete old emails from {domain}',
                        'description': f'Delete emails from {domain} older than 90 days',
                        'criteria': {
                            'from_domain': domain,
                            'older_than_days': 90
                        },
                        'action': {'type': 'delete'}
                    }
                })
        
        # Suggest cleanup for old emails
        old_messages = analysis_data.get('old_messages', 0)
        if old_messages > 100:
            suggestions.append({
                'type': 'old_email_cleanup',
                'title': 'Clean up old emails',
                'description': f'You have {old_messages} emails older than 1 year',
                'rule': {
                    'name': 'Delete very old emails',
                    'description': 'Delete emails older than 2 years',
                    'criteria': {'older_than_days': 730},
                    'action': {'type': 'delete'}
                }
            })
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def generate_rule_id(self, name: str) -> str:
        """Generate a unique rule ID based on name.
        
        Args:
            name: Rule name
            
        Returns:
            Unique rule ID
        """
        # Create base ID from name
        base_id = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        base_id = re.sub(r'_+', '_', base_id).strip('_')
        
        if not base_id:
            base_id = 'rule'
        
        # Check for uniqueness
        existing_ids = {rule.id for rule in self.get_rules()}
        
        rule_id = base_id
        counter = 1
        while rule_id in existing_ids:
            rule_id = f"{base_id}_{counter}"
            counter += 1
        
        return rule_id
    
    def export_rules(self, file_path: str, rule_ids: Optional[List[str]] = None) -> None:
        """Export rules to a file.
        
        Args:
            file_path: Path to export file
            rule_ids: List of rule IDs to export (exports all if None)
        """
        if not self._rule_set:
            raise ValueError("No rules loaded")
        
        if rule_ids:
            rules_to_export = [r for r in self._rule_set.rules if r.id in rule_ids]
        else:
            rules_to_export = self._rule_set.rules
        
        export_data = {
            'name': f"{self._rule_set.name} - Export",
            'description': f"Exported rules from {self._rule_set.name}",
            'version': self._rule_set.version,
            'exported_at': datetime.now().isoformat(),
            'rules': [rule.to_dict() for rule in rules_to_export]
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported {len(rules_to_export)} rules to {file_path}")
    
    def import_rules(self, file_path: str, overwrite: bool = False) -> int:
        """Import rules from a file.
        
        Args:
            file_path: Path to import file
            overwrite: Whether to overwrite existing rules with same ID
            
        Returns:
            Number of rules imported
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        rules_data = data.get('rules', [])
        
        for rule_data in rules_data:
            try:
                rule = Rule.from_dict(rule_data)
                
                # Check if rule already exists
                existing_rule = self.get_rule(rule.id)
                if existing_rule and not overwrite:
                    logger.warning(f"Skipping existing rule: {rule.id}")
                    continue
                
                if existing_rule and overwrite:
                    self.update_rule(rule.id, rule)
                else:
                    self.add_rule(rule)
                
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Failed to import rule {rule_data.get('id', 'unknown')}: {e}")
        
        logger.info(f"Imported {imported_count} rules from {file_path}")
        return imported_count