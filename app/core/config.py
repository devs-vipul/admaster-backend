"""
Application configuration and environment variables
"""
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "AdMaster AI Backend"
    ENV: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # MongoDB
    MONGODB_URL: str
    MONGODB_DB_NAME: str = "admaster"
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_WEBHOOK_SECRET: str = ""
    
    # CORS
    FRONTEND_URL: str = "http://localhost:3000"
    ALLOWED_ORIGINS: Union[List[str], str] = "http://localhost:3000,http://localhost:3001"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
settings = Settings()

