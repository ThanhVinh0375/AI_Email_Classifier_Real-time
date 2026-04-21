"""MongoDB service for data persistence"""
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from datetime import datetime, timedelta
from src.config import settings
from src.utils import get_logger
from src.models.database import ProcessedEmail, AuditLog, ClassifiedEmail

logger = get_logger(__name__)

class MongoDBService:
    """MongoDB service for data operations with async Motor driver"""
    
    def __init__(self):
        """Initialize MongoDB service"""
        self.connection_string = settings.mongodb_url
        self.db_name = settings.mongodb_db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """
        Connect to MongoDB with Motor async driver.
        
        Configures connection pooling and performance tuning settings:
        - maxPoolSize: Controls maximum concurrent connections
        - minPoolSize: Ensures minimum warm connections available
        - serverSelectionTimeoutMS: Timeout for MongoDB discovery
        - socketTimeoutMS: Timeout for individual socket operations
        """
        try:
            # Build Motor connection with connection pooling optimization
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
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(
                f"Connected to MongoDB database: {self.db_name} "
                f"(Pool size: {settings.mongodb_max_pool_size})"
            )
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """
        Create database indexes for optimal query performance.
        
        Indexes are created on both 'processed_emails' and 'classified_emails' collections
        to support common query patterns in the real-time email classification pipeline.
        """
        try:
            # Indexes for 'processed_emails' collection (existing)
            emails_col = self.db["processed_emails"]
            await emails_col.create_index("message_id", unique=True)
            await emails_col.create_index("received_date")
            await emails_col.create_index("classification")
            await emails_col.create_index("from_email")
            
            # Indexes for 'classified_emails' collection (new)
            classified_col = self.db["classified_emails"]
            await classified_col.create_index("email_id", unique=True)
            # Compound index for recent email lookups by date
            await classified_col.create_index([("created_at", -1), ("email_id", 1)])
            await classified_col.create_index("classification_label")
            await classified_col.create_index("sender")
            await classified_col.create_index("created_at", expireAfterSeconds=7776000)  # 90-day TTL
            
            # Audit logs collection indexes
            logs_col = self.db["audit_logs"]
            await logs_col.create_index("timestamp")
            await logs_col.create_index("event_type")
            await logs_col.create_index("message_id")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
    
    # ==================== ORIGINAL METHODS (processed_emails) ====================
    
    async def save_processed_email(self, email_data: ProcessedEmail) -> str:
        """Save processed email to database"""
        try:
            collection: AsyncIOMotorCollection = self.db["processed_emails"]
            result = await collection.insert_one(email_data.dict())
            logger.info(f"Saved processed email: {email_data.message_id}")
            # Also upsert a document into `classified_emails` so the dashboard
            # (which reads `classified_emails`) shows the newly processed email.
            try:
                classified_col: AsyncIOMotorCollection = self.db["classified_emails"]

                classified_doc = {
                    "email_id": email_data.message_id,
                    "sender": email_data.from_email,
                    "subject": email_data.subject,
                    "body_text": email_data.body,
                    "classification_label": getattr(email_data.classification, 'value', str(email_data.classification)),
                    "summary": (email_data.body[:200] if email_data.body else ""),
                    "extracted_entities": [],
                    "sentiment_analysis": None,
                    "processing_time_ms": 0,
                    "model_version": "1.0",
                    "confidence_score": float(email_data.confidence_score),
                    "created_at": email_data.processed_at,
                    "updated_at": email_data.processed_at,
                    "status": email_data.status,
                    "retry_count": email_data.retry_count
                }

                await classified_col.update_one(
                    {"email_id": email_data.message_id},
                    {"$set": classified_doc},
                    upsert=True
                )
                logger.info(f"Upserted classified_emails document: {email_data.message_id}")
            except Exception as e:
                logger.error(f"Failed to upsert classified_emails: {str(e)}")

            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save processed email: {str(e)}")
            raise
    
    async def get_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get email by message ID from processed_emails collection"""
        try:
            collection: AsyncIOMotorCollection = self.db["processed_emails"]
            result = await collection.find_one({"message_id": message_id})
            return result
        except Exception as e:
            logger.error(f"Failed to get email: {str(e)}")
            return None
    
    async def get_emails_by_classification(
        self, 
        classification: str, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get emails by classification from processed_emails collection"""
        try:
            collection: AsyncIOMotorCollection = self.db["processed_emails"]
            cursor = collection.find({"classification": classification}).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Failed to get emails by classification: {str(e)}")
            return []
    
    async def get_emails_by_sender(
        self, 
        from_email: str, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get emails from specific sender from processed_emails collection"""
        try:
            collection: AsyncIOMotorCollection = self.db["processed_emails"]
            cursor = collection.find({"from_email": from_email}).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Failed to get emails by sender: {str(e)}")
            return []
    
    async def log_audit(self, log_entry: AuditLog) -> None:
        """Log audit event"""
        try:
            collection: AsyncIOMotorCollection = self.db["audit_logs"]
            await collection.insert_one(log_entry.dict())
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics from processed_emails collection"""
        try:
            collection: AsyncIOMotorCollection = self.db["processed_emails"]
            
            total_emails = await collection.count_documents({})
            
            # Count by classification
            stats = await collection.aggregate([
                {"$group": {"_id": "$classification", "count": {"$sum": 1}}}
            ]).to_list(length=10)
            
            classification_stats = {item["_id"]: item["count"] for item in stats}
            
            return {
                "total_emails": total_emails,
                "by_classification": classification_stats
            }
        except Exception as e:
            logger.error(f"Failed to get processing stats: {str(e)}")
            return {}
    
    async def update_email_status(
        self, 
        message_id: str, 
        status: str, 
        error: Optional[str] = None
    ) -> bool:
        """Update email processing status"""
        try:
            collection: AsyncIOMotorCollection = self.db["processed_emails"]
            update_data = {
                "status": status,
                "processed_at": datetime.utcnow()
            }
            if error:
                update_data["error_message"] = error
            
            result = await collection.update_one(
                {"message_id": message_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update email status: {str(e)}")
            return False
    
    # ==================== NEW METHODS (classified_emails) ====================
    
    async def save_classified_email(self, email_data: ClassifiedEmail) -> str:
        """
        Save a classified email to the database.
        
        This is the primary method for storing AI-classified emails with complete
        analysis results including summary, extracted entities, and sentiment analysis.
        
        Args:
            email_data: ClassifiedEmail object containing complete classification results
            
        Returns:
            str: MongoDB document _id as string
            
        Raises:
            Exception: If database operation fails
            
        Example:
            classified_email = ClassifiedEmail(
                email_id="msg_123",
                sender="user@example.com",
                subject="Important: Q1 Review",
                body_text="Please review Q1 results...",
                classification_label="work",
                summary="Q1 performance review request",
                extracted_entities=[...],
                sentiment_analysis={...},
                confidence_score=0.95
            )
            doc_id = await mongo_service.save_classified_email(classified_email)
        """
        try:
            collection: AsyncIOMotorCollection = self.db["classified_emails"]
            
            # Prepare document - update timestamp
            email_dict = email_data.dict()
            email_dict["updated_at"] = datetime.utcnow()
            
            # Use upsert to handle duplicate email_ids gracefully
            result = await collection.update_one(
                {"email_id": email_data.email_id},
                {"$set": email_dict},
                upsert=True
            )
            
            # Log success with classification label
            log_msg = f"Saved classified email: {email_data.email_id} as {email_data.classification_label.value}"
            logger.info(log_msg)
            
            # Return the email_id or upserted document id
            return email_data.email_id
            
        except Exception as e:
            logger.error(f"Failed to save classified email '{email_data.email_id}': {str(e)}")
            raise
    
    async def get_classified_email_by_id(
        self, 
        email_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a classified email by email_id.
        
        Args:
            email_id: Unique email identifier
            
        Returns:
            Dict with email document or None if not found
        """
        try:
            collection: AsyncIOMotorCollection = self.db["classified_emails"]
            result = await collection.find_one({"email_id": email_id})
            
            if result:
                logger.debug(f"Retrieved classified email: {email_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get classified email '{email_id}': {str(e)}")
            return None
    
    async def get_classified_emails_by_sender(
        self, 
        sender: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve classified emails from a specific sender with pagination.
        
        Args:
            sender: Sender email address
            limit: Maximum number of results (default 50, max 1000)
            skip: Number of results to skip for pagination
            
        Returns:
            List of email documents
        """
        try:
            collection: AsyncIOMotorCollection = self.db["classified_emails"]
            
            # Ensure limit doesn't exceed max
            limit = min(limit, 1000)
            
            cursor = collection.find({"sender": sender}) \
                .sort("created_at", -1) \
                .skip(skip) \
                .limit(limit)
            
            results = await cursor.to_list(length=limit)
            logger.debug(f"Retrieved {len(results)} classified emails from {sender}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get emails from sender '{sender}': {str(e)}")
            return []
    
    async def get_classified_emails_by_label(
        self,
        classification_label: str,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve classified emails by classification label (Work, Personal, Spam, etc).
        
        Args:
            classification_label: Classification label to filter by
            limit: Maximum number of results (default 100, max 1000)
            skip: Number of results to skip for pagination
            
        Returns:
            List of email documents
        """
        try:
            collection: AsyncIOMotorCollection = self.db["classified_emails"]
            
            limit = min(limit, 1000)
            
            cursor = collection.find({"classification_label": classification_label}) \
                .sort("created_at", -1) \
                .skip(skip) \
                .limit(limit)
            
            results = await cursor.to_list(length=limit)
            logger.debug(f"Retrieved {len(results)} emails with label: {classification_label}")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to get emails by label '{classification_label}': {str(e)}")
            return []
    
    async def search_classified_emails(
        self,
        query: Dict[str, Any],
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "created_at",
        sort_order: int = -1
    ) -> List[Dict[str, Any]]:
        """
        Flexible MongoDB query search for classified emails.
        
        Args:
            query: MongoDB query dictionary (e.g., {"sender": "user@example.com", "classification_label": "work"})
            limit: Maximum number of results
            skip: Number of results to skip
            sort_by: Field to sort by (default: created_at)
            sort_order: Sort order (1 for ascending, -1 for descending)
            
        Returns:
            List of email documents matching query
            
        Example:
            # Find work emails from specific sender created in last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            results = await mongo.search_classified_emails({
                "classification_label": "work",
                "sender": "boss@company.com",
                "created_at": {"$gte": week_ago}
            })
        """
        try:
            collection: AsyncIOMotorCollection = self.db["classified_emails"]
            
            limit = min(limit, 1000)
            
            cursor = collection.find(query) \
                .sort(sort_by, sort_order) \
                .skip(skip) \
                .limit(limit)
            
            results = await cursor.to_list(length=limit)
            logger.debug(f"Search query returned {len(results)} classified emails")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to search classified emails with query {query}: {str(e)}")
            return []
    
    async def get_classified_email_stats(self) -> Dict[str, Any]:
        """
        Get statistics for classified emails collection.
        
        Returns:
            Dict with total count and counts by classification_label
        """
        try:
            collection: AsyncIOMotorCollection = self.db["classified_emails"]
            
            total_emails = await collection.count_documents({})
            
            # Aggregate by classification label
            stats = await collection.aggregate([
                {"$group": {
                    "_id": "$classification_label",
                    "count": {"$sum": 1},
                    "avg_confidence": {"$avg": "$confidence_score"}
                }}
            ]).to_list(length=10)
            
            classification_stats = {
                item["_id"]: {
                    "count": item["count"],
                    "avg_confidence": round(item["avg_confidence"], 3)
                }
                for item in stats
            }
            
            # Get average processing time
            avg_time = await collection.aggregate([
                {"$group": {"_id": None, "avg_ms": {"$avg": "$processing_time_ms"}}}
            ]).to_list(length=1)
            
            avg_processing_time = avg_time[0]["avg_ms"] if avg_time else 0
            
            return {
                "total_classified_emails": total_emails,
                "by_classification": classification_stats,
                "avg_processing_time_ms": round(avg_processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get classified email stats: {str(e)}")
            return {}


# ==================== GLOBAL INSTANCE ====================

_mongo_service: Optional[MongoDBService] = None

async def get_mongo_service() -> MongoDBService:
    """
    Get or create MongoDB service instance (singleton pattern).
    
    Returns:
        MongoDBService: Global MongoDB service instance
        
    Note:
        This function uses a singleton pattern to ensure only one MongoDB
        connection is maintained throughout the application lifecycle.
    """
    global _mongo_service
    if _mongo_service is None:
        _mongo_service = MongoDBService()
        await _mongo_service.connect()
    return _mongo_service
