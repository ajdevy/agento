"""Tests for execution service."""

import pytest

from agento.domain.services.execution_service import (
    ExecutionContext,
    ExecutionMode,
    ExecutionResult,
    ExecutionService,
)
from agento.domain.services.planning_service import (
    Plan,
    PlanStatus,
    PlanStep,
    StepStatus,
)


class TestExecutionContext:
    """Tests for ExecutionContext dataclass."""

    def test_create_context(self):
        """Test creating an execution context."""
        ctx = ExecutionContext(plan_id="plan-1")
        assert ctx.plan_id == "plan-1"
        assert ctx.working_dir is None
        assert ctx.environment == {}
        assert ctx.timeout == 300.0
        assert ctx.max_retries == 3

    def test_context_with_all_fields(self):
        """Test creating context with all fields."""
        ctx = ExecutionContext(
            plan_id="plan-1",
            working_dir="/tmp",
            environment={"KEY": "value"},
            timeout=60.0,
            max_retries=5,
        )
        assert ctx.working_dir == "/tmp"
        assert ctx.environment == {"KEY": "value"}
        assert ctx.timeout == 60.0
        assert ctx.max_retries == 5


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_create_result(self):
        """Test creating an execution result."""
        plan = Plan(id="test", goal="test")
        result = ExecutionResult(plan=plan, success=True)
        assert result.plan == plan
        assert result.success is True
        assert result.completed_steps == 0
        assert result.failed_steps == 0
        assert result.total_time == 0.0
        assert result.errors == []
        assert result.results == {}

    def test_result_with_all_fields(self):
        """Test creating result with all fields."""
        plan = Plan(id="test", goal="test")
        result = ExecutionResult(
            plan=plan,
            success=False,
            completed_steps=3,
            failed_steps=1,
            total_time=10.5,
            errors=["Error 1"],
            results={"1": "Result 1"},
        )
        assert result.completed_steps == 3
        assert result.failed_steps == 1
        assert result.total_time == 10.5
        assert result.errors == ["Error 1"]


class TestExecutionService:
    """Tests for ExecutionService."""

    @pytest.fixture
    def service(self):
        """Create an execution service."""
        return ExecutionService()

    @pytest.fixture
    def sample_plan(self):
        """Create a sample plan."""
        return Plan(
            id="test-plan",
            goal="Test goal",
            steps=[
                PlanStep(id="1", description="Step 1"),
                PlanStep(id="2", description="Step 2"),
                PlanStep(id="3", description="Step 3"),
            ],
        )

    @pytest.fixture
    def context(self):
        """Create an execution context."""
        return ExecutionContext(plan_id="test-plan")

    def test_create_service(self):
        """Test creating an execution service."""
        service = ExecutionService()
        assert service.default_executor is None
        assert service.mode == ExecutionMode.SEQUENTIAL
        assert service._executors == {}
        assert service._execution_history == []

    def test_create_service_with_mode(self):
        """Test creating service with specific mode."""
        service = ExecutionService(mode=ExecutionMode.PARALLEL)
        assert service.mode == ExecutionMode.PARALLEL

    async def test_register_executor(self, service):
        """Test registering an executor."""

        async def executor(step, ctx):
            return f"Result for {step.id}"

        service.register_executor("test", executor)
        assert "test" in service._executors

    @pytest.mark.asyncio
    async def test_execute_plan_empty(self, service, context):
        """Test executing an empty plan."""
        plan = Plan(id="test", goal="test")
        result = await service.execute_plan(plan, context)
        assert result.success is True
        assert result.completed_steps == 0
        assert result.plan.status == PlanStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_plan_sequential(self, service, sample_plan, context):
        """Test executing plan in sequential mode."""
        service.mode = ExecutionMode.SEQUENTIAL

        async def executor(step, ctx):
            return f"Done: {step.description}"

        result = await service.execute_plan(sample_plan, context, executor)
        assert result.success is True
        assert result.completed_steps == 3
        assert result.failed_steps == 0
        assert result.plan.status == PlanStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_plan_parallel(self, service, sample_plan, context):
        """Test executing plan in parallel mode."""
        service.mode = ExecutionMode.PARALLEL

        async def executor(step, ctx):
            return f"Done: {step.description}"

        result = await service.execute_plan(sample_plan, context, executor)
        assert result.success is True
        assert result.completed_steps == 3

    @pytest.mark.asyncio
    @pytest.mark.timeout(5)
    async def test_execute_plan_hybrid(self, service, sample_plan, context):
        """Test executing plan in hybrid mode."""
        service.mode = ExecutionMode.HYBRID

        async def executor(step, ctx):
            return f"Done: {step.description}"

        result = await service.execute_plan(sample_plan, context, executor)
        assert result.success is True
        assert result.completed_steps == 3

    @pytest.mark.asyncio
    async def test_execute_plan_with_dependencies(self, service, context):
        """Test executing plan with step dependencies."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1"),
                PlanStep(id="2", description="Step 2", depends_on=["1"]),
                PlanStep(id="3", description="Step 3", depends_on=["2"]),
            ],
        )
        service.mode = ExecutionMode.SEQUENTIAL

        async def executor(step, ctx):
            return f"Done: {step.id}"

        result = await service.execute_plan(plan, context, executor)
        assert result.success is True
        assert result.completed_steps == 3

    @pytest.mark.asyncio
    async def test_execute_plan_executor_error(self, service, sample_plan, context):
        """Test executing plan when executor raises error."""
        service.mode = ExecutionMode.SEQUENTIAL

        async def failing_executor(step, ctx):
            raise ValueError(f"Failed on step {step.id}")

        result = await service.execute_plan(sample_plan, context, failing_executor)
        assert result.success is False
        assert len(result.errors) > 0
        assert result.plan.status == PlanStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_plan_adds_to_history(self, service, context):
        """Test that execution results are added to history."""
        plan = Plan(id="test", goal="test")
        await service.execute_plan(plan, context)
        assert len(service.get_execution_history()) == 1

    @pytest.mark.asyncio
    async def test_retry_step_success(self, service, sample_plan, context):
        """Test retrying a failed step."""
        sample_plan.steps[0].status = StepStatus.FAILED
        sample_plan.steps[0].attempts = 1

        async def executor(step, ctx):
            return f"Retry success: {step.id}"

        result = await service.retry_step(sample_plan, "1", context, executor)
        assert result == "Retry success: 1"
        assert sample_plan.steps[0].status == StepStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_retry_step_max_attempts_reached(self, service, sample_plan, context):
        """Test retry when max attempts reached."""
        sample_plan.steps[0].status = StepStatus.FAILED
        sample_plan.steps[0].attempts = context.max_retries

        async def executor(step, ctx):
            return "Should not reach here"

        result = await service.retry_step(sample_plan, "1", context, executor)
        assert result is None

    @pytest.mark.asyncio
    async def test_retry_step_not_found(self, service, sample_plan, context):
        """Test retry for non-existent step."""
        result = await service.retry_step(sample_plan, "nonexistent", context)
        assert result is None

    def test_get_execution_history(self, service):
        """Test getting execution history."""
        assert service.get_execution_history() == []

        service._execution_history.append(
            ExecutionResult(plan=Plan(id="1", goal="1"), success=True)
        )
        history = service.get_execution_history()
        assert len(history) == 1

    def test_clear_history(self, service):
        """Test clearing execution history."""
        service._execution_history.append(
            ExecutionResult(plan=Plan(id="1", goal="1"), success=True)
        )
        service.clear_history()
        assert len(service.get_execution_history()) == 0

    def test_get_statistics_empty(self, service):
        """Test statistics with no history."""
        stats = service.get_statistics()
        assert stats["total_executions"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["average_time"] == 0.0

    def test_get_statistics_with_history(self, service):
        """Test statistics with execution history."""
        service._execution_history.append(
            ExecutionResult(
                plan=Plan(id="1", goal="1"),
                success=True,
                completed_steps=3,
                failed_steps=0,
                total_time=10.0,
            )
        )
        service._execution_history.append(
            ExecutionResult(
                plan=Plan(id="2", goal="2"),
                success=False,
                completed_steps=1,
                failed_steps=1,
                total_time=5.0,
            )
        )
        stats = service.get_statistics()
        assert stats["total_executions"] == 2
        assert stats["success_rate"] == 0.5
        assert stats["average_time"] == 7.5
        assert stats["total_steps_completed"] == 4
        assert stats["total_steps_failed"] == 1


class TestExecutionMode:
    """Tests for ExecutionMode enum."""

    def test_all_modes_exist(self):
        """Test all execution modes exist."""
        assert ExecutionMode.SEQUENTIAL is not None
        assert ExecutionMode.PARALLEL is not None
        assert ExecutionMode.HYBRID is not None

    def test_mode_values(self):
        """Test execution mode values."""
        assert ExecutionMode.SEQUENTIAL.value == "sequential"
        assert ExecutionMode.PARALLEL.value == "parallel"
        assert ExecutionMode.HYBRID.value == "hybrid"


class TestStepExecutor:
    """Tests for StepExecutor type."""

    @pytest.mark.asyncio
    async def test_executor_type_hints(self):
        """Test that executor can be used with proper type hints."""

        async def my_executor(step, ctx):
            return "Result"

        service = ExecutionService(executor=my_executor)
        plan = Plan(
            id="test", goal="test", steps=[PlanStep(id="1", description="Test")]
        )
        context = ExecutionContext(plan_id="test")

        result = await service.execute_plan(plan, context)
        assert result.success is True
        assert result.results["1"] == "Result"
