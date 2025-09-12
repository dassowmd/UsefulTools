"""Email analysis API routes."""

import logging
from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends, Query

from ..dependencies import require_gmail_client, get_authenticated_rules_engine, get_current_user
from ..models import (
    AnalysisRequest, AnalysisResponse, SenderAnalysis,
    SearchMessagesRequest, SearchMessagesResponse, MessageSummary
)
from ...core.client import GmailClient
from ...core.processor import EmailProcessor
from ...rules.engine import RulesEngine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/mailbox", response_model=AnalysisResponse)
async def analyze_mailbox(
    request: AnalysisRequest,
    gmail_client: GmailClient = Depends(require_gmail_client),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine),
    current_user: dict = Depends(get_current_user)
):
    """Analyze mailbox to provide insights and suggestions."""
    try:
        # Create email processor for analysis
        processor = EmailProcessor(
            gmail_client=gmail_client,
            rules_engine=rules_engine
        )
        
        # Run analysis
        analysis_data = await processor.analyze_mailbox(
            max_messages=request.max_messages
        )
        
        if 'error' in analysis_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=analysis_data['error']
            )
        
        # Convert to response format
        top_senders = []
        total_analyzed = analysis_data.get('total_messages', 0)
        
        for domain, count in analysis_data.get('top_sender_domains', []):
            percentage = (count / total_analyzed * 100) if total_analyzed > 0 else 0
            top_senders.append(SenderAnalysis(
                domain=domain,
                count=count,
                percentage=round(percentage, 2)
            ))
        
        # Generate suggestions if requested
        suggestions = None
        if request.include_suggestions:
            suggestions = rules_engine.get_rule_suggestions(analysis_data)
        
        # Clean up processor
        processor.close()
        
        logger.info(f"Analyzed mailbox for user {current_user.get('email')}: {total_analyzed} messages")
        
        return AnalysisResponse(
            total_messages=analysis_data.get('total_messages', 0),
            unread_messages=analysis_data.get('unread_messages', 0),
            old_messages=analysis_data.get('old_messages', 0),
            unique_senders=analysis_data.get('unique_senders', 0),
            top_sender_domains=top_senders,
            analysis_date=datetime.now(),
            suggestions=suggestions
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Mailbox analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze mailbox"
        )


@router.post("/search", response_model=SearchMessagesResponse)
async def search_messages(
    request: SearchMessagesRequest,
    gmail_client: GmailClient = Depends(require_gmail_client),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine),
    current_user: dict = Depends(get_current_user)
):
    """Search messages using query or criteria."""
    try:
        # Build search query
        if request.query:
            search_query = request.query
        elif request.criteria:
            # Convert criteria to Gmail query
            criteria_dict = request.criteria.dict(by_alias=True, exclude_none=True)
            from ...rules.models import RuleCriteria
            criteria_obj = RuleCriteria.from_dict(criteria_dict)
            search_query = rules_engine.build_gmail_query(criteria_obj)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either 'query' or 'criteria' must be provided"
            )
        
        # Search messages
        search_result = gmail_client.search_messages(
            query=search_query,
            max_results=request.max_results,
            page_token=request.page_token
        )
        
        # Get message details for first batch
        messages = []
        message_ids = [msg['id'] for msg in search_result.get('messages', [])]
        
        for message_id in message_ids:
            message_details = gmail_client.get_message_details(message_id)
            if message_details:
                messages.append(MessageSummary(
                    id=message_details.id,
                    thread_id=message_details.thread_id,
                    sender=message_details.sender,
                    recipient=message_details.recipient,
                    subject=message_details.subject,
                    date=message_details.date,
                    labels=message_details.labels,
                    snippet=message_details.snippet,
                    is_unread=message_details.is_unread
                ))
        
        logger.info(
            f"Search returned {len(messages)} messages for user {current_user.get('email')} "
            f"with query: {search_query[:100]}"
        )
        
        return SearchMessagesResponse(
            messages=messages,
            next_page_token=search_result.get('nextPageToken'),
            result_count=len(messages),
            estimated_total=search_result.get('resultSizeEstimate', 0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search messages error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search messages"
        )


@router.get("/labels")
async def list_labels(
    gmail_client: GmailClient = Depends(require_gmail_client),
    current_user: dict = Depends(get_current_user)
):
    """List all available Gmail labels."""
    try:
        labels = gmail_client.get_labels()
        
        # Format labels for response
        formatted_labels = []
        for label in labels:
            formatted_labels.append({
                'id': label.get('id'),
                'name': label.get('name'),
                'type': label.get('type'),
                'messages_total': label.get('messagesTotal', 0),
                'messages_unread': label.get('messagesUnread', 0),
                'threads_total': label.get('threadsTotal', 0),
                'threads_unread': label.get('threadsUnread', 0)
            })
        
        logger.info(f"Retrieved {len(formatted_labels)} labels for user {current_user.get('email')}")
        
        return {
            'labels': formatted_labels,
            'total': len(formatted_labels)
        }
    
    except Exception as e:
        logger.error(f"List labels error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve labels"
        )


@router.get("/stats")
async def get_mailbox_stats(
    gmail_client: GmailClient = Depends(require_gmail_client),
    current_user: dict = Depends(get_current_user)
):
    """Get basic mailbox statistics."""
    try:
        # Get user profile for basic stats
        user_info = current_user
        
        # Get additional stats by searching
        stats = {
            'total_messages': user_info.get('messages_total', 0),
            'total_threads': user_info.get('threads_total', 0),
        }
        
        # Get unread count
        try:
            unread_result = gmail_client.search_messages(
                query='is:unread',
                max_results=1
            )
            stats['unread_messages'] = unread_result.get('resultSizeEstimate', 0)
        except Exception as e:
            logger.warning(f"Failed to get unread count: {e}")
            stats['unread_messages'] = 0
        
        # Get inbox count
        try:
            inbox_result = gmail_client.search_messages(
                query='in:inbox',
                max_results=1
            )
            stats['inbox_messages'] = inbox_result.get('resultSizeEstimate', 0)
        except Exception as e:
            logger.warning(f"Failed to get inbox count: {e}")
            stats['inbox_messages'] = 0
        
        # Get sent count
        try:
            sent_result = gmail_client.search_messages(
                query='in:sent',
                max_results=1
            )
            stats['sent_messages'] = sent_result.get('resultSizeEstimate', 0)
        except Exception as e:
            logger.warning(f"Failed to get sent count: {e}")
            stats['sent_messages'] = 0
        
        logger.info(f"Retrieved mailbox stats for user {current_user.get('email')}")
        
        return stats
    
    except Exception as e:
        logger.error(f"Get mailbox stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve mailbox statistics"
        )


@router.post("/preview-rule")
async def preview_rule_results(
    rule_data: dict,
    max_results: int = Query(50, ge=1, le=500),
    gmail_client: GmailClient = Depends(require_gmail_client),
    rules_engine: RulesEngine = Depends(get_authenticated_rules_engine),
    current_user: dict = Depends(get_current_user)
):
    """Preview what messages would be affected by a rule."""
    try:
        # Convert rule data to criteria
        from ...rules.models import RuleCriteria
        criteria = RuleCriteria.from_dict(rule_data.get('criteria', {}))
        
        # Build search query
        search_query = rules_engine.build_gmail_query(criteria)
        
        # Search for matching messages
        search_result = gmail_client.search_messages(
            query=search_query,
            max_results=max_results
        )
        
        # Get message summaries
        messages = []
        message_ids = [msg['id'] for msg in search_result.get('messages', [])]
        
        for message_id in message_ids[:min(20, len(message_ids))]:  # Limit details to 20
            message_details = gmail_client.get_message_details(message_id)
            if message_details:
                messages.append({
                    'id': message_details.id,
                    'sender': message_details.sender,
                    'subject': message_details.subject,
                    'date': message_details.date.isoformat() if message_details.date else None,
                    'snippet': message_details.snippet,
                    'is_unread': message_details.is_unread
                })
        
        logger.info(
            f"Rule preview found {search_result.get('resultSizeEstimate', 0)} matches "
            f"for user {current_user.get('email')}"
        )
        
        return {
            'query': search_query,
            'total_matches': search_result.get('resultSizeEstimate', 0),
            'sample_messages': messages,
            'sample_count': len(messages)
        }
    
    except Exception as e:
        logger.error(f"Preview rule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to preview rule results"
        )