#!/usr/bin/env python3
"""Database Setup and Migration Script
Sets up MongoDB collections and indexes for optimal performance
"""
import asyncio
import logging
import os
from typing import Any

import certifi
from motor.motor_asyncio import AsyncIOMotorClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def setup_database(db) -> None:
    """Set up MongoDB collections and indexes

    Args:
        db: AsyncIOMotorDatabase instance (already connected)

    """
    try:
        logger.info("Setting up database indexes...")

        # Set up indexes for messages collection
        await setup_messages_indexes(db)

        # Set up indexes for other collections
        await setup_ads_indexes(db)
        await setup_leads_indexes(db)
        await setup_platform_accounts_indexes(db)
        await setup_secure_credentials_indexes(db)

        logger.info("Database setup completed successfully")

    except Exception:
        logger.exception("Database setup failed")
        raise


async def setup_messages_indexes(db) -> None:
    """Set up indexes for the messages collection"""
    logger.info("Setting up messages collection indexes...")

    # Compound index for efficient duplicate detection and queries
    await db.messages.create_index(
        [
            ("user_id", 1),
            ("platform", 1),
            ("platform_message_id", 1),
            ("sender_email", 1),
        ],
        name="messages_compound_idx",
        background=True,
    )

    # Index for content hash-based duplicate detection (primary optimization)
    await db.messages.create_index(
        [("user_id", 1), ("content_hash", 1)],
        name="messages_content_hash_idx",
        background=True,
    )

    # Index for user queries and filtering
    await db.messages.create_index(
        [("user_id", 1), ("received_at", -1)],
        name="messages_user_received_idx",
        background=True,
    )

    # Index for platform and status filtering
    await db.messages.create_index(
        [("user_id", 1), ("platform", 1), ("is_read", 1), ("is_responded", 1)],
        name="messages_status_idx",
        background=True,
    )

    # Index for ad matching
    await db.messages.create_index(
        [("user_id", 1), ("ad_id", 1)],
        name="messages_ad_idx",
        background=True,
    )

    logger.info("Messages indexes created")


async def setup_ads_indexes(db) -> None:
    """Set up indexes for the ads collection"""
    logger.info("Setting up ads collection indexes...")

    # Primary user and status index
    await db.ads.create_index(
        [("user_id", 1), ("status", 1), ("created_at", -1)],
        name="ads_user_status_idx",
        background=True,
    )

    # Platform and status index
    await db.ads.create_index(
        [("user_id", 1), ("platforms", 1), ("status", 1)],
        name="ads_platform_status_idx",
        background=True,
    )

    # Unique ad ID index
    await db.ads.create_index(
        [("id", 1)],
        name="ads_id_idx",
        unique=True,
        background=True,
    )

    logger.info("Ads indexes created")


async def setup_leads_indexes(db) -> None:
    """Set up indexes for the leads collection"""
    logger.info("Setting up leads collection indexes...")

    # Primary user and status index
    await db.leads.create_index(
        [("user_id", 1), ("status", 1), ("created_at", -1)],
        name="leads_user_status_idx",
        background=True,
    )

    # Contact information index
    await db.leads.create_index(
        [("user_id", 1), ("platform", 1), ("contact_email", 1)],
        name="leads_contact_email_idx",
        background=True,
        sparse=True,
    )

    await db.leads.create_index(
        [("user_id", 1), ("platform", 1), ("contact_phone", 1)],
        name="leads_contact_phone_idx",
        background=True,
        sparse=True,
    )

    # Ad association index
    await db.leads.create_index(
        [("user_id", 1), ("ad_id", 1)],
        name="leads_ad_idx",
        background=True,
    )

    logger.info("Leads indexes created")


async def setup_platform_accounts_indexes(db) -> None:
    """Set up indexes for platform accounts"""
    logger.info("Setting up platform_accounts collection indexes...")

    # User and platform index
    await db.platform_accounts.create_index(
        [("user_id", 1), ("platform", 1), ("status", 1)],
        name="platform_accounts_user_platform_idx",
        background=True,
    )

    # Unique account per user per platform
    await db.platform_accounts.create_index(
        [("user_id", 1), ("platform", 1), ("account_email", 1)],
        name="platform_accounts_unique_idx",
        unique=True,
        background=True,
    )

    logger.info("Platform accounts indexes created")


async def setup_secure_credentials_indexes(db) -> None:
    """Set up indexes for secure credentials"""
    logger.info("Setting up secure_credentials collection indexes...")

    # User and platform index
    await db.secure_credentials.create_index(
        [("user_id", 1), ("platform", 1)],
        name="secure_credentials_user_platform_idx",
        unique=True,
        background=True,
    )

    logger.info("Secure credentials indexes created")


async def check_existing_indexes(db) -> None:
    """Check what indexes currently exist"""
    logger.info("Checking existing indexes...")

    collections = [
        "messages",
        "ads",
        "leads",
        "platform_accounts",
        "secure_credentials",
    ]

    for collection_name in collections:
        collection = getattr(db, collection_name)
        indexes = await collection.list_indexes().to_list(None)
        logger.info(f"{collection_name} indexes:")
        for idx in indexes:
            logger.info(f"  - {idx['name']}: {idx.get('key', {})}")


async def main() -> None:
    """Main setup function"""
    logger.info("Starting database setup...")

    # Connect to MongoDB once
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "crosspostme")

    # Motor's constructor can be strict with typed client options; annotate client
    # and avoid spurious arg-type errors in mypy with a targeted ignore where used.
    # Motor client is dynamically typed; annotate as Any to suppress mypy false positives
    # Use certifi CA bundle when connecting to Atlas (mongodb+srv)
    client_opts = {}
    if mongo_url.startswith("mongodb+srv") or "mongodb+srv" in mongo_url:
        client_opts.update({"tls": True, "tlsCAFile": certifi.where()})
    client: Any = AsyncIOMotorClient(mongo_url, **client_opts)  # type: ignore[arg-type]
    db = client[db_name]

    try:
        logger.info(f"Connected to MongoDB: {mongo_url}/{db_name}")

        # Test connection
        await client.admin.command("ping")
        logger.info("MongoDB connection successful")

        # Run setup using the same connection
        await setup_database(db)

        # Check results using the same connection
        await check_existing_indexes(db)

        logger.info("Database setup completed!")

    except Exception:
        logger.exception("Error during database setup")
        raise
    finally:
        # Always close the connection
        client.close()


if __name__ == "__main__":
    asyncio.run(main())
