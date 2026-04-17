#!/usr/bin/env python3
"""
📧 Demo: Complete Email Processing Pipeline

This demo shows:
1. How to use GmailService to fetch emails from Gmail API
2. How to process emails with Hybrid AI Classifier
3. How the entire pipeline works end-to-end

Note: This demo requires:
- GCP_CREDENTIALS_PATH set to valid service account JSON
- Gmail API enabled
- Message IDs to test with
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.gmail_service import get_gmail_service
from src.services.email_service import get_email_processing_service
from src.services.mongodb_service import get_mongo_service
from src.utils import get_logger

logger = get_logger(__name__)

# ============================================================================
# DEMO 1: Gmail Service - Fetch Email from Gmail API
# ============================================================================

async def demo_gmail_service():
    """Demo: Fetch and parse email from Gmail API"""
    print("\n" + "="*70)
    print("DEMO 1: Gmail Service - Fetch Email from Gmail API")
    print("="*70)
    
    gmail = get_gmail_service()
    
    # Example message IDs (you would get these from webhook)
    # For demo, we'll try to fetch (will fail if credentials not set)
    test_message_id = "18b7a4c8e8f4d5c2"  # Example ID
    
    print(f"\n📧 Attempting to fetch email: {test_message_id}")
    print("   (This will fail without valid GCP credentials)")
    print()
    
    try:
        email_data = await gmail.get_email_by_id(test_message_id)
        
        if email_data:
            print("✓ Email fetched successfully!")
            
            # Parse headers
            headers = gmail.parse_email_headers(email_data)
            print(f"\n📋 Headers:")
            print(f"  From: {headers.get('from', 'N/A')}")
            print(f"  To: {headers.get('to', 'N/A')}")
            print(f"  Subject: {headers.get('subject', 'N/A')}")
            print(f"  Date: {headers.get('date', 'N/A')}")
            
            # Parse body
            body = gmail.parse_email_body(email_data)
            print(f"\n📝 Body (first 200 chars):")
            print(f"  {body[:200]}...")
            
            # Get attachments
            attachments = gmail.get_attachment_info(email_data)
            print(f"\n📎 Attachments: {len(attachments)}")
            for att in attachments:
                print(f"  • {att['filename']} ({att['mime_type']})")
            
            # Format for processing
            formatted = gmail.format_email_data(email_data)
            print(f"\n✓ Email formatted and ready for processing")
            print(f"  Subject: {formatted['subject'][:50]}...")
            print(f"  Body length: {len(formatted['body'])} chars")
            
        else:
            print("⚠️  Email not found (check message ID and credentials)")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nNote: This demo requires:")
        print("  1. GCP_CREDENTIALS_PATH set in .env")
        print("  2. Gmail API enabled in Google Cloud")
        print("  3. Valid message ID from Gmail")

# ============================================================================
# DEMO 2: Email Processing Service - Hybrid AI Classification
# ============================================================================

async def demo_email_processing():
    """Demo: Process email with Hybrid AI Classifier"""
    print("\n" + "="*70)
    print("DEMO 2: Email Processing Service - Hybrid AI Classification")
    print("="*70)
    
    # Create sample email data (as would come from Gmail API)
    sample_emails = [
        {
            "id": "msg_001",
            "threadId": "thread_001",
            "subject": "URGENT: Budget approval needed by Friday EOD",
            "from": "manager@company.com",
            "to": "you@company.com",
            "body": """
            Hi,
            
            The Q2 marketing budget of $150,000 needs your approval by 
            Friday end of business. This is critical for the quarterly 
            review meeting on Monday.
            
            Can you please confirm by EOD Friday?
            
            Thanks,
            Sarah
            """,
            "received_date": "2026-04-17T10:30:00Z",
            "attachments": [],
            "labels": []
        },
        {
            "id": "msg_002",
            "threadId": "thread_002",
            "subject": "CLICK HERE: Win FREE Money - Limited Time!!!",
            "from": "spam@unknown.com",
            "to": "you@company.com",
            "body": """
            CONGRATULATIONS! You have been selected as a WINNER!
            
            Click here NOW to claim your $10,000 FREE CASH!
            This is a LIMITED TIME offer - act immediately!
            
            Don't miss out!
            """,
            "received_date": "2026-04-17T09:15:00Z",
            "attachments": [],
            "labels": []
        },
        {
            "id": "msg_003",
            "threadId": "thread_003",
            "subject": "Team lunch tomorrow - 12:30 PM",
            "from": "john@company.com",
            "to": "you@company.com",
            "body": """
            Hey! Don't forget about the team lunch tomorrow at 12:30 PM.
            We're going to that new Italian place downtown.
            
            Let me know if you can make it!
            
            John
            """,
            "received_date": "2026-04-17T08:00:00Z",
            "attachments": [],
            "labels": []
        }
    ]
    
    email_service = get_email_processing_service()
    
    print(f"\n📧 Processing {len(sample_emails)} emails with Hybrid AI Classifier\n")
    
    for i, email in enumerate(sample_emails, 1):
        print(f"Email #{i}: {email['subject'][:50]}...")
        
        try:
            result = await email_service.process_email(email)
            
            if result:
                print(f"  ✓ Classification: {result.classification.value.upper()}")
                print(f"  ✓ Confidence: {result.confidence_score:.2%}")
                print(f"  ✓ From: {result.from_email}")
                print()
            else:
                print(f"  ❌ Processing failed\n")
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}\n")

# ============================================================================
# DEMO 3: Complete Pipeline - From Webhook to Classification
# ============================================================================

async def demo_complete_pipeline():
    """Demo: Complete pipeline from webhook to storage"""
    print("\n" + "="*70)
    print("DEMO 3: Complete Pipeline - Webhook to Classification")
    print("="*70)
    
    print("\n📊 Pipeline Flow:")
    print("""
    1. Gmail sends notification (webhook) with message ID
                    ↓
    2. Webhook receives message ID
                    ↓
    3. GmailService fetches full email from Gmail API
       └─ Extracts: headers, body, attachments
                    ↓
    4. Email data is formatted and validated
                    ↓
    5. Hybrid AI Classifier processes email
       ├─ Stage 1: Spam detection (TF-IDF + Naive Bayes)
       └─ Stage 2: LLM analysis (if not spam)
                    ↓
    6. Classification result saved to MongoDB
       └─ Stores: classification, confidence, entities, sentiment
                    ↓
    7. Audit log created for tracking
                    ↓
    ✓ Pipeline Complete!
    """)
    
    print("\n🔄 Key Classes in Pipeline:")
    print("""
    1. GmailService (src/services/gmail_service.py)
       ├─ get_email_by_id() - Fetch from Gmail API
       ├─ parse_email_headers() - Extract headers
       ├─ parse_email_body() - Extract body (handles HTML)
       ├─ get_attachment_info() - Extract attachments
       └─ format_email_data() - Prepare for processing
    
    2. EmailProcessingService (src/services/email_service.py)
       ├─ process_email() - Main processing
       ├─ _extract_headers() - Parse email headers
       ├─ _extract_body() - Get email body
       └─ Integrates with HybridEmailClassifier
    
    3. HybridEmailClassifier (src/models/hybrid_classifier.py)
       ├─ Stage 1: SpamDetector
       ├─ Stage 2: LLMAnalyzer
       └─ classify() - Return classification + analysis
    
    4. MongoDBService (src/services/mongodb_service.py)
       ├─ Save processed emails
       ├─ Query by classification
       └─ Audit logging
    """)
    
    print("\n🔗 API Integration Points:")
    print("""
    POST /api/v1/webhook/gmail
    └─ Receives Pub/Sub notification with message ID
    
    POST /api/v1/webhook/process-email
    ├─ Receives: {"message_id": "xxx"}
    ├─ 1. Calls GmailService.get_email_by_id(message_id)
    ├─ 2. Calls GmailService.format_email_data(email_data)
    ├─ 3. Calls EmailProcessingService.process_email(formatted)
    ├─ 4. Logs to MongoDB
    └─ Returns: {"status": "success", "classification": "important", ...}
    
    GET /api/v1/emails
    ├─ Query processed emails
    ├─ Filter by classification
    └─ Get statistics
    """)

# ============================================================================
# DEMO 4: Configuration & Setup
# ============================================================================

async def demo_configuration():
    """Demo: Configuration requirements"""
    print("\n" + "="*70)
    print("DEMO 4: Configuration & Setup Requirements")
    print("="*70)
    
    print("\n📋 Required .env Variables:")
    print("""
    # Gmail API Setup
    GCP_PROJECT_ID=your-gcp-project-id
    GCP_CREDENTIALS_PATH=./credentials/service-account-key.json
    
    # Gmail Watch Setup
    GMAIL_USER_EMAIL=your@gmail.com
    WEBHOOK_URL=https://your-domain.com/api/v1/webhook/gmail
    
    # MongoDB
    MONGODB_URL=mongodb://localhost:27017
    MONGODB_DB_NAME=email_classifier
    
    # Hybrid AI Classification
    ENABLE_SPAM_DETECTION=true
    SKIP_LLM_FOR_SPAM=true
    LLM_API_PROVIDER=openai
    LLM_API_KEY=sk-...
    LLM_MODEL=gpt-3.5-turbo
    """)
    
    print("\n🔑 Getting GCP Credentials:")
    print("""
    1. Go to Google Cloud Console
    2. Create Service Account
    3. Create JSON Key
    4. Download and save as: ./credentials/service-account-key.json
    5. Set: GCP_CREDENTIALS_PATH=./credentials/service-account-key.json
    """)
    
    print("\n✅ Enable Gmail API:")
    print("""
    1. Google Cloud Console → APIs & Services
    2. Enable: Gmail API
    3. Create OAuth 2.0 credentials (if needed)
    4. Grant scopes: https://www.googleapis.com/auth/gmail.readonly
    """)
    
    print("\n📲 Setup Gmail Push Notifications:")
    print("""
    1. Create Pub/Sub Topic: gmail-notifications
    2. Create Subscription with Push:
       - Push endpoint: https://your-domain/api/v1/webhook/gmail
       - Service account: email-classifier-service@...
    3. Setup Gmail watch: python scripts/setup_gmail_watch.py
    """)

# ============================================================================
# DEMO 5: Code Examples
# ============================================================================

async def demo_code_examples():
    """Demo: Code usage examples"""
    print("\n" + "="*70)
    print("DEMO 5: Code Usage Examples")
    print("="*70)
    
    print("""
✅ Example 1: Using GmailService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from src.services.gmail_service import get_gmail_service

gmail = get_gmail_service()

# Fetch email by message ID
email_data = await gmail.get_email_by_id("message_id_here")

# Parse components
headers = gmail.parse_email_headers(email_data)
body = gmail.parse_email_body(email_data)
attachments = gmail.get_attachment_info(email_data)

# Format for processing
formatted = gmail.format_email_data(email_data)


✅ Example 2: Using EmailProcessingService
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from src.services.email_service import get_email_processing_service

email_service = get_email_processing_service()

# Process email (runs Hybrid AI)
result = await email_service.process_email({
    'id': 'message_id',
    'subject': '...',
    'body': '...',
    'from': '...',
    'to': '...'
})

print(f"Classification: {result.classification}")
print(f"Confidence: {result.confidence_score}")


✅ Example 3: Complete Webhook Handler
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post("/webhook/process-email")
async def process_email_webhook(request: Request):
    payload = await request.json()
    message_id = payload.get("message_id")
    
    # Fetch from Gmail
    gmail = get_gmail_service()
    email_data = await gmail.get_email_by_id(message_id)
    formatted = gmail.format_email_data(email_data)
    
    # Process with AI
    service = get_email_processing_service()
    result = await service.process_email(formatted)
    
    return {
        "status": "success",
        "classification": result.classification.value,
        "confidence": result.confidence_score
    }


✅ Example 4: Batch Processing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def process_multiple_emails(message_ids: List[str]):
    gmail = get_gmail_service()
    service = get_email_processing_service()
    
    results = []
    
    for msg_id in message_ids:
        # Fetch email
        email_data = await gmail.get_email_by_id(msg_id)
        formatted = gmail.format_email_data(email_data)
        
        # Process
        result = await service.process_email(formatted)
        results.append(result)
    
    return results
    """)

# ============================================================================
# Main
# ============================================================================

async def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("📧 COMPLETE EMAIL PROCESSING PIPELINE DEMO")
    print("="*70)
    
    # Demo 1: Gmail Service
    await demo_gmail_service()
    
    # Demo 2: Email Processing
    await demo_email_processing()
    
    # Demo 3: Complete Pipeline
    await demo_complete_pipeline()
    
    # Demo 4: Configuration
    await demo_configuration()
    
    # Demo 5: Code Examples
    await demo_code_examples()
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)
    print("""
📚 Next Steps:
  1. Read: src/services/gmail_service.py (Gmail API integration)
  2. Read: src/api/webhooks.py (Webhook endpoint)
  3. Configure: .env with GCP credentials
  4. Setup: Gmail Push notifications
  5. Deploy: docker-compose up -d
  6. Test: Send emails to your Gmail account

🔗 API Endpoints:
  POST /api/v1/webhook/gmail          - Pub/Sub notifications
  POST /api/v1/webhook/process-email  - Process email with message ID
  GET  /api/v1/emails                 - Query processed emails
  GET  /api/v1/stats                  - Get statistics

📖 Documentation:
  - HYBRID_AI_GUIDE.md               - Complete guide
  - src/services/gmail_service.py    - Gmail API service code
  - src/api/webhooks.py              - Webhook endpoint code
    """)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Demo error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
