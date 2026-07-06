import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import VECTOR
from sqlalchemy.orm import relationship

from app.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    raw_text = Column(Text, nullable=False)
    structured_json = Column(JSONB, nullable=False)
    dense_embedding = Column(VECTOR(1536))
    is_primary = Column(Boolean, default=False)
    storage_key = Column(String(512))
    storage_backend = Column(String(20), default="local")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="resumes")
    alignments = relationship("JobAlignment", back_populates="resume", cascade="all, delete-orphan")
