"""Calendar Agent using LangGraph.

This demonstrates LangGraph's explicit graph-based approach:
1. Define state as a TypedDict with messages
2. Create nodes (agent, tools)
3. Connect nodes with edges and conditional routing
4. Use checkpointing for conversation memory
"""

from datetime import datetime
from typing import Annotated, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from calendar_service import CalendarService

# =============================================================================
# Calendar Service (module-level for tool access)
# =============================================================================

_calendar_service: CalendarService | None = None


def get_service() -> CalendarService:
    if _calendar_service is None:
        raise RuntimeError("Calendar service not initialized")
    return _calendar_service


# =============================================================================
# Tools
# =============================================================================


@tool
def list_events(date: Annotated[str, "Date in YYYY-MM-DD format"]) -> str:
    """List all events for a date. Returns event IDs needed for updates/deletes."""
    service = get_service()
    events = service.list_events(date)

    if not events:
        return f"No events on {date}."

    lines = [f"Events for {date}:"]
    for e in events:
        lines.append(f"- {e.title} (id: {e.id})")
    return "\n".join(lines)


@tool
def create_event(
    title: Annotated[str, "Event title"],
    date: Annotated[str, "Date in YYYY-MM-DD format"],
    start_time: Annotated[str, "Start time in HH:MM format (24-hour)"],
    duration_minutes: Annotated[int, "Duration in minutes"] = 30,
) -> str:
    """Create a calendar event."""
    service = get_service()
    event = service.create_event(
        title=title,
        date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
    )
    return f"Created '{event.title}' on {date} at {start_time}."


@tool
def update_event(
    event_id: Annotated[str, "Event ID from list_events"],
    title: Annotated[str | None, "New title (optional)"] = None,
    date: Annotated[str | None, "New date in YYYY-MM-DD format (optional)"] = None,
    start_time: Annotated[str | None, "New start time in HH:MM format (optional)"] = None,
    duration_minutes: Annotated[int | None, "New duration in minutes (optional)"] = None,
) -> str:
    """Update an existing event. Use list_events first to get the event ID."""
    service = get_service()
    event = service.update_event(
        event_id=event_id,
        title=title,
        date=date,
        start_time=start_time,
        duration_minutes=duration_minutes,
    )
    return f"Updated '{event.title}'."


@tool
def delete_event(event_id: Annotated[str, "Event ID from list_events"]) -> str:
    """Delete an event. Use list_events first to get the event ID."""
    service = get_service()
    service.delete_event(event_id)
    return "Event deleted."


# =============================================================================
# Graph State
# =============================================================================


class State(TypedDict):
    """The state passed between nodes in the graph."""

    messages: Annotated[list, add_messages]


# =============================================================================
# Graph Nodes
# =============================================================================

SYSTEM_PROMPT = f"""You are a helpful calendar assistant. You help users manage their Google Calendar.

Guidelines:
- Default meeting duration is 30 minutes
- Be concise but friendly

Today is {datetime.now().strftime("%Y-%m-%d")}."""

# Tools and model (initialized once)
tools = [list_events, create_event, update_event, delete_event]
tools_by_name = {t.name: t for t in tools}
model = ChatOpenAI(model="gpt-4o").bind_tools(tools)


def agent(state: State) -> State:
    """Call the LLM to decide what to do next."""
    # Prepend system message if this is the first call
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = model.invoke(messages)
    return {"messages": [response]}


def tools_node(state: State) -> State:
    """Execute the tools requested by the LLM."""
    results = []
    last_message: AIMessage = state["messages"][-1]

    for tool_call in last_message.tool_calls:
        tool_fn = tools_by_name[tool_call["name"]]
        result = tool_fn.invoke(tool_call["args"])
        print(f"  [Tool: {tool_call['name']}({tool_call['args']})]")
        results.append(
            ToolMessage(content=result, tool_call_id=tool_call["id"])
        )

    return {"messages": results}


# =============================================================================
# Graph Edges (Routing)
# =============================================================================


def should_continue(state: State) -> Literal["tools", "end"]:
    """Decide whether to call tools or finish."""
    last_message = state["messages"][-1]

    # If the LLM made tool calls, route to tools node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"

    # Otherwise, we're done
    return "end"


# =============================================================================
# Build the Graph
# =============================================================================


def create_graph():
    """
    Build the agent graph:

        START → agent → should_continue? → tools → agent (loop)
                              ↓
                             END
    """
    graph = StateGraph(State)

    # Add nodes
    graph.add_node("agent", agent)
    graph.add_node("tools", tools_node)

    # Add edges
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")

    # Compile with memory checkpointer
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# =============================================================================
# CLI
# =============================================================================


def main():
    global _calendar_service

    print("Calendar Agent (LangGraph)")
    print("Type 'quit' to exit\n")

    try:
        _calendar_service = CalendarService()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    app = create_graph()

    # Thread ID for conversation continuity (checkpointer uses this)
    config = {"configurable": {"thread_id": "calendar-session"}}

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break

        # Run the graph
        result = app.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
        )

        # Get the last message (agent's response)
        response = result["messages"][-1].content
        print(f"Agent: {response}")


if __name__ == "__main__":
    main()
