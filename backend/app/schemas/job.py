from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class JobResponse(BaseModel):
    id: str
    external_source_id: str
    source_platform: str
    title: str
    company_name: str
    description: str
    apply_url: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    salary_currency: str = "USD"
    employment_type: Optional[str] = None
    workplace_modality: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    posted_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class JobSearchResponse(BaseModel):
    id: str
    title: str
    company_name: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    workplace_modality: Optional[str] = None
    employment_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    posted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
