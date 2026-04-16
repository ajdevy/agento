"""Tests for memory commands."""

import pytest

from agento.application.cmd.memory import (
    MemoryCommand,
    MemoryCommandParser,
    MemoryCommandType,
)


@pytest.fixture
def parser():
    """Create a command parser."""
    return MemoryCommandParser()


class TestMemoryCommandParser:
    """Test memory command parser."""

    def test_parse_search_command(self, parser):
        """Test parsing search command."""
        command = parser.parse("/search python")

        assert command is not None
        assert command.type == MemoryCommandType.SEARCH
        assert command.args["query"] == "python"

    def test_parse_search_with_limit(self, parser):
        """Test parsing search with limit."""
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
