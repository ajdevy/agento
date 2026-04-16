"""Tests for core state and graph."""

import pytest

from agento.core.state import AgentState, Message
from agento.core.graph import create_agent_graph


class TestAgentState:
    """Tests for AgentState."""

    def test_state_creation(self):
        """Test creating agent state."""
        state = AgentState(session_id="test-session")

        assert state.session_id == "test-session"
        assert state.messages == []
        assert state.current_mode == "idle"

    def test_add_message(self):
        """Test adding messages."""
        state = AgentState(session_id="test")

        # Messages are added via the graph machinery
        state.messages.append(Message(role="user", content="Hello"))

        assert len(state.messages) == 1
        assert state.messages[0].content == "Hello"

    def test_state_defaults(self):
        """Test state defaults."""
        state = AgentState()

        assert state.current_plan == []
        assert state.completed_tasks == []
        assert state.memory_context == []
        assert state.tools_used == []
        assert state.error_count == 0
        assert state.cost_total == 0.0


class TestAgentGraph:
    """Tests for agent graph."""

    def test_create_graph(self):
        """Test creating the agent graph."""
        graph = create_agent_graph()

        assert graph is not None

    def test_graph_compiled(self):
        """Test that graph compiles."""
        graph = create_agent_graph()

        # Check it's a compiled graph
        assert hasattr(graph, "invoke")

    def test_graph_nodes(self):
        """Test graph has expected nodes."""
        graph = create_agent_graph()

        # Check nodes exist
        assert graph.nodes is not None
