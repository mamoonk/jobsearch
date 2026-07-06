import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


class JobAlignment(Base):
    __tablename__ = "job_alignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    overall_match_score = Column(Integer, nullable=False)
    keyword_score = Column(Integer, nullable=False)
    experience_score = Column(Integer, nullable=False)
    semantic_score = Column(Integer, nullable=False)
    gap_analysis_json = Column(JSONB, nullable=False)
    generated_cover_letter = Column(Text)
    interview_prep_json = Column(JSONB)
    saved_status = Column(String(30), default="aligned")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="alignments")
    resume = relationship("Resume", back_populates="alignments")
    job = relationship("Job", back_populates="alignments")
