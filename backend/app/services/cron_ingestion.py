import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal
from app.models.job import Job
from app.services.job_ingestion import GlobalJobIngestionAdapter
from app.utils.embedding import generate_text_embedding

logger = logging.getLogger("cron.ingestion")

GEO_TARGETS = [
    {"country": "US", "state": "California", "city": "San Francisco"},
    {"country": "US", "state": "New York", "city": "New York"},
    {"country": "US", "state": "Washington", "city": "Seattle"},
    {"country": "US", "state": "Texas", "city": "Austin"},
    {"country": "GB", "city": "London"},
    {"country": "DE", "city": "Berlin"},
    {"country": "CA", "state": "Ontario", "city": "Toronto"},
]

JOB_KEYWORDS = [
    "software engineer",
    "data scientist",
    "product manager",
    "devops engineer",
    "frontend developer",
    "backend developer",
    "machine learning engineer",
]


async def run_daily_ingestion():
    logger.info("Starting daily job ingestion")
    adapter = GlobalJobIngestionAdapter()
    db = SessionLocal()

    try:
        for geo in GEO_TARGETS:
            for keyword in JOB_KEYWORDS:
                try:
                    raw_jobs = await adapter.fetch_jobs_global(keyword, geo, limit=25)
                    for raw in raw_jobs:
                        existing = db.query(Job).filter(
                            Job.external_source_id == raw["external_source_id"]
                        ).first()
                        if existing:
                            continue

                        desc = raw.get("description") or ""
                        embedding = generate_text_embedding(desc) if desc else None

                        job = Job(
                            external_source_id=raw["external_source_id"],
                            source_platform=raw["source_platform"],
                            title=raw["title"],
                            company_name=raw["company_name"],
                            description=desc,
                            apply_url=raw["apply_url"],
                            salary_min=raw.get("salary_min"),
                            salary_max=raw.get("salary_max"),
                            employment_type=raw.get("employment_type"),
                            workplace_modality=raw.get("workplace_modality"),
                            country=raw.get("country"),
                            state=raw.get("state"),
                            county=raw.get("county"),
                            city=raw.get("city"),
                            zipcode=raw.get("zipcode"),
                            description_embedding=embedding,
                        )
                        db.add(job)

                    db.commit()
                    logger.info(
                        "Ingested %d jobs for keyword=%s location=%s",
                        len(raw_jobs), keyword, geo.get("city", geo.get("country")),
                    )
                    await asyncio.sleep(1)
                except Exception as e:
                    logger.error("Failed ingestion for %s %s: %s", keyword, geo, e)
                    db.rollback()
    finally:
        db.close()

    logger.info("Daily ingestion complete")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_daily_ingestion())
