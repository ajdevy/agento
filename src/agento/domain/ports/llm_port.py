"""LLM Port - interface for LLM adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Chat message."""

    role: Literal["system", "user", "assistant"]
    content: str


class ModelResponse(BaseModel):
    """Model response."""

    content: str
    model: str
    usage: dict[str, int] = Field(default_factory=dict)
    cost: float = 0.0


class LLMPort(ABC):
    """LLM port interface."""

    @abstractmethod
    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> ModelResponse:
        """Send chat request to LLM."""
        ...

    @abstractmethod
    async def stream(
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Stream chat response from LLM."""
        ...

    @abstractmethod
    def get_cost(self, model: str, tokens: int) -> float:
        """Get cost for model and token count."""
        ...

    @abstractmethod
    def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status."""
        ...
