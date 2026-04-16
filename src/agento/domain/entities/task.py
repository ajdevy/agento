"""Task entity."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(BaseModel):
    """Task entity."""

    id: str = Field(description="Unique task identifier")
    description: str = Field(description="Task description")
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Task status",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Task dependencies (other task IDs)",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="Last update timestamp",
    )
    result: str | None = Field(
        default=None,
        description="Task result",
    )
    error: str | None = Field(
        default=None,
        description="Error message if failed",
    )
    retry_count: int = Field(
        default=0,
        description="Number of retry attempts",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts",
    )

    def mark_in_progress(self) -> None:
        """Mark task as in progress."""
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now()

    def mark_completed(self, result: str) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.updated_at = datetime.now()

    def mark_failed(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error = error
        self.updated_at = datetime.now()

    def can_retry(self) -> bool:
        """Check if task can be retried."""
        return self.retry_count < self.max_retries

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1
        self.updated_at = datetime.now()
