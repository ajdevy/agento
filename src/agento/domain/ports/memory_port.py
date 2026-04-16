"""Memory Port - interface for memory adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class MemoryEntry(BaseModel):
    """Memory entry."""

    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    vector: list[float] | None = None


class MemoryPort(ABC):
    """Memory port interface."""

    @abstractmethod
    async def add(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """Add a memory entry."""
        ...  # pragma: no cover

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[MemoryEntry]:
        """Search for relevant memories."""
        ...  # pragma: no cover

    @abstractmethod
    async def get(self, memory_id: str) -> MemoryEntry | None:
        """Get a specific memory."""
        ...  # pragma: no cover

    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        ...  # pragma: no cover

    @abstractmethod
    async def clear(self) -> None:
        """Clear all memories."""
        ...  # pragma: no cover

    @abstractmethod
    async def count(self) -> int:
        """Count total memories."""
        ...  # pragma: no cover
