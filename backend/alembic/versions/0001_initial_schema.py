"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-06
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "location_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("search_query", sa.String(255), unique=True, nullable=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("state", sa.String(100)),
        sa.Column("county", sa.String(100)),
        sa.Column("city", sa.String(100)),
        sa.Column("zipcode", sa.String(20)),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("bounding_box", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("structured_json", postgresql.JSONB, nullable=False),
        sa.Column("dense_embedding", postgresql.VECTOR(1536)),
        sa.Column("is_primary", sa.Boolean, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("external_source_id", sa.String(255), unique=True, nullable=False),
        sa.Column("source_platform", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("requirements_clean", sa.Text),
        sa.Column("apply_url", sa.Text, nullable=False),
        sa.Column("salary_min", sa.Numeric(12, 2)),
        sa.Column("salary_max", sa.Numeric(12, 2)),
        sa.Column("salary_currency", sa.String(10), server_default="USD"),
        sa.Column("employment_type", sa.String(50)),
        sa.Column("workplace_modality", sa.String(30)),
        sa.Column("country", sa.String(100)),
        sa.Column("state", sa.String(100)),
        sa.Column("county", sa.String(100)),
        sa.Column("city", sa.String(100)),
        sa.Column("zipcode", sa.String(20)),
        sa.Column("coordinates", postgresql.JSONB),
        sa.Column("description_embedding", postgresql.VECTOR(1536)),
        sa.Column("posted_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "job_alignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("overall_match_score", sa.Integer, nullable=False),
        sa.Column("keyword_score", sa.Integer, nullable=False),
        sa.Column("experience_score", sa.Integer, nullable=False),
        sa.Column("semantic_score", sa.Integer, nullable=False),
        sa.Column("gap_analysis_json", postgresql.JSONB, nullable=False),
        sa.Column("generated_cover_letter", sa.Text),
        sa.Column("interview_prep_json", postgresql.JSONB),
        sa.Column("saved_status", sa.String(30), server_default="aligned"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_index("idx_jobs_embedding", "jobs", ["description_embedding"], postgresql_using="hnsw", postgresql_with={"m": 16, "ef_construction": 200}, postgresql_ops={"description_embedding": "vector_cosine_ops"})


def downgrade() -> None:
    op.drop_table("job_alignments")
    op.drop_table("jobs")
    op.drop_table("resumes")
    op.drop_table("location_cache")
    op.drop_table("users")
