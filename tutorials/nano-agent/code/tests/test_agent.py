"""Tests for the core agent loop."""

import asyncio

import pytest

from nano_agent.agent import Agent, MAX_TURNS_MESSAGE
from nano_agent.events import EventBus, PostToolUse, Stop, SubagentStart, SubagentStop, Thinking
from nano_agent.providers.base import (
    Provider,
    ProviderResponse,
    RedactedThinkingBlock,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
)


class MockProvider(Provider):
    """Returns scripted responses in order."""

    def __init__(self, responses: list[ProviderResponse]) -> None:
        self._responses = list(responses)

    async def send(self, messages, tools, system_prompt) -> ProviderResponse:
        return self._responses.pop(0)


def test_text_response():
    """Agent returns text and emits Stop event for a text-only response."""
    events = []

    async def collect_stop(event):
        events.append(event)

    provider = MockProvider([
        ProviderResponse(content=[TextBlock(text="Hello there!")])
    ])

    bus = EventBus()
    bus.on(Stop, collect_stop)

    agent = Agent(provider=provider, event_bus=bus, tools={})
    result = asyncio.run(agent.run("hi"))

    assert result == "Hello there!"
    assert len(events) == 1
    assert events[0].text == "Hello there!"


def test_tool_call_approved():
    """Agent executes tool when approved and feeds result back."""
    call_log = []

    async def mock_tool(message: str) -> str:
        call_log.append(message)
        return f"echoed: {message}"

    tools = {
        "echo": {
            "function": mock_tool,
            "schema": {"name": "echo", "description": "Echo", "input_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            }},
        }
    }

    provider = MockProvider([
        ProviderResponse(content=[
            ToolUseBlock(id="t1", name="echo", input={"message": "test"})
        ]),
        ProviderResponse(content=[
            TextBlock(text="Done!")
        ]),
    ])

    bus = EventBus()
    agent = Agent(provider=provider, event_bus=bus, tools=tools)
    result = asyncio.run(agent.run("echo test"))

    assert result == "Done!"
    assert call_log == ["test"]


def test_tool_call_denied():
    """Agent uses denial message when listener returns False."""
    async def deny(event):
        return False

    tools = {
        "dangerous": {
            "function": lambda: None,
            "schema": {"name": "dangerous", "description": "Bad", "input_schema": {
                "type": "object", "properties": {}, "required": [],
            }},
        }
    }

    provider = MockProvider([
        ProviderResponse(content=[
            ToolUseBlock(id="t1", name="dangerous", input={})
        ]),
        ProviderResponse(content=[
            TextBlock(text="OK, I won't do that.")
        ]),
    ])

    bus = EventBus()
    bus.on_approval(deny)

    agent = Agent(provider=provider, event_bus=bus, tools=tools)
    result = asyncio.run(agent.run("do something dangerous"))

    assert result == "OK, I won't do that."


def test_thinking_emitted():
    """Agent emits Thinking event when provider returns thinking text."""
    thinking_events = []

    async def collect(event):
        thinking_events.append(event)

    provider = MockProvider([
        ProviderResponse(content=[
            ThinkingBlock(thinking="Let me consider...", signature="sig1"),
            TextBlock(text="42"),
        ])
    ])

    bus = EventBus()
    bus.on(Thinking, collect)

    agent = Agent(provider=provider, event_bus=bus, tools={})
    result = asyncio.run(agent.run("what is the answer?"))

    assert result == "42"
    assert len(thinking_events) == 1
    assert thinking_events[0].text == "Let me consider..."


def test_thinking_in_history():
    """Thinking blocks are echoed in conversation history."""
    provider = MockProvider([
        ProviderResponse(content=[
            ThinkingBlock(thinking="hmm", signature="sig2"),
            TextBlock(text="yes"),
        ])
    ])

    bus = EventBus()
    agent = Agent(provider=provider, event_bus=bus, tools={})
    asyncio.run(agent.run("test"))

    assistant_msg = agent.history[1]
    assert assistant_msg["role"] == "assistant"
    assert isinstance(assistant_msg["content"], list)
    assert assistant_msg["content"][0]["type"] == "thinking"
    assert assistant_msg["content"][1]["type"] == "text"


def test_interleaved_thinking_order_is_preserved_in_history():
    async def echo(message: str) -> str:
        return message

    tools = {
        "echo": {
            "function": echo,
            "schema": {"name": "echo", "description": "Echo", "input_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            }},
        }
    }
    provider = MockProvider([
        ProviderResponse(content=[
            ThinkingBlock(thinking="first", signature="sig1"),
            ToolUseBlock(id="t1", name="echo", input={"message": "hello"}),
            RedactedThinkingBlock(data="encrypted"),
            ThinkingBlock(thinking="second", signature="sig2"),
            TextBlock(text="Checking the result."),
        ]),
        ProviderResponse(content=[TextBlock(text="Done")]),
    ])

    agent = Agent(provider=provider, event_bus=EventBus(), tools=tools)
    result = asyncio.run(agent.run("test"))

    assert result == "Done"
    assistant_content = agent.history[1]["content"]
    assert [block["type"] for block in assistant_content] == [
        "thinking",
        "tool_use",
        "redacted_thinking",
        "thinking",
        "text",
    ]
    assert assistant_content[0]["signature"] == "sig1"
    assert assistant_content[2]["data"] == "encrypted"
    assert assistant_content[3]["signature"] == "sig2"


def test_conversation_history():
    """Conversation history accumulates across multiple run() calls."""
    provider = MockProvider([
        ProviderResponse(content=[TextBlock(text="First")]),
        ProviderResponse(content=[TextBlock(text="Second")]),
    ])

    bus = EventBus()
    agent = Agent(provider=provider, event_bus=bus, tools={})

    asyncio.run(agent.run("one"))
    asyncio.run(agent.run("two"))

    # History: user1, assistant1, user2, assistant2
    assert len(agent.history) == 4
    assert agent.history[0]["role"] == "user"
    assert agent.history[1]["role"] == "assistant"
    assert agent.history[2]["role"] == "user"
    assert agent.history[3]["role"] == "assistant"


def test_multi_step_tool_chain():
    """Agent handles a multi-step tool chain: tool -> provider -> tool -> text."""
    call_log = []

    async def tool_a(x: str) -> str:
        call_log.append(("a", x))
        return f"a_result:{x}"

    async def tool_b(y: str) -> str:
        call_log.append(("b", y))
        return f"b_result:{y}"

    tools = {
        "tool_a": {
            "function": tool_a,
            "schema": {"name": "tool_a", "description": "A", "input_schema": {
                "type": "object", "properties": {"x": {"type": "string"}}, "required": ["x"],
            }},
        },
        "tool_b": {
            "function": tool_b,
            "schema": {"name": "tool_b", "description": "B", "input_schema": {
                "type": "object", "properties": {"y": {"type": "string"}}, "required": ["y"],
            }},
        },
    }

    provider = MockProvider([
        # First: call tool_a
        ProviderResponse(content=[
            ToolUseBlock(id="t1", name="tool_a", input={"x": "hello"})
        ]),
        # Second: call tool_b based on tool_a's result
        ProviderResponse(content=[
            ToolUseBlock(id="t2", name="tool_b", input={"y": "world"})
        ]),
        # Third: final text response
        ProviderResponse(content=[
            TextBlock(text="All done with both tools!")
        ]),
    ])

    bus = EventBus()
    agent = Agent(provider=provider, event_bus=bus, tools=tools)
    result = asyncio.run(agent.run("do multi-step"))

    assert result == "All done with both tools!"
    assert call_log == [("a", "hello"), ("b", "world")]
    # History: user, assistant(tool_a), tool_result, assistant(tool_b), tool_result, assistant(text)
    assert len(agent.history) == 6


def test_post_tool_use_events():
    """PostToolUse events are emitted with correct tool name and result."""
    post_events = []

    async def collect(event):
        post_events.append(event)

    async def mock_tool(msg: str) -> str:
        return f"result:{msg}"

    tools = {
        "echo": {
            "function": mock_tool,
            "schema": {"name": "echo", "description": "Echo", "input_schema": {
                "type": "object", "properties": {"msg": {"type": "string"}}, "required": ["msg"],
            }},
        }
    }

    provider = MockProvider([
        ProviderResponse(content=[
            ToolUseBlock(id="t1", name="echo", input={"msg": "test"})
        ]),
        ProviderResponse(content=[TextBlock(text="done")]),
    ])

    bus = EventBus()
    bus.on(PostToolUse, collect)

    agent = Agent(provider=provider, event_bus=bus, tools=tools)
    asyncio.run(agent.run("echo test"))

    assert len(post_events) == 1
    assert post_events[0].tool_name == "echo"
    assert post_events[0].result == "result:test"


def test_unknown_tool():
    """Agent handles unknown tool names gracefully."""
    provider = MockProvider([
        ProviderResponse(content=[
            ToolUseBlock(id="t1", name="nonexistent", input={})
        ]),
        ProviderResponse(content=[TextBlock(text="OK")]),
    ])

    bus = EventBus()
    agent = Agent(provider=provider, event_bus=bus, tools={})
    result = asyncio.run(agent.run("test"))

    assert result == "OK"


def test_max_turns_stops_tool_loop():
    """Agent stops after the configured number of model calls."""
    stop_events = []

    async def collect_stop(event):
        stop_events.append(event)

    async def echo(message: str) -> str:
        return message

    tools = {
        "echo": {
            "function": echo,
            "schema": {"name": "echo", "description": "Echo", "input_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            }},
        }
    }
    provider = MockProvider([
        ProviderResponse(content=[
            ToolUseBlock(id="t1", name="echo", input={"message": "one"})
        ]),
        ProviderResponse(content=[
            ToolUseBlock(id="t2", name="echo", input={"message": "two"})
        ]),
    ])

    bus = EventBus()
    bus.on(Stop, collect_stop)
    agent = Agent(provider=provider, event_bus=bus, tools=tools, max_turns=2)
    result = asyncio.run(agent.run("keep going"))

    expected = MAX_TURNS_MESSAGE.format(max_turns=2)
    assert result == expected
    assert agent.history[-1] == {"role": "assistant", "content": expected}
    assert [event.text for event in stop_events] == [expected]


def test_max_turns_must_be_positive():
    provider = MockProvider([])
    with pytest.raises(ValueError, match="max_turns must be at least 1"):
        Agent(provider=provider, event_bus=EventBus(), max_turns=0)


def test_spawn_agent():
    """Sub-agents run concurrently, emit SubagentStart/Stop, and return results."""
    events = []

    async def collect_start(event):
        events.append(("start", event.task))

    async def collect_stop(event):
        events.append(("stop", event.task))

    # Parent provider: first returns two spawn_agent calls, then a final text response
    # Sub-agent provider: returns text immediately for each task
    call_count = {"n": 0}

    class SpawnMockProvider(Provider):
        async def send(self, messages, tools, system_prompt) -> ProviderResponse:
            call_count["n"] += 1
            user_msg = messages[-1]["content"]

            # Sub-agent calls (task text as user input)
            if user_msg in ("task A", "task B"):
                return ProviderResponse(
                    content=[TextBlock(text=f"Result for {user_msg}")],
                )

            # First parent call: return two spawn_agent tool uses
            if call_count["n"] == 1:
                return ProviderResponse(
                    content=[
                        ToolUseBlock(id="s1", name="spawn_agent", input={"task": "task A"}),
                        ToolUseBlock(id="s2", name="spawn_agent", input={"task": "task B"}),
                    ],
                )

            # Second parent call: return final text
            return ProviderResponse(
                content=[TextBlock(text="All done!")],
            )

    tools = {
        "spawn_agent": {
            "function": None,
            "schema": {"name": "spawn_agent", "description": "Spawn", "input_schema": {
                "type": "object",
                "properties": {"task": {"type": "string"}},
                "required": ["task"],
            }},
        }
    }

    bus = EventBus()
    bus.on(SubagentStart, collect_start)
    bus.on(SubagentStop, collect_stop)

    agent = Agent(provider=SpawnMockProvider(), event_bus=bus, tools=tools)
    result = asyncio.run(agent.run("do two things"))

    assert result == "All done!"
    # Both sub-agents should have started and stopped
    starts = [e for e in events if e[0] == "start"]
    stops = [e for e in events if e[0] == "stop"]
    assert len(starts) == 2
    assert len(stops) == 2
    assert ("start", "task A") in starts
    assert ("start", "task B") in starts


def test_spawn_agent_no_recursion():
    """Sub-agents do not have access to spawn_agent tool."""
    sub_tool_names = []

    class InspectProvider(Provider):
        async def send(self, messages, tools, system_prompt) -> ProviderResponse:
            user_msg = messages[-1]["content"]

            if user_msg == "sub task":
                # Record what tools the sub-agent has
                sub_tool_names.extend([t["name"] for t in tools])
                return ProviderResponse(
                    content=[TextBlock(text="sub done")],
                )

            # Parent: spawn one sub-agent, then finish
            if not any(m.get("role") == "assistant" for m in messages):
                return ProviderResponse(
                    content=[
                        ToolUseBlock(id="s1", name="spawn_agent", input={"task": "sub task"}),
                    ],
                )

            return ProviderResponse(
                content=[TextBlock(text="parent done")],
            )

    tools = {
        "read_file": {
            "function": lambda file_path: "content",
            "schema": {"name": "read_file", "description": "Read", "input_schema": {
                "type": "object", "properties": {}, "required": [],
            }},
        },
        "spawn_agent": {
            "function": None,
            "schema": {"name": "spawn_agent", "description": "Spawn", "input_schema": {
                "type": "object",
                "properties": {"task": {"type": "string"}},
                "required": ["task"],
            }},
        },
    }

    bus = EventBus()
    agent = Agent(provider=InspectProvider(), event_bus=bus, tools=tools)
    asyncio.run(agent.run("go"))

    assert "spawn_agent" not in sub_tool_names
    assert "read_file" in sub_tool_names


def test_spawn_agent_requires_parent_approval():
    """A denied spawn request does not start a sub-agent."""
    starts = []

    async def deny(_event):
        return False

    async def collect_start(event):
        starts.append(event)

    provider = MockProvider([
        ProviderResponse(content=[
            ToolUseBlock(id="s1", name="spawn_agent", input={"task": "sub task"})
        ]),
        ProviderResponse(content=[TextBlock(text="Stayed local")]),
    ])
    tools = {
        "spawn_agent": {
            "function": None,
            "schema": {"name": "spawn_agent", "description": "Spawn", "input_schema": {
                "type": "object",
                "properties": {"task": {"type": "string"}},
                "required": ["task"],
            }},
        }
    }

    bus = EventBus()
    bus.on_approval(deny)
    bus.on(SubagentStart, collect_start)
    agent = Agent(provider=provider, event_bus=bus, tools=tools)
    result = asyncio.run(agent.run("delegate"))

    assert result == "Stayed local"
    assert starts == []
    assert agent.history[2]["content"][0]["content"] == "Tool call denied by user"
