from typing import List, Dict, Any

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.embedding import generate_text_embedding


BASELINE_MARKET_TERMS = [
    "React", "TypeScript", "Python", "AWS", "Docker",
    "Kubernetes", "SQL", "CI/CD", "NoSQL",
]


class CoreAlignmentScoringEngine:
    def compute_alignment(
        self, structured_resume: Dict[str, Any], job_record: Dict[str, Any]
    ) -> Dict[str, Any]:
        job_description_lower = (job_record.get("description") or "").lower()
        hard_skills = structured_resume.get("hard_skills", [])
        employment_history = structured_resume.get("employment_history", [])

        # LAYER 1: Hard skill keyword overlap (30%)
        matched_keywords = [
            skill for skill in hard_skills
            if skill.lower() in job_description_lower
        ]
        keyword_score = int((len(matched_keywords) / max(len(hard_skills), 5)) * 100) if hard_skills else 0
        keyword_score = min(keyword_score, 100)

        # LAYER 2: Experience delta (30%)
        total_months = sum(exp.get("duration_months", 0) for exp in employment_history)
        target_months = job_record.get("expected_experience_months", 36)
        if total_months >= target_months:
            experience_score = 100
        else:
            experience_score = int((total_months / target_months) * 100) if target_months else 0

        # LAYER 3: Cosine similarity (40%)
        flattened_resume = " ".join(hard_skills) + " "
        flattened_resume += " ".join(
            bullet for job in employment_history for bullet in job.get("core_impact_bullets", [])
        )
        resume_vec = np.array(generate_text_embedding(flattened_resume)).reshape(1, -1)
        job_vec = np.array(generate_text_embedding(job_record["description"])).reshape(1, -1)
        similarity = cosine_similarity(resume_vec, job_vec)[0][0]
        semantic_score = int(((similarity + 1) / 2) * 100)

        # Aggregate
        overall = int(keyword_score * 0.30 + experience_score * 0.30 + semantic_score * 0.40)

        # Gap analysis
        missing_skills = [
            term for term in BASELINE_MARKET_TERMS
            if term.lower() in job_description_lower
            and term.lower() not in [s.lower() for s in hard_skills]
        ]

        return {
            "overall_match_score": max(0, min(overall, 100)),
            "sub_scores": {
                "keyword_score": keyword_score,
                "experience_score": experience_score,
                "semantic_score": semantic_score,
            },
            "gap_log": {
                "detected_matching_keywords": matched_keywords,
                "missing_critical_competencies": missing_skills,
                "total_candidate_months": total_months,
                "target_required_months": target_months,
            },
        }
