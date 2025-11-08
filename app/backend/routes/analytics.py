"""
Analytics Routes

Provides analytics and reporting endpoints for user data, listings performance,
and platform metrics.
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query

from auth import get_current_user
from db import get_typed_db

# Feature flags
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
logger = logging.getLogger(__name__)


# Dashboard Stats (already implemented in ads.py, but adding here for completeness)
@router.get("/dashboard")
async def get_dashboard_analytics(
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get comprehensive dashboard analytics for the user.
    This is a duplicate of the ads.py endpoint for API consistency.
    """
    # Redirect to ads.py implementation or implement here
    # For now, return basic structure
    return {
        "total_listings": 0,
        "active_listings": 0,
        "total_posts": 0,
        "total_views": 0,
        "total_leads": 0,
        "platforms_connected": 0,
        "revenue": 0,
        "conversion_rate": 0.0,
        "period": "30d"
    }


@router.get("/listings")
async def get_listing_analytics(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    platform: str = Query(None, description="Filter by platform"),
    user_id: str = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get detailed analytics for user's listings.
    """
    db = get_typed_db()

    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.now().date().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    analytics = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Get listings for user
                listings_result = client.table("listings").select("*").eq("user_id", user_id).execute()

                for listing in listings_result.data:
                    listing_id = listing["id"]

                    # Get posted ads for this listing
                    posted_result = client.table("posted_ads").select("*").eq("ad_id", listing_id).execute()

                    # Get analytics data from posted_ads (simplified)
                    total_views = 0
                    total_clicks = 0
                    total_leads = 0

                    for posted in posted_result.data:
                        total_views += posted.get("views", 0)
                        total_clicks += posted.get("clicks", 0)
                        total_leads += posted.get("leads", 0)

                    analytics.append({
                        "listing_id": listing_id,
                        "title": listing.get("title", ""),
                        "platform": platform or "all",
                        "views": total_views,
                        "clicks": total_clicks,
                        "leads": total_leads,
                        "conversion_rate": (total_clicks / total_views * 100) if total_views > 0 else 0,
                        "status": listing.get("status", "draft"),
                        "created_at": listing.get("created_at"),
                    })

                logger.info(f"Retrieved listing analytics for {len(analytics)} listings from Supabase")
        except Exception as e:
            logger.error(f"Failed to get listing analytics from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to get listing analytics")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        # Get listings from MongoDB
        query = {"user_id": user_id}
        if platform:
            query["platforms"] = {"$in": [platform]}

        listings = await db["ads"].find(query).to_list(1000)

        for listing in listings:
            listing_id = listing["id"]

            # Get posted ads analytics
            posted_ads = await db["posted_ads"].find({"ad_id": listing_id}).to_list(100)

            total_views = sum(pa.get("views", 0) for pa in posted_ads)
            total_clicks = sum(pa.get("clicks", 0) for pa in posted_ads)
            total_leads = sum(pa.get("leads", 0) for pa in posted_ads)

            analytics.append({
                "listing_id": listing_id,
                "title": listing.get("title", ""),
                "platform": platform or "all",
                "views": total_views,
                "clicks": total_clicks,
                "leads": total_leads,
                "conversion_rate": (total_clicks / total_views * 100) if total_views > 0 else 0,
                "status": listing.get("status", "draft"),
                "created_at": listing.get("created_at"),
            })

    return analytics


@router.get("/platforms")
async def get_platform_analytics(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """
    Get analytics broken down by platform.
    """
    db = get_typed_db()

    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.now().date().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    platform_stats = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Get all posted ads for user and group by platform
                posted_result = client.table("posted_ads").select("*").execute()

                # Group by platform
                platform_data = {}
                for posted in posted_result.data:
                    platform = posted["platform"]
                    if platform not in platform_data:
                        platform_data[platform] = {
                            "platform": platform,
                            "total_posts": 0,
                            "total_views": 0,
                            "total_clicks": 0,
                            "total_leads": 0,
                            "success_rate": 0.0,
                        }

                    platform_data[platform]["total_posts"] += 1
                    platform_data[platform]["total_views"] += posted.get("views", 0)
                    platform_data[platform]["total_clicks"] += posted.get("clicks", 0)
                    platform_data[platform]["total_leads"] += posted.get("leads", 0)

                # Calculate success rates and convert to list
                for platform, data in platform_data.items():
                    data["success_rate"] = (data["total_leads"] / data["total_posts"] * 100) if data["total_posts"] > 0 else 0
                    platform_stats.append(data)

                logger.info(f"Retrieved platform analytics for {len(platform_stats)} platforms from Supabase")
        except Exception as e:
            logger.error(f"Failed to get platform analytics from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to get platform analytics")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        # Aggregate posted ads by platform
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": "$platform",
                "total_posts": {"$sum": 1},
                "total_views": {"$sum": "$views"},
                "total_clicks": {"$sum": "$clicks"},
                "total_leads": {"$sum": "$leads"},
            }},
            {"$sort": {"total_posts": -1}}
        ]

        results = await db["posted_ads"].aggregate(pipeline).to_list(20)

        for result in results:
            platform_stats.append({
                "platform": result["_id"],
                "total_posts": result["total_posts"],
                "total_views": result.get("total_views", 0),
                "total_clicks": result.get("total_clicks", 0),
                "total_leads": result.get("total_leads", 0),
                "success_rate": (result.get("total_leads", 0) / result["total_posts"] * 100) if result["total_posts"] > 0 else 0,
            })

    return platform_stats


@router.get("/revenue")
async def get_revenue_analytics(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get revenue analytics (from Stripe data).
    """
    # Set default date range (last 30 days)
    if not end_date:
        end_date = datetime.now().date().isoformat()
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).date().isoformat()

    # For now, return mock data since revenue tracking would need additional tables
    # In production, this would aggregate from Stripe webhook data stored in database
    return {
        "total_revenue": 0.0,
        "monthly_recurring": 0.0,
        "one_time_payments": 0.0,
        "refunds": 0.0,
        "currency": "USD",
        "period": f"{start_date} to {end_date}",
        "note": "Revenue tracking requires additional database schema for Stripe data"
    }


@router.get("/performance")
async def get_performance_metrics(
    user_id: str = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get overall performance metrics for the user.
    """
    return {
        "account_age_days": 0,
        "total_listings_created": 0,
        "average_listing_lifetime": 0,
        "platform_diversity_score": 0.0,
        "response_time_avg": 0,
        "conversion_funnel": {
            "listings_created": 0,
            "listings_posted": 0,
            "leads_generated": 0,
            "conversions": 0
        },
        "trends": {
            "listings_growth": 0.0,
            "engagement_growth": 0.0,
            "revenue_growth": 0.0
        }
    }