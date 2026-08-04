"""Core agent loop. Manages conversation history, tool dispatch, and event emission."""

import asyncio

from nano_agent.events import (
    EventBus,
    PostToolUse,
    PreToolUse,
    Stop,
    SubagentStart,
    SubagentStop,
    Thinking,
)
from nano_agent.providers.base import (
    Provider,
    ProviderResponse,
    RedactedThinkingBlock,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
)
from nano_agent.system_prompt import SYSTEM_PROMPT

MAX_TURNS_MESSAGE = "Maximum agent turns reached ({max_turns})."


def _serialize_content(response: ProviderResponse) -> list[dict]:
    """Convert normalized blocks back to message content in the same order."""
    content = []
    for block in response.content:
        if isinstance(block, TextBlock):
            content.append({"type": "text", "text": block.text})
        elif isinstance(block, ThinkingBlock):
            content.append({
                "type": "thinking",
                "thinking": block.thinking,
                "signature": block.signature,
            })
        elif isinstance(block, RedactedThinkingBlock):
            content.append({"type": "redacted_thinking", "data": block.data})
        elif isinstance(block, ToolUseBlock):
            content.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    return content


class Agent:
    """The agent loop. Contains zero UI or approval logic - all side effects go through the event bus."""

    def __init__(
        self,
        provider: Provider,
        event_bus: EventBus,
        tools: dict | None = None,
        system_prompt: str = SYSTEM_PROMPT,
        max_turns: int = 20,
    ) -> None:
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        self.provider = provider
        self.event_bus = event_bus
        self.tools = tools or {}
        self.system_prompt = system_prompt
        self.max_turns = max_turns
        self.history: list[dict] = []

    async def run(self, user_input: str) -> str:
        """Run one turn of the agent loop. Returns the final text response."""
        self.history.append({"role": "user", "content": user_input})

        tool_schemas = [tool["schema"] for tool in self.tools.values()]

        for _turn in range(self.max_turns):
            response: ProviderResponse = await self.provider.send(
                self.history, tool_schemas, self.system_prompt
            )

            thinking_blocks = [
                block for block in response.content if isinstance(block, ThinkingBlock)
            ]
            for block in thinking_blocks:
                await self.event_bus.emit(Thinking(text=block.thinking))

            tool_use_blocks = [b for b in response.content if isinstance(b, ToolUseBlock)]
            text_blocks = [b for b in response.content if isinstance(b, TextBlock)]

            if tool_use_blocks:
                # Preserve every response block unchanged and in order.
                assistant_content = _serialize_content(response)
                self.history.append({"role": "assistant", "content": assistant_content})

                # Separate spawn_agent calls from regular tool calls
                spawn_blocks = [b for b in tool_use_blocks if b.name == "spawn_agent"]
                regular_blocks = [b for b in tool_use_blocks if b.name != "spawn_agent"]

                tool_results = []

                # Process regular tool calls sequentially
                for block in regular_blocks:
                    approved = await self.event_bus.emit_approval(
                        PreToolUse(tool_name=block.name, tool_params=block.input)
                    )

                    if approved and block.name in self.tools:
                        tool_fn = self.tools[block.name]["function"]
                        try:
                            result = await tool_fn(**block.input)
                        except Exception as e:
                            result = f"Error: {e}"
                    elif not approved:
                        result = "Tool call denied by user"
                    else:
                        result = f"Unknown tool: {block.name}"

                    await self.event_bus.emit(
                        PostToolUse(tool_name=block.name, result=result)
                    )

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

                # Approve spawn_agent calls before they run concurrently
                if spawn_blocks:
                    approved_spawn_blocks = []
                    for block in spawn_blocks:
                        approved = await self.event_bus.emit_approval(
                            PreToolUse(tool_name=block.name, tool_params=block.input)
                        )
                        if approved:
                            approved_spawn_blocks.append(block)
                            continue

                        result = "Tool call denied by user"
                        await self.event_bus.emit(
                            PostToolUse(tool_name=block.name, result=result)
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                    spawn_results = await self._run_subagents(approved_spawn_blocks)
                    for result in spawn_results:
                        await self.event_bus.emit(
                            PostToolUse(
                                tool_name="spawn_agent",
                                result=result["content"],
                            )
                        )
                    tool_results.extend(spawn_results)

                self.history.append({"role": "user", "content": tool_results})

            else:
                # Text-only response - we're done
                text = "\n".join(b.text for b in text_blocks)
                assistant_content = _serialize_content(response)
                self.history.append({"role": "assistant", "content": assistant_content})
                await self.event_bus.emit(Stop(text=text))
                return text

        text = MAX_TURNS_MESSAGE.format(max_turns=self.max_turns)
        self.history.append({"role": "assistant", "content": text})
        await self.event_bus.emit(Stop(text=text))
        return text

    async def _run_subagents(self, spawn_blocks: list[ToolUseBlock]) -> list[dict]:
        """Run sub-agents concurrently and return tool result dicts."""
        # Build sub-agent tools: same as parent but without spawn_agent (no recursion)
        sub_tools = {k: v for k, v in self.tools.items() if k != "spawn_agent"}

        async def run_one(block: ToolUseBlock) -> dict:
            task = block.input.get("task", "")

            # Sub-agent gets its own event bus with auto-approve
            sub_bus = EventBus()

            async def auto_approve(_event: PreToolUse) -> bool:
                return True

            sub_bus.on_approval(auto_approve)

            sub_agent = Agent(
                provider=self.provider,
                event_bus=sub_bus,
                tools=sub_tools,
                system_prompt=self.system_prompt,
                max_turns=self.max_turns,
            )

            await self.event_bus.emit(SubagentStart(task=task))
            try:
                result = await sub_agent.run(task)
            except Exception as e:
                result = f"Sub-agent error: {e}"
            await self.event_bus.emit(SubagentStop(task=task, result=result))

            return {
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            }

        results = await asyncio.gather(*[run_one(b) for b in spawn_blocks])
        return list(results)
