"""Schemas for AdMaster-Crawler results"""
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field


class CrawlResponse(BaseModel):
    description: str = Field("", description="Detected brand description")
    logo_url: Optional[HttpUrl] = Field(
        default=None, description="Best guess for brand logo URL"
    )
    brand_colors: List[str] = Field(default_factory=list, description="Hex colors")
    tone_of_voice: List[str] = Field(
        default_factory=list, description="Suggested tone of voice options"
    )
    language: str = Field("en", description="BCP-47 primary language tag")


