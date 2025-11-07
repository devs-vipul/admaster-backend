"""
Brand API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.business import Business
from app.schemas.brand import BrandResponse, BrandUpdate
from app.services.brand_service import BrandService
from app.services.business_service import BusinessService


router = APIRouter(prefix="/brands", tags=["brands"])


@router.get(
    "/business/{business_id}",
    response_model=BrandResponse,
    summary="Get brand information for a business",
)
async def get_brand_by_business(
    business_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get brand information for a specific business"""
    # Verify business belongs to user
    business = await BusinessService.get_business_by_id(
        business_id=business_id,
        user_id=current_user.clerk_id,
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    
    # Get or create brand
    brand = await BrandService.get_or_create_brand(business_id)
    
    return BrandResponse(**brand.model_dump())


@router.put(
    "/business/{business_id}",
    response_model=BrandResponse,
    summary="Update brand information for a business",
)
async def update_brand(
    business_id: str,
    brand_data: BrandUpdate,
    current_user: User = Depends(get_current_active_user),
):
    """Update brand information for a business"""
    # Verify business belongs to user
    business = await BusinessService.get_business_by_id(
        business_id=business_id,
        user_id=current_user.clerk_id,
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    
    # Create or update brand
    brand = await BrandService.create_or_update_brand(
        business_id=business_id,
        brand_data=brand_data,
    )
    
    return BrandResponse(**brand.model_dump())


@router.post(
    "/business/{business_id}/complete",
    response_model=BrandResponse,
    summary="Mark brand as complete",
)
async def mark_brand_complete(
    business_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Mark brand as complete (user has reviewed)"""
    # Verify business belongs to user
    business = await BusinessService.get_business_by_id(
        business_id=business_id,
        user_id=current_user.clerk_id,
    )
    
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business not found",
        )
    
    brand = await BrandService.mark_brand_complete(business_id)
    
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )
    
    return BrandResponse(**brand.model_dump())

