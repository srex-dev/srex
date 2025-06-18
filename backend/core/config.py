from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SREX API"
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SREX_SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: List[str] = os.getenv("SREX_CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = int(os.getenv("SREX_RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("SREX_RATE_LIMIT_WINDOW", "60"))
    
    # API Key Settings
    API_KEY_PREFIX: str = "srex_"
    API_KEY_LENGTH: int = 32
    API_KEY_EXPIRY_DAYS: int = 90
    
    # File Storage
    UPLOAD_DIR: Path = Path("uploads")
    POLICY_DIR: Path = Path("policies")
    SLO_DIR: Path = Path("slos")
    
    # Logging
    LOG_LEVEL: str = os.getenv("SREX_LOG_LEVEL", "INFO")
    LOG_FILE: Path = Path("logs/api.log")
    
    # Metrics
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.POLICY_DIR.mkdir(parents=True, exist_ok=True)
settings.SLO_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True) 