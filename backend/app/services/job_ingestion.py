from typing import Dict, Any, List, Optional

import httpx

from app.config import settings


class GlobalJobIngestionAdapter:
    def __init__(self):
        self.ts_key = settings.theirstack_api_key
        self.sa_key = settings.serpapi_api_key

    async def fetch_jobs_global(
        self, keyword: str, geo_data: Dict[str, Any], limit: int = 50
    ) -> List[Dict[str, Any]]:
        jobs = await self._fetch_theirstack(keyword, geo_data, limit)
        if not jobs:
            jobs = await self._fetch_serp_api_google_jobs(keyword, geo_data)
        return jobs

    async def _fetch_theirstack(
        self, keyword: str, geo_data: Dict[str, Any], limit: int = 50
    ) -> List[Dict[str, Any]]:
        payload = {
            "page": 0,
            "limit": limit,
            "blur_company_name": False,
            "search_term": keyword,
            "country": geo_data.get("country"),
            "region": geo_data.get("state"),
            "county": geo_data.get("county"),
            "city": geo_data.get("city"),
            "postal_code": geo_data.get("zipcode"),
        }
        headers = {"Authorization": f"Bearer {self.ts_key}", "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    "https://api.theirstack.com/v1/jobs/search",
                    json=payload,
                    headers=headers,
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json().get("data", [])
                    if data:
                        return self._normalize_theirstack_payload(data)
            except httpx.RequestError:
                pass
        return []

    def _normalize_theirstack_payload(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        normalized = []
        for item in items:
            normalized.append({
                "external_source_id": str(item.get("id")),
                "source_platform": "TheirStack",
                "title": item.get("job_title"),
                "company_name": item.get("company_name"),
                "description": item.get("job_description"),
                "apply_url": item.get("url"),
                "salary_min": item.get("salary_min"),
                "salary_max": item.get("salary_max"),
                "employment_type": item.get("employment_type"),
                "workplace_modality": item.get("job_type"),
                "country": item.get("country"),
                "state": item.get("admin_region_1"),
                "county": item.get("admin_region_2"),
                "city": item.get("city"),
                "zipcode": item.get("postal_code"),
            })
        return normalized

    async def _fetch_serp_api_google_jobs(
        self, keyword: str, geo_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        loc_string = " ".join(filter(None, [
            geo_data.get("city", ""),
            geo_data.get("state", ""),
            geo_data.get("country", ""),
        ])).strip()
        if not loc_string:
            loc_string = geo_data.get("country", "")

        params = {
            "engine": "google_jobs",
            "q": keyword,
            "location": loc_string,
            "api_key": self.sa_key,
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get("https://serpapi.com/search", params=params, timeout=15)
                if resp.status_code == 200:
                    jobs_list = resp.json().get("jobs_results", [])
                    return [
                        {
                            "external_source_id": j.get("job_id", str(hash(j.get("title", "") + j.get("company_name", "")))),
                            "source_platform": "SerpApi_GoogleJobs",
                            "title": j.get("title"),
                            "company_name": j.get("company_name"),
                            "description": j.get("description"),
                            "apply_url": j.get("via_link") or j.get("link") or "",
                            "salary_min": None,
                            "salary_max": None,
                            "employment_type": j.get("detected_extensions", {}).get("schedule_type"),
                            "workplace_modality": "Onsite",
                            "country": geo_data.get("country"),
                            "state": geo_data.get("state"),
                            "county": geo_data.get("county"),
                            "city": geo_data.get("city"),
                            "zipcode": geo_data.get("zipcode"),
                        }
                        for j in jobs_list
                    ]
            except httpx.RequestError:
                pass
        return []
