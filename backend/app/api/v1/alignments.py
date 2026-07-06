from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.models.job import Job
from app.models.alignment import JobAlignment
from app.schemas.alignment import AlignmentResponse, AlignmentCreate
from app.middleware.auth import get_current_user
from app.services.scoring_engine import CoreAlignmentScoringEngine

router = APIRouter()
scoring_engine = CoreAlignmentScoringEngine()


@router.post("/", response_model=AlignmentResponse, status_code=status.HTTP_201_CREATED)
def create_alignment(
    req: AlignmentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = db.query(Resume).filter(Resume.id == req.resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    result = scoring_engine.compute_alignment(
        resume.structured_json,
        {
            "description": job.description,
            "expected_experience_months": 36,
        },
    )

    alignment = JobAlignment(
        user_id=user.id,
        resume_id=resume.id,
        job_id=job.id,
        overall_match_score=result["overall_match_score"],
        keyword_score=result["sub_scores"]["keyword_score"],
        experience_score=result["sub_scores"]["experience_score"],
        semantic_score=result["sub_scores"]["semantic_score"],
        gap_analysis_json=result["gap_log"],
    )
    db.add(alignment)
    db.commit()
    db.refresh(alignment)
    return alignment


@router.get("/", response_model=list[AlignmentResponse])
def list_alignments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return (
        db.query(JobAlignment)
        .filter(JobAlignment.user_id == user.id)
        .order_by(JobAlignment.created_at.desc())
        .all()
    )


@router.get("/{alignment_id}", response_model=AlignmentResponse)
def get_alignment(
    alignment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alignment = db.query(JobAlignment).filter(
        JobAlignment.id == alignment_id, JobAlignment.user_id == user.id
    ).first()
    if not alignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alignment not found")
    return alignment


@router.patch("/{alignment_id}/status")
def update_status(
    alignment_id: str,
    status_value: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alignment = db.query(JobAlignment).filter(
        JobAlignment.id == alignment_id, JobAlignment.user_id == user.id
    ).first()
    if not alignment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alignment not found")
    alignment.saved_status = status_value
    db.commit()
    return {"status": status_value}
