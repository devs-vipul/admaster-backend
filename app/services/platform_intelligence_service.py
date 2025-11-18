"""
Platform Intelligence Service - AI-powered platform recommendation using Google Gemini
Uses comprehensive website content crawling (20 pages) and AI semantic analysis
Completely AI-driven - no rule-based scoring, no fallbacks
Model name from GEMINI_MODEL or DEFAULT_MODEL environment variable
"""
import os
from typing import List, Optional, Dict, Any
from app.models.platform import Platform
from app.models.campaign import ConversionGoal
from app.models.brand import Brand
from app.models.business import Business
from app.services.platform_service import PlatformService
from app.services.admaster_content_crawler_service import AdMasterContentCrawlerService

# Import Gemini AI analyzer (required)
# Check if google-genai package can be imported (lazy check - API key checked when used)
try:
    from google import genai
    from app.services.ai_platform_analyzer import AIPlatformAnalyzer
    GEMINI_AVAILABLE = True
except (ImportError, Exception) as e:
    GEMINI_AVAILABLE = False
    print(f"❌ ERROR: Gemini AI package not available - {str(e)}")


class PlatformIntelligenceService:
    """
    AI-powered platform recommendation using Google Gemini
    Uses comprehensive website content crawling and semantic AI analysis
    All recommendations are AI-generated - no rule-based scoring, no fallbacks
    Model name from GEMINI_MODEL or DEFAULT_MODEL environment variable
    """

    @staticmethod
    async def get_best_platform_with_analysis(
        conversion_goal: ConversionGoal,
        business: Business,
        brand: Optional[Brand] = None,
        locations: Optional[List[Any]] = None,  # Can be List[Dict] or List[Pydantic models]
    ) -> Optional[Dict[str, Any]]:
        """
        Get the best platform using AI-powered analysis (Google Gemini)
        Model name from GEMINI_MODEL or DEFAULT_MODEL environment variable
        
        This method:
        1. Crawls website content (20 pages)
        2. Uses Gemini AI to analyze:
           - Website content (semantic understanding)
           - Brand description, tone, colors
           - Campaign goal and target locations
           - Industry and business type
        3. Returns AI-recommended platforms with scores, reasoning, and analysis
        
        Returns:
            {
                "platform": Platform,
                "score": float,
                "reasons": List[str],
                "ai_reasoning": str,
                "ai_analysis": Dict,
                "all_recommendations": List[Dict]
            }
        """
        if not GEMINI_AVAILABLE:
            raise ValueError("Gemini AI package is not installed. Please install google-genai package.")
        
        # Check if API key is available (lazy check)
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required. Please add it to your .env file.")
        
        # 1. Get brand data if available
        if not brand:
            from app.services.brand_service import BrandService
            business_id = str(business.id) if hasattr(business, 'id') else str(business._id)
            brand = await BrandService.get_brand_by_business_id(business_id)

        # 2. Crawl website content (optional - only if needed)
        # Content crawler is NOT run automatically - it should be triggered separately if needed
        website_content = None

        # 3. Use Gemini AI for intelligent analysis (no fallbacks, no defaults)
        model_name = os.getenv("GEMINI_MODEL") or os.getenv("DEFAULT_MODEL")
        if not model_name:
            raise ValueError("GEMINI_MODEL or DEFAULT_MODEL environment variable is required. Please add it to your .env file.")
        
        print(f"🤖 Using {model_name} for AI-powered platform recommendation...")
        ai_analyzer = AIPlatformAnalyzer()
        ai_result = await ai_analyzer.analyze_and_recommend(
            conversion_goal=conversion_goal,
            business=business,
            brand=brand,
            website_content=website_content,
            locations=locations,
        )
        
        print(f"✅ Gemini AI recommended: {ai_result['recommended_platform_name']}")
        print(f"📊 AI Reasoning: {ai_result.get('ai_reasoning', 'N/A')[:200]}...")
        
        # Convert AI result to platform objects
        from app.services.platform_service import PlatformService
        
        recommended_platform = await PlatformService.get_platform_by_id(
            ai_result["recommended_platform_id"]
        )
        
        if not recommended_platform:
            raise ValueError(f"AI recommended platform ID {ai_result['recommended_platform_id']} not found in database")
        
        # Get all recommended platforms
        all_platform_ids = [rec["platform_id"] for rec in ai_result["all_recommendations"]]
        all_platforms = await PlatformService.get_platforms_by_ids(all_platform_ids)
        
        # Find the recommended platform's score and details
        recommended_rec = next(
            (r for r in ai_result["all_recommendations"] 
             if r["platform_id"] == recommended_platform.platform_id),
            None
        )
        
        if not recommended_rec:
            raise ValueError("Recommended platform not found in AI recommendations")
        
        return {
            "platform": recommended_platform,
            "score": recommended_rec["score"],
            "reasons": recommended_rec.get("reasons", []),
            "ai_reasoning": ai_result.get("ai_reasoning", ""),
            "ai_analysis": ai_result.get("ai_analysis", {}),
            "all_recommendations": [
                {
                    "platform_id": rec["platform_id"],
                    "name": rec["name"],
                    "score": rec["score"],
                    "reasons": rec.get("reasons", []),
                    "ai_reasoning": rec.get("ai_reasoning", ""),
                }
                for rec in ai_result["all_recommendations"]
            ],
        }
