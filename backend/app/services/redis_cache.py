import json
import logging
from typing import Optional

from app.config import settings

logger = logging.getLogger("redis_cache")

try:
    import redis.asyncio as aioredis

    _redis_available = bool(settings.redis_host)
except ImportError:
    _redis_available = False

_client = None
TTL_SECONDS = 86400  # 24h


async def get_client():
    global _client
    if _client is None and _redis_available:
        try:
            _client = aioredis.Redis(host=settings.redis_host, port=settings.redis_port)
            await _client.ping()
            logger.info("Connected to Redis for geo-caching")
        except Exception as e:
            logger.warning("Redis unavailable, geo-cache will be disabled: %s", e)
            _client = None
    return _client


async def cache_geo_result(query: str, data: dict) -> None:
    client = await get_client()
    if client:
        key = f"geo:{query.lower().strip()}"
        try:
            await client.setex(key, TTL_SECONDS, json.dumps(data))
        except Exception as e:
            logger.debug("Redis set failed: %s", e)


async def get_cached_geo(query: str) -> Optional[dict]:
    client = await get_client()
    if client:
        key = f"geo:{query.lower().strip()}"
        try:
            raw = await client.get(key)
            if raw:
                return json.loads(raw)
        except Exception as e:
            logger.debug("Redis get failed: %s", e)
    return None


async def invalidate_geo(query: str) -> None:
    client = await get_client()
    if client:
        key = f"geo:{query.lower().strip()}"
        try:
            await client.delete(key)
        except Exception as e:
            logger.debug("Redis delete failed: %s", e)
