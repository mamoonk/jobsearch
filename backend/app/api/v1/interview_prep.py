import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.alignment import JobAlignment
from app.models.job import Job
from app.models.resume import Resume
from app.middleware.auth import get_current_user
from app.services.interview_prep import generate_interview_prep
from app.services.resume_parser import summarize_resume_for_prompts

router = APIRouter()


@router.post("/{alignment_id}")
async def create_interview_prep(
    alignment_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alignment = db.query(JobAlignment).filter(
        JobAlignment.id == alignment_id, JobAlignment.user_id == user.id
    ).first()
    if not alignment:
        raise HTTPException(status_code=404, detail="Alignment not found")

    job = db.query(Job).filter(Job.id == alignment.job_id).first()
    resume = db.query(Resume).filter(Resume.id == alignment.resume_id).first()
    if not job or not resume:
        raise HTTPException(status_code=404, detail="Job or Resume not found")

    questions = await generate_interview_prep(
        job_title=job.title,
        job_description=job.description,
        candidate_resume_summary=summarize_resume_for_prompts(resume.structured_json),
        alignment_gaps_json=json.dumps(alignment.gap_analysis_json),
    )

    alignment.interview_prep_json = questions
    db.commit()
    return {"questions": questions}
