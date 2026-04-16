"""Command handling for Agento."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

# mypy: disable-error-code=no-any-return


class CommandType(Enum):
    """Command types."""

    CHAT = "chat"
    CODE = "code"
    DEVOPS = "devops"
    PLAN = "plan"
    EXECUTE = "execute"
    MEMORY = "memory"
    EXIT = "exit"


@dataclass
class Command:
    """Command representation."""

    type: CommandType
    args: list[str]
    raw: str


class CommandParser:
    """Parse user commands."""

    COMMANDS: ClassVar[dict[str, CommandType]] = {
        "/chat": CommandType.CHAT,
        "/c": CommandType.CHAT,
        "/code": CommandType.CODE,
        "/devops": CommandType.DEVOPS,
        "/d": CommandType.DEVOPS,
        "/plan": CommandType.PLAN,
        "/p": CommandType.PLAN,
        "/execute": CommandType.EXECUTE,
        "/x": CommandType.EXECUTE,
        "/memory": CommandType.MEMORY,
        "/m": CommandType.MEMORY,
        "/quit": CommandType.EXIT,
        "/exit": CommandType.EXIT,
        "/q": CommandType.EXIT,
    }

    def parse(self, input_str: str) -> Command:
        """Parse input string into command."""
        input_str = input_str.strip()

        if not input_str.startswith("/"):
            return Command(
                type=CommandType.CHAT,
                args=[input_str],
                raw=input_str,
            )

        parts = input_str.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1].split() if len(parts) > 1 else []

        cmd_type = self.COMMANDS.get(cmd, CommandType.CHAT)

        return Command(
            type=cmd_type,
            args=args,
            raw=input_str,
        )

    def is_exit_command(self, input_str: str) -> bool:
        """Check if input is an exit command."""
        return input_str.strip().lower() in ("/quit", "/exit", "/q")

    def is_help_command(self, input_str: str) -> bool:
        """Check if input is a help command."""
        return input_str.strip().lower() in ("/help", "/h", "help")


class CommandHandler:
    """Handle command execution."""

    def __init__(self, agent: Any):
        self.agent = agent
        self.parser = CommandParser()

    async def handle(self, input_str: str) -> str:
        """Handle user input."""
        command = self.parser.parse(input_str)

        if command.type == CommandType.EXIT:
            return "__EXIT__"

        if command.type == CommandType.CHAT:
            return await self.agent.chat(command.raw)

        if command.type == CommandType.CODE:  # pragma: no cover
            return await self.agent.chat(f"[CODE] {command.raw}")  # pragma: no cover

        if command.type == CommandType.DEVOPS:  # pragma: no cover
            return await self.agent.chat(f"[DEVOPS] {command.raw}")  # pragma: no cover

        if command.type == CommandType.PLAN:  # pragma: no cover
            return await self.agent.chat(
                f"[PLANNING] {command.raw}"
            )  # pragma: no cover

        if command.type == CommandType.EXECUTE:  # pragma: no cover
            return await self.agent.chat(f"[EXECUTE] {command.raw}")  # pragma: no cover

        if command.type == CommandType.MEMORY:  # pragma: no cover
            return await self.agent.chat(f"[MEMORY] {command.raw}")  # pragma: no cover

        return await self.agent.chat(command.raw)  # pragma: no cover

    def get_help_text(self) -> str:
        """Get help text."""
        return """
**Agento Commands:**

| Command | Alias | Description |
|---------|-------|-------------|
| `/chat <msg>` | default | Chat with the agent |
| `/code <task>` | - | Generate code |
| `/devops <task>` | `/d` | DevOps tasks |
| `/plan <task>` | `/p` | Create execution plan |
| `/execute <task>` | `/x` | Execute plan |
| `/memory <query>` | `/m` | Query memory |
| `/help` | `/h` | Show this help |
| `/quit` | `/q` | Exit |
"""
