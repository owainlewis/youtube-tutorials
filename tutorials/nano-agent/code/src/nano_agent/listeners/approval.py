"""Tool call approval listener. Prompts user with y/n before executing a tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from nano_agent.events import EventBus, PreToolUse

if TYPE_CHECKING:
    from nano_agent.config import AgentConfig

console = Console()


def register_approval_listener(event_bus: EventBus, config: AgentConfig | None = None) -> None:
    """Register the approval listener on the bus.

    If config has skip_approval=True, all tools are auto-approved.
    """

    async def on_pre_tool_use(event: PreToolUse) -> bool:
        if config and config.skip_approval:
            return True
        response = console.input(f"  Allow [bold cyan]{event.tool_name}[/]? [y/n] ")
        return response.strip().lower().startswith("y")

    event_bus.on_approval(on_pre_tool_use)
