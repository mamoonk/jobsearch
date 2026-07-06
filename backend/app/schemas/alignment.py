from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class GapAnalysis(BaseModel):
    detected_matching_keywords: List[str]
    missing_critical_competencies: List[str]
    total_candidate_months: int
    target_required_months: int


class SubScores(BaseModel):
    keyword_score: int
    experience_score: int
    semantic_score: int


class AlignmentResponse(BaseModel):
    id: str
    user_id: str
    resume_id: str
    job_id: str
    overall_match_score: int
    keyword_score: int
    experience_score: int
    semantic_score: int
    gap_analysis_json: GapAnalysis
    generated_cover_letter: Optional[str] = None
    interview_prep_json: Optional[list] = None
    saved_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlignmentCreate(BaseModel):
    job_id: str
    resume_id: str
