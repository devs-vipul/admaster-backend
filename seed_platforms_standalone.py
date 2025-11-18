"""
Standalone script to seed platforms into MongoDB
Run: python3 seed_platforms_standalone.py
"""
import os
import pymongo
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PLATFORMS_DATA = [
    {
        "platform_id": 0,
        "name": "Google Ads",
        "slug": "google-ads",
        "type": "search",
        "description": "Appear with your ads on top of the world's first search engine.",
        "icon": "Search",
        "supports_search": True,
        "supports_display": True,
        "supports_video": True,
        "supports_shopping": True,
        "supports_mobile": True,
        "best_for_goals": ["website-traffic", "online-leads", "online-sales"],
        "best_for_industries": ["Technology", "E-commerce", "Retail", "Professional Services"],
        "min_budget": 1.0,
        "currency_support": ["USD", "INR", "EUR", "GBP", "AUD", "CAD"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 1,
        "name": "Facebook Ads",
        "slug": "facebook-ads",
        "type": "social",
        "description": "Appear with your ads in the newsfeed & stories & reels of your audience.",
        "icon": "Facebook",
        "supports_display": True,
        "supports_video": True,
        "supports_mobile": True,
        "best_for_goals": ["brand-awareness", "online-leads", "online-sales"],
        "best_for_industries": ["E-commerce", "Retail", "Food & Beverage", "Media & Entertainment"],
        "min_budget": 1.0,
        "currency_support": ["USD", "INR", "EUR", "GBP"],
        "requires_own_account": True,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 2,
        "name": "Instagram Ads",
        "slug": "instagram-ads",
        "type": "social",
        "description": "Appear with your ads in the newsfeed, stories & reels of your audience.",
        "icon": "Instagram",
        "supports_display": True,
        "supports_video": True,
        "supports_mobile": True,
        "best_for_goals": ["brand-awareness", "online-sales"],
        "best_for_industries": ["E-commerce", "Fashion", "Food & Beverage", "Media & Entertainment"],
        "min_budget": 1.0,
        "currency_support": ["USD", "INR", "EUR", "GBP"],
        "requires_own_account": True,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 3,
        "name": "LinkedIn Ads",
        "slug": "linkedin-ads",
        "type": "social",
        "description": "Engage a community of professionals to drive actions that are relevant to your business.",
        "icon": "Linkedin",
        "supports_display": True,
        "supports_video": True,
        "best_for_goals": ["online-leads", "brand-awareness"],
        "best_for_industries": ["Technology", "Professional Services", "Consulting", "Finance"],
        "min_budget": 10.0,
        "currency_support": ["USD", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 4,
        "name": "Twitter Ads",
        "slug": "twitter-ads",
        "type": "social",
        "description": "Appear with your ads in the timeline & search results of your audience.",
        "icon": "Twitter",
        "supports_display": True,
        "supports_video": True,
        "best_for_goals": ["brand-awareness", "online-leads"],
        "best_for_industries": ["Technology", "Media & Entertainment", "Marketing & Advertising"],
        "min_budget": 1.0,
        "currency_support": ["USD", "EUR", "GBP"],
        "requires_own_account": True,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 8,
        "name": "YouTube Ads",
        "slug": "youtube-ads",
        "type": "video",
        "description": "Video advertising on YouTube",
        "icon": "Youtube",
        "supports_video": True,
        "supports_display": True,
        "best_for_goals": ["brand-awareness", "website-traffic"],
        "best_for_industries": ["Media & Entertainment", "Education", "Technology"],
        "min_budget": 1.0,
        "currency_support": ["USD", "INR", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 10,
        "name": "TikTok Ads",
        "slug": "tiktok-ads",
        "type": "video",
        "description": "Short-form video advertising",
        "icon": "Music",
        "supports_video": True,
        "supports_mobile": True,
        "best_for_goals": ["brand-awareness", "online-sales"],
        "best_for_industries": ["E-commerce", "Media & Entertainment", "Food & Beverage"],
        "min_budget": 20.0,
        "currency_support": ["USD", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 17,
        "name": "Microsoft Ads",
        "slug": "microsoft-ads",
        "type": "search",
        "description": "Appear with your ads on top of Bing, Yahoo! & other search partners.",
        "icon": "Search",
        "supports_search": True,
        "supports_display": True,
        "best_for_goals": ["website-traffic", "online-leads"],
        "best_for_industries": ["Technology", "Professional Services", "E-commerce"],
        "min_budget": 1.0,
        "currency_support": ["USD", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 19,
        "name": "Google Performance Max",
        "slug": "google-performance-max",
        "type": "display",
        "description": "Performance Max is a goal-based campaign that allows advertisers to access all of the Google Ads inventory in a single campaign.",
        "icon": "TrendingUp",
        "supports_search": True,
        "supports_display": True,
        "supports_video": True,
        "supports_shopping": True,
        "supports_mobile": True,
        "best_for_goals": ["website-traffic", "online-sales", "online-leads"],
        "best_for_industries": ["E-commerce", "Retail", "Technology"],
        "min_budget": 1.0,
        "currency_support": ["USD", "INR", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 20,
        "name": "Online Bannering",
        "slug": "online-bannering",
        "type": "display",
        "description": "Reach a broad audience and build awareness",
        "icon": "Monitor",
        "supports_display": True,
        "best_for_goals": ["brand-awareness"],
        "best_for_industries": ["E-commerce", "Retail", "Media & Entertainment"],
        "min_budget": 1.0,
        "currency_support": ["USD", "INR", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
    {
        "platform_id": 18,
        "name": "Amazon Ads",
        "slug": "amazon-ads",
        "type": "shopping",
        "description": "Product advertising on Amazon",
        "icon": "ShoppingCart",
        "supports_shopping": True,
        "supports_display": True,
        "best_for_goals": ["online-sales"],
        "best_for_industries": ["E-commerce", "Retail"],
        "min_budget": 1.0,
        "currency_support": ["USD", "EUR", "GBP"],
        "requires_own_account": False,
        "is_active": True,
        "is_beta": False,
    },
]


def seed_platforms():
    """Seed platforms into database"""
    # Get MongoDB URL from environment
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    mongodb_db_name = os.getenv("MONGODB_DB_NAME", "admaster")
    
    print(f"🔌 Connecting to MongoDB: {mongodb_db_name}")
    
    client = None
    try:
        # Connect to MongoDB
        client = pymongo.MongoClient(mongodb_url)
        db = client[mongodb_db_name]
        platforms_collection = db["platforms"]
        
        print("🌱 Seeding platforms...\n")
        
        created_count = 0
        skipped_count = 0
        
        for platform_data in PLATFORMS_DATA:
            # Check if platform already exists
            existing = platforms_collection.find_one(
                {"platform_id": platform_data["platform_id"]}
            )
            
            if existing:
                print(f"⏭️  Platform {platform_data['name']} (ID: {platform_data['platform_id']}) already exists, skipping...")
                skipped_count += 1
                continue
            
            # Insert platform
            platforms_collection.insert_one(platform_data)
            print(f"✅ Created platform: {platform_data['name']} (ID: {platform_data['platform_id']})")
            created_count += 1
        
        # Count total platforms
        total = platforms_collection.count_documents({})
        print(f"\n{'='*50}")
        print(f"✅ Platform seeding complete!")
        print(f"   Created: {created_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total platforms in DB: {total}")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"❌ Error seeding platforms: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        if client:
            client.close()


if __name__ == "__main__":
    seed_platforms()

