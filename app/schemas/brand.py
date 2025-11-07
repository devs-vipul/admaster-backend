"""
Pydantic schemas for Brand API requests/responses
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class BrandBase(BaseModel):
    """Base brand schema"""
    description: str = Field(default="", max_length=500)
    logo_url: Optional[HttpUrl] = None
    brand_colors: List[str] = Field(default_factory=list)
    tone_of_voice: List[str] = Field(default_factory=list)
    language: str = Field(default="en", max_length=10)
    is_complete: bool = Field(default=False)


class BrandCreate(BrandBase):
    """Schema for creating a new brand"""
    business_id: str


class BrandUpdate(BaseModel):
    """Schema for updating brand information"""
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[HttpUrl] = None
    brand_colors: Optional[List[str]] = None
    tone_of_voice: Optional[List[str]] = None
    language: Optional[str] = Field(None, max_length=10)
    is_complete: Optional[bool] = None


class BrandResponse(BrandBase):
    """Schema for brand response"""
    id: str = Field(alias="_id")
    business_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True

