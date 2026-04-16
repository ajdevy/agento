"""Plan entity."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from agento.domain.entities.task import Task, TaskStatus


class Plan(BaseModel):
    """Execution plan entity."""

    id: str = Field(description="Unique plan identifier")
    description: str = Field(description="Plan description")
    tasks: list[Task] = Field(
        default_factory=list,
        description="Ordered list of tasks",
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Creation timestamp",
    )
    current_task_index: int = Field(
        default=0,
        description="Current task index",
    )
    status: str = Field(
        default="pending",
        description="Plan status",
    )

    def get_next_task(self) -> Task | None:
        """Get the next task to execute."""
        if self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None

    def advance(self) -> None:
        """Move to the next task."""
        self.current_task_index += 1

    def is_complete(self) -> bool:
        """Check if all tasks are complete."""
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)

    def add_task(self, task: Task) -> None:
        """Add a task to the plan."""
        self.tasks.append(task)

    @property
    def progress(self) -> tuple[int, int]:
        """Return (completed, total) task counts."""
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        return completed, len(self.tasks)
