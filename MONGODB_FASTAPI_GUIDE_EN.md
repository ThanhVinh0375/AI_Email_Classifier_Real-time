# MongoDB & FastAPI Integration Guide - AI Email Classification System

## Overview

This guide demonstrates how to use MongoDB and Motor (async driver) in a FastAPI application to build a high-performance real-time email classification system.

## Table of Contents
1. [Architecture Design](#architecture-design)
2. [MongoDB Configuration](#mongodb-configuration)
3. [FastAPI Integration](#fastapi-integration)
4. [Saving Classified Emails](#saving-classified-emails)
5. [Docker Compose Setup](#docker-compose-setup)
6. [Usage Examples](#usage-examples)
7. [Performance Optimization](#performance-optimization)

---

## Architecture Design

### Technology Stack
- **Database**: MongoDB 7.0 (Document database ideal for unstructured email data)
- **Async Driver**: Motor (asyncio-based MongoDB async driver)
- **Web Framework**: FastAPI
- **Connection Pool**: Motor built-in connection pool with max 50 concurrent connections, min 10 reserved connections

### Why Choose MongoDB?
- ✅ **Flexible Schema**: Email data has variable structure (different field combinations)
- ✅ **Fast Writes**: Suitable for real-time email processing
- ✅ **Document Storage**: Naturally stores JSON-formatted emails and analysis results
- ✅ **Native Async Support**: Motor integrates perfectly with FastAPI's async model

---

## MongoDB Configuration

### 1. Environment Variables Setup (`.env`)

```bash
# MongoDB Connection Configuration
MONGODB_URL=mongodb://admin:changeme123@mongodb:27017
MONGODB_DB_NAME=email_classifier
MONGODB_USER=admin
MONGODB_PASSWORD=changeme123

# Connection Pool Configuration
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=10
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
MONGODB_SOCKET_TIMEOUT_MS=30000
MONGODB_CONNECT_TIMEOUT_MS=10000
MONGODB_MAX_IDLE_TIME_MS=45000
MONGODB_RETRY_WRITES=true
MONGODB_RETRY_READS=true
```

### 2. Configuration File (`src/config/settings.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application Configuration"""
    
    # MongoDB Basic Configuration
    mongodb_url: str = "mongodb://admin:changeme123@mongodb:27017"
    mongodb_db_name: str = "email_classifier"
    
    # Connection Pool Optimization - Critical Performance Parameters
    mongodb_max_pool_size: int = 50          # Max concurrent connections
    mongodb_min_pool_size: int = 10          # Min reserved connections
    mongodb_server_selection_timeout_ms: int = 5000    # Server discovery timeout
    mongodb_socket_timeout_ms: int = 30000   # Socket operation timeout
    mongodb_connect_timeout_ms: int = 10000  # Connection timeout
    mongodb_max_idle_time_ms: int = 45000    # Max idle time
    mongodb_max_pool_size_per_host: int = 50 # Max connections per host
    mongodb_retry_writes: bool = True         # Enable automatic retry
    mongodb_retry_reads: bool = True          # Enable read retry
    
    class Config:
        env_file = ".env"
```

---

## FastAPI Integration

### 1. MongoDB Service Class (`src/services/mongodb_service.py`)

```python
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from datetime import datetime
from typing import Optional, List, Dict, Any

class MongoDBService:
    """
    MongoDB Async Service Class
    
    Features:
    - Uses Motor async driver, fully compatible with asyncio
    - Built-in connection pool management
    - Automatic optimized index creation
    - Complete error handling
    """
    
    def __init__(self):
        self.connection_string = settings.mongodb_url
        self.db_name = settings.mongodb_db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """
        Connect to MongoDB (with connection pool optimization)
        
        Optimization Configuration:
        - maxPoolSize: Control max concurrent connections
        - minPoolSize: Ensure minimum hot connections available
        - Automatic retry mechanism
        """
        connection_kwargs = {
            "maxPoolSize": settings.mongodb_max_pool_size,
            "minPoolSize": settings.mongodb_min_pool_size,
            "serverSelectionTimeoutMS": settings.mongodb_server_selection_timeout_ms,
            "socketTimeoutMS": settings.mongodb_socket_timeout_ms,
            "connectTimeoutMS": settings.mongodb_connect_timeout_ms,
            "maxIdleTimeMS": settings.mongodb_max_idle_time_ms,
            "retryWrites": settings.mongodb_retry_writes,
            "retryReads": settings.mongodb_retry_reads,
        }
        
        self.client = AsyncIOMotorClient(
            self.connection_string,
            **connection_kwargs
        )
        
        # Test connection
        await self.client.admin.command('ping')
        self.db = self.client[self.db_name]
        
        # Create database indexes
        await self._create_indexes()
        
        logger.info(f"Connected to MongoDB: {self.db_name}")
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create database indexes to optimize query performance"""
        # classified_emails collection indexes
        classified_col = self.db["classified_emails"]
        
        # Unique index (email_id no duplicates)
        await classified_col.create_index("email_id", unique=True)
        
        # Compound index (descending date query)
        await classified_col.create_index([("created_at", -1), ("email_id", 1)])
        
        # Classification label index
        await classified_col.create_index("classification_label")
        
        # Sender index
        await classified_col.create_index("sender")
        
        # TTL index (auto-delete after 90 days)
        await classified_col.create_index(
            "created_at", 
            expireAfterSeconds=7776000  # 90 days
        )
        
        logger.info("Database indexes created")
```

### 2. Core Method for Saving Classified Emails

```python
async def save_classified_email(self, email_data: ClassifiedEmail) -> str:
    """
    Save classified email to MongoDB
    
    This is the most critical method in the system for persisting AI classification results
    
    Parameters:
        email_data: ClassifiedEmail object (contains all analysis results)
    
    Returns:
        str: MongoDB document ID
    
    Workflow:
        1. Validate email data
        2. Use upsert operation (allow update of existing emails)
        3. Auto-record processing timestamp
        4. Return document ID for tracking
    """
    try:
        collection = self.db["classified_emails"]
        
        # Prepare document data
        email_dict = email_data.dict()
        email_dict["updated_at"] = datetime.utcnow()
        
        # Use upsert operation (update if exists, insert if not)
        result = await collection.update_one(
            {"email_id": email_data.email_id},
            {"$set": email_dict},
            upsert=True
        )
        
        logger.info(
            f"Classified email saved: {email_data.email_id} "
            f"[Label: {email_data.classification_label}] "
            f"[Confidence: {email_data.confidence_score:.2%}]"
        )
        
        return email_data.email_id
        
    except Exception as e:
        logger.error(f"Failed to save classified email: {str(e)}")
        raise


async def get_classified_emails_by_label(
    self,
    classification_label: str,
    limit: int = 100,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """
    Retrieve emails by classification label
    
    Parameters:
        classification_label: Classification label (work/personal/spam/etc)
        limit: Maximum number of results to return
        skip: Number of results to skip (for pagination)
    
    Returns:
        List of email documents
    
    Example:
        # Get all "work" classified emails
        work_emails = await mongo.get_classified_emails_by_label(
            "work",
            limit=50,
            skip=0
        )
    """
    try:
        collection = self.db["classified_emails"]
        
        # Ensure limit doesn't exceed max
        limit = min(limit, 1000)
        
        # Build query (newest first)
        cursor = collection.find(
            {"classification_label": classification_label}
        ).sort("created_at", -1).skip(skip).limit(limit)
        
        results = await cursor.to_list(length=limit)
        
        logger.debug(
            f"Retrieved {len(results)} emails with label "
            f"'{classification_label}'"
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to query classified emails: {str(e)}")
        return []
```

---

## Saving Classified Emails

### Data Models (`src/models/database.py`)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ClassificationLabel(str, Enum):
    """Classification Labels"""
    SPAM = "spam"
    WORK = "work"
    PERSONAL = "personal"
    PROMOTIONAL = "promotional"
    SOCIAL = "social"
    IMPORTANT = "important"

class ExtractedEntity(BaseModel):
    """Extracted Entities"""
    entity_type: str  # deadline, amount, requester, etc
    value: str
    confidence: float = 1.0

class SentimentAnalysis(BaseModel):
    """Sentiment Analysis Results"""
    sentiment: str  # positive, negative, neutral
    score: float  # Range: 0-100
    urgency_level: str = "normal"  # low, normal, high, critical

class ClassifiedEmail(BaseModel):
    """Complete Classified Email Document"""
    
    # Basic Information
    email_id: str = Field(..., description="Unique email identifier")
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject")
    body_text: str = Field(..., description="Email body text")
    
    # AI Classification Results
    classification_label: ClassificationLabel = Field(
        ..., 
        description="Classification label (Spam/Work/Personal etc)"
    )
    confidence_score: float = Field(
        ..., 
        ge=0, 
        le=1, 
        description="Confidence score (0-1)"
    )
    
    # AI Analysis Results
    summary: Optional[str] = Field(
        None, 
        description="5-second content summary"
    )
    extracted_entities: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Extracted entities (deadlines, amounts, requesters etc)"
    )
    sentiment_analysis: Optional[SentimentAnalysis] = Field(
        None, 
        description="Sentiment and urgency level analysis"
    )
    
    # Metadata
    processing_time_ms: float = Field(
        0, 
        description="Processing time (milliseconds)"
    )
    model_version: str = Field("1.0", description="Model version")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation time"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update time"
    )
    status: str = Field("completed", description="Processing status")
    retry_count: int = Field(0, ge=0, description="Retry count")
    error_message: Optional[str] = Field(None, description="Error message")
    
    class Config:
        from_attributes = True
```

### Usage Examples

```python
# Use in FastAPI routes
from fastapi import FastAPI, Depends
from src.services.mongodb_service import MongoDBService

app = FastAPI()
mongo_service = MongoDBService()

@app.on_event("startup")
async def startup():
    """Connect to MongoDB on application startup"""
    await mongo_service.connect()

@app.on_event("shutdown")
async def shutdown():
    """Disconnect from MongoDB on application shutdown"""
    await mongo_service.disconnect()

@app.post("/api/v1/emails/classify")
async def classify_and_save_email(email_data: EmailData):
    """
    Classify email and save to MongoDB
    """
    try:
        # 1. AI Classification
        classification_result = await classify_email(email_data)
        
        # 2. Create classified email object
        classified_email = ClassifiedEmail(
            email_id=email_data.message_id,
            sender=email_data.from_email,
            subject=email_data.subject,
            body_text=email_data.body,
            classification_label=classification_result["label"],
            confidence_score=classification_result["confidence"],
            summary=classification_result["summary"],
            extracted_entities=classification_result["entities"],
            sentiment_analysis=classification_result["sentiment"],
            processing_time_ms=classification_result["processing_time"]
        )
        
        # 3. Save to MongoDB
        doc_id = await mongo_service.save_classified_email(classified_email)
        
        return {
            "status": "success",
            "document_id": doc_id,
            "classification": classification_result["label"],
            "confidence": classification_result["confidence"]
        }
        
    except Exception as e:
        logger.error(f"Classification and save failed: {str(e)}")
        return {"status": "error", "message": str(e)}
```

---

## Docker Compose Setup

### MongoDB Service in `docker-compose.yml`

```yaml
version: '3.8'

services:
  # MongoDB Database (Production-Grade Configuration)
  mongodb:
    image: mongo:7.0
    container_name: email_classifier_mongodb
    
    # Environment Variables
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USER:-admin}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD:-changeme123}
      MONGO_INITDB_DATABASE: ${MONGODB_DB_NAME:-email_classifier}
    
    # Port Mapping
    ports:
      - "27017:27017"
    
    # Data Persistence Volumes
    volumes:
      - mongodb_data:/data/db          # Data volume
      - mongodb_config:/data/configdb  # Configuration volume
      - mongodb_logs:/var/log/mongodb  # Logs volume
    
    # Network Configuration
    networks:
      - email_classifier_network
    
    # MongoDB Startup Command
    command: mongod --wiredTigerCacheSizeGB 2
    
    # Health Check (Ensure Container Starts Successfully)
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s      # Check every 10 seconds
      timeout: 5s        # Timeout 5 seconds
      retries: 5         # Retry 5 times
      start_period: 30s  # Startup wait period 30 seconds
    
    # Restart Policy
    restart: unless-stopped
    
    # Resource Limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    
    # Logging Configuration
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "10"

  # Redis (Cache Layer)
  redis:
    image: redis:7-alpine
    container_name: email_classifier_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - email_classifier_network
    command: redis-server --appendonly yes --maxmemory 512mb
    restart: unless-stopped

  # FastAPI Application
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: email_classifier_api
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://${MONGODB_USER:-admin}:${MONGODB_PASSWORD:-changeme123}@mongodb:27017
      MONGODB_DB_NAME: ${MONGODB_DB_NAME:-email_classifier}
    depends_on:
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - email_classifier_network
    restart: unless-stopped

# Network Definition
networks:
  email_classifier_network:
    driver: bridge

# Volume Definition
volumes:
  mongodb_data:
  mongodb_config:
  mongodb_logs:
  redis_data:
```

### Startup Commands

```bash
# 1. Create .env file
cat > .env << EOF
MONGODB_USER=admin
MONGODB_PASSWORD=changeme123
MONGODB_DB_NAME=email_classifier
GCP_PROJECT_ID=your-project-id
GCP_CREDENTIALS_PATH=/app/credentials/service-account-key.json
EOF

# 2. Start all services
docker-compose up -d

# 3. Check service status
docker-compose ps

# 4. View MongoDB logs
docker-compose logs mongodb

# 5. Connect to MongoDB (local testing)
mongosh mongodb://admin:changeme123@localhost:27017

# 6. Stop all services
docker-compose down

# 7. Complete cleanup (including data)
docker-compose down -v
```

---

## Usage Examples

### 1. Complete Email Processing Workflow

```python
from datetime import datetime, timedelta

async def process_email_workflow(raw_email: EmailData):
    """Complete email processing workflow"""
    
    # Initialize service
    mongo_service = MongoDBService()
    await mongo_service.connect()
    
    try:
        # 1. AI Classification
        classification = await ai_classifier.classify(raw_email.body)
        
        # 2. Entity Extraction
        entities = await entity_extractor.extract(raw_email.body)
        
        # 3. Sentiment Analysis
        sentiment = await sentiment_analyzer.analyze(raw_email.body)
        
        # 4. Generate Summary
        summary = await summarizer.summarize(raw_email.body, max_length=500)
        
        # 5. Create Classified Email Object
        classified_email = ClassifiedEmail(
            email_id=raw_email.message_id,
            sender=raw_email.from_email,
            subject=raw_email.subject,
            body_text=raw_email.body,
            classification_label=classification["label"],
            confidence_score=classification["confidence"],
            summary=summary,
            extracted_entities=entities,
            sentiment_analysis=sentiment,
            processing_time_ms=classification["processing_time"]
        )
        
        # 6. Save to MongoDB
        doc_id = await mongo_service.save_classified_email(classified_email)
        
        return {
            "success": True,
            "document_id": doc_id,
            "classification": classification["label"]
        }
        
    finally:
        await mongo_service.disconnect()
```

### 2. Query Classified Emails

```python
async def get_work_emails(limit: int = 50):
    """Get all "work" classified emails"""
    
    mongo_service = MongoDBService()
    await mongo_service.connect()
    
    try:
        # Query by classification label
        work_emails = await mongo_service.get_classified_emails_by_label(
            classification_label="work",
            limit=limit
        )
        
        return work_emails
        
    finally:
        await mongo_service.disconnect()
```

### 3. Advanced Query Examples

```python
async def advanced_search():
    """Advanced search example"""
    
    mongo_service = MongoDBService()
    await mongo_service.connect()
    
    try:
        # Query urgent work emails from specific sender in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        results = await mongo_service.search_classified_emails(
            query={
                "classification_label": "work",
                "sender": "boss@company.com",
                "created_at": {"$gte": week_ago},
                "sentiment_analysis.urgency_level": {"$in": ["high", "critical"]}
            },
            limit=100,
            sort_by="created_at",
            sort_order=-1  # Newest first
        )
        
        return results
        
    finally:
        await mongo_service.disconnect()
```

---

## Performance Optimization

### 1. Connection Pool Optimization

```python
# Optimization settings example
{
    "maxPoolSize": 50,           # ✓ Large enough for concurrent requests
    "minPoolSize": 10,           # ✓ Keep hot connections to avoid cold start
    "maxIdleTimeMS": 45000,      # ✓ Recycle idle connections after 45 seconds
    "serverSelectionTimeoutMS": 5000  # ✓ Quick failover
}
```

### 2. Indexing Strategy

```python
# Critical indexes
await collection.create_index("email_id", unique=True)  # Uniqueness
await collection.create_index([("created_at", -1)])      # Date range query
await collection.create_index("classification_label")    # Classification filter
await collection.create_index("sender")                  # Sender query

# TTL index (auto-delete old data)
await collection.create_index("created_at", expireAfterSeconds=7776000)
```

### 3. Query Optimization

```python
# ✓ Good practice: Use indexed fields
db.classified_emails.find({"classification_label": "work"}).limit(100)

# ✗ Bad practice: Full table scan
db.classified_emails.find({"summary": {"$regex": "deadline"}})

# ✓ Use projection to reduce data transfer
db.classified_emails.find(
    {"classification_label": "work"},
    {"email_id": 1, "sender": 1, "subject": 1, "confidence_score": 1}
)
```

### 4. Bulk Operations

```python
async def bulk_save_emails(emails: List[ClassifiedEmail]):
    """Bulk save emails (more efficient)"""
    
    collection = self.db["classified_emails"]
    
    # Prepare bulk operations
    operations = []
    for email in emails:
        operations.append(
            UpdateOne(
                {"email_id": email.email_id},
                {"$set": email.dict()},
                upsert=True
            )
        )
    
    # Execute all operations at once
    result = await collection.bulk_write(operations)
    
    return result.upserted_id or result.modified_count
```

---

## Troubleshooting

### Issue 1: MongoDB Connection Timeout

```bash
# Check container running status
docker-compose ps

# View MongoDB logs
docker-compose logs mongodb

# Check network connectivity
docker exec email_classifier_api ping mongodb
```

### Issue 2: Poor Index Performance

```python
# Analyze query performance
result = await collection.find(query).explain()
print(result)  # Check if indexes are being used

# Create missing index
await collection.create_index("field_name")
```

### Issue 3: High Memory Usage

```yaml
# Adjust WiredTiger cache size
command: mongod --wiredTigerCacheSizeGB 1  # Reduce to 1GB
```

---

## Summary

✅ **This integration provides**:
- Complete MongoDB + FastAPI async integration
- Production-grade connection pool management
- Optimized indexing strategy
- Comprehensive error handling
- Containerized Docker deployment

💡 **Key Points**:
1. Use Motor async driver for non-blocking operations
2. Configure connection pool size appropriately
3. Create indexes for frequently queried fields
4. Use TTL indexes to automatically clean up expired data
5. Monitor performance metrics regularly

---

## Related Resources

- [Motor Official Documentation](https://motor.readthedocs.io/)
- [MongoDB Best Practices](https://docs.mongodb.com/manual/administration/production-checklist/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
