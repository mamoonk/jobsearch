import asyncio
import logging

import redis.asyncio as redis

from app.config import settings
from app.services.cron_ingestion import run_daily_ingestion

logger = logging.getLogger("worker")


async def schedule_daily_ingestion():
    while True:
        logger.info("Running daily job ingestion...")
        try:
            await run_daily_ingestion()
        except Exception as e:
            logger.error("Daily ingestion failed: %s", e)
        await asyncio.sleep(86400)


async def main():
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port)
    logger.info("Worker connected to Redis at %s:%s", settings.redis_host, settings.redis_port)

    async def listener():
        pubsub = r.pubsub()
        await pubsub.subscribe("job:ingest")
        async for message in pubsub.listen():
            if message["type"] == "message":
                logger.info("Received manual trigger: %s", message["data"])
                await run_daily_ingestion()

    await asyncio.gather(schedule_daily_ingestion(), listener())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
    asyncio.run(main())
