"""Main FastAPI application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.config import settings
from src.api import webhooks_router, emails_router
from src.services import get_mongo_service
from src.utils import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting up application...")
    try:
        mongo = await get_mongo_service()
        logger.info("MongoDB connection established")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    try:
        mongo = await get_mongo_service()
        await mongo.disconnect()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Event-Driven AI Email Classifier using Gmail Push Notifications",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhooks_router)
app.include_router(emails_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=(settings.api_env == "development")
    )
