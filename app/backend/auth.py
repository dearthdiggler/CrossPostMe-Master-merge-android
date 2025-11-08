import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# JWT Configuration
try:
    from vault import get_secret
    _SECRET_KEY = get_secret('secret_key')
except Exception:
    # Fallback to environment variable
    _SECRET_KEY = os.getenv("SECRET_KEY")

if not _SECRET_KEY:
    # Development fallback - DO NOT use in production
    import warnings

    warnings.warn(
        "SECRET_KEY not found in vault or environment. Using development fallback. "
        "Generate a secure key for production with: openssl rand -hex 32",
        UserWarning,
        stacklevel=2,
    )
    _SECRET_KEY = "dev-secret-key-change-in-production-" + "a" * 32
SECRET_KEY: str = _SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Shortened for security
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Longer-lived refresh tokens

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    user_id: str | None = None
    token_type: str | None = None  # "access" or "refresh"


class RefreshTokenData(BaseModel):
    user_id: str
    token_type: str = "refresh"


class User(BaseModel):
    id: str
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False


class UserInDB(User):
    hashed_password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


def _user_from_payload(payload: dict) -> User | None:
    """Extract User object from JWT payload if all required fields are present.
    Returns None if any required field is missing.
    """
    user_id = payload.get("user_id")
    username = payload.get("username")
    email = payload.get("email")
    is_active = payload.get("is_active")
    is_admin = payload.get("is_admin", False)

    # Only return User object if we have all required fields
    if user_id and username and email and is_active is not None:
        return User(
            id=user_id,
            username=username,
            email=email,
            is_active=is_active,
            is_admin=is_admin,
        )
    return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash."""
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    # Truncate password to 72 bytes for bcrypt compatibility
    # (bcrypt has a 72-byte limit)
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return str(pwd_context.hash(password))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a new access token."""
    # Ensure is_admin is always explicitly present in the token claims
    to_encode = data.copy()
    # Always assign a boolean for is_admin (defaults to False)
    to_encode["is_admin"] = bool(to_encode.get("is_admin", False))
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        )

    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


def create_refresh_token(user_id: str) -> str:
    """Create a new refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"user_id": user_id, "exp": expire, "token_type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return str(encoded_jwt)


async def get_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Get the current user from JWT token (cookie-first, fallback to Authorization header).
    Returns user_id for use in route functions.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Try cookie first, then fallback to Authorization header
    token = access_token
    if not token and credentials:
        token = credentials.credentials

    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        token_type = payload.get("token_type")

        # Ensure it's an access token, not a refresh token
        if user_id is None or token_type != "access":
            raise credentials_exception

        return str(user_id) if user_id else ""
    except JWTError as err:
        raise credentials_exception from err


async def get_current_user_data(
    access_token: Annotated[str | None, Cookie()] = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User | None:
    """Get the current user data from JWT token.
    Returns full User object from JWT claims, avoiding DB lookup.
    Falls back to None if JWT doesn't contain complete user data (for older tokens).
    """
    # Try cookie first, then fallback to Authorization header
    token = access_token
    if not token and credentials:
        token = credentials.credentials

    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_type = payload.get("token_type")

        # Ensure it's an access token
        if token_type != "access":
            return None

        return _user_from_payload(payload)
    except JWTError:
        # For invalid tokens, let get_current_user handle the exception
        raise


async def get_current_user_with_fallback(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get current user data with optimized JWT-first approach and DB fallback.
    Returns tuple of (user_data: User | None, user_id: str).
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = payload.get("user_id")
        if user_id is None:
            raise credentials_exception

        # Try to get full user data from JWT using helper
        user_data = _user_from_payload(payload)

        return user_data, user_id

    except JWTError as err:
        raise credentials_exception from err


async def get_optional_current_user(
    access_token: Annotated[str | None, Cookie()] = None,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    """Get current user but allow anonymous access with default user.
    This is useful for development/demo mode.
    """
    if not access_token and (credentials is None):
        return "default"  # Anonymous/demo user

    try:
        return await get_current_user(access_token, credentials)
    except HTTPException:
        return "default"  # Fall back to demo user if token is invalid
