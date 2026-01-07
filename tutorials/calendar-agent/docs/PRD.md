# Calendar Agent PRD

## Overview

A conversational AI agent that helps users manage their Google Calendar. The agent can view schedules, create, update, and delete events.

This agent will be implemented across multiple AI frameworks to demonstrate their different approaches:
- Pydantic AI (Python)
- LangGraph (Python)
- Vercel AI SDK (TypeScript)
- Google ADK (Python)
- Spring AI (Java)

All implementations share a common calendar service layer and exhibit identical user-facing behavior.

---

## Goals

1. **Teach agent fundamentals** — Tool use, conversation state, dependency injection
2. **Show framework differences** — Same behavior, different implementations
3. **Keep it simple** — Minimal complexity to focus on framework patterns
4. **Be runnable** — Real Google Calendar integration, not mocks

---

## Agent Capabilities

### Tools

| Tool | Description |
|------|-------------|
| `list_events` | Show all events for a given date (returns event IDs) |
| `create_event` | Schedule a new meeting |
| `update_event` | Modify an existing event (requires event ID) |
| `delete_event` | Remove an event (requires event ID) |

### Supported Queries

The agent should handle natural language requests including:

- "What's on my calendar tomorrow?"
- "Schedule a 1:1 with Jamie tomorrow at 3pm"
- "Cancel my 2pm meeting"
- "Move my standup to 9:30am"

---

## Conversation Flows

### Flow 1: View Schedule

```
User: "What do I have tomorrow?"

Agent: [calls list_events]
       "Tomorrow you have 3 events:
        - Team Standup (id: abc123)
        - Design Review (id: def456)
        - 1:1 with Sarah (id: ghi789)"
```

### Flow 2: Create Event

```
User: "Schedule a 1:1 with Jamie tomorrow at 3pm"

Agent: [calls create_event]
       "Created '1:1 with Jamie' on 2025-01-16 at 15:00."
```

### Flow 3: Delete Event

```
User: "Cancel my 2pm meeting tomorrow"

Agent: [calls list_events to find the meeting]
       [calls delete_event with the event ID]
       "Event deleted."
```

### Flow 4: Update Event

```
User: "Move my standup to 9:30am"

Agent: [calls list_events to find standup]
       [calls update_event with new time]
       "Updated 'Team Standup'."
```

---

## Calendar Service Interface

All framework implementations share this service interface. Implementations should use the official Google Calendar API.

### Dependencies

**Python:**
```
google-auth-oauthlib
google-api-python-client
```

**TypeScript:**
```
googleapis
```

**Java:**
```
com.google.api-client
com.google.oauth-client
com.google.apis:google-api-services-calendar
```

### Authentication

- OAuth 2.0 with offline access
- Credentials stored in `credentials.json`
- Tokens cached in `token.json`
- Scopes: `https://www.googleapis.com/auth/calendar`

### Service Methods

```
list_events(date: string) -> Event[]
    List all events for a given date.

    Parameters:
        date: ISO date string (YYYY-MM-DD)

    Returns:
        Array of events with: id, title, start, end

create_event(title: string, date: string, start_time: string, duration_minutes: int) -> Event
    Create a new calendar event.

    Parameters:
        title: Event title
        date: ISO date string (YYYY-MM-DD)
        start_time: 24-hour time (HH:MM)
        duration_minutes: Length of meeting (default: 30)

    Returns:
        Created event with: id, title, start, end

update_event(event_id: string, title?: string, date?: string, start_time?: string, duration_minutes?: int) -> Event
    Update an existing event.

    Parameters:
        event_id: Google Calendar event ID
        title: Optional new title
        date: Optional new date (YYYY-MM-DD)
        start_time: Optional new time (HH:MM)
        duration_minutes: Optional new duration

    Returns:
        Updated event

delete_event(event_id: string) -> void
    Delete an event.

    Parameters:
        event_id: Google Calendar event ID
```

### Data Types

```
Event {
    id: string
    title: string
    start: string (ISO datetime)
    end: string (ISO datetime)
}
```

---

## Agent Configuration

### Model

Use Claude Sonnet (or equivalent) for all implementations:
- Anthropic: `claude-sonnet-4-20250514`
- OpenAI (if needed): `gpt-4o`
- Google (for ADK): `gemini-2.0-flash`

### System Prompt

```
You are a helpful calendar assistant. You help users manage their Google Calendar.

Guidelines:
- Default meeting duration is 30 minutes
- Be concise but friendly

Today is {current_date}.
```

### Default Values

| Parameter | Default |
|-----------|---------|
| Meeting duration | 30 minutes |
| Calendar | primary |
| Timezone | UTC |

---

## Implementation Requirements

### All Frameworks

1. **Calendar service** — Implement the service interface for the framework's language
2. **Interactive CLI** — Simple chat loop for testing
3. **Conversation history** — Maintain context within a session
4. **Error handling** — Graceful handling of API errors

### Framework-Specific

#### Pydantic AI (Python)
- Use `@agent.tool` decorator for tools
- Use `RunContext` for dependency injection
- Use `deps_type` for calendar service

#### LangGraph (Python)
- Define tools with `@tool` decorator
- Use `MemorySaver` for checkpointing
- Bind tools to model with `bind_tools()`

#### Vercel AI SDK (TypeScript)
- Use `generateText` with tools
- Use Zod for tool parameter validation
- Use `maxSteps` for multi-turn tool use

#### Google ADK (Python)
- Use ADK's native tool definition format
- Use `FunctionTool` for calendar operations

#### Spring AI (Java)
- Use Spring AI's function calling
- Implement as Spring Boot application
- Use Spring's dependency injection for calendar service

---

## File Structure

```
calendar-agent/
├── README.md
├── docs/
│   ├── PRD.md
│   └── google-credentials-setup.md
│
├── pydantic-agent/
│   ├── pyproject.toml
│   ├── calendar_service.py
│   └── agent.py
│
├── langgraph-agent/
│   ├── pyproject.toml
│   ├── calendar_service.py
│   └── agent.py
│
├── vercel-agent/
│   ├── package.json
│   ├── calendar-service.ts
│   └── agent.ts
│
├── google-adk-agent/
│   ├── pyproject.toml
│   ├── calendar_service.py
│   └── agent.py
│
└── spring-agent/
    ├── pom.xml
    └── src/main/java/
        ├── CalendarService.java
        └── Agent.java
```

---

## Success Criteria

An implementation is complete when it:

1. ✅ Can list events for a date
2. ✅ Can create new events
3. ✅ Can update existing events
4. ✅ Can delete events
5. ✅ Runs as interactive CLI
6. ✅ Maintains conversation context within a session

---

## Out of Scope

- Human-in-the-loop confirmation (keep it simple)
- Conflict/availability checking
- Attendees and invites
- Multi-calendar support
- Recurring events
- Web UI
- Timezone conversion