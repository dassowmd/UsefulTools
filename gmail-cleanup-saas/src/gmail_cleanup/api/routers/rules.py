"""Rules management API routes."""

import logging
from typing import List, Optional
import uuid

from fastapi import APIRouter, HTTPException, status, Depends, Query

from ..dependencies import get_authenticated_rules_engine, get_current_user, validate_rule_id
from ..models import (
    RuleCreateRequest, RuleUpdateRequest, RuleResponse, RuleListResponse,
    TemplateResponse, TemplateListResponse, CreateRuleFromTemplateRequest,
    ErrorResponse
)
from ...rules.engine import RulesEngine, RuleValidationError
from ...rules.models import Rule, RuleCriteria, RuleAction, ActionType
from ...rules.templates import RuleTemplates

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=RuleListResponse)
async def list_rules(
    enabled_only: bool = Query(False, description="Return only enabled rules"),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine)
):
    """List all rules for the authenticated user."""
    try:
        if enabled_only:
            rules = rules_engine.get_enabled_rules()
        else:
            rules = rules_engine.get_rules()
        
        rule_responses = []
        for rule in rules:
            rule_responses.append(RuleResponse(
                id=rule.id,
                name=rule.name,
                description=rule.description,
                criteria=rule.criteria.to_dict(),
                action=rule.action.to_dict(),
                enabled=rule.enabled,
                priority=rule.priority,
                max_messages=rule.max_messages,
                dry_run=rule.dry_run,
                schedule=rule.schedule.to_dict() if rule.schedule else None,
                created_at=rule.created_at,
                updated_at=rule.updated_at,
                last_run_at=rule.last_run_at,
                stats=rule.stats
            ))
        
        return RuleListResponse(
            rules=rule_responses,
            total=len(rule_responses)
        )
    
    except Exception as e:
        logger.error(f"List rules error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rules"
        )


@router.post("/", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    request: RuleCreateRequest,
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine),
    current_user: dict = Depends(get_current_user)
):
    """Create a new rule."""
    try:
        # Generate unique ID
        rule_id = str(uuid.uuid4())
        
        # Convert request to Rule object
        rule = Rule(
            id=rule_id,
            name=request.name,
            description=request.description,
            criteria=RuleCriteria.from_dict(request.criteria.dict(by_alias=True, exclude_none=True)),
            action=RuleAction.from_dict(request.action.dict()),
            enabled=request.enabled,
            priority=request.priority,
            max_messages=request.max_messages,
            dry_run=request.dry_run,
            schedule=None  # TODO: Implement schedule conversion
        )
        
        # Add rule to engine
        rules_engine.add_rule(rule)
        
        # Save to file if configured
        if rules_engine.rules_file:
            rules_engine.save_rules_to_file()
        
        logger.info(f"Created rule: {rule.name} (ID: {rule.id})")
        
        return RuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            criteria=rule.criteria.to_dict(),
            action=rule.action.to_dict(),
            enabled=rule.enabled,
            priority=rule.priority,
            max_messages=rule.max_messages,
            dry_run=rule.dry_run,
            schedule=rule.schedule.to_dict() if rule.schedule else None,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            last_run_at=rule.last_run_at,
            stats=rule.stats
        )
    
    except RuleValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule validation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Create rule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create rule"
        )


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: str = Depends(validate_rule_id),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine)
):
    """Get a specific rule by ID."""
    try:
        rule = rules_engine.get_rule(rule_id)
        
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        return RuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            criteria=rule.criteria.to_dict(),
            action=rule.action.to_dict(),
            enabled=rule.enabled,
            priority=rule.priority,
            max_messages=rule.max_messages,
            dry_run=rule.dry_run,
            schedule=rule.schedule.to_dict() if rule.schedule else None,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            last_run_at=rule.last_run_at,
            stats=rule.stats
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get rule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rule"
        )


@router.put("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    request: RuleUpdateRequest,
    rule_id: str = Depends(validate_rule_id),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine)
):
    """Update an existing rule."""
    try:
        existing_rule = rules_engine.get_rule(rule_id)
        
        if not existing_rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # Create updated rule with merged data
        updated_rule = Rule(
            id=existing_rule.id,
            name=request.name if request.name is not None else existing_rule.name,
            description=request.description if request.description is not None else existing_rule.description,
            criteria=RuleCriteria.from_dict(request.criteria.dict(by_alias=True, exclude_none=True)) if request.criteria else existing_rule.criteria,
            action=RuleAction.from_dict(request.action.dict()) if request.action else existing_rule.action,
            enabled=request.enabled if request.enabled is not None else existing_rule.enabled,
            priority=request.priority if request.priority is not None else existing_rule.priority,
            max_messages=request.max_messages if request.max_messages is not None else existing_rule.max_messages,
            dry_run=request.dry_run if request.dry_run is not None else existing_rule.dry_run,
            schedule=existing_rule.schedule,  # TODO: Implement schedule updates
            created_at=existing_rule.created_at,
            last_run_at=existing_rule.last_run_at,
            stats=existing_rule.stats
        )
        
        # Update rule in engine
        success = rules_engine.update_rule(rule_id, updated_rule)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # Save to file if configured
        if rules_engine.rules_file:
            rules_engine.save_rules_to_file()
        
        logger.info(f"Updated rule: {updated_rule.name} (ID: {rule_id})")
        
        return RuleResponse(
            id=updated_rule.id,
            name=updated_rule.name,
            description=updated_rule.description,
            criteria=updated_rule.criteria.to_dict(),
            action=updated_rule.action.to_dict(),
            enabled=updated_rule.enabled,
            priority=updated_rule.priority,
            max_messages=updated_rule.max_messages,
            dry_run=updated_rule.dry_run,
            schedule=updated_rule.schedule.to_dict() if updated_rule.schedule else None,
            created_at=updated_rule.created_at,
            updated_at=updated_rule.updated_at,
            last_run_at=updated_rule.last_run_at,
            stats=updated_rule.stats
        )
    
    except HTTPException:
        raise
    except RuleValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule validation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Update rule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update rule"
        )


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str = Depends(validate_rule_id),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine)
):
    """Delete a rule."""
    try:
        success = rules_engine.remove_rule(rule_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Rule not found"
            )
        
        # Save to file if configured
        if rules_engine.rules_file:
            rules_engine.save_rules_to_file()
        
        logger.info(f"Deleted rule ID: {rule_id}")
        
        return {"success": True, "message": "Rule deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete rule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete rule"
        )


# Template routes

@router.get("/templates/", response_model=TemplateListResponse)
async def list_templates(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """List available rule templates."""
    try:
        if category:
            templates_data = RuleTemplates.get_template_by_category(category)
        else:
            templates_data = RuleTemplates.get_all_templates()
        
        templates = []
        for template in templates_data:
            templates.append(TemplateResponse(
                id=template['id'],
                name=template['name'],
                description=template['description'],
                category=template.get('category', 'general'),
                risk_level=template.get('risk_level', 'low'),
                criteria=template['criteria'],
                action=template['action']
            ))
        
        categories = RuleTemplates.get_categories()
        
        return TemplateListResponse(
            templates=templates,
            categories=categories
        )
    
    except Exception as e:
        logger.error(f"List templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve templates"
        )


@router.post("/templates/{template_id}", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule_from_template(
    template_id: str,
    request: CreateRuleFromTemplateRequest = None,
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine),
    current_user: dict = Depends(get_current_user)
):
    """Create a rule from a template."""
    try:
        # Get customizations if provided
        customizations = request.customizations if request else {}
        
        # Create rule from template
        rule = RuleTemplates.create_rule_from_template(template_id, **customizations)
        
        # Add rule to engine
        rules_engine.add_rule(rule)
        
        # Save to file if configured
        if rules_engine.rules_file:
            rules_engine.save_rules_to_file()
        
        logger.info(f"Created rule from template {template_id}: {rule.name}")
        
        return RuleResponse(
            id=rule.id,
            name=rule.name,
            description=rule.description,
            criteria=rule.criteria.to_dict(),
            action=rule.action.to_dict(),
            enabled=rule.enabled,
            priority=rule.priority,
            max_messages=rule.max_messages,
            dry_run=rule.dry_run,
            schedule=rule.schedule.to_dict() if rule.schedule else None,
            created_at=rule.created_at,
            updated_at=rule.updated_at,
            last_run_at=rule.last_run_at,
            stats=rule.stats
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except RuleValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rule validation failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Create rule from template error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create rule from template"
        )