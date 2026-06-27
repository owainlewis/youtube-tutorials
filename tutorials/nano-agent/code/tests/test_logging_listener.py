"""Tests for the file-logging event listener."""

from __future__ import annotations

import asyncio
import logging
import logging.handlers
from pathlib import Path

import pytest

from nano_agent.events import (
    EventBus,
    PostToolUse,
    PreToolUse,
    Stop,
    SubagentStart,
    SubagentStop,
    Thinking,
)
from nano_agent.listeners.logging import register_logging_listeners

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def isolate_logger():
    """Remove all handlers from the nano_agent.events logger before and after
    each test so that handler state never leaks between tests."""
    logger = logging.getLogger("nano_agent.events")
    # Tear down anything left by a previous test
    for h in list(logger.handlers):
        h.close()
        logger.removeHandler(h)
    yield
    # Tear down handlers created by this test
    for h in list(logger.handlers):
        h.close()
        logger.removeHandler(h)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fresh_bus_and_log(tmp_path: Path, level: int = logging.DEBUG) -> tuple[EventBus, Path]:
    """Return a new EventBus wired to a unique temp log file, plus the log path."""
    log_file = tmp_path / "test-agent.log"
    bus = EventBus()
    register_logging_listeners(bus, log_path=log_file, level=level)
    return bus, log_file


def _log_contents(log_file: Path) -> str:
    return log_file.read_text(encoding="utf-8")


def _flush_logger() -> None:
    """Flush all handlers on the nano_agent.events logger."""
    logger = logging.getLogger("nano_agent.events")
    for handler in logger.handlers:
        handler.flush()


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


def test_log_file_created(tmp_path: Path) -> None:
    """register_logging_listeners should create the log file immediately."""
    log_file = tmp_path / "agent.log"
    assert not log_file.exists()

    bus = EventBus()
    register_logging_listeners(bus, log_path=log_file)

    _flush_logger()
    assert log_file.exists()


def test_log_file_nested_dirs_created(tmp_path: Path) -> None:
    """Parent directories that do not yet exist should be created."""
    log_file = tmp_path / "deeply" / "nested" / "agent.log"
    bus = EventBus()
    register_logging_listeners(bus, log_path=log_file)

    _flush_logger()
    assert log_file.exists()


def test_returns_logger(tmp_path: Path) -> None:
    """register_logging_listeners should return a logging.Logger."""
    bus = EventBus()
    result = register_logging_listeners(bus, log_path=tmp_path / "x.log")
    assert isinstance(result, logging.Logger)


def test_rotating_handler_attached(tmp_path: Path) -> None:
    """A RotatingFileHandler should be attached to the logger."""
    bus = EventBus()
    logger = register_logging_listeners(bus, log_path=tmp_path / "x.log")
    rotating = [h for h in logger.handlers if isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(rotating) >= 1


# ---------------------------------------------------------------------------
# Thinking
# ---------------------------------------------------------------------------


def test_thinking_logged_at_debug(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path, level=logging.DEBUG)
    asyncio.run(bus.emit(Thinking(text="pondering the universe")))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "[Thinking]" in contents
    assert "pondering the universe" in contents


def test_thinking_truncated_in_log(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path, level=logging.DEBUG)
    long_text = "x" * 200
    asyncio.run(bus.emit(Thinking(text=long_text)))
    _flush_logger()
    contents = _log_contents(log_file)
    # The preview written to the log must be ≤ 120 printable chars + "..."
    assert "..." in contents


def test_thinking_suppressed_at_info_level(tmp_path: Path) -> None:
    """Thinking is logged at DEBUG; setting level=INFO should suppress it."""
    bus, log_file = _fresh_bus_and_log(tmp_path, level=logging.INFO)
    asyncio.run(bus.emit(Thinking(text="invisible thought")))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "invisible thought" not in contents


# ---------------------------------------------------------------------------
# PreToolUse
# ---------------------------------------------------------------------------


def test_pre_tool_use_logged(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(PreToolUse(tool_name="read_file", tool_params={"path": "/tmp/f.txt"})))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "[PreToolUse]" in contents
    assert "read_file" in contents
    assert "/tmp/f.txt" in contents


def test_pre_tool_use_empty_params(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(PreToolUse(tool_name="list_directory", tool_params={})))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "list_directory" in contents


# ---------------------------------------------------------------------------
# PostToolUse
# ---------------------------------------------------------------------------


def test_post_tool_use_logged(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(PostToolUse(tool_name="run_bash", result="hello world")))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "[PostToolUse]" in contents
    assert "run_bash" in contents
    assert "hello world" in contents


def test_post_tool_use_result_truncated(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    long_result = "y" * 300
    asyncio.run(bus.emit(PostToolUse(tool_name="run_bash", result=long_result)))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "..." in contents


# ---------------------------------------------------------------------------
# Stop
# ---------------------------------------------------------------------------


def test_stop_logged(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(Stop(text="All done!")))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "[Stop]" in contents
    assert "All done!" in contents


def test_stop_response_truncated(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    long_response = "z" * 300
    asyncio.run(bus.emit(Stop(text=long_response)))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "..." in contents


# ---------------------------------------------------------------------------
# SubagentStart / SubagentStop
# ---------------------------------------------------------------------------


def test_subagent_start_logged(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(SubagentStart(task="analyse the repo")))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "[SubagentStart]" in contents
    assert "analyse the repo" in contents


def test_subagent_stop_logged(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(SubagentStop(task="analyse the repo", result="done fine")))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "[SubagentStop]" in contents
    assert "analyse the repo" in contents
    assert "done fine" in contents


def test_subagent_stop_result_truncated(tmp_path: Path) -> None:
    bus, log_file = _fresh_bus_and_log(tmp_path)
    asyncio.run(bus.emit(SubagentStop(task="t", result="r" * 300)))
    _flush_logger()
    contents = _log_contents(log_file)
    assert "..." in contents


# ---------------------------------------------------------------------------
# All events appear in a single session
# ---------------------------------------------------------------------------


def test_all_events_in_single_log(tmp_path: Path) -> None:
    """Emit every event type once and confirm all appear in the same file."""
    bus, log_file = _fresh_bus_and_log(tmp_path)

    async def emit_all() -> None:
        await bus.emit(Thinking(text="hmm"))
        await bus.emit_approval(PreToolUse(tool_name="edit_file", tool_params={"path": "a.py"}))
        await bus.emit(PostToolUse(tool_name="edit_file", result="ok"))
        await bus.emit(SubagentStart(task="sub-task"))
        await bus.emit(SubagentStop(task="sub-task", result="sub-result"))
        await bus.emit(Stop(text="finished"))

    asyncio.run(emit_all())
    _flush_logger()

    contents = _log_contents(log_file)
    for marker in ("[Thinking]", "[PreToolUse]", "[PostToolUse]", "[SubagentStart]", "[SubagentStop]", "[Stop]"):
        assert marker in contents, f"Missing marker: {marker}"


# ---------------------------------------------------------------------------
# Isolation: listener does not break other listeners
# ---------------------------------------------------------------------------


def test_logging_listener_coexists_with_other_listeners(tmp_path: Path) -> None:
    """Registering the logging listener must not prevent other listeners from firing."""
    received: list[Stop] = []

    async def other_listener(event: Stop) -> None:
        received.append(event)

    bus, _ = _fresh_bus_and_log(tmp_path)
    bus.on(Stop, other_listener)

    asyncio.run(bus.emit(Stop(text="coexist")))

    assert len(received) == 1
    assert received[0].text == "coexist"
