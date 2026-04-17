"""Services module - lazy imports for optional dependencies"""

def get_pubsub_service():
    """Lazy import for Pub/Sub service"""
    from .pubsub_service import get_pubsub_service as _get_pubsub_service
    return _get_pubsub_service()

def get_mongo_service():
    """Lazy import for MongoDB service"""
    from .mongodb_service import get_mongo_service as _get_mongo_service
    return _get_mongo_service()

def get_email_processing_service():
    """Lazy import for Email processing service"""
    from .email_service import get_email_processing_service as _get_email_processing_service
    return _get_email_processing_service()

def get_gmail_service():
    """Lazy import for Gmail service"""
    from .gmail_service import get_gmail_service as _get_gmail_service
    return _get_gmail_service()

# Direct imports for type hints (optional)
try:
    from .pubsub_service import PubSubService
except ImportError:
    PubSubService = None

try:
    from .mongodb_service import MongoDBService
except ImportError:
    MongoDBService = None

try:
    from .email_service import EmailProcessingService
except ImportError:
    EmailProcessingService = None

try:
    from .gmail_service import GmailService
except ImportError:
    GmailService = None

__all__ = [
    "get_pubsub_service",
    "PubSubService",
    "get_mongo_service",
    "MongoDBService",
    "get_email_processing_service",
    "EmailProcessingService",
    "get_gmail_service",
    "GmailService"
]
