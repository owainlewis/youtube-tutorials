#!/usr/bin/env python3
# /// script
# dependencies = [
#   "google-api-python-client>=2.150.0",
#   "google-auth-oauthlib>=1.0.0",
#   "youtube-transcript-api>=0.6.0",
#   "pyyaml>=6.0",
# ]
# ///
"""
YouTube Tool - Research, search, and upload videos.

Usage:
    uv run youtube.py get_channel_videos @mkbhd --days 30
    uv run youtube.py search_videos "AI agents" --max 20
    uv run youtube.py get_transcript VIDEO_ID
    uv run youtube.py upload video.mp4 --title "My Video" --description "..."

Environment:
    YOUTUBE_API_KEY - Required for research commands.
    YOUTUBE_CLIENT_SECRETS - Path to OAuth client_secrets.json (for upload).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


# =============================================================================
# Helpers
# =============================================================================


def parse_markdown_metadata(content: str) -> dict:
    """Parse markdown file with YAML frontmatter.

    Format:
        ---
        title: My Video
        tags: [a, b, c]
        privacy: unlisted
        thumbnail: thumb.jpg
        ---

        Description body here...

    Returns:
        Dict with frontmatter fields + 'description' from body
    """
    # Match YAML frontmatter between --- markers
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        # No frontmatter, treat entire content as description
        return {"description": content.strip()}

    frontmatter_str, body = match.groups()

    try:
        metadata = yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError:
        metadata = {}

    metadata["description"] = body.strip()
    return metadata


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Video:
    """A YouTube video with computed metrics."""

    video_id: str
    title: str
    url: str
    channel_name: str
    published_at: str
    view_count: int
    like_count: int
    comment_count: int
    engagement_rate: float
    views_per_day: float
    outlier_score: float | None = None
    is_outlier: bool | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class ChannelInfo:
    """Information about a YouTube channel."""

    channel_id: str
    name: str
    subscriber_count: int
    total_video_count: int
    handle: str | None = None


@dataclass
class ChannelVideosResponse:
    """Response from get_channel_videos."""

    channel_name: str
    period_days: int
    total_videos: int
    avg_views: float
    std_dev_views: float
    videos: list[Video]


@dataclass
class SearchResponse:
    """Response from search_videos."""

    query: str
    total_results: int
    avg_views: float
    top_channels: list[dict]
    videos: list[Video]


# =============================================================================
# YouTube Service
# =============================================================================


class YouTubeService:
    """YouTube Data API v3 wrapper providing research tools."""

    def __init__(self, api_key: str):
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def resolve_channel(self, channel_input: str) -> ChannelInfo | dict:
        """Resolve a channel from @handle, URL, or channel ID."""
        try:
            channel_id = self._parse_channel_input(channel_input)
            if channel_id is None:
                return {"error": f"Could not parse channel input: {channel_input}"}

            if channel_id.startswith("@"):
                search_response = (
                    self.youtube.search()
                    .list(part="snippet", q=channel_id, type="channel", maxResults=1)
                    .execute()
                )
                if not search_response.get("items"):
                    return {"error": f"Channel not found: {channel_id}"}
                channel_id = search_response["items"][0]["snippet"]["channelId"]

            response = (
                self.youtube.channels()
                .list(part="snippet,statistics", id=channel_id)
                .execute()
            )

            if not response.get("items"):
                return {"error": f"Channel not found: {channel_id}"}

            item = response["items"][0]
            snippet = item["snippet"]
            stats = item["statistics"]

            return ChannelInfo(
                channel_id=item["id"],
                handle=snippet.get("customUrl"),
                name=snippet["title"],
                subscriber_count=int(stats.get("subscriberCount", 0)),
                total_video_count=int(stats.get("videoCount", 0)),
            )

        except HttpError as e:
            return {"error": f"YouTube API error: {e.reason}"}
        except Exception as e:
            return {"error": f"Error resolving channel: {str(e)}"}

    def get_channel_videos(
        self, channel_id: str, days_back: int = 30, max_results: int = 50
    ) -> ChannelVideosResponse | dict:
        """Get videos from a channel with performance metrics and outlier analysis."""
        try:
            channel_response = (
                self.youtube.channels().list(part="snippet", id=channel_id).execute()
            )
            if not channel_response.get("items"):
                return {"error": f"Channel not found: {channel_id}"}

            channel_name = channel_response["items"][0]["snippet"]["title"]
            published_after = datetime.now(timezone.utc) - timedelta(days=days_back)

            search_response = (
                self.youtube.search()
                .list(
                    part="id",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    publishedAfter=published_after.isoformat(),
                    maxResults=max_results,
                )
                .execute()
            )

            video_ids = [
                item["id"]["videoId"] for item in search_response.get("items", [])
            ]

            if not video_ids:
                return ChannelVideosResponse(
                    channel_name=channel_name,
                    period_days=days_back,
                    total_videos=0,
                    avg_views=0.0,
                    std_dev_views=0.0,
                    videos=[],
                )

            videos = self._fetch_video_details(video_ids)

            if not videos:
                return ChannelVideosResponse(
                    channel_name=channel_name,
                    period_days=days_back,
                    total_videos=0,
                    avg_views=0.0,
                    std_dev_views=0.0,
                    videos=[],
                )

            view_counts = [v.view_count for v in videos]
            avg_views = statistics.mean(view_counts)
            std_dev_views = (
                statistics.stdev(view_counts) if len(view_counts) > 1 else 0.0
            )

            for video in videos:
                if std_dev_views > 0:
                    video.outlier_score = round(
                        (video.view_count - avg_views) / std_dev_views, 2
                    )
                    video.is_outlier = video.outlier_score > 2.0
                else:
                    video.outlier_score = 0.0
                    video.is_outlier = False

            videos.sort(key=lambda v: v.outlier_score or 0, reverse=True)

            return ChannelVideosResponse(
                channel_name=channel_name,
                period_days=days_back,
                total_videos=len(videos),
                avg_views=round(avg_views, 2),
                std_dev_views=round(std_dev_views, 2),
                videos=videos,
            )

        except HttpError as e:
            return {"error": f"YouTube API error: {e.reason}"}
        except Exception as e:
            return {"error": f"Error fetching channel videos: {str(e)}"}

    def search_videos(
        self,
        query: str,
        max_results: int = 25,
        days_back: int | None = None,
        order_by: str = "relevance",
    ) -> SearchResponse | dict:
        """Search YouTube videos by keyword."""
        try:
            order_map = {
                "relevance": "relevance",
                "view_count": "viewCount",
                "date": "date",
            }
            order = order_map.get(order_by, "relevance")

            search_params: dict[str, Any] = {
                "part": "id",
                "q": query,
                "type": "video",
                "order": order,
                "maxResults": max_results,
            }

            if days_back is not None:
                published_after = datetime.now(timezone.utc) - timedelta(days=days_back)
                search_params["publishedAfter"] = published_after.isoformat()

            search_response = self.youtube.search().list(**search_params).execute()

            total_results = search_response.get("pageInfo", {}).get("totalResults", 0)
            video_ids = [
                item["id"]["videoId"] for item in search_response.get("items", [])
            ]

            if not video_ids:
                return SearchResponse(
                    query=query,
                    total_results=0,
                    avg_views=0.0,
                    top_channels=[],
                    videos=[],
                )

            videos = self._fetch_video_details(video_ids)
            avg_views = (
                statistics.mean([v.view_count for v in videos]) if videos else 0.0
            )

            channel_counts: dict[str, int] = {}
            for video in videos:
                channel_counts[video.channel_name] = (
                    channel_counts.get(video.channel_name, 0) + 1
                )

            top_channels = [
                {"name": name, "video_count": count}
                for name, count in sorted(
                    channel_counts.items(), key=lambda x: x[1], reverse=True
                )[:5]
            ]

            return SearchResponse(
                query=query,
                total_results=total_results,
                avg_views=round(avg_views, 2),
                top_channels=top_channels,
                videos=videos,
            )

        except HttpError as e:
            return {"error": f"YouTube API error: {e.reason}"}
        except Exception as e:
            return {"error": f"Error searching videos: {str(e)}"}

    def get_transcript(self, video_id: str, max_chars: int = 5000) -> dict:
        """Get video transcript/captions."""
        try:
            api = YouTubeTranscriptApi()
            # Try English first, then fall back to any available language
            try:
                transcript = api.fetch(video_id, languages=["en"])
                language = "en"
            except NoTranscriptFound:
                # Fall back to first available transcript
                transcript_list = api.list(video_id)
                transcript = transcript_list.find_transcript(
                    [t.language_code for t in transcript_list]
                ).fetch()
                language = transcript_list[0].language_code if transcript_list else "unknown"

            full_text = " ".join([snippet.text for snippet in transcript])

            if len(full_text) > max_chars:
                full_text = full_text[:max_chars] + "... [truncated]"

            return {
                "video_id": video_id,
                "language": language,
                "is_generated": getattr(transcript, 'is_generated', False),
                "transcript": full_text,
            }

        except TranscriptsDisabled:
            return {"error": f"Transcripts are disabled for video: {video_id}"}
        except NoTranscriptFound:
            return {"error": f"No transcript found for video: {video_id}"}
        except VideoUnavailable:
            return {"error": f"Video unavailable: {video_id}"}
        except Exception as e:
            return {"error": f"Error fetching transcript: {str(e)}"}

    def _parse_channel_input(self, channel_input: str) -> str | None:
        """Parse channel input and return channel ID or @handle."""
        channel_input = channel_input.strip()

        if channel_input.startswith("@"):
            return channel_input

        url_patterns = [
            r"(?:https?://)?(?:www\.)?youtube\.com/@([\w-]+)",
            r"(?:https?://)?(?:www\.)?youtube\.com/channel/(UC[\w-]+)",
            r"(?:https?://)?(?:www\.)?youtube\.com/c/([\w-]+)",
        ]

        for pattern in url_patterns:
            match = re.match(pattern, channel_input)
            if match:
                result = match.group(1)
                if not result.startswith("UC"):
                    return f"@{result}"
                return result

        if channel_input.startswith("UC"):
            return channel_input

        if re.match(r"^[\w-]+$", channel_input):
            return f"@{channel_input}"

        return None

    def _fetch_video_details(self, video_ids: list[str]) -> list[Video]:
        """Fetch detailed video information for a list of video IDs."""
        videos = []

        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i : i + 50]

            response = (
                self.youtube.videos()
                .list(part="snippet,statistics", id=",".join(batch_ids))
                .execute()
            )

            for item in response.get("items", []):
                video = self._parse_video_item(item)
                if video:
                    videos.append(video)

        return videos

    def _parse_video_item(self, item: dict) -> Video | None:
        """Parse a YouTube API video item into a Video."""
        try:
            snippet = item["snippet"]
            stats = item.get("statistics", {})

            video_id = item["id"]
            published_at = datetime.fromisoformat(
                snippet["publishedAt"].replace("Z", "+00:00")
            )

            view_count = int(stats.get("viewCount", 0))
            like_count = int(stats.get("likeCount", 0))
            comment_count = int(stats.get("commentCount", 0))

            engagement_rate = 0.0
            if view_count > 0:
                engagement_rate = (like_count + comment_count) / view_count

            days_since_published = (datetime.now(timezone.utc) - published_at).days
            views_per_day = view_count / max(days_since_published, 1)

            return Video(
                video_id=video_id,
                title=snippet["title"],
                url=f"https://www.youtube.com/watch?v={video_id}",
                channel_name=snippet["channelTitle"],
                published_at=published_at.isoformat(),
                view_count=view_count,
                like_count=like_count,
                comment_count=comment_count,
                engagement_rate=round(engagement_rate, 4),
                views_per_day=round(views_per_day, 2),
                tags=snippet.get("tags", []),
            )
        except (KeyError, ValueError):
            return None


# =============================================================================
# YouTube Uploader (OAuth)
# =============================================================================

# OAuth scopes for uploading
UPLOAD_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]

DEFAULT_TOKEN_PATH = Path.home() / ".youtube-agent" / "token.json"


class YouTubeUploader:
    """YouTube uploader using OAuth credentials."""

    def __init__(
        self,
        client_secrets_path: Path,
        token_path: Path = DEFAULT_TOKEN_PATH,
    ):
        self.client_secrets_path = Path(client_secrets_path)
        self.token_path = Path(token_path)

        if not self.client_secrets_path.exists():
            raise FileNotFoundError(
                f"Client secrets not found: {self.client_secrets_path}\n"
                "Download OAuth credentials from Google Cloud Console."
            )

        self.credentials = self._get_credentials()
        self.youtube = build("youtube", "v3", credentials=self.credentials)

    def _get_credentials(self) -> Credentials:
        """Get or refresh OAuth credentials."""
        credentials = None

        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                str(self.token_path), UPLOAD_SCOPES
            )

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_path), UPLOAD_SCOPES
                )
                credentials = flow.run_local_server(port=0)

            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, "w") as f:
                f.write(credentials.to_json())

        return credentials

    def upload(
        self,
        video_path: Path,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        category_id: str = "22",  # People & Blogs
        privacy: str = "private",
        thumbnail_path: Path | None = None,
    ) -> dict:
        """Upload a video to YouTube.

        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID (22 = People & Blogs, 10 = Music)
            privacy: private, unlisted, or public
            thumbnail_path: Optional thumbnail image

        Returns:
            Dict with video_id and url
        """
        video_path = Path(video_path)
        if not video_path.exists():
            return {"error": f"Video file not found: {video_path}"}

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(
            str(video_path),
            mimetype="video/mp4",
            resumable=True,
            chunksize=1024 * 1024,
        )

        try:
            request = self.youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Upload progress: {int(status.progress() * 100)}%")

            video_id = response["id"]

            if thumbnail_path:
                self.set_thumbnail(video_id, thumbnail_path)

            return {
                "video_id": video_id,
                "url": f"https://youtube.com/watch?v={video_id}",
                "title": title,
                "privacy": privacy,
            }

        except HttpError as e:
            return {"error": f"Upload failed: {e.reason}"}
        except Exception as e:
            return {"error": f"Upload failed: {str(e)}"}

    def set_thumbnail(self, video_id: str, thumbnail_path: Path) -> dict:
        """Set custom thumbnail for a video."""
        thumbnail_path = Path(thumbnail_path)
        if not thumbnail_path.exists():
            return {"error": f"Thumbnail not found: {thumbnail_path}"}

        # Detect mimetype from file extension
        ext = thumbnail_path.suffix.lower()
        mimetype_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg"}
        mimetype = mimetype_map.get(ext, "image/png")

        try:
            media = MediaFileUpload(str(thumbnail_path), mimetype=mimetype)
            self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media,
            ).execute()
            return {"success": True, "video_id": video_id}

        except HttpError as e:
            return {"error": f"Thumbnail failed: {e.reason}"}
        except Exception as e:
            return {"error": f"Thumbnail failed: {str(e)}"}


# =============================================================================
# Output Formatters
# =============================================================================


def format_number(n: int | float) -> str:
    """Format large numbers for display (e.g., 1.2M, 45K)."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


def print_channel_videos(result: ChannelVideosResponse) -> None:
    """Pretty print channel videos result."""
    print(f"\n{'=' * 60}")
    print(f"Channel: {result.channel_name}")
    print(f"Period: Last {result.period_days} days")
    print(f"Videos: {result.total_videos}")
    print(f"Avg Views: {format_number(result.avg_views)}")
    print(f"{'=' * 60}\n")

    if not result.videos:
        print("No videos found in this period.")
        return

    print("Top Videos by Outlier Score:\n")
    for i, video in enumerate(result.videos[:10], 1):
        outlier = f"[OUTLIER {video.outlier_score:.1f}x]" if video.is_outlier else ""
        print(f"{i}. {video.title}")
        print(f"   Views: {format_number(video.view_count)} | "
              f"Engagement: {video.engagement_rate:.2%} | "
              f"Score: {video.outlier_score:.2f} {outlier}")
        print(f"   {video.url}\n")


def print_search_results(result: SearchResponse) -> None:
    """Pretty print search results."""
    print(f"\n{'=' * 60}")
    print(f"Search: {result.query}")
    print(f"Results: {result.total_results:,}")
    print(f"Avg Views: {format_number(result.avg_views)}")
    print(f"{'=' * 60}\n")

    if result.top_channels:
        print("Top Channels:")
        for ch in result.top_channels:
            print(f"  - {ch['name']} ({ch['video_count']} videos)")
        print()

    if not result.videos:
        print("No videos found.")
        return

    print("Videos:\n")
    for i, video in enumerate(result.videos[:10], 1):
        print(f"{i}. {video.title}")
        print(f"   Channel: {video.channel_name} | Views: {format_number(video.view_count)}")
        print(f"   {video.url}\n")


def print_transcript(result: dict) -> None:
    """Pretty print transcript."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"\n{'=' * 60}")
    print(f"Video ID: {result['video_id']}")
    print(f"Language: {result['language']}")
    print(f"Generated: {result['is_generated']}")
    print(f"{'=' * 60}\n")
    print(result["transcript"])


# =============================================================================
# CLI Commands
# =============================================================================


def cmd_get_channel_videos(args: argparse.Namespace, service: YouTubeService) -> None:
    """Handle get_channel_videos command."""
    channel_info = service.resolve_channel(args.handle)
    if isinstance(channel_info, dict) and "error" in channel_info:
        if args.json:
            print(json.dumps(channel_info, indent=2))
        else:
            print(f"Error: {channel_info['error']}")
        sys.exit(1)

    result = service.get_channel_videos(
        channel_id=channel_info.channel_id,
        days_back=args.days,
        max_results=args.max,
    )

    if isinstance(result, dict) and "error" in result:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)

    if args.json:
        print(json.dumps(asdict(result), indent=2, default=str))
    else:
        print_channel_videos(result)


def cmd_search_videos(args: argparse.Namespace, service: YouTubeService) -> None:
    """Handle search_videos command."""
    result = service.search_videos(
        query=args.query,
        max_results=args.max,
        days_back=args.days,
        order_by=args.order,
    )

    if isinstance(result, dict) and "error" in result:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}")
        sys.exit(1)

    if args.json:
        print(json.dumps(asdict(result), indent=2, default=str))
    else:
        print_search_results(result)


def cmd_get_transcript(args: argparse.Namespace, service: YouTubeService) -> None:
    """Handle get_transcript command."""
    result = service.get_transcript(args.video_id, max_chars=args.max_chars)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_transcript(result)

    if "error" in result:
        sys.exit(1)


def cmd_upload(args: argparse.Namespace) -> None:
    """Handle upload command."""
    client_secrets = os.environ.get("YOUTUBE_CLIENT_SECRETS")
    if not client_secrets:
        print("Error: YOUTUBE_CLIENT_SECRETS environment variable not set", file=sys.stderr)
        print("Set it to the path of your OAuth client_secrets.json file", file=sys.stderr)
        sys.exit(1)

    try:
        uploader = YouTubeUploader(Path(client_secrets))
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Load from metadata file if provided
    if args.metadata:
        metadata_path = Path(args.metadata)
        if not metadata_path.exists():
            print(f"Error: Metadata file not found: {metadata_path}", file=sys.stderr)
            sys.exit(1)

        with open(metadata_path) as f:
            content = f.read()

        # Parse based on file extension
        if metadata_path.suffix.lower() == ".md":
            metadata = parse_markdown_metadata(content)
        else:
            metadata = yaml.safe_load(content) or {}

        title = metadata.get("title", args.title)
        description = metadata.get("description", args.description or "")
        tags = metadata.get("tags", [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",")]
        category_id = str(metadata.get("category", args.category))
        privacy = metadata.get("privacy", args.privacy)
        # Thumbnail from metadata, but --thumbnail flag overrides
        thumbnail = args.thumbnail or metadata.get("thumbnail")
        thumbnail_path = Path(thumbnail) if thumbnail else None
    else:
        title = args.title
        description = args.description or ""
        tags = args.tags.split(",") if args.tags else []
        category_id = args.category
        privacy = args.privacy
        thumbnail_path = Path(args.thumbnail) if args.thumbnail else None

    if not title:
        print("Error: --title is required (or provide in metadata file)", file=sys.stderr)
        sys.exit(1)

    result = uploader.upload(
        video_path=Path(args.video),
        title=title,
        description=description,
        tags=tags,
        category_id=category_id,
        privacy=privacy,
        thumbnail_path=thumbnail_path,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    elif "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    else:
        print(f"Uploaded: {result['url']}")
        print(f"Video ID: {result['video_id']}")
        print(f"Privacy: {result['privacy']}")


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="YouTube Tool - Research and upload",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run youtube.py get_channel_videos @mkbhd --days 30
    uv run youtube.py search_videos "AI agents" --max 20 --order view_count
    uv run youtube.py get_transcript dQw4w9WgXcQ
    uv run youtube.py upload video.mp4 --title "My Video" --privacy unlisted
        """,
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # get_channel_videos
    p_channel = subparsers.add_parser(
        "get_channel_videos",
        help="Get videos from a channel with outlier analysis",
    )
    p_channel.add_argument("handle", help="Channel @handle, URL, or ID")
    p_channel.add_argument("--days", type=int, default=30, help="Days to look back")
    p_channel.add_argument("--max", type=int, default=50, help="Max videos to fetch")
    p_channel.add_argument("--json", action="store_true", help="Output as JSON")

    # search_videos
    p_search = subparsers.add_parser("search_videos", help="Search YouTube videos")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max", type=int, default=25, help="Max results")
    p_search.add_argument("--days", type=int, default=None, help="Filter by days")
    p_search.add_argument(
        "--order",
        choices=["relevance", "view_count", "date"],
        default="relevance",
        help="Sort order",
    )
    p_search.add_argument("--json", action="store_true", help="Output as JSON")

    # get_transcript
    p_transcript = subparsers.add_parser(
        "get_transcript", help="Get video transcript/captions"
    )
    p_transcript.add_argument("video_id", help="YouTube video ID")
    p_transcript.add_argument(
        "--max-chars", type=int, default=5000, help="Max transcript chars"
    )
    p_transcript.add_argument("--json", action="store_true", help="Output as JSON")

    # upload
    p_upload = subparsers.add_parser("upload", help="Upload a video to YouTube")
    p_upload.add_argument("video", help="Path to video file")
    p_upload.add_argument("--metadata", help="Path to metadata file (.md or .yaml)")
    p_upload.add_argument("--title", help="Video title (required if no metadata file)")
    p_upload.add_argument("--description", help="Video description")
    p_upload.add_argument("--tags", help="Comma-separated tags")
    p_upload.add_argument("--category", default="22", help="Category ID (default: 22)")
    p_upload.add_argument(
        "--privacy",
        choices=["private", "unlisted", "public"],
        default="private",
        help="Privacy status (default: private)",
    )
    p_upload.add_argument("--thumbnail", help="Path to thumbnail image")
    p_upload.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Upload command uses OAuth, not API key
    if args.command == "upload":
        cmd_upload(args)
        return

    # Research commands use API key
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    service = YouTubeService(api_key)

    # Dispatch to command handler
    commands = {
        "get_channel_videos": cmd_get_channel_videos,
        "search_videos": cmd_search_videos,
        "get_transcript": cmd_get_transcript,
    }

    handler = commands.get(args.command)
    if handler:
        handler(args, service)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
