import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME")
POLL_INTERVAL = int(os.environ.get("METRICS_POLL_INTERVAL", "300"))


async def poll_metrics_once(db_client: Any):
    db = db_client[DB_NAME]
    # Placeholder: scan posted_ads and update metrics by querying real platform adapters
    posted = await db.posted_ads.find({}).to_list(1000)
    logger.info(f"Found {len(posted)} posted ads while polling metrics")
    now = datetime.now(timezone.utc).isoformat()
    for pa in posted:
        # Simulate a metrics update
        await db.posted_ads.update_one(
            {"id": pa.get("id")}, {"$set": {"last_polled": now}}
        )


async def main():
    if not MONGO_URL or not DB_NAME:
        logger.error("MONGO_URL or DB_NAME not set; metrics poller exiting")
        return
    client = AsyncIOMotorClient(MONGO_URL)
    try:
        while True:
            try:
                await poll_metrics_once(client)
            except Exception as e:
                logger.exception("Error while polling metrics: %s", e)
            await asyncio.sleep(POLL_INTERVAL)
    finally:
        client.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
