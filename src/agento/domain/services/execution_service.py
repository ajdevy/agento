"""Execution service - plan execution and orchestration."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from agento.domain.services.planning_service import (
    Plan,
    PlanStatus,
    PlanStep,
    StepStatus,
)


class ExecutionMode(Enum):
    """Execution mode."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HYBRID = "hybrid"


@dataclass
class ExecutionContext:
    """Context for plan execution."""

    plan_id: str
    working_dir: str | None = None
    environment: dict[str, str] = field(default_factory=dict)
    timeout: float = 300.0
    max_retries: int = 3


@dataclass
class ExecutionResult:
    """Result of plan execution."""

    plan: Plan
    success: bool
    completed_steps: int = 0
    failed_steps: int = 0
    total_time: float = 0.0
    errors: list[str] = field(default_factory=list)
    results: dict[str, str] = field(default_factory=dict)


StepExecutor = Callable[[PlanStep, ExecutionContext], Awaitable[str]]


class ExecutionService:
    """Service for executing plans."""

    def __init__(
        self,
        executor: StepExecutor | None = None,
        mode: ExecutionMode = ExecutionMode.SEQUENTIAL,
    ):
        self.default_executor = executor
        self.mode = mode
        self._executors: dict[str, StepExecutor] = {}
        self._execution_history: list[ExecutionResult] = []

    def register_executor(
        self,
        step_type: str,
        executor: StepExecutor,
    ) -> None:
        """Register an executor for a step type."""
        self._executors[step_type] = executor

    async def execute_plan(
        self,
        plan: Plan,
        context: ExecutionContext,
        executor: StepExecutor | None = None,
    ) -> ExecutionResult:
        """Execute a plan."""
        start_time = datetime.now()
        result_executor = executor or self.default_executor

        plan.status = PlanStatus.IN_PROGRESS
        errors: list[str] = []
        results: dict[str, str] = {}

        try:
            if self.mode == ExecutionMode.SEQUENTIAL:
                step_errors, step_results = await self._execute_sequential(
                    plan, context, result_executor
                )
            elif self.mode == ExecutionMode.PARALLEL:
                step_errors, step_results = await self._execute_parallel(
                    plan, context, result_executor
                )
            else:
                step_errors, step_results = await self._execute_hybrid(
                    plan, context, result_executor
                )

            errors.extend(step_errors)
            results.update(step_results)

        except Exception as e:
            errors.append(f"Execution failed: {e!s}")

        total_time = (datetime.now() - start_time).total_seconds()

        plan.status = PlanStatus.COMPLETED if not errors else PlanStatus.FAILED

        completed_steps = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        failed_steps = sum(1 for s in plan.steps if s.status == StepStatus.FAILED)

        result = ExecutionResult(
            plan=plan,
            success=len(errors) == 0,
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            total_time=total_time,
            errors=errors,
            results=results,
        )

        self._execution_history.append(result)
        return result

    async def _execute_sequential(
        self,
        plan: Plan,
        context: ExecutionContext,
        executor: StepExecutor | None,
    ) -> tuple[list[str], dict[str, str]]:
        """Execute steps sequentially."""
        errors: list[str] = []
        results: dict[str, str] = {}

        while True:
            next_step = plan.get_next_step()
            if not next_step:
                break

            plan = self._update_step_status(plan, next_step.id, StepStatus.IN_PROGRESS)

            try:
                result = await self._execute_step(next_step, context, executor)
                plan = self._update_step_status(
                    plan, next_step.id, StepStatus.COMPLETED, result=result
                )
                results[next_step.id] = result

            except Exception as e:
                error_msg = f"Step {next_step.id} failed: {e!s}"
                errors.append(error_msg)
                plan = self._update_step_status(
                    plan, next_step.id, StepStatus.FAILED, error=str(e)
                )

                if next_step.attempts >= context.max_retries:
                    break

        return errors, results

    async def _execute_parallel(
        self,
        plan: Plan,
        context: ExecutionContext,
        executor: StepExecutor | None,
    ) -> tuple[list[str], dict[str, str]]:
        """Execute independent steps in parallel."""
        errors: list[str] = []
        results: dict[str, str] = {}

        while True:
            ready_steps = plan.get_ready_steps()
            if not ready_steps:
                break

            tasks = []
            for step in ready_steps:
                plan = self._update_step_status(plan, step.id, StepStatus.IN_PROGRESS)
                tasks.append(self._execute_step(step, context, executor))

            step_results = await asyncio.gather(*tasks, return_exceptions=True)

            for step, step_result in zip(ready_steps, step_results, strict=False):
                if isinstance(step_result, Exception):
                    error_msg = f"Step {step.id} failed: {step_result!s}"
                    errors.append(error_msg)
                    plan = self._update_step_status(
                        plan, step.id, StepStatus.FAILED, error=str(step_result)
                    )
                else:
                    plan = self._update_step_status(
                        plan, step.id, StepStatus.COMPLETED, result=str(step_result)
                    )
                    results[step.id] = str(step_result)

        return errors, results

    async def _execute_hybrid(
        self,
        plan: Plan,
        context: ExecutionContext,
        executor: StepExecutor | None,
    ) -> tuple[list[str], dict[str, str]]:
        """Execute with limited parallelism (up to 3 concurrent)."""
        errors: list[str] = []
        results: dict[str, str] = {}
        semaphore = asyncio.Semaphore(3)

        async def execute_with_limit(
            step: PlanStep,
        ) -> tuple[str, str | None, str | None]:
            async with semaphore:
                self._update_step_status(plan, step.id, StepStatus.IN_PROGRESS)
                try:
                    result = await self._execute_step(step, context, executor)
                    self._update_step_status(
                        plan, step.id, StepStatus.COMPLETED, result=result
                    )
                    return step.id, result, None
                except Exception as e:
                    error = str(e)
                    self._update_step_status(
                        plan, step.id, StepStatus.FAILED, error=error
                    )
                    return step.id, None, error

        while True:
            ready_steps = plan.get_ready_steps()
            if not ready_steps:
                break

            tasks = [execute_with_limit(step) for step in ready_steps]
            step_results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in step_results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                elif isinstance(result, tuple):
                    step_id, step_result, step_error = result
                    if step_error:
                        errors.append(f"Step {step_id} failed: {step_error}")
                    elif step_result:
                        results[step_id] = step_result

        return errors, results

    async def _execute_step(
        self,
        step: PlanStep,
        context: ExecutionContext,
        executor: StepExecutor | None,
    ) -> str:
        """Execute a single step."""
        if executor:
            return await executor(step, context)

        if self.default_executor:
            return await self.default_executor(step, context)

        await asyncio.sleep(0.1)
        return f"Completed: {step.description}"

    def _update_step_status(
        self,
        plan: Plan,
        step_id: str,
        status: StepStatus,
        result: str | None = None,
        error: str | None = None,
    ) -> Plan:
        """Update step status in plan."""
        for step in plan.steps:
            if step.id == step_id:
                step.status = status
                if result is not None:
                    step.result = result
                if error is not None:
                    step.error = error
                if status == StepStatus.IN_PROGRESS:
                    step.started_at = datetime.now()
                    step.attempts += 1
                if status in (StepStatus.COMPLETED, StepStatus.FAILED):
                    step.completed_at = datetime.now()
                break

        plan.updated_at = datetime.now()

        if plan.is_complete():
            plan.status = PlanStatus.COMPLETED
        elif plan.is_failed():
            plan.status = PlanStatus.FAILED

        return plan

    async def retry_step(
        self,
        plan: Plan,
        step_id: str,
        context: ExecutionContext,
        executor: StepExecutor | None = None,
    ) -> str | None:
        """Retry a failed step."""
        for step in plan.steps:
            if step.id == step_id and step.status == StepStatus.FAILED:
                if step.attempts >= context.max_retries:
                    return None

                plan = self._update_step_status(plan, step_id, StepStatus.PENDING)
                result_executor = executor or self.default_executor

                try:
                    result = await self._execute_step(step, context, result_executor)
                    plan = self._update_step_status(
                        plan, step_id, StepStatus.COMPLETED, result=result
                    )
                    return result
                except Exception as e:
                    plan = self._update_step_status(
                        plan, step_id, StepStatus.FAILED, error=str(e)
                    )
                    return None

        return None

    def get_execution_history(self) -> list[ExecutionResult]:
        """Get execution history."""
        return self._execution_history.copy()

    def clear_history(self) -> None:
        """Clear execution history."""
        self._execution_history.clear()

    def get_statistics(self) -> dict[str, Any]:
        """Get execution statistics."""
        if not self._execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_time": 0.0,
            }

        total = len(self._execution_history)
        successes = sum(1 for r in self._execution_history if r.success)
        total_time = sum(r.total_time for r in self._execution_history)

        return {
            "total_executions": total,
            "success_rate": successes / total,
            "average_time": total_time / total,
            "total_steps_completed": sum(
                r.completed_steps for r in self._execution_history
            ),
            "total_steps_failed": sum(r.failed_steps for r in self._execution_history),
        }
