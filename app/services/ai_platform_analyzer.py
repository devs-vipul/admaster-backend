"""
AI Platform Analyzer - Uses Google Gemini 2.5 Flash to intelligently analyze content and recommend platforms
No fallbacks - requires GOOGLE_API_KEY or GEMINI_API_KEY environment variable
"""
import os
import json
from typing import Dict, Any, List, Optional
from google import genai
from app.models.campaign import ConversionGoal
from app.models.business import Business
from app.models.brand import Brand


class AIPlatformAnalyzer:
    """
    Uses Google Gemini 2.5 Flash AI to analyze website content, brand data, and campaign goals
    to provide intelligent platform recommendations with reasoning.
    
    Requires GOOGLE_API_KEY or GEMINI_API_KEY environment variable - no fallbacks.
    Uses google-genai package (new API) with async support.
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google Gemini API key (defaults to GOOGLE_API_KEY or GEMINI_API_KEY env var)
            model_name: Model name (defaults to GEMINI_MODEL env var, or DEFAULT_MODEL as fallback)
        """
        # Get API key from env - GOOGLE_API_KEY takes precedence over GEMINI_API_KEY
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY or GEMINI_API_KEY environment variable is required. Please add it to your .env file.")
        
        # Get model name from env - use DEFAULT_MODEL if GEMINI_MODEL not set
        if model_name:
            self.model_name = model_name
        else:
            self.model_name = os.getenv("GEMINI_MODEL") or os.getenv("DEFAULT_MODEL")
            if not self.model_name:
                raise ValueError("GEMINI_MODEL or DEFAULT_MODEL environment variable is required. Please add it to your .env file.")
        
        # Initialize Gemini client (new API)
        self.client = genai.Client(api_key=self.api_key)
        # Get async client for async operations
        self.async_client = self.client.aio
    
    async def analyze_and_recommend(
        self,
        conversion_goal: ConversionGoal,
        business: Business,
        brand: Optional[Brand] = None,
        website_content: Optional[Dict[str, Any]] = None,
        locations: Optional[List[Any]] = None,  # Can be List[Dict] or List[Pydantic models]
    ) -> Dict[str, Any]:
        """
        Use Gemini AI to analyze all data and recommend platforms with reasoning
        
        Returns:
            {
                "recommended_platform_id": int,
                "recommended_platform_name": str,
                "all_recommendations": [
                    {
                        "platform_id": int,
                        "name": str,
                        "score": float (0.0-1.0),
                        "reasons": List[str],
                        "ai_reasoning": str
                    }
                ],
                "ai_analysis": {
                    "content_summary": str,
                    "target_audience": str,
                    "content_type": str,
                    "brand_personality": str
                },
                "ai_reasoning": str
            }
        """
        
        # Build comprehensive context for Gemini
        context = self._build_context(
            conversion_goal=conversion_goal,
            business=business,
            brand=brand,
            website_content=website_content,
            locations=locations,
        )
        
        # Get available platforms from database
        platforms_info = await self._get_platforms_info()
        
        # Create refined prompt for Gemini
        prompt = self._create_analysis_prompt(context, platforms_info, conversion_goal)
        
        try:
            # Call Gemini API (async)
            print(f"🤖 Calling Gemini AI for platform recommendation...")
            response = await self.async_client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            # Parse Gemini response
            # New API returns response.text directly
            response_text = response.text if hasattr(response, 'text') else str(response)
            result = self._parse_gemini_response(response_text)
            
            print(f"✅ Gemini AI analysis complete!")
            return result
            
        except Exception as e:
            print(f"❌ Gemini API error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _build_context(
        self,
        conversion_goal: ConversionGoal,
        business: Business,
        brand: Optional[Brand],
        website_content: Optional[Dict[str, Any]],
        locations: Optional[List[Any]],  # Can be List[Dict] or List[Pydantic models]
    ) -> Dict[str, Any]:
        """Build comprehensive context dictionary for AI analysis"""
        
        # Convert locations to dicts if they're Pydantic models
        target_locations = []
        if locations:
            for loc in locations:
                if isinstance(loc, dict):
                    target_locations.append(loc.get("name", ""))
                else:
                    # Pydantic model - access attribute directly
                    target_locations.append(getattr(loc, "name", ""))
        
        context = {
            "campaign_goal": conversion_goal.value,
            "business_name": business.name,
            "business_industry": business.industry.value if business.industry else "Unknown",
            "website_url": str(business.website),
            "target_locations": target_locations,
        }
        
        # Add brand information
        if brand:
            context.update({
                "brand_description": brand.description,
                "brand_colors": brand.brand_colors,
                "brand_tone": brand.tone_of_voice,
                "brand_language": brand.language,
            })
        else:
            context.update({
                "brand_description": "Not available",
                "brand_colors": [],
                "brand_tone": [],
                "brand_language": "en",
            })
        
        # Add comprehensive website content analysis
        if website_content:
            aggregated_text = website_content.get("aggregated_text", "")
            pages_crawled = website_content.get("pages_crawled", 0)
            total_words = website_content.get("total_words", 0)
            pages = website_content.get("pages", [])
            
            # Extract detailed content insights
            total_images = sum(len(page.get("images", [])) for page in pages)
            avg_images_per_page = total_images / len(pages) if pages else 0
            
            # Extract page titles and descriptions
            page_titles = [page.get("title", "") for page in pages[:20]]
            page_descriptions = [page.get("description", "") for page in pages[:20]]
            
            # Get full content from all pages (up to 10000 chars)
            full_content = aggregated_text[:10000] if len(aggregated_text) > 10000 else aggregated_text
            
            context.update({
                "website_content_full": full_content,  # Full content for semantic analysis
                "content_stats": {
                    "pages_crawled": pages_crawled,
                    "total_words": total_words,
                    "total_images": total_images,
                    "avg_images_per_page": round(avg_images_per_page, 2),
                },
                "page_titles": page_titles,
                "page_descriptions": page_descriptions,
                "content_type_indicators": {
                    "has_ecommerce_keywords": any(
                        kw in aggregated_text.lower() 
                        for kw in ["buy", "shop", "cart", "checkout", "product", "price", "add to cart", "purchase"]
                    ),
                    "is_visual_heavy": avg_images_per_page > 5,
                    "is_text_heavy": total_words > 10000,
                    "has_video_content": any("video" in page.get("content", "").lower() for page in pages),
                    "has_blog_content": any("blog" in page.get("url", "").lower() or "article" in page.get("url", "").lower() for page in pages),
                },
            })
        else:
            context.update({
                "website_content_full": "Content not crawled",
                "content_stats": {
                    "pages_crawled": 0,
                    "total_words": 0,
                    "total_images": 0,
                    "avg_images_per_page": 0,
                },
                "page_titles": [],
                "page_descriptions": [],
                "content_type_indicators": {},
            })
        
        return context
    
    async def _get_platforms_info(self) -> List[Dict[str, Any]]:
        """Get information about available ad platforms from database"""
        from app.services.platform_service import PlatformService
        
        platforms = await PlatformService.get_all_platforms()
        
        # Convert to format for AI prompt
        platforms_info = []
        for platform in platforms:
            platforms_info.append({
                "id": platform.platform_id,
                "name": platform.name,
                "type": platform.type.value,
                "slug": platform.slug,
                "description": platform.description,
                "best_for_goals": platform.best_for_goals,
                "best_for_industries": platform.best_for_industries,
                "supports_search": platform.supports_search,
                "supports_display": platform.supports_display,
                "supports_video": platform.supports_video,
                "supports_shopping": platform.supports_shopping,
                "supports_mobile": platform.supports_mobile,
                "min_budget": platform.min_budget,
                "currency_support": platform.currency_support,
                "requires_own_account": platform.requires_own_account,
            })
        
        return platforms_info
    
    def _get_platforms_info_old(self) -> List[Dict[str, Any]]:
        """OLD - Get information about available ad platforms (hardcoded) - DEPRECATED"""
        return [
            {
                "id": 0,
                "name": "Google Ads",
                "type": "search",
                "best_for": ["website-traffic", "online-leads", "online-sales"],
                "description": "Search engine advertising, display ads, shopping ads, video ads",
                "audience": "Broad, intent-driven users searching for products/services",
            },
            {
                "id": 1,
                "name": "Facebook Ads",
                "type": "social",
                "best_for": ["brand-awareness", "online-leads", "online-sales"],
                "description": "Social media feed ads, stories, reels, video ads",
                "audience": "Broad consumer audience, great for B2C",
            },
            {
                "id": 2,
                "name": "Instagram Ads",
                "type": "social",
                "best_for": ["brand-awareness", "online-sales"],
                "description": "Visual social media ads, stories, reels, shopping",
                "audience": "Younger demographic, visual content lovers, fashion/beauty/e-commerce",
            },
            {
                "id": 3,
                "name": "LinkedIn Ads",
                "type": "social",
                "best_for": ["online-leads", "brand-awareness"],
                "description": "Professional network advertising, B2B focused",
                "audience": "Professionals, B2B decision makers, career-focused",
            },
            {
                "id": 4,
                "name": "Twitter Ads",
                "type": "social",
                "best_for": ["brand-awareness", "online-leads"],
                "description": "Real-time social media advertising",
                "audience": "News-aware, tech-savvy, engaged users",
            },
            {
                "id": 8,
                "name": "YouTube Ads",
                "type": "video",
                "best_for": ["brand-awareness", "website-traffic"],
                "description": "Video advertising on YouTube",
                "audience": "Video content consumers, broad reach",
            },
            {
                "id": 10,
                "name": "TikTok Ads",
                "type": "video",
                "best_for": ["brand-awareness", "online-sales"],
                "description": "Short-form video advertising",
                "audience": "Gen Z, young millennials, creative content",
            },
            {
                "id": 17,
                "name": "Microsoft Ads",
                "type": "search",
                "best_for": ["website-traffic", "online-leads"],
                "description": "Bing, Yahoo search advertising",
                "audience": "Older demographic, Windows users, alternative to Google",
            },
            {
                "id": 19,
                "name": "Google Performance Max",
                "type": "display",
                "best_for": ["website-traffic", "online-sales", "online-leads"],
                "description": "AI-powered campaign across all Google properties",
                "audience": "Broad reach across Google ecosystem",
            },
            {
                "id": 20,
                "name": "Online Bannering",
                "type": "display",
                "best_for": ["brand-awareness"],
                "description": "Display banner advertising",
                "audience": "Broad reach, awareness campaigns",
            },
            {
                "id": 18,
                "name": "Amazon Ads",
                "type": "shopping",
                "best_for": ["online-sales"],
                "description": "Product advertising on Amazon",
                "audience": "Amazon shoppers, purchase-ready users",
            },
        ]
    
    def _create_analysis_prompt(
        self,
        context: Dict[str, Any],
        platforms: List[Dict[str, Any]],
        conversion_goal: ConversionGoal,
    ) -> str:
        """Create comprehensive, refined prompt for Gemini AI"""
        
        goal_descriptions = {
            "website-traffic": "Drive visitors to the website",
            "brand-awareness": "Increase brand visibility and recognition",
            "online-leads": "Generate leads (form submissions, signups, inquiries)",
            "online-sales": "Drive direct sales and conversions",
        }
        
        # Build comprehensive prompt
        prompt = f"""You are an expert digital marketing strategist with deep knowledge of advertising platforms, audience targeting, and campaign optimization. Your task is to analyze a business comprehensively and recommend the best advertising platform(s) using AI-powered semantic understanding.

**CAMPAIGN OBJECTIVE:**
- Primary Goal: {conversion_goal.value} ({goal_descriptions.get(conversion_goal.value, '')})
- Business Name: {context['business_name']}
- Industry: {context['business_industry']}
- Website URL: {context['website_url']}
- Target Locations: {', '.join(context.get('target_locations', [])) or 'Global/No specific location targeting'}

**BRAND IDENTITY:**
- Brand Description: {context.get('brand_description', 'Not available')}
- Brand Colors: {', '.join(context.get('brand_colors', [])) or 'Not specified'}
- Tone of Voice: {', '.join(context.get('brand_tone', [])) or 'Not specified'}
- Primary Language: {context.get('brand_language', 'en')}

**WEBSITE CONTENT ANALYSIS:**
"""
        
        stats = context.get('content_stats', {})
        content_indicators = context.get('content_type_indicators', {})
        
        prompt += f"""
- Pages Crawled: {stats.get('pages_crawled', 0)} pages
- Total Content: {stats.get('total_words', 0)} words
- Visual Content: {stats.get('total_images', 0)} images ({stats.get('avg_images_per_page', 0):.1f} avg per page)
- Content Type Indicators:
  * E-commerce Elements: {content_indicators.get('has_ecommerce_keywords', False)}
  * Visual-Heavy: {content_indicators.get('is_visual_heavy', False)}
  * Text-Heavy: {content_indicators.get('is_text_heavy', False)}
  * Video Content: {content_indicators.get('has_video_content', False)}
  * Blog/Article Content: {content_indicators.get('has_blog_content', False)}

**WEBSITE CONTENT (Semantic Analysis):**
"""
        
        # Add full website content for semantic understanding
        website_content = context.get('website_content_full', '')
        if website_content and website_content != "Content not crawled":
            # Limit to 8000 chars to stay within token limits
            prompt += f"""
{website_content[:8000]}

(Content truncated if longer - this represents the semantic understanding of the website)
"""
        else:
            prompt += "\nWebsite content was not crawled or is unavailable.\n"
        
        # Add page structure info
        page_titles = context.get('page_titles', [])
        if page_titles:
            prompt += f"""
**Page Structure (Top {len(page_titles[:10])} pages):**
{chr(10).join(f"- {title}" for title in page_titles[:10])}
"""
        
        prompt += f"""

**AVAILABLE ADVERTISING PLATFORMS:**
{json.dumps(platforms, indent=2)}

**YOUR COMPREHENSIVE ANALYSIS TASK:**

Perform a deep semantic analysis considering:

1. **Campaign Goal Alignment**: Which platform(s) are most effective for achieving "{conversion_goal.value}"? Consider platform strengths, audience intent, and conversion capabilities.

2. **Target Audience Analysis**: Based on the website content, brand description, industry, and target locations, who is the ideal customer? Which platform(s) have audiences that match this profile?

3. **Content Type Suitability**: Analyze the website's content style (visual vs text-heavy, e-commerce vs informational, B2B vs B2C). Which platform(s) best showcase this type of content?

4. **Brand Personality Match**: Consider the brand's tone of voice, colors, and description. Which platform(s) align with this brand personality? (e.g., professional brands → LinkedIn, creative brands → Instagram/TikTok)

5. **Industry Best Practices**: Based on the industry "{context['business_industry']}", which platform(s) have proven success in this vertical?

6. **Geographic Considerations**: How do the target locations affect platform selection? (e.g., some platforms have better coverage in certain regions)

**REQUIRED OUTPUT FORMAT (Valid JSON only):**
{{
  "recommended_platform_id": <integer - ID of the single best platform>,
  "recommended_platform_name": "<string - name of recommended platform>",
  "ai_reasoning": "<string - comprehensive explanation (300-500 words) of why this platform is the best choice, considering all factors above>",
  "all_recommendations": [
    {{
      "platform_id": <integer>,
      "name": "<string>",
      "score": <float between 0.0 and 1.0, where 1.0 = perfect match>,
      "reasons": ["<specific reason 1>", "<specific reason 2>", "<specific reason 3>"],
      "ai_reasoning": "<detailed explanation (100-200 words) of why this platform fits, including audience match, content suitability, and goal alignment>"
    }},
    // ... at least top 5-8 platforms ranked by score
  ],
  "ai_analysis": {{
    "content_summary": "<string - comprehensive summary of what type of website/content this is (100-150 words)>",
    "target_audience": "<string - detailed description of the ideal customer profile based on content analysis (100-150 words)>",
    "content_type": "<string - visual-heavy/text-heavy/mixed/e-commerce/informational/blog/etc>",
    "brand_personality": "<string - professional/casual/creative/technical/luxury/affordable/etc based on tone and description>"
  }}
}}

**SCORING GUIDELINES:**
- 0.9-1.0: Exceptional match - platform is ideal for this campaign
- 0.7-0.89: Strong match - platform is very suitable
- 0.5-0.69: Good match - platform is suitable with some considerations
- 0.3-0.49: Moderate match - platform could work but not optimal
- 0.0-0.29: Poor match - platform is not recommended

**IMPORTANT:**
- Return ONLY valid JSON (no markdown code blocks, no explanations outside JSON)
- Ensure all scores are between 0.0 and 1.0
- Provide at least 5 platform recommendations, ranked by score
- Be specific and detailed in your reasoning
- Consider all factors holistically, not just individual metrics
"""
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's JSON response"""
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            result = json.loads(cleaned)
            
            # Validate structure
            if "recommended_platform_id" not in result:
                raise ValueError("Missing recommended_platform_id in response")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Gemini JSON response: {e}")
            print(f"Response was: {response_text[:500]}")
            raise ValueError(f"Invalid JSON response from Gemini: {e}")

