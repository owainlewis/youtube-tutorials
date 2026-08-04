# Content Repurposer: Requirements

## What It Does

A web app that takes a YouTube video URL and drafts short-form social content from it. The user pastes a link, picks a mode (tweets or longer-form notes), and gets back N drafts that use their saved writing examples as prompt context. The user reviews and edits every draft before publishing.

## Why It Exists

This app is built by a team of AI agents (backend, frontend, code reviewer) to demonstrate Anthropic's agent teams feature.

---

## Core User Flow

1. User pastes a YouTube URL and picks a mode (tweets or notes) and a count (1-10)
2. App downloads the audio via yt-dlp, transcribes it via Whisper API, and generates content via Claude
3. User sees progress as each step completes (downloading → transcribing → generating)
4. Results appear as cards with copy-to-clipboard functionality

## Features

### Generation

- **Input**: YouTube URL, mode (tweets or notes), count (1-10)
- **Pipeline**: yt-dlp audio download → OpenAI Whisper transcription → Claude content generation
- **Tweet mode**: <=280 characters, one key insight per tweet, punchy and self-contained
- **Notes mode**: 1-3 paragraphs, conversational and opinionated, 100-300 words each
- **Streaming progress**: frontend shows which step is currently running

### Style Examples

- Separate page where users can paste examples of their writing style
- Add/remove examples freely, each in its own text area
- Persisted to localStorage so they survive page reloads
- These examples are injected into the Claude prompt as few-shot examples
- Examples give the model evidence about the requested style. The user should review the result because examples do not guarantee an accurate voice match.

### Results

- Each result displayed in a card with copy-to-clipboard
- Tweet mode shows character count (green if <=280, red if over)
- Option to generate more from the same video or start fresh with a new URL

---

## Tech Stack

### Backend
- Python 3.12+, managed with `uv`
- FastAPI (async)
- yt-dlp for audio download (use as Python library, not subprocess)
- OpenAI SDK for Whisper transcription
- Anthropic SDK for Claude content generation
- Temp files for audio, cleaned up after processing

### Frontend
- Next.js (App Router) with Bun
- shadcn/ui component library
- Tailwind CSS
- Dark mode only, modern minimal aesthetic

### Layout
- Left sidebar navigation with two pages: Generate and Style Examples
- Clean, spacious design with lots of breathing room

---

## API Contract

### `POST /api/v1/generate`

```json
// Request
{
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "mode": "tweets" | "notes",
  "count": 5,
  "examples": ["Example writing snippet 1...", "Example snippet 2..."]
}

// Response (SSE stream of JSON events)
{
  "status": "downloading" | "transcribing" | "generating" | "complete" | "error",
  "progress": "Downloading audio...",
  "video_title": "How to Build AI Agents",
  "results": [
    { "id": 1, "content": "...", "char_count": 241 }
  ]
}
```

`examples` is optional. When provided, they are injected into the Claude prompt to match the user's writing style.

### `GET /api/v1/health`

Returns `{"status": "ok"}`.

---

## Prompt Strategy

The quality of the output depends heavily on the prompt. Key principles:

- Different system prompts for tweets vs notes mode
- When user provides style examples, wrap them in a clear instruction: "Match the tone, structure, and rhythm of these examples. Your output should feel like it was written by the same person."
- Generate all N items in a single Claude API call, return as JSON array
- For tweets, validate length and instruct Claude to stay under 280 chars
- Read the model identifier from configuration and use a model currently supported by the Anthropic API

---

## Environment Variables

Create a committed `.env.example` at the project root with placeholder values only. The user copies it to an untracked `.env` and fills in real values locally. The backend may load those variables with `python-dotenv` or Pydantic settings. Agents must not read, print, commit, or expose values from `.env`.

```
OPENAI_API_KEY=replace-with-your-key       # Whisper transcription
ANTHROPIC_API_KEY=replace-with-your-key    # Claude generation
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Agent Team Structure

| Agent | Role |
|-------|------|
| **backend** | Builds the FastAPI backend: audio download, transcription, generation services, API endpoint |
| **frontend** | Builds the Next.js frontend: sidebar layout, generate page, examples page, API integration |
| **reviewer** | Reviews code from both agents, ensures API contract alignment, catches bugs |

Backend and frontend work in parallel. Reviewer checks work as it's completed.

---

## Constraints

- No database: stateless
- No auth: demo app, local use only
- No caching: keep it simple
- yt-dlp must be available on the system
- Check the current transcription provider's documented file limit before upload, and handle oversized files without silently truncating them
- Minimal dependencies
