"""
Business API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.business import Business, BusinessStatus
from app.schemas.business import (
    BusinessCreate,
    BusinessUpdate,
    BusinessResponse,
    BusinessListResponse,
)
from app.services.business_service import BusinessService


router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new business",
)
async def create_business(
    business_data: BusinessCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new business for the authenticated user
    
    This is called from the /business-creation/settings page
    """
    business = await BusinessService.create_business(
        user_id=current_user.clerk_id,
        business_data=business_data,
    )
    
    return BusinessResponse(**business.model_dump())


@router.get(
    "",
    response_model=BusinessListResponse,
    summary="Get all user's businesses",
)
async def get_businesses(
    status: Optional[BusinessStatus] = None,
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all businesses belonging to the authenticated user
    
    Optionally filter by status (active, paused, archived)
    """
    businesses = await BusinessService.get_user_businesses(
        user_id=current_user.clerk_id,
        status=status,
    )
    
    return BusinessListResponse(
        businesses=[BusinessResponse(**b.model_dump()) for b in businesses],
        total=len(businesses),
    )


@router.get(
    "/{business_id}",
    response_model=BusinessResponse,
    summary="Get a specific business",
)
async def get_business(
    business_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific business by ID"""
    business = await BusinessService.get_business_by_id(
        business_id=business_id,
        user_id=current_user.clerk_id,
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    
    return BusinessResponse(**business.model_dump())


@router.put(
    "/{business_id}",
    response_model=BusinessResponse,
    summary="Update a business",
)
async def update_business(
    business_id: str,
    business_data: BusinessUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update business information"""
    business = await BusinessService.update_business(
        business_id=business_id,
        user_id=current_user.clerk_id,
        business_data=business_data,
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    
    return BusinessResponse(**business.model_dump())


@router.delete(
    "/{business_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a business",
)
async def delete_business(
    business_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Delete a business"""
    success = await BusinessService.delete_business(
        business_id=business_id,
        user_id=current_user.clerk_id,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )


@router.get(
    "/check/has-business",
    summary="Check if user has any business",
)
async def check_has_business(
    current_user: User = Depends(get_current_active_user),
):
    """
    Check if user has any business
    
    Used to determine if user should be redirected to business creation page
    """
    has_business = await BusinessService.has_any_business(current_user.clerk_id)
    
    return {
        "has_business": has_business,
        "business_count": len(current_user.businesses),
    }

