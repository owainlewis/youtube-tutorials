# Calendar Agent

A conversational AI agent that helps manage Google Calendar. Implemented across multiple AI frameworks to demonstrate different approaches.

## Setup

### 1. Google Calendar API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Calendar API**
4. Go to **Credentials** → **Create Credentials** → **OAuth Client ID**
5. Select **Desktop Application**
6. Download the JSON file as `credentials.json`

### 2. Anthropic API Key

```bash
export ANTHROPIC_API_KEY=your_api_key
```

## Implementations

Each implementation is self-contained with its own dependencies.

### Pydantic AI

```bash
cd pydantic-agent
cp /path/to/credentials.json .
uv run agent.py
```

On first run, a browser window opens for Google OAuth. Tokens are cached in `token.json`.

## Usage Examples

```
You: What's on my calendar tomorrow?
Agent: Events for 2025-01-08:
- Team Standup (9:00am-9:30am)
- Design Review (11:00am-12:00pm)

You: Am I free at 3pm tomorrow?
Agent: You're free on 2025-01-08 at 15:00 for 30 minutes.

You: Schedule a 1:1 with Jamie tomorrow at 3pm
Agent: I'll create '1:1 with Jamie' on 2025-01-08 at 15:00 for 30 minutes.

Should I book this? (y/n)

You: y
Agent: Done! Scheduled '1:1 with Jamie' for 2025-01-08 at 15:00.
Link: https://calendar.google.com/...
```

## Project Structure

```
calendar-agent/
├── pydantic-agent/          # Pydantic AI implementation
│   ├── pyproject.toml
│   ├── calendar_service.py
│   └── agent.py
├── langgraph-agent/         # Coming soon
├── vercel-ai-agent/         # Coming soon
├── google-adk-agent/        # Coming soon
└── spring-ai-agent/         # Coming soon
```

## Framework Comparison

| Framework | Language | Human-in-the-loop |
|-----------|----------|-------------------|
| Pydantic AI | Python | Proposal pattern via tools |
| LangGraph | Python | `interrupt()` function |
| Vercel AI SDK | TypeScript | Multi-step flow |
| Google ADK | Python | Callback mechanism |
| Spring AI | Java | Function calling |
