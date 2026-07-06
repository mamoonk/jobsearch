import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class LocationCache(Base):
    __tablename__ = "location_cache"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    search_query = Column(String(255), unique=True, nullable=False)
    country = Column(String(100), nullable=False)
    state = Column(String(100))
    county = Column(String(100))
    city = Column(String(100))
    zipcode = Column(String(20))
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    bounding_box = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
