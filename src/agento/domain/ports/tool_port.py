"""Tool Port - interface for tool adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Tool execution result."""

    success: bool
    output: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolPort(ABC):
    """Tool port interface."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        ...  # pragma: no cover

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """Execute the tool."""
        ...  # pragma: no cover

    @abstractmethod
    def validate(self, **kwargs: Any) -> bool:
        """Validate tool parameters."""
        ...  # pragma: no cover
