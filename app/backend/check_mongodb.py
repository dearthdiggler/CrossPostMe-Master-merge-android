"""MongoDB Connection Checker
This script verifies your MongoDB connection and displays database information.
"""

# Disable specific mypy check which triggers a false-positive in this health-check script
# (mypy may incorrectly report 'func-returns-value' here due to complex control flow).
# mypy: disable-error-code=func-returns-value

import asyncio
import os
from typing import Any
from urllib.parse import urlparse, urlunparse

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import errors as pymongo_errors

# Load environment variables
load_dotenv()


async def check_mongodb_connection() -> None:  # type: ignore[func-returns-value]
    """Check MongoDB connection and display information"""
    # Get connection details from environment
    mongo_url = os.getenv("MONGO_URL")
    db_name = os.getenv("DB_NAME")

    print("=" * 60)
    print("MongoDB Connection Check")
    print("=" * 60)

    # Display configuration (hide password)
    if mongo_url:
        # Hide password in connection string for security using urllib.parse
        try:
            parsed = urlparse(mongo_url)
            # Mask password if present in the URL
            if parsed.password:
                # Replace password with ****
                safe_netloc = f"{parsed.username}:****@{parsed.hostname}"
                if parsed.port:
                    safe_netloc += f":{parsed.port}"
                safe_url = urlunparse(
                    (
                        parsed.scheme,
                        safe_netloc,
                        parsed.path,
                        parsed.params,
                        parsed.query,
                        parsed.fragment,
                    ),
                )
            else:
                safe_url = mongo_url
        except (ValueError, AttributeError, TypeError):
            # Fallback to placeholder if URL parsing fails
            # ValueError: malformed URL
            # AttributeError: missing expected attributes (hostname, port, etc.)
            # TypeError: unexpected types in URL components
            safe_url = "mongodb://****:****@[malformed-url]"
        print(f"\n📡 Connection String: {safe_url}")
    else:
        print("\n❌ MONGO_URL not found in environment variables!")
        return

    print(f"🗄️  Database Name: {db_name or 'NOT SET'}")

    if not db_name:
        print("\n❌ DB_NAME not found in environment variables!")
        return

    print("\n" + "-" * 60)
    print("Attempting to connect to MongoDB...")
    print("-" * 60)

    # Initialize client variable to None for finally block
    # Annotate as Any to avoid mypy issues with motor's stubs
    client: Any | None = None

    try:
        # Create client with a short timeout for testing
        client_options = {"serverSelectionTimeoutMS": 10000}

        # Only add TLS option if using mongodb+srv://
        if "mongodb+srv://" in mongo_url:
            client_options["tls"] = True

        # Motor's AsyncIOMotorClient constructor typing is strict in stubs; callers
        # pass dynamic client options as a dict[str, int]. We apply a targeted
        # inline ignore on the constructor call below to avoid noisy mypy
        # arg-type errors while retaining runtime behavior.
        client = AsyncIOMotorClient(mongo_url, **client_options)  # type: ignore[arg-type]

        # Test connection with ping
        print("\n⏳ Pinging MongoDB server...")
        await client.admin.command("ping")
        print("✅ Connection successful! MongoDB server is reachable.")

        # Get database
        db = client[db_name]

        # List collections
        print(f"\n📚 Collections in '{db_name}' database:")
        collections = await db.list_collection_names()
        if collections:
            for idx, coll in enumerate(collections, 1):
                # Get document count
                count = await db[coll].count_documents({})
                print(f"   {idx}. {coll} ({count} documents)")
        else:
            print("   (No collections found - database is empty)")

        # Get server info
        print("\n🖥️  MongoDB Server Information:")
        server_info = await client.server_info()
        print(f"   Version: {server_info.get('version', 'Unknown')}")
        print(f"   Git Version: {server_info.get('gitVersion', 'Unknown')}")

        # Get database stats
        print(f"\n📊 Database Statistics for '{db_name}':")
        stats = await db.command("dbStats")
        print(f"   Collections: {stats.get('collections', 0)}")
        print(f"   Data Size: {stats.get('dataSize', 0) / 1024 / 1024:.2f} MB")
        print(f"   Storage Size: {stats.get('storageSize', 0) / 1024 / 1024:.2f} MB")
        print(f"   Indexes: {stats.get('indexes', 0)}")
        print(f"   Index Size: {stats.get('indexSize', 0) / 1024 / 1024:.2f} MB")

        # Check specific collections used by your app
        print("\n🔍 Application Collections Check:")
        app_collections = ["users", "ads", "posted_ads", "platform_accounts"]
        for coll_name in app_collections:
            exists = coll_name in collections
            if exists:
                count = await db[coll_name].count_documents({})
                # Check for indexes
                indexes = await db[coll_name].list_indexes().to_list(length=100)
                index_names = [idx["name"] for idx in indexes]
                print(f"   ✅ {coll_name}: {count} documents, {len(indexes)} indexes")
                if len(index_names) > 1:  # More than just _id index
                    print(f"      Indexes: {', '.join(index_names)}")
            else:
                print(f"   ⚠️  {coll_name}: Not found (will be created on first use)")

        # Test a simple query on users collection
        if "users" in collections:
            print("\n👤 Sample User Data (first user, limited fields):")
            sample_user = await db.users.find_one(
                {},
                {"username": 1, "email": 1, "is_active": 1, "_id": 0},
            )
            if sample_user:
                # Mask username to avoid PII exposure
                username = sample_user.get("username", "N/A")
                if username != "N/A" and len(username) > 2:
                    masked_username = username[:2] + "***"
                elif username != "N/A":
                    masked_username = "***"
                else:
                    masked_username = "N/A"
                print(f"   Username: {masked_username}")

                # Mask entire email to avoid PII exposure (both local part and domain)
                email = sample_user.get("email", "N/A")
                if email != "N/A" and "@" in email:
                    masked_email = "****@****"
                else:
                    masked_email = "N/A"
                print(f"   Email: {masked_email}")
                print(f"   Active: {sample_user.get('is_active', 'N/A')}")
            else:
                print("   (No users found)")

        print("\n" + "=" * 60)
        print("✅ MongoDB connection check completed successfully!")
        print("=" * 60)

    except pymongo_errors.ServerSelectionTimeoutError as e:
        print("\n❌ MongoDB Server Selection Timeout!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e!s}")
        print("\n💡 Timeout troubleshooting:")
        print("   1. Check MONGO_URL is correct in .env file")
        print("   2. Verify MongoDB Atlas IP whitelist allows your IP")
        print("   3. Confirm username/password are correct")
        print("   4. Check if MongoDB cluster is accessible from your network")
        print("   5. Try increasing MONGO_SERVER_SELECTION_TIMEOUT_MS")
        print("   6. Verify DNS resolution for mongodb.net domains")
        print("\n" + "=" * 60)

    except pymongo_errors.ConnectionFailure as e:
        print("\n❌ MongoDB Connection Failure!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e!s}")
        print("\n💡 Connection failure troubleshooting:")
        print("   1. Verify MongoDB Atlas cluster is running (not paused)")
        print("   2. Check MongoDB Atlas IP whitelist includes your IP or 0.0.0.0/0")
        print("   3. Confirm network connectivity and firewall settings")
        print("   4. Verify the connection string format (mongodb+srv://...)")
        print("\n" + "=" * 60)

    except Exception as e:
        print("\n❌ Unexpected error occurred!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {e!s}")
        print("\n💡 General troubleshooting:")
        print("   1. Check MONGO_URL is correct in .env file")
        print("   2. Verify MongoDB Atlas IP whitelist includes your IP")
        print("   3. Confirm username/password are correct")
        print("   4. Check network connectivity")
        print("   5. Verify MongoDB Atlas cluster is running")
        print("\n" + "=" * 60)

    finally:
        # Always close the client connection if it was created
        if client:
            client.close()

    # Explicitly return None to make control flow explicit for type checkers
    return None


if __name__ == "__main__":
    asyncio.run(check_mongodb_connection())
