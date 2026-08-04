"""Tests for CLI configuration overrides."""

from argparse import Namespace

from nano_agent.main import resolve_config


def test_resolve_config_applies_cli_safety_and_thinking_overrides(
    tmp_path, monkeypatch
):
    config_path = tmp_path / "nano-agent.yml"
    config_path.write_text("""
max_tokens: 16000
max_turns: 20
thinking_mode: adaptive
""")
    args = Namespace(
        config=str(config_path),
        model=None,
        max_tokens=12000,
        max_turns=8,
        thinking_mode="enabled",
        thinking_budget_tokens=4000,
    )
    monkeypatch.delenv("NANO_AGENT_MODEL", raising=False)

    config = resolve_config(args)

    assert config.max_tokens == 12000
    assert config.max_turns == 8
    assert config.thinking_mode == "enabled"
    assert config.thinking_budget_tokens == 4000


def test_resolve_config_revalidates_cli_overrides(tmp_path, monkeypatch):
    config_path = tmp_path / "nano-agent.yml"
    config_path.write_text("max_turns: 20\n")
    args = Namespace(
        config=str(config_path),
        model=None,
        max_tokens=None,
        max_turns=0,
        thinking_mode=None,
        thinking_budget_tokens=None,
    )
    monkeypatch.delenv("NANO_AGENT_MODEL", raising=False)

    try:
        resolve_config(args)
    except ValueError as error:
        assert str(error) == "max_turns must be at least 1"
    else:
        raise AssertionError("invalid CLI max_turns was accepted")


def test_non_manual_cli_mode_clears_configured_budget(tmp_path, monkeypatch):
    config_path = tmp_path / "nano-agent.yml"
    config_path.write_text("""
max_tokens: 16000
thinking_mode: enabled
thinking_budget_tokens: 4000
""")
    args = Namespace(
        config=str(config_path),
        model=None,
        max_tokens=None,
        max_turns=None,
        thinking_mode="disabled",
        thinking_budget_tokens=None,
    )
    monkeypatch.delenv("NANO_AGENT_MODEL", raising=False)

    config = resolve_config(args)

    assert config.thinking_mode == "disabled"
    assert config.thinking_budget_tokens is None
