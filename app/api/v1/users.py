"""
User API endpoints
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current authenticated user's information
    
    This returns the user's MongoDB data including their businesses
    """
    return UserResponse(**current_user.model_dump())


@router.get(
    "/me/profile",
    summary="Get user profile with business details",
)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get complete user profile including business count and other stats
    """
    from app.services.business_service import BusinessService
    
    businesses = await BusinessService.get_user_businesses(current_user.clerk_id)
    
    return {
        "user": UserResponse(**current_user.model_dump()),
        "business_count": len(businesses),
        "active_businesses": len([b for b in businesses if b.status == "active"]),
    }

