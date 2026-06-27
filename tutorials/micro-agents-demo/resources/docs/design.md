# YouTube Agent: Design Document

**Version**: 1.0
**Status**: Draft

---

## Overview

The YouTube Agent is a personal AI assistant for YouTube content research and publishing. It helps creators analyze what's working on the platform, study successful videos, write scripts and titles, and upload content.

---

## Goal

**Help research and manage all YouTube operations.**

Specifically:

1. **Research** — Find high-performing content and understand why it works
2. **Analyze** — Identify outlier videos that beat channel averages
3. **Learn** — Extract and study transcripts from successful creators
4. **Create** — Write scripts and titles following proven patterns
5. **Publish** — Upload videos with proper metadata

---

## Tools

### search_videos

Search YouTube for videos matching a query. Useful for topic research and competitive analysis.

```bash
uv run tools/youtube.py search_videos "QUERY" --max 25 --json
```

| Option | Description | Default |
|--------|-------------|---------|
| `--max` | Maximum results | 25 |
| `--days` | Filter to recent N days | None |
| `--order` | Sort by: `relevance`, `view_count`, `date` | relevance |
| `--json` | Output as JSON | false |

**Returns:**
- Total result count
- Average views across results
- Top channels appearing in results
- Video list with: title, URL, channel, views, engagement rate

**Use cases:**
- "What videos exist on [topic]?"
- "Who are the top creators in [niche]?"
- "What's trending in the last 7 days?"

---

### get_channel_videos

Fetch videos from a specific channel with performance metrics and outlier detection.

```bash
uv run tools/youtube.py get_channel_videos @HANDLE --days 30 --json
```

| Option | Description | Default |
|--------|-------------|---------|
| `--days` | Days to look back | 30 |
| `--max` | Maximum videos | 50 |
| `--json` | Output as JSON | false |

**Returns:**
- Channel name and stats
- Average views and standard deviation
- Videos sorted by outlier score
- Each video includes:
  - `outlier_score` — Standard deviations above/below mean
  - `is_outlier` — True if score > 2.0
  - `views_per_day` — Velocity metric
  - `engagement_rate` — (likes + comments) / views

**Outlier Analysis:**

Videos with `outlier_score > 2.0` performed significantly above channel average. These are worth studying:
- What was the title/thumbnail?
- What topic did they cover?
- How was the video structured?

**Use cases:**
- "What's working for @mkbhd lately?"
- "Find outlier videos from competitors"
- "Analyze my own channel performance"

---

### get_transcript

Download the transcript/captions from a video for analysis.

```bash
uv run tools/youtube.py get_transcript VIDEO_ID
```

| Option | Description | Default |
|--------|-------------|---------|
| `--max-chars` | Truncate transcript length | 5000 |
| `--json` | Output as JSON | false |

**Returns:**
- Video ID
- Language detected
- Whether captions are auto-generated
- Full transcript text

**Use cases:**
- "How did they structure this video?"
- "What hooks do top creators use?"
- "Extract key points from a video"

---

### upload

Upload a video to YouTube with metadata.

```bash
uv run tools/youtube.py upload video.mp4 --metadata metadata.md
```

| Option | Description | Default |
|--------|-------------|---------|
| `--metadata` | Path to metadata file (.md or .yaml) | None |
| `--title` | Video title (if no metadata file) | Required |
| `--description` | Video description | "" |
| `--tags` | Comma-separated tags | None |
| `--category` | YouTube category ID | 22 |
| `--privacy` | `private`, `unlisted`, `public` | private |
| `--thumbnail` | Path to thumbnail image | None |
| `--json` | Output as JSON | false |

**Metadata File Format:**

```yaml
---
title: My Video Title
tags: [ai, python, tutorial]
privacy: unlisted
thumbnail: thumb.jpg
---

Video description goes here.
Supports multiple lines.
```

**Important:** Always upload as `unlisted` first, review, then change to `public`.

---

## Workflows

### 1. Research a Topic

Understand the landscape before creating content.

1. **Search broadly** — `search_videos "AI agents" --max 25`
2. **Identify top channels** — Note which channels appear most
3. **Analyze those channels** — `get_channel_videos @channel --days 90`
4. **Find outliers** — Videos with `outlier_score > 2.0`
5. **Study transcripts** — `get_transcript VIDEO_ID` for top performers
6. **Save findings** — Write to `workspace/research/<topic>.md`

**Output:** Research document with:
- Top performing videos and why
- Common patterns in titles/thumbnails
- Content gaps or opportunities
- Transcript excerpts worth studying

---

### 2. Write a Script

Create a video script following proven patterns.

1. **Read the guide** — `context/script-guide.md`
2. **Review research** — Check `workspace/research/` for topic insights
3. **Create project folder** — `workspace/projects/<name>/`
4. **Write script** — Save as `script.md`

**Script structure:**
- Hook (0:00-0:45) — Why watch?
- Content — Deliver value
- CTA — What's next?

**Style:** Conversational, short sentences, no filler words.

---

### 3. Write Titles

Generate title options following patterns that work.

1. **Read the guide** — `context/title-guide.md`
2. **Generate 10 options** — Mix different patterns
3. **Evaluate each** — Curiosity + clarity + searchability
4. **Pick top 3** — Check length (50-60 chars)
5. **Save to project** — Add to `metadata.md`

**Working patterns:**
- How to [Goal] with [Method]
- [Number] [Things] to [Goal]
- Why [Common Belief] Is Wrong
- [Claim] ([Clarifier])

---

### 4. Upload a Video

Publish with proper metadata.

1. **Copy template** — `context/templates/metadata.md`
2. **Fill in fields:**
   - Title (50-60 chars)
   - Description (first 150 chars critical)
   - Tags (5-15 relevant)
   - Timestamps
3. **Save to project** — `workspace/projects/<name>/metadata.md`
4. **User reviews** — Get approval before upload
5. **Upload as unlisted** — `upload video.mp4 --metadata metadata.md`
6. **Verify** — Check the video on YouTube
7. **Make public** — Change privacy setting when ready

---

## Workspace Structure

```
workspace/
├── projects/           # Video production folders
│   └── <project-name>/
│       ├── research.md     # Topic research
│       ├── script.md       # Video script
│       └── metadata.md     # Upload metadata
│
├── research/           # General topic research
│   └── <topic>.md
│
└── transcripts/        # Downloaded transcripts
    └── <video_id>.md
```

**Conventions:**
- One folder per video project
- Use kebab-case for folder names
- Transcripts named by video ID for easy lookup

---

## Context Files

Reference documentation the agent reads before tasks.

| File | Purpose |
|------|---------|
| `context/script-guide.md` | How to structure and write scripts |
| `context/title-guide.md` | Patterns for effective titles |
| `context/templates/metadata.md` | Upload metadata template |

---

## Environment Setup

### Required

```bash
export YOUTUBE_API_KEY=your_api_key
```

Get from [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials.

### For Upload (OAuth)

```bash
export YOUTUBE_CLIENT_SECRETS=/path/to/client_secrets.json
```

1. Create OAuth 2.0 credentials in Google Cloud Console
2. Download as `client_secrets.json`
3. First upload will open browser for authorization
4. Token saved to `~/.youtube-agent/token.json`

---

## Metrics & Analysis

### Outlier Score

Measures how far a video's views deviate from channel average:

```
outlier_score = (video_views - channel_avg) / standard_deviation
```

| Score | Interpretation |
|-------|----------------|
| > 2.0 | Significant outlier — study this |
| 1.0 - 2.0 | Above average |
| -1.0 - 1.0 | Normal performance |
| < -1.0 | Below average |

### Engagement Rate

```
engagement_rate = (likes + comments) / views
```

Higher engagement suggests content resonates beyond just impressions.

### Views Per Day

```
views_per_day = total_views / days_since_publish
```

Normalizes for video age. Useful for comparing recent vs older videos.

---

## Example Session

```
User: Research what's working for AI agent content on YouTube

Agent: I'll search for AI agent videos and analyze top channels.

[Runs: search_videos "AI agents tutorial" --max 25 --json]
[Runs: get_channel_videos @XXX --days 90 --json]
[Runs: get_channel_videos @XXX --days 90 --json]

Found 3 outlier videos worth studying:
1. "Build AI Agents with Just Two Files" — 4.2x average
2. "Why LangChain Is Overkill" — 3.1x average
3. "The Simplest Agent Framework" — 2.8x average

Common patterns:
- Contrarian takes on frameworks
- "Simple" and "minimal" in titles
- 10-15 minute length

[Saves to: workspace/research/ai-agents.md]
```

---

## Limitations

- **API Quotas** — YouTube Data API has daily limits (10,000 units)
- **Transcript Availability** — Some videos have captions disabled
- **Upload Verification** — Must be verified channel for custom thumbnails
- **Rate Limits** — Don't hammer the API; batch operations when possible
