"""
User Management Routes

Handles CRUD operations for user accounts with Supabase support.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from auth import User, get_current_user_with_fallback, get_password_hash
from db import get_typed_db
from supabase_db import db as supabase_db

logger = logging.getLogger(__name__)

# Feature flags
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")

router = APIRouter(prefix="/api/users", tags=["users"])
db = get_typed_db()


# --- Request/Response Models ---

class UserUpdate(BaseModel):
    """User update request model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None  # If provided, will be hashed
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Full user response with all fields."""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    trial_active: Optional[bool] = None
    trial_type: Optional[str] = None


# --- Helper Functions ---

def _get_user_from_supabase(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user from Supabase by ID."""
    try:
        from supabase_db import get_supabase
        client = get_supabase()
        if client:
            result = client.table("users").select("*").eq("id", user_id).execute()
            if result.data and len(result.data) > 0:
                return result.data[0]
    except Exception as e:
        logger.error(f"Supabase user fetch failed: {e}")
    return None


def _update_user_in_supabase(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update user in Supabase."""
    try:
        updated = supabase_db.update_user(user_id, update_data)
        return updated
    except Exception as e:
        logger.error(f"Supabase user update failed: {e}")
        raise


def _delete_user_from_supabase(user_id: str) -> bool:
    """Delete user from Supabase (soft delete - set is_active=False)."""
    try:
        update_data = {
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        supabase_db.update_user(user_id, update_data)
        return True
    except Exception as e:
        logger.error(f"Supabase user deletion failed: {e}")
        return False


# --- Routes ---

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    current_user=Depends(get_current_user_with_fallback)
):
    """Get user by ID.

    Users can only access their own profile unless they're an admin.
    Supports both Supabase (primary) and MongoDB (fallback).
    """
    user_data, current_user_id = current_user

    # Check authorization (users can only view their own profile, unless admin)
    is_admin = user_data.is_admin if user_data else False
    if user_id != current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )

    user_doc = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        user_doc = _get_user_from_supabase(user_id)

        if not user_doc:
            logger.warning(f"User not found in Supabase: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    else:
        # --- MONGODB PATH (FALLBACK) ---
        user_doc = await db.users.find_one({"id": user_id})

        if not user_doc:
            logger.warning(f"User not found in MongoDB: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    # Remove password hash from response
    user_doc.pop("password_hash", None)
    user_doc.pop("hashed_password", None)
    user_doc.pop("_id", None)

    return UserResponse(**user_doc)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user=Depends(get_current_user_with_fallback)
):
    """Update user information.

    Users can only update their own profile unless they're an admin.
    Supports both Supabase (primary) and MongoDB (backup with parallel writes).
    """
    user_data, current_user_id = current_user

    # Check authorization
    is_admin = user_data.is_admin if user_data else False
    if user_id != current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    # Build update dictionary (only include provided fields)
    update_data = {
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    if user_update.email is not None:
        update_data["email"] = user_update.email
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.phone is not None:
        update_data["phone"] = user_update.phone
    if user_update.password is not None:
        update_data["password_hash"] = get_password_hash(user_update.password)
        update_data["hashed_password"] = update_data["password_hash"]  # MongoDB compatibility
    if user_update.is_active is not None and is_admin:
        # Only admins can change active status
        update_data["is_active"] = user_update.is_active

    updated_user = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            updated_user = _update_user_in_supabase(user_id, update_data)

            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info(f"User updated in Supabase: {user_id}")

            # PARALLEL WRITE: Also update in MongoDB
            if PARALLEL_WRITE:
                try:
                    await db.users.update_one(
                        {"id": user_id},
                        {"$set": update_data}
                    )
                    logger.info(f"✅ Parallel write to MongoDB successful for user: {user_id}")
                except Exception as e:
                    logger.warning(f"⚠️  Parallel MongoDB write failed for user {user_id}: {e}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User update failed (Supabase): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    else:
        # --- MONGODB PATH (FALLBACK) ---
        try:
            result = await db.users.update_one(
                {"id": user_id},
                {"$set": update_data}
            )

            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            # Fetch updated user
            updated_user = await db.users.find_one({"id": user_id})
            logger.info(f"User updated in MongoDB: {user_id}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User update failed (MongoDB): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )

    # Remove password hash from response
    updated_user.pop("password_hash", None)
    updated_user.pop("hashed_password", None)
    updated_user.pop("_id", None)

    return UserResponse(**updated_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user=Depends(get_current_user_with_fallback)
):
    """Delete user account (soft delete - sets is_active=False).

    Users can only delete their own account unless they're an admin.
    Supports both Supabase (primary) and MongoDB (backup with parallel writes).
    """
    user_data, current_user_id = current_user

    # Check authorization
    is_admin = user_data.is_admin if user_data else False
    if user_id != current_user_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            success = _delete_user_from_supabase(user_id)

            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info(f"User soft-deleted in Supabase: {user_id}")

            # PARALLEL WRITE: Also delete in MongoDB
            if PARALLEL_WRITE:
                try:
                    await db.users.update_one(
                        {"id": user_id},
                        {"$set": {
                            "is_active": False,
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }}
                    )
                    logger.info(f"✅ Parallel write to MongoDB successful for user deletion: {user_id}")
                except Exception as e:
                    logger.warning(f"⚠️  Parallel MongoDB write failed for user deletion {user_id}: {e}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User deletion failed (Supabase): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
    else:
        # --- MONGODB PATH (FALLBACK) ---
        try:
            result = await db.users.update_one(
                {"id": user_id},
                {"$set": {
                    "is_active": False,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )

            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            logger.info(f"User soft-deleted in MongoDB: {user_id}")

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"User deletion failed (MongoDB): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

    return {
        "message": "User deleted successfully",
        "user_id": user_id
    }


@router.get("/search/query", response_model=List[UserResponse])
async def search_users(
    q: Optional[str] = None,
    limit: int = 20,
    current_user=Depends(get_current_user_with_fallback)
):
    """Search users by username or email (admin only).

    Supports both Supabase (primary) and MongoDB (fallback).
    """
    user_data, current_user_id = current_user

    # Only admins can search users
    is_admin = user_data.is_admin if user_data else False
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    users: list = []

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                query = client.table("users").select("*").limit(limit)

                if q:
                    # Search in username or email
                    query = query.or_(f"username.ilike.%{q}%,email.ilike.%{q}%")

                result = query.execute()
                users = result.data if result.data else []

            logger.info(f"User search in Supabase: {len(users)} results for query: {q}")

        except Exception as e:
            logger.error(f"User search failed (Supabase): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Search failed"
            )
    else:
        # --- MONGODB PATH (FALLBACK) ---
        try:
            query_filter = {}
            if q:
                query_filter = {
                    "$or": [
                        {"username": {"$regex": q, "$options": "i"}},
                        {"email": {"$regex": q, "$options": "i"}}
                    ]
                }

            cursor = db.users.find(query_filter).limit(limit)
            users = await cursor.to_list(length=limit)

            logger.info(f"User search in MongoDB: {len(users)} results for query: {q}")

        except Exception as e:
            logger.error(f"User search failed (MongoDB): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Search failed"
            )

    # Remove sensitive data
    for user in users:
        user.pop("password_hash", None)
        user.pop("hashed_password", None)
        user.pop("_id", None)

    return [UserResponse(**user) for user in users]
