"""Agent state for LangGraph."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""

    role: Literal["user", "assistant", "system", "tool"]
    content: str
    name: str | None = None


class AgentState(BaseModel):
    """Agent state for LangGraph."""

    messages: Annotated[list[Message], add_messages] = Field(
        default_factory=list,
        description="Chat messages",
    )

    session_id: str = Field(
        default="",
        description="Session identifier",
    )

    current_mode: Literal[
        "idle",
        "chat",
        "code",
        "devops",
        "memory",
        "planning",
        "multi",
        "spec",
    ] = Field(
        default="idle",
        description="Current agent mode",
    )

    current_plan: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Current execution plan",
    )

    completed_tasks: list[str] = Field(
        default_factory=list,
        description="Completed task IDs",
    )

    memory_context: list[str] = Field(
        default_factory=list,
        description="Retrieved memory IDs",
    )

    tools_used: list[str] = Field(
        default_factory=list,
        description="Tools used in this session",
    )

    error_count: int = Field(
        default=0,
        description="Error count",
    )

    model: str = Field(
        default="openrouter/free",
        description="Current model",
    )

    cost_total: float = Field(
        default=0.0,
        description="Total cost this session",
    )
