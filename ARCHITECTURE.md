# 📐 Event-Driven Architecture Technical Reference

## System Design Document

### 1. Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         External Services                      │
├────────────────────────────────────────────────────────────────┤
│ Gmail                      │  Google Cloud Pub/Sub              │
│ ├─ Inbox (User)           │  ├─ Topic: gmail-notifications    │
│ ├─ Labels                 │  └─ Subscription: push to webhook  │
│ └─ API Access             │                                    │
└────────────────────────────────────────────────────────────────┘
         │ Push Notification                  │
         └──────────────────────────────────────┘
                      │
                      ↓
         ┌────────────────────────┐
         │   FastAPI Server       │
         │  (Webhook Listener)    │
         ├────────────────────────┤
         │ POST /webhook/gmail    │
         │ ├─ Verify signature    │
         │ ├─ Decode Pub/Sub msg  │
         │ └─ Queue for processing│
         └────────────────────────┘
                      │
                      ↓
         ┌────────────────────────┐
         │  Processing Service    │
         │  (Async Workers)       │
         ├────────────────────────┤
         │ ├─ Max workers: 4      │
         │ ├─ Retry logic         │
         │ └─ Queue management    │
         └────────────────────────┘
                      │
         ┌────────────┴─────────────┐
         ↓                          ↓
    ┌─────────────┐         ┌──────────────┐
    │ Gmail API   │         │AI Classifier │
    │ (Fetch)     │         │ (Model)      │
    └─────────────┘         └──────────────┘
         │                         │
         └────────────┬────────────┘
                      ↓
         ┌────────────────────────┐
         │     MongoDB            │
         ├────────────────────────┤
         │ Collections:           │
         │ • processed_emails     │
         │ • audit_logs           │
         │ • classifications      │
         └────────────────────────┘
                      │
                      ↓
         ┌────────────────────────┐
         │    REST API Routes     │
         ├────────────────────────┤
         │ GET /api/v1/emails     │
         │ GET /api/v1/stats      │
         │ GET /api/v1/health     │
         └────────────────────────┘
```

### 2. Component Responsibilities

#### FastAPI Application (src/main.py)
- **Lifecycle**: Startup/shutdown hooks
- **Routes**: Register all API endpoints
- **Middleware**: CORS, error handling
- **Logging**: Centralized logging

#### Webhook Routes (src/api/webhooks.py)
- **POST /webhook/gmail**: Receive Pub/Sub messages
- **POST /webhook/process-email**: Async processing trigger
- **GET /health**: Health check endpoint
- **Signature verification**: Validate webhook authenticity

#### Email Query Routes (src/api/emails.py)
- **GET /emails**: List all processed emails
- **GET /emails/{message_id}**: Get specific email
- **GET /emails/sender/{email}**: Filter by sender
- **GET /stats**: Get classification statistics

#### Pub/Sub Service (src/services/pubsub_service.py)
- **Connection management**: Authenticate with GCP
- **Message subscription**: Subscribe to Gmail notifications
- **Message decoding**: Base64 decoding and parsing
- **Callback handling**: Process received messages

#### MongoDB Service (src/services/mongodb_service.py)
- **Connection pooling**: Motor async client
- **Index creation**: Performance optimization
- **CRUD operations**: Save/read emails and logs
- **Aggregation**: Statistics and analytics

#### Email Processing Service (src/services/email_service.py)
- **Email fetching**: Get full email from Gmail API
- **Header extraction**: Parse email metadata
- **Body extraction**: Extract text content
- **Classification**: Run AI model
- **Batch processing**: Concurrent worker management
- **Retry logic**: Exponential backoff

### 3. Data Flow Sequence

```
1. USER: Send email to Gmail account
   └─> Gmail stores in Inbox

2. GMAIL: Detects new email
   └─> Pub/Sub notification triggered

3. PUB/SUB: Routes message to subscription
   └─> HTTP POST to webhook endpoint

4. FASTAPI: Receives webhook
   ├─ Verify signature
   ├─ Decode message
   └─ Extract message_id

5. EMAIL SERVICE: Process email
   ├─ Fetch full email from Gmail API
   ├─ Extract headers (subject, from, to)
   ├─ Extract body (text/html)
   └─ Run AI classification

6. AI MODEL: Classify email
   └─> Returns: classification + confidence_score

7. MONGODB: Store results
   ├─ Save processed_email document
   └─ Log audit event

8. API CLIENT: Query results
   ├─ GET /emails?classification=important
   └─> Retrieve processed emails
```

### 4. Database Schema

#### Collections

**processed_emails**
```javascript
{
  _id: ObjectId,
  message_id: String (indexed, unique),
  thread_id: String,
  subject: String,
  from_email: String (indexed),
  to_emails: [String],
  body: String,
  received_date: ISODate (indexed),
  classification: String (indexed),  // enum: spam|promotional|social|important|general
  confidence_score: Number (0.0-1.0),
  processed_at: ISODate,
  status: String,  // completed|pending|failed
  error_message: String,
  retry_count: Number,
  created_at: ISODate (default: now)
}
```

**audit_logs**
```javascript
{
  _id: ObjectId,
  timestamp: ISODate (indexed),
  event_type: String (indexed),  // webhook_received|processing_started|classification_completed|error
  message_id: String (indexed),
  details: Object,
  status: String,  // success|error
  error: String,
  duration_ms: Number,
  created_at: ISODate (default: now)
}
```

### 5. Configuration Management

**Environment-based configuration** (src/config/settings.py)

```python
class Settings(BaseSettings):
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"
    
    # Database
    mongodb_url: str
    mongodb_db_name: str
    
    # Google Cloud
    gcp_project_id: str
    gcp_credentials_path: str
    
    # Processing
    max_workers: int = 4
    confidence_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        case_sensitive = False
```

### 6. Error Handling & Retry Strategy

```
Retry Configuration:
├─ Max Attempts: 3
├─ Initial Delay: 1 second
├─ Backoff Multiplier: 2.0
│  └─ Delay progression: 1s → 2s → 4s
└─ Total Max Wait: ~7 seconds

Error Scenarios:
├─ Network Error: RETRY
├─ Temporary Failure: RETRY
├─ Invalid Signature: SKIP (don't retry)
├─ Missing Message ID: LOG & SKIP
└─ Database Error: QUEUE for later
```

### 7. Concurrency Model

```python
# AsyncIO-based concurrency
Processing Architecture:
├─ Event Loop: Uvicorn + FastAPI
├─ Async I/O: Motor (MongoDB), httpx (HTTP)
├─ Semaphore: Limit concurrent tasks
│  └─ MAX_WORKERS = 4 (configurable)
└─ Tasks: Each email = 1 async task

Benefits:
├─ Low memory overhead
├─ Handle high throughput
├─ Non-blocking operations
└─ Efficient resource usage
```

### 8. Security Considerations

**Authentication & Authorization**
```
Webhook Signature Verification:
├─ Google Cloud Pub/Sub OIDC tokens
├─ Service account validation
└─ Timestamp freshness check

API Security:
├─ CORS configuration
├─ Rate limiting (future)
├─ Input validation (Pydantic)
└─ SQL injection prevention (NoSQL)
```

**Data Protection**
```
Database:
├─ MongoDB authentication required
├─ Passwords in environment variables
├─ Credentials in separate directory

Application:
├─ No sensitive data in logs
├─ Secure session handling
└─ Input sanitization
```

### 9. Performance Optimization

**Index Strategy**
```
indexed fields:
├─ message_id (unique) - for lookups
├─ received_date - for time-range queries
├─ classification - for filtering
├─ from_email - for sender queries
└─ timestamp - for audit logs
```

**Query Optimization**
```
├─ Limit results (pagination)
├─ Project only needed fields
├─ Use appropriate indexes
└─ Batch operations when possible
```

**Caching (Optional)**
```
Redis Cache:
├─ Recent emails
├─ Classification statistics
├─ User preferences
└─ TTL: 1 hour
```

### 10. Monitoring & Observability

**Metrics to Track**
```
Application Metrics:
├─ API response time
├─ Email processing latency
├─ Queue depth
├─ Success/failure rates
└─ CPU/memory usage

Business Metrics:
├─ Emails processed/hour
├─ Classification distribution
├─ Confidence score trends
└─ Error rates by type
```

**Logging Strategy**
```
Log Levels:
├─ DEBUG: Detailed execution trace
├─ INFO: Important milestones
├─ WARNING: Unexpected behavior
├─ ERROR: Failures requiring attention
└─ CRITICAL: System breakdown

Log Format:
timestamp - service - level - message
2024-01-15 10:00:05 - email_service - INFO - Successfully processed email: msg_123
```

### 11. Deployment Considerations

**Docker Layers**
```
Layer 1: Builder
├─ Install build tools
├─ Compile dependencies
└─ ~1.5GB

Layer 2: Runtime (reuse from builder)
├─ Minimal base image
├─ Only runtime dependencies
└─ ~400MB (multi-stage build benefit)
```

**Network Architecture**
```
External Network
├─ Internet facing: Reverse proxy (Nginx)
├─ HTTPS: SSL/TLS termination
└─ Load balanced across API instances

Internal Network (Docker network)
├─ api ↔ mongodb (port 27017)
├─ api ↔ redis (port 6379)
└─ All services on isolated network
```

---

## Class & Function Reference

### Core Services

```python
# pubsub_service.py
class PubSubService:
    initialize()           # Connect to Pub/Sub
    subscribe(callback)    # Subscribe to Gmail notifications
    decode_pubsub_message(message) -> dict
    acknowledge_message(subscription_path, ack_ids)

# mongodb_service.py
class MongoDBService:
    async connect()        # Establish MongoDB connection
    async disconnect()     # Close connection
    async save_processed_email(email_data) -> str
    async get_email(message_id) -> dict
    async get_emails_by_classification(classification, limit) -> list
    async get_processing_stats() -> dict
    async log_audit(log_entry)

# email_service.py
class EmailProcessingService:
    async process_email(email_data) -> ProcessedEmail
    async process_batch(emails) -> dict
    def _extract_headers(email_data) -> dict
    def _extract_body(email_data) -> str
    async _classify_email(subject, body, from_email) -> tuple
```

### API Routes

```python
# webhooks.py
@router.post("/api/v1/webhook/gmail")
async def gmail_webhook(request) -> dict

@router.post("/api/v1/webhook/process-email")
async def process_email_webhook(request) -> dict

@router.get("/health")
async def health_check() -> dict

# emails.py
@router.get("/api/v1/emails")
async def get_emails(classification, limit, skip) -> list

@router.get("/api/v1/emails/{message_id}")
async def get_email(message_id) -> dict

@router.get("/api/v1/stats")
async def get_classification_stats() -> dict
```

---

## 🔍 Code Examples

### Processing an Email

```python
# Service usage
email_service = get_email_processing_service()

email_data = {
    "id": "message_123",
    "threadId": "thread_456",
    "payload": {
        "headers": [...],
        "body": {...}
    }
}

result = await email_service.process_email(email_data)
# Returns: ProcessedEmail or raises exception on failure
```

### Querying Results

```python
# Get important emails from specific sender
mongo = await get_mongo_service()
emails = await mongo.get_emails_by_sender("boss@company.com")

for email in emails:
    if email["classification"] == "important":
        print(f"Important: {email['subject']}")
```

### Batch Processing

```python
# Process multiple emails concurrently
service = get_email_processing_service()

results = await service.process_batch(email_list)
print(f"Success: {results['successful']}, Failed: {results['failed']}")
```

---

## 📚 Related Files

- Architecture Diagram: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Setup Guide: [SETUP_GUIDE.md](./SETUP_GUIDE.md)
- API Documentation: http://localhost:8000/docs (when running)
- Configuration: [.env.example](.env.example)
- Dependencies: [requirements.txt](./requirements.txt)

---

**Document Version**: 1.0  
**Last Updated**: 2024-04-17  
**Architecture**: Event-Driven with Google Cloud Pub/Sub
