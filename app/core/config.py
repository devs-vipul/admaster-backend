"""
Application configuration and environment variables
"""
from typing import List, Union, Optional
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
    ALGORITHM: str  # JWT algorithm (e.g., "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int  # Token expiration in minutes
    
    # Campaign defaults (from env or constants)
    DEFAULT_CURRENCY: Optional[str] = None  # Default currency code (e.g., "INR", "USD")
    DEFAULT_DAILY_BUDGET: Optional[float] = None  # Default daily budget (e.g., 0.0)
    
    # Note: Gemini AI configuration (GOOGLE_API_KEY, GEMINI_MODEL, DEFAULT_MODEL) 
    # is handled directly via os.getenv() in the service code, not through Settings
    
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
        extra="ignore",  # Ignore extra env vars not defined in Settings (e.g., GEMINI_API_KEY, GEMINI_MODEL, DEFAULT_MODEL)
    )


# Global settings instance
settings = Settings()

