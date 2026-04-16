"""Memory entity."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MemoryType(StrEnum):
    """Memory type."""

    CONVERSATION = "conversation"
    CODE_SNIPPET = "code_snippet"
    PATTERN = "pattern"
    PREFERENCE = "preference"
    PROJECT = "project"


class Memory(BaseModel):
    """Memory entity."""

    id: str = Field(description="Unique memory identifier")
    content: str = Field(description="Memory content")
    memory_type: MemoryType = Field(
        default=MemoryType.CONVERSATION,
        description="Memory type",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    access_count: int = Field(
        default=0,
        description="Number of times accessed",
    )
    relevance_score: float = Field(
        default=0.0,
        description="Relevance score for search",
    )

    def increment_access(self) -> None:
        """Increment access count."""
        self.access_count += 1

    def update_relevance(self, score: float) -> None:
        """Update relevance score."""
        self.relevance_score = score
