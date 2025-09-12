"""Data models for email filtering rules."""

from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class ActionType(str, Enum):
    """Available rule actions."""
    DELETE = "delete"
    MOVE_TO_TRASH = "move_to_trash" 
    MARK_READ = "mark_read"
    ADD_LABEL = "add_label"
    REMOVE_LABEL = "remove_label"
    ARCHIVE = "archive"
    PERMANENT_DELETE = "permanent_delete"


@dataclass
class RuleCriteria:
    """Criteria for matching emails."""
    from_email: Optional[str] = None
    to_email: Optional[str] = None
    subject_contains: Optional[str] = None
    subject_regex: Optional[str] = None
    body_contains: Optional[str] = None
    body_regex: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    older_than_days: Optional[int] = None
    newer_than_days: Optional[int] = None
    labels: Optional[List[str]] = None
    exclude_labels: Optional[List[str]] = None
    from_domain: Optional[str] = None
    size_larger_than: Optional[int] = None  # in bytes
    size_smaller_than: Optional[int] = None  # in bytes
    has_words: Optional[str] = None
    exclude_words: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {
            key: value for key, value in {
                'from': self.from_email,
                'to': self.to_email,
                'subject_contains': self.subject_contains,
                'subject_regex': self.subject_regex,
                'body_contains': self.body_contains,
                'body_regex': self.body_regex,
                'has_attachment': self.has_attachment,
                'is_unread': self.is_unread,
                'older_than_days': self.older_than_days,
                'newer_than_days': self.newer_than_days,
                'labels': self.labels,
                'exclude_labels': self.exclude_labels,
                'from_domain': self.from_domain,
                'size_larger_than': self.size_larger_than,
                'size_smaller_than': self.size_smaller_than,
                'has_words': self.has_words,
                'exclude_words': self.exclude_words,
            }.items() if value is not None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleCriteria':
        """Create RuleCriteria from dictionary."""
        return cls(
            from_email=data.get('from'),
            to_email=data.get('to'),
            subject_contains=data.get('subject_contains'),
            subject_regex=data.get('subject_regex'),
            body_contains=data.get('body_contains'),
            body_regex=data.get('body_regex'),
            has_attachment=data.get('has_attachment'),
            is_unread=data.get('is_unread'),
            older_than_days=data.get('older_than_days'),
            newer_than_days=data.get('newer_than_days'),
            labels=data.get('labels'),
            exclude_labels=data.get('exclude_labels'),
            from_domain=data.get('from_domain'),
            size_larger_than=data.get('size_larger_than'),
            size_smaller_than=data.get('size_smaller_than'),
            has_words=data.get('has_words'),
            exclude_words=data.get('exclude_words'),
        )


@dataclass
class RuleAction:
    """Action to perform on matched emails."""
    type: ActionType
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {'type': self.type.value}
        if self.parameters:
            result['parameters'] = self.parameters
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleAction':
        """Create RuleAction from dictionary."""
        return cls(
            type=ActionType(data['type']),
            parameters=data.get('parameters', {})
        )


@dataclass
class RuleSchedule:
    """Schedule for when rule should run."""
    enabled: bool = True
    frequency: Optional[str] = None  # 'daily', 'weekly', 'monthly'
    time_of_day: Optional[str] = None  # '09:00'
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    day_of_month: Optional[int] = None  # 1-31
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'enabled': self.enabled,
            'frequency': self.frequency,
            'time_of_day': self.time_of_day,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleSchedule':
        """Create RuleSchedule from dictionary."""
        return cls(
            enabled=data.get('enabled', True),
            frequency=data.get('frequency'),
            time_of_day=data.get('time_of_day'),
            day_of_week=data.get('day_of_week'),
            day_of_month=data.get('day_of_month'),
        )


@dataclass
class Rule:
    """Email filtering rule."""
    id: str
    name: str
    description: str
    criteria: RuleCriteria
    action: RuleAction
    enabled: bool = True
    priority: int = 0  # Higher number = higher priority
    max_messages: Optional[int] = None  # Limit number of messages to process
    dry_run: bool = False
    schedule: Optional[RuleSchedule] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_run_at: Optional[datetime] = None
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'criteria': self.criteria.to_dict(),
            'action': self.action.to_dict(),
            'enabled': self.enabled,
            'priority': self.priority,
            'dry_run': self.dry_run,
            'stats': self.stats,
        }
        
        if self.max_messages is not None:
            result['max_messages'] = self.max_messages
        
        if self.schedule is not None:
            result['schedule'] = self.schedule.to_dict()
        
        if self.created_at is not None:
            result['created_at'] = self.created_at.isoformat()
        
        if self.updated_at is not None:
            result['updated_at'] = self.updated_at.isoformat()
        
        if self.last_run_at is not None:
            result['last_run_at'] = self.last_run_at.isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        """Create Rule from dictionary."""
        return cls(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            criteria=RuleCriteria.from_dict(data['criteria']),
            action=RuleAction.from_dict(data['action']),
            enabled=data.get('enabled', True),
            priority=data.get('priority', 0),
            max_messages=data.get('max_messages'),
            dry_run=data.get('dry_run', False),
            schedule=RuleSchedule.from_dict(data['schedule']) if 'schedule' in data else None,
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None,
            last_run_at=datetime.fromisoformat(data['last_run_at']) if 'last_run_at' in data else None,
            stats=data.get('stats', {}),
        )


@dataclass
class RuleSet:
    """Collection of rules."""
    name: str
    description: str
    rules: List[Rule] = field(default_factory=list)
    version: str = "1.0"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the set."""
        self.rules.append(rule)
        self.updated_at = datetime.now()
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        original_count = len(self.rules)
        self.rules = [r for r in self.rules if r.id != rule_id]
        
        if len(self.rules) < original_count:
            self.updated_at = datetime.now()
            return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[Rule]:
        """Get rule by ID."""
        return next((r for r in self.rules if r.id == rule_id), None)
    
    def get_enabled_rules(self) -> List[Rule]:
        """Get only enabled rules, sorted by priority."""
        enabled_rules = [r for r in self.rules if r.enabled]
        return sorted(enabled_rules, key=lambda r: r.priority, reverse=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'rules': [rule.to_dict() for rule in self.rules],
            'metadata': self.metadata,
        }
        
        if self.created_at is not None:
            result['created_at'] = self.created_at.isoformat()
        
        if self.updated_at is not None:
            result['updated_at'] = self.updated_at.isoformat()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleSet':
        """Create RuleSet from dictionary."""
        return cls(
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0'),
            rules=[Rule.from_dict(rule_data) for rule_data in data.get('rules', [])],
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else None,
            metadata=data.get('metadata', {}),
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RuleSet':
        """Create RuleSet from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


@dataclass
class RuleExecutionResult:
    """Result of executing a rule."""
    rule_id: str
    rule_name: str
    matched_count: int
    processed_count: int
    success_count: int
    error_count: int
    errors: List[str] = field(default_factory=list)
    execution_time: Optional[float] = None
    executed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {
            'rule_id': self.rule_id,
            'rule_name': self.rule_name,
            'matched_count': self.matched_count,
            'processed_count': self.processed_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'errors': self.errors,
        }
        
        if self.execution_time is not None:
            result['execution_time'] = self.execution_time
        
        if self.executed_at is not None:
            result['executed_at'] = self.executed_at.isoformat()
        
        return result