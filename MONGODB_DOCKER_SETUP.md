# MongoDB & FastAPI Docker Setup Guide

Comprehensive guide for setting up and running the AI Email Classifier with MongoDB and FastAPI using Docker Compose.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Environment Configuration](#environment-configuration)
4. [Docker Compose Services](#docker-compose-services)
5. [MongoDB Connection Pooling](#mongodb-connection-pooling)
6. [Performance Tuning](#performance-tuning)
7. [Health Checks & Monitoring](#health-checks--monitoring)
8. [Development vs Production](#development-vs-production)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Quick Start

### 1. Start All Services

```bash
# Navigate to project root
cd e:\PJ Data\AI_Email_Classifier_Real-time

# Start all services in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 2. Verify Services Are Healthy

```bash
# Wait for all services to be healthy (takes ~30-40 seconds)
# Services will show "healthy" status in docker-compose ps output

# Test MongoDB connection
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 --eval "db.runCommand('ping')"

# Test FastAPI
curl http://localhost:8000/api/v1/stats

# Test Redis
docker exec email_classifier_redis redis-cli ping
```

### 3. Access Admin Panels

- **MongoDB Express** (Web UI): http://localhost:8081
  - Username: `admin`
  - Password: `admin123`

- **Redis Commander** (Web UI): http://localhost:8082

- **FastAPI Swagger Docs**: http://localhost:8000/docs

---

## Prerequisites

### System Requirements

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 1.29+ ([Install Compose](https://docs.docker.com/compose/install/))
- **Disk Space**: 5GB minimum (MongoDB + Redis + Application)
- **RAM**: 8GB minimum (4GB for MongoDB, 2GB for FastAPI, 512MB for Redis)

### Verify Installation

```bash
docker --version
docker-compose --version
```

---

## Environment Configuration

### 1. Create `.env` File

Create a `.env` file in the project root with the following variables:

```env
# MongoDB Configuration
MONGODB_USER=admin
MONGODB_PASSWORD=changeme123
MONGODB_DB_NAME=email_classifier

# FastAPI Configuration
API_ENV=production
API_WORKERS=4
LOG_LEVEL=INFO

# Google Cloud Configuration (required for email processing)
GCP_PROJECT_ID=your-gcp-project-id
GCP_CREDENTIALS_PATH=/app/credentials/service-account-key.json

# LLM Configuration
LLM_API_PROVIDER=openai  # or "claude"
LLM_MODEL=gpt-3.5-turbo

# Admin Panel Credentials
ADMIN_USER=admin
ADMIN_PASSWORD=admin123
```

### 2. GCP Credentials Setup

```bash
# Copy your GCP service account key to credentials folder
mkdir -p credentials
cp /path/to/service-account-key.json credentials/
```

### 3. Override Variables (Optional)

You can override any environment variable when starting:

```bash
docker-compose up -d -e MONGODB_PASSWORD=super_secure_password
```

---

## Docker Compose Services

### MongoDB 7.0 Service

**Container**: `email_classifier_mongodb`  
**Port**: 27017  
**Purpose**: Primary data storage with async Motor driver

**Configuration Highlights:**
- **Replica Set**: `email_classifier_rs` (enables high availability)
- **Max Connections**: 200 (handles real-time workload)
- **Cache Size**: 2GB WiredTiger cache
- **Slow Query Logging**: Logs queries > 100ms
- **Data Volumes**: 
  - `mongodb_data` - Database files
  - `mongodb_config` - Replica set configuration
  - `mongodb_logs` - Query logs

**Connection String**:
```
mongodb://admin:password@mongodb:27017/email_classifier?authSource=admin
```

---

### FastAPI Service

**Container**: `email_classifier_api`  
**Port**: 8000  
**Purpose**: REST API for email classification and queries

**Configuration Highlights:**
- **Workers**: 4 (configurable via `API_WORKERS`)
- **HTTP Server**: Uvicorn with uvloop optimization
- **Connection Pooling**: Motor with 50 max connections
- **Health Check**: Every 15 seconds
- **Startup Time**: ~10 seconds

**Key Endpoints:**
```
POST   /api/v1/emails/classify-and-save          # Save classified email
GET    /api/v1/classified-emails/{email_id}      # Retrieve email
GET    /api/v1/classified-emails/sender/{sender} # Emails from sender
GET    /api/v1/classified-emails/label/{label}   # Emails by label
GET    /api/v1/classified-emails/stats           # Classification stats
```

---

### Redis Service

**Container**: `email_classifier_redis`  
**Port**: 6379  
**Purpose**: Cache layer for frequent queries

**Configuration:**
- **Max Memory**: 512MB
- **Eviction Policy**: LRU (least recently used)
- **Persistence**: AOF (append-only file)

---

### MongoDB Express (Optional)

**Container**: `email_classifier_mongodb_express`  
**Port**: 8081  
**Purpose**: Web UI for MongoDB management

Use this for:
- Browsing documents
- Running queries
- Viewing indexes
- Managing collections

---

### Redis Commander (Optional)

**Container**: `email_classifier_redis_commander`  
**Port**: 8082  
**Purpose**: Web UI for Redis management

Use this for:
- Viewing cached data
- Monitoring memory usage
- Debugging cache issues

---

## MongoDB Connection Pooling

### Motor Driver Configuration

Motor (async MongoDB driver) is configured in `src/config/settings.py`:

```python
# Connection pool settings
mongodb_max_pool_size: int = 50           # Max concurrent connections
mongodb_min_pool_size: int = 10           # Min pooled connections
mongodb_server_selection_timeout_ms: int = 5000
mongodb_socket_timeout_ms: int = 30000    # Per-operation timeout
mongodb_connect_timeout_ms: int = 10000
mongodb_max_idle_time_ms: int = 45000     # Recycle after idle
mongodb_retry_writes: bool = True         # Retry transient failures
mongodb_retry_reads: bool = True          # Retry read operations
```

### Tuning for Real-Time Workloads

For high-throughput email classification:

```python
# Increase for high-concurrency scenarios (1000+ emails/min)
mongodb_max_pool_size = 100
mongodb_min_pool_size = 20

# Reduce for low-latency requirements
mongodb_socket_timeout_ms = 10000  # 10 seconds

# Enable for write-heavy workloads
mongodb_retry_writes = True
```

### Monitor Connection Pool Usage

```bash
# Check MongoDB connection statistics
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 --eval "db.adminCommand('connPoolStats')"

# Monitor in real-time
docker logs -f email_classifier_api | grep "connection"
```

---

## Performance Tuning

### MongoDB WiredTiger Optimization

The `docker-compose.yml` includes these tuning parameters:

```yaml
--wiredTigerCacheSizeGB 2              # Cache memory
--wiredTigerEngineRuntimeConfig="eviction=(threads_min=4,threads_max=8)"  # Eviction threads
--maxConnections 200                   # Connection limit
--setParameter operationProfiling.slowOpThresholdMs=100  # Log slow queries
```

### FastAPI Performance

```bash
# Run with more workers for high throughput
docker-compose up -d -e API_WORKERS=8

# Monitor CPU/Memory
docker stats email_classifier_api
```

### Index Strategy

Indexes are automatically created on startup:

```javascript
// Classified emails collection
db.classified_emails.createIndex({ email_id: 1 }, { unique: true })
db.classified_emails.createIndex({ created_at: -1, email_id: 1 })  // Compound
db.classified_emails.createIndex({ classification_label: 1 })
db.classified_emails.createIndex({ sender: 1 })
db.classified_emails.createIndex({ created_at: 1 }, { expireAfterSeconds: 7776000 }) // 90-day TTL
```

### Enable Query Profiling

```bash
# Check slow queries (> 100ms)
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 --eval "db.system.profile.find({ millis: { \$gt: 100 } }).sort({ ts: -1 }).limit(5).pretty()"
```

---

## Health Checks & Monitoring

### Service Health Status

```bash
# View health status
docker-compose ps

# Expected output:
# NAME                              STATUS
# email_classifier_mongodb          healthy
# email_classifier_api              healthy
# email_classifier_redis            healthy
```

### Health Check Details

| Service | Health Check | Interval | Timeout |
|---------|-------------|----------|---------|
| MongoDB | `ping` command | 10s | 5s |
| FastAPI | GET `/api/v1/stats` | 15s | 5s |
| Redis | `PING` command | 10s | 5s |

### Monitor Resource Usage

```bash
# Real-time resource monitoring
docker stats

# MongoDB memory usage
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 --eval "db.stats()"

# API memory usage
docker inspect email_classifier_api | grep -i memory
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api

# Last N lines
docker-compose logs --tail=50 api

# Show timestamps
docker-compose logs -f --timestamps api
```

---

## Development vs Production

### Development Setup

```bash
# Use development overrides
docker-compose up -d

# Settings (from .env):
# API_ENV=development
# LOG_LEVEL=DEBUG
# API_WORKERS=2  # Lower for faster reload
```

Development features:
- Verbose logging
- Auto-reload on code changes (if using `--reload`)
- Smaller connection pools
- Lower resource limits

### Production Deployment

```bash
# Use production environment file
cp docker-compose.yml docker-compose.prod.yml

# Modify .env for production
# API_ENV=production
# LOG_LEVEL=INFO
# API_WORKERS=8
# MONGODB_PASSWORD=<strong_password>
```

Production recommendations:
1. **Security**: Change default MongoDB and admin passwords
2. **Scaling**: Increase `MONGODB_MAX_POOL_SIZE` and `API_WORKERS`
3. **Monitoring**: Enable ELK stack or Datadog integration
4. **Backup**: Set up automated MongoDB backups
5. **SSL/TLS**: Use reverse proxy (nginx) for HTTPS

---

## Troubleshooting

### Services Won't Start

**Problem**: `docker-compose up` fails with connection errors

```bash
# Solution 1: Check Docker daemon
docker ps

# Solution 2: Remove old containers
docker-compose down
docker-compose up -d

# Solution 3: Check logs
docker-compose logs mongodb
```

### MongoDB Connection Timeout

**Problem**: FastAPI can't connect to MongoDB

```bash
# Verify MongoDB is running and healthy
docker-compose ps mongodb

# Check logs
docker-compose logs mongodb

# Test direct connection
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 --eval "db.runCommand('ping')"

# Check network
docker network inspect email_classifier_network
```

### High Memory Usage

**Problem**: Docker containers consuming too much RAM

```bash
# Check current usage
docker stats

# Reduce MongoDB cache size in docker-compose.yml
--wiredTigerCacheSizeGB 1  # From 2 to 1

# Reduce pool size in settings.py
mongodb_max_pool_size = 25  # From 50 to 25

# Restart services
docker-compose down
docker-compose up -d
```

### Slow Queries

**Problem**: Email classification is slow

```bash
# View slow query logs (> 100ms)
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 << 'EOF'
db.system.profile.find({ millis: { $gt: 100 } })
  .sort({ ts: -1 })
  .limit(10)
  .pretty()
EOF

# Check indexes
docker exec email_classifier_mongodb mongosh --username admin --password changeme123 --eval "db.classified_emails.getIndexes()"
```

### Port Already in Use

**Problem**: `Address already in use` error

```bash
# Find process using port
lsof -i :27017  # MongoDB
lsof -i :8000   # FastAPI
lsof -i :6379   # Redis

# Kill process (Linux/Mac)
kill -9 <PID>

# Or use different ports in docker-compose.yml
ports:
  - "27018:27017"  # MongoDB on 27018
  - "8001:8000"    # FastAPI on 8001
```

---

## Best Practices

### 1. **Always Use Named Volumes**

```yaml
# ✓ Good: Named volumes persist data
volumes:
  - mongodb_data:/data/db

# ✗ Avoid: Bind mounts in production
volumes:
  - ./data:/data/db
```

### 2. **Set Resource Limits**

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
    reservations:
      cpus: '1'
      memory: 2G
```

### 3. **Use Health Checks**

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 15s
  timeout: 5s
  retries: 3
```

### 4. **Centralize Logging**

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "10"
```

### 5. **Enable Replica Sets (HA)**

```yaml
command: --replSet email_classifier_rs
```

Enables automatic failover and high availability.

### 6. **Regular Backups**

```bash
# Backup MongoDB
docker exec email_classifier_mongodb mongodump --out /backup/mongodb --username admin --password changeme123

# Restore from backup
docker exec email_classifier_mongodb mongorestore /backup/mongodb --username admin --password changeme123
```

### 7. **Monitor Connection Pool**

```python
# Add to startup checks
from src.services.mongodb_service import get_mongo_service

async def startup_event():
    mongo = await get_mongo_service()
    stats = await mongo.db.command('connectionPoolStats')
    print(f"Connection pool initialized: {stats['totalConnections']} connections")
```

### 8. **Use Environment Variables for Secrets**

```bash
# ✓ Good
MONGODB_PASSWORD=${DB_PASSWORD}

# ✗ Avoid
MONGODB_PASSWORD=hardcoded_password
```

---

## API Usage Examples

### Save a Classified Email

```bash
curl -X POST http://localhost:8000/api/v1/emails/classify-and-save \
  -H "Content-Type: application/json" \
  -d '{
    "email_id": "msg_123",
    "sender": "user@company.com",
    "subject": "Important Update",
    "body_text": "This is an important email...",
    "classification_label": "work",
    "summary": "Important company update",
    "extracted_entities": [],
    "sentiment_analysis": {
      "sentiment": "neutral",
      "score": 50,
      "urgency_level": "high"
    },
    "confidence_score": 0.95
  }'
```

### Get Classified Email Stats

```bash
curl http://localhost:8000/api/v1/classified-emails/stats | jq
```

### Query Emails by Label

```bash
curl "http://localhost:8000/api/v1/classified-emails/label/work?limit=20" | jq
```

---

## Next Steps

1. ✅ Start Docker services: `docker-compose up -d`
2. ✅ Run example script: `python scripts/example_mongodb_usage.py`
3. ✅ Test FastAPI endpoints: Visit `http://localhost:8000/docs`
4. ✅ Monitor services: Check `docker stats` and admin panels
5. ✅ Configure production settings: Update `.env` for your environment

---

## Additional Resources

- **MongoDB Documentation**: https://docs.mongodb.com/manual/
- **Motor (Async Driver)**: https://motor.readthedocs.io/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Docker Compose**: https://docs.docker.com/compose/
- **WiredTiger Tuning**: https://docs.mongodb.com/manual/core/wiredtiger/

---

## Support

For issues or questions:

1. Check Docker logs: `docker-compose logs -f`
2. Review [Troubleshooting](#troubleshooting) section
3. Verify prerequisites are installed
4. Ensure `.env` file is properly configured
