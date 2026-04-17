"""Email processing service with Hybrid AI Classification

Combines:
1. Fast spam detection (Scikit-Learn TF-IDF)
2. Deep LLM analysis for legitimate emails
"""

import base64
from typing import Optional, Dict, Any
from datetime import datetime
from src.utils import get_logger, retry, log_execution
from src.models.database import ProcessedEmail, ClassificationLabel, AuditLog
from src.models.hybrid_classifier import get_hybrid_classifier
from src.services.mongodb_service import get_mongo_service
from src.config import settings
import asyncio

logger = get_logger(__name__)

class EmailProcessingService:
    """Service for processing emails using Hybrid AI"""
    
    def __init__(self):
        """Initialize email processing service"""
        self.min_confidence = settings.classification_confidence_threshold
        self.max_workers = settings.max_workers
        self.hybrid_classifier = get_hybrid_classifier()
    
    @retry(max_attempts=3, delay=1.0)
    @log_execution
    async def process_email(self, email_data: Dict[str, Any]) -> Optional[ProcessedEmail]:
        """
        Process raw email data from Gmail API using Hybrid AI
        
        Stage 1: Fast spam detection (TF-IDF + Naive Bayes)
        Stage 2: Deep LLM analysis (if not spam)
        
        Args:
            email_data: Raw email data from Gmail API
            
        Returns:
            ProcessedEmail object or None if processing failed
        """
        try:
            # Extract message ID (required)
            message_id = email_data.get("id")
            if not message_id:
                logger.error("Email missing message ID")
                return None
            
            # Log processing started
            mongo = await get_mongo_service()
            await mongo.log_audit(AuditLog(
                event_type="processing_started",
                message_id=message_id,
                details={"source": "webhook", "method": "hybrid_ai"}
            ))
            
            # Extract headers and body
            headers = self._extract_headers(email_data)
            body = self._extract_body(email_data)
            
            subject = headers.get("subject", "")
            from_email = headers.get("from", "")
            
            # Run Hybrid AI Classification
            logger.info(f"Running Hybrid AI classification for {message_id}")
            
            classification_result = await self.hybrid_classifier.classify({
                'subject': subject,
                'body': body
            })
            
            classification = classification_result['classification']
            confidence = classification_result['confidence']
            
            # Check if confidence meets threshold
            if confidence < self.min_confidence and classification != ClassificationLabel.SPAM:
                logger.warning(
                    f"Low confidence ({confidence:.2f}) for {message_id}, "
                    f"defaulting to GENERAL"
                )
                classification = ClassificationLabel.GENERAL
            
            # Create processed email document
            processed_email = ProcessedEmail(
                message_id=message_id,
                thread_id=email_data.get("threadId", ""),
                subject=subject,
                from_email=from_email,
                to_emails=headers.get("to", "").split(",") if headers.get("to") else [],
                body=body,
                received_date=datetime.fromisoformat(
                    headers.get("date", datetime.utcnow().isoformat())
                ),
                classification=classification,
                confidence_score=confidence
            )
            
            # Save to MongoDB
            await mongo.save_processed_email(processed_email)
            
            # Log completion with detailed analysis
            analysis_details = classification_result.get('analysis', {})
            await mongo.log_audit(AuditLog(
                event_type="classification_completed",
                message_id=message_id,
                details={
                    "classification": classification,
                    "confidence": confidence,
                    "is_spam": classification_result.get('is_spam', False),
                    "processing_time_ms": classification_result.get('processing_time_ms', 0),
                    "has_entities": 'entities' in classification_result,
                    "sentiment": classification_result.get('sentiment', {})
                }
            ))
            
            logger.info(
                f"Successfully processed email {message_id}: "
                f"{classification} (confidence: {confidence:.2%}, "
                f"time: {classification_result.get('processing_time_ms', 0):.0f}ms)"
            )
            
            return processed_email
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            
            # Log error
            try:
                mongo = await get_mongo_service()
                await mongo.log_audit(AuditLog(
                    event_type="error",
                    message_id=message_id,
                    status="error",
                    error=str(e)
                ))
            except:
                pass
            
            raise
    
    def _extract_headers(self, email_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract important headers from email data"""
        headers = {}
        payload = email_data.get("payload", {})
        email_headers = payload.get("headers", [])
        
        header_mapping = {
            "Subject": "subject",
            "From": "from",
            "To": "to",
            "Cc": "cc",
            "Date": "date",
            "Message-ID": "message_id"
        }
        
        for header in email_headers:
            name = header.get("name")
            value = header.get("value", "")
            if name in header_mapping:
                headers[header_mapping[name]] = value
        
        return headers
    
    def _extract_body(self, email_data: Dict[str, Any]) -> str:
        """Extract email body text"""
        payload = email_data.get("payload", {})
        
        # Handle simple case: body in payload parts
        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        try:
                            return base64.urlsafe_b64decode(data).decode('utf-8')
                        except Exception:
                            continue
        
        # Handle simple case: body directly in payload
        data = payload.get("body", {}).get("data", "")
        if data:
            try:
                return base64.urlsafe_b64decode(data).decode('utf-8')
            except Exception:
                pass
        
        return ""
    
    async def process_batch(
        self, 
        emails: list
    ) -> Dict[str, Any]:
        """
        Process batch of emails concurrently
        
        Args:
            emails: List of email data
            
        Returns:
            Processing results summary
        """
        try:
            logger.info(f"Starting batch processing for {len(emails)} emails")
            
            # Process emails concurrently with worker limit
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def process_with_semaphore(email):
                async with semaphore:
                    return await self.process_email(email)
            
            tasks = [process_with_semaphore(email) for email in emails]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Count results
            successful = sum(1 for r in results if isinstance(r, ProcessedEmail))
            failed = sum(1 for r in results if isinstance(r, Exception))
            
            logger.info(
                f"Batch processing complete: {successful} successful, "
                f"{failed} failed out of {len(emails)} total"
            )
            
            return {
                "total": len(emails),
                "successful": successful,
                "failed": failed,
                "results": results
            }
        except Exception as e:
            logger.error(f"Batch processing error: {str(e)}")
            raise
    
    def get_classifier_info(self) -> Dict[str, Any]:
        """Get hybrid classifier information"""
        return {
            "classifier_type": "hybrid_ai",
            "stages": [
                {
                    "stage": 1,
                    "name": "Spam Detection",
                    "method": "TF-IDF + Naive Bayes",
                    "enabled": settings.enable_spam_detection
                },
                {
                    "stage": 2,
                    "name": "Deep Analysis",
                    "method": f"LLM ({settings.llm_api_provider})",
                    "model": settings.llm_model,
                    "enabled": settings.enable_llm_analysis
                }
            ],
            "features": [
                "Spam Detection",
                "Summarization",
                "Named Entity Recognition (NER)",
                "Sentiment Analysis",
                "Urgency Detection"
            ]
        }

# Global instance
_email_service: Optional[EmailProcessingService] = None

def get_email_processing_service() -> EmailProcessingService:
    """Get or create email processing service"""
    global _email_service
    if _email_service is None:
        _email_service = EmailProcessingService()
    return _email_service

