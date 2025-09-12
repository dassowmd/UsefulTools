"""Email processing API routes."""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks

from ..dependencies import require_gmail_client, get_authenticated_rules_engine, get_current_user
from ..models import (
    ProcessRulesRequest, ProcessingResultResponse, RuleExecutionResponse,
    ProcessingStatsResponse, BatchOperationRequest, BatchOperationResponse
)
from ...core.client import GmailClient
from ...core.processor import EmailProcessor
from ...rules.engine import RulesEngine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/rules/run", response_model=ProcessingResultResponse)
async def process_rules(
    request: ProcessRulesRequest,
    gmail_client: GmailClient = Depends(require_gmail_client),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine),
    current_user: dict = Depends(get_current_user)
):
    """Process email rules."""
    try:
        # Create email processor
        processor = EmailProcessor(
            gmail_client=gmail_client,
            rules_engine=rules_engine
        )
        
        # Process rules
        if request.rule_ids:
            # Process specific rules
            rules_to_process = []
            for rule_id in request.rule_ids:
                rule = rules_engine.get_rule(rule_id)
                if not rule:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Rule not found: {rule_id}"
                    )
                rules_to_process.append(rule)
            
            # Process each rule individually
            results = []
            overall_stats = ProcessingStatsResponse(
                total_messages=0,
                processed_messages=0,
                successful_operations=0,
                failed_operations=0,
                skipped_messages=0,
                success_rate=0.0
            )
            
            for rule in rules_to_process:
                result = await processor.process_rule(
                    rule=rule,
                    dry_run=request.dry_run,
                    max_messages=request.max_messages_per_rule
                )
                
                execution_result = RuleExecutionResponse(
                    rule_id=result.rule.id,
                    rule_name=result.rule.name,
                    matched_count=len(result.matched_messages),
                    processed_count=result.batch_result.processed,
                    success_count=result.batch_result.succeeded,
                    error_count=result.batch_result.failed,
                    errors=result.batch_result.errors,
                    execution_time=result.stats.duration,
                    executed_at=result.stats.end_time
                )
                
                results.append(execution_result)
                
                # Update overall stats
                overall_stats.total_messages += result.stats.total_messages
                overall_stats.processed_messages += result.stats.processed_messages
                overall_stats.successful_operations += result.stats.successful_operations
                overall_stats.failed_operations += result.stats.failed_operations
        else:
            # Process all rules
            processing_results = await processor.process_all_rules(
                dry_run=request.dry_run,
                max_messages_per_rule=request.max_messages_per_rule
            )
            
            results = []
            overall_stats = ProcessingStatsResponse(
                total_messages=0,
                processed_messages=0,
                successful_operations=0,
                failed_operations=0,
                skipped_messages=0,
                success_rate=0.0
            )
            
            for result in processing_results:
                execution_result = RuleExecutionResponse(
                    rule_id=result.rule.id,
                    rule_name=result.rule.name,
                    matched_count=len(result.matched_messages),
                    processed_count=result.batch_result.processed,
                    success_count=result.batch_result.succeeded,
                    error_count=result.batch_result.failed,
                    errors=result.batch_result.errors,
                    execution_time=result.stats.duration,
                    executed_at=result.stats.end_time
                )
                
                results.append(execution_result)
                
                # Update overall stats
                overall_stats.total_messages += result.stats.total_messages
                overall_stats.processed_messages += result.stats.processed_messages
                overall_stats.successful_operations += result.stats.successful_operations
                overall_stats.failed_operations += result.stats.failed_operations
        
        # Calculate overall success rate
        if overall_stats.processed_messages > 0:
            overall_stats.success_rate = (
                overall_stats.successful_operations / overall_stats.processed_messages * 100
            )
        
        # Clean up processor
        processor.close()
        
        success = len([r for r in results if r.error_count == 0]) == len(results)
        message = "All rules processed successfully" if success else "Some rules had errors"
        
        logger.info(f"Processed {len(results)} rules for user {current_user.get('email')}")
        
        return ProcessingResultResponse(
            success=success,
            message=message,
            results=results,
            overall_stats=overall_stats
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Process rules error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process rules"
        )


@router.post("/rules/validate")
async def validate_rules(
    request: ProcessRulesRequest,
    gmail_client: GmailClient = Depends(require_gmail_client),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine)
):
    """Validate rules without executing them (dry run with analysis)."""
    try:
        # Force dry run for validation
        request.dry_run = True
        
        # Create email processor
        processor = EmailProcessor(
            gmail_client=gmail_client,
            rules_engine=rules_engine
        )
        
        if request.rule_ids:
            rules_to_validate = []
            for rule_id in request.rule_ids:
                rule = rules_engine.get_rule(rule_id)
                if not rule:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Rule not found: {rule_id}"
                    )
                rules_to_validate.append(rule)
        else:
            rules_to_validate = rules_engine.get_enabled_rules()
        
        validation_results = []
        
        for rule in rules_to_validate:
            try:
                # Build query to test syntax
                query = rules_engine.build_gmail_query(rule.criteria)
                
                # Test search (limited to 10 results for validation)
                search_result = gmail_client.search_messages(
                    query=query,
                    max_results=10
                )
                
                validation_results.append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'valid': True,
                    'query': query,
                    'sample_matches': len(search_result.get('messages', [])),
                    'estimated_total': search_result.get('resultSizeEstimate', 0),
                    'errors': []
                })
                
            except Exception as e:
                validation_results.append({
                    'rule_id': rule.id,
                    'rule_name': rule.name,
                    'valid': False,
                    'query': '',
                    'sample_matches': 0,
                    'estimated_total': 0,
                    'errors': [str(e)]
                })
        
        # Clean up processor
        processor.close()
        
        all_valid = all(result['valid'] for result in validation_results)
        
        return {
            'success': all_valid,
            'message': 'All rules are valid' if all_valid else 'Some rules have errors',
            'results': validation_results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Validate rules error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate rules"
        )


@router.post("/batch", response_model=BatchOperationResponse)
async def batch_operation(
    request: BatchOperationRequest,
    gmail_client: GmailClient = Depends(require_gmail_client),
    current_user: dict = Depends(get_current_user)
):
    """Perform batch operation on messages."""
    try:
        operation = request.operation.lower()
        message_ids = request.message_ids
        parameters = request.parameters
        
        start_time = time.time()
        
        if operation == 'delete':
            result = gmail_client.move_to_trash(message_ids)
        elif operation == 'mark_read':
            result = gmail_client.mark_messages_read(message_ids)
        elif operation == 'add_label':
            labels = parameters.get('labels', [])
            if not labels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Labels parameter required for add_label operation"
                )
            result = gmail_client.add_labels(message_ids, labels)
        elif operation == 'remove_label':
            labels = parameters.get('labels', [])
            if not labels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Labels parameter required for remove_label operation"
                )
            result = gmail_client.remove_labels(message_ids, labels)
        elif operation == 'archive':
            # Archive by removing INBOX label
            result = gmail_client.remove_labels(message_ids, ['INBOX'])
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown operation: {operation}"
            )
        
        execution_time = time.time() - start_time
        
        logger.info(
            f"Batch {operation} completed: {result.succeeded}/{result.processed} messages "
            f"for user {current_user.get('email')}"
        )
        
        return BatchOperationResponse(
            success=result.failed == 0,
            processed=result.processed,
            succeeded=result.succeeded,
            failed=result.failed,
            errors=result.errors,
            execution_time=execution_time
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch operation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch operation failed"
        )


import time