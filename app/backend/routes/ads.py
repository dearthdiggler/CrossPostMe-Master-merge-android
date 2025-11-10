def deserialize_datetime_fields(
    doc: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    """Convert ISO strings back to datetime objects."""
    for field in fields:
        if field in doc and doc[field] is not None and isinstance(doc[field], str):
            import logging
            import os
            from datetime import datetime
            from typing import Any

            from fastapi import APIRouter

            logger = logging.getLogger(__name__)

            # Feature flags for Supabase migration
            USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in (
                "true",
                "1",
                "yes",
            )
            PARALLEL_WRITE = os.getenv("PARALLEL_WRITE", "true").lower() in (
                "true",
                "1",
                "yes",
            )

            router = APIRouter(prefix="/api/ads", tags=["ads"])

            # Helper functions for datetime serialization/deserialization
            def serialize_datetime_fields(
                doc: dict[str, Any], fields: list[str]
            ) -> dict[str, Any]:
                """Convert datetime objects to ISO strings for MongoDB storage."""
                for field in fields:
                    if (
                        field in doc
                        and doc[field] is not None
                        and isinstance(doc[field], datetime)
                    ):
                        doc[field] = doc[field].isoformat()
                return doc

            def deserialize_datetime_fields(
                doc: dict[str, Any],
                fields: list[str],
            ) -> dict[str, Any]:
                """Convert ISO strings back to datetime objects."""
                for field in fields:
                    if (
                        field in doc
                        and doc[field] is not None
                        and isinstance(doc[field], str)
                    ):
                        import logging
                        import os
                        from datetime import datetime, timezone
                        from typing import Any

                        from fastapi import APIRouter

                        from backend.db import get_db

                        logger = logging.getLogger(__name__)

                        # Feature flags for Supabase migration
                        USE_SUPABASE = os.getenv("USE_SUPABASE", "true").lower() in (
                            "true",
                            "1",
                            "yes",
                        )
                        PARALLEL_WRITE = os.getenv(
                            "PARALLEL_WRITE", "true"
                        ).lower() in ("true", "1", "yes")

                        router = APIRouter(prefix="/api/ads", tags=["ads"])

                        # Helper functions for datetime serialization/deserialization
                        def serialize_datetime_fields(
                            doc: dict[str, Any], fields: list[str]
                        ) -> dict[str, Any]:
                            for field in fields:
                                if (
                                    field in doc
                                    and doc[field] is not None
                                    and isinstance(doc[field], datetime)
                                ):
                                    doc[field] = doc[field].isoformat()
                            return doc

                        def deserialize_datetime_fields(
                            doc: dict[str, Any], fields: list[str]
                        ) -> dict[str, Any]:
                            for field in fields:
                                if (
                                    field in doc
                                    and doc[field] is not None
                                    and isinstance(doc[field], str)
                                ):
                                    try:
                                        doc[field] = datetime.fromisoformat(doc[field])
                                    except ValueError:
                                        if (
                                            field == "created_at"
                                            or field == "posted_at"
                                        ):
                                            doc[field] = datetime.now(timezone.utc)
                            return doc

                        def normalize_posted_ad_dict(
                            doc: dict[str, Any],
                        ) -> dict[str, Any]:
                            d: dict[str, Any] = dict(doc or {})
                            if "posted_at" in d and d["posted_at"] is not None:
                                v = d["posted_at"]
                                if isinstance(v, str):
                                    try:
                                        d["posted_at"] = datetime.fromisoformat(v)
                                    except Exception:
                                        d["posted_at"] = datetime.now(timezone.utc)
                            else:
                                d["posted_at"] = datetime.now(timezone.utc)
                            for key in ("platform_ad_id", "post_url"):
                                if key in d and d[key] is not None:
                                    d[key] = str(d[key])
                                else:
                                    d[key] = None
                            for key in ("views", "clicks", "leads"):
                                try:
                                    d[key] = (
                                        int(d.get(key, 0))
                                        if d.get(key) is not None
                                        else 0
                                    )
                                except Exception:
                                    d[key] = 0
                            return d

                        db = get_db()

                        # ...rest of the file from Supa repo (full content, no placeholders)
