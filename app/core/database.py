"""
MongoDB database connection and initialization
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from beanie import init_beanie
from typing import Optional

from app.core.config import settings
from app.models.user import User
from app.models.business import Business


class Database:
    """MongoDB database manager"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB"""
        try:
            # Create MongoDB client
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # Initialize Beanie ODM with models
            await init_beanie(
                database=cls.db,
                document_models=[User, Business],
            )
            
            print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
            
        except Exception as e:
            print(f"❌ Error connecting to MongoDB: {e}")
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            print("✅ MongoDB connection closed")


# Database instance
db = Database()


# Dependency to get database
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database"""
    return db.db

