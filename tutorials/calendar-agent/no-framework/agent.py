"""Calendar Agent WITHOUT any framework - just the OpenAI API.

This demonstrates that AI agents are fundamentally simple:
1. Send messages to an LLM with tool definitions
2. If the LLM wants to call tools, execute them
3. Send results back to the LLM
4. Repeat until done
"""

import json
from datetime import datetime

from openai import OpenAI

from calendar_service import CalendarService

# =============================================================================
# Tool Definitions (OpenAI function calling format)
# =============================================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_events",
            "description": "List all events for a date. Returns event IDs needed for updates/deletes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format",
                    }
                },
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Create a calendar event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Event title"},
                    "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "start_time": {"type": "string", "description": "Start time in HH:MM format"},
                    "duration_minutes": {
                        "type": "integer",
                        "description": "Duration in minutes (default 30)",
                        "default": 30,
                    },
                },
                "required": ["title", "date", "start_time"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_event",
            "description": "Update an existing event. Use list_events first to get the event ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID from list_events"},
                    "title": {"type": "string", "description": "New title (optional)"},
                    "date": {"type": "string", "description": "New date in YYYY-MM-DD (optional)"},
                    "start_time": {"type": "string", "description": "New start time in HH:MM (optional)"},
                    "duration_minutes": {"type": "integer", "description": "New duration in minutes (optional)"},
                },
                "required": ["event_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Delete an event. Use list_events first to get the event ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID from list_events"},
                },
                "required": ["event_id"],
            },
        },
    },
]


# =============================================================================
# Tool Implementations
# =============================================================================


def execute_tool(service: CalendarService, name: str, args: dict) -> str:
    """Execute a tool and return the result as a string."""
    if name == "list_events":
        events = service.list_events(args["date"])
        if not events:
            return f"No events on {args['date']}."
        lines = [f"Events for {args['date']}:"]
        for e in events:
            lines.append(f"- {e.title} (id: {e.id})")
        return "\n".join(lines)

    elif name == "create_event":
        event = service.create_event(
            title=args["title"],
            date=args["date"],
            start_time=args["start_time"],
            duration_minutes=args.get("duration_minutes", 30),
        )
        return f"Created '{event.title}' on {args['date']} at {args['start_time']}."

    elif name == "update_event":
        event = service.update_event(
            event_id=args["event_id"],
            title=args.get("title"),
            date=args.get("date"),
            start_time=args.get("start_time"),
            duration_minutes=args.get("duration_minutes"),
        )
        return f"Updated '{event.title}'."

    elif name == "delete_event":
        service.delete_event(args["event_id"])
        return "Event deleted."

    else:
        return f"Unknown tool: {name}"


# =============================================================================
# The Agent Loop - This is the core of any AI agent
# =============================================================================


def run_agent(client: OpenAI, service: CalendarService, messages: list) -> str:
    """
    The agent loop:
    1. Call the LLM with messages and tools
    2. If it wants to use tools, execute them and add results
    3. Repeat until it responds with text (no tool calls)
    """
    while True:
        # Call the LLM
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
        )

        message = response.choices[0].message

        # Add the assistant's response to history
        messages.append(message)

        # If no tool calls, we're done - return the text response
        if not message.tool_calls:
            return message.content

        # Execute each tool call
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"  [Tool: {name}({args})]")

            result = execute_tool(service, name, args)

            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


# =============================================================================
# CLI
# =============================================================================


def main():
    print("Calendar Agent (No Framework)")
    print("Type 'quit' to exit\n")

    try:
        service = CalendarService()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    client = OpenAI()

    system_prompt = f"""You are a helpful calendar assistant. You help users manage their Google Calendar.

Guidelines:
- Default meeting duration is 30 minutes
- Be concise but friendly

Today is {datetime.now().strftime("%Y-%m-%d")}."""

    messages = [{"role": "system", "content": system_prompt}]

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

        messages.append({"role": "user", "content": user_input})

        response = run_agent(client, service, messages)
        print(f"Agent: {response}")


if __name__ == "__main__":
    main()
