# YouTube Agent

A YouTube research and publishing agent for analyzing channels, finding high-performing content patterns, and uploading videos.

## Quick Reference

| Task | Command |
|------|---------|
| Analyze channel | `uv run scripts/youtube.py get_channel_videos @HANDLE --days 30` |
| Search videos | `uv run scripts/youtube.py search_videos "QUERY" --max 25` |
| Get transcript | `uv run scripts/youtube.py get_transcript VIDEO_ID` |
| Upload video | `uv run scripts/youtube.py upload video.mp4 --metadata metadata.md` |

## Environment Setup

```bash
export YOUTUBE_API_KEY=your_api_key              # Required for research
export YOUTUBE_CLIENT_SECRETS=/path/to/client_secrets.json  # Required for uploads
```

## Research Commands

### Analyze Channel Videos

Find outlier videos from a channel. Outliers are videos performing 2+ standard deviations above the channel average—these reveal what resonates with the audience.

```bash
uv run scripts/youtube.py get_channel_videos @mkbhd --days 30 --json
```

| Option | Default | Description |
|--------|---------|-------------|
| `--days N` | 30 | Days to look back |
| `--max N` | 50 | Maximum videos to fetch |
| `--json` | off | Structured output for processing |

### Search Videos

Search YouTube for videos matching a query across all channels.

```bash
uv run scripts/youtube.py search_videos "AI agents tutorial" --order view_count --max 20 --json
```

| Option | Default | Description |
|--------|---------|-------------|
| `--max N` | 25 | Maximum results |
| `--days N` | none | Filter to recent videos only |
| `--order` | relevance | Sort: `relevance`, `view_count`, `date` |
| `--json` | off | Structured output for processing |

### Get Transcript

Extract video transcript for content analysis. Useful for understanding video structure, hooks, and talking points.

```bash
uv run scripts/youtube.py get_transcript dQw4w9WgXcQ --json
```

Extract the VIDEO_ID from URLs: `youtube.com/watch?v=VIDEO_ID`

## Publishing

### Upload Workflow

1. **Create metadata** — Copy `docs/description_template.md` and fill in details
2. **Human review** — User edits title, description, tags
3. **Upload** — Always start as unlisted for final review

```bash
uv run scripts/youtube.py upload video.mp4 --metadata video.md --thumbnail thumb.jpg
```

### Metadata File Format (Markdown)

```markdown
---
title: "Video Title Here"
tags: [ai, agents, tutorial]
privacy: unlisted
---

First 150 chars hook with primary keyword.

Full description continues here...

TIMESTAMPS
0:00 - Intro
```

The frontmatter contains title, tags, privacy. The body becomes the description.

### Inline Upload (Quick)

For simple uploads without a metadata file:

```bash
uv run scripts/youtube.py upload video.mp4 \
  --title "Video Title" \
  --description "Description here" \
  --thumbnail thumb.jpg \
  --privacy unlisted
```

## Key Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| `outlier_score` | Std devs above channel avg | >2.0 = outlier, worth studying |
| `is_outlier` | outlier_score > 2.0 | Boolean flag for filtering |
| `engagement_rate` | (likes + comments) / views | Audience interaction quality |
| `views_per_day` | views / days_since_publish | Velocity indicator |

## Best Practices

- Always use `--json` when processing results programmatically
- Default uploads to `--privacy unlisted` until human review is complete
- Outlier videos often share common title patterns worth analyzing
- Check `docs/` for templates before writing any metadata

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API errors | Verify `YOUTUBE_API_KEY` is set and valid |
| Upload fails | Check `YOUTUBE_CLIENT_SECRETS` path and OAuth setup |
| No transcript | Video may not have captions enabled |
| Empty results | Try broader search terms or longer `--days` window |
