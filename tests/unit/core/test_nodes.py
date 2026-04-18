"""Tests for core nodes."""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestChatNode:
    """Tests for chat_node_fn."""

    @pytest.mark.asyncio
    async def test_chat_node_success(self):
        """Test chat node with successful response."""
        from langchain_core.messages import HumanMessage

        from agento.core.nodes import chat_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            messages=[HumanMessage(content="Hello")],
            model="openrouter/free",
        )

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Hello! How can I help?"
        mock_response.cost = 0.0
        mock_client.chat.return_value = mock_response

        result = await chat_node_fn(state, mock_client)

        assert result["current_mode"] == "chat"
        assert result["messages"] is not None
        assert len(result["messages"]) == 1
        assert result["messages"][0].role == "assistant"

    @pytest.mark.asyncio
    async def test_chat_node_error(self):
        """Test chat node with error."""
        from langchain_core.messages import HumanMessage

        from agento.core.nodes import chat_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            messages=[HumanMessage(content="Hello")],
            model="openrouter/free",
            error_count=0,
        )

        mock_client = AsyncMock()
        mock_client.chat.side_effect = Exception("API Error")

        result = await chat_node_fn(state, mock_client)

        assert result["error_count"] == 1
        assert result["messages"] is None


class TestPlannerNode:
    """Tests for planner_node_fn."""

    @pytest.mark.asyncio
    async def test_planner_node_empty_messages(self):
        """Test planner node with no messages."""
        from agento.core.nodes import planner_node_fn
        from agento.core.state import AgentState

        state = AgentState(messages=[])

        mock_client = AsyncMock()

        result = await planner_node_fn(state, mock_client)

        assert result["current_plan"] == []
        assert result["current_mode"] == "planning"

    @pytest.mark.asyncio
    async def test_planner_node_with_plan(self):
        """Test planner node generates plan."""
        from langchain_core.messages import HumanMessage

        from agento.core.nodes import planner_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            messages=[HumanMessage(content="Create a web app")],
        )

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = (
            '[{"id": "1", "description": "Setup project", "type": "code"}]'
        )
        mock_response.cost = 0.0
        mock_client.chat.return_value = mock_response

        result = await planner_node_fn(state, mock_client)

        assert result["current_mode"] == "planning"
        assert len(result["current_plan"]) == 1
        assert result["current_plan"][0]["id"] == "1"


class TestExecutorNode:
    """Tests for executor_node_fn."""

    @pytest.mark.asyncio
    async def test_executor_node_no_plan(self):
        """Test executor node with no plan."""
        from agento.core.nodes import executor_node_fn
        from agento.core.state import AgentState

        state = AgentState(current_plan=[])

        mock_client = AsyncMock()

        result = await executor_node_fn(state, mock_client)

        assert result["completed_tasks"] == []

    @pytest.mark.asyncio
    async def test_executor_node_with_plan(self):
        """Test executor node executes plan."""
        from agento.core.nodes import executor_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            current_plan=[
                {"id": "1", "description": "Setup project", "type": "code"},
                {"id": "2", "description": "Add features", "type": "code"},
            ],
            completed_tasks=[],
        )

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Setup complete!"
        mock_response.cost = 0.0
        mock_client.chat.return_value = mock_response

        result = await executor_node_fn(state, mock_client)

        assert len(result["completed_tasks"]) == 1
        assert "1" in result["completed_tasks"]

    @pytest.mark.asyncio
    async def test_executor_node_all_complete(self):
        """Test executor node when all tasks complete."""
        from agento.core.nodes import executor_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            current_plan=[
                {"id": "1", "description": "Setup project", "type": "code"},
            ],
            completed_tasks=["1"],
        )

        mock_client = AsyncMock()

        result = await executor_node_fn(state, mock_client)

        assert result["completed_tasks"] == ["1"]


class TestReflectorNode:
    """Tests for reflector_node_fn."""

    @pytest.mark.asyncio
    async def test_reflector_node_no_plan(self):
        """Test reflector node with no plan."""
        from agento.core.nodes import reflector_node_fn
        from agento.core.state import AgentState

        state = AgentState(current_plan=[])

        mock_client = AsyncMock()

        result = await reflector_node_fn(state, mock_client)

        assert result["current_mode"] == "reflector"

    @pytest.mark.asyncio
    async def test_reflector_node_continue(self):
        """Test reflector node continues execution."""
        from agento.core.nodes import reflector_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            current_plan=[
                {"id": "1", "description": "Task 1", "type": "code"},
                {"id": "2", "description": "Task 2", "type": "code"},
            ],
            completed_tasks=["1"],
            error_count=0,
        )

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "YES, continue with next task"
        mock_response.cost = 0.0
        mock_client.chat.return_value = mock_response

        result = await reflector_node_fn(state, mock_client)

        assert result["current_mode"] == "executor"

    @pytest.mark.asyncio
    async def test_reflector_node_end(self):
        """Test reflector node ends execution."""
        from agento.core.nodes import reflector_node_fn
        from agento.core.state import AgentState

        state = AgentState(
            current_plan=[
                {"id": "1", "description": "Task 1", "type": "code"},
            ],
            completed_tasks=["1"],
            error_count=0,
        )

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "NO, all tasks complete"
        mock_response.cost = 0.0
        mock_client.chat.return_value = mock_response

        result = await reflector_node_fn(state, mock_client)

        assert result["current_mode"] == "chat"
