"""Tests for commands module."""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestCommandType:
    """Tests for CommandType enum."""

    def test_command_types(self):
        """Test command types exist."""
        from agento.application.commands import CommandType

        assert CommandType.CHAT.value == "chat"
        assert CommandType.CODE.value == "code"
        assert CommandType.DEVOPS.value == "devops"
        assert CommandType.PLAN.value == "plan"
        assert CommandType.EXECUTE.value == "execute"
        assert CommandType.MEMORY.value == "memory"
        assert CommandType.EXIT.value == "exit"


class TestCommand:
    """Tests for Command dataclass."""

    def test_command_creation(self):
        """Test command creation."""
        from agento.application.commands import Command, CommandType

        cmd = Command(type=CommandType.CHAT, args=["hello"], raw="hello")

        assert cmd.type == CommandType.CHAT
        assert cmd.args == ["hello"]
        assert cmd.raw == "hello"


class TestCommandParser:
    """Tests for CommandParser."""

    def test_parser_creation(self):
        """Test parser creation."""
        from agento.application.commands import CommandParser

        parser = CommandParser()
        assert parser is not None

    def test_parse_chat(self):
        """Test parsing chat message."""
        from agento.application.commands import CommandParser, CommandType

        parser = CommandParser()
        cmd = parser.parse("Hello world")

        assert cmd.type == CommandType.CHAT
        assert cmd.args == ["Hello world"]

    def test_parse_slash_command(self):
        """Test parsing slash command."""
        from agento.application.commands import CommandParser, CommandType

        parser = CommandParser()
        cmd = parser.parse("/code Write a function")

        assert cmd.type == CommandType.CODE
        assert cmd.args == ["Write", "a", "function"]

    def test_parse_alias(self):
        """Test parsing command aliases."""
        from agento.application.commands import CommandParser, CommandType

        parser = CommandParser()

        cmd = parser.parse("/c hello")
        assert cmd.type == CommandType.CHAT

        cmd = parser.parse("/d deploy")
        assert cmd.type == CommandType.DEVOPS

        cmd = parser.parse("/p plan task")
        assert cmd.type == CommandType.PLAN

    def test_is_exit_command(self):
        """Test exit command detection."""
        from agento.application.commands import CommandParser

        parser = CommandParser()

        assert parser.is_exit_command("/quit")
        assert parser.is_exit_command("/exit")
        assert parser.is_exit_command("/q")
        assert not parser.is_exit_command("/help")

    def test_is_help_command(self):
        """Test help command detection."""
        from agento.application.commands import CommandParser

        parser = CommandParser()

        assert parser.is_help_command("/help")
        assert parser.is_help_command("/h")
        assert parser.is_help_command("help")


class TestCommandHandler:
    """Tests for CommandHandler."""

    def test_handler_creation(self):
        """Test handler creation."""
        from agento.application.commands import CommandHandler

        mock_agent = MagicMock()
        handler = CommandHandler(mock_agent)

        assert handler.agent is mock_agent
        assert handler.parser is not None

    @pytest.mark.asyncio
    async def test_handle_chat(self):
        """Test handling chat command."""
        from agento.application.commands import CommandHandler

        mock_agent = MagicMock()
        mock_agent.chat = AsyncMock(return_value="Hello!")

        handler = CommandHandler(mock_agent)
        result = await handler.handle("Hello")

        assert result == "Hello!"
        mock_agent.chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_exit(self):
        """Test handling exit command."""
        from agento.application.commands import CommandHandler

        mock_agent = MagicMock()
        handler = CommandHandler(mock_agent)

        result = await handler.handle("/quit")

        assert result == "__EXIT__"

    @pytest.mark.asyncio
    async def test_handle_code(self):
        """Test handling code command."""
        from agento.application.commands import CommandHandler

        mock_agent = MagicMock()
        mock_agent.chat = AsyncMock(return_value="def hello(): pass")

        handler = CommandHandler(mock_agent)
        result = await handler.handle("/code Write hello function")

        assert result == "def hello(): pass"

    def test_get_help_text(self):
        """Test getting help text."""
        from agento.application.commands import CommandHandler

        mock_agent = MagicMock()
        handler = CommandHandler(mock_agent)

        help_text = handler.get_help_text()

        assert "/chat" in help_text
        assert "/code" in help_text
        assert "/help" in help_text
