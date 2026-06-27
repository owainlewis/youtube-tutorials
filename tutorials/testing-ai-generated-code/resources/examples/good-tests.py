"""
Good tests: test YOUR logic, not someone else's code.

These examples show tests that catch real bugs,
define security boundaries, and protect business logic.
"""

import pytest


# ── Business Logic ──────────────────────────────────────────────

def test_scorer_zero_experience_perfect_skills():
    """Candidate with no experience but perfect skill match
    should still score above 0.5 because skills outweigh tenure."""
    candidate = Candidate(years_experience=0, skills=["python", "fastapi", "postgresql"])
    job = Job(required_skills=["python", "fastapi", "postgresql"])

    score = calculate_score(candidate, job)

    assert score > 0.5
    assert score < 1.0  # Not a perfect score without experience


def test_scorer_no_matching_skills():
    """Candidate with zero skill overlap should score near zero
    regardless of experience."""
    candidate = Candidate(years_experience=15, skills=["java", "spring"])
    job = Job(required_skills=["python", "fastapi", "postgresql"])

    score = calculate_score(candidate, job)

    assert score < 0.2


def test_scorer_empty_job_description():
    """Job with no required skills should not crash.
    Should return a neutral score."""
    candidate = Candidate(years_experience=5, skills=["python"])
    job = Job(required_skills=[])

    score = calculate_score(candidate, job)

    assert score == 0.5  # Neutral when nothing to match against


# ── Security Boundaries ────────────────────────────────────────

def test_recruiter_cannot_see_other_recruiters_candidates():
    """Data isolation: recruiter A should never see recruiter B's candidates."""
    recruiter_a = create_recruiter("alice@company.com")
    recruiter_b = create_recruiter("bob@company.com")
    candidate = create_candidate(recruiter_id=recruiter_b.id)

    response = client.get("/candidates", headers=auth_headers(recruiter_a))

    candidate_ids = [c["id"] for c in response.json()]
    assert candidate.id not in candidate_ids


def test_wrong_password_returns_401():
    """Incorrect password should return 401 and no token."""
    create_user("user@example.com", password="correct-password")

    response = client.post("/auth/login", json={
        "email": "user@example.com",
        "password": "wrong-password"
    })

    assert response.status_code == 401
    assert "token" not in response.json()


def test_expired_token_rejected():
    """An expired JWT should return 401, not silently succeed."""
    token = create_token("user@example.com", expires_in=-60)  # Already expired

    response = client.get("/candidates", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


# ── Edge Cases AI Typically Misses ──────────────────────────────

def test_normalizer_handles_none_input():
    """Normalizer should return empty string for None, not crash."""
    result = normalize_text(None)
    assert result == ""


def test_normalizer_handles_unicode():
    """Job titles with unicode characters should normalize cleanly."""
    result = normalize_text("Senior Entwickler (m/w/d)")
    assert isinstance(result, str)
    assert len(result) > 0


def test_search_empty_query_returns_empty():
    """Empty search query should return empty results, not all records."""
    response = client.get("/search", params={"q": ""})
    assert response.json() == []


# ── Error Recovery ──────────────────────────────────────────────

def test_external_api_failure_returns_empty_list():
    """When the job board API returns 500, we return an empty list,
    not an unhandled exception."""
    with mock_job_board_api(status_code=500):
        results = fetch_jobs("python developer")

    assert results == []


def test_external_api_timeout_returns_empty_list():
    """When the job board API times out, we return an empty list."""
    with mock_job_board_api(timeout=True):
        results = fetch_jobs("python developer")

    assert results == []
