# 🎯 Event-Driven Architecture Setup Guide

## Phần I: Lý Thuyết Kiến Trúc Event-Driven

### 1. Tại sao từ bỏ Polling?

**❌ Polling (Phương pháp cũ)**
```
Every X minutes → Check Gmail API → Costly API calls → Wasted resources
```
- **Chi phí**: Gmail API có quota hạn chế (~600M requests/day)
- **Delay**: Chỉ check mỗi X phút = delay max X phút
- **Tải máy**: Luôn gửi request ngay cả khi không có email mới
- **Hiệu suất**: Tốn CPU/Network không cần thiết

**✅ Event-Driven (Phương pháp mới)**
```
Email arrives → Pub/Sub notification → Instant webhook → Only process when needed
```
- **Realtime**: Nhận notification tức thì (milliseconds)
- **Efficient**: Chỉ xử lý khi có sự kiện
- **Scalable**: Google Cloud Pub/Sub xử lý triệu sự kiện/giây
- **Cost**: Giảm 90%+ API calls

### 2. Quy Trình Hoạt Động (Event Flow)

```
┌─────────────┐
│ Gmail Inbox │
│   (User)    │
└──────┬──────┘
       │ (New Email Arrives)
       ↓
┌─────────────────────────┐
│ Google Cloud Pub/Sub     │
│ (Message Broker)        │
│ - Gmail notifications   │
│   topic                 │
└──────┬──────────────────┘
       │ (HTTP POST)
       ↓
┌─────────────────────────┐
│ FastAPI Webhook         │
│ /api/v1/webhook/gmail   │
│ (Event Listener)        │
└──────┬──────────────────┘
       │ (Decode + Queue)
       ↓
┌─────────────────────────┐
│ Processing Queue        │
│ (AsyncIO/Redis)         │
└──────┬──────────────────┘
       │ (Async Processing)
       ↓
┌─────────────────────────┐
│ Email Processing Svc    │
│ - Fetch from Gmail      │
│ - Extract headers       │
│ - Run AI Classification │
└──────┬──────────────────┘
       │
       ↓
┌─────────────────────────┐
│ MongoDB                 │
│ - processed_emails      │
│ - audit_logs            │
│ - statistics            │
└─────────────────────────┘
```

### 3. Các Thành Phần Chính

#### A. Google Cloud Pub/Sub (Event Broker)
- **Topic**: Nơi Gmail gửi notifications
- **Subscription**: Nơi FastAPI subscribe để nhận messages
- **Message Format**: Base64-encoded JSON

#### B. FastAPI Webhook Server
- **Nhận**: HTTP POST từ Pub/Sub
- **Verify**: Kiểm tra signature
- **Parse**: Decode Pub/Sub message
- **Queue**: Đưa vào processing queue

#### C. Email Processing Service
- **Async**: Xử lý đồng thời nhiều emails
- **Retry**: Tự động retry với exponential backoff
- **Classify**: Chạy AI model
- **Persist**: Lưu vào MongoDB

#### D. MongoDB
- **processed_emails**: Lưu email đã phân loại
- **audit_logs**: Lưu tất cả sự kiện
- **Indexes**: Tối ưu query performance

---

## Phần II: Setup Từng Bước

### Step 1: Tạo Google Cloud Project

```bash
# A. Login vào Google Cloud Console
https://console.cloud.google.com

# B. Tạo project mới
gcloud projects create ai-email-classifier

# C. Set as current project
gcloud config set project ai-email-classifier

# D. Enable required APIs
gcloud services enable gmail.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable cloudapi.googleapis.com
```

### Step 2: Tạo Service Account

```bash
# Create service account
gcloud iam service-accounts create email-classifier-service \
  --display-name="AI Email Classifier"

# Grant Gmail permissions
gcloud projects add-iam-policy-binding ai-email-classifier \
  --member=serviceAccount:email-classifier-service@ai-email-classifier.iam.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

# Grant Pub/Sub permissions
gcloud projects add-iam-policy-binding ai-email-classifier \
  --member=serviceAccount:email-classifier-service@ai-email-classifier.iam.gserviceaccount.com \
  --role=roles/pubsub.subscriber

# Generate JSON key
gcloud iam service-accounts keys create credentials/service-account-key.json \
  --iam-account=email-classifier-service@ai-email-classifier.iam.gserviceaccount.com
```

### Step 3: Setup Pub/Sub Topic & Subscription

```bash
# Create topic (for Gmail notifications)
gcloud pubsub topics create gmail-notifications \
  --project=ai-email-classifier

# Get your webhook URL (external)
# Format: https://your-domain.com/api/v1/webhook/gmail
# For local testing: use ngrok: ngrok http 8000

# Create subscription with push endpoint
gcloud pubsub subscriptions create gmail-notifications-sub \
  --topic=gmail-notifications \
  --push-endpoint=https://your-webhook-url/api/v1/webhook/gmail \
  --push-auth-service-account=email-classifier-service@ai-email-classifier.iam.gserviceaccount.com \
  --project=ai-email-classifier
```

### Step 4: Setup Gmail Watch

```bash
# Export environment variables
export GCP_PROJECT_ID=ai-email-classifier
export GCP_CREDENTIALS_PATH=./credentials/service-account-key.json

# Run setup script
python scripts/setup_gmail_watch.py
```

### Step 5: Start Docker Services

```bash
# Copy environment file
cp .env.example .env

# Edit .env with your values:
# - GCP_PROJECT_ID=ai-email-classifier
# - MongoDB credentials
# - API host/port

# Start all services
docker-compose up -d

# Verify services
docker-compose ps
docker-compose logs -f api
```

### Step 6: Test Integration

```bash
# Check health
curl http://localhost:8000/health

# Send test email to your Gmail
# Should see it appear in processed emails after ~5 seconds

# Query results
curl http://localhost:8000/api/v1/emails
curl http://localhost:8000/api/v1/stats
```

---

## Phần III: Configuration Chi Tiết

### Environment Variables (.env)

```env
# === Google Cloud ===
GCP_PROJECT_ID=ai-email-classifier
GCP_CREDENTIALS_PATH=./credentials/service-account-key.json

# Topic: projects/{PROJECT_ID}/topics/gmail-notifications
GCP_PUBSUB_TOPIC=projects/ai-email-classifier/topics/gmail-notifications

# Subscription: projects/{PROJECT_ID}/subscriptions/gmail-notifications-sub
GCP_PUBSUB_SUBSCRIPTION=projects/ai-email-classifier/subscriptions/gmail-notifications-sub

# === MongoDB ===
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=email_classifier
MONGODB_USER=admin
MONGODB_PASSWORD=your-strong-password-here

# === FastAPI ===
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=development  # production for production

# === Processing ===
MAX_WORKERS=4              # Concurrent email processing
BATCH_SIZE=10              # Emails per batch
CONFIDENCE_THRESHOLD=0.7   # Min confidence to save classification

# === Logging ===
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### MongoDB Collections Schema

```javascript
// processed_emails collection
{
  _id: ObjectId,
  message_id: "AMDOWf...",
  thread_id: "thread_id",
  subject: "Test Email",
  from_email: "sender@example.com",
  to_emails: ["recipient@example.com"],
  body: "Email content...",
  received_date: ISODate("2024-01-15T10:00:00Z"),
  classification: "important",  // spam, promotional, social, important, general
  confidence_score: 0.95,
  processed_at: ISODate("2024-01-15T10:00:05Z"),
  status: "completed",  // completed, pending, failed
  error_message: null,
  retry_count: 0
}

// Indexes:
// - message_id (unique)
// - received_date
// - classification
// - from_email
```

---

## Phần IV: Monitoring & Troubleshooting

### Checking Logs

```bash
# API logs
docker-compose logs -f api

# MongoDB logs
docker-compose logs -f mongodb

# All services
docker-compose logs -f

# Specific time range
docker-compose logs --since 10m api
```

### Common Issues & Solutions

**1. Webhook not receiving messages**
```
Problem: No emails in MongoDB after sending test email

Solution:
1. Check Pub/Sub subscription exists:
   gcloud pubsub subscriptions list

2. Verify webhook URL in subscription:
   gcloud pubsub subscriptions describe gmail-notifications-sub

3. Check service account has Pub/Sub role:
   gcloud projects get-iam-policy ai-email-classifier

4. View Pub/Sub activity:
   gcloud pubsub subscriptions list-subscriptions
   gcloud pubsub subscriptions pull gmail-notifications-sub --auto-ack
```

**2. MongoDB connection error**
```
Problem: "Failed to connect to MongoDB"

Solution:
1. Check MongoDB is running:
   docker-compose ps

2. Verify credentials in .env:
   docker exec email_classifier_mongodb mongosh -u admin -p changeme123

3. Check connection string:
   MONGODB_URL=mongodb://admin:password@mongodb:27017
```

**3. High API latency**
```
Problem: Slow webhook response

Solution:
1. Increase max_workers in .env
2. Add Redis caching layer
3. Use message batching
4. Check MongoDB indexes are created
```

---

## Phần V: Scaling & Production Deployment

### Horizontal Scaling

```yaml
# docker-compose.prod.yml
services:
  api:
    deploy:
      replicas: 3
    depends_on:
      - mongodb
      - redis
    
  # Add load balancer
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    # Configure upstream to api instances
```

### High Availability Setup

```
Load Balancer (Nginx)
    ↓
├─ FastAPI Instance 1
├─ FastAPI Instance 2
└─ FastAPI Instance 3
    ↓
MongoDB Replica Set
    ├─ Primary
    ├─ Secondary 1
    └─ Secondary 2
    ↓
Redis Cluster
```

### Monitoring Tools

- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **ELK Stack**: Log aggregation
- **Sentry**: Error tracking
- **DataDog**: APM monitoring

---

## Phần VI: Best Practices

### 1. Security

```python
# ✅ DO:
- Use environment variables for secrets
- Enable HTTPS for webhooks
- Verify Pub/Sub signatures
- Use strong MongoDB passwords
- Implement rate limiting

# ❌ DON'T:
- Hardcode API keys
- Use default credentials
- Skip signature verification
- Expose MongoDB directly
```

### 2. Performance

```python
# ✅ DO:
- Use async/await for I/O operations
- Implement connection pooling
- Cache frequently accessed data
- Index database collections
- Batch process messages

# ❌ DON'T:
- Synchronous database queries
- New connection per request
- Load all data into memory
- Missing indexes
- Process one message at a time
```

### 3. Reliability

```python
# ✅ DO:
- Implement retry logic with backoff
- Log all operations for audit
- Health checks
- Graceful error handling
- Database backups

# ❌ DON'T:
- Silently fail
- No error logging
- No recovery mechanism
- Lose processing state
- Skip backups
```

---

## 📊 Performance Comparison: Polling vs Event-Driven

| Metric | Polling (Every 1 min) | Event-Driven |
|--------|----------------------|--------------|
| API Calls/day | 1,440 | ~100 (only new emails) |
| Processing Latency | ~30 seconds avg | <1 second |
| False Positives | ~1,300/day | 0 |
| Resource Waste | High (60%+) | Minimal |
| Scalability | Limited | Unlimited |
| Cost | High | Low |

---

## 🎓 Next Steps

1. ✅ Setup Google Cloud Project
2. ✅ Deploy services locally with Docker
3. ✅ Test webhook integration
4. ✅ Implement AI classification model
5. ✅ Add authentication/authorization
6. ✅ Setup production monitoring
7. ✅ Deploy to cloud (GCP, AWS, Kubernetes)

---

## 📞 Support Resources

- Google Cloud: https://cloud.google.com/docs
- FastAPI: https://fastapi.tiangolo.com
- MongoDB: https://docs.mongodb.com
- Docker: https://docs.docker.com
- Gmail API: https://developers.google.com/gmail

---

**Generated**: 2024-04-17
**Architecture Version**: 1.0 Event-Driven
**Tech Lead**: Your Name
