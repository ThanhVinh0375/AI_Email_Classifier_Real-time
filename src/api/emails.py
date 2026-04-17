"""API routes for querying processed emails"""
from fastapi import APIRouter, Query, HTTPException, status
from typing import List, Optional
from datetime import datetime
from src.models.database import ProcessedEmail, ClassificationLabel
from src.services import get_mongo_service
from src.utils import get_logger

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
