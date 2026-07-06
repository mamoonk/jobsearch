import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.orm import relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_source_id = Column(String(255), unique=True, nullable=False)
    source_platform = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements_clean = Column(Text)
    apply_url = Column(Text, nullable=False)
    salary_min = Column(Numeric(12, 2))
    salary_max = Column(Numeric(12, 2))
    salary_currency = Column(String(10), default="USD")
    employment_type = Column(String(50))
    workplace_modality = Column(String(30))
    country = Column(String(100))
    state = Column(String(100))
    county = Column(String(100))
    city = Column(String(100))
    zipcode = Column(String(20))
    coordinates = Column(JSONB)
    description_embedding = Column(VECTOR(1536))
    posted_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    alignments = relationship("JobAlignment", back_populates="job", cascade="all, delete-orphan")
