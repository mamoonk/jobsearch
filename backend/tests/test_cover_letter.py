import pytest
from unittest.mock import AsyncMock, patch

from app.services.cover_letter_generator import generate_cover_letter


@pytest.mark.asyncio
async def test_generate_cover_letter_no_api_key():
    with patch("app.services.cover_letter_generator.settings.openai_api_key", ""):
        with patch("app.services.cover_letter_generator.client.chat.completions.create") as mock_create:
            mock_create.return_value.choices[0].message.content = "Test cover letter"

            result = await generate_cover_letter(
                company_name="Acme",
                job_title="Engineer",
                job_description="Do stuff",
                candidate_resume_summary="Skilled in Python",
                alignment_gaps_json='{"missing": []}',
            )
            assert result == "Test cover letter"


@pytest.mark.asyncio
async def test_generate_cover_letter_empty():
    with patch("app.services.cover_letter_generator.client.chat.completions.create") as mock_create:
        mock_create.return_value.choices[0].message.content = ""

        result = await generate_cover_letter(
            company_name="Co",
            job_title="Role",
            job_description="Desc",
            candidate_resume_summary="Sum",
            alignment_gaps_json="{}",
        )
        assert result == ""
