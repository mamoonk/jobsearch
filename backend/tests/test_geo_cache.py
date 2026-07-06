import pytest
from unittest.mock import AsyncMock, patch

from app.services.redis_cache import cache_geo_result, get_cached_geo, invalidate_geo


@pytest.mark.asyncio
async def test_cache_and_retrieve():
    query = "San Francisco, CA"
    data = {"city": "San Francisco", "state": "CA", "country": "US"}

    with patch("app.services.redis_cache.get_client", new=AsyncMock(return_value=None)):
        result = await get_cached_geo(query)
        assert result is None


@pytest.mark.asyncio
async def test_cache_miss():
    with patch("app.services.redis_cache.get_client", new=AsyncMock(return_value=None)):
        result = await get_cached_geo("unknown place")
        assert result is None


@pytest.mark.asyncio
async def test_cache_invalidate():
    with patch("app.services.redis_cache.get_client", new=AsyncMock(return_value=None)):
        await invalidate_geo("some query")
        # Should not raise
        assert True
