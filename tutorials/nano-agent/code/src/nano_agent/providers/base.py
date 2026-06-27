"""Provider interface and shared types."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TextBlock:
    """A text content block from the model response."""

    text: str
    type: str = "text"


@dataclass
class ToolUseBlock:
    """A tool_use content block from the model response."""

    id: str
    name: str
    input: dict
    type: str = "tool_use"


ContentBlock = TextBlock | ToolUseBlock


@dataclass
class ThinkingBlock:
    """A thinking/reasoning block from the model response."""

    thinking: str
    signature: str
    type: str = "thinking"


@dataclass
class ProviderResponse:
    """Normalized response from an LLM provider."""

    thinking: ThinkingBlock | None
    content: list[ContentBlock]


class ProviderError(Exception):
    """Raised when a provider call fails."""


class Provider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def send(
        self,
        messages: list[dict],
        tools: list[dict],
        system_prompt: str,
    ) -> ProviderResponse:
        """Send messages to the model and return a normalized response."""
