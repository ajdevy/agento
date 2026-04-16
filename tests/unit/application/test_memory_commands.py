"""Tests for memory commands."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agento.application.cmd.memory import (
    MemoryCommand,
    MemoryCommandHandler,
    MemoryCommandParser,
    MemoryCommandType,
)
from agento.domain.entities.memory import Memory, MemoryType
from agento.domain.services.memory_service import MemorySearchResult, MemoryStats


@pytest.fixture
def parser():
    """Create a command parser."""
    return MemoryCommandParser()


@pytest.fixture
def mock_memory_service():
    """Create a mock memory service."""
    service = MagicMock()
    service.search_memories = AsyncMock(return_value=[])
    service.store_memory = AsyncMock(return_value="test-id")
    service.get_recent_memories = AsyncMock(return_value=[])
    service.delete_memory = AsyncMock(return_value=True)
    service.get_stats = AsyncMock(
        return_value=MagicMock(
            total_memories=0,
            by_type={},
            average_access_count=0.0,
            most_accessed_type=None,
        )
    )
    service.clear_memories = AsyncMock(return_value=0)
    return service


@pytest.fixture
def handler(mock_memory_service):
    """Create a command handler."""
    return MemoryCommandHandler(mock_memory_service)


class TestMemoryCommandParser:
    """Test memory command parser."""

    def test_parse_search_command(self, parser):
        """Test parsing search command."""
        command = parser.parse("/search python")

        assert command is not None
        assert command.type == MemoryCommandType.SEARCH
        assert command.args["query"] == "python"

    def test_parse_search_with_limit(self, parser):
        """Test parsing search command with limit."""
        command = parser.parse("/search python 10")

        assert command is not None
        assert command.args["query"] == "python"
        assert command.args.get("limit") == 10

    def test_parse_save_command(self, parser):
        """Test parsing save command."""
        command = parser.parse("/save Remember")

        assert command is not None
        assert command.type == MemoryCommandType.SAVE
        assert command.args["content"] == "Remember"

    def test_parse_list_command(self, parser):
        """Test parsing list command."""
        command = parser.parse("/list 10")

        assert command is not None
        assert command.type == MemoryCommandType.LIST
        assert command.args["limit"] == 10

    def test_parse_forget_command(self, parser):
        """Test parsing forget command."""
        command = parser.parse("/forget abc123")

        assert command is not None
        assert command.type == MemoryCommandType.FORGET
        assert command.args["memory_id"] == "abc123"

    def test_parse_stats_command(self, parser):
        """Test parsing stats command."""
        command = parser.parse("/stats")

        assert command is not None
        assert command.type == MemoryCommandType.STATS

    def test_parse_clear_command(self, parser):
        """Test parsing clear command."""
        command = parser.parse("/clear")

        assert command is not None
        assert command.type == MemoryCommandType.CLEAR

    def test_parse_alias_search(self, parser):
        """Test parsing search alias."""
        command = parser.parse("/s test query")

        assert command is not None
        assert command.type == MemoryCommandType.SEARCH

    def test_parse_alias_list(self, parser):
        """Test parsing list alias."""
        command = parser.parse("/l")

        assert command is not None
        assert command.type == MemoryCommandType.LIST

    def test_parse_alias_delete(self, parser):
        """Test parsing delete alias."""
        command = parser.parse("/delete abc123")

        assert command is not None
        assert command.type == MemoryCommandType.FORGET

    def test_parse_non_memory_command(self, parser):
        """Test parsing non-memory command."""
        command = parser.parse("/help")
        assert command is None

    def test_parse_empty_string(self, parser):
        """Test parsing empty string."""
        command = parser.parse("")
        assert command is None

    def test_parse_regular_text(self, parser):
        """Test parsing regular text."""
        command = parser.parse("Hello world")
        assert command is None

    def test_is_memory_command_true(self, parser):
        """Test is_memory_command with valid command."""
        assert parser.is_memory_command("/search test") is True
        assert parser.is_memory_command("/save test") is True
        assert parser.is_memory_command("/list") is True

    def test_is_memory_command_false(self, parser):
        """Test is_memory_command with invalid command."""
        assert parser.is_memory_command("hello") is False
        assert parser.is_memory_command("/help") is False
        assert parser.is_memory_command("") is False

    def test_get_help_text(self, parser):
        """Test getting help text."""
        help_text = parser.get_help_text()

        assert "Memory Commands" in help_text
        assert "/search" in help_text
        assert "/save" in help_text
        assert "/list" in help_text


class TestMemoryCommand:
    """Test memory command model."""

    def test_create_command(self):
        """Test creating a command."""
        command = MemoryCommand(
            type=MemoryCommandType.SEARCH,
            args={"query": "test"},
        )

        assert command.type == MemoryCommandType.SEARCH
        assert command.args["query"] == "test"


class TestMemoryCommandHandler:
    """Test memory command handler."""

    @pytest.mark.asyncio
    async def test_handler_search(self, handler, mock_memory_service):
        """Test handling search command."""
        mock_memory_service.search_memories = AsyncMock(
            return_value=[
                MemorySearchResult(
                    memory=Memory(id="1", content="Test content"),
                    score=0.95,
                ),
            ]
        )

        command = MemoryCommand(
            type=MemoryCommandType.SEARCH,
            args={"query": "test"},
        )

        result = await handler.handle(command)
        assert "Found" in result
        assert "Test content" in result

    @pytest.mark.asyncio
    async def test_handler_search_empty_query(self, handler):
        """Test handling search with empty query."""
        command = MemoryCommand(
            type=MemoryCommandType.SEARCH,
            args={},
        )

        result = await handler.handle(command)
        assert "Usage:" in result

    @pytest.mark.asyncio
    async def test_handler_search_no_results(self, handler, mock_memory_service):
        """Test handling search with no results."""
        mock_memory_service.search_memories = AsyncMock(return_value=[])

        command = MemoryCommand(
            type=MemoryCommandType.SEARCH,
            args={"query": "nonexistent"},
        )

        result = await handler.handle(command)
        assert "No memories found" in result

    @pytest.mark.asyncio
    async def test_handler_save(self, handler, mock_memory_service):
        """Test handling save command."""
        command = MemoryCommand(
            type=MemoryCommandType.SAVE,
            args={"content": "Remember this"},
        )

        result = await handler.handle(command)
        assert "saved" in result.lower()

    @pytest.mark.asyncio
    async def test_handler_save_empty_content(self, handler):
        """Test handling save with empty content."""
        command = MemoryCommand(
            type=MemoryCommandType.SAVE,
            args={},
        )

        result = await handler.handle(command)
        assert "Usage:" in result

    @pytest.mark.asyncio
    async def test_handler_list(self, handler, mock_memory_service):
        """Test handling list command."""
        mock_memory_service.get_recent_memories = AsyncMock(
            return_value=[
                Memory(id="1", content="Memory 1", memory_type=MemoryType.CONVERSATION),
                Memory(id="2", content="Memory 2", memory_type=MemoryType.CONVERSATION),
            ]
        )

        command = MemoryCommand(
            type=MemoryCommandType.LIST,
            args={},
        )

        result = await handler.handle(command)
        assert "Recent Memories" in result

    @pytest.mark.asyncio
    async def test_handler_list_empty(self, handler, mock_memory_service):
        """Test handling list with no memories."""
        mock_memory_service.get_recent_memories = AsyncMock(return_value=[])

        command = MemoryCommand(
            type=MemoryCommandType.LIST,
            args={},
        )

        result = await handler.handle(command)
        assert "No memories" in result

    @pytest.mark.asyncio
    async def test_handler_forget(self, handler, mock_memory_service):
        """Test handling forget command."""
        mock_memory_service.delete_memory = AsyncMock(return_value=True)

        command = MemoryCommand(
            type=MemoryCommandType.FORGET,
            args={"memory_id": "test-id"},
        )

        result = await handler.handle(command)
        assert "deleted" in result.lower()

    @pytest.mark.asyncio
    async def test_handler_forget_not_found(self, handler, mock_memory_service):
        """Test handling forget with not found."""
        mock_memory_service.delete_memory = AsyncMock(return_value=False)

        command = MemoryCommand(
            type=MemoryCommandType.FORGET,
            args={"memory_id": "nonexistent"},
        )

        result = await handler.handle(command)
        assert "not found" in result.lower()

    @pytest.mark.asyncio
    async def test_handler_stats(self, handler, mock_memory_service):
        """Test handling stats command."""
        mock_memory_service.get_stats = AsyncMock(
            return_value=MemoryStats(
                total_memories=5,
                by_type={"conversation": 3, "code_snippet": 2},
                average_access_count=2.5,
                most_accessed_type="conversation",
            )
        )

        command = MemoryCommand(
            type=MemoryCommandType.STATS,
            args={},
        )

        result = await handler.handle(command)
        assert "Memory Statistics" in result
        assert "5" in result

    @pytest.mark.asyncio
    async def test_handler_clear(self, handler, mock_memory_service):
        """Test handling clear command."""
        mock_memory_service.clear_memories = AsyncMock(return_value=3)

        command = MemoryCommand(
            type=MemoryCommandType.CLEAR,
            args={},
        )

        result = await handler.handle(command)
        assert "cleared" in result.lower()

    @pytest.mark.asyncio
    async def test_handler_unknown(self, handler):
        """Test handling with search having no results (edge case)."""
        command = MemoryCommand(
            type=MemoryCommandType.SEARCH,
            args={"query": ""},
        )

        result = await handler.handle(command)
        assert "Usage:" in result
