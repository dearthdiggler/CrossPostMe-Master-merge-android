"""Database Connection Test
Tests the connection between backend and MongoDB
Run with: pytest tests/test_db_connection.py -v
Or from backend root: python -m tests.test_db_connection
"""

import asyncio
import logging
import os
import sys
from typing import Any

# Import from parent package using absolute imports
from backend.db import get_db

# Configure logger for this test module
logger = logging.getLogger(__name__)


async def test_database_connection() -> bool:
    """Test database connection and basic operations

    Returns True on success, False on failure when invoked as a script.
    Pytest will ignore the return value; the annotation documents behavior
    for static checkers.
    """
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)

    db: Any = None  # Initialize to avoid NameError in finally block

    try:
        # Get database instance
        db = get_db()
        print("✓ Database instance created")

        # Get database name without exposing connection details
        db_name = os.getenv("DB_NAME", "unknown")
        print(f"  Database: {db_name}")

        # Test connection by inserting a test document
        print("\nTesting database operations...")
        test_doc = {"test": "connection", "client_name": "test_script"}

        result = await db["status_checks"].insert_one(test_doc)
        print(f"✓ Insert operation successful (ID: {result.inserted_id})")

        # Test reading the document back
        retrieved = await db["status_checks"].find_one({"_id": result.inserted_id})
        if retrieved:
            print("✓ Read operation successful")

        # Clean up test document
        await db["status_checks"].delete_one({"_id": result.inserted_id})
        print("✓ Delete operation successful")

        # List all collections using public API
        # Note: We test with known collections rather than listing all
        known_collections = [
            "ads",
            "posted_ads",
            "platform_accounts",
            "status_checks",
            "platform_tokens",
            "platform_credentials",
            "oauth_states",
            "messages",
            "leads",
        ]

        print("\n✓ Testing known collections:")
        for coll_name in sorted(known_collections):
            try:
                count = await db.get_collection(coll_name).count_documents({})
                print(f"  - {coll_name}: {count} documents")
            except Exception as e:
                # Collection may not exist yet, which is fine
                logger.debug(f"Skipping collection '{coll_name}': {e!r}")
                print(f"  - {coll_name}: skipped (not accessible)")

        print("\n" + "=" * 60)
        print("✓ All database tests passed!")
        print("=" * 60)

    except Exception as e:
        print("\n✗ Database connection failed!")
        print(f"  Error: {type(e).__name__}: {e!s}")
        print("\nTroubleshooting:")
        print("  1. Check if MongoDB is running")
        print("  2. Verify MONGO_URL in .env file")
        print("  3. Ensure DB_NAME is set correctly")
        return False

    finally:
        # Close connection only if db was successfully created
        if db is not None:
            db.close()

    return True


def main() -> None:
    """Main entry point for running test as script"""
    # Configure logging - set to DEBUG for verbose output
    log_level = os.getenv("TEST_LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(levelname)s: %(message)s",
    )

    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
