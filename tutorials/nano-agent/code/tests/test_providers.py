"""Tests for the Anthropic provider with mocked API."""

import asyncio
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nano_agent.providers.anthropic import AnthropicProvider
from nano_agent.providers.base import ProviderError, TextBlock, ThinkingBlock, ToolUseBlock


def _make_mock_block(block_type, **kwargs):
    """Create a mock API response block."""
    block = MagicMock()
    block.type = block_type
    for k, v in kwargs.items():
        setattr(block, k, v)
    return block


class TestAnthropicProvider:
    def test_send_constructs_correct_request(self):
        """Verify model, messages, tools, system, and thinking params are passed."""
        mock_response = MagicMock()
        mock_response.content = [_make_mock_block("text", text="hello")]

        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider(model="claude-test", max_tokens=8000, api_key="test-key")

            messages = [{"role": "user", "content": "hi"}]
            tools = [{"name": "read_file", "description": "Read", "input_schema": {}}]
            system_prompt = "You are helpful."

            asyncio.run(provider.send(messages, tools, system_prompt))

            call_kwargs = client_instance.messages.create.call_args[1]
            assert call_kwargs["model"] == "claude-test"
            assert call_kwargs["max_tokens"] == 8000
            assert call_kwargs["system"] == "You are helpful."
            assert call_kwargs["messages"] == messages
            assert call_kwargs["tools"] == tools
            assert call_kwargs["thinking"] == {"type": "enabled", "budget_tokens": 4000}

    def test_send_omits_tools_when_empty(self):
        """When no tools are provided, tools key should not be in the request."""
        mock_response = MagicMock()
        mock_response.content = [_make_mock_block("text", text="hello")]

        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider(api_key="test-key")
            asyncio.run(provider.send([{"role": "user", "content": "hi"}], [], "system"))

            call_kwargs = client_instance.messages.create.call_args[1]
            assert "tools" not in call_kwargs

    def test_send_maps_text_response(self):
        """Mock response with text block maps to TextBlock."""
        mock_response = MagicMock()
        mock_response.content = [_make_mock_block("text", text="Hello world")]

        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider(api_key="test-key")
            result = asyncio.run(provider.send(
                [{"role": "user", "content": "hi"}], [], "system"
            ))

            assert result.thinking is None
            assert len(result.content) == 1
            assert isinstance(result.content[0], TextBlock)
            assert result.content[0].text == "Hello world"

    def test_send_maps_tool_use_response(self):
        """Mock response with tool_use block maps to ToolUseBlock."""
        mock_response = MagicMock()
        mock_response.content = [
            _make_mock_block("tool_use", id="t1", name="read_file", input={"file_path": "test.py"})
        ]

        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider(api_key="test-key")
            result = asyncio.run(provider.send(
                [{"role": "user", "content": "read test.py"}], [], "system"
            ))

            assert len(result.content) == 1
            assert isinstance(result.content[0], ToolUseBlock)
            assert result.content[0].id == "t1"
            assert result.content[0].name == "read_file"
            assert result.content[0].input == {"file_path": "test.py"}

    def test_send_maps_thinking(self):
        """Mock response with thinking block sets ProviderResponse.thinking."""
        mock_response = MagicMock()
        mock_response.content = [
            _make_mock_block("thinking", thinking="Let me think...", signature="sig123"),
            _make_mock_block("text", text="42"),
        ]

        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider(api_key="test-key")
            result = asyncio.run(provider.send(
                [{"role": "user", "content": "think"}], [], "system"
            ))

            assert result.thinking is not None
            assert isinstance(result.thinking, ThinkingBlock)
            assert result.thinking.thinking == "Let me think..."
            assert result.thinking.signature == "sig123"
            assert len(result.content) == 1
            assert result.content[0].text == "42"

    def test_send_maps_mixed_response(self):
        """Response with text and tool_use blocks both mapped correctly."""
        mock_response = MagicMock()
        mock_response.content = [
            _make_mock_block("text", text="I'll read the file"),
            _make_mock_block("tool_use", id="t1", name="read_file", input={"file_path": "a.py"}),
        ]

        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(return_value=mock_response)

            provider = AnthropicProvider(api_key="test-key")
            result = asyncio.run(provider.send(
                [{"role": "user", "content": "read a.py"}], [], "system"
            ))

            assert len(result.content) == 2
            assert isinstance(result.content[0], TextBlock)
            assert isinstance(result.content[1], ToolUseBlock)

    def test_send_wraps_api_error(self):
        """API exceptions are wrapped in ProviderError."""
        with patch("nano_agent.providers.anthropic.AsyncAnthropic") as MockClient:
            client_instance = MockClient.return_value
            client_instance.messages.create = AsyncMock(
                side_effect=Exception("API rate limit exceeded")
            )

            provider = AnthropicProvider(api_key="test-key")

            with pytest.raises(ProviderError, match="API rate limit exceeded"):
                asyncio.run(provider.send(
                    [{"role": "user", "content": "hi"}], [], "system"
                ))
