"""
Platform service - Handles platform operations and recommendations
"""
from typing import List, Optional
from app.models.platform import Platform
from app.models.campaign import ConversionGoal


class PlatformService:
    """Service for platform operations"""

    @staticmethod
    async def get_all_platforms() -> List[Platform]:
        """Get all active platforms"""
        return await Platform.find(Platform.is_active == True).to_list()

    @staticmethod
    async def get_platform_by_id(platform_id: int) -> Optional[Platform]:
        """Get platform by ID"""
        return await Platform.find_one(Platform.platform_id == platform_id)

    @staticmethod
    async def get_platforms_by_ids(platform_ids: List[int]) -> List[Platform]:
        """Get platforms by list of IDs"""
        # Beanie query: use $in operator for MongoDB
        return await Platform.find({"platform_id": {"$in": platform_ids}}).to_list()

    @staticmethod
    async def recommend_platforms(
        conversion_goal: ConversionGoal,
        industry: Optional[str] = None,
        budget: Optional[float] = None,
        currency: str = "INR",
    ) -> List[Platform]:
        """
        Recommend platforms based on campaign parameters
        
        Simple recommendation logic:
        - Website Traffic: Google Ads (search), Facebook Ads (social)
        - Brand Awareness: Facebook, Instagram, LinkedIn, YouTube
        - Online Leads: Google Ads, LinkedIn, Facebook
        - Online Sales: Google Shopping, Facebook, Instagram
        """
        all_platforms = await PlatformService.get_all_platforms()
        
        # Filter by goal
        recommended = []
        for platform in all_platforms:
            if conversion_goal.value in platform.best_for_goals:
                recommended.append(platform)
        
        # If no specific matches, use default logic
        if not recommended:
            if conversion_goal == ConversionGoal.WEBSITE_TRAFFIC:
                # Search platforms for traffic
                recommended = [p for p in all_platforms if p.supports_search]
            elif conversion_goal == ConversionGoal.BRAND_AWARENESS:
                # Social platforms for awareness
                recommended = [p for p in all_platforms if p.type.value == "social"]
            elif conversion_goal == ConversionGoal.ONLINE_LEADS:
                # Search + Social for leads
                recommended = [p for p in all_platforms if p.supports_search or p.type.value == "social"]
            elif conversion_goal == ConversionGoal.ONLINE_SALES:
                # Shopping + Social for sales
                recommended = [p for p in all_platforms if p.supports_shopping or p.type.value == "social"]
        
        # Filter by industry if provided
        if industry:
            industry_filtered = [p for p in recommended if industry in p.best_for_industries]
            if industry_filtered:
                recommended = industry_filtered
        
        # Filter by budget if provided
        if budget:
            recommended = [p for p in recommended if not p.min_budget or p.min_budget <= budget]
        
        # Filter by currency support
        recommended = [p for p in recommended if currency in p.currency_support or not p.currency_support]
        
        return recommended[:10]  # Return top 10

    @staticmethod
    async def get_recommended_platform(
        conversion_goal: ConversionGoal,
        industry: Optional[str] = None,
        budget: Optional[float] = None,
        currency: str = "INR",
    ) -> Optional[Platform]:
        """Get the single best recommended platform"""
        platforms = await PlatformService.recommend_platforms(
            conversion_goal, industry, budget, currency
        )
        return platforms[0] if platforms else None

