"""Tests for the event bus and lifecycle events."""

import asyncio

from nano_agent.events import EventBus, PostToolUse, PreToolUse, Stop, Thinking


def test_emit_calls_listener():
    events_received = []

    async def listener(event):
        events_received.append(event)

    bus = EventBus()
    bus.on(Stop, listener)

    asyncio.run(bus.emit(Stop(text="hello")))

    assert len(events_received) == 1
    assert events_received[0].text == "hello"


def test_emit_multiple_listeners():
    order = []

    async def first(event):
        order.append("first")

    async def second(event):
        order.append("second")

    bus = EventBus()
    bus.on(Stop, first)
    bus.on(Stop, second)

    asyncio.run(bus.emit(Stop(text="test")))

    assert order == ["first", "second"]


def test_emit_no_listeners():
    bus = EventBus()
    # Should not raise
    asyncio.run(bus.emit(Stop(text="test")))


def test_approval_default_true():
    """No approval handler registered - defaults to True."""
    bus = EventBus()
    result = asyncio.run(bus.emit_approval(PreToolUse(tool_name="test", tool_params={})))
    assert result is True


def test_approval_approved():
    async def approve(event):
        return True

    bus = EventBus()
    bus.on_approval(approve)

    result = asyncio.run(bus.emit_approval(PreToolUse(tool_name="test", tool_params={})))
    assert result is True


def test_approval_denied():
    async def deny(event):
        return False

    bus = EventBus()
    bus.on_approval(deny)

    result = asyncio.run(bus.emit_approval(PreToolUse(tool_name="test", tool_params={})))
    assert result is False


def test_emit_approval_also_notifies_listeners():
    """emit_approval() calls both on() listeners and the approval handler."""
    ui_events = []

    async def ui_listener(event):
        ui_events.append(event)

    async def deny(event):
        return False

    bus = EventBus()
    bus.on(PreToolUse, ui_listener)
    bus.on_approval(deny)

    event = PreToolUse(tool_name="test", tool_params={})

    # emit calls on() listeners - does not call approval handler
    asyncio.run(bus.emit(event))
    assert len(ui_events) == 1

    # emit_approval calls both on() listeners and approval handler
    result = asyncio.run(bus.emit_approval(event))
    assert result is False
    assert len(ui_events) == 2


def test_thinking_event():
    events_received = []

    async def listener(event):
        events_received.append(event)

    bus = EventBus()
    bus.on(Thinking, listener)

    asyncio.run(bus.emit(Thinking(text="Let me think...")))

    assert len(events_received) == 1
    assert events_received[0].text == "Let me think..."


def test_different_event_types_isolated():
    stop_events = []
    post_events = []

    async def stop_listener(event):
        stop_events.append(event)

    async def post_listener(event):
        post_events.append(event)

    bus = EventBus()
    bus.on(Stop, stop_listener)
    bus.on(PostToolUse, post_listener)

    asyncio.run(bus.emit(Stop(text="done")))
    asyncio.run(bus.emit(PostToolUse(tool_name="read_file", result="contents")))

    assert len(stop_events) == 1
    assert len(post_events) == 1
