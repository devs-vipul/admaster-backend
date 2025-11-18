"""
Business model - Main entity for AdMaster AI
"""
from datetime import datetime
from typing import Optional
from enum import Enum
from beanie import Document
from pydantic import Field


class BusinessStatus(str, Enum):
    """Business status enum"""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class BusinessSize(str, Enum):
    """Business size enum"""
    SMALL = "Small (1 - 10 employees)"
    MEDIUM = "Medium (10 - 50 employees)"
    LARGE = "Large (50+ employees)"


class Industry(str, Enum):
    """Industry enum"""
    TECHNOLOGY = "Technology"
    HEALTHCARE = "Healthcare"
    ECOMMERCE = "E-commerce"
    FINANCE = "Finance"
    EDUCATION = "Education"
    REAL_ESTATE = "Real Estate"
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail"
    HOSPITALITY = "Hospitality"
    CONSULTING = "Consulting"
    MARKETING_ADVERTISING = "Marketing & Advertising"
    MEDIA_ENTERTAINMENT = "Media & Entertainment"
    FOOD_BEVERAGE = "Food & Beverage"
    PROFESSIONAL_SERVICES = "Professional Services"
    OTHER = "Other"


class Business(Document):
    """
    Business model - stores onboarded businesses
    Each business belongs to a user
    """
    
    # Owner (links to Clerk user)
    user_id: str = Field(..., index=True)  # Clerk user ID
    
    # Business information
    name: str = Field(..., min_length=1, max_length=200)
    website: str  # Store as string to avoid MongoDB serialization issues
    industry: Industry
    size: BusinessSize = BusinessSize.SMALL
    
    # Status
    status: BusinessStatus = BusinessStatus.ACTIVE
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "businesses"  # MongoDB collection name
        indexes = [
            "user_id",
            "status",
            [("user_id", 1), ("created_at", -1)],  # Compound index
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_2abc123xyz",
                "name": "Corider",
                "website": "https://corider.in",
                "industry": "Technology",
                "size": "Small (1 - 10 employees)",
                "status": "active",
            }
        }
    
    async def archive(self):
        """Archive this business"""
        self.status = BusinessStatus.ARCHIVED
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def pause(self):
        """Pause this business"""
        self.status = BusinessStatus.PAUSED
        self.updated_at = datetime.utcnow()
        await self.save()
    
    async def activate(self):
        """Activate this business"""
        self.status = BusinessStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        await self.save()

