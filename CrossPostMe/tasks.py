import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Dict

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

# Database connection
mongo_url = os.environ.get("MONGO_URL")
db_name = os.environ.get("DB_NAME")


async def get_db():
    client = AsyncIOMotorClient(mongo_url)
    return client[db_name]


# Social media posting tasks
def process_social_post(post_data: Dict[str, Any]):
    """Process and distribute a post to multiple social media platforms"""
    try:
        platforms = post_data.get("platforms", [])
        content = post_data.get("content", "")
        media_urls = post_data.get("media_urls", [])

        results = {}

        for platform in platforms:
            # Adapt content for platform-specific requirements
            adapted_content = adapt_content_for_platform(content, platform)

            # Post to platform
            result = post_to_platform(platform, adapted_content, media_urls)
            results[platform] = result

        return {"status": "completed", "results": results}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def adapt_content_for_platform(content: str, platform: str) -> str:
    """Adapt content based on platform-specific requirements"""
    adaptations = {
        "twitter": lambda c: c[:280],  # Twitter character limit
        "linkedin": lambda c: c[:3000],  # LinkedIn limit
        "facebook": lambda c: c[:63206],  # Facebook limit
        "instagram": lambda c: c[:2200],  # Instagram caption limit
    }

    adapter = adaptations.get(platform.lower(), lambda c: c)
    return adapter(content)


def post_to_platform(platform: str, content: str, media_urls: list) -> Dict[str, Any]:
    """Post content to specific social media platform"""
    # This would integrate with actual platform APIs
    # For now, return a mock response
    return {
        "platform": platform,
        "post_id": f"mock_{platform}_{datetime.now().timestamp()}",
        "status": "posted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def schedule_post(post_data: Dict[str, Any], scheduled_time: str):
    """Schedule a post for future publication"""
    try:
        # Store scheduled post in database
        asyncio.run(store_scheduled_post(post_data, scheduled_time))
        return {"status": "scheduled", "scheduled_time": scheduled_time}
    except Exception as e:
        return {"status": "failed", "error": str(e)}


async def store_scheduled_post(post_data: Dict[str, Any], scheduled_time: str, db=None):
    """Store scheduled post in database. If `db` is not provided, create a temporary client."""
    own_client = None
    if db is None:
        own_client = AsyncIOMotorClient(mongo_url)
        db = own_client[db_name]

    scheduled_post = {
        "content": post_data.get("content"),
        "platforms": post_data.get("platforms", []),
        "media_urls": post_data.get("media_urls", []),
        "scheduled_time": scheduled_time,
        "status": "scheduled",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.scheduled_posts.insert_one(scheduled_post)

    if own_client is not None:
        own_client.close()


def validate_platforms(platforms: list) -> Dict[str, Any]:
    """Validate platform connections and credentials"""
    try:
        validation_results = {}

        for platform in platforms:
            # Check platform connectivity and auth
            is_valid = check_platform_auth(platform)
            validation_results[platform] = {
                "valid": is_valid,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

        return {"status": "completed", "results": validation_results}

    except Exception as e:
        return {"status": "failed", "error": str(e)}


def check_platform_auth(platform: str) -> bool:
    """Check if platform authentication is valid"""
    # This would check actual platform API credentials
    # For now, return True as mock
    return True
