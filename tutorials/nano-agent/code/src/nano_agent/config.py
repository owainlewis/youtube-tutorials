"""YAML-based agent configuration."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    """Top-level agent configuration."""

    model: str = "claude-sonnet-4-6"
    max_tokens: int = 16000
    max_turns: int = 20
    thinking_mode: str = "adaptive"
    thinking_budget_tokens: int | None = None
    skip_approval: bool = False

    def validate(self) -> None:
        """Reject settings that the agent or Anthropic API cannot use."""
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if self.max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        if self.thinking_mode not in {"adaptive", "enabled", "disabled"}:
            raise ValueError(
                "thinking_mode must be one of: adaptive, enabled, disabled"
            )
        if self.thinking_mode == "enabled":
            if self.thinking_budget_tokens is None:
                raise ValueError(
                    "thinking_budget_tokens is required when thinking_mode is enabled"
                )
            if self.thinking_budget_tokens < 1024:
                raise ValueError("thinking_budget_tokens must be at least 1024")
            if self.thinking_budget_tokens >= self.max_tokens:
                raise ValueError("thinking_budget_tokens must be less than max_tokens")
        elif self.thinking_budget_tokens is not None:
            raise ValueError(
                "thinking_budget_tokens is only valid when thinking_mode is enabled"
            )


DEFAULT_CONFIG_PATHS = [
    Path("nano-agent.yml"),
    Path("nano-agent.yaml"),
    Path(".nano-agent.yml"),
    Path(".nano-agent.yaml"),
]


def load_config(path: str | Path | None = None) -> AgentConfig:
    """Load config from a YAML file.

    If no path is given, searches for default config files in the current directory.
    Returns a default AgentConfig if no config file is found.
    """
    if path is not None:
        config_path = Path(path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        return _parse_config(config_path)

    # Search default locations
    for candidate in DEFAULT_CONFIG_PATHS:
        if candidate.exists():
            return _parse_config(candidate)

    return AgentConfig()


def _parse_config(path: Path) -> AgentConfig:
    """Parse a YAML config file into an AgentConfig."""
    raw = yaml.safe_load(path.read_text()) or {}

    config = AgentConfig(
        model=raw.get("model", "claude-sonnet-4-6"),
        max_tokens=raw.get("max_tokens", 16000),
        max_turns=raw.get("max_turns", 20),
        thinking_mode=raw.get("thinking_mode", "adaptive"),
        thinking_budget_tokens=raw.get("thinking_budget_tokens"),
        skip_approval=raw.get("skip_approval", False),
    )
    config.validate()
    return config
