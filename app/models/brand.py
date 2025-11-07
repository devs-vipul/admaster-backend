"""
Brand model - stores brand information extracted by AdMaster-Crawler
Each brand belongs to a business
"""
from datetime import datetime
from typing import List, Optional
from beanie import Document
from pydantic import Field, HttpUrl


class Brand(Document):
    """
    Brand model - stores brand information for a business
    Extracted by AdMaster-Crawler and can be edited by user
    """
    
    # Link to business
    business_id: str = Field(..., index=True)  # Business ID
    
    # Brand information (from crawler)
    description: str = Field(default="", max_length=500)
    logo_url: Optional[HttpUrl] = None
    brand_colors: List[str] = Field(default_factory=list)  # Hex color codes
    tone_of_voice: List[str] = Field(default_factory=list)  # e.g., ["Professional", "Optimistic"]
    language: str = Field(default="en", max_length=10)  # BCP-47 language code
    
    # Status
    is_complete: bool = Field(default=False)  # Whether user has reviewed/confirmed
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "brands"  # MongoDB collection name
        indexes = [
            "business_id",
            [("business_id", 1), ("created_at", -1)],  # Compound index
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "business_id": "690ca90c73e6e78b3bb2525f",
                "description": "CoRider is a social ride-sharing platform...",
                "logo_url": "https://corider.in/logo.png",
                "brand_colors": ["#14803B", "#BFBF9C", "#848481"],
                "tone_of_voice": ["Optimistic", "Professional"],
                "language": "en",
                "is_complete": False,
            }
        }
    
    async def update_brand_info(
        self,
        description: Optional[str] = None,
        logo_url: Optional[HttpUrl] = None,
        brand_colors: Optional[List[str]] = None,
        tone_of_voice: Optional[List[str]] = None,
        language: Optional[str] = None,
        is_complete: Optional[bool] = None,
    ):
        """Update brand information"""
        if description is not None:
            self.description = description
        if logo_url is not None:
            self.logo_url = logo_url
        if brand_colors is not None:
            self.brand_colors = brand_colors
        if tone_of_voice is not None:
            self.tone_of_voice = tone_of_voice
        if language is not None:
            self.language = language
        if is_complete is not None:
            self.is_complete = is_complete
        
        self.updated_at = datetime.utcnow()
        await self.save()

