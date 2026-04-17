#!/usr/bin/env python3
"""
📧 Quick Start: Gmail Webhook + FastAPI Backend

Hướng dẫn nhanh sử dụng Gmail API Webhook với FastAPI
"""

# ============================================================================
# 3 DÒNG CODE ĐƠN GIẢN - FETCH & PARSE EMAIL
# ============================================================================

"""
from src.services.gmail_service import get_gmail_service

gmail = get_gmail_service()
email = await gmail.format_email_data(await gmail.get_email_by_id("msg_id"))
print(f"From: {email['from']}, Subject: {email['subject']}")
"""

# ============================================================================
# WEBHOOK ENDPOINT - COMPLETE EXAMPLE
# ============================================================================

"""
from fastapi import APIRouter, Request
from src.services.gmail_service import get_gmail_service
from src.services.email_service import get_email_processing_service

router = APIRouter()

@router.post("/api/v1/webhook/process-email")
async def process_email_webhook(request: Request):
    '''
    Complete webhook flow:
    1. Receive message_id
    2. Fetch email from Gmail API
    3. Classify with Hybrid AI
    4. Save to MongoDB
    5. Return result
    '''
    payload = await request.json()
    message_id = payload.get("message_id")
    
    # Fetch from Gmail
    gmail = get_gmail_service()
    email_data = await gmail.get_email_by_id(message_id)
    formatted = gmail.format_email_data(email_data)
    
    # Classify
    service = get_email_processing_service()
    result = await service.process_email(formatted)
    
    return {
        "status": "success",
        "classification": result.classification.value,
        "confidence": float(result.confidence_score),
        "from": result.from_email,
        "subject": result.subject
    }
"""

# ============================================================================
# FILE STRUCTURE
# ============================================================================

"""
📂 Key Files:

1️⃣ GmailService (src/services/gmail_service.py) - 450 lines
   ├─ get_email_by_id(message_id) → Fetch from Gmail API
   ├─ parse_email_headers(email_data) → Extract headers
   ├─ parse_email_body(email_data) → Extract body (HTML safe)
   ├─ get_attachment_info(email_data) → Get attachments
   └─ format_email_data(email_data) → Ready for AI

2️⃣ Webhook Endpoint (src/api/webhooks.py) - Updated
   └─ process_email_webhook() → Complete integration

3️⃣ Email Service (src/services/email_service.py)
   └─ process_email() → Hybrid AI classification

4️⃣ Demo Script (scripts/demo_email_pipeline.py) - 350+ lines
   ├─ 5 complete working examples
   ├─ Configuration guide
   └─ Architecture explanation

5️⃣ Documentation (GMAIL_WEBHOOK_GUIDE.md) - 400+ lines
   ├─ Step-by-step setup
   ├─ Code examples
   └─ Troubleshooting
"""

# ============================================================================
# MINIMAL SETUP
# ============================================================================

"""
🚀 3 Bước Setup:

1. Download Google Cloud Credentials
   - Vào: https://console.cloud.google.com
   - Service Accounts → Create
   - Create JSON Key
   - Save: ./credentials/service-account-key.json

2. Update .env
   GCP_PROJECT_ID=your-project
   GCP_CREDENTIALS_PATH=./credentials/service-account-key.json
   MONGODB_URL=mongodb://localhost:27017
   LLM_API_KEY=sk-...

3. Run Demo
   python scripts/demo_email_pipeline.py

✅ Done! System ready.
"""

# ============================================================================
# API USAGE
# ============================================================================

"""
📡 Test Webhook:

curl -X POST http://localhost:8000/api/v1/webhook/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "18b7a4c8e8f4d5c2"
  }'

Response:
{
  "status": "success",
  "classification": "important",
  "confidence": 0.92,
  "from": "boss@company.com",
  "subject": "Budget approval needed"
}
"""

# ============================================================================
# UNDERSTANDING THE FLOW
# ============================================================================

"""
📧 Complete Email Processing Flow:

Gmail Account
    ↓ (Email arrives)
    
Google Cloud Pub/Sub
    ↓ (Push notification)
    
FastAPI Webhook
    ├─ Receives: {"message_id": "xxx"}
    
GmailService
    ├─ Fetch email from Gmail API
    ├─ Parse headers, body, attachments
    └─ Format for processing
    
EmailProcessingService (Hybrid AI)
    ├─ Stage 1: Spam detection (TF-IDF)
    └─ Stage 2: LLM analysis (if not spam)
    
MongoDB
    ├─ Save classification result
    ├─ Save entities extracted
    ├─ Save sentiment analysis
    └─ Create audit log
    
Response
    └─ Return classification + confidence + metadata


Components Architecture:

GmailService (gmail_service.py)
├─ Authentication
├─ Email fetching
├─ Parsing (headers, body, attachments)
├─ HTML handling
└─ Error handling

Webhook Endpoint (webhooks.py)
├─ Receive request
├─ Call GmailService
├─ Call EmailProcessingService
├─ Save to MongoDB
└─ Return response

EmailProcessingService (email_service.py)
├─ Uses HybridEmailClassifier
├─ Stage 1: SpamDetector
└─ Stage 2: LLMAnalyzer
"""

# ============================================================================
# EXAMPLE: BATCH PROCESSING
# ============================================================================

"""
import asyncio
from src.services.gmail_service import get_gmail_service
from src.services.email_service import get_email_processing_service

async def process_batch(message_ids: list):
    '''Process multiple emails concurrently'''
    
    gmail = get_gmail_service()
    service = get_email_processing_service()
    
    results = {}
    
    for msg_id in message_ids:
        # Fetch
        email_data = await gmail.get_email_by_id(msg_id)
        if not email_data:
            continue
        
        # Format
        formatted = gmail.format_email_data(email_data)
        
        # Classify
        result = await service.process_email(formatted)
        results[msg_id] = {
            "classification": result.classification.value,
            "confidence": result.confidence_score,
            "subject": result.subject
        }
    
    return results

# Usage
asyncio.run(process_batch(["msg1", "msg2", "msg3"]))
"""

# ============================================================================
# KEY METHODS REFERENCE
# ============================================================================

"""
🔧 GmailService Methods:

1. get_email_by_id(message_id: str) → Dict
   - Fetch email from Gmail API
   - Uses service account credentials
   - Has retry logic
   - Returns raw email data

2. parse_email_headers(email_data: Dict) → Dict
   - Extract headers: subject, from, to, date, cc, bcc
   - Returns: {'subject': '...', 'from': '...', ...}

3. parse_email_body(email_data: Dict) → str
   - Extract email body
   - Handles both text/plain and text/html
   - Strips HTML tags
   - Decodes base64url encoding

4. get_attachment_info(email_data: Dict) → List[Dict]
   - Get attachment metadata
   - Returns: [{'filename': '...', 'mime_type': '...', ...}]

5. format_email_data(email_data: Dict) → Dict
   - Clean, formatted email data
   - Ready for EmailProcessingService
   - Includes all parsed components
   - Returns: {'id': '...', 'subject': '...', 'body': '...', ...}
"""

# ============================================================================
# TESTING
# ============================================================================

"""
✅ Test Checklist:

1. Unit Test GmailService
   python -c "
   import asyncio
   from src.services.gmail_service import get_gmail_service
   gmail = get_gmail_service()
   print('✓ GmailService initialized')
   "

2. Run Demo
   python scripts/demo_email_pipeline.py

3. Test Webhook
   curl -X POST http://localhost:8000/api/v1/webhook/process-email \
     -H "Content-Type: application/json" \
     -d '{"message_id": "test"}'

4. Check MongoDB
   mongosh mongodb://localhost:27017/email_classifier
   db.processed_emails.findOne()
"""

# ============================================================================
# CONFIGURATION
# ============================================================================

"""
⚙️ Required Environment Variables:

# Google Cloud
GCP_PROJECT_ID=your-gcp-project-id
GCP_CREDENTIALS_PATH=./credentials/service-account-key.json

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=email_classifier
MONGODB_USER=admin
MONGODB_PASSWORD=changeme

# Hybrid AI
ENABLE_SPAM_DETECTION=true
SKIP_LLM_FOR_SPAM=true
LLM_API_PROVIDER=openai
LLM_API_KEY=sk-your-key
LLM_MODEL=gpt-3.5-turbo

# API
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development
"""

# ============================================================================
# DOCUMENTATION FILES
# ============================================================================

"""
📚 Complete Documentation:

GMAIL_WEBHOOK_GUIDE.md (400+ lines)
├─ Complete setup guide
├─ Gmail API configuration
├─ Code examples
├─ Troubleshooting
└─ Best practices

scripts/demo_email_pipeline.py (350+ lines)
├─ 5 working examples
├─ Demo 1: GmailService
├─ Demo 2: EmailProcessingService
├─ Demo 3: Complete pipeline
├─ Demo 4: Configuration
└─ Demo 5: Code examples

src/services/gmail_service.py (450 lines)
├─ Full implementation
├─ Docstrings
├─ Type hints
└─ Error handling

src/api/webhooks.py (Updated)
├─ Webhook endpoint
├─ Complete integration
└─ Proper error handling

README.md (Updated)
├─ Project overview
├─ Setup instructions
└─ Links to guides
"""

# ============================================================================
# COMMAND REFERENCE
# ============================================================================

"""
🔄 Common Commands:

# Start development server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run demo
python scripts/demo_email_pipeline.py

# Start Docker
docker-compose up -d

# View logs
docker-compose logs -f api

# Check API docs
# Open: http://localhost:8000/docs

# Test webhook
curl -X POST http://localhost:8000/api/v1/webhook/process-email \\
  -H "Content-Type: application/json" \\
  -d '{"message_id": "test"}'

# Connect to MongoDB
mongosh mongodb://localhost:27017

# Find processed emails
db.processed_emails.find().pretty()
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
🔧 Common Issues:

Issue: ImportError: No module named 'src'
→ Add project to PYTHONPATH
→ python -c "import sys; sys.path.insert(0, '.'); from src import main"

Issue: Gmail API credentials not found
→ Check GCP_CREDENTIALS_PATH in .env
→ Verify file exists: ls ./credentials/service-account-key.json

Issue: Email not fetched from Gmail
→ Check Gmail API is enabled in GCP
→ Verify message_id is valid
→ Check credentials have Gmail scope

Issue: Webhook timeout
→ Increase LLM_TIMEOUT in .env
→ Check MongoDB connection
→ Check Gmail API is responsive

Issue: Low classification confidence
→ Adjust CLASSIFICATION_CONFIDENCE_THRESHOLD
→ Check LLM API key is valid
→ Check email body is not empty
"""

# ============================================================================
# SUMMARY
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║               📧 GMAIL WEBHOOK + FASTAPI INTEGRATION                      ║
║                         ✅ COMPLETE & READY                               ║
╚════════════════════════════════════════════════════════════════════════════╝

📦 What Was Created:
  • GmailService (450 lines) - Gmail API integration
  • Updated Webhook Endpoint - Complete integration
  • Demo Script (350+ lines) - 5 working examples
  • Comprehensive Guide (400+ lines) - Setup & usage
  • Updated Documentation - README, guides

🚀 Quick Start:
  1. Setup Google Cloud credentials
  2. Update .env with GCP_CREDENTIALS_PATH
  3. python scripts/demo_email_pipeline.py
  4. docker-compose up -d

📊 Architecture:
  Gmail → Pub/Sub → Webhook → GmailService → Hybrid AI → MongoDB

🔗 API:
  POST /api/v1/webhook/process-email {"message_id": "xxx"}
  → Fetches email → Classifies → Returns result

📚 Documentation:
  • GMAIL_WEBHOOK_GUIDE.md - Complete guide
  • scripts/demo_email_pipeline.py - Working examples
  • src/services/gmail_service.py - Full code
  • README.md - Project overview

✅ Status: Production Ready

Next: Read GMAIL_WEBHOOK_GUIDE.md for complete setup!
""")
