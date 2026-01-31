"""
Configuration management for Inventix AI Backend
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "sqlite:///./inventix.db"
    
    # File uploads
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50
    allowed_extensions: str = ".pdf,.docx,.doc,.txt"
    
    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
    
    # API
    api_prefix: str = "/api"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def allowed_extensions_list(self) -> list[str]:
        return [ext.strip() for ext in self.allowed_extensions.split(",")]
    
    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Ensure upload directory exists
def ensure_upload_dir():
    settings = get_settings()
    os.makedirs(settings.upload_dir, exist_ok=True)
