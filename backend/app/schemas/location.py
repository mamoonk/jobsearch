from typing import Optional
from pydantic import BaseModel


class LocationSuggestion(BaseModel):
    search_query: str
    country: str
    state: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    zipcode: Optional[str] = None
    latitude: float
    longitude: float
    bounding_box: Optional[dict] = None


class GeoSearchRequest(BaseModel):
    keyword: str
    location_query: str
    limit: int = 25
