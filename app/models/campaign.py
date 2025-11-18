"""
Campaign model - Campaign groups created by users
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from beanie import Document
from pydantic import Field, HttpUrl


class ConversionGoal(str, Enum):
    """Conversion goal enum"""
    WEBSITE_TRAFFIC = "website-traffic"
    BRAND_AWARENESS = "brand-awareness"
    ONLINE_LEADS = "online-leads"
    ONLINE_SALES = "online-sales"


class ConversionGoalIcon(str, Enum):
    """Icon names for conversion goals"""
    WEBSITE_TRAFFIC = "CursorClick"
    BRAND_AWARENESS = "Eye"
    ONLINE_LEADS = "Users"
    ONLINE_SALES = "ShoppingCart"


class BiddingStrategyType(str, Enum):
    """Bidding strategy types"""
    MAXIMIZE_CLICKS = "maximize_clicks"
    MAXIMIZE_CONVERSIONS = "maximize_conversions"
    TARGET_CPA = "target_cpa"
    TARGET_ROAS = "target_roas"
    MANUAL_CPC = "manual_cpc"


class CampaignStatus(str, Enum):
    """Campaign status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Campaign(Document):
    """
    Campaign model - stores campaign groups
    Similar structure to competitor's campaign group
    """
    
    # Identification
    business_id: str = Field(..., index=True)  # Links to Business
    user_id: str = Field(..., index=True)  # Links to User (Clerk ID)
    
    # Campaign details
    title: str = Field(..., min_length=1, max_length=200)
    url: str  # Website URL (stored as string, validated as HttpUrl in schema)
    phone: Optional[str] = None
    
    # Conversion goal
    conversion_goal: ConversionGoal = Field(..., alias="conversion_goal")
    conversion_goal_icon: ConversionGoalIcon = Field(default=ConversionGoalIcon.WEBSITE_TRAFFIC)
    conversion: Optional[str] = None  # Specific conversion event if any
    can_have_conversions: bool = Field(default=False)
    
    # Data source
    data_source: str = Field(...)  # "user" or "crawler" - required, no default
    
    # Budget
    budget_currency: str = Field(..., max_length=3)  # Required, no default - must be set from env
    daily_budget: float = Field(..., ge=0)  # Required, no default - must be set from env
    
    # Bidding strategy
    bidding_strategy_type: BiddingStrategyType = Field(default=BiddingStrategyType.MAXIMIZE_CLICKS)
    max_bid: Optional[float] = None
    target_amount: Optional[float] = None  # For CPA/ROAS
    revenue_on_ad_spend: Optional[float] = None
    
    # Supported bidding strategies (for UI)
    supported_bidding_strategy_types: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Platform recommendations
    recommended_platform_id: Optional[int] = None  # Recommended platform ID
    supported_platform_ids: List[int] = Field(default_factory=list)  # All supported platform IDs
    
    # Demographics
    demographics_languages: List[Dict[str, str]] = Field(default_factory=list)  # [{"id": "en", "text": "English", "iso": "en"}]
    demographics_locations_countries: List[Dict[str, Any]] = Field(default_factory=list)
    demographics_location_areas: List[Dict[str, Any]] = Field(default_factory=list)  # Location targeting
    
    # Additional data
    time_ranges: List[Dict[str, Any]] = Field(default_factory=list)
    time_period: Optional[str] = None
    website_industry: Optional[str] = None
    sitelinks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Related campaigns (actual ad campaigns created from this group)
    campaigns: List[str] = Field(default_factory=list)  # Array of campaign IDs
    
    # Metrics (performance data)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Status
    status: CampaignStatus = Field(default=CampaignStatus.DRAFT)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "campaigns"  # MongoDB collection name
        indexes = [
            "business_id",
            "user_id",
            "status",
            [("business_id", 1), ("created_at", -1)],
            [("user_id", 1), ("status", 1)],
        ]
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "business_id": "690ca90c73e6e78b3bb2525f",
                "user_id": "user_2abc123xyz",
                "title": "Test Campaign",
                "url": "https://corider.in",
                "conversion_goal": "website-traffic",
                "conversion_goal_icon": "CursorClick",
                "budget_currency": "INR",
                "daily_budget": 1000.0,
                "bidding_strategy_type": "maximize_clicks",
                "supported_platform_ids": [0, 1, 2],
                "recommended_platform_id": 0,
                "status": "draft",
            }
        }

