"""YAML-based agent configuration."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class AgentConfig:
    """Top-level agent configuration."""

    model: str = "claude-sonnet-4-6"
    max_tokens: int = 16000
    skip_approval: bool = False


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

    return AgentConfig(
        model=raw.get("model", "claude-sonnet-4-6"),
        max_tokens=raw.get("max_tokens", 16000),
        skip_approval=raw.get("skip_approval", False),
    )
