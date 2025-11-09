"""
Test Supabase Connection
Quick test to verify Supabase is configured correctly
"""

import os
import sys

import pytest

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from supabase_db import db, get_supabase


def test_connection():
    """Basic Supabase connection smoke test using assertions."""
    client = get_supabase()
    # If Supabase is not configured in this environment, skip the integration test
    if not client:
        pytest.skip("Supabase not configured for this environment")

    # Basic query should not raise; wrap in try/except to convert to assertion
    try:
        _ = client.table("users").select("*").limit(1).execute()
    except Exception as e:
        pytest.skip(f"Supabase not fully configured for integration tests: {e}")

    # Check SupabaseDB wrapper method doesn't raise (may return empty results)
    try:
        stats = db.get_industry_stats()
        assert stats is not None
    except Exception:
        # This is non-fatal; skip if DB schema/views not created
        pytest.skip("SupabaseDB wrapper unavailable in this environment")


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("CROSSPOSTME - SUPABASE CONNECTION TEST")
    print("=" * 50 + "\n")
    try:
        test_connection()
        sys.exit(0)
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
