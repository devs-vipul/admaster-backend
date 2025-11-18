"""
Platform API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.platform import Platform
from app.services.platform_service import PlatformService


router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get(
    "",
    response_model=List[dict],
    summary="Get all active platforms",
)
async def get_platforms(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all active platforms available for advertising
    
    Returns list of platforms with their details
    """
    platforms = await PlatformService.get_all_platforms()
    
    return [
        {
            "platform_id": p.platform_id,
            "name": p.name,
            "slug": p.slug,
            "type": p.type.value,
            "description": p.description,
            "icon": p.icon,
            "supports_search": p.supports_search,
            "supports_display": p.supports_display,
            "supports_video": p.supports_video,
            "supports_shopping": p.supports_shopping,
            "supports_mobile": p.supports_mobile,
            "best_for_goals": p.best_for_goals,
            "best_for_industries": p.best_for_industries,
            "min_budget": p.min_budget,
            "currency_support": p.currency_support,
            "requires_own_account": getattr(p, "requires_own_account", False),
            "is_active": p.is_active,
            "is_beta": p.is_beta,
        }
        for p in platforms
    ]


@router.get(
    "/{platform_id}",
    response_model=dict,
    summary="Get a specific platform by ID",
)
async def get_platform(
    platform_id: int,
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific platform by its platform_id"""
    platform = await PlatformService.get_platform_by_id(platform_id)
    
    if not platform:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found",
        )
    
    return {
        "platform_id": platform.platform_id,
        "name": platform.name,
        "slug": platform.slug,
        "type": platform.type.value,
        "description": platform.description,
        "icon": platform.icon,
        "supports_search": platform.supports_search,
        "supports_display": platform.supports_display,
        "supports_video": platform.supports_video,
        "supports_shopping": platform.supports_shopping,
        "supports_mobile": platform.supports_mobile,
        "best_for_goals": platform.best_for_goals,
        "best_for_industries": platform.best_for_industries,
        "min_budget": platform.min_budget,
        "currency_support": platform.currency_support,
        "requires_own_account": getattr(platform, "requires_own_account", False),
        "is_active": platform.is_active,
        "is_beta": platform.is_beta,
    }

