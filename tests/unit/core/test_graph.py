"""Tests for graph nodes."""

from langchain_core.messages import AIMessage, HumanMessage


class TestRouterNode:
    """Tests for router_node function."""

    def test_router_with_empty_messages(self):
        """Test router returns current_mode for empty messages."""
        from agento.core.graph import router_node
        from agento.core.state import AgentState

        state = AgentState(current_mode="chat")
        result = router_node(state)

        assert result["current_mode"] == "chat"

    def test_router_with_user_message(self):
        """Test router with user message returns current_mode."""
        from agento.core.graph import router_node
        from agento.core.state import AgentState

        state = AgentState(current_mode="code")
        state.messages.append(HumanMessage(content="Hello"))

        result = router_node(state)
        assert result["current_mode"] == "code"

    def test_router_with_assistant_message(self):
        """Test router with assistant message returns current_mode."""
        from agento.core.graph import router_node
        from agento.core.state import AgentState

        state = AgentState(current_mode="plan")
        state.messages.append(AIMessage(content="Hi"))

        result = router_node(state)
        assert result["current_mode"] == "plan"


class TestChatNode:
    """Tests for chat_node function."""

    def test_chat_node_returns_chat_mode(self):
        """Test chat_node sets current_mode to chat."""
        from agento.core.graph import chat_node
        from agento.core.state import AgentState

        state = AgentState()
        result = chat_node(state)

        assert result["current_mode"] == "chat"


class TestPlannerNode:
    """Tests for planner_node function."""

    def test_planner_node_returns_empty_plan(self):
        """Test planner_node returns empty current_plan."""
        from agento.core.graph import planner_node
        from agento.core.state import AgentState

        state = AgentState()
        result = planner_node(state)

        assert result["current_plan"] == []


class TestExecutorNode:
    """Tests for executor_node function."""

    def test_executor_node_returns_empty_dict(self):
        """Test executor_node returns empty dict."""
        from agento.core.graph import executor_node
        from agento.core.state import AgentState

        state = AgentState()
        result = executor_node(state)

        assert result == {}


class TestReflectorNode:
    """Tests for reflector_node function."""

    def test_reflector_node_returns_empty_dict(self):
        """Test reflector_node returns empty dict."""
        from agento.core.graph import reflector_node
        from agento.core.state import AgentState

        state = AgentState()
        result = reflector_node(state)

        assert result == {}


class TestRouteMode:
    """Tests for route_mode function."""

    def test_route_mode_returns_current_mode(self):
        """Test route_mode returns current_mode."""
        from agento.core.graph import route_mode
        from agento.core.state import AgentState

        state = AgentState(current_mode="code")
        result = route_mode(state)

        assert result == "code"


class TestShouldContinue:
    """Tests for should_continue function."""

    def test_should_continue_end_when_error_count_high(self):
        """Test returns end when error_count > 3."""
        from agento.core.graph import should_continue
        from agento.core.state import AgentState

        state = AgentState(error_count=5)
        result = should_continue(state)

        assert result == "end"

    def test_should_continue_end_when_all_tasks_complete(self):
        """Test returns end when all tasks complete."""
        from agento.core.graph import should_continue
        from agento.core.state import AgentState

        state = AgentState(
            current_plan=[{"id": "1"}, {"id": "2"}],
            completed_tasks=["1", "2"],
            error_count=0,
        )
        result = should_continue(state)

        assert result == "end"

    def test_should_continue_continue_when_work_remains(self):
        """Test returns continue when work remains."""
        from agento.core.graph import should_continue
        from agento.core.state import AgentState

        state = AgentState(
            current_plan=[{"id": "1"}, {"id": "2"}],
            completed_tasks=["1"],
            error_count=0,
        )
        result = should_continue(state)

        assert result == "continue"
