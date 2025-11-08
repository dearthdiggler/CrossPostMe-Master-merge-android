import os
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from auth import get_optional_current_user
from db import get_db
from models import Ad, AdAnalytics, AdCreate, AdUpdate, DashboardStats, PostedAd
from supabase_db import db as supabase_db

# Feature flags for Supabase migration
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/ads", tags=["ads"])


# Helper functions for datetime serialization/deserialization
def serialize_datetime_fields(doc: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Convert datetime objects to ISO strings for MongoDB storage."""
    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], datetime):
            doc[field] = doc[field].isoformat()
    return doc


def deserialize_datetime_fields(
    doc: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    """Convert ISO strings back to datetime objects."""
    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            try:
                doc[field] = datetime.fromisoformat(doc[field])
            except ValueError:
                # Handle invalid ISO format - set to current time for fallback
                if field == "created_at" or field == "posted_at":
                    doc[field] = datetime.now(timezone.utc)
    return doc


# Helpers to normalize posted ad documents before constructing PostedAd
def normalize_posted_ad_dict(doc: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow-copied dict with fields coerced to the types
    expected by the PostedAd model (datetime for posted_at, ints for
    views/clicks/leads, strings or None for platform_ad_id/post_url).
    This keeps runtime semantics identical while satisfying static typing.
    """
    d: dict[str, Any] = dict(doc or {})

    # posted_at -> datetime
    if "posted_at" in d and d["posted_at"] is not None:
        v = d["posted_at"]
        if isinstance(v, str):
            try:
                d["posted_at"] = datetime.fromisoformat(v)
            except Exception:
                d["posted_at"] = datetime.now(timezone.utc)
    else:
        d["posted_at"] = datetime.now(timezone.utc)

    # Optional string fields
    for key in ("platform_ad_id", "post_url"):
        if key in d and d[key] is not None:
            d[key] = str(d[key])
        else:
            d[key] = None

    # Numeric counters
    for key in ("views", "clicks", "leads"):
        try:
            d[key] = int(d.get(key, 0)) if d.get(key) is not None else 0
        except Exception:
            d[key] = 0

    return d


# Typed database wrapper
db = get_db()

import logging
logger = logging.getLogger(__name__)


# Create Ad
@router.post("/", response_model=Ad)
async def create_ad(ad: AdCreate) -> Ad:
    ad_dict = ad.model_dump()
    ad_obj = Ad(**ad_dict)

    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = ad_obj.model_dump()
    serialize_datetime_fields(doc, ["created_at", "scheduled_time"])

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Insert into Supabase listings table
                listing_data = {
                    "id": doc["id"],
                    "user_id": doc.get("user_id"),
                    "title": doc["title"],
                    "description": doc.get("description"),
                    "price": float(doc["price"]) if doc.get("price") else None,
                    "category": doc.get("category"),
                    "condition": doc.get("condition"),
                    "images": doc.get("images", []),
                    "location": doc.get("location"),
                    "status": doc.get("status", "draft"),
                    "platforms": doc.get("platforms", {}),
                    "metadata": {
                        "scheduled_time": doc.get("scheduled_time"),
                        "original_doc": doc  # Store full doc for compatibility
                    }
                }
                result = client.table("listings").insert(listing_data).execute()
                logger.info(f"Ad created in Supabase: {doc['id']}")

                # PARALLEL WRITE: Also write to MongoDB
                if PARALLEL_WRITE:
                    try:
                        await db["ads"].insert_one(doc)
                        logger.info(f"✅ Parallel write to MongoDB successful for ad: {doc['id']}")
                    except Exception as e:
                        logger.warning(f"⚠️  Parallel MongoDB write failed for ad {doc['id']}: {e}")
        except Exception as e:
            logger.error(f"Ad creation failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to create ad")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        await db["ads"].insert_one(doc)
        logger.info(f"Ad created in MongoDB: {doc['id']}")

    return ad_obj


# Get All Ads
@router.get("/", response_model=list[Ad])
async def get_ads(
    status: str | None = None,
    platform: str | None = None,
    user_id: str | None = Depends(get_optional_current_user),
) -> list[Ad]:
    ads = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                query = client.table("listings").select("*")

                # Apply filters
                if user_id:
                    query = query.eq("user_id", user_id)
                if status:
                    query = query.eq("status", status)

                query = query.order("created_at", desc=True).limit(1000)
                result = query.execute()

                # Convert Supabase listings to Ad format
                for listing in result.data:
                    # Extract original doc from metadata if available
                    ad_data = listing.get("metadata", {}).get("original_doc", {})
                    if not ad_data:
                        # Build ad data from listing fields
                        ad_data = {
                            "id": listing["id"],
                            "user_id": listing.get("user_id"),
                            "title": listing["title"],
                            "description": listing.get("description"),
                            "price": listing.get("price"),
                            "category": listing.get("category"),
                            "condition": listing.get("condition"),
                            "images": listing.get("images", []),
                            "location": listing.get("location"),
                            "status": listing.get("status"),
                            "platforms": listing.get("platforms", []),
                            "created_at": listing.get("created_at"),
                        }
                    deserialize_datetime_fields(ad_data, ["created_at", "scheduled_time"])
                    ads.append(Ad(**ad_data))

                logger.info(f"Fetched {len(ads)} ads from Supabase")
        except Exception as e:
            logger.error(f"Failed to fetch ads from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch ads")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        if platform:
            query["platforms"] = platform
        if user_id:
            query["user_id"] = user_id

        ads_docs = await db["ads"].find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)

        # Convert ISO string timestamps back to datetime objects
        for ad in ads_docs:
            deserialize_datetime_fields(ad, ["created_at", "scheduled_time"])
            ads.append(Ad(**ad))

        logger.info(f"Fetched {len(ads)} ads from MongoDB")

    return ads


# Get Ad by ID
@router.get("/{ad_id}", response_model=Ad)
async def get_ad(ad_id: str) -> Ad:
    ad = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                result = client.table("listings").select("*").eq("id", ad_id).execute()
                if result.data and len(result.data) > 0:
                    listing = result.data[0]
                    # Extract original doc from metadata if available
                    ad_data = listing.get("metadata", {}).get("original_doc", {})
                    if not ad_data:
                        # Build ad data from listing fields
                        ad_data = {
                            "id": listing["id"],
                            "user_id": listing.get("user_id"),
                            "title": listing["title"],
                            "description": listing.get("description"),
                            "price": listing.get("price"),
                            "category": listing.get("category"),
                            "condition": listing.get("condition"),
                            "images": listing.get("images", []),
                            "location": listing.get("location"),
                            "status": listing.get("status"),
                            "platforms": listing.get("platforms", []),
                            "created_at": listing.get("created_at"),
                        }
                    ad = Ad(**ad_data)
                    logger.info(f"Fetched ad from Supabase: {ad_id}")
        except Exception as e:
            logger.error(f"Failed to fetch ad from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch ad")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        ad_doc = await db["ads"].find_one({"id": ad_id})
        if ad_doc:
            ad = Ad(**ad_doc)
            logger.info(f"Fetched ad from MongoDB: {ad_id}")

    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    return ad


# Update Ad
@router.put("/{ad_id}", response_model=Ad)
async def update_ad(ad_id: str, ad_update: AdUpdate) -> Ad:
    updated_ad = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Build update data from AdUpdate model
                update_data = ad_update.model_dump(exclude_unset=True)

                # Convert datetime fields to ISO strings
                if "scheduled_time" in update_data and update_data["scheduled_time"]:
                    update_data["scheduled_time"] = update_data["scheduled_time"].isoformat()

                # Map to Supabase listing fields
                listing_update = {}
                if "title" in update_data:
                    listing_update["title"] = update_data["title"]
                if "description" in update_data:
                    listing_update["description"] = update_data["description"]
                if "price" in update_data:
                    listing_update["price"] = float(update_data["price"]) if update_data["price"] else None
                if "category" in update_data:
                    listing_update["category"] = update_data["category"]
                if "location" in update_data:
                    listing_update["location"] = update_data["location"]
                if "images" in update_data:
                    listing_update["images"] = update_data["images"]
                if "status" in update_data:
                    listing_update["status"] = update_data["status"]
                if "platforms" in update_data:
                    listing_update["platforms"] = update_data["platforms"]

                listing_update["updated_at"] = datetime.now(timezone.utc).isoformat()

                # Update in Supabase
                result = client.table("listings").update(listing_update).eq("id", ad_id).execute()

                if result.data and len(result.data) > 0:
                    listing = result.data[0]
                    # Build Ad object from listing
                    ad_data = {
                        "id": listing["id"],
                        "user_id": listing.get("user_id"),
                        "title": listing["title"],
                        "description": listing.get("description"),
                        "price": listing.get("price"),
                        "category": listing.get("category"),
                        "condition": listing.get("condition"),
                        "images": listing.get("images", []),
                        "location": listing.get("location"),
                        "status": listing.get("status"),
                        "platforms": listing.get("platforms", []),
                        "created_at": listing.get("created_at"),
                    }
                    updated_ad = Ad(**ad_data)
                    logger.info(f"Updated ad in Supabase: {ad_id}")

                    # PARALLEL WRITE: Also update in MongoDB
                    if PARALLEL_WRITE:
                        try:
                            await db["ads"].update_one({"id": ad_id}, {"$set": update_data})
                            logger.info(f"✅ Parallel write to MongoDB successful for ad update: {ad_id}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for ad update {ad_id}: {e}")
                else:
                    raise HTTPException(status_code=404, detail="Ad not found")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ad update failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to update ad")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})
        if not ad:
            raise HTTPException(status_code=404, detail="Ad not found")

        update_data = ad_update.model_dump(exclude_unset=True)

        # Convert datetime fields to ISO strings for MongoDB
        serialize_datetime_fields(update_data, ["scheduled_time"])

        if update_data:
            await db["ads"].update_one({"id": ad_id}, {"$set": update_data})

        updated_ad_doc = await db["ads"].find_one({"id": ad_id}, {"_id": 0})

        # Convert ISO string timestamps back to datetime objects
        deserialize_datetime_fields(updated_ad_doc, ["created_at", "scheduled_time"])
        updated_ad = Ad(**updated_ad_doc)
        logger.info(f"Updated ad in MongoDB: {ad_id}")

    return updated_ad


# Delete Ad
@router.delete("/{ad_id}")
async def delete_ad(ad_id: str) -> dict[str, str]:
    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Soft delete by setting status to 'deleted'
                update_data = {
                    "status": "deleted",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                result = client.table("listings").update(update_data).eq("id", ad_id).execute()

                if result.data and len(result.data) > 0:
                    logger.info(f"Soft-deleted ad in Supabase: {ad_id}")

                    # PARALLEL WRITE: Also soft-delete in MongoDB
                    if PARALLEL_WRITE:
                        try:
                            await db["ads"].update_one({"id": ad_id}, {"$set": update_data})
                            logger.info(f"✅ Parallel write to MongoDB successful for ad deletion: {ad_id}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for ad deletion {ad_id}: {e}")

                    return {"message": "Ad deleted successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Ad not found")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Ad deletion failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to delete ad")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        result = await db["ads"].delete_one({"id": ad_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Ad not found")
        logger.info(f"Deleted ad in MongoDB: {ad_id}")
        return {"message": "Ad deleted successfully"}


# Post Ad to Platform (Real Integration)
@router.post("/{ad_id}/post", response_model=PostedAd)
async def post_ad(
    ad_id: str,
    platform: str,
    user_id: str = Depends(get_optional_current_user),
) -> PostedAd:
    from ..automation import AdData, PostStatus, automation_manager

    ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Get platform credentials for this user/platform using secure credential manager
    from ..automation.credentials import credential_manager

    credentials = await credential_manager.get_credentials(user_id, platform)

    if not credentials:
        raise HTTPException(
            status_code=400,
            detail=f"No credentials found for {platform}. Please connect your account first.",
        )

    # Get platform account info for contact details
    platform_account = await db["platform_accounts"].find_one(
        {
            "platform": platform,
            "status": "active",
            "user_id": ad.get("user_id", user_id),
        },
        {"_id": 0},
    )

    # Convert ad data to automation format
    contact_info = {}
    email = credentials.email or (
        platform_account.get("account_email") if platform_account else None
    )
    phone = credentials.phone or (
        platform_account.get("phone") if platform_account else None
    )
    if email is not None:
        contact_info["email"] = str(email)
    if phone is not None:
        contact_info["phone"] = str(phone)
    ad_data = AdData(
        title=ad["title"],
        description=ad["description"],
        price=ad["price"],
        category=ad["category"],
        location=ad["location"],
        images=ad.get("images", []),
        contact_info=contact_info if contact_info else None,
    )

    try:
        # Use real platform automation
        result = await automation_manager.post_to_platform(
            platform,
            ad_data,
            credentials,
        )

        if result.status == PostStatus.SUCCESS:
            # Create successful posted ad record
            posted_ad_dict = {
                "ad_id": ad_id,
                "platform": platform,
                "platform_ad_id": result.platform_ad_id,
                "post_url": result.post_url,
                "status": "active",
            }
            posted_ad = PostedAd(**normalize_posted_ad_dict(posted_ad_dict))

            # Save to database
            if USE_SUPABASE:
                # --- SUPABASE PATH (PRIMARY) ---
                try:
                    from supabase_db import get_supabase
                    client = get_supabase()
                    if client:
                        # Insert into posted_ads table
                        posted_data = {
                            "ad_id": ad_id,
                            "platform": platform,
                            "platform_ad_id": result.platform_ad_id,
                            "post_url": result.post_url,
                            "status": "active"
                        }
                        client.table("posted_ads").insert(posted_data).execute()
                        logger.info(f"Saved posted ad to Supabase: {ad_id} on {platform}")

                        # Update listing platforms JSONB
                        listing_update = {
                            "platforms": {platform: {
                                "posted_at": datetime.now(timezone.utc).isoformat(),
                                "platform_ad_id": result.platform_ad_id,
                                "post_url": result.post_url,
                                "status": "active"
                            }},
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                        client.table("listings").update(listing_update).eq("id", ad_id).execute()

                        # PARALLEL WRITE: Also save to MongoDB
                        if PARALLEL_WRITE:
                            try:
                                doc = posted_ad.model_dump()
                                serialize_datetime_fields(doc, ["posted_at"])
                                await db["posted_ads"].insert_one(doc)
                                await db["ads"].update_one({"id": ad_id}, {"$set": {"status": "posted"}})
                                logger.info(f"✅ Parallel write to MongoDB successful for posted ad: {ad_id}")
                            except Exception as e:
                                logger.warning(f"⚠️  Parallel MongoDB write failed for posted ad {ad_id}: {e}")
                except Exception as e:
                    logger.error(f"Failed to save posted ad to Supabase: {e}")
                    # Continue with response even if DB save fails
            else:
                # --- MONGODB PATH (FALLBACK) ---
                doc = posted_ad.model_dump()
                serialize_datetime_fields(doc, ["posted_at"])
                await db["posted_ads"].insert_one(doc)

            # Update ad status
            await db["ads"].update_one({"id": ad_id}, {"$set": {"status": "posted"}})

            return posted_ad

        # Handle posting failure
        error_message = f"Failed to post to {platform}: {result.message}"

        if result.status == PostStatus.RATE_LIMITED:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limited. Try again in {result.retry_after} seconds.",
            )
        if result.status == PostStatus.LOGIN_REQUIRED:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed for {platform}. Please check your credentials.",
            )
        if result.status == PostStatus.CAPTCHA_REQUIRED:
            raise HTTPException(
                status_code=423,
                detail=f"CAPTCHA required for {platform}. Manual intervention needed.",
            )
        raise HTTPException(status_code=400, detail=error_message)

    except Exception as e:
        # Log error and return HTTP exception
        import logging

        logger = logging.getLogger("ads.post")
        logger.error(f"Error posting to {platform}: {e}")

        raise HTTPException(
            status_code=500,
            detail=f"Internal error posting to {platform}: {e!s}",
        ) from e


# Post Ad to Multiple Platforms
@router.post("/{ad_id}/post-multiple")
async def post_ad_multiple_platforms(
    ad_id: str,
    platforms: list[str],
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, Any]:
    from backend.automation import AdData, automation_manager

    ad = await db["ads"].find_one({"id": ad_id}, {"_id": 0})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    # Get credentials for all requested platforms using secure credential manager
    from backend.automation.credentials import credential_manager

    credentials_map = {}

    for platform in platforms:
        credentials = await credential_manager.get_credentials(user_id, platform)
        if credentials:
            credentials_map[platform] = credentials

    if not credentials_map:
        raise HTTPException(
            status_code=400,
            detail="No active platform accounts found for the requested platforms",
        )

    # Convert ad data
    ad_data = AdData(
        title=ad["title"],
        description=ad["description"],
        price=ad["price"],
        category=ad["category"],
        location=ad["location"],
        images=ad.get("images", []),
    )

    # Post to multiple platforms concurrently
    results = await automation_manager.post_to_multiple_platforms(
        list(credentials_map.keys()),
        ad_data,
        credentials_map,
    )

    # Process results and save successful posts
    successful_posts = []
    failed_posts = []

    for platform, result in results.items():
        if result.status.value == "success":
            # Save successful post
            posted_ad_dict = {
                "ad_id": ad_id,
                "platform": platform,
                "platform_ad_id": result.platform_ad_id,
                "post_url": result.post_url,
                "status": "active",
            }
            posted_ad = PostedAd(**normalize_posted_ad_dict(posted_ad_dict))

            # Save to database
            if USE_SUPABASE:
                # --- SUPABASE PATH (PRIMARY) ---
                try:
                    from supabase_db import get_supabase
                    client = get_supabase()
                    if client:
                        # Insert into posted_ads table
                        posted_data = {
                            "ad_id": ad_id,
                            "platform": platform,
                            "platform_ad_id": result.platform_ad_id,
                            "post_url": result.post_url,
                            "status": "active"
                        }
                        client.table("posted_ads").insert(posted_data).execute()

                        # Update listing platforms JSONB
                        current_listing = client.table("listings").select("platforms").eq("id", ad_id).execute()
                        current_platforms = current_listing.data[0].get("platforms", {}) if current_listing.data else {}
                        current_platforms[platform] = {
                            "posted_at": datetime.now(timezone.utc).isoformat(),
                            "platform_ad_id": result.platform_ad_id,
                            "post_url": result.post_url,
                            "status": "active"
                        }

                        listing_update = {
                            "platforms": current_platforms,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                        client.table("listings").update(listing_update).eq("id", ad_id).execute()

                        # PARALLEL WRITE: Also save to MongoDB
                        if PARALLEL_WRITE:
                            try:
                                doc = posted_ad.model_dump()
                                serialize_datetime_fields(doc, ["posted_at"])
                                await db["posted_ads"].insert_one(doc)
                                logger.info(f"✅ Parallel write to MongoDB successful for multi-post: {ad_id} on {platform}")
                            except Exception as e:
                                logger.warning(f"⚠️  Parallel MongoDB write failed for multi-post {ad_id} on {platform}: {e}")
                except Exception as e:
                    logger.error(f"Failed to save multi-post to Supabase: {e}")
                    # Continue processing other platforms
            else:
                # --- MONGODB PATH (FALLBACK) ---
                doc = posted_ad.model_dump()
                serialize_datetime_fields(doc, ["posted_at"])
                await db["posted_ads"].insert_one(doc)

            successful_posts.append(
                {
                    "platform": platform,
                    "status": "success",
                    "post_url": result.post_url,
                    "platform_ad_id": result.platform_ad_id,
                },
            )
        else:
            failed_posts.append(
                {
                    "platform": platform,
                    "status": result.status.value,
                    "message": result.message,
                    "retry_after": result.retry_after,
                },
            )

    # Update ad status if any posts were successful
    if successful_posts:
        if USE_SUPABASE:
            # Update Supabase listing status
            try:
                from supabase_db import get_supabase
                client = get_supabase()
                if client:
                    client.table("listings").update({
                        "status": "posted",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }).eq("id", ad_id).execute()
            except Exception as e:
                logger.error(f"Failed to update listing status in Supabase: {e}")

        # Also update MongoDB status
        await db["ads"].update_one({"id": ad_id}, {"$set": {"status": "posted"}})

    return {
        "ad_id": ad_id,
        "successful_posts": successful_posts,
        "failed_posts": failed_posts,
        "total_requested": len(platforms),
        "total_successful": len(successful_posts),
        "total_failed": len(failed_posts),
    }


# Get Posted Ads
@router.get("/{ad_id}/posts", response_model=list[PostedAd])
async def get_posted_ads(ad_id: str) -> list[PostedAd]:
    posted_ads = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                result = client.table("posted_ads").select("*").eq("ad_id", ad_id).order("posted_at", desc=True).limit(1000).execute()

                for posted in result.data:
                    posted_ad_dict = {
                        "id": posted["id"],
                        "ad_id": posted["ad_id"],
                        "platform": posted["platform"],
                        "platform_ad_id": posted.get("platform_ad_id"),
                        "post_url": posted.get("post_url"),
                        "posted_at": posted.get("posted_at"),
                        "status": posted.get("status", "active"),
                        "views": posted.get("views", 0),
                        "clicks": posted.get("clicks", 0),
                        "leads": posted.get("leads", 0)
                    }
                    posted_ads.append(PostedAd(**normalize_posted_ad_dict(posted_ad_dict)))

                logger.info(f"Fetched {len(posted_ads)} posted ads from Supabase for ad: {ad_id}")
        except Exception as e:
            logger.error(f"Failed to fetch posted ads from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch posted ads")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        posted_ads_docs = await db["posted_ads"].find({"ad_id": ad_id}, {"_id": 0}).to_list(1000)

        # Convert ISO string timestamps back to datetime objects and coerce types
        for pa in posted_ads_docs:
            deserialize_datetime_fields(pa, ["posted_at"])
            posted_ads.append(PostedAd(**normalize_posted_ad_dict(pa)))

    return posted_ads


# Get All Posted Ads
@router.get("/posted/all", response_model=list[PostedAd])
async def get_all_posted_ads(platform: str | None = None) -> list[PostedAd]:
    posted_ads = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                query = client.table("posted_ads").select("*")

                if platform:
                    query = query.eq("platform", platform)

                query = query.order("posted_at", desc=True).limit(1000)
                result = query.execute()

                for posted in result.data:
                    posted_ad_dict = {
                        "id": posted["id"],
                        "ad_id": posted["ad_id"],
                        "platform": posted["platform"],
                        "platform_ad_id": posted.get("platform_ad_id"),
                        "post_url": posted.get("post_url"),
                        "posted_at": posted.get("posted_at"),
                        "status": posted.get("status", "active"),
                        "views": posted.get("views", 0),
                        "clicks": posted.get("clicks", 0),
                        "leads": posted.get("leads", 0)
                    }
                    posted_ads.append(PostedAd(**normalize_posted_ad_dict(posted_ad_dict)))

                logger.info(f"Fetched {len(posted_ads)} posted ads from Supabase")
        except Exception as e:
            logger.error(f"Failed to fetch all posted ads from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch posted ads")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        query: dict[str, Any] = {}
        if platform:
            query["platform"] = platform

        posted_ads_docs = (
            await db["posted_ads"]
            .find(query, {"_id": 0})
            .sort("posted_at", -1)
            .to_list(1000)
        )

        # Convert ISO string timestamps back to datetime objects and coerce types
        for pa in posted_ads_docs:
            deserialize_datetime_fields(pa, ["posted_at"])
            posted_ads.append(PostedAd(**normalize_posted_ad_dict(pa)))

    return posted_ads


# Get Dashboard Stats
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats() -> DashboardStats:
    total_ads = 0
    active_ads = 0
    total_posts = 0
    total_views = 0
    total_leads = 0
    platforms_connected = 0

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Get total ads count
                ads_result = client.table("listings").select("id", count="exact").execute()
                total_ads = ads_result.count if ads_result.count is not None else 0

                # Get active ads count (status = 'posted')
                active_result = client.table("listings").select("id", count="exact").eq("status", "posted").execute()
                active_ads = active_result.count if active_result.count is not None else 0

                # Get total posts count
                posts_result = client.table("posted_ads").select("id", count="exact").execute()
                total_posts = posts_result.count if posts_result.count is not None else 0

                # Get aggregate views and leads from posted_ads
                # Note: This is a simplified version - in production you'd want proper analytics tables
                analytics_result = client.table("posted_ads").select("views,leads").execute()
                for row in analytics_result.data:
                    total_views += row.get("views", 0)
                    total_leads += row.get("leads", 0)

                # Get platforms connected (distinct platforms in posted_ads)
                platforms_result = client.table("posted_ads").select("platform").execute()
                unique_platforms = set()
                for row in platforms_result.data:
                    unique_platforms.add(row["platform"])
                platforms_connected = len(unique_platforms)

                logger.info(f"Dashboard stats from Supabase: {total_ads} ads, {active_ads} active, {total_posts} posts")
        except Exception as e:
            logger.error(f"Failed to get dashboard stats from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to get dashboard stats")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        total_ads = await db["ads"].count_documents({})
        active_ads = await db["ads"].count_documents({"status": "posted"})
        total_posts = await db["posted_ads"].count_documents({})

        # Calculate total views and leads
        posted_ads = await db["posted_ads"].find({}).to_list(1000)
        total_views = sum(pa.get("views", 0) for pa in posted_ads)
        total_leads = sum(pa.get("leads", 0) for pa in posted_ads)

        # Count unique platforms
        platforms = await db["platform_accounts"].distinct("platform")
        platforms_connected = len(platforms)

    return DashboardStats(
        total_ads=total_ads,
        active_ads=active_ads,
        total_posts=total_posts,
        total_views=total_views,
        total_leads=total_leads,
        platforms_connected=platforms_connected,
    )


# Get Ad Analytics
@router.get("/{ad_id}/analytics", response_model=list[AdAnalytics])
async def get_ad_analytics(ad_id: str, days: int = 7) -> list[AdAnalytics]:
    analytics = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Get posted ads for this ad_id within date range
                start_date = datetime.now(timezone.utc) - timedelta(days=days)
                start_iso = start_date.isoformat()

                result = client.table("posted_ads").select("*").eq("ad_id", ad_id).gte("posted_at", start_iso).execute()

                for posted in result.data:
                    # For now, generate mock analytics data based on posted ad
                    # In production, you'd have a separate analytics table
                    analytics.append(
                        AdAnalytics(
                            ad_id=ad_id,
                            platform=posted["platform"],
                            views=random.randint(50, 500),
                            clicks=random.randint(10, 100),
                            leads=random.randint(1, 20),
                            messages=random.randint(1, 15),
                            conversion_rate=round(random.uniform(2.0, 8.0), 2),
                            date=posted.get("posted_at"),
                        ),
                    )

                logger.info(f"Generated analytics for {len(analytics)} posted ads from Supabase")
        except Exception as e:
            logger.error(f"Failed to get ad analytics from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to get ad analytics")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        start_date = datetime.now(timezone.utc) - timedelta(days=days)

        posted_ads = (
            await db["posted_ads"]
            .find({"ad_id": ad_id, "posted_at": {"$gte": start_date}})
            .to_list(1000)
        )

        for pa in posted_ads:
            analytics.append(
                AdAnalytics(
                    ad_id=ad_id,
                    platform=pa.get("platform"),
                    views=pa.get("views", random.randint(50, 500)),
                    clicks=pa.get("clicks", random.randint(10, 100)),
                    leads=pa.get("leads", random.randint(1, 20)),
                    messages=pa.get("messages", random.randint(1, 15)),
                    conversion_rate=round(random.uniform(2.0, 8.0), 2),
                    date=pa.get("posted_at"),
                ),
            )

    return analytics
