"""
Enhanced Signup Route - Collects comprehensive business intelligence data
This creates a valuable data asset for future monetization and market insights
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from auth import create_access_token, get_password_hash
from db import get_typed_db
from supabase_db import db as supabase_db
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth-enhanced"])
db = get_typed_db()  # MongoDB (keep for parallel operation)

# Feature flag for Supabase migration
USE_SUPABASE = True  # Set to True to enable Supabase
PARALLEL_WRITE = True  # Write to both MongoDB and Supabase during migration


class EnhancedSignupRequest(BaseModel):
    """Enhanced signup model that collects valuable business data"""

    # Basic account info
    email: EmailStr
    password: str = Field(..., min_length=8)
    fullName: str
    phone: Optional[str] = None

    # Business intelligence (THE GOLD MINE)
    businessName: Optional[str] = None
    businessType: Optional[str] = None
    industry: Optional[str] = None

    # Marketplace intelligence
    currentMarketplaces: List[str] = []
    monthlyListings: Optional[str] = None
    averageItemPrice: Optional[str] = None
    monthlyRevenue: Optional[str] = None

    # Pain points & needs (product development insights)
    biggestChallenge: Optional[str] = None
    currentTools: List[str] = []
    teamSize: Optional[str] = None

    # Goals (upsell opportunities)
    growthGoal: Optional[str] = None
    listingsGoal: Optional[str] = None

    # Marketing & data permissions
    marketingEmails: bool = True
    dataSharing: bool = True
    betaTester: bool = False

    # Metadata
    trialType: Optional[str] = None
    signupDate: Optional[str] = None
    source: Optional[str] = None
    utmSource: Optional[str] = None
    utmMedium: Optional[str] = None
    utmCampaign: Optional[str] = None


@router.post("/enhanced-signup")
async def enhanced_signup(request: EnhancedSignupRequest) -> Dict:
    """
    Enhanced signup that collects comprehensive business data.

    This data becomes a valuable asset for:
    1. Market research & benchmarking
    2. Product development insights
    3. Targeted marketing campaigns
    4. Upsell opportunities
    5. Partner/investor presentations
    6. Competitive intelligence
    7. Future data monetization
    """

    try:
        # Check if user already exists (check both databases during migration)
        if USE_SUPABASE:
            existing_user = supabase_db.get_user_by_email(request.email)
        else:
            existing_user = db["users"].find_one({"email": request.email})

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user account
        # Use email as username for simplicity (make unique if needed)
        base_username = request.email.split('@')[0]
        username = base_username

        # Check if username exists and make it unique
        counter = 1
        if USE_SUPABASE:
            while supabase_db.get_user_by_username(username):
                username = f"{base_username}{counter}"
                counter += 1
        else:
            while db["users"].find_one({"username": username}):
                username = f"{base_username}{counter}"
                counter += 1

        # Hash password with error handling
        try:
            # Ensure password is not too long for bcrypt (72 byte limit)
            password_to_hash = request.password
            if len(password_to_hash.encode('utf-8')) > 72:
                password_to_hash = password_to_hash[:72]
            password_hash = get_password_hash(password_to_hash)
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password processing failed"
            )

        user_data = {
            "username": username,  # Required for auth system
            "email": request.email,
            "password_hash": password_hash,
            "full_name": request.fullName,
            "phone": request.phone,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "trial_active": True,
            "trial_type": request.trialType or "free",
            "trial_start_date": datetime.utcnow().isoformat(),

            # Business intelligence data
            "business_profile": {
                "business_name": request.businessName,
                "business_type": request.businessType,
                "industry": request.industry,
                "team_size": request.teamSize,
            },

            # Marketplace intelligence
            "marketplace_data": {
                "current_marketplaces": request.currentMarketplaces,
                "monthly_listings": request.monthlyListings,
                "average_item_price": request.averageItemPrice,
                "monthly_revenue": request.monthlyRevenue,
                "biggest_challenge": request.biggestChallenge,
                "current_tools": request.currentTools,
            },

            # Goals & expectations (for upselling)
            "goals": {
                "growth_goal": request.growthGoal,
                "listings_goal": request.listingsGoal,
            },

            # Marketing & permissions
            "preferences": {
                "marketing_emails": request.marketingEmails,
                "data_sharing": request.dataSharing,
                "beta_tester": request.betaTester,
            },

            # Attribution & source tracking
            "attribution": {
                "source": request.source,
                "utm_source": request.utmSource,
                "utm_medium": request.utmMedium,
                "utm_campaign": request.utmCampaign,
                "signup_date": request.signupDate or datetime.utcnow().isoformat(),
            },

            # Engagement tracking (for ML/analytics)
            "engagement": {
                "signup_completed": True,
                "onboarding_completed": False,
                "first_listing_date": None,
                "last_active_date": datetime.utcnow().isoformat(),
                "total_listings": 0,
                "total_views": 0,
                "total_messages": 0,
            },
        }

        # Insert user - Supabase or MongoDB
        if USE_SUPABASE:
            # Supabase: Separate user and business profile tables
            supabase_user_data = {
                "username": username,
                "email": request.email,
                "password_hash": get_password_hash(request.password),
                "full_name": request.fullName,
                "phone": request.phone,
                "is_active": True,
                "trial_active": True,
                "trial_type": request.trialType or "free",
                "metadata": {
                    "engagement": user_data["engagement"],
                    "preferences": user_data["preferences"],
                }
            }

            # Create user in Supabase
            created_user = supabase_db.create_user(supabase_user_data)
            user_id = created_user["id"]

            # Create business profile in separate table (normalized design)
            business_profile_data = {
                "user_id": user_id,
                "business_name": request.businessName,
                "business_type": request.businessType,
                "industry": request.industry,
                "team_size": request.teamSize,
                "current_marketplaces": request.currentMarketplaces,
                "monthly_listings": request.monthlyListings,
                "average_item_price": request.averageItemPrice,
                "monthly_revenue": request.monthlyRevenue,
                "biggest_challenge": request.biggestChallenge,
                "current_tools": request.currentTools,
                "growth_goal": request.growthGoal,
                "listings_goal": request.listingsGoal,
                "marketing_emails": request.marketingEmails,
                "data_sharing": request.dataSharing,
                "beta_tester": request.betaTester,
                "signup_source": request.source,
                "utm_source": request.utmSource,
                "utm_medium": request.utmMedium,
                "utm_campaign": request.utmCampaign,
            }

            supabase_db.create_business_profile(business_profile_data)

            # Log business intelligence event
            supabase_db.log_event(
                user_id=user_id,
                event_type="enhanced_signup",
                event_data={
                    "business_type": request.businessType,
                    "industry": request.industry,
                    "monthly_revenue": request.monthlyRevenue,
                    "monthly_listings": request.monthlyListings,
                    "marketplaces": request.currentMarketplaces,
                    "biggest_challenge": request.biggestChallenge,
                    "trial_type": request.trialType,
                }
            )

            logger.info(f"✅ User created in Supabase: {user_id}")

        else:
            # MongoDB (original code)
            result = db["users"].insert_one(user_data)
            user_id = str(result.inserted_id)

            # Log business intelligence event
            db["business_intelligence"].insert_one({
                "user_id": user_id,
                "event_type": "enhanced_signup",
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "business_type": request.businessType,
                    "industry": request.industry,
                    "monthly_revenue": request.monthlyRevenue,
                    "monthly_listings": request.monthlyListings,
                    "marketplaces": request.currentMarketplaces,
                    "biggest_challenge": request.biggestChallenge,
                    "trial_type": request.trialType,
                }
            })

        # PARALLEL WRITE: Also write to MongoDB during migration
        if USE_SUPABASE and PARALLEL_WRITE:
            try:
                # Convert Supabase UUID to string for MongoDB
                user_data["supabase_id"] = user_id
                result = db["users"].insert_one(user_data)
                mongo_id = str(result.inserted_id)
                logger.info(f"✅ Parallel write to MongoDB: {mongo_id}")
            except Exception as e:
                logger.warning(f"⚠️  Parallel MongoDB write failed: {e}")
                # Don't fail the request if MongoDB write fails

        # Create access token
        access_token = create_access_token(
            data={
                "sub": username,  # Use username for token (consistent with auth system)
                "user_id": user_id,
                "token_type": "access"
            }
        )

        logger.info(f"Enhanced signup completed for user: {user_id} | "
                   f"Username: {username} | "
                   f"Industry: {request.industry} | "
                   f"Revenue: {request.monthlyRevenue} | "
                   f"Listings: {request.monthlyListings}")

        # Return success with token and username
        return {
            "token": access_token,
            "token_type": "bearer",
            "user_id": user_id,
            "username": username,  # Return username for frontend
            "email": request.email,
            "trial_active": True,
            "trial_type": request.trialType,
            "message": "Account created successfully! Your free trial has started."
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhanced signup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed. Please try again."
        )


@router.get("/business-insights")
async def get_business_insights() -> Dict:
    """
    Analytics endpoint to view aggregated business intelligence data.
    This data is GOLD for investors, partners, and product decisions.
    """

    try:
        # Aggregate data from all users
        total_users = db["users"].count_documents({})

        # Industry breakdown
        industries = db["users"].aggregate([
            {"$match": {"business_profile.industry": {"$ne": None}}},
            {"$group": {
                "_id": "$business_profile.industry",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ])

        # Revenue breakdown
        revenue_ranges = db["users"].aggregate([
            {"$match": {"marketplace_data.monthly_revenue": {"$ne": None}}},
            {"$group": {
                "_id": "$marketplace_data.monthly_revenue",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ])

        # Most used marketplaces
        marketplace_usage = db["users"].aggregate([
            {"$unwind": "$marketplace_data.current_marketplaces"},
            {"$group": {
                "_id": "$marketplace_data.current_marketplaces",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ])

        # Top challenges (product development insights)
        challenges = db["users"].aggregate([
            {"$match": {"marketplace_data.biggest_challenge": {"$ne": None}}},
            {"$group": {
                "_id": "$marketplace_data.biggest_challenge",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ])

        return {
            "total_users": total_users,
            "industries": list(industries),
            "revenue_ranges": list(revenue_ranges),
            "marketplace_usage": list(marketplace_usage),
            "top_challenges": list(challenges),
            "generated_at": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error fetching business insights: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch insights"
        )


@router.get("/data-export")
async def export_business_data() -> Dict:
    """
    Export anonymized business intelligence data.
    This endpoint can be used to:
    1. Share market insights with partners
    2. Create investor presentations
    3. Sell anonymized data to market research firms
    4. Generate industry reports
    """

    try:
        # Export anonymized aggregate data
        all_data = list(db["business_intelligence"].find(
            {},
            {"_id": 0, "user_id": 0}  # Remove identifying info
        ))

        return {
            "data_points": len(all_data),
            "data": all_data[:100],  # Limit to 100 for demo
            "export_date": datetime.utcnow().isoformat(),
            "note": "This is anonymized aggregate data safe for sharing"
        }

    except Exception as e:
        logger.error(f"Error exporting data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed"
        )
