"""Event bus and lifecycle event types for the agent loop."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable


# -- Event types --


@dataclass
class Thinking:
    """Emitted when the model produces a thinking/reasoning trace."""

    text: str


@dataclass
class PreToolUse:
    """Emitted before a tool is executed. Approval gate - listeners return True/False."""

    tool_name: str
    tool_params: dict


@dataclass
class PostToolUse:
    """Emitted after a tool has executed with its result."""

    tool_name: str
    result: str


@dataclass
class Stop:
    """Emitted when the agent produces a final text response (no more tool calls)."""

    text: str


@dataclass
class SubagentStart:
    """Emitted when a sub-agent begins its task."""

    task: str


@dataclass
class SubagentStop:
    """Emitted when a sub-agent completes its task."""

    task: str
    result: str


# -- Event Bus --


class EventBus:
    """Simple event dispatcher. Listeners are async callables registered by event type."""

    def __init__(self) -> None:
        self._listeners: dict[type, list[Callable]] = defaultdict(list)
        self._approval_handler: Callable | None = None

    def on(self, event_type: type, callback: Callable) -> None:
        """Register an async callback for an event type."""
        self._listeners[event_type].append(callback)

    def on_approval(self, callback: Callable) -> None:
        """Register the approval handler for PreToolUse events.

        This is separate from on() so that emit() and emit_approval() don't
        conflict. UI listeners use on(PreToolUse, ...) to render the panel.
        The approval handler uses on_approval(...) to gate execution.
        """
        self._approval_handler = callback

    async def emit(self, event: Any) -> None:
        """Emit an event to all registered listeners."""
        for callback in self._listeners[type(event)]:
            await callback(event)

    async def emit_approval(self, event: PreToolUse) -> bool:
        """Emit to regular listeners, then call the approval handler.

        Returns True if no handler is registered.
        """
        await self.emit(event)
        if self._approval_handler is None:
            return True
        result = await self._approval_handler(event)
        return result is not False
