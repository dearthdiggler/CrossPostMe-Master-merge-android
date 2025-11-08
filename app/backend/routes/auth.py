import hashlib
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pymongo.errors
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jwt import PyJWTError as JWTError

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    User,
    UserCreate,
    UserLogin,
    create_access_token,
    create_refresh_token,
    get_current_user_with_fallback,
    get_password_hash,
    verify_password,
)
from db import get_typed_db
from supabase_db import db as supabase_db

# Configure logger for authentication events
logger = logging.getLogger(__name__)

# Feature flags for Supabase migration
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")


def _create_user_hash(identifier: str) -> str:
    """Create a non-reversible hash of a user identifier for logging.

    This prevents PII from being logged while still providing a unique
    identifier for tracking and debugging purposes.

    Args:
        identifier: Username, email, or other user identifier

    Returns:
        First 16 characters of SHA-256 hash (hex format)

    """
    return hashlib.sha256(identifier.encode("utf-8")).hexdigest()[:16]


router = APIRouter(prefix="/api/auth", tags=["authentication"])

db = get_typed_db()

# Cookie configuration - can be overridden based on environment
COOKIE_SECURE = True  # Set to False for local development without HTTPS

# Demo login configuration - disabled in production for security
ENABLE_DEMO_LOGIN = os.getenv("ENABLE_DEMO_LOGIN", "false").lower() == "true"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set both access and refresh token cookies with consistent security options.

    Args:
        response: FastAPI Response object
        access_token: JWT access token string
        refresh_token: JWT refresh token string

    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
    )


def clear_auth_cookies(response: Response) -> None:
    """Clear both access and refresh token cookies by setting empty values with immediate expiry.

    Args:
        response: FastAPI Response object

    """
    response.set_cookie(
        key="access_token",
        value="",
        max_age=0,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
    )

    response.set_cookie(
        key="refresh_token",
        value="",
        max_age=0,
        httponly=True,
        secure=COOKIE_SECURE,
        samesite="strict",
    )


async def initialize_auth_indexes():
    """Initialize database indexes for authentication collections."""
    try:
        # Create unique indexes on username and email fields
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)
    except pymongo.errors.OperationFailure as e:
        # Only suppress if it's the specific "index already exists" condition
        # MongoDB error codes: 85 = IndexOptionsConflict, 86 = IndexKeySpecsConflict
        if e.code in (85, 86) or "already exists" in str(e):
            # Index already exists, which is fine
            logger.info("Auth index already exists: %s", e)
        else:
            # Re-raise for other errors (permissions, connectivity, etc.)
            logger.error("Failed to create auth indexes: %s", e)
            raise
    except Exception as exc:  # pragma: no cover - broad catch for logging
        # Surface other connection-related errors (ServerSelectionTimeout, SSL, etc.)
        logger.exception(
            "Unexpected error while initializing auth indexes: %s",
            exc,
        )
        # Re-raise so the startup process can observe the failure and exit
        raise


@router.post("/register", response_model=User)
async def register(request: Request, user_data: UserCreate):
    """Register a new user.

    Supports both Supabase (primary) and MongoDB (backup) with parallel writes.
    Feature flags: USE_SUPABASE, PARALLEL_WRITE
    """
    client_ip = request.client.host if request.client else "unknown"
    user_id = str(uuid.uuid4())

    # Hash password once for both databases
    hashed_password = get_password_hash(user_data.password)

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            # Check if user exists in Supabase
            existing_user = supabase_db.get_user_by_email(user_data.email)
            if not existing_user:
                existing_user = supabase_db.get_user_by_username(user_data.username)

            if existing_user:
                user_hash = _create_user_hash(user_data.username)
                logger.warning(
                    "Registration failed - username or email already exists (Supabase) | "
                    f"event_type=registration_failed | "
                    f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                    f"client_ip={client_ip} | "
                    f"user_hash={user_hash} | "
                    f"reason=duplicate_credentials",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered",
                )

            # Create user in Supabase
            user_doc = {
                "id": user_id,
                "username": user_data.username,
                "email": user_data.email,
                "password_hash": hashed_password,
                "is_active": True,
            }

            created_user = supabase_db.create_user(user_doc)

            logger.info(
                "Registration successful (Supabase) | "
                f"event_type=registration_success | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_id={user_id}",
            )

            # PARALLEL WRITE: Also write to MongoDB for safety
            if PARALLEL_WRITE:
                try:
                    mongo_doc = {
                        "id": user_id,
                        "username": user_data.username,
                        "email": user_data.email,
                        "hashed_password": hashed_password,
                        "is_active": True,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                        "supabase_id": user_id,  # Track Supabase ID
                    }
                    await db.users.insert_one(mongo_doc)
                    logger.info(f"✅ Parallel write to MongoDB successful for user: {user_id}")
                except Exception as e:
                    # Non-blocking: MongoDB failure doesn't fail the request
                    logger.warning(f"⚠️  Parallel MongoDB write failed for user {user_id}: {e}")

            return User(
                id=created_user["id"],
                username=created_user["username"],
                email=created_user["email"],
                is_active=created_user.get("is_active", True),
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration failed (Supabase): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed. Please try again.",
            )

    else:
        # --- MONGODB PATH (FALLBACK/LEGACY) ---
        # Optional early check for better UX feedback
        existing_user = await db.users.find_one(
            {"$or": [{"username": user_data.username}, {"email": user_data.email}]},
        )

        if existing_user:
            user_hash = _create_user_hash(user_data.username)
            logger.warning(
                "Registration failed - username or email already exists (MongoDB) | "
                f"event_type=registration_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_hash={user_hash} | "
                f"reason=duplicate_credentials",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            )

        # Create user in MongoDB
        user_doc = {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            await db.users.insert_one(user_doc)

            logger.info(
                "Registration successful (MongoDB) | "
                f"event_type=registration_success | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_id={user_id}",
            )
        except pymongo.errors.DuplicateKeyError:
            logger.warning(
                "Registration failed - duplicate key error (MongoDB) | "
                f"event_type=registration_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"reason=duplicate_key_race_condition",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered",
            ) from None

        return User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            is_active=True,
        )


@router.post("/login")
async def login(request: Request, login_data: UserLogin, response: Response):
    """Login user and set secure httpOnly cookies.

    Supports both Supabase (primary) and MongoDB (fallback).
    Feature flag: USE_SUPABASE
    """
    client_ip = request.client.host if request.client else "unknown"
    user_doc = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            # Find user by username in Supabase
            user_doc = supabase_db.get_user_by_username(login_data.username)

            if not user_doc:
                user_hash = _create_user_hash(login_data.username)
                logger.warning(
                    "Login failed - user not found (Supabase) | "
                    f"event_type=login_failed | "
                    f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                    f"client_ip={client_ip} | "
                    f"user_hash={user_hash} | "
                    f"reason=invalid_credentials",
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Verify password (Supabase stores as password_hash, MongoDB as hashed_password)
            password_hash = user_doc.get("password_hash") or user_doc.get("hashed_password")
            if not password_hash or not verify_password(login_data.password, password_hash):
                user_hash = _create_user_hash(login_data.username)
                logger.warning(
                    "Login failed - incorrect password (Supabase) | "
                    f"event_type=login_failed | "
                    f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                    f"client_ip={client_ip} | "
                    f"user_hash={user_hash} | "
                    f"reason=invalid_credentials",
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            if not user_doc.get("is_active", True):
                logger.warning(
                    "Login failed - inactive user (Supabase) | "
                    f"event_type=login_failed | "
                    f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                    f"client_ip={client_ip} | "
                    f"user_id={user_doc['id']} | "
                    f"reason=inactive_user",
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user",
                )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed (Supabase): {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed. Please try again.",
            )

    else:
        # --- MONGODB PATH (FALLBACK/LEGACY) ---
        user_doc = await db.users.find_one({"username": login_data.username})

        if not user_doc or not verify_password(
            login_data.password,
            user_doc["hashed_password"],
        ):
            user_hash = _create_user_hash(login_data.username)
            logger.warning(
                "Login failed - incorrect credentials (MongoDB) | "
                f"event_type=login_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_hash={user_hash} | "
                f"reason=invalid_credentials",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user_doc.get("is_active", True):
            logger.warning(
                "Login failed - inactive user (MongoDB) | "
                f"event_type=login_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_id={user_doc['id']} | "
                f"reason=inactive_user",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

    # Common token creation logic (works for both databases)
    user_id = user_doc["id"]

    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user_id,
            "username": user_doc["username"],
            "email": user_doc["email"],
            "is_active": user_doc.get("is_active", True),
            "is_admin": user_doc.get("is_admin", False),
        },
        expires_delta=access_token_expires,
    )

    refresh_token = create_refresh_token(user_id)

    # Set secure httpOnly cookies using helper function
    set_auth_cookies(response, access_token, refresh_token)

    # Log successful login (PII-safe: no username/email)
    db_source = "Supabase" if USE_SUPABASE else "MongoDB"
    logger.info(
        f"Login successful ({db_source}) | "
        f"event_type=login_success | "
        f"timestamp={datetime.now(timezone.utc).isoformat()} | "
        f"client_ip={client_ip} | "
        f"user_id={user_id}",
    )

    return {
        "message": "Login successful",
        "user": {
            "id": user_id,
            "username": user_doc["username"],
            "email": user_doc["email"],
            "is_active": user_doc.get("is_active", True),
        },
    }


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """Refresh access token using refresh token."""
    client_ip = request.client.host if request.client else "unknown"
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        # Log missing refresh token
        logger.warning(
            "Token refresh failed - missing refresh token | "
            f"event_type=token_refresh_failed | "
            f"timestamp={datetime.now(timezone.utc).isoformat()} | "
            f"client_ip={client_ip} | "
            f"reason=missing_token",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    try:
        # Verify refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        token_type = payload.get("token_type")

        if token_type != "refresh":
            # Log invalid token type
            logger.warning(
                "Token refresh failed - invalid token type | "
                f"event_type=token_refresh_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_id={user_id} | "
                f"reason=invalid_token_type",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        # Get user data from Supabase or MongoDB
        user_doc = None

        if USE_SUPABASE:
            # --- SUPABASE PATH (PRIMARY) ---
            try:
                from supabase_db import get_supabase
                client = get_supabase()
                if client:
                    result = client.table("users").select("*").eq("id", user_id).execute()
                    if result.data and len(result.data) > 0:
                        user_doc = result.data[0]
            except Exception as e:
                logger.error(f"Failed to fetch user from Supabase: {e}")
                # Continue to MongoDB fallback

        # MongoDB fallback
        if not user_doc:
            user_doc = await db.users.find_one({"id": user_id})

        if not user_doc:
            # Log user not found
            logger.warning(
                "Token refresh failed - user not found | "
                f"event_type=token_refresh_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_id={user_id} | "
                f"reason=user_not_found",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        if not user_doc.get("is_active", True):
            # Log inactive user (PII-safe: no username)
            logger.warning(
                "Token refresh failed - inactive user | "
                f"event_type=token_refresh_failed | "
                f"timestamp={datetime.now(timezone.utc).isoformat()} | "
                f"client_ip={client_ip} | "
                f"user_id={user_id} | "
                f"reason=inactive_user",
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user",
            )

        # Create new access token and refresh token (token rotation for security)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={
                "user_id": user_id,
                "username": user_doc["username"],
                "email": user_doc["email"],
                "is_active": user_doc.get("is_active", True),
                "is_admin": user_doc.get("is_admin", False),
            },
            expires_delta=access_token_expires,
        )

        # Create new refresh token for security (token rotation)
        new_refresh_token = create_refresh_token(user_id)

        # Set new access and refresh token cookies using helper function
        set_auth_cookies(response, new_access_token, new_refresh_token)

        # Log successful token refresh (PII-safe: no username)
        logger.info(
            "Token refresh successful | "
            f"event_type=token_refresh_success | "
            f"timestamp={datetime.now(timezone.utc).isoformat()} | "
            f"client_ip={client_ip} | "
            f"user_id={user_id}",
        )

        return {"message": "Token refreshed successfully"}

    except JWTError as err:
        # Log JWT error
        logger.warning(
            "Token refresh failed - invalid JWT | "
            f"event_type=token_refresh_failed | "
            f"timestamp={datetime.now(timezone.utc).isoformat()} | "
            f"client_ip={client_ip} | "
            f"reason=invalid_jwt",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from err


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    user_data_and_id=Depends(get_current_user_with_fallback),
):
    """Logout user by clearing secure cookies."""
    client_ip = request.client.host if request.client else "unknown"
    _user_data, user_id = user_data_and_id  # Prefix unused var with underscore

    # Clear authentication cookies using helper function
    clear_auth_cookies(response)

    # Log successful logout
    logger.info(
        "Logout successful | "
        f"event_type=logout | "
        f"timestamp={datetime.now(timezone.utc).isoformat()} | "
        f"client_ip={client_ip} | "
        f"user_id={user_id}",
    )

    return {"message": "Logout successful"}


@router.get("/me", response_model=User)
async def get_current_user_info(
    user_data_and_id=Depends(get_current_user_with_fallback),
):
    """Get current user information.

    Optimized to read user data from JWT claims when available, with DB fallback.
    Supports both Supabase (primary) and MongoDB (fallback).
    Feature flag: USE_SUPABASE
    """
    user_data, user_id = user_data_and_id

    # If JWT contains complete user data, return it directly (no DB query)
    if user_data:
        return user_data

    # Fallback: query database for older tokens that don't contain full user data
    user_doc = None

    if USE_SUPABASE:
        # --- SUPABASE PATH (PRIMARY) ---
        try:
            # Query Supabase by user ID
            from supabase_db import get_supabase
            client = get_supabase()
            if client:
                result = client.table("users").select("*").eq("id", user_id).execute()
                if result.data and len(result.data) > 0:
                    user_doc = result.data[0]

        except Exception as e:
            logger.error(f"Failed to fetch user from Supabase: {e}")
            # Continue to MongoDB fallback

    # MongoDB fallback (if Supabase disabled or failed)
    if not user_doc:
        user_doc = await db.users.find_one({"id": user_id})

    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return User(
        id=user_doc["id"],
        username=user_doc["username"],
        email=user_doc["email"],
        is_active=user_doc.get("is_active", True),
    )


@router.post("/demo-login")
async def demo_login(request: Request, response: Response):
    """Create a demo user session for development/testing.
    This creates secure cookies for the default user.

    SECURITY: This endpoint is disabled in production environments.
    Set ENABLE_DEMO_LOGIN=true environment variable to enable.
    """
    # Production guard - reject demo login in production
    if not ENABLE_DEMO_LOGIN:
        # Log blocked attempt with security context (PII-safe: hashed identifiers)
        client_ip = request.client.host if request.client else "unknown"
        username_hash = _create_user_hash("demo_user")
        email_hash = _create_user_hash("demo@example.com")
        logger.warning(
            "Blocked demo login attempt - demo login disabled | "
            f"timestamp={datetime.now(timezone.utc).isoformat()} | "
            f"client_ip={client_ip} | "
            f"username_hash={username_hash} | "
            f"email_hash={email_hash}",
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo login is disabled in this environment",
        )

    # Check if default user exists, create if not
    default_user = await db.users.find_one({"id": "default"})

    if not default_user:
        # Create default demo user
        user_doc = {
            "id": "default",
            "username": "demo_user",
            "email": "demo@example.com",
            "hashed_password": get_password_hash("demo123"),
            "is_active": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(user_doc)

    user_id = "default"

    # Ensure we have the latest user record (in case we just created it)
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo user not available",
        )

    # Create access and refresh tokens based on stored user record
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user_doc["id"],
            "username": user_doc.get("username"),
            "email": user_doc.get("email"),
            "is_active": user_doc.get("is_active", True),
            "is_admin": user_doc.get("is_admin", False),
        },
        expires_delta=access_token_expires,
    )

    refresh_token = create_refresh_token(user_id)

    # Set secure httpOnly cookies using helper function
    set_auth_cookies(response, access_token, refresh_token)

    return {
        "message": "Demo login successful",
        "user": {
            "id": user_id,
            "username": "demo_user",
            "email": "demo@example.com",
            "is_active": True,
        },
    }
