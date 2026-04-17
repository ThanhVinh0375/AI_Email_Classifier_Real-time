# 📧 Hướng Dẫn: Gmail Webhook + FastAPI Backend

## Tổng Quan

Hệ thống này tích hợp Gmail Push Notifications với FastAPI để tự động nhận và xử lý email.

**Luồng Hoạt Động:**

```
Gmail Account
    ↓ (Email arrives)
Google Cloud Pub/Sub
    ↓ (Push notification with message ID)
FastAPI Webhook Endpoint
    ↓ (POST /api/v1/webhook/process-email)
GmailService (Fetch email from Gmail API)
    ↓
EmailProcessingService (Hybrid AI Classification)
    ↓
MongoDB (Store result)
    ↓
✓ Complete!
```

---

## Các Thành Phần Chính

### 1. **GmailService** (`src/services/gmail_service.py`)

Chăm sóc tương tác với Gmail API:

```python
from src.services.gmail_service import get_gmail_service

gmail = get_gmail_service()

# Lấy email từ Gmail API
email_data = await gmail.get_email_by_id("message_id")

# Parse headers
headers = gmail.parse_email_headers(email_data)
# → {'subject': '...', 'from': '...', 'to': '...', ...}

# Extract body (handle HTML)
body = gmail.parse_email_body(email_data)
# → Decoded text (removes HTML tags)

# Get attachments
attachments = gmail.get_attachment_info(email_data)
# → [{'filename': '...', 'mime_type': '...', ...}]

# Format cho processing
formatted = gmail.format_email_data(email_data)
# → Clean data structure sẵn sàng cho AI classifier
```

**Tính Năng:**
- ✅ Authentication với Google service account
- ✅ Fetch email by message ID
- ✅ Parse email headers (Subject, From, To, Date, etc.)
- ✅ Extract body (text & HTML)
- ✅ Handle attachments
- ✅ Error handling & retries
- ✅ Clean data formatting

### 2. **Webhook Endpoint** (`src/api/webhooks.py`)

FastAPI endpoint nhận notifications:

```python
@router.post("/api/v1/webhook/process-email")
async def process_email_webhook(request: Request):
    """
    Nhận message_id từ Pub/Sub
    Fetch email từ Gmail API
    Classify với Hybrid AI
    Save to MongoDB
    """
    # Implementation...
```

**Luồng Xử Lý:**

1. **Nhận Request**
   ```json
   {
       "message_id": "18b7a4c8e8f4d5c2"
   }
   ```

2. **Fetch Email từ Gmail**
   ```python
   gmail = get_gmail_service()
   email_data = await gmail.get_email_by_id(message_id)
   ```

3. **Format Dữ Liệu**
   ```python
   formatted = gmail.format_email_data(email_data)
   # → {'id': '...', 'subject': '...', 'body': '...', ...}
   ```

4. **Classify với Hybrid AI**
   ```python
   service = get_email_processing_service()
   result = await service.process_email(formatted)
   # → ProcessedEmail with classification, confidence, entities, sentiment
   ```

5. **Trả Về Response**
   ```json
   {
       "status": "success",
       "classification": "important",
       "confidence": 0.92,
       "from": "...",
       "subject": "..."
   }
   ```

### 3. **EmailProcessingService** (`src/services/email_service.py`)

Xử lý email với Hybrid AI:

```python
service = get_email_processing_service()
result = await service.process_email(email_data)

# Result:
# ProcessedEmail {
#     message_id: str
#     subject: str
#     from_email: str
#     body: str
#     classification: ClassificationLabel  # IMPORTANT, SPAM, etc.
#     confidence_score: float              # 0.0-1.0
#     # ... entities, sentiment analysis, etc.
# }
```

---

## Cài Đặt & Cấu Hình

### **Bước 1: Tạo Google Cloud Service Account**

```bash
# 1. Vào Google Cloud Console
# https://console.cloud.google.com

# 2. Tạo Service Account
# Service Accounts → Create Service Account
# Name: email-classifier-service

# 3. Tạo JSON Key
# Service Account → Keys → Add Key → Create new key → JSON

# 4. Download file JSON
# Lưu vào: ./credentials/service-account-key.json
```

### **Bước 2: Enable Gmail API**

```bash
# 1. Vào Google Cloud Console
# APIs & Services → Enable APIs and Services

# 2. Search: Gmail API

# 3. Click: Enable
```

### **Bước 3: Cấu Hình .env**

```env
# Google Cloud
GCP_PROJECT_ID=your-project-id
GCP_CREDENTIALS_PATH=./credentials/service-account-key.json

# Gmail
GMAIL_USER_EMAIL=your@gmail.com
WEBHOOK_URL=https://your-domain.com/api/v1/webhook/process-email

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=email_classifier

# Hybrid AI
ENABLE_SPAM_DETECTION=true
SKIP_LLM_FOR_SPAM=true
LLM_API_PROVIDER=openai
LLM_API_KEY=sk-...
```

### **Bước 4: Setup Gmail Push Notifications**

```bash
# Tạo Pub/Sub Topic
gcloud pubsub topics create gmail-notifications \
  --project=YOUR_PROJECT_ID

# Tạo Push Subscription
gcloud pubsub subscriptions create gmail-notifications-sub \
  --topic=gmail-notifications \
  --push-endpoint=https://your-domain.com/api/v1/webhook/process-email \
  --push-auth-service-account=email-classifier-service@YOUR_PROJECT.iam.gserviceaccount.com
```

### **Bước 5: Setup Gmail Watch**

```bash
# Script để setup Gmail watch
python scripts/setup_gmail_watch.py
```

---

## Code Examples

### **Example 1: Sử Dụng GmailService**

```python
import asyncio
from src.services.gmail_service import get_gmail_service

async def fetch_email():
    gmail = get_gmail_service()
    
    # Fetch email
    message_id = "18b7a4c8e8f4d5c2"
    email_data = await gmail.get_email_by_id(message_id)
    
    if email_data:
        # Parse components
        headers = gmail.parse_email_headers(email_data)
        body = gmail.parse_email_body(email_data)
        attachments = gmail.get_attachment_info(email_data)
        
        # Format for AI processing
        formatted = gmail.format_email_data(email_data)
        
        print(f"From: {formatted['from']}")
        print(f"Subject: {formatted['subject']}")
        print(f"Body (first 100 chars): {formatted['body'][:100]}...")
        print(f"Attachments: {len(formatted['attachments'])}")

asyncio.run(fetch_email())
```

### **Example 2: Complete Webhook Implementation**

```python
from fastapi import APIRouter, Request, HTTPException
from src.services.gmail_service import get_gmail_service
from src.services.email_service import get_email_processing_service
from src.services.mongodb_service import get_mongo_service
from src.models.database import AuditLog

router = APIRouter()

@router.post("/api/v1/webhook/process-email")
async def process_email_webhook(request: Request):
    """
    Handle email processing webhook
    """
    try:
        # Parse request
        payload = await request.json()
        message_id = payload.get("message_id")
        
        if not message_id:
            raise HTTPException(400, "message_id required")
        
        # Fetch email from Gmail
        gmail = get_gmail_service()
        email_data = await gmail.get_email_by_id(message_id)
        
        if not email_data:
            raise HTTPException(404, "Email not found")
        
        # Format and process
        formatted = gmail.format_email_data(email_data)
        
        service = get_email_processing_service()
        result = await service.process_email(formatted)
        
        # Log to MongoDB
        mongo = await get_mongo_service()
        await mongo.log_audit(AuditLog(
            event_type="processing_completed",
            message_id=message_id,
            status="success"
        ))
        
        # Return result
        return {
            "status": "success",
            "classification": result.classification.value,
            "confidence": float(result.confidence_score),
            "subject": result.subject
        }
        
    except HTTPException:
        raise
    except Exception as e:
        mongo = await get_mongo_service()
        await mongo.log_audit(AuditLog(
            event_type="processing_error",
            status="error",
            error=str(e)
        ))
        raise HTTPException(500, str(e))
```

### **Example 3: Batch Processing**

```python
import asyncio
from src.services.gmail_service import get_gmail_service
from src.services.email_service import get_email_processing_service

async def process_multiple_emails(message_ids: list):
    """Process multiple emails concurrently"""
    
    gmail = get_gmail_service()
    service = get_email_processing_service()
    
    tasks = []
    
    for msg_id in message_ids:
        # Fetch email
        email_data = await gmail.get_email_by_id(msg_id)
        
        if email_data:
            # Format
            formatted = gmail.format_email_data(email_data)
            
            # Process (create task)
            task = service.process_email(formatted)
            tasks.append(task)
    
    # Run all concurrently
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    classifications = {}
    for result in results:
        label = result.classification.value
        classifications[label] = classifications.get(label, 0) + 1
    
    print(f"Processed {len(results)} emails:")
    for label, count in classifications.items():
        print(f"  {label}: {count}")

# Usage
asyncio.run(process_multiple_emails([
    "msg_001",
    "msg_002",
    "msg_003"
]))
```

---

## File Structure

```
src/
├── api/
│   └── webhooks.py              ← Webhook endpoint
│       ├── @router.post("/webhook/gmail")
│       └── @router.post("/webhook/process-email")
│
├── services/
│   ├── gmail_service.py         ← Gmail API integration
│   │   ├── GmailService
│   │   ├── get_email_by_id()
│   │   ├── parse_email_headers()
│   │   ├── parse_email_body()
│   │   └── format_email_data()
│   │
│   ├── email_service.py         ← Email processing
│   │   └── process_email()
│   │
│   └── mongodb_service.py       ← Data persistence
│       └── log_audit()
│
├── models/
│   ├── hybrid_classifier.py     ← Hybrid AI
│   │   └── classify()
│   │
│   └── database.py              ← Data models
│       ├── ProcessedEmail
│       ├── AuditLog
│       └── ClassificationLabel
│
├── config/
│   └── settings.py              ← Configuration
│
└── main.py                      ← FastAPI app
    ├── app = FastAPI(...)
    └── include_router(webhooks_router)
```

---

## Chạy Hệ Thống

### **Development Mode (Local Testing)**

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
cp .env.example .env
# Edit .env with your settings

# 3. Start FastAPI server
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 4. API available at: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### **Production Mode (Docker)**

```bash
# 1. Build and start with Docker Compose
docker-compose up -d

# 2. Check logs
docker-compose logs -f api

# 3. Access API
curl http://localhost:8000/health

# 4. View docs
# http://localhost:8000/docs
```

---

## Testing Webhook

### **Cách 1: Manual Test (curl)**

```bash
# Test webhook endpoint
curl -X POST http://localhost:8000/api/v1/webhook/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "18b7a4c8e8f4d5c2"
  }'

# Expected Response:
# {
#   "status": "success",
#   "classification": "important",
#   "confidence": 0.92,
#   "from": "...",
#   "subject": "..."
# }
```

### **Cách 2: Demo Script**

```bash
python scripts/demo_email_pipeline.py
```

### **Cách 3: Real Gmail Notifications**

1. Setup Gmail Watch (see above)
2. Send email to your account
3. Gmail → Pub/Sub → Webhook → Processing
4. Check MongoDB for results

---

## Monitoring & Logging

### **View Logs**

```bash
# Docker logs
docker-compose logs -f api

# Application logs
tail -f logs/app.log
```

### **Check MongoDB**

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017

# List processed emails
db.processed_emails.find().pretty()

# Get statistics
db.processed_emails.aggregate([
  {$group: {_id: "$classification", count: {$sum: 1}}}
]).pretty()
```

### **View API Docs**

```
http://localhost:8000/docs
```

---

## Troubleshooting

### **Issue: Gmail API credentials not found**

**Solution:**
```bash
# Check if credentials file exists
ls -la ./credentials/service-account-key.json

# Check .env
echo $GCP_CREDENTIALS_PATH

# Update .env if needed
GCP_CREDENTIALS_PATH=./credentials/service-account-key.json
```

### **Issue: Webhook timeout**

**Solution:**
```env
# Increase timeout
LLM_TIMEOUT=60
WEBHOOK_TIMEOUT=30
```

### **Issue: Email not fetched from Gmail**

**Solution:**
1. Check Gmail API is enabled
2. Verify service account has access
3. Check message_id is valid
4. Check credentials file permissions

### **Issue: Classification confidence too low**

**Solution:**
```env
# Adjust threshold
CLASSIFICATION_CONFIDENCE_THRESHOLD=0.6
SPAM_DETECTION_THRESHOLD=0.6
```

---

## Best Practices

✅ **Do:**
- Use async/await for I/O operations
- Implement retry logic
- Log everything
- Handle errors gracefully
- Use type hints
- Test with real data

❌ **Don't:**
- Hardcode credentials
- Ignore errors
- Block on I/O
- Expose sensitive data in logs
- Skip validation

---

## Chi Tiết Kỹ Thuật

### **GmailService Methods**

| Method | Description | Returns |
|--------|-------------|---------|
| `get_email_by_id(msg_id)` | Fetch email from Gmail API | dict or None |
| `parse_email_headers(email_data)` | Extract headers | dict |
| `parse_email_body(email_data)` | Extract and decode body | str |
| `get_attachment_info(email_data)` | Get attachment metadata | list |
| `format_email_data(email_data)` | Format for processing | dict |

### **Webhook Request Format**

```json
{
    "message_id": "18b7a4c8e8f4d5c2"
}
```

### **Webhook Response Format**

```json
{
    "status": "success",
    "message_id": "18b7a4c8e8f4d5c2",
    "classification": "important",
    "confidence": 0.92,
    "from": "sender@example.com",
    "subject": "Email Subject"
}
```

---

## Reference Files

- **Implementation**: `src/services/gmail_service.py`
- **Webhook**: `src/api/webhooks.py`
- **Email Service**: `src/services/email_service.py`
- **Demo**: `scripts/demo_email_pipeline.py`
- **Documentation**: `HYBRID_AI_GUIDE.md`

---

**Phiên bản**: 1.0
**Ngày**: 2026-04-17
**Trạng thái**: Production Ready ✅
