"""
Pydantic schemas for Business API requests/responses
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

from app.models.business import BusinessStatus, BusinessSize, Industry


class BusinessBase(BaseModel):
    """Base business schema"""
    name: str = Field(..., min_length=1, max_length=200)
    website: HttpUrl
    industry: Industry
    size: BusinessSize = BusinessSize.SMALL


class BusinessCreate(BusinessBase):
    """Schema for creating a new business"""
    pass


class BusinessUpdate(BaseModel):
    """Schema for updating a business"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    website: Optional[HttpUrl] = None
    industry: Optional[Industry] = None
    size: Optional[BusinessSize] = None
    status: Optional[BusinessStatus] = None


class BusinessResponse(BusinessBase):
    """Schema for business response"""
    id: str = Field(alias="_id")
    user_id: str
    status: BusinessStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
        from_attributes = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "user_id": "user_2abc123xyz",
                "name": "Corider",
                "website": "https://corider.in",
                "industry": "Technology",
                "size": "Small (1 - 10 employees)",
                "status": "active",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            }
        }


class BusinessListResponse(BaseModel):
    """Schema for business list response"""
    businesses: list[BusinessResponse]
    total: int

