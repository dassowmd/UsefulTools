"""Tests for the rules engine."""

import pytest
import uuid
from datetime import datetime

from src.gmail_cleanup.rules.engine import RulesEngine, RuleValidationError
from src.gmail_cleanup.rules.models import Rule, RuleCriteria, RuleAction, ActionType


def create_rule_from_data(rule_data: dict, rule_id: str = None) -> Rule:
    """Helper function to create a Rule from test data."""
    return Rule(
        id=rule_id or str(uuid.uuid4()),
        name=rule_data["name"],
        description=rule_data["description"],
        criteria=RuleCriteria(**rule_data["criteria"]),
        action=RuleAction(type=ActionType(rule_data["action"]["type"])),
        enabled=rule_data.get("enabled", True),
        priority=rule_data.get("priority", 0),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


class TestRulesEngine:
    """Test the RulesEngine class."""
    
    def test_init(self, temp_rules_file):
        """Test RulesEngine initialization."""
        engine = RulesEngine(rules_file=temp_rules_file)
        assert engine.rules_file == temp_rules_file
        assert len(engine.get_rules()) == 0
    
    def test_add_rule(self, rules_engine, sample_rule_data):
        """Test adding a rule."""
        rule = create_rule_from_data(sample_rule_data)
        rules_engine.add_rule(rule)
        
        assert len(rules_engine.get_rules()) == 1
        assert rules_engine.get_rules()[0].name == sample_rule_data["name"]
    
    def test_add_duplicate_rule_id(self, rules_engine, sample_rule_data):
        """Test adding a rule with duplicate ID raises error."""
        rule_id = "test-rule-id"
        rule1 = create_rule_from_data(sample_rule_data, rule_id)
        rule2 = create_rule_from_data(sample_rule_data, rule_id)
        
        rules_engine.add_rule(rule1)
        
        with pytest.raises(RuleValidationError, match="already exists"):
            rules_engine.add_rule(rule2)
    
    def test_get_rule(self, rules_engine, sample_rule_data):
        """Test getting a rule by ID."""
        rule = create_rule_from_data(sample_rule_data)
        rules_engine.add_rule(rule)
        
        found_rule = rules_engine.get_rule(rule.id)
        assert found_rule is not None
        assert found_rule.id == rule.id
        assert found_rule.name == rule.name
    
    def test_get_rule_not_found(self, rules_engine):
        """Test getting a non-existent rule by ID."""
        rule = rules_engine.get_rule("non-existent-id")
        assert rule is None
    
    def test_get_rules_list(self, rules_engine, sample_rule_data):
        """Test getting all rules."""
        rule = create_rule_from_data(sample_rule_data)
        rules_engine.add_rule(rule)
        
        all_rules = rules_engine.get_rules()
        assert len(all_rules) == 1
        assert all_rules[0].name == sample_rule_data["name"]
    
    def test_update_rule(self, rules_engine, sample_rule_data):
        """Test updating a rule."""
        rule = create_rule_from_data(sample_rule_data)
        rules_engine.add_rule(rule)
        
        # Create updated rule
        updated_rule = create_rule_from_data(sample_rule_data, rule.id)
        updated_rule.description = "Updated description"
        
        updated = rules_engine.update_rule(rule.id, updated_rule)
        
        assert updated is True
        found_rule = rules_engine.get_rule(rule.id)
        assert found_rule.description == "Updated description"
        assert found_rule.updated_at >= found_rule.created_at
    
    def test_remove_rule(self, rules_engine, sample_rule_data):
        """Test removing a rule."""
        rule = create_rule_from_data(sample_rule_data)
        rules_engine.add_rule(rule)
        
        removed = rules_engine.remove_rule(rule.id)
        assert removed is True
        assert len(rules_engine.get_rules()) == 0
        
        found_rule = rules_engine.get_rule(rule.id)
        assert found_rule is None
    
    def test_get_enabled_rules(self, rules_engine, sample_rule_data):
        """Test getting only enabled rules."""
        rule1_data = sample_rule_data.copy()
        rule1_data["name"] = "Enabled Rule"
        rule1_data["enabled"] = True
        
        rule2_data = sample_rule_data.copy()
        rule2_data["name"] = "Disabled Rule"
        rule2_data["enabled"] = False
        
        rule1 = create_rule_from_data(rule1_data)
        rule2 = create_rule_from_data(rule2_data)
        
        rules_engine.add_rule(rule1)
        rules_engine.add_rule(rule2)
        
        enabled_rules = rules_engine.get_enabled_rules()
        assert len(enabled_rules) == 1
        assert enabled_rules[0].name == "Enabled Rule"
    
    def test_get_enabled_rules_by_priority(self, rules_engine, sample_rule_data):
        """Test getting enabled rules sorted by priority."""
        rule1_data = sample_rule_data.copy()
        rule1_data["name"] = "High Priority"
        rule1_data["priority"] = 10
        
        rule2_data = sample_rule_data.copy()
        rule2_data["name"] = "Low Priority"
        rule2_data["priority"] = 1
        
        rule1 = create_rule_from_data(rule1_data, "rule1")
        rule2 = create_rule_from_data(rule2_data, "rule2")
        
        rules_engine.add_rule(rule1)
        rules_engine.add_rule(rule2)
        
        enabled_rules = rules_engine.get_enabled_rules()
        assert len(enabled_rules) == 2
        assert enabled_rules[0].name == "High Priority"
        assert enabled_rules[1].name == "Low Priority"
    
    def test_save_and_load_rules(self, rules_engine, sample_rule_data):
        """Test saving rules to file and loading them back."""
        rule = create_rule_from_data(sample_rule_data)
        rules_engine.add_rule(rule)
        
        # Save to file
        rules_engine.save_rules_to_file()
        
        # Create new engine and load
        new_engine = RulesEngine(rules_file=rules_engine.rules_file)
        
        assert len(new_engine.get_rules()) == 1
        loaded_rule = new_engine.get_rules()[0]
        assert loaded_rule.name == sample_rule_data["name"]
        assert loaded_rule.description == sample_rule_data["description"]


class TestRule:
    """Test the Rule model."""
    
    def test_rule_creation(self, sample_rule_data):
        """Test creating a rule from dict."""
        # Create rule using constructor instead of from_dict since from_dict requires ID
        rule = Rule(
            id="test-id",
            name=sample_rule_data["name"],
            description=sample_rule_data["description"],
            criteria=RuleCriteria(**sample_rule_data["criteria"]),
            action=RuleAction(type=ActionType(sample_rule_data["action"]["type"])),
            enabled=sample_rule_data["enabled"],
            priority=sample_rule_data["priority"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert rule.name == sample_rule_data["name"]
        assert rule.description == sample_rule_data["description"]
        assert rule.enabled == sample_rule_data["enabled"]
        assert rule.priority == sample_rule_data["priority"]
        assert isinstance(rule.created_at, datetime)
        assert isinstance(rule.updated_at, datetime)
    
    def test_rule_to_dict(self, sample_rule_data):
        """Test converting rule to dict."""
        rule = Rule(
            id="test-id",
            name=sample_rule_data["name"],
            description=sample_rule_data["description"],
            criteria=RuleCriteria(**sample_rule_data["criteria"]),
            action=RuleAction(type=ActionType(sample_rule_data["action"]["type"])),
            enabled=sample_rule_data["enabled"],
            priority=sample_rule_data["priority"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        rule_dict = rule.to_dict()
        
        assert rule_dict["name"] == sample_rule_data["name"]
        assert rule_dict["description"] == sample_rule_data["description"]
        assert "id" in rule_dict
        assert "created_at" in rule_dict
        assert "updated_at" in rule_dict
    
    def test_rule_criteria_validation(self):
        """Test rule criteria validation."""
        # Valid criteria
        criteria = RuleCriteria(from_email="test@example.com")
        assert criteria.from_email == "test@example.com"
        
        # Test multiple criteria
        criteria = RuleCriteria(
            from_email="test@example.com",
            subject_contains="Important",
            older_than_days=30
        )
        assert criteria.from_email == "test@example.com"
        assert criteria.subject_contains == "Important"
        assert criteria.older_than_days == 30
    
    def test_rule_action_types(self):
        """Test different rule action types."""
        # Delete action
        action = RuleAction(type=ActionType.DELETE)
        assert action.type == ActionType.DELETE
        
        # Archive action
        action = RuleAction(type=ActionType.ARCHIVE)
        assert action.type == ActionType.ARCHIVE
        
        # Mark read action
        action = RuleAction(type=ActionType.MARK_READ)
        assert action.type == ActionType.MARK_READ
        
        # Add label action
        action = RuleAction(type=ActionType.ADD_LABEL, parameters={"label": "Important"})
        assert action.type == ActionType.ADD_LABEL
        assert action.parameters["label"] == "Important"