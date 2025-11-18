"""
Platform model - Ad platforms supported by AdMaster AI
"""
from datetime import datetime
from typing import List, Optional
from enum import Enum
from beanie import Document
from pydantic import Field


class PlatformType(str, Enum):
    """Platform type enum"""
    SEARCH = "search"  # Google Ads, Bing Ads
    SOCIAL = "social"  # Facebook, Instagram, LinkedIn, Twitter/X
    DISPLAY = "display"  # Google Display Network, Programmatic
    VIDEO = "video"  # YouTube, TikTok
    SHOPPING = "shopping"  # Google Shopping, Amazon Ads
    NATIVE = "native"  # Taboola, Outbrain


class Platform(Document):
    """
    Platform model - stores ad platform information
    Used for platform recommendations
    """
    
    # Platform identification
    platform_id: int = Field(..., unique=True, index=True)  # Numeric ID matching competitor's system
    name: str = Field(..., min_length=1, max_length=100)  # e.g., "Google Ads", "Facebook"
    slug: str = Field(..., unique=True, index=True)  # e.g., "google-ads", "facebook"
    type: PlatformType
    
    # Platform details
    description: Optional[str] = None
    icon: Optional[str] = None  # Icon name or URL
    website_url: Optional[str] = None
    
    # Capabilities
    supports_search: bool = False
    supports_display: bool = False
    supports_video: bool = False
    supports_shopping: bool = False
    supports_mobile: bool = False
    
    # Recommendation factors
    best_for_goals: List[str] = Field(default_factory=list)  # ["website-traffic", "brand-awareness"]
    best_for_industries: List[str] = Field(default_factory=list)  # ["Technology", "E-commerce"]
    min_budget: Optional[float] = None  # Minimum daily budget
    currency_support: List[str] = Field(default_factory=list)  # ["USD", "INR", "EUR"]
    
    # Account requirements
    requires_own_account: bool = Field(default=False)  # Whether user needs their own ad account
    
    # Status
    is_active: bool = Field(default=True)
    is_beta: bool = Field(default=False)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "platforms"  # MongoDB collection name
        indexes = [
            "platform_id",
            "slug",
            "type",
            "is_active",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": 0,
                "name": "Google Ads",
                "slug": "google-ads",
                "type": "search",
                "description": "Reach customers on Google Search and Display Network",
                "icon": "Search",
                "supports_search": True,
                "supports_display": True,
                "best_for_goals": ["website-traffic", "online-leads"],
                "best_for_industries": ["Technology", "E-commerce"],
            }
        }

