"""Planning service - task decomposition and planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Priority(Enum):
    """Task priority."""

    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3


class DecomposableTask:
    """A task that can be decomposed into subtasks."""

    def __init__(
        self,
        id: str,
        title: str,
        description: str,
        priority: Priority = Priority.MEDIUM,
        depends_on: list[str] | None = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.depends_on = depends_on or []


class PlanStatus(Enum):
    """Plan execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Step execution status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    """Individual step in a plan."""

    id: str
    description: str
    depends_on: list[str] = field(default_factory=list)
    status: StepStatus = StepStatus.PENDING
    result: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    attempts: int = 0


@dataclass
class Plan:
    """Execution plan."""

    id: str
    goal: str
    steps: list[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.PENDING
    current_step_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_next_step(self) -> PlanStep | None:
        """Get the next pending step."""
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                if all(
                    s.status == StepStatus.COMPLETED
                    for s in self.steps
                    if s.id in step.depends_on
                ):
                    return step
        return None

    def get_ready_steps(self) -> list[PlanStep]:
        """Get all steps that are ready to execute."""
        ready = []
        for step in self.steps:
            if step.status == StepStatus.PENDING:
                deps_met = all(
                    s.status == StepStatus.COMPLETED
                    for s in self.steps
                    if s.id in step.depends_on
                )
                if deps_met:
                    ready.append(step)
        return ready

    def is_complete(self) -> bool:
        """Check if plan is complete."""
        return all(
            s.status in (StepStatus.COMPLETED, StepStatus.SKIPPED) for s in self.steps
        )

    def is_failed(self) -> bool:
        """Check if plan has failed."""
        return any(s.status == StepStatus.FAILED for s in self.steps)

    def get_progress(self) -> float:
        """Get plan progress (0-1)."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.status == StepStatus.COMPLETED)
        return completed / len(self.steps)


@dataclass
class PlanningResult:
    """Result of planning operation."""

    plan: Plan
    success: bool
    error: str | None = None


class PlanningService:
    """Service for task planning and decomposition."""

    def __init__(
        self,
        llm_client: Any | None = None,
        max_depth: int = 10,
    ):
        self.llm_client = llm_client
        self.max_depth = max_depth
        self._planning_history: list[Plan] = []

    async def create_plan(
        self,
        goal: str,
        context: dict[str, Any] | None = None,
    ) -> PlanningResult:
        """Create an execution plan for a goal."""
        try:
            if self.llm_client:
                return await self._llm_planning(goal, context)
            return self._rule_based_planning(goal, context)

        except Exception as e:
            return PlanningResult(
                plan=Plan(id="fallback", goal=goal),
                success=False,
                error=str(e),
            )

    async def _llm_planning(
        self,
        goal: str,
        context: dict[str, Any] | None,
    ) -> PlanningResult:
        """Use LLM for planning."""
        context = context or {}

        assert self.llm_client is not None

        prompt = f"""Break down this goal into clear, executable steps:

Goal: {goal}

Context: {context}

Requirements:
- Each step should be atomic and testable
- Identify dependencies between steps
- Prioritize steps that unblock others
"""

        response = await self.llm_client.chat(
            messages=[{"role": "user", "content": prompt}]
        )

        steps = self._parse_llm_response(str(response.content), goal)
        plan = Plan(id=str(id(response)), goal=goal, steps=steps)
        self._planning_history.append(plan)

        return PlanningResult(plan=plan, success=True)

    def _rule_based_planning(
        self,
        goal: str,
        context: dict[str, Any] | None,
    ) -> PlanningResult:
        """Rule-based planning when LLM is not available."""
        goal_lower = goal.lower()
        steps: list[PlanStep] = []

        if "test" in goal_lower or "spec" in goal_lower:
            steps.extend(
                [
                    PlanStep(
                        id="1", description="Understand requirements", depends_on=[]
                    ),
                    PlanStep(id="2", description="Write tests", depends_on=["1"]),
                    PlanStep(
                        id="3",
                        description="Verify tests fail initially",
                        depends_on=["2"],
                    ),
                ]
            )

        elif (
            "implement" in goal_lower or "create" in goal_lower or "build" in goal_lower
        ):
            steps.extend(
                [
                    PlanStep(id="1", description="Design solution", depends_on=[]),
                    PlanStep(
                        id="2", description="Implement core logic", depends_on=["1"]
                    ),
                    PlanStep(
                        id="3", description="Add error handling", depends_on=["2"]
                    ),
                    PlanStep(id="4", description="Write tests", depends_on=["2"]),
                ]
            )

        elif "fix" in goal_lower or "bug" in goal_lower:
            steps.extend(
                [
                    PlanStep(id="1", description="Identify the bug", depends_on=[]),
                    PlanStep(
                        id="2", description="Write reproduction test", depends_on=["1"]
                    ),
                    PlanStep(id="3", description="Implement fix", depends_on=["2"]),
                    PlanStep(id="4", description="Verify tests pass", depends_on=["3"]),
                ]
            )

        elif "refactor" in goal_lower:
            steps.extend(
                [
                    PlanStep(id="1", description="Analyze current code", depends_on=[]),
                    PlanStep(
                        id="2",
                        description="Plan refactoring approach",
                        depends_on=["1"],
                    ),
                    PlanStep(
                        id="3", description="Implement refactoring", depends_on=["2"]
                    ),
                    PlanStep(
                        id="4", description="Run tests to verify", depends_on=["3"]
                    ),
                ]
            )

        else:
            steps.extend(
                [
                    PlanStep(id="1", description="Analyze goal", depends_on=[]),
                    PlanStep(id="2", description="Execute main task", depends_on=["1"]),
                    PlanStep(id="3", description="Verify results", depends_on=["2"]),
                ]
            )

        plan = Plan(id=str(id(goal)), goal=goal, steps=steps)
        self._planning_history.append(plan)

        return PlanningResult(plan=plan, success=True)

    def _parse_llm_response(
        self,
        response: str,
        goal: str,
    ) -> list[PlanStep]:
        """Parse LLM response into plan steps."""
        steps: list[PlanStep] = []
        lines = response.strip().split("\n")

        step_id = 1
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit() or line.startswith("-") or line.startswith("*"):
                clean_desc = line.lstrip("0123456789.-* ").strip()
                if clean_desc:
                    steps.append(
                        PlanStep(
                            id=str(step_id),
                            description=clean_desc,
                            depends_on=[str(step_id - 1)] if step_id > 1 else [],
                        )
                    )
                    step_id += 1

        if not steps:
            steps.append(
                PlanStep(
                    id="1",
                    description=f"Execute: {goal[:100]}",
                    depends_on=[],
                )
            )

        return steps

    def decompose_task(
        self,
        task: DecomposableTask,
    ) -> list[DecomposableTask]:
        """Decompose a complex task into subtasks."""
        subtasks: list[DecomposableTask] = []

        priority_map = {
            Priority.CRITICAL: 3,
            Priority.HIGH: 2,
            Priority.MEDIUM: 1,
            Priority.LOW: 0,
        }

        base_priority = priority_map.get(task.priority, Priority.MEDIUM)

        if "implement" in task.title.lower():
            subtasks.append(
                DecomposableTask(
                    id="1",
                    title=f"Design: {task.title}",
                    description=f"Design solution for {task.title}",
                    priority=Priority(base_priority),
                )
            )
            subtasks.append(
                DecomposableTask(
                    id="2",
                    title=f"Code: {task.title}",
                    description=f"Implement {task.title}",
                    priority=Priority(base_priority),
                )
            )
            subtasks.append(
                DecomposableTask(
                    id="3",
                    title=f"Test: {task.title}",
                    description=f"Write tests for {task.title}",
                    priority=Priority(base_priority),
                )
            )

        elif "fix" in task.title.lower():
            subtasks.append(
                DecomposableTask(
                    id="1",
                    title=f"Investigate: {task.title}",
                    description=f"Find root cause of {task.title}",
                    priority=Priority(base_priority),
                )
            )
            subtasks.append(
                DecomposableTask(
                    id="2",
                    title=f"Fix: {task.title}",
                    description=f"Fix the issue in {task.title}",
                    priority=Priority(base_priority),
                )
            )

        else:
            subtasks.append(
                DecomposableTask(
                    id="1",
                    title=task.title,
                    description=task.description,
                    priority=task.priority,
                )
            )

        for i, subtask in enumerate(subtasks):
            if i > 0:
                subtask.depends_on = [subtasks[i - 1].id]

        return subtasks

    def update_plan_progress(
        self,
        plan: Plan,
        step_id: str,
        status: StepStatus,
        result: str | None = None,
        error: str | None = None,
    ) -> Plan:
        """Update plan progress after step execution."""
        for step in plan.steps:
            if step.id == step_id:
                step.status = status
                step.result = result
                step.error = error
                step.completed_at = datetime.now()

                if status == StepStatus.IN_PROGRESS:
                    step.started_at = datetime.now()
                    step.attempts += 1

        plan.updated_at = datetime.now()

        if status == StepStatus.COMPLETED:
            plan.current_step_index = plan.steps.index(step) + 1

        if plan.is_complete():
            plan.status = PlanStatus.COMPLETED
        elif plan.is_failed():
            plan.status = PlanStatus.FAILED

        return plan

    def get_planning_history(self) -> list[Plan]:
        """Get planning history."""
        return self._planning_history.copy()

    def clear_history(self) -> None:
        """Clear planning history."""
        self._planning_history.clear()
