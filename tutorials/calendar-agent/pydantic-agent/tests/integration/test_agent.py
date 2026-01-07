"""Integration tests for the calendar agent."""

import pytest
from datetime import datetime

from agent import agent
from calendar_service import CalendarService


@pytest.fixture
def calendar_service():
    """Provide a CalendarService instance."""
    return CalendarService()


@pytest.mark.asyncio
async def test_list_events(calendar_service):
    """Test that the agent can list calendar events."""
    today = datetime.now().strftime("%Y-%m-%d")

    result = await agent.run(
        f"What events do I have on {today}?",
        deps=calendar_service,
    )

    assert result.output is not None
