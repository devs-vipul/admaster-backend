"""
Campaign API endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.campaign import ConversionGoal
from app.schemas.campaign import CampaignCreate, CampaignResponse, CampaignListResponse
from app.services.campaign_service import CampaignService
from app.services.business_service import BusinessService
from app.core.config import settings
from app.core.constants import DEFAULT_CURRENCY as CONSTANT_DEFAULT_CURRENCY
from app.core.exceptions import NotFoundError


router = APIRouter(prefix="/campaign/groups", tags=["campaigns"])


@router.get(
    "",
    response_model=CampaignListResponse,
    summary="Get all campaigns for the current user (Shown format)",
)
async def get_all_campaigns(
    current_user: User = Depends(get_current_active_user),
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
):
    """
    Get all campaigns for the current user.
    Returns campaigns in Shown format with campaign_groups, total metrics, and filters.
    """
    campaigns = await CampaignService.get_all_user_campaigns(
        user_id=current_user.clerk_id,
    )
    
    # Convert to response format
    campaign_groups = []
    total_impressions = 0
    total_clicks = 0
    total_cost = 0.0
    total_conversions = 0
    total_daily_budget = 0.0
    
    for campaign in campaigns:
        campaign_id = str(campaign.id) if hasattr(campaign, 'id') else str(campaign._id)
        
        # Calculate metrics from campaign
        campaign_metrics = campaign.metrics if campaign.metrics else []
        for metric in campaign_metrics:
            total_impressions += metric.get("impressions", 0) if metric.get("impressions") else 0
            total_clicks += metric.get("clicks", 0) if metric.get("clicks") else 0
            total_cost += float(metric.get("cost", 0)) if metric.get("cost") else 0.0
            total_conversions += metric.get("conversions", 0) if metric.get("conversions") else 0
        
        total_daily_budget += campaign.daily_budget if campaign.daily_budget else 0.0
        
        # Determine conversion goal ID (matching Shown's format)
        conversion_goal_id = 0
        if campaign.conversion_goal == ConversionGoal.BRAND_AWARENESS:
            conversion_goal_id = 5
        elif campaign.conversion_goal == ConversionGoal.ONLINE_LEADS:
            conversion_goal_id = 1
        elif campaign.conversion_goal == ConversionGoal.ONLINE_SALES:
            conversion_goal_id = 2
        
        campaign_groups.append(CampaignResponse(
            id=campaign_id,
            business_id=campaign.business_id,
            user_id=campaign.user_id,
            title=campaign.title,
            url=campaign.url,
            phone=campaign.phone,
            conversion_goal={
                "id": conversion_goal_id,
                "name": campaign.conversion_goal.value.replace("-", " ").title(),
                "icon": campaign.conversion_goal_icon.value,
            },
            conversion=campaign.conversion,
            can_have_conversions=campaign.can_have_conversions,
            data_source=campaign.data_source,
            budget={
                "currency": campaign.budget_currency,
                "daily_budget": campaign.daily_budget,
            },
            bidding_strategy={
                "type": campaign.bidding_strategy_type.value,
                "max_bid": campaign.max_bid,
                "target_amount": campaign.target_amount,
                "revenue_on_ad_spend": campaign.revenue_on_ad_spend,
            },
            supported_bidding_strategy_types=campaign.supported_bidding_strategy_types,
            recommended_platform=campaign.recommended_platform_id,
            supported_platforms=campaign.supported_platform_ids,
            demographics={
                "languages": campaign.demographics_languages,
                "locations_countries": campaign.demographics_locations_countries,
                "location_areas": campaign.demographics_location_areas,
            },
            time_ranges=campaign.time_ranges,
            time_period=campaign.time_period,
            website_industry=campaign.website_industry if campaign.website_industry else "",
            sitelinks=campaign.sitelinks,
            campaigns=campaign.campaigns,
            metrics=campaign.metrics,
            status=campaign.status,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            is_imported=False,
        ))
    
    # Calculate totals
    total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
    total_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0.0
    total_cpa = (total_cost / total_conversions) if total_conversions > 0 else 0.0
    total_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
    
    # Get currency from first campaign (required - no fallback)
    if not campaigns:
        raise NotFoundError("Campaigns")
    total_currency = campaigns[0].budget_currency
    
    # Date filters (required - no defaults)
    from datetime import datetime, timedelta
    if not date_start:
        date_start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y%m%d")
    if not date_end:
        date_end = datetime.utcnow().strftime("%Y%m%d")
    
    return CampaignListResponse(
        campaign_groups=campaign_groups,
        total={
            "metrics": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "cost": f"{total_cost:.2f}",
                "conversions": total_conversions,
                "click_through_rate": f"{total_ctr:.2f}",
                "cost_per_click": f"{total_cpc:.2f}",
                "cost_per_conversion": f"{total_cpa:.2f}",
                "conversions_rate": f"{total_cvr:.2f}",
                "currency": total_currency,
            },
            "budget": {
                "currency": total_currency,
                "daily_budget": total_daily_budget,
            },
        },
        filters={
            "date_start": date_start,
            "date_end": date_end,
        },
    )


@router.post(
    "/create",
    response_model=CampaignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new campaign group",
)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_active_user),
):
    """
    Create a new campaign group.
    This endpoint creates a campaign with platform recommendations.
    """
    # Verify business belongs to user
    business = await BusinessService.get_business_by_id(
        campaign_data.business_id,
        current_user.clerk_id,
    )
    if not business:
        raise NotFoundError("Business", campaign_data.business_id)
    
    # Create campaign
    campaign = await CampaignService.create_campaign(
        campaign_data=campaign_data,
        user_id=current_user.clerk_id,
    )
    
    # Convert to response format
    # Beanie uses .id property which returns string representation of ObjectId
    campaign_id = str(campaign.id) if hasattr(campaign, 'id') else str(campaign._id)
    print(f"📤 Returning campaign CREATE response with ID: {campaign_id}")
    
    return CampaignResponse(
        id=campaign_id,
        business_id=campaign.business_id,
        user_id=campaign.user_id,
        title=campaign.title,
        url=campaign.url,
        phone=campaign.phone,
        conversion_goal={
            "id": 0 if campaign.conversion_goal.value == "website-traffic" else 1,
            "name": campaign.conversion_goal.value.replace("-", " ").title(),
            "icon": campaign.conversion_goal_icon.value,
        },
        conversion=campaign.conversion,
        can_have_conversions=campaign.can_have_conversions,
        data_source=campaign.data_source,
        budget={
            "currency": campaign.budget_currency,
            "daily_budget": campaign.daily_budget,
        },
        bidding_strategy={
            "type": campaign.bidding_strategy_type.value,
            "max_bid": campaign.max_bid,
            "target_amount": campaign.target_amount,
            "revenue_on_ad_spend": campaign.revenue_on_ad_spend,
        },
        supported_bidding_strategy_types=campaign.supported_bidding_strategy_types,
        recommended_platform=campaign.recommended_platform_id if campaign.recommended_platform_id else None,
        supported_platforms=campaign.supported_platform_ids,
        demographics={
            "languages": campaign.demographics_languages,
            "locations_countries": campaign.demographics_locations_countries,
            "location_areas": campaign.demographics_location_areas,
        },
        time_ranges=campaign.time_ranges,
        time_period=campaign.time_period,
        website_industry=campaign.website_industry,
        sitelinks=campaign.sitelinks,
        campaigns=campaign.campaigns,
        metrics=campaign.metrics,
        status=campaign.status,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
    )


@router.get(
    "/{campaign_id}",
    response_model=CampaignListResponse,
    summary="Get a campaign by ID (Shown format)",
)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_active_user),
    date_start: Optional[str] = None,
    date_end: Optional[str] = None,
):
    """
    Get a specific campaign by its ID.
    Returns campaign in Shown format with campaign_groups, total metrics, and filters.
    """
    campaign = await CampaignService.get_campaign_by_id(
        campaign_id=campaign_id,
        user_id=current_user.clerk_id,
    )
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found",
        )
    
    # Convert to response format
    campaign_id_str = str(campaign.id) if hasattr(campaign, 'id') else str(campaign._id)
    print(f"📤 Returning campaign GET response with ID: {campaign_id_str}")
    
    # Calculate metrics from campaign (if available)
    total_impressions = 0
    total_clicks = 0
    total_cost = 0.0
    total_conversions = 0
    
    campaign_metrics = campaign.metrics or []
    for metric in campaign_metrics:
        total_impressions += metric.get("impressions", 0)
        total_clicks += metric.get("clicks", 0)
        total_cost += float(metric.get("cost", 0) or 0)
        total_conversions += metric.get("conversions", 0)
    
    # Determine conversion goal ID (matching Shown's format)
    conversion_goal_id = 0
    if campaign.conversion_goal == ConversionGoal.BRAND_AWARENESS:
        conversion_goal_id = 5
    elif campaign.conversion_goal == ConversionGoal.ONLINE_LEADS:
        conversion_goal_id = 1
    elif campaign.conversion_goal == ConversionGoal.ONLINE_SALES:
        conversion_goal_id = 2
    
    campaign_response = CampaignResponse(
        id=campaign_id_str,
        business_id=campaign.business_id,
        user_id=campaign.user_id,
        title=campaign.title,
        url=campaign.url,
        phone=campaign.phone,
        conversion_goal={
            "id": conversion_goal_id,
            "name": campaign.conversion_goal.value.replace("-", " ").title(),
            "icon": campaign.conversion_goal_icon.value,
        },
        conversion=campaign.conversion,
        can_have_conversions=campaign.can_have_conversions,
        data_source=campaign.data_source,
        budget={
            "currency": campaign.budget_currency,
            "daily_budget": campaign.daily_budget,
        },
        bidding_strategy={
            "type": campaign.bidding_strategy_type.value,
            "max_bid": campaign.max_bid,
            "target_amount": campaign.target_amount,
            "revenue_on_ad_spend": campaign.revenue_on_ad_spend,
        },
        supported_bidding_strategy_types=campaign.supported_bidding_strategy_types,
        recommended_platform=campaign.recommended_platform_id if campaign.recommended_platform_id else None,
        supported_platforms=campaign.supported_platform_ids,
        demographics={
            "languages": campaign.demographics_languages,
            "locations_countries": campaign.demographics_locations_countries,
            "location_areas": campaign.demographics_location_areas,
        },
        time_ranges=campaign.time_ranges,
        time_period=campaign.time_period,
        website_industry=campaign.website_industry or "",
        sitelinks=campaign.sitelinks,
        campaigns=campaign.campaigns,
        metrics=campaign.metrics,
        status=campaign.status,
        created_at=campaign.created_at,
        updated_at=campaign.updated_at,
        is_imported=False,
    )
    
    # Calculate totals
    total_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0.0
    total_cpc = (total_cost / total_clicks) if total_clicks > 0 else 0.0
    total_cpa = (total_cost / total_conversions) if total_conversions > 0 else 0.0
    total_cvr = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0.0
    
    # Default date filters (last 7 days if not provided)
    from datetime import datetime, timedelta
    if not date_start:
        date_start = (datetime.utcnow() - timedelta(days=7)).strftime("%Y%m%d")
    if not date_end:
        date_end = datetime.utcnow().strftime("%Y%m%d")
    
    return CampaignListResponse(
        campaign_groups=[campaign_response],
        total={
            "metrics": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "cost": f"{total_cost:.2f}",
                "conversions": total_conversions,
                "click_through_rate": f"{total_ctr:.2f}",
                "cost_per_click": f"{total_cpc:.2f}",
                "cost_per_conversion": f"{total_cpa:.2f}",
                "conversions_rate": f"{total_cvr:.2f}",
                "currency": campaign.budget_currency,
            },
            "budget": {
                "currency": campaign.budget_currency,
                "daily_budget": campaign.daily_budget if campaign.daily_budget else 0.0,
            },
        },
        filters={
            "date_start": date_start,
            "date_end": date_end,
        },
    )

