"""Test cases for email classification system"""
import pytest
from datetime import datetime
from src.models.database import ProcessedEmail, ClassificationLabel, AuditLog

class TestDataModels:
    """Test data models"""
    
    def test_processed_email_creation(self):
        """Test ProcessedEmail model creation"""
        email = ProcessedEmail(
            message_id="test_123",
            thread_id="thread_456",
            subject="Test Email",
            from_email="sender@example.com",
            to_emails=["recipient@example.com"],
            body="Test body",
            received_date=datetime.utcnow(),
            classification=ClassificationLabel.IMPORTANT,
            confidence_score=0.95
        )
        
        assert email.message_id == "test_123"
        assert email.classification == ClassificationLabel.IMPORTANT
        assert email.confidence_score == 0.95
        assert email.status == "completed"
    
    def test_classification_labels(self):
        """Test classification label enum"""
        labels = [
            ClassificationLabel.SPAM,
            ClassificationLabel.PROMOTIONAL,
            ClassificationLabel.SOCIAL,
            ClassificationLabel.IMPORTANT,
            ClassificationLabel.GENERAL
        ]
        
        assert len(labels) == 5
        assert ClassificationLabel.SPAM == "spam"

class TestEmailProcessing:
    """Test email processing logic"""
    
    @pytest.mark.asyncio
    async def test_email_header_extraction(self):
        """Test email header extraction"""
        from src.services.email_service import EmailProcessingService
        
        service = EmailProcessingService()
        
        email_data = {
            "id": "msg_123",
            "threadId": "thread_123",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "Test Subject"},
                    {"name": "From", "value": "sender@example.com"},
                    {"name": "To", "value": "recipient@example.com"},
                    {"name": "Date", "value": "2024-01-15T10:00:00Z"}
                ]
            }
        }
        
        headers = service._extract_headers(email_data)
        
        assert headers["subject"] == "Test Subject"
        assert headers["from"] == "sender@example.com"

@pytest.fixture
def mongodb_client():
    """MongoDB test client fixture"""
    # In production, use test MongoDB instance
    pass

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
