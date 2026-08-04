"""Anthropic API provider implementation."""

from anthropic import AsyncAnthropic

from .base import (
    Provider,
    ProviderError,
    ProviderResponse,
    RedactedThinkingBlock,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
)


class AnthropicProvider(Provider):
    """Anthropic API implementation with configurable thinking support."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 16000,
        thinking_mode: str = "adaptive",
        thinking_budget_tokens: int | None = None,
        api_key: str | None = None,
    ) -> None:
        if thinking_mode not in {"adaptive", "enabled", "disabled"}:
            raise ValueError(
                "thinking_mode must be one of: adaptive, enabled, disabled"
            )
        if thinking_mode == "enabled":
            if thinking_budget_tokens is None:
                raise ValueError(
                    "thinking_budget_tokens is required when thinking_mode is enabled"
                )
            if thinking_budget_tokens < 1024:
                raise ValueError("thinking_budget_tokens must be at least 1024")
            if thinking_budget_tokens >= max_tokens:
                raise ValueError("thinking_budget_tokens must be less than max_tokens")
        elif thinking_budget_tokens is not None:
            raise ValueError(
                "thinking_budget_tokens is only valid when thinking_mode is enabled"
            )

        self.model = model
        self.max_tokens = max_tokens
        self.thinking_mode = thinking_mode
        self.thinking_budget_tokens = thinking_budget_tokens
        self.client = AsyncAnthropic(api_key=api_key)

    async def send(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> ProviderResponse:
        """Send messages to Anthropic API and return normalized response."""
        try:
            kwargs: dict = {
                "model": self.model,
                "max_tokens": self.max_tokens,
                "system": system_prompt,
                "messages": messages,
            }

            if self.thinking_mode == "enabled":
                kwargs["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget_tokens,
                }
            else:
                kwargs["thinking"] = {"type": self.thinking_mode}

            if tools:
                kwargs["tools"] = tools

            response = await self.client.messages.create(**kwargs)

        except Exception as e:
            raise ProviderError(str(e)) from e

        content: list[
            TextBlock | ThinkingBlock | RedactedThinkingBlock | ToolUseBlock
        ] = []

        for block in response.content:
            if block.type == "thinking":
                content.append(
                    ThinkingBlock(
                        thinking=block.thinking,
                        signature=block.signature,
                    )
                )
            elif block.type == "redacted_thinking":
                content.append(RedactedThinkingBlock(data=block.data))
            elif block.type == "text":
                content.append(TextBlock(text=block.text))
            elif block.type == "tool_use":
                content.append(
                    ToolUseBlock(id=block.id, name=block.name, input=block.input)
                )

        return ProviderResponse(content=content)
