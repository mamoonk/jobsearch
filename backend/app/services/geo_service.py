from typing import Dict, Any, Optional

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.location_cache import LocationCache
from app.services.redis_cache import cache_geo_result, get_cached_geo


class GeoService:
    def __init__(self):
        self.api_key = settings.geoapify_api_key
        self.base_url = "https://api.geoapify.com/v1"

    async def autocomplete(self, query: str) -> list[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            params = {
                "text": query,
                "apiKey": self.api_key,
                "type": "city",
                "limit": 5,
                "format": "json",
            }
            resp = await client.get(f"{self.base_url}/geocode/autocomplete", params=params, timeout=10)
            resp.raise_for_status()
            results = resp.json()
            suggestions = []
            for feature in results.get("features", []):
                props = feature.get("properties", {})
                suggestions.append({
                    "search_query": props.get("formatted", query),
                    "country": props.get("country", ""),
                    "state": props.get("state", ""),
                    "county": props.get("county", ""),
                    "city": props.get("city", ""),
                    "zipcode": props.get("postcode", ""),
                    "latitude": props.get("lat", 0),
                    "longitude": props.get("lon", 0),
                    "bounding_box": feature.get("bbox"),
                })
            return suggestions

    async def geocode(self, query: str) -> Optional[Dict[str, Any]]:
        cached = await get_cached_geo(query)
        if cached:
            return cached

        async with httpx.AsyncClient() as client:
            params = {"text": query, "apiKey": self.api_key, "limit": 1, "format": "json"}
            resp = await client.get(f"{self.base_url}/geocode/search", params=params, timeout=10)
            resp.raise_for_status()
            results = resp.json()
            features = results.get("features", [])
            if not features:
                return None
            props = features[0].get("properties", {})
            data = {
                "search_query": props.get("formatted", query),
                "country": props.get("country", ""),
                "state": props.get("state", ""),
                "county": props.get("county", ""),
                "city": props.get("city", ""),
                "zipcode": props.get("postcode", ""),
                "latitude": props.get("lat", 0),
                "longitude": props.get("lon", 0),
                "bounding_box": features[0].get("bbox"),
            }

            await cache_geo_result(query, data)
            return data

    def resolve_from_cache(self, db: Session, query: str) -> Optional[LocationCache]:
        return db.query(LocationCache).filter(LocationCache.search_query == query.lower().strip()).first()

    def cache_location(self, db: Session, data: Dict[str, Any]) -> LocationCache:
        entry = LocationCache(
            search_query=data["search_query"].lower().strip(),
            country=data["country"],
            state=data.get("state"),
            county=data.get("county"),
            city=data.get("city"),
            zipcode=data.get("zipcode"),
            latitude=data["latitude"],
            longitude=data["longitude"],
            bounding_box=data.get("bounding_box"),
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
