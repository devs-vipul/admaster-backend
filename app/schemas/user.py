"""
Pydantic schemas for User API requests/responses
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating user (from Clerk webhook)"""
    clerk_id: str


class UserUpdate(BaseModel):
    """Schema for updating user"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    image_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: str = Field(alias="_id")
    clerk_id: str
    businesses: List[str] = []
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        from_attributes = True


class UserWithBusinesses(UserResponse):
    """User response with populated business details"""
    business_details: List[dict] = []

