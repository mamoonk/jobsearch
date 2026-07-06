import pytest
from unittest.mock import AsyncMock, patch

from app.services.job_ingestion import GlobalJobIngestionAdapter


@pytest.fixture
def adapter():
    return GlobalJobIngestionAdapter()


@pytest.mark.asyncio
async def test_fetch_jobs_global_theirstack(adapter):
    geo_data = {"country": "US", "state": "CA", "city": "San Francisco"}

    with patch.object(adapter, "_fetch_theirstack", new=AsyncMock(return_value=[])):
        with patch.object(adapter, "_fetch_serp_api_google_jobs", new=AsyncMock(return_value=[])):
            result = await adapter.fetch_jobs_global("engineer", geo_data)
            assert result == []


@pytest.mark.asyncio
async def test_theirstack_fallback_to_serpapi(adapter):
    geo_data = {"country": "US", "state": "NY", "city": "New York"}

    serp_result = [
        {
            "external_source_id": "serp_1",
            "source_platform": "SerpApi_GoogleJobs",
            "title": "Test Engineer",
            "company_name": "TestCorp",
            "description": "A test job",
            "apply_url": "https://example.com/apply",
            "salary_min": None,
            "salary_max": None,
            "employment_type": "Full-time",
            "workplace_modality": "Onsite",
            "country": "US",
            "state": "NY",
            "city": "New York",
            "zipcode": None,
        }
    ]

    with patch.object(adapter, "_fetch_theirstack", new=AsyncMock(return_value=[])):
        with patch.object(adapter, "_fetch_serp_api_google_jobs", new=AsyncMock(return_value=serp_result)):
            result = await adapter.fetch_jobs_global("engineer", geo_data)
            assert len(result) == 1
            assert result[0]["external_source_id"] == "serp_1"
            assert result[0]["company_name"] == "TestCorp"


def test_normalize_theirstack(adapter):
    items = [
        {
            "id": 123,
            "job_title": "Senior Engineer",
            "company_name": "Acme",
            "job_description": "Do things",
            "url": "https://acme.com/job",
            "salary_min": 100000,
            "salary_max": 150000,
            "employment_type": "Full-time",
            "job_type": "Remote",
            "country": "US",
            "admin_region_1": "CA",
            "admin_region_2": "Los Angeles",
            "city": "Los Angeles",
            "postal_code": "90001",
        }
    ]
    result = adapter._normalize_theirstack_payload(items)
    assert len(result) == 1
    assert result[0]["source_platform"] == "TheirStack"
    assert result[0]["title"] == "Senior Engineer"
    assert result[0]["salary_min"] == 100000
