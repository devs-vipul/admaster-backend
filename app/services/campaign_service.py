"""
Campaign service - Handles campaign operations
"""
import os
from typing import List, Optional
from datetime import datetime
import asyncio

from app.models.campaign import Campaign, ConversionGoal, ConversionGoalIcon, BiddingStrategyType, CampaignStatus
from app.models.business import Business
from app.schemas.campaign import CampaignCreate, LocationAreaSchema, DemographicsLanguageSchema
from app.services.platform_service import PlatformService
from app.services.platform_intelligence_service import PlatformIntelligenceService
from app.services.brand_service import BrandService
from app.core.config import settings
from app.core.constants import DEFAULT_CURRENCY as CONSTANT_DEFAULT_CURRENCY, DEFAULT_DAILY_BUDGET as CONSTANT_DEFAULT_DAILY_BUDGET
from app.core.exceptions import NotFoundError, ValidationError, InternalServerError


class CampaignService:
    """Service for campaign operations"""

    @staticmethod
    def _map_advertising_goal_to_conversion_goal(advertising_goal: str) -> ConversionGoal:
        """Map frontend advertising goal to conversion goal"""
        mapping = {
            "website-traffic": ConversionGoal.WEBSITE_TRAFFIC,
            "brand-awareness": ConversionGoal.BRAND_AWARENESS,
            "online-leads": ConversionGoal.ONLINE_LEADS,
            "online-sales": ConversionGoal.ONLINE_SALES,
        }
        if advertising_goal not in mapping:
            raise ValidationError(f"Invalid advertising goal: {advertising_goal}")
        return mapping[advertising_goal]

    @staticmethod
    def _get_conversion_goal_icon(conversion_goal: ConversionGoal) -> ConversionGoalIcon:
        """Get icon for conversion goal"""
        mapping = {
            ConversionGoal.WEBSITE_TRAFFIC: ConversionGoalIcon.WEBSITE_TRAFFIC,
            ConversionGoal.BRAND_AWARENESS: ConversionGoalIcon.BRAND_AWARENESS,
            ConversionGoal.ONLINE_LEADS: ConversionGoalIcon.ONLINE_LEADS,
            ConversionGoal.ONLINE_SALES: ConversionGoalIcon.ONLINE_SALES,
        }
        if conversion_goal not in mapping:
            raise ValidationError(f"Invalid conversion goal: {conversion_goal}")
        return mapping[conversion_goal]

    @staticmethod
    async def create_campaign(
        campaign_data: CampaignCreate,
        user_id: str,
    ) -> Campaign:
        """Create a new campaign"""
        
        # Get business to extract industry
        business = await Business.get(campaign_data.business_id)
        if not business:
            raise NotFoundError("Business", campaign_data.business_id)
        
        # Map advertising goal to conversion goal
        if campaign_data.advertising_goal:
            conversion_goal = CampaignService._map_advertising_goal_to_conversion_goal(
                campaign_data.advertising_goal
            )
        elif campaign_data.conversion_goal:
            conversion_goal = campaign_data.conversion_goal
        else:
            raise ValidationError("Either advertising_goal or conversion_goal must be provided")
        
        conversion_goal_icon = CampaignService._get_conversion_goal_icon(conversion_goal)
        
        # Get brand data for intelligence analysis
        print(f"📋 Campaign Creation Flow:")
        print(f"   Goal: {conversion_goal.value}")
        print(f"   Business: {business.name} ({business.industry.value if business.industry else 'No industry'})")
        print(f"   Campaign URL: {campaign_data.url}")
        print(f"   Business Website: {business.website}")
        
        brand = await BrandService.get_brand_by_business_id(campaign_data.business_id)
        if brand:
            print(f"   Brand found: {brand.description[:50]}...")
        else:
            print(f"   ⚠️  No brand data found (crawler may not have run)")
        
        # Get platform recommendations using AI intelligence service
        # No fallbacks - must use AI
        # Model name from GEMINI_MODEL or DEFAULT_MODEL environment variable (no fallback)
        model_name = os.getenv("GEMINI_MODEL")
        if not model_name:
            model_name = os.getenv("DEFAULT_MODEL")
        if not model_name:
            raise InternalServerError(
                "GEMINI_MODEL or DEFAULT_MODEL environment variable is required. Please add it to your .env file.",
                details={"missing_env_vars": ["GEMINI_MODEL", "DEFAULT_MODEL"]}
            )
        
        print(f"\n🚀 Starting Intelligence Service (with {model_name} AI)...")
        recommendation_result = await PlatformIntelligenceService.get_best_platform_with_analysis(
            conversion_goal=conversion_goal,
            business=business,
            brand=brand,
            locations=campaign_data.locations,
        )
        
        if not recommendation_result:
            raise InternalServerError("AI platform recommendation failed - no result returned")
        
        recommended_platform = recommendation_result["platform"]
        print(f"✅ Intelligence Service Success!")
        print(f"   Recommended: {recommended_platform.name} (ID: {recommended_platform.platform_id})")
        
        # Extract platform IDs from recommendations
        all_recommended_platform_ids = [
            rec["platform_id"] for rec in recommendation_result["all_recommendations"]
        ]
        print(f"   Supported platforms: {all_recommended_platform_ids}")
        
        # Fetch platform objects by IDs
        all_recommended_platforms = await PlatformService.get_platforms_by_ids(
            all_recommended_platform_ids
        )
        print(f"   Fetched {len(all_recommended_platforms)} platform objects")
        
        # Build demographics - no defaults, must be provided
        demographics_languages = [
            DemographicsLanguageSchema(
                id=campaign_data.language,
                text=campaign_data.language.upper(),
                iso=campaign_data.language,
            ).model_dump()
        ]
        
        demographics_location_areas = [
            loc.model_dump() if isinstance(loc, LocationAreaSchema) else loc
            for loc in campaign_data.locations
        ]
        
        # Create campaign
        # Convert HttpUrl to string for MongoDB storage
        url_str = str(campaign_data.url)
        
        campaign = Campaign(
            business_id=campaign_data.business_id,
            user_id=user_id,
            title=campaign_data.title,
            url=url_str,
            phone=campaign_data.phone,
            conversion_goal=conversion_goal,
            conversion_goal_icon=conversion_goal_icon,
            can_have_conversions=False,
            data_source="user",
            budget_currency=settings.DEFAULT_CURRENCY or CONSTANT_DEFAULT_CURRENCY,
            daily_budget=settings.DEFAULT_DAILY_BUDGET if settings.DEFAULT_DAILY_BUDGET is not None else CONSTANT_DEFAULT_DAILY_BUDGET,
            bidding_strategy_type=BiddingStrategyType.MAXIMIZE_CLICKS,
            supported_bidding_strategy_types=[
                {
                    "name": "MAXIMIZE_CLICKS",
                    "value": "maximize_clicks",
                    "type": "target_amount",
                }
            ],
            recommended_platform_id=recommended_platform.platform_id if recommended_platform else None,
            supported_platform_ids=[p.platform_id for p in all_recommended_platforms],
            demographics_languages=demographics_languages,
            demographics_location_areas=demographics_location_areas,
            website_industry=business.industry.value if business.industry else None,
            status=CampaignStatus.DRAFT,
        )
        
        print(f"\n📝 Campaign Created:")
        print(f"   Recommended Platform ID: {recommended_platform.platform_id if recommended_platform else None}")
        print(f"   Supported Platform IDs: {[p.platform_id for p in all_recommended_platforms]}")
        print(f"   ==========================================\n")
        
        await campaign.insert()
        return campaign

    @staticmethod
    async def get_campaign_by_id(campaign_id: str, user_id: str) -> Optional[Campaign]:
        """Get campaign by ID (with user check)"""
        from bson import ObjectId
        from bson.errors import InvalidId
        
        # Convert campaign_id to ObjectId
        try:
            obj_id = ObjectId(campaign_id)
        except (InvalidId, ValueError):
            print(f"❌ Invalid campaign ID format: {campaign_id}")
            return None
        
        # Query campaign by ID
        campaign = await Campaign.find_one({"_id": obj_id})
        
        if not campaign:
            print(f"⚠️  Campaign {campaign_id} not found in database")
            return None
        
        # Verify it belongs to the user
        if campaign.user_id != user_id:
            print(f"⚠️  Campaign {campaign_id} found but user_id mismatch: campaign.user_id={campaign.user_id}, requested={user_id}")
            return None
        
        return campaign

    @staticmethod
    async def get_campaigns_by_business(business_id: str, user_id: str) -> List[Campaign]:
        """Get all campaigns for a business"""
        return await Campaign.find(
            Campaign.business_id == business_id,
            Campaign.user_id == user_id,
        ).to_list()

    @staticmethod
    async def get_all_user_campaigns(user_id: str) -> List[Campaign]:
        """Get all campaigns for a user"""
        return await Campaign.find(
            Campaign.user_id == user_id,
        ).sort(-Campaign.created_at).to_list()

