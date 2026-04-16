"""Agent graph creation."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import StateGraph

from agento.core.state import AgentState


def create_agent_graph() -> StateGraph:
    """Create the main agent graph."""
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("router", router_node)
    graph.add_node("chat", chat_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_node)
    graph.add_node("reflector", reflector_node)

    # Set entry point
    graph.set_entry_point("router")

    # Add edges
    graph.add_conditional_edges(
        "router",
        route_mode,
        {
            "chat": "chat",
            "code": "planner",
            "devops": "planner",
            "planning": "planner",
            "multi": "planner",
            "idle": "chat",
        },
    )

    # Chat flow
    graph.add_edge("chat", "__end__")

    # Planning flow
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "reflector")
    graph.add_conditional_edges(
        "reflector",
        should_continue,
        {
            "continue": "executor",
            "end": "__end__",
        },
    )

    return graph.compile()


def router_node(state: AgentState) -> dict:
    """Route to appropriate handler based on mode."""
    if not state.messages:
        return {"current_mode": "idle"}

    last_message = state.messages[-1]
    return {"current_mode": last_message.role}


def chat_node(state: AgentState) -> dict:
    """Handle chat messages."""
    return {"current_mode": "chat"}


def planner_node(state: AgentState) -> dict:
    """Create execution plan."""
    return {"current_plan": []}


def executor_node(state: AgentState) -> dict:
    """Execute current plan."""
    return {}


def reflector_node(state: AgentState) -> dict:
    """Reflect on execution results."""
    return {}


def route_mode(state: AgentState) -> str:
    """Route based on current mode."""
    return state.current_mode


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """Determine if execution should continue."""
    if state.error_count > 3:
        return "end"
    if len(state.completed_tasks) >= len(state.current_plan):
        return "end"
    return "continue"
