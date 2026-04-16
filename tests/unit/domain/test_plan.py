"""Tests for Plan entity."""


from agento.domain.entities.plan import Plan
from agento.domain.entities.task import Task


class TestPlanEntity:
    """Tests for Plan entity."""

    def test_plan_creation_with_id_and_description(self):
        """Test creating a plan with id and description."""
        plan = Plan(id="plan-1", description="Test plan")

        assert plan.id == "plan-1"
        assert plan.description == "Test plan"
        assert plan.tasks == []
        assert plan.current_task_index == 0
        assert plan.status == "pending"

    def test_plan_is_complete_when_no_tasks(self):
        """Test is_complete returns True when no tasks."""
        plan = Plan(id="plan-1", description="Empty plan")
        assert plan.is_complete() is True

    def test_plan_is_complete_with_all_completed_tasks(self):
        """Test is_complete returns True when all tasks done."""
        plan = Plan(id="plan-1", description="Complete plan")
        task1 = Task(id="t1", description="Task 1")
        task2 = Task(id="t2", description="Task 2")

        task1.mark_completed("Done")
        task2.mark_completed("Done")

        plan.add_task(task1)
        plan.add_task(task2)

        assert plan.is_complete() is True

    def test_plan_is_not_complete_with_pending_tasks(self):
        """Test is_complete returns False when tasks pending."""
        plan = Plan(id="plan-1", description="Incomplete plan")
        task1 = Task(id="t1", description="Task 1")
        task2 = Task(id="t2", description="Task 2")

        task1.mark_completed("Done")
        # task2 still pending

        plan.add_task(task1)
        plan.add_task(task2)

        assert plan.is_complete() is False

    def test_advance_increments_index(self):
        """Test advance increments current_task_index."""
        plan = Plan(id="plan-1", description="Test plan")
        plan.add_task(Task(id="t1", description="Task 1"))
        plan.add_task(Task(id="t2", description="Task 2"))

        assert plan.current_task_index == 0

        plan.advance()
        assert plan.current_task_index == 1

        plan.advance()
        assert plan.current_task_index == 2

    def test_get_next_task_returns_none_when_no_tasks(self):
        """Test get_next_task returns None when no tasks."""
        plan = Plan(id="plan-1", description="Empty plan")

        assert plan.get_next_task() is None

    def test_get_next_task_respects_index(self):
        """Test get_next_task returns task at current index."""
        plan = Plan(id="plan-1", description="Test plan")
        task1 = Task(id="t1", description="Task 1")
        task2 = Task(id="t2", description="Task 2")

        plan.add_task(task1)
        plan.add_task(task2)

        assert plan.get_next_task() == task1

        plan.advance()

        assert plan.get_next_task() == task2

    def test_get_next_task_returns_none_when_exhausted(self):
        """Test get_next_task returns None when exhausted."""
        plan = Plan(id="plan-1", description="Test plan")
        task1 = Task(id="t1", description="Task 1")

        plan.add_task(task1)
        plan.advance()  # Move past the only task

        assert plan.get_next_task() is None
