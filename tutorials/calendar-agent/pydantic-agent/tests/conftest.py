"""Shared test fixtures."""

import pytest

from calendar_service import CalendarService


@pytest.fixture
def calendar_service():
    """Provide a CalendarService instance for tests."""
    return CalendarService()
