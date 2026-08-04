"""Tests for the YAML configuration system."""

from pathlib import Path

import pytest

from nano_agent.config import AgentConfig, load_config, _parse_config


@pytest.fixture
def tmp_config(tmp_path):
    """Helper to write a YAML config file and return its path."""
    def _write(content: str) -> Path:
        p = tmp_path / "nano-agent.yml"
        p.write_text(content)
        return p
    return _write


class TestAgentConfig:
    def test_defaults(self):
        config = AgentConfig()
        assert config.model == "claude-sonnet-4-6"
        assert config.max_tokens == 16000
        assert config.max_turns == 20
        assert config.thinking_mode == "adaptive"
        assert config.thinking_budget_tokens is None
        assert config.skip_approval is False

    def test_skip_approval(self):
        config = AgentConfig(skip_approval=True)
        assert config.skip_approval is True


class TestLoadConfig:
    def test_no_config_returns_defaults(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        config = load_config()
        assert config.model == "claude-sonnet-4-6"

    def test_explicit_path(self, tmp_config):
        path = tmp_config("model: claude-opus-4-6\nmax_tokens: 32000\n")
        config = load_config(path)
        assert config.model == "claude-opus-4-6"
        assert config.max_tokens == 32000

    def test_missing_explicit_path_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yml")

    def test_auto_detect(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "nano-agent.yml").write_text("model: claude-haiku-4-5-20251001\n")
        config = load_config()
        assert config.model == "claude-haiku-4-5-20251001"


class TestParseConfig:
    def test_full_config(self, tmp_config):
        path = tmp_config("""
model: claude-opus-4-6
max_tokens: 32000
max_turns: 12
thinking_mode: enabled
thinking_budget_tokens: 8000
skip_approval: true
""")
        config = _parse_config(path)
        assert config.model == "claude-opus-4-6"
        assert config.max_tokens == 32000
        assert config.max_turns == 12
        assert config.thinking_mode == "enabled"
        assert config.thinking_budget_tokens == 8000
        assert config.skip_approval is True

    def test_empty_config(self, tmp_config):
        path = tmp_config("")
        config = _parse_config(path)
        assert config.model == "claude-sonnet-4-6"
        assert config.skip_approval is False

    def test_skip_approval_defaults_false(self, tmp_config):
        path = tmp_config("model: claude-sonnet-4-6\n")
        config = _parse_config(path)
        assert config.skip_approval is False

    @pytest.mark.parametrize("max_turns", [0, -1])
    def test_max_turns_must_be_positive(self, tmp_config, max_turns):
        path = tmp_config(f"max_turns: {max_turns}\n")
        with pytest.raises(ValueError, match="max_turns must be at least 1"):
            _parse_config(path)

    def test_manual_thinking_requires_budget(self, tmp_config):
        path = tmp_config("thinking_mode: enabled\n")
        with pytest.raises(ValueError, match="thinking_budget_tokens is required"):
            _parse_config(path)

    def test_manual_thinking_budget_must_fit_max_tokens(self, tmp_config):
        path = tmp_config("""
max_tokens: 8000
thinking_mode: enabled
thinking_budget_tokens: 8000
""")
        with pytest.raises(ValueError, match="must be less than max_tokens"):
            _parse_config(path)

    def test_budget_is_rejected_for_adaptive_thinking(self, tmp_config):
        path = tmp_config("thinking_budget_tokens: 4000\n")
        with pytest.raises(ValueError, match="only valid"):
            _parse_config(path)
