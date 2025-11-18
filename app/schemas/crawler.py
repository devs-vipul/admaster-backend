"""Schemas for AdMaster-Crawler results"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class CrawlResponse(BaseModel):
    description: str = Field("", description="Detected brand description")
    logo_url: Optional[str] = Field(
        default=None, description="Best guess for brand logo URL"
    )
    
    @field_validator("logo_url")
    @classmethod
    def validate_logo_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate that logo_url is a valid URL if provided"""
        if v is None or v == "":
            return None
        # Basic URL validation - ensure it starts with http:// or https://
        if not v.startswith(("http://", "https://")):
            raise ValueError("Logo URL must start with http:// or https://")
        return v
    brand_colors: List[str] = Field(default_factory=list, description="Hex colors")
    tone_of_voice: List[str] = Field(
        default_factory=list, description="Suggested tone of voice options"
    )
    language: str = Field("en", description="BCP-47 primary language tag")


