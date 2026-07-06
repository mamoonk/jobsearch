from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.location_cache import LocationCache
from app.schemas.job import JobSearchResponse
from app.schemas.location import LocationSuggestion
from app.services.geo_service import GeoService
from app.services.job_ingestion import GlobalJobIngestionAdapter
from app.utils.embedding import generate_text_embedding

router = APIRouter()
geo_service = GeoService()
job_adapter = GlobalJobIngestionAdapter()


@router.get("/autocomplete", response_model=list[LocationSuggestion])
async def autocomplete_location(q: str = Query(min_length=2)):
    if not q:
        return []
    return await geo_service.autocomplete(q)


@router.post("/jobs", response_model=list[JobSearchResponse])
async def search_jobs(
    keyword: str = Query(min_length=1),
    location: str = Query(min_length=1),
    db: Session = Depends(get_db),
):
    # Resolve location
    cached = geo_service.resolve_from_cache(db, location)
    if cached:
        geo_data = {
            "country": cached.country,
            "state": cached.state,
            "county": cached.county,
            "city": cached.city,
            "zipcode": cached.zipcode,
        }
    else:
        result = await geo_service.geocode(location)
        if not result:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not resolve location")
        geo_data = result
        geo_service.cache_location(db, result)

    # Fetch from APIs
    raw_jobs = await job_adapter.fetch_jobs_global(keyword, geo_data)

    saved_jobs = []
    for raw in raw_jobs:
        existing = db.query(Job).filter(Job.external_source_id == raw["external_source_id"]).first()
        if existing:
            saved_jobs.append(existing)
            continue

        desc = raw.get("description", "")
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
        db.refresh(job)
        saved_jobs.append(job)

    return saved_jobs
