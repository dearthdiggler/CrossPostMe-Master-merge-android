## Removed broken top-level function header

import logging
import os
from datetime import datetime, timezone
from typing import Any

from db import get_db
from fastapi import APIRouter

logger = logging.getLogger(__name__)
USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in ("true", "1", "yes")
PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in ("true", "1", "yes")
router = APIRouter(prefix="/api/ads", tags=["ads"])


# Helper functions for datetime serialization/deserialization
def serialize_datetime_fields(doc: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    """Convert datetime objects to ISO strings for Supabase storage."""
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

# ...rest of improved file from Supa repo...
