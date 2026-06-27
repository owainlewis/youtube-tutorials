"""
Bad tests: tests that waste time and catch nothing.

These are the kinds of tests AI agents will happily generate
if you don't constrain them. They look productive. They aren't.
"""

import pytest


# ── Testing the Framework ───────────────────────────────────────

def test_health_endpoint_returns_200():
    """This tests FastAPI, not your code.
    FastAPI already has tests for this. You're testing their work."""
    response = client.get("/health")
    assert response.status_code == 200


def test_root_returns_json():
    """Again, testing that FastAPI can return JSON.
    It can. That's what it does."""
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"


# ── Testing Library Behavior ────────────────────────────────────

def test_json_loads_parses_json():
    """You're testing Python's json module. It works."""
    import json
    result = json.loads('{"key": "value"}')
    assert result == {"key": "value"}


def test_datetime_formats_correctly():
    """You're testing Python's datetime module.
    Standard library. Tested by thousands of people already."""
    from datetime import datetime
    dt = datetime(2026, 4, 9, 12, 0, 0)
    assert dt.isoformat() == "2026-04-09T12:00:00"


# ── Mocks Testing Mocks ────────────────────────────────────────

def test_sends_welcome_email(mock_smtp):
    """This tests that the mock was called, not that email works.
    When the real SMTP server rejects the email format,
    this test still passes. False confidence."""
    send_welcome_email("user@example.com")
    mock_smtp.send.assert_called_once()


def test_saves_to_database(mock_db):
    """This tests that mock_db.save was called.
    It tells you nothing about whether the data actually persists.
    When you change the schema, this test still passes."""
    create_candidate(name="Alice", recruiter_id=1)
    mock_db.save.assert_called_once()


# ── Implementation Detail Tests ─────────────────────────────────

def test_scorer_calls_skills_match_helper():
    """Testing that a specific internal function is called
    couples the test to the implementation. If you refactor
    the scorer to inline the logic, this test breaks
    even though the behavior is identical."""
    with patch("app.services.scorer.skills_match") as mock:
        calculate_score(candidate, job)
        mock.assert_called_once()


def test_api_calls_service_layer():
    """Same problem. You're testing the wiring, not the behavior.
    If you restructure the code, the test breaks for no reason."""
    with patch("app.services.scorer.calculate_score") as mock:
        mock.return_value = 0.8
        response = client.get("/candidates/1/score")
        mock.assert_called_once()


# ── Tautological Tests (AI's Favorite) ─────────────────────────

def test_scorer_returns_expected_value():
    """This test was written AFTER the implementation.
    The expected value (0.73) was copied from the output.
    If the scoring logic is wrong, the test confirms the wrong answer.
    It's grading its own homework."""
    candidate = Candidate(years_experience=5, skills=["python"])
    job = Job(required_skills=["python", "fastapi"])

    score = calculate_score(candidate, job)

    assert score == 0.73  # Where did 0.73 come from? The code itself.
