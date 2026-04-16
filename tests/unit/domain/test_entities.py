"""Tests for domain entities."""


from agento.domain.entities.memory import Memory, MemoryType
from agento.domain.entities.plan import Plan
from agento.domain.entities.task import Task, TaskStatus


class TestTask:
    """Tests for Task entity."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(
            id="task-1",
            description="Test task",
        )

        assert task.id == "task-1"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.retry_count == 0

    def test_task_mark_in_progress(self):
        """Test marking task as in progress."""
        task = Task(id="task-1", description="Test task")
        task.mark_in_progress()

        assert task.status == TaskStatus.IN_PROGRESS

    def test_task_mark_completed(self):
        """Test marking task as completed."""
        task = Task(id="task-1", description="Test task")
        task.mark_completed("Result")

        assert task.status == TaskStatus.COMPLETED
        assert task.result == "Result"

    def test_task_mark_failed(self):
        """Test marking task as failed."""
        task = Task(id="task-1", description="Test task")
        task.mark_failed("Error message")

        assert task.status == TaskStatus.FAILED
        assert task.error == "Error message"

    def test_task_can_retry(self):
        """Test retry logic."""
        task = Task(id="task-1", description="Test task", max_retries=3)

        assert task.can_retry() is True

        task.retry_count = 3
        assert task.can_retry() is False

    def test_task_increment_retry(self):
        """Test incrementing retry count."""
        task = Task(id="task-1", description="Test task")
        task.increment_retry()

        assert task.retry_count == 1


class TestPlan:
    """Tests for Plan entity."""

    def test_plan_creation(self):
        """Test creating a plan."""
        plan = Plan(
            id="plan-1",
            description="Test plan",
        )

        assert plan.id == "plan-1"
        assert plan.tasks == []
        assert plan.current_task_index == 0

    def test_plan_add_task(self):
        """Test adding tasks to plan."""
        plan = Plan(id="plan-1", description="Test plan")
        task = Task(id="task-1", description="Task 1")

        plan.add_task(task)

        assert len(plan.tasks) == 1
        assert plan.tasks[0] == task

    def test_plan_get_next_task(self):
        """Test getting next task."""
        plan = Plan(id="plan-1", description="Test plan")
        task1 = Task(id="task-1", description="Task 1")
        task2 = Task(id="task-2", description="Task 2")

        plan.add_task(task1)
        plan.add_task(task2)

        assert plan.get_next_task() == task1
        plan.advance()
        assert plan.get_next_task() == task2

    def test_plan_progress(self):
        """Test plan progress."""
        plan = Plan(id="plan-1", description="Test plan")
        task1 = Task(id="task-1", description="Task 1")
        task2 = Task(id="task-2", description="Task 2")

        plan.add_task(task1)
        plan.add_task(task2)

        assert plan.progress == (0, 2)

        task1.mark_completed("Done")
        assert plan.progress == (1, 2)


class TestMemory:
    """Tests for Memory entity."""

    def test_memory_creation(self):
        """Test creating memory."""
        memory = Memory(
            id="mem-1",
            content="Test memory content",
        )

        assert memory.id == "mem-1"
        assert memory.content == "Test memory content"
        assert memory.memory_type == MemoryType.CONVERSATION
        assert memory.access_count == 0

    def test_memory_increment_access(self):
        """Test incrementing access count."""
        memory = Memory(id="mem-1", content="Test content")
        memory.increment_access()

        assert memory.access_count == 1

    def test_memory_update_relevance(self):
        """Test updating relevance score."""
        memory = Memory(id="mem-1", content="Test content")
        memory.update_relevance(0.95)

        assert memory.relevance_score == 0.95
