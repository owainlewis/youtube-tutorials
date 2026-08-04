"""CLI entry point. Wires up the agent with listeners and runs the REPL."""

import argparse
import asyncio
import os

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nano_agent import __version__
from nano_agent.agent import Agent
from nano_agent.config import AgentConfig, load_config
from nano_agent.events import EventBus
from nano_agent.listeners import register_approval_listener, register_logging_listeners, register_ui_listeners
from nano_agent.providers import AnthropicProvider
from nano_agent.providers.base import ProviderError
from nano_agent.tools import get_tools

console = Console()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nano Agent - a minimal coding agent")
    parser.add_argument(
        "--config",
        default=None,
        help="Path to YAML config file (default: auto-detect nano-agent.yml)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Model to use (overrides config file)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Max tokens for model response (overrides config file)",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Maximum model calls per user request (overrides config file)",
    )
    parser.add_argument(
        "--thinking-mode",
        choices=("adaptive", "enabled", "disabled"),
        default=None,
        help="Thinking mode (overrides config file)",
    )
    parser.add_argument(
        "--thinking-budget-tokens",
        type=int,
        default=None,
        help="Token budget for manual thinking mode",
    )
    return parser.parse_args()


def resolve_config(args: argparse.Namespace) -> AgentConfig:
    """Build the final AgentConfig from file + CLI args + env vars."""
    config = load_config(args.config)

    # CLI args and env vars override the config file
    if args.model:
        config.model = args.model
    elif env_model := os.environ.get("NANO_AGENT_MODEL"):
        config.model = env_model

    if args.max_tokens is not None:
        config.max_tokens = args.max_tokens

    if args.max_turns is not None:
        config.max_turns = args.max_turns

    if args.thinking_mode is not None:
        config.thinking_mode = args.thinking_mode
        if args.thinking_mode != "enabled" and args.thinking_budget_tokens is None:
            config.thinking_budget_tokens = None

    if args.thinking_budget_tokens is not None:
        config.thinking_budget_tokens = args.thinking_budget_tokens

    config.validate()

    return config


def print_splash(config: AgentConfig) -> None:
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        cwd = "~" + cwd[len(home):]

    info = Table.grid(padding=(0, 2))
    info.add_column()
    info.add_column(style="dim")
    info.add_row("model", config.model)
    info.add_row("cwd", cwd)

    panel = Panel(
        info,
        title=f"[bold]nano-agent[/bold] v{__version__}",
        border_style="dim",
        padding=(1, 2),
    )
    console.print(panel)
    console.print()


async def run() -> None:
    args = parse_args()
    config = resolve_config(args)

    provider = AnthropicProvider(
        model=config.model,
        max_tokens=config.max_tokens,
        thinking_mode=config.thinking_mode,
        thinking_budget_tokens=config.thinking_budget_tokens,
    )
    event_bus = EventBus()

    register_ui_listeners(event_bus)
    register_approval_listener(event_bus, config=config)
    register_logging_listeners(event_bus)

    agent = Agent(
        provider=provider,
        event_bus=event_bus,
        tools=get_tools(),
        max_turns=config.max_turns,
    )

    print_splash(config)

    while True:
        try:
            user_input = console.input("[bold]❯[/bold] ")
        except (KeyboardInterrupt, EOFError):
            console.print("\nGoodbye!", style="dim")
            return

        if not user_input.strip():
            continue

        try:
            await agent.run(user_input)
            console.print()
        except ProviderError as e:
            console.print(f"  error: {e}", style="bold red")
            console.print()


def main() -> None:
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        console.print("\nGoodbye!", style="dim")


if __name__ == "__main__":
    main()
