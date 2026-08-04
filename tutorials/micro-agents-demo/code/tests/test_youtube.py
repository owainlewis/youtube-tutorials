from __future__ import annotations

import argparse
import importlib.util
import io
import sys
import tempfile
import tomllib
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


TOOL_PATH = Path(__file__).parents[1] / "tools" / "youtube.py"
SPEC = importlib.util.spec_from_file_location("micro_agents_youtube", TOOL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {TOOL_PATH}")
youtube = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = youtube
SPEC.loader.exec_module(youtube)


class MetadataParsingTests(unittest.TestCase):
    def test_parses_frontmatter_and_description(self) -> None:
        content = """---
title: A clear title
tags: [python, agents]
privacy: unlisted
---

The description.
"""

        metadata = youtube.parse_markdown_metadata(content)

        self.assertEqual(metadata["title"], "A clear title")
        self.assertEqual(metadata["tags"], ["python", "agents"])
        self.assertEqual(metadata["privacy"], "unlisted")
        self.assertEqual(metadata["description"], "The description.")

    def test_plain_markdown_becomes_description(self) -> None:
        metadata = youtube.parse_markdown_metadata("  A plain description.  ")

        self.assertEqual(metadata, {"description": "A plain description."})


class CommandDispatchTests(unittest.TestCase):
    def test_parser_reads_search_command(self) -> None:
        args = youtube.build_parser().parse_args(
            ["search_videos", "agent testing", "--max", "7", "--json"]
        )

        self.assertEqual(args.command, "search_videos")
        self.assertEqual(args.query, "agent testing")
        self.assertEqual(args.max, 7)
        self.assertTrue(args.json)

    def test_dispatch_calls_selected_handler(self) -> None:
        calls: list[tuple[argparse.Namespace, object]] = []
        args = argparse.Namespace(command="search_videos")
        service = object()

        youtube.dispatch_research_command(
            args,
            service,
            commands={"search_videos": lambda parsed, client: calls.append((parsed, client))},
        )

        self.assertEqual(calls, [(args, service)])

    def test_unknown_command_is_an_error(self) -> None:
        args = argparse.Namespace(command="unknown")

        with self.assertRaisesRegex(ValueError, "Unknown research command: unknown"):
            youtube.dispatch_research_command(args, object(), commands={})


class ErrorHandlingTests(unittest.TestCase):
    def test_search_error_exits_nonzero_and_prints_message(self) -> None:
        class FailingService:
            def search_videos(self, **_: object) -> dict[str, str]:
                return {"error": "quota exhausted"}

        args = argparse.Namespace(
            query="agents",
            max=5,
            days=None,
            order="relevance",
            json=False,
        )
        output = io.StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            youtube.cmd_search_videos(args, FailingService())

        self.assertEqual(raised.exception.code, 1)
        self.assertIn("Error: quota exhausted", output.getvalue())


class TranscriptTests(unittest.TestCase):
    def test_manifest_requires_instance_based_transcript_api(self) -> None:
        with (Path(__file__).parents[1] / "pyproject.toml").open("rb") as handle:
            dependencies = tomllib.load(handle)["project"]["dependencies"]

        self.assertIn("youtube-transcript-api>=1.0.0", dependencies)

    def test_transcript_fetch_uses_instance_api_without_network(self) -> None:
        class Snippet:
            def __init__(self, text: str) -> None:
                self.text = text

        class FakeTranscriptApi:
            def __init__(self) -> None:
                self.video_ids: list[str] = []

            def fetch(self, video_id: str, languages: list[str]) -> list[Snippet]:
                self.video_ids.append(video_id)
                self.languages = languages
                return [Snippet("first"), Snippet("second")]

        fake_api = FakeTranscriptApi()
        service = youtube.YouTubeService.__new__(youtube.YouTubeService)

        with patch.object(youtube, "YouTubeTranscriptApi", return_value=fake_api):
            result = service.get_transcript("video-123")

        self.assertEqual(fake_api.video_ids, ["video-123"])
        self.assertEqual(fake_api.languages, ["en"])
        self.assertEqual(result["transcript"], "first second")


class UploadLoopTests(unittest.TestCase):
    def test_upload_stops_when_request_returns_a_response(self) -> None:
        class FakeStatus:
            @staticmethod
            def progress() -> float:
                return 0.5

        class FakeRequest:
            def __init__(self) -> None:
                self.calls = 0

            def next_chunk(self) -> tuple[FakeStatus | None, dict[str, str] | None]:
                self.calls += 1
                if self.calls == 1:
                    return FakeStatus(), None
                return None, {"id": "video-123"}

        class FakeVideos:
            def __init__(self, request: FakeRequest) -> None:
                self.request = request

            def insert(self, **_: object) -> FakeRequest:
                return self.request

        class FakeYouTube:
            def __init__(self, request: FakeRequest) -> None:
                self.request = request

            def videos(self) -> FakeVideos:
                return FakeVideos(self.request)

        request = FakeRequest()
        uploader = youtube.YouTubeUploader.__new__(youtube.YouTubeUploader)
        uploader.youtube = FakeYouTube(request)

        with tempfile.TemporaryDirectory() as directory:
            video_path = Path(directory) / "video.mp4"
            video_path.touch()
            with (
                patch.object(youtube, "MediaFileUpload", return_value=object()),
                redirect_stdout(io.StringIO()),
            ):
                result = uploader.upload(video_path, title="Test upload")

        self.assertEqual(request.calls, 2)
        self.assertEqual(result["video_id"], "video-123")
        self.assertEqual(result["url"], "https://youtube.com/watch?v=video-123")


if __name__ == "__main__":
    unittest.main()
