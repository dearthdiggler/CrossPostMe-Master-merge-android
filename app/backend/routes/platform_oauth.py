"""Platform OAuth Routes
FastAPI routes for handling marketplace platform OAuth integrations
"""

import logging
import os
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth import get_current_user
from db import get_db
from services.platform_oauth_service import PlatformOAuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/platforms", tags=["Platform OAuth"])


# Pydantic models for request/response
class OAuthInitRequest(BaseModel):
    platform: str = Field(
        ...,
        description="Platform name: facebook, ebay, offerup, craigslist",
    )
    redirect_uri: str = Field(..., description="Redirect URI after authorization")


class OAuthInitResponse(BaseModel):
    platform: str
    method: str  # 'oauth' or 'credentials'
    auth_url: str | None = None
    state: str | None = None
    form_url: str | None = None
    credentials_needed: list[str] | None = None
    instructions: str
    security_note: str | None = None


class OAuthCallbackRequest(BaseModel):
    platform: str
    code: str
    state: str


class CredentialsRequest(BaseModel):
    platform: str
    credentials: dict[str, str]


class PlatformResponse(BaseModel):
    success: bool
    platform: str
    message: str
    user_id: str | None = None


class ConnectedPlatform(BaseModel):
    platform: str
    type: str  # 'oauth' or 'credentials'
    status: str
    connected_at: datetime
    user_info: dict[str, Any] | None = None


def get_oauth_service(db=Depends(get_db)) -> PlatformOAuthService:
    """Dependency to get OAuth service instance"""
    return PlatformOAuthService(db)


@router.get("/supported", response_model=dict[str, Any])
async def get_supported_platforms():
    """Get list of supported platforms and their integration methods"""
    return {
        "platforms": {
            "facebook": {
                "name": "Facebook Marketplace",
                "method": "oauth",
                "description": "Connect your Facebook account to post to Marketplace",
                "features": ["Auto-posting", "Message management", "Analytics"],
                "oauth_available": True,
            },
            "ebay": {
                "name": "eBay",
                "method": "oauth",
                "description": "Connect your eBay seller account for listing management",
                "features": ["Auction listings", "Buy It Now", "Inventory sync"],
                "oauth_available": True,
            },
            "offerup": {
                "name": "OfferUp",
                "method": "credentials",
                "description": "Connect your OfferUp account for local marketplace posting",
                "features": ["Local listings", "Auto-posting", "Message management"],
                "oauth_available": False,
                "note": "Requires account credentials",
            },
            "craigslist": {
                "name": "Craigslist",
                "method": "credentials",
                "description": "Connect your Craigslist account for multi-city posting",
                "features": [
                    "Multi-city posting",
                    "Category management",
                    "Auto-renewal",
                ],
                "oauth_available": False,
                "note": "Requires account credentials",
            },
        },
    }


@router.post("/connect", response_model=OAuthInitResponse)
async def initiate_platform_connection(
    request: OAuthInitRequest,
    current_user: dict = Depends(get_current_user),
    oauth_service: PlatformOAuthService = Depends(get_oauth_service),
):
    """Initiate connection to a marketplace platform
    Returns OAuth URL for OAuth platforms or credential form for others
    """
    try:
        user_id = current_user["user_id"]

        result = await oauth_service.initiate_oauth_flow(
            platform=request.platform,
            user_id=user_id,
            redirect_uri=request.redirect_uri,
        )

        return OAuthInitResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error initiating platform connection for {request.platform}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate connection: {e!s}",
        ) from e


@router.post("/oauth/callback", response_model=PlatformResponse)
async def handle_oauth_callback(
    request: OAuthCallbackRequest,
    oauth_service: PlatformOAuthService = Depends(get_oauth_service),
):
    """Handle OAuth callback from marketplace platforms
    Exchange authorization code for access token
    """
    try:
        result = await oauth_service.handle_oauth_callback(
            platform=request.platform,
            code=request.code,
            state=request.state,
        )

        return PlatformResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error during OAuth callback for {request.platform}")
        raise HTTPException(
            status_code=500,
            detail=f"OAuth callback failed: {e!s}",
        ) from e


@router.post("/{platform}/credentials", response_model=PlatformResponse)
async def store_platform_credentials(
    platform: str,
    request: CredentialsRequest,
    current_user: dict = Depends(get_current_user),
    oauth_service: PlatformOAuthService = Depends(get_oauth_service),
):
    """Store platform credentials for non-OAuth platforms (OfferUp, Craigslist)"""
    if platform not in ["offerup", "craigslist"]:
        raise HTTPException(
            status_code=400,
            detail=f"Credential storage not supported for {platform}",
        )

    try:
        user_id = current_user["user_id"]

        result = await oauth_service.store_platform_credentials(
            user_id=user_id,
            platform=platform,
            credentials=request.credentials,
        )

        return PlatformResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error storing credentials for {platform}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to store credentials: {e!s}",
        ) from e


@router.get("/connected", response_model=list[ConnectedPlatform])
async def get_connected_platforms(
    current_user: dict = Depends(get_current_user),
    oauth_service: PlatformOAuthService = Depends(get_oauth_service),
):
    """Get all connected platforms for the current user"""
    try:
        user_id = current_user["user_id"]
        platforms = await oauth_service.get_user_platforms(user_id)

        return [ConnectedPlatform(**platform) for platform in platforms]

    except Exception as e:
        logger.exception("Error fetching connected platforms")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch platforms: {e!s}",
        ) from e


@router.delete("/{platform}/disconnect", response_model=PlatformResponse)
async def disconnect_platform(
    platform: str,
    current_user: dict = Depends(get_current_user),
    oauth_service: PlatformOAuthService = Depends(get_oauth_service),
):
    """Disconnect a platform from the user's account"""
    try:
        user_id = current_user["user_id"]

        result = await oauth_service.disconnect_platform(
            user_id=user_id,
            platform=platform,
        )

        return PlatformResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error disconnecting platform {platform}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to disconnect platform: {e!s}",
        ) from e


@router.get("/{platform}/status")
async def get_platform_status(
    platform: str,
    current_user: dict = Depends(get_current_user),
    oauth_service: PlatformOAuthService = Depends(get_oauth_service),
):
    """Get connection status for a specific platform"""
    try:
        user_id = current_user["user_id"]
        platforms = await oauth_service.get_user_platforms(user_id)

        platform_info = next((p for p in platforms if p["platform"] == platform), None)

        if platform_info:
            return {
                "platform": platform,
                "connected": True,
                "type": platform_info["type"],
                "status": platform_info["status"],
                "connected_at": platform_info["connected_at"],
            }
        return {"platform": platform, "connected": False, "status": "not_connected"}

    except Exception as e:
        logger.exception(f"Error checking platform status for {platform}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check platform status: {e!s}",
        ) from e


# Environment configuration endpoints (for development/testing)
@router.get("/config/oauth")
async def get_oauth_config():
    """Get OAuth configuration status (for debugging)"""
    config_status = {
        "facebook": {
            "client_id_set": bool(os.getenv("FACEBOOK_CLIENT_ID")),
            "client_secret_set": bool(os.getenv("FACEBOOK_CLIENT_SECRET")),
        },
        "ebay": {
            "client_id_set": bool(os.getenv("EBAY_CLIENT_ID")),
            "client_secret_set": bool(os.getenv("EBAY_CLIENT_SECRET")),
        },
    }

    return {
        "oauth_configs": config_status,
        "note": "Set environment variables for OAuth credentials",
    }
