"""Calendar Agent using Pydantic AI."""

import asyncio
from datetime import datetime

from pydantic_ai import Agent, RunContext

from calendar_service import CalendarService

# =============================================================================
# Agent Setup
# =============================================================================

SYSTEM_PROMPT = f"""You are a helpful calendar assistant. You help users manage their Google Calendar.

Guidelines:
- Default meeting duration is 30 minutes
- Be concise but friendly

Today is {datetime.now().strftime("%Y-%m-%d")}.
"""

agent = Agent(
    "openai:gpt-4o",
    system_prompt=SYSTEM_PROMPT,
    deps_type=CalendarService,
)


# =============================================================================
# Tools
# =============================================================================


@agent.tool
async def list_events(ctx: RunContext[CalendarService], date: str) -> str:
    """List all events for a date (YYYY-MM-DD). Returns event IDs needed for updates/deletes."""
    events = ctx.deps.list_events(date)

    if not events:
        return f"No events on {date}."

    lines = [f"Events for {date}:"]
    for e in events:
        lines.append(f"- {e.title} (id: {e.id})")
    return "\n".join(lines)


@agent.tool
async def create_event(
    ctx: RunContext[CalendarService],
    title: str,
    date: str,
    start_time: str,
    duration_minutes: int = 30,
) -> str:
    """Create a calendar event."""
    event = ctx.deps.create_event(
        title=title,
        date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
    )
    return f"Created '{event.title}' on {date} at {start_time}."


@agent.tool
async def update_event(
    ctx: RunContext[CalendarService],
    event_id: str,
    title: str | None = None,
    date: str | None = None,
    start_time: str | None = None,
    duration_minutes: int | None = None,
) -> str:
    """Update an existing event. Use list_events first to get the event ID."""
    event = ctx.deps.update_event(
        event_id=event_id,
        title=title,
        date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
    )
    return f"Updated '{event.title}'."


@agent.tool
async def delete_event(ctx: RunContext[CalendarService], event_id: str) -> str:
    """Delete an event. Use list_events first to get the event ID."""
    ctx.deps.delete_event(event_id)
    return "Event deleted."


# =============================================================================
# CLI
# =============================================================================


async def main():
    print("Calendar Agent (Pydantic AI)")
    print("Type 'quit' to exit\n")

    try:
        service = CalendarService()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break

        result = await agent.run(user_input, deps=service, message_history=history)
        history = result.all_messages()
        print(f"Agent: {result.output}")


if __name__ == "__main__":
    asyncio.run(main())
