import asyncio
import time
from typing import Any, Optional

from fastapi import Header, HTTPException, Request
from services.auth import verify_token


async def get_db(request: Request) -> Any:
    """Dependency to read the Motor database instance from app.state."""
    db = getattr(request.app.state, "db", None)
    if db is None:
        raise HTTPException(
            status_code=503, detail="Database connection not initialized"
        )
    return db


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[str]:
    """Extract the user id from a Bearer token using services.auth.verify_token.

    Returns None if no valid Authorization header or token.
    """
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1]
    return verify_token(token)


class RateLimiter:
    """Very small in-memory token-bucket rate limiter for single-process dev use.

    For production use a centralized store (Redis) keyed by user or IP.
    """

    def __init__(self) -> None:
        self._buckets: dict[str, tuple[float, float]] = {}
        self._lock = asyncio.Lock()

    async def allow(self, key: str, capacity: int, per_seconds: int) -> bool:
        now = time.time()
        async with self._lock:
            tokens, last = self._buckets.get(key, (float(capacity), now))
            elapsed = now - last
            if elapsed > 0:
                refill = (elapsed / per_seconds) * capacity
                tokens = min(float(capacity), tokens + refill)
            if tokens >= 1.0:
                tokens -= 1.0
                self._buckets[key] = (tokens, now)
                return True
            self._buckets[key] = (tokens, now)
            return False


_GLOBAL_RATE_LIMITER = RateLimiter()


def rate_limit_dependency(capacity: int = 10, per_seconds: int = 60):
    """Factory that returns a FastAPI dependency enforcing a per-key rate limit.

    Keying: if Authorization Bearer token present, use `user:{token}`, otherwise `ip:{ip}`.
    """

    async def _dep(request: Request, authorization: Optional[str] = Header(None)):
        if authorization:
            parts = authorization.split()
            token = (
                parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else None
            )
        else:
            token = None
        if token:
            key = f"user:{token}"
        else:
            client = getattr(request, "client", None)
            ip = client.host if client is not None else "unknown"
            key = f"ip:{ip}"

        allowed = await _GLOBAL_RATE_LIMITER.allow(key, capacity, per_seconds)
        if not allowed:
            raise HTTPException(status_code=429, detail="Too many requests")

    return _dep
