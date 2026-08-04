"""Copyable review snippets, not a runnable test module.

The undefined application names are intentional. Read each example as a test
shape to discuss, then run the complete example under ``code/``.
"""


# Narrow framework checks

def test_health_endpoint_returns_200():
    """This only proves that the route is wired and returns a status.

    Keep it when that wiring is the requirement. It does not prove the
    endpoint's business behavior.
    """
    response = client.get("/health")
    assert response.status_code == 200


def test_root_returns_json():
    """This checks response wiring, but no application-specific content."""
    response = client.get("/")
    assert response.headers["content-type"] == "application/json"


# Library behavior without application policy

def test_json_loads_parses_json():
    """This repeats documented json.loads behavior without our own policy."""
    import json

    result = json.loads('{"key": "value"}')
    assert result == {"key": "value"}


def test_datetime_formats_correctly():
    """This repeats documented datetime formatting behavior."""
    from datetime import datetime

    dt = datetime(2026, 4, 9, 12, 0, 0)
    assert dt.isoformat() == "2026-04-09T12:00:00"


# Narrow interaction checks

def test_sends_welcome_email(mock_smtp):
    """This proves the interaction contract, not successful delivery.

    Keep it when the call is the boundary under test. Add an integration check
    when delivery behavior matters.
    """
    send_welcome_email("user@example.com")
    mock_smtp.send.assert_called_once()


def test_saves_to_database(mock_db):
    """This proves the save interaction, not database persistence.

    A database integration test is needed to check schema mapping and storage.
    """
    create_candidate(name="Alice", recruiter_id=1)
    mock_db.save.assert_called_once()


# Implementation detail checks

def test_scorer_calls_skills_match_helper():
    """This couples the test to a private helper rather than the result."""
    with patch("app.services.scorer.skills_match") as mock:
        calculate_score(candidate, job)
        mock.assert_called_once()


def test_api_calls_service_layer():
    """This locks in wiring rather than the response behavior.

    Keep it only when that interaction is an intentional contract.
    """
    with patch("app.services.scorer.calculate_score") as mock:
        mock.return_value = 0.8
        response = client.get("/candidates/1/score")
        mock.assert_called_once()


# Tautological check

def test_scorer_returns_value_copied_from_current_output():
    """An unexplained expected value can preserve an existing logic error."""
    candidate = Candidate(years_experience=5, skills=["python"])
    job = Job(required_skills=["python", "fastapi"])

    score = calculate_score(candidate, job)

    assert score == 0.73  # No requirement explains this number.
