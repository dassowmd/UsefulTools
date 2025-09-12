"""Pydantic models for API requests and responses."""

from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator
from ..rules.models import ActionType


# Request/Response Models

class AuthRequest(BaseModel):
    """Authentication request."""
    client_config: Optional[Dict[str, Any]] = None
    redirect_uri: Optional[str] = None


class AuthResponse(BaseModel):
    """Authentication response."""
    success: bool
    message: str
    auth_url: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    """User profile response."""
    email: str
    is_authenticated: bool
    messages_total: int = 0
    threads_total: int = 0


# Rule Models

class RuleCriteriaRequest(BaseModel):
    """Rule criteria for API requests."""
    from_email: Optional[str] = Field(None, alias="from")
    to_email: Optional[str] = Field(None, alias="to")
    subject_contains: Optional[str] = None
    subject_regex: Optional[str] = None
    body_contains: Optional[str] = None
    body_regex: Optional[str] = None
    has_attachment: Optional[bool] = None
    is_unread: Optional[bool] = None
    older_than_days: Optional[int] = Field(None, ge=1, le=3650)
    newer_than_days: Optional[int] = Field(None, ge=1, le=3650)
    labels: Optional[List[str]] = None
    exclude_labels: Optional[List[str]] = None
    from_domain: Optional[str] = None
    size_larger_than: Optional[int] = Field(None, ge=0)
    size_smaller_than: Optional[int] = Field(None, ge=0)
    has_words: Optional[str] = None
    exclude_words: Optional[str] = None

    @field_validator('older_than_days', 'newer_than_days')
    @classmethod
    def validate_days(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Days must be positive')
        return v

    model_config = {"populate_by_name": True}


class RuleActionRequest(BaseModel):
    """Rule action for API requests."""
    type: ActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)


class RuleScheduleRequest(BaseModel):
    """Rule schedule for API requests."""
    enabled: bool = True
    frequency: Optional[str] = Field(None, pattern=r'^(daily|weekly|monthly)$')
    time_of_day: Optional[str] = Field(None, pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)


class RuleCreateRequest(BaseModel):
    """Request to create a new rule."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    criteria: RuleCriteriaRequest
    action: RuleActionRequest
    enabled: bool = True
    priority: int = Field(0, ge=0, le=100)
    max_messages: Optional[int] = Field(None, ge=1)
    dry_run: bool = False
    schedule: Optional[RuleScheduleRequest] = None


class RuleUpdateRequest(BaseModel):
    """Request to update an existing rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    criteria: Optional[RuleCriteriaRequest] = None
    action: Optional[RuleActionRequest] = None
    enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)
    max_messages: Optional[int] = Field(None, ge=1)
    dry_run: Optional[bool] = None
    schedule: Optional[RuleScheduleRequest] = None


class RuleResponse(BaseModel):
    """Rule response model."""
    id: str
    name: str
    description: str
    criteria: Dict[str, Any]
    action: Dict[str, Any]
    enabled: bool
    priority: int
    max_messages: Optional[int]
    dry_run: bool
    schedule: Optional[Dict[str, Any]]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_run_at: Optional[datetime]
    stats: Dict[str, Any]


class RuleListResponse(BaseModel):
    """Response for listing rules."""
    rules: List[RuleResponse]
    total: int


# Processing Models

class ProcessRulesRequest(BaseModel):
    """Request to process rules."""
    rule_ids: Optional[List[str]] = None  # Process all if None
    dry_run: bool = False
    max_messages_per_rule: Optional[int] = Field(None, ge=1, le=10000)


class ProcessingStatsResponse(BaseModel):
    """Processing statistics response."""
    total_messages: int
    processed_messages: int
    successful_operations: int
    failed_operations: int
    skipped_messages: int
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    success_rate: float


class RuleExecutionResponse(BaseModel):
    """Rule execution result response."""
    rule_id: str
    rule_name: str
    matched_count: int
    processed_count: int
    success_count: int
    error_count: int
    errors: List[str]
    execution_time: Optional[float]
    executed_at: Optional[datetime]


class ProcessingResultResponse(BaseModel):
    """Processing result response."""
    success: bool
    message: str
    results: List[RuleExecutionResponse]
    overall_stats: ProcessingStatsResponse


# Analysis Models

class AnalysisRequest(BaseModel):
    """Request for mailbox analysis."""
    max_messages: Optional[int] = Field(1000, ge=100, le=10000)
    include_suggestions: bool = True


class SenderAnalysis(BaseModel):
    """Sender analysis data."""
    domain: str
    count: int
    percentage: float


class AnalysisResponse(BaseModel):
    """Mailbox analysis response."""
    total_messages: int
    unread_messages: int
    old_messages: int
    unique_senders: int
    top_sender_domains: List[SenderAnalysis]
    analysis_date: datetime
    suggestions: Optional[List[Dict[str, Any]]] = None


# Template Models

class TemplateResponse(BaseModel):
    """Rule template response."""
    id: str
    name: str
    description: str
    category: str
    risk_level: str
    criteria: Dict[str, Any]
    action: Dict[str, Any]


class TemplateListResponse(BaseModel):
    """Response for listing templates."""
    templates: List[TemplateResponse]
    categories: List[str]


class CreateRuleFromTemplateRequest(BaseModel):
    """Request to create rule from template."""
    template_id: str
    customizations: Dict[str, Any] = Field(default_factory=dict)


# Search Models

class SearchMessagesRequest(BaseModel):
    """Request to search messages."""
    query: Optional[str] = None
    criteria: Optional[RuleCriteriaRequest] = None
    max_results: int = Field(100, ge=1, le=1000)
    page_token: Optional[str] = None


class MessageSummary(BaseModel):
    """Summary of an email message."""
    id: str
    thread_id: str
    sender: str
    recipient: str
    subject: str
    date: Optional[datetime]
    labels: List[str]
    snippet: str
    is_unread: bool


class SearchMessagesResponse(BaseModel):
    """Search messages response."""
    messages: List[MessageSummary]
    next_page_token: Optional[str]
    result_count: int
    estimated_total: int


# Error Models

class ErrorResponse(BaseModel):
    """Error response model."""
    error: bool = True
    message: str
    details: Optional[Dict[str, Any]] = None
    code: Optional[str] = None


# Batch Operation Models

class BatchOperationRequest(BaseModel):
    """Request for batch operations."""
    message_ids: List[str] = Field(..., min_items=1, max_items=1000)
    operation: str = Field(..., pattern=r'^(delete|mark_read|add_label|remove_label|archive)$')
    parameters: Dict[str, Any] = Field(default_factory=dict)


class BatchOperationResponse(BaseModel):
    """Batch operation response."""
    success: bool
    processed: int
    succeeded: int
    failed: int
    errors: List[str]
    execution_time: Optional[float]


# Export/Import Models

class ExportRequest(BaseModel):
    """Request to export rules."""
    rule_ids: Optional[List[str]] = None
    format: str = Field("json", pattern=r'^(json|yaml)$')


class ExportResponse(BaseModel):
    """Export response."""
    success: bool
    download_url: Optional[str] = None
    filename: str
    exported_count: int


class ImportRequest(BaseModel):
    """Request to import rules."""
    file_content: str
    overwrite_existing: bool = False
    format: str = Field("json", pattern=r'^(json|yaml)$')


class ImportResponse(BaseModel):
    """Import response."""
    success: bool
    imported_count: int
    skipped_count: int
    errors: List[str]