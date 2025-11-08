"""Cleanup test data from LeadService tests"""

import asyncio
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient


async def cleanup() -> None:
    # Motor client is typed as Any to avoid mypy issues with motor stubs
    client: Any = AsyncIOMotorClient("mongodb://localhost:27017")  # type: ignore[arg-type]
    db = client.crosspostme

    try:
        # Delete test leads
        result = await db.leads.delete_many({"user_id": "user_test"})
        print(f"✅ Deleted {result.deleted_count} test leads")

        # Verify deletion
        remaining = await db.leads.count_documents({"user_id": "user_test"})
        print(f"✅ Remaining test leads: {remaining}")

    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
    finally:
        client.close()
        print("👋 Cleanup complete")


if __name__ == "__main__":
    asyncio.run(cleanup())
