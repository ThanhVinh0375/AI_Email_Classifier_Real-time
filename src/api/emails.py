"""API routes for querying processed emails"""
from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime
from src.models.database import ProcessedEmail, ClassificationLabel, ClassifiedEmail, ExtractedEntity, SentimentAnalysis
from src.services import get_mongo_service
from src.utils import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["emails"])

@router.get("/emails", response_model=List[dict])
async def get_emails(
    classification: Optional[str] = Query(None, description="Filter by classification"),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
) -> List[dict]:
    """Get processed emails with optional filtering"""
    try:
        mongo = await get_mongo_service()
        
        if classification:
            # Validate classification
            try:
                ClassificationLabel(classification)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid classification: {classification}"
                )
            
            emails = await mongo.get_emails_by_classification(classification, limit)
        else:
            # Get all emails
            collection = mongo.db["processed_emails"]
            cursor = collection.find().skip(skip).limit(limit)
            emails = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for email in emails:
            email["_id"] = str(email.get("_id", ""))
        
        return emails
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving emails: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emails"
        )

@router.get("/emails/{message_id}", response_model=dict)
async def get_email(message_id: str) -> dict:
    """Get specific email by message ID"""
    try:
        mongo = await get_mongo_service()
        email = await mongo.get_email(message_id)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email {message_id} not found"
            )
        
        email["_id"] = str(email.get("_id", ""))
        return email
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving email {message_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve email"
        )

@router.get("/emails/sender/{from_email}", response_model=List[dict])
async def get_emails_from_sender(
    from_email: str,
    limit: int = Query(50, ge=1, le=500)
) -> List[dict]:
    """Get emails from specific sender"""
    try:
        mongo = await get_mongo_service()
        emails = await mongo.get_emails_by_sender(from_email, limit)
        
        for email in emails:
            email["_id"] = str(email.get("_id", ""))
        
        return emails
        
    except Exception as e:
        logger.error(f"Error retrieving emails from {from_email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve emails"
        )

@router.get("/stats", response_model=dict)
async def get_classification_stats() -> dict:
    """Get classification statistics"""
    try:
        mongo = await get_mongo_service()
        stats = await mongo.get_processing_stats()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


# ==================== CLASSIFIED EMAILS ENDPOINTS ====================

@router.post("/emails/classify-and-save", response_model=dict, status_code=status.HTTP_201_CREATED)
async def classify_and_save_email(classified_email: ClassifiedEmail) -> dict:
    """
    Classify and save an email to the database.
    
    This endpoint accepts a completely classified email with all analysis results
    (summary, extracted entities, sentiment analysis) and persists it to MongoDB.
    
    Request body example:
    {
        "email_id": "msg_abc123xyz",
        "sender": "john@example.com",
        "subject": "Q1 Budget Review Meeting",
        "body_text": "Hi, we need to schedule the Q1 budget review...",
        "classification_label": "work",
        "summary": "Scheduling request for Q1 budget review meeting",
        "extracted_entities": [
            {"entity_type": "deadline", "value": "Next Friday", "confidence": 0.95},
            {"entity_type": "requester", "value": "John Doe", "confidence": 0.98}
        ],
        "sentiment_analysis": {
            "sentiment": "neutral",
            "score": 50,
            "urgency_level": "high"
        },
        "processing_time_ms": 245.3,
        "confidence_score": 0.92
    }
    
    Returns:
        {
            "message": "Email classified and saved successfully",
            "email_id": "msg_abc123xyz",
            "classification": "work",
            "timestamp": "2026-04-17T10:30:45.123456",
            "status": "completed"
        }
    """
    try:
        mongo = await get_mongo_service()
        
        # Save classified email to MongoDB
        email_id = await mongo.save_classified_email(classified_email)
        
        logger.info(f"Successfully saved classified email: {email_id}")
        
        return {
            "message": "Email classified and saved successfully",
            "email_id": email_id,
            "classification": classified_email.classification_label.value,
            "confidence_score": classified_email.confidence_score,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email data: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error saving classified email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save classified email"
        )


@router.get("/classified-emails/{email_id}", response_model=dict)
async def get_classified_email(email_id: str) -> dict:
    """
    Retrieve a classified email by email_id.
    
    Args:
        email_id: Unique email identifier
        
    Returns:
        Complete classified email document with all analysis results
    """
    try:
        mongo = await get_mongo_service()
        email = await mongo.get_classified_email_by_id(email_id)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Classified email '{email_id}' not found"
            )
        
        email["_id"] = str(email.get("_id", ""))
        return email
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving classified email {email_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classified email"
        )


@router.get("/classified-emails/sender/{sender}", response_model=List[dict])
async def get_classified_emails_from_sender(
    sender: str,
    limit: int = Query(50, ge=1, le=500),
    skip: int = Query(0, ge=0)
) -> List[dict]:
    """
    Retrieve classified emails from a specific sender with pagination.
    
    Args:
        sender: Sender email address
        limit: Maximum number of results (default 50)
        skip: Number of results to skip for pagination
        
    Returns:
        List of classified email documents
    """
    try:
        mongo = await get_mongo_service()
        emails = await mongo.get_classified_emails_by_sender(sender, limit, skip)
        
        for email in emails:
            email["_id"] = str(email.get("_id", ""))
        
        return emails
        
    except Exception as e:
        logger.error(f"Error retrieving classified emails from {sender}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classified emails"
        )


@router.get("/classified-emails/label/{label}", response_model=List[dict])
async def get_classified_emails_by_label(
    label: str,
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0)
) -> List[dict]:
    """
    Retrieve classified emails by classification label (work, personal, spam, etc).
    
    Args:
        label: Classification label to filter by
        limit: Maximum number of results
        skip: Number of results to skip for pagination
        
    Returns:
        List of classified email documents matching the label
    """
    try:
        # Validate classification label
        try:
            ClassificationLabel(label)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid classification label: {label}. Must be one of: {', '.join([c.value for c in ClassificationLabel])}"
            )
        
        mongo = await get_mongo_service()
        emails = await mongo.get_classified_emails_by_label(label, limit, skip)
        
        for email in emails:
            email["_id"] = str(email.get("_id", ""))
        
        return emails
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving emails by label {label}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classified emails"
        )


@router.get("/classified-emails/stats", response_model=dict)
async def get_classified_email_stats() -> dict:
    """
    Get statistics for classified emails collection.
    
    Returns:
        {
            "total_classified_emails": 1234,
            "by_classification": {
                "work": {"count": 500, "avg_confidence": 0.89},
                "personal": {"count": 400, "avg_confidence": 0.85},
                "spam": {"count": 334, "avg_confidence": 0.92}
            },
            "avg_processing_time_ms": 245.3,
            "timestamp": "2026-04-17T10:30:45.123456"
        }
    """
    try:
        mongo = await get_mongo_service()
        stats = await mongo.get_classified_email_stats()
        
        return {
            **stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error retrieving classified email stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve classified email statistics"
        )
