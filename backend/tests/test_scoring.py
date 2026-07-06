import pytest


def test_keyword_score_logic():
    from app.services.scoring_engine import CoreAlignmentScoringEngine

    engine = CoreAlignmentScoringEngine()
    resume = {
        "hard_skills": ["Python", "Docker", "SQL"],
        "soft_skills": [],
        "employment_history": [
            {
                "role_title": "Engineer",
                "company": "Acme",
                "duration_months": 24,
                "core_impact_bullets": ["Built APIs"],
            }
        ],
    }
    job = {
        "description": "We need Python and Docker expertise with SQL knowledge",
        "expected_experience_months": 12,
    }

    result = engine.compute_alignment(resume, job)
    assert 0 <= result["overall_match_score"] <= 100
    assert "Python" in result["gap_log"]["detected_matching_keywords"]

    # The semantic score requires OpenAI embedding - skip that assertion
    assert result["sub_scores"]["keyword_score"] >= 60  # 3/5 min skill match = 60%
    assert result["sub_scores"]["experience_score"] == 100  # 24mo >= 12mo
    assert result["gap_log"]["total_candidate_months"] == 24
    assert result["gap_log"]["target_required_months"] == 12


def test_keyword_score_zero():
    from app.services.scoring_engine import CoreAlignmentScoringEngine

    engine = CoreAlignmentScoringEngine()
    resume = {
        "hard_skills": [],
        "soft_skills": [],
        "employment_history": [],
    }
    job = {"description": "Some text", "expected_experience_months": 36}
    result = engine.compute_alignment(resume, job)
    assert result["sub_scores"]["keyword_score"] == 0
    assert result["sub_scores"]["experience_score"] == 0
