# Event-Driven AI Email Classifier

A production-ready, event-driven email classification system using Gmail Push Notifications (Google Cloud Pub/Sub) and FastAPI with MongoDB.

## Architecture Overview

```
Gmail Account
    ↓ (Push Notification via Pub/Sub)
Google Cloud Pub/Sub Topic
    ↓ (HTTP POST)
FastAPI Webhook Listener (Async)
    ↓
Message Processing Queue
    ↓
MongoDB (Storage) + AI Classification
    ↓
Results & Analytics
```

## Key Features

✅ **Hybrid AI Classification** (NEW!)
  - Stage 1: Fast spam detection (TF-IDF + Naive Bayes) - <1ms, free
  - Stage 2: Deep email analysis (LLM API) - Only for legitimate emails
  - Result: 90% cost reduction while maintaining high accuracy
  
✅ **Event-Driven**: No polling needed - receive notifications instantly via Google Cloud Pub/Sub  
✅ **Real-time Processing**: Async/concurrent email processing with configurable workers  
✅ **MongoDB Persistence**: Store emails and classifications with full audit trails  
✅ **RESTful API**: Query processed emails by classification, sender, or message ID  
✅ **Webhook Signature Verification**: Secure webhook endpoints  
✅ **Docker Ready**: Complete docker-compose setup with MongoDB, Redis, and FastAPI  
✅ **Logging & Monitoring**: Comprehensive audit logs and health checks  

## Prerequisites

- Python 3.10+
- Docker & Docker Compose
- Google Cloud Project with Gmail API enabled
- Google Cloud Pub/Sub Topic configured for Gmail
- MongoDB 5.0+

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd "e:\PJ Data\AI Email Classifier Real-time"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Hybrid AI Classification (Optional but Recommended)

The system uses a hybrid approach to classify emails:

**Stage 1: Spam Detection** (TF-IDF + Naive Bayes)
```bash
# Train the spam detector (one time)
python scripts/train_spam_detector.py
# Output: Model saved to ./models/spam_detector.pkl
```

**Stage 2: Deep Email Analysis** (LLM API - OpenAI or Claude)
```bash
# Set in .env:
LLM_API_PROVIDER=openai           # or "claude"
LLM_API_KEY=sk-your-api-key
LLM_MODEL=gpt-3.5-turbo          # Cheap & fast

# Critical for cost savings:
SKIP_LLM_FOR_SPAM=true           # Skip expensive LLM for spam!
```

**Cost Savings Example:**
- Without Hybrid: 100 emails × $0.0015 = $4.50/month
- With Hybrid: 30 legitimate emails × $0.0015 = $1.35/month
- **Savings: 70% reduction! 💰**

For detailed hybrid AI documentation, see:
- [HYBRID_AI_GUIDE.md](./HYBRID_AI_GUIDE.md) - Complete technical guide
- [HYBRID_AI_IMPLEMENTATION.md](./HYBRID_AI_IMPLEMENTATION.md) - Implementation details
- [HYBRID_AI_CONFIG.md](./HYBRID_AI_CONFIG.md) - Configuration reference
- [scripts/QUICK_REFERENCE.py](./scripts/QUICK_REFERENCE.py) - Copy-paste code examples

### 3. Setup Gmail Webhook Integration (NEW!)

The system now includes complete Gmail API webhook integration:

**GmailService** (`src/services/gmail_service.py`) - Reads emails from Gmail API:
```python
from src.services.gmail_service import get_gmail_service

gmail = get_gmail_service()

# Fetch email by message ID
email_data = await gmail.get_email_by_id("message_id")

# Parse components
headers = gmail.parse_email_headers(email_data)
body = gmail.parse_email_body(email_data)
attachments = gmail.get_attachment_info(email_data)

# Format for processing
formatted = gmail.format_email_data(email_data)
```

**Webhook Endpoint** (`src/api/webhooks.py`):
```python
@router.post("/api/v1/webhook/process-email")
async def process_email_webhook(request: Request):
    """
    1. Receives message_id from Pub/Sub
    2. Fetches email from Gmail API
    3. Classifies with Hybrid AI
    4. Saves to MongoDB
    """
    # Implementation...
```

**Complete Flow:**
```
Gmail Account → Pub/Sub → Webhook → GmailService → Hybrid AI → MongoDB
```

For detailed Gmail webhook documentation, see:
- [GMAIL_WEBHOOK_GUIDE.md](./GMAIL_WEBHOOK_GUIDE.md) - Complete integration guide
- [src/services/gmail_service.py](./src/services/gmail_service.py) - Gmail API service
- [src/api/webhooks.py](./src/api/webhooks.py) - Webhook endpoint
- [scripts/demo_email_pipeline.py](./scripts/demo_email_pipeline.py) - Complete examples

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
# Required:
# - GCP_PROJECT_ID
# - GCP_CREDENTIALS_PATH (path to Google Cloud service account JSON)
# - MONGODB_PASSWORD (change default)
# - LLM_API_KEY (for deep email analysis)
```

### 5. Setup Google Cloud (Important!)

Follow this step-by-step guide to enable Gmail Push Notifications:

#### Step A: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: "AI Email Classifier"
3. Enable APIs:
   - Gmail API
   - Cloud Pub/Sub API

#### Step B: Create Service Account
1. Go to **Service Accounts** → Create Service Account
   - Name: `email-classifier-service`
   - Grant role: **Editor** (for development; use specific roles in production)
2. Create JSON key → Save to `credentials/service-account-key.json`

#### Step C: Create Pub/Sub Topic & Subscription
```bash
# Using Google Cloud CLI (gcloud)
gcloud pubsub topics create gmail-notifications \
  --project=YOUR_PROJECT_ID

gcloud pubsub subscriptions create gmail-notifications-sub \
  --topic=gmail-notifications \
  --push-endpoint=https://YOUR_WEBHOOK_URL/api/v1/webhook/gmail \
  --push-auth-service-account=email-classifier-service@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

#### Step D: Setup Gmail Push (via Gmail API)
```bash
gcloud auth application-default login

# Run watch command
python scripts/setup_gmail_watch.py
```

### 6. Run with Docker Compose

```bash
# Build and start services
docker-compose up -d

# Check logs
docker-compose logs -f api

# Stop services
docker-compose down
```

Services will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017
- **Redis**: localhost:6379
- **Adminer** (MongoDB UI): http://localhost:8080

### 7. Test the System

```bash
# Check API health
curl http://localhost:8000/health

# Get classification statistics
curl http://localhost:8000/api/v1/stats

# Get processed emails
curl http://localhost:8000/api/v1/emails

# Get emails by classification
curl "http://localhost:8000/api/v1/emails?classification=important"
```

## Project Structure

```
AI Email Classifier Real-time/
├── src/
│   ├── api/                 # FastAPI routes
│   │   ├── webhooks.py      # Webhook endpoints
│   │   └── emails.py        # Email query endpoints
│   ├── services/            # Business logic
│   │   ├── gmail_service.py        # Gmail API integration (NEW!)
│   │   ├── pubsub_service.py       # Google Cloud Pub/Sub
│   │   ├── mongodb_service.py      # Database operations
│   │   └── email_service.py        # Email processing
│   ├── models/              # Data models
│   │   └── database.py      # Pydantic models
│   ├── config/              # Configuration
│   │   └── settings.py      # App settings
│   ├── utils/               # Utilities
│   │   ├── logger.py        # Logging setup
│   │   └── decorators.py    # Retry, logging decorators
│   └── main.py              # FastAPI app entry point
├── docker/
│   └── Dockerfile           # Container image
├── docker-compose.yml       # Multi-container orchestration
├── scripts/
│   ├── setup_gmail_watch.py # Gmail Pub/Sub setup
│   └── deploy.sh            # Deployment script
├── tests/                   # Unit/integration tests
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## API Endpoints

### Webhooks
- `POST /api/v1/webhook/gmail` - Receive Gmail push notifications
- `POST /api/v1/webhook/process-email` - Process specific email

### Queries
- `GET /api/v1/emails` - Get all processed emails (with filters)
- `GET /api/v1/emails/{message_id}` - Get specific email
- `GET /api/v1/emails/sender/{from_email}` - Get emails from sender
- `GET /api/v1/stats` - Get classification statistics
- `GET /health` - Health check

## Configuration

### Environment Variables

```env
# API
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=email_classifier
MONGODB_USER=admin
MONGODB_PASSWORD=changeme123

# Google Cloud
GCP_PROJECT_ID=your-project-id
GCP_CREDENTIALS_PATH=./credentials/service-account-key.json
GCP_PUBSUB_TOPIC=projects/your-project-id/topics/gmail-notifications
GCP_PUBSUB_SUBSCRIPTION=projects/your-project-id/subscriptions/gmail-notifications-sub

# Processing
MAX_WORKERS=4
BATCH_SIZE=10
CONFIDENCE_THRESHOLD=0.7

# Logging
LOG_LEVEL=INFO
```

## Deployment Guide

### Production Checklist

- [ ] Use strong MongoDB password
- [ ] Set `API_ENV=production`
- [ ] Use environment-specific service account keys
- [ ] Enable CORS with specific origins
- [ ] Set up proper logging and monitoring
- [ ] Use reverse proxy (Nginx) with SSL
- [ ] Configure automated backups for MongoDB
- [ ] Set up error tracking (e.g., Sentry)
- [ ] Use load balancer for API scaling

### Docker Production Deployment

```bash
# Build production image
docker build -f docker/Dockerfile -t email-classifier:1.0.0 .

# Push to registry
docker tag email-classifier:1.0.0 your-registry/email-classifier:1.0.0
docker push your-registry/email-classifier:1.0.0

# Deploy using docker-compose or Kubernetes
docker-compose -f docker-compose.prod.yml up -d
```

## Scaling Considerations

### Horizontal Scaling
- Add multiple API instances behind load balancer
- MongoDB replication for high availability
- Redis for distributed caching

### Optimization
- Use connection pooling for MongoDB (Motor)
- Implement message batching in Pub/Sub
- Cache frequently accessed emails in Redis
- Use background tasks (Celery) for heavy processing

## Troubleshooting

### MongoDB Connection Failed
```bash
# Check MongoDB is running
docker-compose ps

# View MongoDB logs
docker-compose logs mongodb

# Verify credentials
docker exec email_classifier_mongodb mongosh -u admin -p changeme123 admin
```

### Webhook Not Receiving Messages
1. Verify Pub/Sub subscription push endpoint is correct
2. Check firewall/network allows inbound HTTPS
3. Verify webhook authentication token in Gmail settings
4. Check application logs: `docker-compose logs api`

### High Memory Usage
- Reduce `MAX_WORKERS` in `.env`
- Implement pagination for large queries
- Use MongoDB projection to fetch only required fields

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -am 'Add feature'`
3. Push to branch: `git push origin feature/your-feature`
4. Submit pull request

## License

MIT License

## Support

For issues and questions:
1. Check logs: `docker-compose logs -f`
2. Review API documentation: http://localhost:8000/docs
3. Check MongoDB collections using Adminer: http://localhost:8080

---

**Tech Lead Notes**: This architecture eliminates polling waste, provides real-time processing, and scales horizontally. The event-driven approach with Pub/Sub ensures you only process emails when they arrive, saving resources and providing instant classification.
