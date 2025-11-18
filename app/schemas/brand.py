"""
Pydantic schemas for Brand API requests/responses
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class BrandBase(BaseModel):
    """Base brand schema"""
    description: str = Field(default="", max_length=500)
    logo_url: Optional[str] = Field(default=None, description="Brand logo URL")
    brand_colors: List[str] = Field(default_factory=list)
    tone_of_voice: List[str] = Field(default_factory=list)
    language: str = Field(default="en", max_length=10)
    is_complete: bool = Field(default=False)
    
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


class BrandCreate(BrandBase):
    """Schema for creating a new brand"""
    business_id: str


class BrandUpdate(BaseModel):
    """Schema for updating brand information"""
    description: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    brand_colors: Optional[List[str]] = None
    tone_of_voice: Optional[List[str]] = None
    language: Optional[str] = Field(None, max_length=10)
    is_complete: Optional[bool] = None
    
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


class BrandResponse(BrandBase):
    """Schema for brand response"""
    id: str = Field(alias="_id")
    business_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True

