from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import ResumeResponse, ResumeListResponse
from app.middleware.auth import get_current_user
from app.services.resume_parser import extract_text_from_pdf, transform_resume_text_to_schema
from app.services.storage_service import upload_resume, get_presigned_download_url
from app.utils.embedding import generate_text_embedding

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")

    file_bytes = await file.read()
    raw_text = extract_text_from_pdf(file_bytes)
    structured = transform_resume_text_to_schema(raw_text)
    structured_dict = structured.model_dump()

    flat = " ".join(structured_dict.get("hard_skills", [])) + " "
    flat += " ".join(
        bullet for job in structured_dict.get("employment_history", [])
        for bullet in job.get("core_impact_bullets", [])
    )
    embedding = generate_text_embedding(flat)

    storage_result = upload_resume(file_bytes, file.filename)

    existing_primary = db.query(Resume).filter(
        Resume.user_id == user.id, Resume.is_primary.is_(True)
    ).first()
    is_primary = existing_primary is None

    resume = Resume(
        user_id=user.id,
        raw_text=raw_text,
        structured_json=structured_dict,
        dense_embedding=embedding,
        storage_key=storage_result["key"],
        storage_backend=storage_result["storage"],
        is_primary=is_primary,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/", response_model=list[ResumeListResponse])
def list_resumes(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resumes = db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).all()
    result = []
    for r in resumes:
        result.append(ResumeListResponse(
            id=str(r.id),
            is_primary=r.is_primary,
            created_at=r.created_at,
            full_name=r.structured_json.get("full_name"),
        ))
    return result


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.get("/{resume_id}/download")
def download_resume(resume_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume or not resume.storage_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume file not found")

    url = get_presigned_download_url(resume.storage_key)
    if url:
        return {"download_url": url}

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate download URL")


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    db.delete(resume)
    db.commit()
