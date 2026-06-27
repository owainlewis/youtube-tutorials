"""Rich-based UI event listeners. The agent loop never calls UI code directly."""

import json

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from nano_agent.events import (
    EventBus,
    PostToolUse,
    PreToolUse,
    Stop,
    SubagentStart,
    SubagentStop,
    Thinking,
)

MAX_RESULT_LINES = 5
MAX_THINKING = 200

console = Console()


def _format_tool_call(name: str, params: dict) -> str:
    """Format tool call as a function-call style string like Bash(date)."""
    if not params:
        return f"{name}()"
    values = list(params.values())
    if len(params) == 1 and isinstance(values[0], str) and len(values[0]) < 60:
        return f"{name}({values[0]})"
    compact = json.dumps(params, separators=(",", ":"))
    if len(compact) > 80:
        compact = compact[:77] + "..."
    return f"{name}({compact})"


async def on_thinking(event: Thinking) -> None:
    """Render a truncated thinking summary."""
    text = event.text.strip().replace("\n", " ")
    if len(text) > MAX_THINKING:
        text = text[:MAX_THINKING] + "…"
    console.print(f"  {text}", style="dim italic")


async def on_pre_tool_use(event: PreToolUse) -> None:
    """Render tool call as a compact line with green dot."""
    call_str = _format_tool_call(event.tool_name, event.tool_params)
    line = Text()
    line.append("● ", style="green")
    line.append(call_str, style="bold")
    console.print(line)


async def on_post_tool_use(event: PostToolUse) -> None:
    """Render tool result indented with ⎿ prefix."""
    result = event.result.strip()
    if not result:
        return
    lines = result.split("\n")
    # Show first few lines, then a count of remaining
    if len(lines) > MAX_RESULT_LINES:
        visible = lines[:MAX_RESULT_LINES]
        remaining = len(lines) - MAX_RESULT_LINES
        for line in visible:
            console.print(f"  ⎿  {line}", style="dim")
        console.print(f"  ⎿  … {remaining} more lines", style="dim")
    else:
        for line in lines:
            console.print(f"  ⎿  {line}", style="dim")
    console.print()


async def on_stop(event: Stop) -> None:
    """Render final response with green dot prefix, as Rich markdown."""
    text = event.text.strip()
    if not text:
        return
    console.print()
    console.print(Text("● ", style="green"), end="")
    console.print(Markdown(text))


async def on_subagent_start(event: SubagentStart) -> None:
    """Render sub-agent start status."""
    task = event.task[:80] + "…" if len(event.task) > 80 else event.task
    line = Text()
    line.append("● ", style="magenta")
    line.append(f"Agent({task})", style="bold")
    console.print(line)


async def on_subagent_stop(event: SubagentStop) -> None:
    """Render sub-agent completion."""
    task = event.task[:60] + "…" if len(event.task) > 60 else event.task
    console.print(f"  ⎿  done: {task}", style="dim green")
    console.print()


def register_ui_listeners(event_bus: EventBus) -> None:
    """Register all UI event listeners on the bus."""
    event_bus.on(Thinking, on_thinking)
    event_bus.on(PreToolUse, on_pre_tool_use)
    event_bus.on(PostToolUse, on_post_tool_use)
    event_bus.on(Stop, on_stop)
    event_bus.on(SubagentStart, on_subagent_start)
    event_bus.on(SubagentStop, on_subagent_stop)
