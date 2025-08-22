import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://username:password@localhost:5432/astrochat"
    chroma_persist_directory: str = "./chroma_db"
    
    # Google Gemini API
    gemini_api_key: str
    
    # Redis Configuration (Optional)
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # Panchang API (Future)
    panchang_api_url: Optional[str] = None
    panchang_api_key: Optional[str] = None
    
    # ChromaDB Settings
    chroma_telemetry_enabled: bool = True
    
    # Cache Settings
    cache_ttl_minutes: int = 30  # Cache TTL in minutes
    
    # Application Settings
    debug: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
