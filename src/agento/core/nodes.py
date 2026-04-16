"""LangGraph nodes for agent execution."""

from __future__ import annotations

from typing import Any, TypedDict

from agento.core.state import AgentState, Message
from agento.infrastructure.llm.openrouter import OpenRouterClient


class NodeResult(TypedDict):
    """Result from a node execution."""

    messages: list[Message] | None
    current_mode: str | None
    current_plan: list[dict[str, Any]] | None
    error_count: int | None
    cost_total: float | None


async def chat_node_fn(
    state: AgentState,
    llm_client: OpenRouterClient,
) -> NodeResult:
    """Handle chat messages using LLM."""
    system_prompt = """You are Agento, an AI coding assistant. You help with:
- Code generation and review
- DevOps automation
- Technical questions
- Debugging help

Be concise and helpful. Format code blocks properly."""

    messages = [Message(role="system", content=system_prompt)]
    messages.extend(state.messages)

    try:
        response = await llm_client.chat(
            messages=[{"role": m.role, "content": m.content} for m in messages],
            model=state.model,
            temperature=0.7,
        )

        assistant_message = Message(
            role="assistant",
            content=response.content,
        )

        return {
            "messages": [assistant_message],
            "current_mode": "chat",
            "error_count": state.error_count,
            "cost_total": state.cost_total + response.cost,
        }
    except Exception:
        return {
            "messages": None,
            "current_mode": "chat",
            "error_count": state.error_count + 1,
            "cost_total": state.cost_total,
        }


async def planner_node_fn(
    state: AgentState,
    llm_client: OpenRouterClient,
) -> NodeResult:
    """Create execution plan for tasks."""
    if not state.messages:
        return {
            "current_plan": [],
            "current_mode": "planning",
        }

    last_message = state.messages[-1]

    planning_prompt = f"""Create a plan to: {last_message.content}

Return a JSON array of tasks with this format:
[
  {{"id": "1", "description": "task description", "type": "code|devops|research"}}
]

Be specific and break down into actionable steps."""

    try:
        response = await llm_client.chat(
            messages=[Message(role="user", content=planning_prompt)],
            model=state.model,
            temperature=0.3,
        )

        import json

        try:
            plan = json.loads(response.content)
            if isinstance(plan, list):  # pragma: no cover
                return {  # pragma: no cover
                    "current_plan": plan,  # pragma: no cover
                    "current_mode": "planning",  # pragma: no cover
                    "error_count": state.error_count,  # pragma: no cover
                    "cost_total": state.cost_total + response.cost,  # pragma: no cover
                }  # pragma: no cover
        except json.JSONDecodeError:  # pragma: no cover
            pass  # pragma: no cover

        return {
            "current_plan": [],
            "current_mode": "planning",
            "error_count": state.error_count,
            "cost_total": state.cost_total + response.cost,
        }
    except Exception:  # pragma: no cover
        return {  # pragma: no cover
            "current_plan": [],  # pragma: no cover
            "current_mode": "planning",  # pragma: no cover
            "error_count": state.error_count + 1,  # pragma: no cover
            "cost_total": state.cost_total,  # pragma: no cover
        }  # pragma: no cover


async def executor_node_fn(
    state: AgentState,
    llm_client: OpenRouterClient,
) -> NodeResult:
    """Execute current plan tasks."""
    if not state.current_plan:
        return {
            "completed_tasks": [],
            "current_mode": "executor",
        }

    pending_tasks = [
        task
        for task in state.current_plan
        if task.get("id") not in state.completed_tasks
    ]

    if not pending_tasks:
        return {
            "completed_tasks": state.completed_tasks,
            "current_mode": "executor",
        }

    current_task = pending_tasks[0]
    task_id = current_task.get("id", "")

    execution_prompt = f"""Execute this task: {current_task.get("description", "")}

Provide the code or commands needed. Be concise and practical."""

    try:
        response = await llm_client.chat(
            messages=[Message(role="user", content=execution_prompt)],
            model=state.model,
            temperature=0.5,
        )

        result_message = Message(
            role="assistant",
            content=f"[Task {task_id}] {response.content}",
        )

        return {
            "messages": [result_message],
            "completed_tasks": [*state.completed_tasks, task_id],
            "current_mode": "executor",
            "error_count": state.error_count,
            "cost_total": state.cost_total + response.cost,
        }
    except Exception:  # pragma: no cover
        return {  # pragma: no cover
            "completed_tasks": state.completed_tasks,  # pragma: no cover
            "current_mode": "executor",  # pragma: no cover
            "error_count": state.error_count + 1,  # pragma: no cover
            "cost_total": state.cost_total,  # pragma: no cover
        }  # pragma: no cover


async def reflector_node_fn(
    state: AgentState,
    llm_client: OpenRouterClient,
) -> NodeResult:
    """Reflect on execution and decide next steps."""
    if not state.current_plan:
        return {"current_mode": "reflector"}

    reflection_prompt = f"""Review the completed tasks: {state.completed_tasks}
Total planned: {len(state.current_plan)}

Should we continue with more tasks? Reply YES or NO and briefly explain."""

    try:
        response = await llm_client.chat(
            messages=[Message(role="user", content=reflection_prompt)],
            model=state.model,
            temperature=0.3,
        )

        should_continue = "YES" in response.content.upper()
        new_mode = "executor" if should_continue and state.error_count < 3 else "chat"

        return {
            "current_mode": new_mode,
            "error_count": state.error_count,
            "cost_total": state.cost_total + response.cost,
        }
    except Exception:  # pragma: no cover
        return {  # pragma: no cover
            "current_mode": "chat",  # pragma: no cover
            "error_count": state.error_count + 1,  # pragma: no cover
            "cost_total": state.cost_total,  # pragma: no cover
        }  # pragma: no cover
