"""
AdMaster AI Backend - FastAPI Application
"""
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env file for os.getenv() to work
load_dotenv()

from app.core.config import settings
from app.core.database import db
from app.core.exceptions import AdMasterException
from app.core.error_handler import (
    admaster_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.api.v1 import businesses, users, webhooks, brands, campaigns, platforms
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("🚀 Starting AdMaster AI Backend...")
    await db.connect_db()
    print(f"✅ Server running on {settings.HOST}:{settings.PORT}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await db.close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered marketing automation platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
app.add_exception_handler(AdMasterException, admaster_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PydanticValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Health check
@app.get("/", tags=["health"])
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.ENV,
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENV,
    }


# Include routers
app.include_router(businesses.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_V1_PREFIX)
app.include_router(brands.router, prefix=settings.API_V1_PREFIX)
app.include_router(campaigns.router, prefix=settings.API_V1_PREFIX)
app.include_router(platforms.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

