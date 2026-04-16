"""Tests for domain ports."""


import pytest


class TestLLMPort:
    """Tests for LLM port."""

    def test_llm_port_is_abstract(self):
        """Test LLMPort cannot be instantiated directly."""
        from agento.domain.ports.llm_port import LLMPort

        with pytest.raises(TypeError):
            LLMPort()

    def test_message_creation(self):
        """Test creating a message."""
        from agento.domain.ports.llm_port import Message

        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"

    def test_model_response_creation(self):
        """Test creating a model response."""
        from agento.domain.ports.llm_port import ModelResponse

        resp = ModelResponse(
            content="Hello!",
            model="openrouter/free",
            usage={"prompt_tokens": 10, "completion_tokens": 5},
            cost=0.0,
        )
        assert resp.content == "Hello!"
        assert resp.model == "openrouter/free"
        assert resp.cost == 0.0


class TestMemoryPort:
    """Tests for Memory port."""

    def test_memory_port_is_abstract(self):
        """Test MemoryPort cannot be instantiated directly."""
        from agento.domain.ports.memory_port import MemoryPort

        with pytest.raises(TypeError):
            MemoryPort()

    def test_memory_entry_creation(self):
        """Test creating a memory entry."""
        from agento.domain.ports.memory_port import MemoryEntry

        entry = MemoryEntry(
            id="test-1", content="Test content", metadata={"key": "value"}
        )
        assert entry.id == "test-1"
        assert entry.content == "Test content"
        assert entry.metadata["key"] == "value"

    def test_memory_entry_with_vector(self):
        """Test creating memory entry with vector."""
        from agento.domain.ports.memory_port import MemoryEntry

        entry = MemoryEntry(
            id="test-2", content="Content with embedding", vector=[0.1, 0.2, 0.3]
        )
        assert entry.vector == [0.1, 0.2, 0.3]


class TestToolPort:
    """Tests for Tool port."""

    def test_tool_port_is_abstract(self):
        """Test ToolPort cannot be instantiated directly."""
        from agento.domain.ports.tool_port import ToolPort

        with pytest.raises(TypeError):
            ToolPort()

    def test_tool_result_creation(self):
        """Test creating a tool result."""
        from agento.domain.ports.tool_port import ToolResult

        result = ToolResult(
            success=True, output="Command output", metadata={"exit_code": 0}
        )
        assert result.success is True
        assert result.output == "Command output"
        assert result.metadata["exit_code"] == 0

    def test_tool_result_error(self):
        """Test creating a tool result with error."""
        from agento.domain.ports.tool_port import ToolResult

        result = ToolResult(success=False, error="Command failed")
        assert result.success is False
        assert result.error == "Command failed"

    def test_tool_result_creation_with_all_fields(self):
        """Test creating tool result with all fields."""
        from agento.domain.ports.tool_port import ToolResult

        result = ToolResult(
            success=True, output="Output", error=None, metadata={"key": "value"}
        )
        assert result.success
        assert result.output == "Output"
        assert result.metadata == {"key": "value"}
