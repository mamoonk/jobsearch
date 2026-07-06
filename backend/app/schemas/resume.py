from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class WorkHistoryItem(BaseModel):
    role_title: str
    company: str
    duration_months: int
    core_impact_bullets: List[str]


class EncapsulatedProfileSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    hard_skills: List[str]
    soft_skills: List[str]
    employment_history: List[WorkHistoryItem]


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    raw_text: str
    structured_json: EncapsulatedProfileSchema
    is_primary: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ResumeListResponse(BaseModel):
    id: str
    is_primary: bool
    created_at: datetime
    full_name: Optional[str] = None

    model_config = {"from_attributes": True}
