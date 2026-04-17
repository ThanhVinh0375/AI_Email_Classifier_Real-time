"""Google Cloud Pub/Sub service for receiving Gmail notifications"""
import json
import base64
from typing import Callable, Optional

try:
    from google.cloud import pubsub_v1
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    pubsub_v1 = None
    service_account = None

from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)

class PubSubService:
    """Google Cloud Pub/Sub service"""
    
    def __init__(self):
        """Initialize Pub/Sub service"""
        self.project_id = settings.gcp_project_id
        self.credentials_path = settings.gcp_credentials_path
        self.subscriber = None
        self.subscription_path = settings.gcp_pubsub_subscription
        
    def initialize(self):
        """Initialize Pub/Sub subscriber"""
        if not GOOGLE_CLOUD_AVAILABLE:
            logger.warning("Google Cloud packages not available. Pub/Sub service disabled.")
            return
        
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path
            )
            self.subscriber = pubsub_v1.SubscriberClient(credentials=credentials)
            logger.info("Pub/Sub service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pub/Sub service: {str(e)}")
            raise
    
    def subscribe(self, callback: Callable[[dict], None]) -> None:
        """Subscribe to Gmail notifications"""
        if not self.subscriber:
            self.initialize()
        
        try:
            future = self.subscriber.subscribe(self.subscription_path, callback=callback)
            logger.info(f"Subscribed to {self.subscription_path}")
            
            # Keep the subscriber running
            try:
                future.result()
            except KeyboardInterrupt:
                future.cancel()
                logger.info("Subscription cancelled")
        except Exception as e:
            logger.error(f"Subscription error: {str(e)}")
            raise
    
    @staticmethod
    def decode_pubsub_message(message: dict) -> dict:
        """
        Decode Google Cloud Pub/Sub message
        
        Args:
            message: Raw Pub/Sub message
            
        Returns:
            Decoded message data
        """
        try:
            # The message data is base64 encoded
            data = message.get("message", {}).get("data", "")
            attributes = message.get("message", {}).get("attributes", {})
            
            if data:
                decoded_data = base64.b64decode(data).decode('utf-8')
                return {
                    "data": json.loads(decoded_data),
                    "attributes": attributes,
                    "message_id": message.get("message", {}).get("messageId", "")
                }
            return {"data": {}, "attributes": attributes}
        except Exception as e:
            logger.error(f"Failed to decode Pub/Sub message: {str(e)}")
            raise
    
    def acknowledge_message(self, subscription_path: str, ack_ids: list) -> None:
        """Acknowledge received messages"""
        if not self.subscriber:
            return
        
        try:
            self.subscriber.acknowledge(subscription_path, ack_ids)
            logger.debug(f"Acknowledged {len(ack_ids)} messages")
        except Exception as e:
            logger.error(f"Failed to acknowledge messages: {str(e)}")

# Global instance
_pubsub_service: Optional[PubSubService] = None

def get_pubsub_service() -> PubSubService:
    """Get or create Pub/Sub service instance"""
    global _pubsub_service
    if _pubsub_service is None:
        _pubsub_service = PubSubService()
    return _pubsub_service
