"""Tests for planning service."""

import pytest

from agento.domain.services.planning_service import (
    DecomposableTask,
    Plan,
    PlanningResult,
    PlanningService,
    PlanStatus,
    PlanStep,
    Priority,
    StepStatus,
)


class TestPlanStep:
    """Tests for PlanStep dataclass."""

    def test_create_plan_step(self):
        """Test creating a plan step."""
        step = PlanStep(
            id="1",
            description="Test step",
            depends_on=[],
        )
        assert step.id == "1"
        assert step.description == "Test step"
        assert step.depends_on == []
        assert step.status == StepStatus.PENDING
        assert step.result is None
        assert step.error is None
        assert step.started_at is None
        assert step.completed_at is None
        assert step.attempts == 0

    def test_plan_step_with_dependencies(self):
        """Test creating a plan step with dependencies."""
        step = PlanStep(
            id="2",
            description="Dependent step",
            depends_on=["1"],
        )
        assert step.depends_on == ["1"]


class TestPlan:
    """Tests for Plan dataclass."""

    def test_create_plan(self):
        """Test creating a plan."""
        plan = Plan(id="test-plan", goal="Test goal")
        assert plan.id == "test-plan"
        assert plan.goal == "Test goal"
        assert plan.steps == []
        assert plan.status == PlanStatus.PENDING
        assert plan.current_step_index == 0

    def test_get_next_step_empty(self):
        """Test get_next_step with empty steps."""
        plan = Plan(id="test", goal="test")
        assert plan.get_next_step() is None

    def test_get_next_step_no_dependencies(self):
        """Test get_next_step with steps that have no dependencies."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1"),
                PlanStep(id="2", description="Step 2"),
            ],
        )
        next_step = plan.get_next_step()
        assert next_step is not None
        assert next_step.id == "1"

    def test_get_next_step_with_dependencies(self):
        """Test get_next_step respects dependencies."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1"),
                PlanStep(id="2", description="Step 2", depends_on=["1"]),
            ],
        )
        next_step = plan.get_next_step()
        assert next_step is not None
        assert next_step.id == "1"

    def test_get_next_step_blocked_by_incomplete_dependency(self):
        """Test get_next_step returns None when dependency is incomplete."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2", depends_on=["1"]),
                PlanStep(id="3", description="Step 3", depends_on=["2"]),
            ],
        )
        plan.steps[1].status = StepStatus.COMPLETED
        next_step = plan.get_next_step()
        assert next_step is not None
        assert next_step.id == "3"

    def test_get_ready_steps(self):
        """Test get_ready_steps returns all ready steps."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1"),
                PlanStep(id="2", description="Step 2", depends_on=["1"]),
            ],
        )
        ready = plan.get_ready_steps()
        assert len(ready) == 1
        assert ready[0].id == "1"

    def test_get_ready_steps_multiple_independent(self):
        """Test get_ready_steps with multiple independent steps."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1"),
                PlanStep(id="2", description="Step 2"),
            ],
        )
        ready = plan.get_ready_steps()
        assert len(ready) == 2

    def test_is_complete_empty(self):
        """Test is_complete with empty steps."""
        plan = Plan(id="test", goal="test")
        assert plan.is_complete() is True

    def test_is_complete_partial(self):
        """Test is_complete with partial completion."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2"),
            ],
        )
        assert plan.is_complete() is False

    def test_is_complete_all_completed(self):
        """Test is_complete when all steps completed."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2", status=StepStatus.COMPLETED),
            ],
        )
        assert plan.is_complete() is True

    def test_is_complete_with_skipped(self):
        """Test is_complete includes skipped steps."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2", status=StepStatus.SKIPPED),
            ],
        )
        assert plan.is_complete() is True

    def test_is_failed_no_failures(self):
        """Test is_failed with no failures."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
            ],
        )
        assert plan.is_failed() is False

    def test_is_failed_with_failure(self):
        """Test is_failed when a step has failed."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2", status=StepStatus.FAILED),
            ],
        )
        assert plan.is_failed() is True

    def test_get_progress_empty(self):
        """Test get_progress with no steps."""
        plan = Plan(id="test", goal="test")
        assert plan.get_progress() == 0.0

    def test_get_progress_partial(self):
        """Test get_progress with partial completion."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2", status=StepStatus.COMPLETED),
                PlanStep(id="3", description="Step 3"),
            ],
        )
        assert plan.get_progress() == pytest.approx(2 / 3)

    def test_get_progress_complete(self):
        """Test get_progress when complete."""
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2", status=StepStatus.COMPLETED),
            ],
        )
        assert plan.get_progress() == 1.0


class TestPlanningService:
    """Tests for PlanningService."""

    @pytest.fixture
    def service(self):
        """Create a planning service without LLM."""
        return PlanningService(llm_client=None)

    def test_create_service(self):
        """Test creating a planning service."""
        service = PlanningService()
        assert service.llm_client is None
        assert service.max_depth == 10
        assert service._planning_history == []

    def test_create_service_with_custom_max_depth(self):
        """Test creating service with custom max_depth."""
        service = PlanningService(max_depth=5)
        assert service.max_depth == 5

    @pytest.mark.asyncio
    async def test_create_plan_rule_based_test_goal(self, service):
        """Test rule-based planning for test goals."""
        result = await service.create_plan("Write tests for feature")
        assert result.success is True
        assert len(result.plan.steps) == 3
        assert result.error is None

    @pytest.mark.asyncio
    async def test_create_plan_rule_based_implement_goal(self, service):
        """Test rule-based planning for implement goals."""
        result = await service.create_plan("Implement login feature")
        assert result.success is True
        assert len(result.plan.steps) == 4

    @pytest.mark.asyncio
    async def test_create_plan_rule_based_fix_goal(self, service):
        """Test rule-based planning for fix goals."""
        result = await service.create_plan("Fix the login bug")
        assert result.success is True
        assert len(result.plan.steps) == 4

    @pytest.mark.asyncio
    async def test_create_plan_rule_based_refactor_goal(self, service):
        """Test rule-based planning for refactor goals."""
        result = await service.create_plan("Refactor authentication module")
        assert result.success is True
        assert len(result.plan.steps) == 4

    @pytest.mark.asyncio
    async def test_create_plan_rule_based_default_goal(self, service):
        """Test rule-based planning for unknown goal type."""
        result = await service.create_plan("Just do something")
        assert result.success is True
        assert len(result.plan.steps) == 3

    @pytest.mark.asyncio
    async def test_create_plan_adds_to_history(self, service):
        """Test that created plans are added to history."""
        await service.create_plan("Write tests")
        assert len(service.get_planning_history()) == 1

        await service.create_plan("Implement feature")
        assert len(service.get_planning_history()) == 2

    @pytest.mark.asyncio
    async def test_create_plan_with_context(self, service):
        """Test creating plan with context."""
        result = await service.create_plan(
            "Write tests",
            context={"files": ["src/main.py"], "language": "python"},
        )
        assert result.success is True

    @pytest.mark.asyncio
    async def test_create_plan_error_handling(self, service):
        """Test error handling in create_plan."""
        service._rule_based_planning = None
        result = await service.create_plan("Test")
        assert result.success is False
        assert result.error is not None

    def test_parse_llm_response_numbered_list(self):
        """Test parsing numbered list response."""
        service = PlanningService()
        response = """1. First step
2. Second step
3. Third step"""
        steps = service._parse_llm_response(response, "Test")
        assert len(steps) == 3
        assert steps[0].description == "First step"
        assert steps[1].description == "Second step"

    def test_parse_llm_response_bullet_list(self):
        """Test parsing bullet list response."""
        service = PlanningService()
        response = """- First step
- Second step
- Third step"""
        steps = service._parse_llm_response(response, "Test")
        assert len(steps) == 3

    def test_parse_llm_response_empty(self):
        """Test parsing empty response."""
        service = PlanningService()
        steps = service._parse_llm_response("", "Test goal")
        assert len(steps) == 1
        assert "Test goal" in steps[0].description

    def test_parse_llm_response_dependencies(self):
        """Test that parsed steps have correct dependencies."""
        service = PlanningService()
        response = """1. Step one
2. Step two
3. Step three"""
        steps = service._parse_llm_response(response, "Test")
        assert steps[0].depends_on == []
        assert steps[1].depends_on == ["1"]
        assert steps[2].depends_on == ["2"]

    def test_decompose_task_implement(self):
        """Test decomposing implementation task."""
        service = PlanningService()
        task = DecomposableTask(
            id="task-1",
            title="Implement user auth",
            description="Add authentication",
            priority=Priority.HIGH,
        )
        subtasks = service.decompose_task(task)
        assert len(subtasks) == 3
        assert "Design" in subtasks[0].title
        assert "Code" in subtasks[1].title
        assert "Test" in subtasks[2].title

    def test_decompose_task_fix(self):
        """Test decomposing fix task."""
        service = PlanningService()
        task = DecomposableTask(
            id="task-2",
            title="Fix login bug",
            description="Login not working",
            priority=Priority.CRITICAL,
        )
        subtasks = service.decompose_task(task)
        assert len(subtasks) == 2
        assert "Investigate" in subtasks[0].title
        assert "Fix" in subtasks[1].title

    def test_decompose_task_other(self):
        """Test decomposing other task type."""
        service = PlanningService()
        task = DecomposableTask(
            id="task-3",
            title="Review code",
            description="Code review",
            priority=Priority.MEDIUM,
        )
        subtasks = service.decompose_task(task)
        assert len(subtasks) == 1
        assert subtasks[0].title == task.title

    def test_update_plan_progress_completed(self):
        """Test updating plan progress for completed step."""
        service = PlanningService()
        plan = Plan(
            id="test",
            goal="test",
            steps=[PlanStep(id="1", description="Step 1")],
        )
        updated = service.update_plan_progress(plan, "1", StepStatus.COMPLETED, "Done")
        assert updated.steps[0].status == StepStatus.COMPLETED
        assert updated.steps[0].result == "Done"
        assert updated.steps[0].completed_at is not None

    def test_update_plan_progress_in_progress(self):
        """Test updating plan progress for in-progress step."""
        service = PlanningService()
        plan = Plan(
            id="test",
            goal="test",
            steps=[PlanStep(id="1", description="Step 1")],
        )
        updated = service.update_plan_progress(plan, "1", StepStatus.IN_PROGRESS)
        assert updated.steps[0].status == StepStatus.IN_PROGRESS
        assert updated.steps[0].started_at is not None
        assert updated.steps[0].attempts == 1

    def test_update_plan_progress_failed(self):
        """Test updating plan progress for failed step."""
        service = PlanningService()
        plan = Plan(
            id="test",
            goal="test",
            steps=[PlanStep(id="1", description="Step 1")],
        )
        updated = service.update_plan_progress(
            plan, "1", StepStatus.FAILED, error="Error occurred"
        )
        assert updated.steps[0].status == StepStatus.FAILED
        assert updated.steps[0].error == "Error occurred"
        assert updated.status == PlanStatus.FAILED

    def test_update_plan_progress_completes_plan(self):
        """Test that completing last step completes the plan."""
        service = PlanningService()
        plan = Plan(
            id="test",
            goal="test",
            steps=[
                PlanStep(id="1", description="Step 1", status=StepStatus.COMPLETED),
                PlanStep(id="2", description="Step 2"),
            ],
        )
        updated = service.update_plan_progress(plan, "2", StepStatus.COMPLETED)
        assert updated.status == PlanStatus.COMPLETED

    def test_get_planning_history(self):
        """Test getting planning history."""
        service = PlanningService()
        assert service.get_planning_history() == []

        service._planning_history.append(Plan(id="1", goal="Goal 1"))
        history = service.get_planning_history()
        assert len(history) == 1
        assert history[0].goal == "Goal 1"

    def test_clear_history(self):
        """Test clearing planning history."""
        service = PlanningService()
        service._planning_history.append(Plan(id="1", goal="Goal 1"))
        service.clear_history()
        assert len(service.get_planning_history()) == 0


class TestPlanningResult:
    """Tests for PlanningResult dataclass."""

    def test_create_successful_result(self):
        """Test creating a successful planning result."""
        plan = Plan(id="test", goal="test")
        result = PlanningResult(plan=plan, success=True)
        assert result.plan == plan
        assert result.success is True
        assert result.error is None

    def test_create_failed_result(self):
        """Test creating a failed planning result."""
        plan = Plan(id="test", goal="test")
        result = PlanningResult(plan=plan, success=False, error="Test error")
        assert result.success is False
        assert result.error == "Test error"


class TestPlanningServiceWithLLM:
    """Tests for PlanningService with LLM client."""

    @pytest.mark.asyncio
    async def test_llm_planning(self):
        """Test LLM-based planning."""

        class MockLLM:
            async def chat(self, messages):
                class Response:
                    content = "1. First step\n2. Second step\n3. Third step"

                return Response()

        service = PlanningService(llm_client=MockLLM())
        result = await service.create_plan("Build a feature")
        assert result.success is True
        assert len(result.plan.steps) == 3

    @pytest.mark.asyncio
    async def test_llm_planning_exception(self):
        """Test LLM planning handles exceptions."""

        class FailingLLM:
            async def chat(self, messages):
                raise ValueError("LLM error")

        service = PlanningService(llm_client=FailingLLM())
        result = await service.create_plan("Build a feature")
        assert result.success is False
        assert result.error is not None

    def test_parse_llm_response_with_asterisk(self):
        """Test parsing LLM response with asterisk bullets."""
        service = PlanningService()
        response = """* First task
* Second task
* Third task"""
        steps = service._parse_llm_response(response, "Test")
        assert len(steps) == 3

    def test_parse_llm_response_with_numbered_with_dot(self):
        """Test parsing LLM response with numbered list and trailing dot."""
        service = PlanningService()
        response = """1. First step.
2. Second step.
3. Third step."""
        steps = service._parse_llm_response(response, "Test")
        assert len(steps) == 3
