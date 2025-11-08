import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

# Simple JWT-based auth utilities. For production, use a robust library and rotate secrets.
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"


def create_token(user_id: str, expires_minutes: int = 60) -> str:
    now = datetime.now(timezone.utc)
    iat = int(now.timestamp())
    exp = int((now + timedelta(minutes=expires_minutes)).timestamp())
    payload = {"sub": str(user_id), "iat": iat, "exp": exp}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        sub = payload.get("sub")
        return str(sub) if sub is not None else None
    except Exception:
        return None
