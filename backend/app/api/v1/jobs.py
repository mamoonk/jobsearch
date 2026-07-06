from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobResponse, JobSearchResponse

router = APIRouter()


@router.get("/", response_model=list[JobSearchResponse])
def list_jobs(
    page: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    jobs = (
        db.query(Job)
        .order_by(Job.posted_at.desc().nullslast())
        .offset(page * limit)
        .limit(limit)
        .all()
    )
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job
