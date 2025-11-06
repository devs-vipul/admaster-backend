"""
User model - Synced from Clerk
"""
from datetime import datetime
from typing import List, Optional
from beanie import Document
from pydantic import EmailStr, Field


class User(Document):
    """
    User model stored in MongoDB
    Synced from Clerk via webhooks
    """
    
    # Clerk user ID (foreign key)
    clerk_id: str = Field(..., unique=True, index=True)
    
    # User information
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None
    
    # Related entities
    businesses: List[str] = Field(default_factory=list)  # Array of business IDs
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login_at: Optional[datetime] = None
    
    class Settings:
        name = "users"  # MongoDB collection name
        indexes = [
            "clerk_id",
            "email",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "clerk_id": "user_2abc123xyz",
                "email": "user@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "image_url": "https://...",
                "businesses": [],
            }
        }
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email
    
    async def add_business(self, business_id: str):
        """Add a business to user's businesses list"""
        if business_id not in self.businesses:
            self.businesses.append(business_id)
            self.updated_at = datetime.utcnow()
            await self.save()
    
    async def remove_business(self, business_id: str):
        """Remove a business from user's businesses list"""
        if business_id in self.businesses:
            self.businesses.remove(business_id)
            self.updated_at = datetime.utcnow()
            await self.save()

