import logging
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth import get_optional_current_user
from db import get_typed_db
from models import PlatformAccount, PlatformAccountCreate

# Import datetime helpers from ads module
from .ads import deserialize_datetime_fields, serialize_datetime_fields

# Feature flags
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

logger = logging.getLogger("platforms")

router = APIRouter(prefix="/api/platforms", tags=["platforms"])


# Request models for credential management
class PlatformCredentialsRequest(BaseModel):
    platform: str
    username: str
    password: str
    email: str | None = None
    phone: str | None = None
    additional_data: dict[str, str] | None = None


class CredentialTestRequest(BaseModel):
    platform: str
    username: str
    password: str
    additional_data: dict[str, str] | None = None


db = get_typed_db()


# Create Platform Account
@router.post("/accounts", response_model=PlatformAccount)
async def create_platform_account(
    account: PlatformAccountCreate,
    user_id: str = Depends(get_optional_current_user),
) -> PlatformAccount:
    account_dict = account.model_dump()
    account_dict["user_id"] = user_id  # Add user_id for multi-tenant support
    account_obj = PlatformAccount(**account_dict)

    # Serialize datetime fields for MongoDB storage
    doc = account_obj.model_dump()
    serialize_datetime_fields(doc, ["created_at", "last_used"])

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Insert into platform_connections table
                connection_data = {
                    "user_id": user_id,
                    "platform": account.platform,
                    "platform_user_id": account.account_name,  # Use account_name as platform_user_id
                    "is_active": True,
                    "metadata": {
                        "account_email": account.account_email,
                        "status": "active",
                        "created_at": doc.get("created_at"),
                        "last_used": doc.get("last_used")
                    }
                }
                result = client.table("platform_connections").insert(connection_data).execute()
                logger.info(f"Platform connection created in Supabase: {account.platform} for user {user_id}")

                # PARALLEL WRITE: Also write to MongoDB
                if PARALLEL_WRITE:
                    try:
                        await db["platform_accounts"].insert_one(doc)
                        logger.info(f"✅ Parallel write to MongoDB successful for platform account: {account.platform}")
                    except Exception as e:
                        logger.warning(f"⚠️  Parallel MongoDB write failed for platform account {account.platform}: {e}")
        except Exception as e:
            logger.error(f"Platform account creation failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to create platform account")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        await db["platform_accounts"].insert_one(doc)
        logger.info(f"Platform account created in MongoDB: {account.platform} for user {user_id}")

    return account_obj


# Get All Platform Accounts
@router.get("/accounts", response_model=list[PlatformAccount])
async def get_platform_accounts(
    platform: str | None = None,
    user_id: str = Depends(get_optional_current_user),
) -> list[PlatformAccount]:
    accounts = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                query = client.table("platform_connections").select("*").eq("user_id", user_id).eq("is_active", True)

                if platform:
                    query = query.eq("platform", platform)

                query = query.order("created_at", desc=True)
                result = query.execute()

                # Convert Supabase platform_connections to PlatformAccount format
                for conn in result.data:
                    metadata = conn.get("metadata", {})
                    account_data = {
                        "id": conn["id"],
                        "user_id": conn["user_id"],
                        "platform": conn["platform"],
                        "account_name": conn.get("platform_user_id", ""),
                        "account_email": metadata.get("account_email", ""),
                        "status": "active" if conn.get("is_active", True) else "inactive",
                        "created_at": conn.get("created_at"),
                        "last_used": metadata.get("last_used"),
                    }
                    deserialize_datetime_fields(account_data, ["created_at", "last_used"])
                    accounts.append(PlatformAccount(**account_data))

                logger.info(f"Fetched {len(accounts)} platform accounts from Supabase for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to fetch platform accounts from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch platform accounts")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        query: dict[str, Any] = {"user_id": user_id}  # Scope by user for security
        if platform:
            query["platform"] = platform

        accounts_docs = await db["platform_accounts"].find(query, {"_id": 0}).to_list(1000)

        # Convert ISO string timestamps back to datetime objects
        for account in accounts_docs:
            deserialize_datetime_fields(account, ["created_at", "last_used"])
            accounts.append(PlatformAccount(**account))

    return accounts


# Get Platform Account by ID
@router.get("/accounts/{account_id}", response_model=PlatformAccount)
async def get_platform_account(
    account_id: str,
    user_id: str = Depends(get_optional_current_user),
) -> PlatformAccount:
    account = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                result = client.table("platform_connections").select("*").eq("id", account_id).eq("user_id", user_id).execute()
                if result.data and len(result.data) > 0:
                    conn = result.data[0]
                    metadata = conn.get("metadata", {})
                    account_data = {
                        "id": conn["id"],
                        "user_id": conn["user_id"],
                        "platform": conn["platform"],
                        "account_name": conn.get("platform_user_id", ""),
                        "account_email": metadata.get("account_email", ""),
                        "status": "active" if conn.get("is_active", True) else "inactive",
                        "created_at": conn.get("created_at"),
                        "last_used": metadata.get("last_used"),
                    }
                    account = PlatformAccount(**account_data)
                    logger.info(f"Fetched platform account from Supabase: {account_id}")
        except Exception as e:
            logger.error(f"Failed to fetch platform account from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch platform account")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        account_doc = await db["platform_accounts"].find_one(
            {"id": account_id, "user_id": user_id},
            {"_id": 0},
        )
        if account_doc:
            account = PlatformAccount(**account_doc)
            logger.info(f"Fetched platform account from MongoDB: {account_id}")

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


# Update Platform Account Status
@router.put("/accounts/{account_id}/status")
async def update_account_status(
    account_id: str,
    status: str,
    user_id: str = Depends(get_optional_current_user),
) -> PlatformAccount:
    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Update is_active based on status
                is_active = status == "active"
                update_data = {
                    "is_active": is_active,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }

                # Also update metadata status
                current_conn = client.table("platform_connections").select("metadata").eq("id", account_id).eq("user_id", user_id).execute()
                if current_conn.data:
                    metadata = current_conn.data[0].get("metadata", {})
                    metadata["status"] = status
                    update_data["metadata"] = metadata

                result = client.table("platform_connections").update(update_data).eq("id", account_id).eq("user_id", user_id).execute()

                if result.data and len(result.data) > 0:
                    conn = result.data[0]
                    metadata = conn.get("metadata", {})
                    account_data = {
                        "id": conn["id"],
                        "user_id": conn["user_id"],
                        "platform": conn["platform"],
                        "account_name": conn.get("platform_user_id", ""),
                        "account_email": metadata.get("account_email", ""),
                        "status": status,
                        "created_at": conn.get("created_at"),
                        "last_used": metadata.get("last_used"),
                    }
                    updated_account = PlatformAccount(**account_data)
                    logger.info(f"Updated platform account status in Supabase: {account_id} to {status}")

                    # PARALLEL WRITE: Also update in MongoDB
                    if PARALLEL_WRITE:
                        try:
                            await db["platform_accounts"].update_one(
                                {"id": account_id, "user_id": user_id},
                                {"$set": {"status": status}},
                            )
                            logger.info(f"✅ Parallel write to MongoDB successful for account status update: {account_id}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for account status update {account_id}: {e}")

                    return updated_account
                else:
                    raise HTTPException(status_code=404, detail="Account not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Account status update failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to update account status")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        account = await db["platform_accounts"].find_one(
            {"id": account_id, "user_id": user_id},
            {"_id": 0},
        )
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        await db["platform_accounts"].update_one(
            {"id": account_id, "user_id": user_id},
            {"$set": {"status": status}},
        )

        updated_account_doc = await db["platform_accounts"].find_one(
            {"id": account_id, "user_id": user_id},
            {"_id": 0},
        )

        # Convert ISO string timestamps back to datetime objects
        deserialize_datetime_fields(updated_account_doc, ["created_at", "last_used"])

        return PlatformAccount(**updated_account_doc)


# Delete Platform Account
@router.delete("/accounts/{account_id}")
async def delete_platform_account(
    account_id: str,
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, str]:
    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Soft delete by setting is_active=false
                update_data = {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                result = client.table("platform_connections").update(update_data).eq("id", account_id).eq("user_id", user_id).execute()

                if result.data and len(result.data) > 0:
                    logger.info(f"Soft-deleted platform account in Supabase: {account_id}")

                    # PARALLEL WRITE: Also soft-delete in MongoDB
                    if PARALLEL_WRITE:
                        try:
                            await db["platform_accounts"].update_one(
                                {"id": account_id, "user_id": user_id},
                                {"$set": {"status": "inactive"}},
                            )
                            logger.info(f"✅ Parallel write to MongoDB successful for account deletion: {account_id}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for account deletion {account_id}: {e}")

                    return {"message": "Account deleted successfully"}
                else:
                    raise HTTPException(status_code=404, detail="Account not found")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Account deletion failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail="Failed to delete account")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        result = await db["platform_accounts"].delete_one(
            {"id": account_id, "user_id": user_id},
        )
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Account not found")
        return {"message": "Account deleted successfully"}


# Get Available Platforms
@router.get("/available")
async def get_available_platforms() -> list[dict[str, str]]:
    return [
        {
            "id": "facebook",
            "name": "Facebook Marketplace",
            "icon": "facebook",
            "description": "Post to Facebook Marketplace with 1B+ users",
        },
        {
            "id": "craigslist",
            "name": "Craigslist",
            "icon": "list",
            "description": "Reach local buyers on America's #1 classifieds site",
        },
        {
            "id": "offerup",
            "name": "OfferUp",
            "icon": "shopping-bag",
            "description": "Mobile-first marketplace with 20M+ monthly users",
        },
        {
            "id": "ebay",
            "name": "eBay",
            "icon": "shopping-cart",
            "description": "World's largest online marketplace with global reach",
        },
        {
            "id": "whatnot",
            "name": "Whatnot",
            "icon": "zap",
            "description": "Live shopping and auctions for collectibles, sneakers, and more",
        },
        {
            "id": "nextdoor",
            "name": "Nextdoor",
            "icon": "map-pin",
            "description": "Neighborhood marketplace for local buying and selling",
        },
    ]


# Store Platform Credentials (Secure)
@router.post("/credentials")
async def store_platform_credentials(
    credentials_request: PlatformCredentialsRequest,
    user_id: str = "default",  # In production, get from JWT token
) -> dict[str, Any]:
    """Store encrypted platform credentials for a user"""
    try:
        from ..automation.base import PlatformCredentials
        from ..automation.credentials import credential_manager

        credentials = PlatformCredentials(
            username=credentials_request.username,
            password=credentials_request.password,
            email=credentials_request.email,
            phone=credentials_request.phone,
            additional_data=credentials_request.additional_data,
        )

        success = await credential_manager.store_credentials(
            user_id,
            credentials_request.platform,
            credentials,
        )

        if success:
            # Also create/update the platform account record
            account_obj = PlatformAccount(
                platform=credentials_request.platform,
                account_name=credentials_request.username,
                account_email=credentials_request.email or credentials_request.username,
                status="active",
                user_id=user_id,  # Add user_id for multi-tenant support
            )

            # Serialize datetime fields for MongoDB storage
            doc = account_obj.model_dump()
            serialize_datetime_fields(doc, ["created_at", "last_used"])

            await db["platform_accounts"].update_one(
                {
                    "platform": credentials_request.platform,
                    "account_email": account_obj.account_email,
                    "user_id": user_id,
                },
                {"$set": doc},
                upsert=True,
            )

            return {
                "success": True,
                "message": f"Credentials stored for {credentials_request.platform}",
                "platform": credentials_request.platform,
            }
        raise HTTPException(status_code=500, detail="Failed to store credentials")
    except Exception as e:
        logger.exception("Error storing platform credentials")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Test Platform Credentials
@router.post("/test-credentials")
async def test_platform_credentials(
    test_request: CredentialTestRequest,
    user_id: str = "default",
) -> dict[str, Any]:
    """Test platform credentials by attempting authentication"""
    try:
        from ..automation import automation_manager
        from ..automation.base import PlatformCredentials

        if test_request.platform not in automation_manager.platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Platform {test_request.platform} not supported",
            )

        credentials = PlatformCredentials(
            username=test_request.username,
            password=test_request.password,
            additional_data=test_request.additional_data,
        )

        platform = automation_manager.platforms[test_request.platform]
        is_valid = await platform.validate_credentials(credentials)

        return {
            "success": is_valid,
            "platform": test_request.platform,
            "message": "Credentials valid" if is_valid else "Credentials invalid",
        }
    except Exception as e:
        return {
            "success": False,
            "platform": test_request.platform,
            "message": f"Error testing credentials: {e!s}",
        }


# Get User's Platform Status
@router.get("/status/{user_id}")
async def get_user_platform_status(user_id: str = "default") -> dict[str, Any]:
    """Get the status of all platforms for a user"""
    try:
        from ..automation.credentials import credential_manager

        platforms = await credential_manager.list_user_platforms(user_id)

        platform_status = []
        for platform in platforms:
            is_valid = await credential_manager.validate_platform_credentials(
                user_id,
                platform,
            )
            platform_status.append(
                {
                    "platform": platform,
                    "has_credentials": True,
                    "credentials_valid": is_valid,
                    "status": "active" if is_valid else "needs_attention",
                },
            )

        return {
            "user_id": user_id,
            "platforms": platform_status,
            "total_platforms": len(platform_status),
            "active_platforms": sum(
                1 for p in platform_status if p["credentials_valid"]
            ),
        }
    except Exception as e:
        logger.exception(f"Error getting platform status for user {user_id}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Get Connected Platforms (Main Route)
@router.get("/")
async def get_connected_platforms(
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Get all platforms connected by the user."""
    platforms = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                result = client.table("platform_connections").select("*").eq("user_id", user_id).eq("is_active", True).execute()

                for conn in result.data:
                    platform_data = {
                        "id": conn["platform"],
                        "name": conn["platform"].title(),
                        "connected": True,
                        "connection_id": conn["id"],
                        "platform_user_id": conn.get("platform_user_id"),
                        "last_sync": conn.get("last_sync"),
                        "status": "active" if conn.get("is_active", True) else "inactive"
                    }
                    platforms.append(platform_data)

                logger.info(f"Fetched {len(platforms)} connected platforms from Supabase for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to fetch connected platforms from Supabase: {e}")
            raise HTTPException(status_code=500, detail="Failed to fetch connected platforms")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        accounts_docs = await db["platform_accounts"].find(
            {"user_id": user_id, "status": "active"},
            {"_id": 0}
        ).to_list(1000)

        for account in accounts_docs:
            platform_data = {
                "id": account["platform"],
                "name": account["platform"].title(),
                "connected": True,
                "connection_id": account["id"],
                "platform_user_id": account.get("account_name"),
                "last_sync": account.get("last_used"),
                "status": account.get("status", "active")
            }
            platforms.append(platform_data)

    return {
        "platforms": platforms,
        "total_connected": len(platforms)
    }


# Connect Platform (OAuth Flow Placeholder)
@router.post("/{platform}/connect")
async def connect_platform(
    platform: str,
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Initiate OAuth connection for a platform."""
    # This is a placeholder for OAuth flow
    # In production, this would redirect to platform's OAuth URL

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Check if connection already exists
                existing = client.table("platform_connections").select("*").eq("user_id", user_id).eq("platform", platform).execute()

                if existing.data:
                    # Update existing connection
                    update_data = {
                        "is_active": True,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                    client.table("platform_connections").update(update_data).eq("user_id", user_id).eq("platform", platform).execute()
                    connection_id = existing.data[0]["id"]
                else:
                    # Create new connection
                    connection_data = {
                        "user_id": user_id,
                        "platform": platform,
                        "is_active": True,
                        "metadata": {"status": "connecting"}
                    }
                    result = client.table("platform_connections").insert(connection_data).execute()
                    connection_id = result.data[0]["id"]

                logger.info(f"Platform connection initiated in Supabase: {platform} for user {user_id}")

                # PARALLEL WRITE: Also update/create in MongoDB
                if PARALLEL_WRITE:
                    try:
                        account_data = {
                            "id": connection_id,
                            "user_id": user_id,
                            "platform": platform,
                            "account_name": f"{platform}_user",
                            "account_email": f"user@{platform}.com",
                            "status": "active"
                        }
                        await db["platform_accounts"].update_one(
                            {"user_id": user_id, "platform": platform},
                            {"$set": account_data},
                            upsert=True
                        )
                        logger.info(f"✅ Parallel write to MongoDB successful for platform connect: {platform}")
                    except Exception as e:
                        logger.warning(f"⚠️  Parallel MongoDB write failed for platform connect {platform}: {e}")

                return {
                    "success": True,
                    "platform": platform,
                    "connection_id": connection_id,
                    "status": "connecting",
                    "message": f"OAuth flow initiated for {platform}. In production, this would redirect to {platform}'s authorization URL."
                }
        except Exception as e:
            logger.error(f"Platform connection failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail=f"Failed to connect {platform}")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        # Create/update platform account
        account_data = {
            "user_id": user_id,
            "platform": platform,
            "account_name": f"{platform}_user",
            "account_email": f"user@{platform}.com",
            "status": "active"
        }
        await db["platform_accounts"].update_one(
            {"user_id": user_id, "platform": platform},
            {"$set": account_data},
            upsert=True
        )

        return {
            "success": True,
            "platform": platform,
            "status": "connected",
            "message": f"Connected to {platform} (MongoDB fallback)"
        }


# Disconnect Platform
@router.post("/{platform}/disconnect")
async def disconnect_platform(
    platform: str,
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Disconnect a platform."""

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Soft disconnect by setting is_active=false
                update_data = {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                result = client.table("platform_connections").update(update_data).eq("user_id", user_id).eq("platform", platform).execute()

                if result.data and len(result.data) > 0:
                    logger.info(f"Platform disconnected in Supabase: {platform} for user {user_id}")

                    # PARALLEL WRITE: Also disconnect in MongoDB
                    if PARALLEL_WRITE:
                        try:
                            await db["platform_accounts"].update_one(
                                {"user_id": user_id, "platform": platform},
                                {"$set": {"status": "inactive"}},
                            )
                            logger.info(f"✅ Parallel write to MongoDB successful for platform disconnect: {platform}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for platform disconnect {platform}: {e}")

                    return {
                        "success": True,
                        "platform": platform,
                        "status": "disconnected",
                        "message": f"Successfully disconnected from {platform}"
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"No connection found for {platform}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Platform disconnect failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail=f"Failed to disconnect {platform}")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        result = await db["platform_accounts"].update_one(
            {"user_id": user_id, "platform": platform},
            {"$set": {"status": "inactive"}},
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"No connection found for {platform}")

        return {
            "success": True,
            "platform": platform,
            "status": "disconnected",
            "message": f"Successfully disconnected from {platform}"
        }


# Sync Platform Data
@router.post("/{platform}/sync")
async def sync_platform_data(
    platform: str,
    user_id: str = Depends(get_optional_current_user),
) -> dict[str, Any]:
    """Sync data from a connected platform."""

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                # Update last_sync timestamp
                update_data = {
                    "last_sync": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                result = client.table("platform_connections").update(update_data).eq("user_id", user_id).eq("platform", platform).execute()

                if result.data and len(result.data) > 0:
                    logger.info(f"Platform sync initiated in Supabase: {platform} for user {user_id}")

                    # PARALLEL WRITE: Also update in MongoDB
                    if PARALLEL_WRITE:
                        try:
                            await db["platform_accounts"].update_one(
                                {"user_id": user_id, "platform": platform},
                                {"$set": {"last_used": datetime.now(timezone.utc)}},
                            )
                            logger.info(f"✅ Parallel write to MongoDB successful for platform sync: {platform}")
                        except Exception as e:
                            logger.warning(f"⚠️  Parallel MongoDB write failed for platform sync {platform}: {e}")

                    return {
                        "success": True,
                        "platform": platform,
                        "status": "syncing",
                        "last_sync": update_data["last_sync"],
                        "message": f"Sync initiated for {platform}. In production, this would trigger data synchronization."
                    }
                else:
                    raise HTTPException(status_code=404, detail=f"No connection found for {platform}")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Platform sync failed (Supabase): {e}")
            raise HTTPException(status_code=500, detail=f"Failed to sync {platform}")
    else:
        # --- MONGODB PATH (FALLBACK) ---
        result = await db["platform_accounts"].update_one(
            {"user_id": user_id, "platform": platform},
            {"$set": {"last_used": datetime.now(timezone.utc)}},
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail=f"No connection found for {platform}")

        return {
            "success": True,
            "platform": platform,
            "status": "synced",
            "message": f"Sync completed for {platform} (MongoDB fallback)"
        }
