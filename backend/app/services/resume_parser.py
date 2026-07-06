from typing import List, Optional

import openai
import pdfplumber

from app.config import settings
from app.schemas.resume import EncapsulatedProfileSchema, WorkHistoryItem
from app.middleware.pii_redaction import redact_pii

_client: Optional[openai.OpenAI] = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        _client = openai.OpenAI(api_key=settings.openai_api_key)
    return _client


def extract_text_from_pdf(file_bytes: bytes) -> str:
    text_parts: List[str] = []
    with pdfplumber.open(file_bytes) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def transform_resume_text_to_schema(raw_text: str) -> EncapsulatedProfileSchema:
    if not settings.openai_api_key:
        return EncapsulatedProfileSchema(
            full_name=None,
            email=None,
            hard_skills=[],
            soft_skills=[],
            employment_history=[],
        )

    safe_text = redact_pii(raw_text)
    client = _get_client()
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a rigid ATS pipeline ingestion compiler. "
                    "Extract all core entity attributes from the raw resume text input "
                    "and map them cleanly into the requested structural schema formats without modification."
                ),
            },
            {"role": "user", "content": safe_text},
        ],
        response_format=EncapsulatedProfileSchema,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Failed to parse resume text into structured schema")
    return parsed


def summarize_resume_for_prompts(schema: EncapsulatedProfileSchema) -> str:
    lines = [f"Candidate: {schema.full_name or 'N/A'}"]
    if schema.hard_skills:
        lines.append(f"Technical Skills: {', '.join(schema.hard_skills)}")
    if schema.soft_skills:
        lines.append(f"Soft Skills: {', '.join(schema.soft_skills)}")
    for exp in schema.employment_history:
        bullets = "; ".join(exp.core_impact_bullets)
        lines.append(f"- {exp.role_title} at {exp.company} ({exp.duration_months}mo): {bullets}")
    return "\n".join(lines)
