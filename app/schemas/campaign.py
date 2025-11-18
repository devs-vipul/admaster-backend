"""
Campaign schemas for API requests/responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from app.models.campaign import ConversionGoal, ConversionGoalIcon, BiddingStrategyType, CampaignStatus


class ConversionGoalSchema(BaseModel):
    """Conversion goal schema"""
    id: int
    name: str
    icon: str


class BudgetSchema(BaseModel):
    """Budget schema"""
    currency: str  # Required, no default
    daily_budget: float = Field(..., ge=0)  # Required, no default


class BiddingStrategySchema(BaseModel):
    """Bidding strategy schema"""
    type: str
    max_bid: Optional[float] = None
    target_amount: Optional[float] = None
    revenue_on_ad_spend: Optional[float] = None


class DemographicsLanguageSchema(BaseModel):
    id: str
    text: str
    iso: str


class LocationAreaSchema(BaseModel):
    google_place_id: Optional[str] = None
    name: str
    radius: Optional[int] = None
    units: Optional[str] = None
    lat: float
    lng: float
    country_code: Optional[str] = None


class DemographicsSchema(BaseModel):
    languages: List[DemographicsLanguageSchema] = Field(default_factory=list)
    locations_countries: List[Dict[str, Any]] = Field(default_factory=list)
    location_areas: List[LocationAreaSchema] = Field(default_factory=list)


class CampaignCreate(BaseModel):
    business_id: str
    title: str = Field(..., min_length=1, max_length=200)
    url: HttpUrl
    phone: Optional[str] = None
    conversion_goal: Optional[ConversionGoal] = None  # Optional, can be derived from advertising_goal
    website_url: Optional[str] = None  # From form (same as url, kept for compatibility)
    language: str = Field(..., min_length=1)  # Required from form - no default
    locations: List[LocationAreaSchema] = Field(..., min_length=1)  # Required from form - at least one location, no default
    advertising_goal: Optional[str] = None  # From form (maps to conversion_goal)


class CampaignResponse(BaseModel):
    """Schema for campaign response"""
    id: str  # Use id directly, not _id alias
    business_id: str
    user_id: str
    title: str
    url: HttpUrl
    phone: Optional[str] = None
    conversion_goal: Dict[str, Any]  # {"id": 0, "name": "Website Traffic", "icon": "CursorClick"}
    conversion: Optional[str] = None
    can_have_conversions: bool
    data_source: str
    budget: BudgetSchema
    bidding_strategy: BiddingStrategySchema
    supported_bidding_strategy_types: List[Dict[str, Any]]
    recommended_platform: Optional[int] = None
    supported_platforms: List[int] = Field(default_factory=list)
    demographics: DemographicsSchema
    time_ranges: List[Dict[str, Any]] = Field(default_factory=list)
    time_period: Optional[str] = None
    website_industry: Optional[str] = None
    sitelinks: List[Dict[str, Any]] = Field(default_factory=list)
    campaigns: List[str] = Field(default_factory=list)
    metrics: List[Dict[str, Any]] = Field(default_factory=list)
    status: CampaignStatus
    created_at: datetime
    updated_at: datetime
    is_imported: bool = Field(default=False)

    class Config:
        populate_by_name = True
        from_attributes = True


class CampaignListResponse(BaseModel):
    """Schema for campaign list response (Shown format)"""
    campaign_groups: List[CampaignResponse]
    total: Dict[str, Any]  # {"metrics": {...}, "budget": {...}}
    filters: Dict[str, Any]  # {"date_start": "...", "date_end": "..."}
