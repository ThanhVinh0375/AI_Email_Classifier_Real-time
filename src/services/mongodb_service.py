"""MongoDB service for data persistence"""
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from datetime import datetime
from src.config import settings
from src.utils import get_logger
from src.models.database import ProcessedEmail, AuditLog

logger = get_logger(__name__)

class MongoDBService:
    """MongoDB service for data operations"""
    
    def __init__(self):
        """Initialize MongoDB service"""
        self.connection_string = settings.mongodb_url
        self.db_name = settings.mongodb_db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.db_name]
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"Connected to MongoDB database: {self.db_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """Create database indexes"""
        try:
            # Emails collection indexes
            emails_col = self.db["processed_emails"]
            await emails_col.create_index("message_id", unique=True)
            await emails_col.create_index("received_date")
            await emails_col.create_index("classification")
            await emails_col.create_index("from_email")
            
            # Audit logs collection indexes
            logs_col = self.db["audit_logs"]
            await logs_col.create_index("timestamp")
            await logs_col.create_index("event_type")
            await logs_col.create_index("message_id")
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Failed to create indexes: {str(e)}")
    
    async def save_processed_email(self, email_data: ProcessedEmail) -> str:
        """Save processed email to database"""
        try:
            collection: AsyncCollection = self.db["processed_emails"]
            result = await collection.insert_one(email_data.dict())
            logger.info(f"Saved processed email: {email_data.message_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to save processed email: {str(e)}")
            raise
    
    async def get_email(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get email by message ID"""
        try:
            collection: AsyncCollection = self.db["processed_emails"]
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
        """Get emails by classification"""
        try:
            collection: AsyncCollection = self.db["processed_emails"]
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
        """Get emails from specific sender"""
        try:
            collection: AsyncCollection = self.db["processed_emails"]
            cursor = collection.find({"from_email": from_email}).limit(limit)
            results = await cursor.to_list(length=limit)
            return results
        except Exception as e:
            logger.error(f"Failed to get emails by sender: {str(e)}")
            return []
    
    async def log_audit(self, log_entry: AuditLog) -> None:
        """Log audit event"""
        try:
            collection: AsyncCollection = self.db["audit_logs"]
            await collection.insert_one(log_entry.dict())
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        try:
            collection: AsyncCollection = self.db["processed_emails"]
            
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
            collection: AsyncCollection = self.db["processed_emails"]
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

# Global instance
_mongo_service: Optional[MongoDBService] = None

async def get_mongo_service() -> MongoDBService:
    """Get or create MongoDB service instance"""
    global _mongo_service
    if _mongo_service is None:
        _mongo_service = MongoDBService()
        await _mongo_service.connect()
    return _mongo_service
