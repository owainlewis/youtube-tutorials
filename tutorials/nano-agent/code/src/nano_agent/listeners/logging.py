"""File-based logging listener. Writes every agent-loop event to a rotating log file."""

from __future__ import annotations

import json
import logging
import logging.handlers
from pathlib import Path

from nano_agent.events import (
    EventBus,
    PostToolUse,
    PreToolUse,
    Stop,
    SubagentStart,
    SubagentStop,
    Thinking,
)

# ---------------------------------------------------------------------------
# Logger construction
# ---------------------------------------------------------------------------

_DEFAULT_LOG_PATH = Path("nano-agent.log")
_MAX_BYTES = 10 * 1024 * 1024  # 10 MB per file
_BACKUP_COUNT = 3               # keep nano-agent.log + 3 rotated copies


def _build_logger(log_path: Path, level: int) -> logging.Logger:
    """Create (or retrieve) the *nano_agent.events* logger and attach a
    RotatingFileHandler pointed at *log_path*.

    Using a named logger (rather than the root logger) keeps the agent's event
    log isolated from any logging configuration the caller may have applied to
    the root logger.

    A fresh handler is always created for the given *log_path* so that
    multiple calls with different paths (e.g. in tests) each write to their
    own file.  Any existing RotatingFileHandler that already targets the same
    resolved path is reused instead of duplicated.
    """
    logger = logging.getLogger("nano_agent.events")

    resolved = str(log_path.resolve())
    already_present = any(
        isinstance(h, logging.handlers.RotatingFileHandler)
        and str(Path(h.baseFilename).resolve()) == resolved
        for h in logger.handlers
    )

    if not already_present:
        handler = logging.handlers.RotatingFileHandler(
            filename=log_path,
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s  %(levelname)-8s  %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S",
            )
        )
        logger.addHandler(handler)

    logger.setLevel(level)
    # Never propagate to the root logger - keeps output out of the console.
    logger.propagate = False
    return logger


# ---------------------------------------------------------------------------
# Per-event async handlers
# ---------------------------------------------------------------------------


def _make_handlers(logger: logging.Logger):
    """Return a dict mapping each event type to its async handler closure."""

    async def on_thinking(event: Thinking) -> None:
        # Keep the log line short: emit a single-line preview (≤120 chars).
        preview = event.text.strip().replace("\n", " ")
        if len(preview) > 120:
            preview = preview[:117] + "..."
        logger.debug("[Thinking] %s", preview)

    async def on_pre_tool_use(event: PreToolUse) -> None:
        params_json = json.dumps(event.tool_params, separators=(",", ":"))
        logger.info("[PreToolUse] tool=%s params=%s", event.tool_name, params_json)

    async def on_post_tool_use(event: PostToolUse) -> None:
        # Truncate very long results so the log stays readable.
        result_preview = event.result.strip().replace("\n", " ")
        if len(result_preview) > 200:
            result_preview = result_preview[:197] + "..."
        logger.info("[PostToolUse] tool=%s result=%s", event.tool_name, result_preview)

    async def on_stop(event: Stop) -> None:
        preview = event.text.strip().replace("\n", " ")
        if len(preview) > 200:
            preview = preview[:197] + "..."
        logger.info("[Stop] response=%s", preview)

    async def on_subagent_start(event: SubagentStart) -> None:
        logger.info("[SubagentStart] task=%s", event.task)

    async def on_subagent_stop(event: SubagentStop) -> None:
        result_preview = event.result.strip().replace("\n", " ")
        if len(result_preview) > 200:
            result_preview = result_preview[:197] + "..."
        logger.info("[SubagentStop] task=%s result=%s", event.task, result_preview)

    return {
        Thinking: on_thinking,
        PreToolUse: on_pre_tool_use,
        PostToolUse: on_post_tool_use,
        Stop: on_stop,
        SubagentStart: on_subagent_start,
        SubagentStop: on_subagent_stop,
    }


# ---------------------------------------------------------------------------
# Public registration function
# ---------------------------------------------------------------------------


def register_logging_listeners(
    event_bus: EventBus,
    log_path: Path | str = _DEFAULT_LOG_PATH,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """Register file-logging handlers for every agent-loop event type.

    Parameters
    ----------
    event_bus:
        The :class:`~nano_agent.events.EventBus` to attach listeners to.
    log_path:
        Destination log file.  Defaults to ``nano-agent.log`` in the current
        working directory.  Parent directories are created automatically.
    level:
        Logging level applied to the *nano_agent.events* logger.  Defaults to
        ``logging.DEBUG`` so that ``Thinking`` traces (logged at DEBUG) are
        captured; set to ``logging.INFO`` to suppress them.

    Returns
    -------
    logging.Logger
        The configured logger, exposed so callers can adjust it further if
        needed (e.g. add an extra handler, change the level at runtime).
    """
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = _build_logger(log_path, level)
    logger.info("Logging listener initialised - writing to %s", log_path.resolve())

    handlers = _make_handlers(logger)
    for event_type, handler in handlers.items():
        event_bus.on(event_type, handler)

    return logger
