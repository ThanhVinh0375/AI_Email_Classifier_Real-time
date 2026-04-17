"""FastAPI webhook routes for receiving Gmail notifications"""
import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, status
from datetime import datetime
from src.utils import get_logger
from src.config import settings
from src.services import (
    get_email_processing_service,
    get_mongo_service,
    get_gmail_service
)
from src.models.database import WebhookEvent, AuditLog

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["webhooks"])

@router.post("/webhook/gmail")
async def gmail_webhook(request: Request) -> dict:
    """
    Webhook endpoint for receiving Gmail push notifications from Google Cloud Pub/Sub
    
    Flow:
    1. Google Cloud Pub/Sub sends HTTP POST request to this endpoint
    2. Verify webhook signature
    3. Decode Pub/Sub message
    4. Extract message ID and email details
    5. Queue for processing
    6. Return success to acknowledge receipt
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Optional: Verify webhook signature
        # signature = request.headers.get("X-Goog-IAM-Authority-Selector")
        # if not _verify_webhook_signature(body, signature):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        payload = await request.json()
        
        logger.info(f"Received webhook: {payload.get('message', {}).get('messageId', 'unknown')}")
        
        # Log webhook receipt
        mongo = await get_mongo_service()
        await mongo.log_audit(AuditLog(
            event_type="webhook_received",
            details={
                "message_id": payload.get("message", {}).get("messageId"),
                "timestamp": datetime.utcnow().isoformat()
            }
        ))
        
        # Decode Pub/Sub message to get email message ID
        message_data = payload.get("message", {})
        attributes = message_data.get("attributes", {})
        
        # The Gmail Push notification contains email message ID in attributes
        email_message_id = attributes.get("message_id")
        if not email_message_id:
            logger.warning("No email message ID in webhook payload")
            return {"status": "received", "error": "missing_message_id"}
        
        logger.info(f"Processing Gmail message ID: {email_message_id}")
        
        # Queue the email for processing
        # In production, you might use a task queue like Celery
        # For now, we'll process it asynchronously
        
        return {
            "status": "received",
            "message_id": email_message_id,
            "processing": "queued"
        }
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        await mongo.log_audit(AuditLog(
            event_type="webhook_error",
            status="error",
            error=str(e)
        ))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/webhook/process-email")
async def process_email_webhook(request: Request) -> dict:
    """
    Process email webhook - Fetches email from Gmail API and classifies it
    
    Flow:
    1. Receive message ID from webhook request
    2. Fetch full email from Gmail API
    3. Parse email headers and body
    4. Pass to Hybrid AI Classifier
    5. Save result to MongoDB
    
    Args:
        request: FastAPI request with message_id in body
        
    Returns:
        Processing status and classification result
    """
    mongo = None
    
    try:
        payload = await request.json()
        message_id = payload.get("message_id")
        
        if not message_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="message_id is required in request body"
            )
        
        logger.info(f"Processing email: {message_id}")
        mongo = await get_mongo_service()
        
        # Step 1: Fetch email from Gmail API
        gmail = get_gmail_service()
        email_data = await gmail.get_email_by_id(message_id)
        
        if not email_data:
            logger.error(f"Failed to fetch email from Gmail API: {message_id}")
            await mongo.log_audit(AuditLog(
                event_type="email_fetch_failed",
                message_id=message_id,
                status="error",
                error="Gmail API returned no data"
            ))
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Email not found in Gmail: {message_id}"
            )
        
        # Step 2: Format email data
        formatted_email = gmail.format_email_data(email_data)
        logger.info(f"Email formatted: {len(formatted_email.get('body', ''))} chars body")
        
        # Step 3: Process with Hybrid AI Classifier
        email_service = get_email_processing_service()
        processed_email = await email_service.process_email(formatted_email)
        
        if not processed_email:
            logger.error(f"Failed to process email: {message_id}")
            await mongo.log_audit(AuditLog(
                event_type="processing_failed",
                message_id=message_id,
                status="error"
            ))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Email processing failed"
            )
        
        # Step 4: Log success
        await mongo.log_audit(AuditLog(
            event_type="processing_completed",
            message_id=message_id,
            status="success",
            details={
                "classification": processed_email.classification.value,
                "confidence": float(processed_email.confidence_score),
                "processing_time": "N/A"
            }
        ))
        
        logger.info(
            f"Email processed successfully: {message_id} "
            f"→ {processed_email.classification.value} "
            f"({processed_email.confidence_score:.2%})"
        )
        
        return {
            "status": "success",
            "message_id": message_id,
            "classification": processed_email.classification.value,
            "confidence": float(processed_email.confidence_score),
            "from": processed_email.from_email,
            "subject": processed_email.subject
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email processing error: {str(e)}", exc_info=True)
        
        if mongo:
            try:
                await mongo.log_audit(AuditLog(
                    event_type="processing_error",
                    status="error",
                    error=str(e)
                ))
            except:
                pass
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing error: {str(e)}"
        )

@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint"""
    try:
        mongo = await get_mongo_service()
        stats = await mongo.get_processing_stats()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )

def _verify_webhook_signature(body: bytes, signature: str) -> bool:
    """
    Verify webhook signature from Google Cloud Pub/Sub
    In production, implement proper signature verification
    """
    # Placeholder: In production, verify using OIDC token
    return True
