import math
import os
import random
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from models import (
    Ad,
    AdAnalytics,
    AdCreate,
    AdUpdate,
    DashboardStats,
    PaginatedAdsResponse,
    PaginatedPostedAdsResponse,
    PaginationInfo,
    PostedAd,
    PostedAdCreate,
)
from routes.dependencies import get_current_user, get_db, rate_limit_dependency
from services.diagram import generate_ad_mermaid

router = APIRouter(prefix="/api/ads", tags=["ads"])


# Create Ad
@router.post("/", response_model=Ad)
async def create_ad(
    ad: AdCreate,
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
):
    ad_dict = ad.dict()
    # attach owner if authenticated
    if current_user:
        ad_dict["owner_id"] = current_user
    ad_obj = Ad(**ad_dict)
    await database.ads.insert_one(ad_obj.dict())
    return ad_obj


# Get All Ads with Pagination
@router.get("/", response_model=PaginatedAdsResponse)
async def get_ads(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str = Query(None, description="Filter by status"),
    platform: str = Query(None, description="Filter by platform"),
    database=Depends(get_db),
):
    query = {}
    if status:
        query["status"] = status
    if platform:
        query["platforms"] = platform

    # Calculate pagination
    skip = (page - 1) * per_page
    total_items = await database.ads.count_documents(query)
    total_pages = math.ceil(total_items / per_page)

    # Get paginated results
    ads = (
        await database.ads.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(per_page)
        .to_list(per_page)
    )

    # Create pagination info
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedAdsResponse(items=[Ad(**ad) for ad in ads], pagination=pagination)


# Get Ad by ID
@router.get("/{ad_id}", response_model=Ad)
async def get_ad(ad_id: str, database=Depends(get_db)):
    ad = await database.ads.find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return Ad(**ad)


# Update Ad
@router.put("/{ad_id}", response_model=Ad)
async def update_ad(
    ad_id: str,
    ad_update: AdUpdate,
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
):
    ad = await database.ads.find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    # ownership check
    if ad.get("owner_id") and current_user != ad.get("owner_id"):
        raise HTTPException(status_code=403, detail="Not authorized to update this ad")

    update_data = ad_update.dict(exclude_unset=True)
    if update_data:
        await database.ads.update_one({"id": ad_id}, {"$set": update_data})

    updated_ad = await database.ads.find_one({"id": ad_id})
    return Ad(**updated_ad)


# Delete Ad
@router.delete("/{ad_id}")
async def delete_ad(
    ad_id: str,
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
):
    ad = await database.ads.find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.get("owner_id") and current_user != ad.get("owner_id"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this ad")
    result = await database.ads.delete_one({"id": ad_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Ad not found")
    return {"message": "Ad deleted successfully"}


# Post Ad to Platform
@router.post("/{ad_id}/post", response_model=PostedAd)
async def post_ad(
    ad_id: str,
    platform: str,
    posted: Optional[PostedAdCreate] = None,
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
):
    ad = await database.ads.find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    # ownership check: only owner can post
    if ad.get("owner_id") and current_user != ad.get("owner_id"):
        raise HTTPException(status_code=403, detail="Not authorized to post this ad")

    # Simulate posting to platform
    posted_ad_dict = {
        "ad_id": ad_id,
        "platform": platform,
        "platform_ad_id": f"{platform}_{random.randint(100000, 999999)}",
        "post_url": f"https://{platform}.com/listing/{random.randint(100000, 999999)}",
        "metrics": {},
    }
    # merge provided posted metrics if present
    if posted and posted.metrics:
        posted_ad_dict["metrics"].update(posted.metrics)

    posted_ad = PostedAd(**posted_ad_dict)
    await database.posted_ads.insert_one(posted_ad.dict())

    # Update ad status
    await database.ads.update_one({"id": ad_id}, {"$set": {"status": "posted"}})

    return posted_ad


# List ads for a specific user
@router.get("/user/{user_id}/ads", response_model=List[Ad])
async def get_user_ads(
    user_id: str,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
):
    # allow only the user or admin (no admin support yet) to list
    if current_user != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these ads")
    skip = (page - 1) * per_page
    ads = (
        await database.ads.find({"owner_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(per_page)
        .to_list(per_page)
    )
    return [Ad(**a) for a in ads]


# Generate diagrams for all ads owned by a user
@router.get("/user/{user_id}/diagrams")
async def get_user_diagrams(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number for diagrams"),
    per_page: int = Query(25, ge=1, le=100, description="Diagrams per page"),
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
    _rl=Depends(rate_limit_dependency(capacity=10, per_seconds=60)),
):
    if current_user != user_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to view these diagrams"
        )

    # Pagination/safety: cap total ads processed per request
    MAX_ADS_PER_REQUEST = 500
    skip = (page - 1) * per_page
    limit = min(per_page, MAX_ADS_PER_REQUEST)
    ads = (
        await database.ads.find({"owner_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
        .to_list(limit)
    )
    if not ads:
        return {}

    # Batch fetch all posted_ads for these ads in a single query to avoid N+1
    ad_ids = [a.get("id") for a in ads if a.get("id")]
    posted_cursor = database.posted_ads.find({"ad_id": {"$in": ad_ids}})
    posted_list = await posted_cursor.to_list(length=2000)

    # Group posted ads by ad_id
    from collections import defaultdict

    posted_by_ad = defaultdict(list)
    for pa in posted_list:
        posted_by_ad[pa.get("ad_id")].append(pa)

    # Generate diagrams concurrently for responsiveness
    import asyncio

    async def make_diagram(ad):
        pid = ad.get("id")
        posted = posted_by_ad.get(pid, [])
        # generate_ad_mermaid is CPU/lightweight; if it becomes heavy consider offloading
        return pid, generate_ad_mermaid(ad, posted)

    tasks = [make_diagram(a) for a in ads]
    results = await asyncio.gather(*tasks)

    diagrams = {pid: mer for pid, mer in results}
    return diagrams


# Render Mermaid to SVG (requires `mmdc` to be installed and available in PATH)
@router.post("/render/svg")
async def render_mermaid_svg(mermaid_text: str):
    import asyncio
    import shutil
    import tempfile

    mmdc = shutil.which("mmdc")
    if not mmdc:
        raise HTTPException(
            status_code=501,
            detail="Mermaid CLI (mmdc) not installed on server. Install it to use SVG rendering.",
        )

    # Enforce a mermaid_text size limit to avoid resource exhaustion
    MAX_INPUT_SIZE = 32 * 1024  # 32 KB
    if (
        not isinstance(mermaid_text, str)
        or len(mermaid_text.encode("utf-8")) > MAX_INPUT_SIZE
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Mermaid input too large (max {MAX_INPUT_SIZE} bytes)",
        )

    # Use asyncio subprocess to avoid blocking the event loop and apply a timeout
    src = None
    dst = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_text)
            src = f.name
        dst = src + ".svg"

        proc = await asyncio.create_subprocess_exec(mmdc, "-i", src, "-o", dst)

        try:
            await asyncio.wait_for(proc.wait(), timeout=10)
        except asyncio.TimeoutError:
            proc.kill()
            raise HTTPException(status_code=504, detail="SVG rendering timed out")

        if proc.returncode != 0:
            raise HTTPException(
                status_code=500, detail="Mermaid CLI failed to render SVG"
            )

        # Read resulting file safely
        loop = asyncio.get_running_loop()
        with open(dst, "rb") as svgf:
            data = await loop.run_in_executor(None, svgf.read)

        return Response(content=data, media_type="image/svg+xml")

    finally:
        # Best-effort cleanup
        try:
            if src and os.path.exists(src):
                os.remove(src)
            if dst and os.path.exists(dst):
                os.remove(dst)
        except Exception:
            pass


# Get Posted Ads with Pagination
@router.get("/{ad_id}/posts", response_model=PaginatedPostedAdsResponse)
async def get_posted_ads(
    ad_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    database=Depends(get_db),
):
    # Calculate pagination
    skip = (page - 1) * per_page
    query = {"ad_id": ad_id}
    total_items = await database.posted_ads.count_documents(query)
    total_pages = math.ceil(total_items / per_page)

    # Get paginated results
    posted_ads = (
        await database.posted_ads.find(query)
        .sort("posted_at", -1)
        .skip(skip)
        .limit(per_page)
        .to_list(per_page)
    )

    # Create pagination info
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedPostedAdsResponse(
        items=[PostedAd(**pa) for pa in posted_ads], pagination=pagination
    )


# Get All Posted Ads with Pagination
@router.get("/posted/all", response_model=PaginatedPostedAdsResponse)
async def get_all_posted_ads(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    platform: str = Query(None, description="Filter by platform"),
    database=Depends(get_db),
):
    query = {}
    if platform:
        query["platform"] = platform

    # Calculate pagination
    skip = (page - 1) * per_page
    total_items = await database.posted_ads.count_documents(query)
    total_pages = math.ceil(total_items / per_page)

    # Get paginated results
    posted_ads = (
        await database.posted_ads.find(query)
        .sort("posted_at", -1)
        .skip(skip)
        .limit(per_page)
        .to_list(per_page)
    )

    # Create pagination info
    pagination = PaginationInfo(
        page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1,
    )

    return PaginatedPostedAdsResponse(
        items=[PostedAd(**pa) for pa in posted_ads], pagination=pagination
    )


# Get Dashboard Stats
@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(database=Depends(get_db)):
    total_ads = await database.ads.count_documents({})
    active_ads = await database.ads.count_documents({"status": "posted"})
    total_posts = await database.posted_ads.count_documents({})

    # Calculate total views and leads
    posted_ads = await database.posted_ads.find({}).to_list(1000)
    total_views = sum(pa.get("views", 0) for pa in posted_ads)
    total_leads = sum(pa.get("leads", 0) for pa in posted_ads)

    # Count unique platforms
    platforms = await database.platform_accounts.distinct("platform")
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
@router.get("/{ad_id}/analytics", response_model=List[AdAnalytics])
async def get_ad_analytics(ad_id: str, days: int = 7, database=Depends(get_db)):
    """
    Get analytics for a specific ad over the specified time period.

    **Note: Analytics data are simulated/generated for demonstration purposes.**
    The following fields contain synthetic data and do not represent real metrics:
    - views: Randomly generated between 50-500
    - clicks: Randomly generated between 10-100
    - leads: Randomly generated between 1-20
    - messages: Randomly generated between 1-15
    - conversion_rate: Randomly generated between 2.0-8.0%

    Only the ad_id, platform, and date fields reflect actual posting data.
    """
    # First check if the ad exists
    ad = await database.ads.find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")

    start_date = datetime.utcnow() - timedelta(days=days)

    posted_ads = await database.posted_ads.find(
        {"ad_id": ad_id, "posted_at": {"$gte": start_date}}
    ).to_list(1000)

    analytics = []
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
            )
        )

    return analytics


# Get Mermaid diagram for an ad
@router.get("/{ad_id}/diagram", response_model=str)
async def get_ad_diagram(
    ad_id: str,
    current_user: Optional[str] = Depends(get_current_user),
    database=Depends(get_db),
):
    # Verify ad exists
    ad = await database.ads.find_one({"id": ad_id})
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.get("owner_id") and current_user != ad.get("owner_id"):
        raise HTTPException(
            status_code=403, detail="Not authorized to view this diagram"
        )

    # Get recent posted_ads for the ad (limit to 1000)
    posted_ads = await database.posted_ads.find({"ad_id": ad_id}).to_list(1000)

    mermaid = generate_ad_mermaid(ad, posted_ads)

    # Return raw Mermaid markdown (caller can wrap in triple backticks if needed)
    return mermaid
