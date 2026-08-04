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

1. **Research:** Find relevant content and inspect its public performance data
2. **Analyze:** Identify videos that differ from a channel's average
3. **Learn:** Extract available transcripts for closer study
4. **Create:** Draft scripts and titles using the supplied guidance
5. **Publish:** Upload videos with reviewed metadata

---

## Tools

### search_videos

Search YouTube for videos matching a query. Useful for topic research and competitive analysis.

```bash
.venv/bin/python tools/youtube.py search_videos "QUERY" --max 25 --json
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
.venv/bin/python tools/youtube.py get_channel_videos @HANDLE --days 30 --json
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
  - `outlier_score`: Standard deviations above or below the mean
  - `is_outlier`: True if score > 2.0
  - `views_per_day`: Views divided by days since publication
  - `engagement_rate`: (likes + comments) / views

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
.venv/bin/python tools/youtube.py get_transcript VIDEO_ID
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
.venv/bin/python tools/youtube.py upload video.mp4 --metadata metadata.md
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

1. **Search broadly:** `search_videos "AI agents" --max 25`
2. **Identify repeated channels:** Note which channels appear most
3. **Analyze those channels:** `get_channel_videos @channel --days 90`
4. **Find outliers:** Inspect videos with `outlier_score > 2.0`
5. **Study transcripts:** `get_transcript VIDEO_ID` for selected videos
6. **Save findings:** Write to `workspace/research/<topic>.md`

**Output:** Research document with:
- Top performing videos and why
- Common patterns in titles/thumbnails
- Content gaps or opportunities
- Transcript excerpts worth studying

---

### 2. Write a Script

Create a video script following proven patterns.

1. **Read the guide:** `context/script-guide.md`
2. **Review research:** Check `workspace/research/` for topic insights
3. **Create project folder:** `workspace/projects/<name>/`
4. **Write script:** Save as `script.md`

**Script structure:**
- Hook (0:00-0:45): Why watch?
- Content: Deliver value
- CTA: What's next?

**Style:** Conversational, short sentences, no filler words.

---

### 3. Write Titles

Generate title options following patterns that work.

1. **Read the guide:** `context/title-guide.md`
2. **Generate options:** Mix different patterns
3. **Evaluate each:** Check clarity and searchability
4. **Pick a shortlist:** Check how each title renders
5. **Save to project:** Add to `metadata.md`

**Working patterns:**
- How to [Goal] with [Method]
- [Number] [Things] to [Goal]
- Why [Common Belief] Is Wrong
- [Claim] ([Clarifier])

---

### 4. Upload a Video

Publish with proper metadata.

1. **Copy template:** `context/templates/metadata.md`
2. **Fill in fields:**
   - Title (50-60 chars)
   - Description (first 150 chars critical)
   - Tags (5-15 relevant)
   - Timestamps
3. **Save to project:** `workspace/projects/<name>/metadata.md`
4. **User reviews:** Get approval before upload
5. **Upload as unlisted:** `upload video.mp4 --metadata metadata.md`
6. **Verify:** Check the video on YouTube
7. **Make public:** Change privacy only when ready

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
| > 2.0 | Flagged by this demo's outlier heuristic |
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

The response includes video titles, URLs, view counts, and outlier scores.

The agent selects a few videos for closer inspection and records why each one is relevant.

[Saves to: workspace/research/ai-agents.md]
```

---

## Limitations

- **API quotas:** YouTube Data API requests consume a configured project's quota
- **Transcript availability:** Some videos do not expose captions
- **Upload permissions:** OAuth credentials and channel permissions affect available actions
- **Remote failures:** Network errors and service responses still need handling
