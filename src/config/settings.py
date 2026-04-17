from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    """Application settings configuration"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_env: str = "development"
    api_title: str = "AI Email Classifier"
    api_version: str = "1.0.0"
    
    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "email_classifier"
    mongodb_user: Optional[str] = None
    mongodb_password: Optional[str] = None
    
    # Google Cloud Configuration
    gcp_project_id: str
    gcp_credentials_path: str
    gcp_pubsub_topic: str
    gcp_pubsub_subscription: str
    
    # Gmail API
    gmail_scopes: list = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.labels"
    ]
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key"
    webhook_secret: str = "your-webhook-secret"
    
    # Processing Configuration
    max_workers: int = 4
    batch_size: int = 10
    processing_timeout: int = 300  # 5 minutes
    
    # AI Model Configuration - Spam Detection
    spam_model_path: str = "./models/spam_detector.pkl"
    spam_detection_threshold: float = 0.7  # Confidence threshold for spam classification
    
    # LLM Configuration (OpenAI or Claude)
    llm_api_provider: str = "openai"  # "openai" or "claude"
    llm_api_key: Optional[str] = None  # Uses env variable OPENAI_API_KEY or ANTHROPIC_API_KEY
    llm_model: str = "gpt-3.5-turbo"  # OpenAI: gpt-3.5-turbo, gpt-4 | Claude: claude-3-sonnet
    llm_use_fallback: bool = True  # Use heuristics if API unavailable
    llm_timeout: int = 30  # Seconds
    llm_max_retries: int = 2
    
    # Hybrid Classifier Configuration
    enable_spam_detection: bool = True  # Enable Stage 1 spam detection
    enable_llm_analysis: bool = True   # Enable Stage 2 LLM analysis
    skip_llm_for_spam: bool = True     # Skip expensive LLM calls for spam
    classification_confidence_threshold: float = 0.7
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
