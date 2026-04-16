"""Memory commands for the CLI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, ClassVar

from agento.domain.entities.memory import MemoryType


class MemoryCommandType(Enum):
    """Memory command types."""

    SEARCH = "search"
    SAVE = "save"
    LIST = "list"
    FORGET = "forget"
    STATS = "stats"
    CLEAR = "clear"


@dataclass
class MemoryCommand:
    """Memory command representation."""

    type: MemoryCommandType
    args: dict[str, Any]


class MemoryCommandParser:
    """Parse memory commands."""

    COMMANDS: ClassVar[dict[str, MemoryCommandType]] = {
        "/search": MemoryCommandType.SEARCH,
        "/s": MemoryCommandType.SEARCH,
        "/save": MemoryCommandType.SAVE,
        "/list": MemoryCommandType.LIST,
        "/l": MemoryCommandType.LIST,
        "/forget": MemoryCommandType.FORGET,
        "/delete": MemoryCommandType.FORGET,
        "/stats": MemoryCommandType.STATS,
        "/clear": MemoryCommandType.CLEAR,
    }

    def parse(self, input_str: str) -> MemoryCommand | None:
        """Parse input string into memory command."""
        input_str = input_str.strip()

        if not input_str.startswith("/"):
            return None

        parts = input_str.split(maxsplit=2)
        cmd = parts[0].lower()

        cmd_type = self.COMMANDS.get(cmd)
        if not cmd_type:
            return None

        args: dict[str, Any] = {}

        if len(parts) > 1:
            if cmd_type == MemoryCommandType.SEARCH:
                args["query"] = parts[1]
                if len(parts) > 2:
                    try:
                        args["limit"] = int(parts[2])
                    except ValueError:
                        pass
            elif cmd_type == MemoryCommandType.SAVE:
                args["content"] = parts[1]
                if len(parts) > 2:
                    args["memory_type"] = parts[2]
            elif cmd_type == MemoryCommandType.LIST:
                if len(parts) > 1:
                    try:
                        args["limit"] = int(parts[1])
                    except ValueError:
                        args["memory_type"] = parts[1]
            elif cmd_type in (MemoryCommandType.FORGET, MemoryCommandType.STATS):
                if len(parts) > 1:
                    args["memory_id"] = parts[1]

        return MemoryCommand(type=cmd_type, args=args)

    def is_memory_command(self, input_str: str) -> bool:
        """Check if input is a memory command."""
        input_str = input_str.strip()
        if not input_str.startswith("/"):
            return False

        parts = input_str.split()
        if not parts:
            return False

        cmd = parts[0].lower()
        return cmd in self.COMMANDS

    def get_help_text(self) -> str:
        """Get help text for memory commands."""
        return """
**Memory Commands:**

| Command | Alias | Description |
|---------|-------|-------------|
| `/search <query>` | `/s` | Search memories |
| `/save <content>` | - | Save a memory |
| `/list` | `/l` | List recent memories |
| `/forget <id>` | `/delete` | Delete a memory |
| `/stats` | - | Show memory statistics |
| `/clear` | - | Clear all memories |

**Examples:**
- `/search python code`
- `/save Remember to use type hints`
- `/list 10`
- `/forget abc123`
"""


class MemoryCommandHandler:
    """Handle memory command execution."""

    def __init__(self, memory_service: Any):
        self.memory_service = memory_service
        self.parser = MemoryCommandParser()

    async def handle(
        self,
        command: MemoryCommand,
    ) -> str:
        """Handle memory command."""
        if command.type == MemoryCommandType.SEARCH:
            return await self._handle_search(command.args)
        elif command.type == MemoryCommandType.SAVE:
            return await self._handle_save(command.args)
        elif command.type == MemoryCommandType.LIST:
            return await self._handle_list(command.args)
        elif command.type == MemoryCommandType.FORGET:
            return await self._handle_forget(command.args)
        elif command.type == MemoryCommandType.STATS:
            return await self._handle_stats(command.args)
        elif command.type == MemoryCommandType.CLEAR:
            return await self._handle_clear(command.args)

        return "Unknown memory command"

    async def _handle_search(self, args: dict[str, Any]) -> str:
        """Handle search command."""
        query = args.get("query", "")
        limit = args.get("limit", 5)

        if not query:
            return "Usage: /search <query> [limit]"

        results = await self.memory_service.search_memories(query, top_k=limit)

        if not results:
            return f"No memories found for: {query}"

        output = [f"**Found {len(results)} memories:**\n"]
        for i, result in enumerate(results, 1):
            output.append(f"{i}. Score: {result.score:.2f}")
            output.append(f"   {result.memory.content[:100]}...")
            output.append("")

        return "\n".join(output)

    async def _handle_save(self, args: dict[str, Any]) -> str:
        """Handle save command."""
        content = args.get("content", "")
        memory_type_str = args.get("memory_type", "conversation")

        if not content:
            return "Usage: /save <content> [type]"

        try:
            memory_type = MemoryType(memory_type_str)
        except ValueError:
            memory_type = MemoryType.CONVERSATION

        memory_id = await self.memory_service.store_memory(
            content=content,
            memory_type=memory_type,
        )

        return f"Memory saved with ID: {memory_id}"

    async def _handle_list(self, args: dict[str, Any]) -> str:
        """Handle list command."""
        limit = args.get("limit", 10)

        memories = await self.memory_service.get_recent_memories(limit=limit)

        if not memories:
            return "No memories stored yet."

        output = ["**Recent Memories:**\n"]
        for i, memory in enumerate(memories, 1):
            output.append(f"{i}. [{memory.memory_type.value}]")
            output.append(f"   {memory.content[:80]}...")
            output.append(f"   ID: {memory.id}")
            output.append("")

        return "\n".join(output)

    async def _handle_forget(self, args: dict[str, Any]) -> str:
        """Handle forget command."""
        memory_id = args.get("memory_id", "")

        if not memory_id:
            return "Usage: /forget <memory_id>"

        success = await self.memory_service.delete_memory(memory_id)

        if success:
            return f"Memory {memory_id} deleted."
        return f"Memory {memory_id} not found."

    async def _handle_stats(self, args: dict[str, Any]) -> str:
        """Handle stats command."""
        stats = await self.memory_service.get_stats()

        output = ["**Memory Statistics:**\n"]
        output.append(f"- Total memories: {stats.total_memories}")
        output.append(f"- Average access count: {stats.average_access_count:.2f}")

        if stats.most_accessed_type:
            output.append(f"- Most accessed type: {stats.most_accessed_type}")

        output.append("\n**By Type:**")
        for mem_type, count in stats.by_type.items():
            output.append(f"- {mem_type}: {count}")

        return "\n".join(output)

    async def _handle_clear(self, args: dict[str, Any]) -> str:
        """Handle clear command."""
        memory_type_str = args.get("memory_type")

        if memory_type_str:
            try:
                memory_type = MemoryType(memory_type_str)
                count = await self.memory_service.clear_memories(memory_type)
                return f"Cleared {count} memories of type {memory_type.value}."
            except ValueError:
                return f"Unknown memory type: {memory_type_str}"

        await self.memory_service.clear_memories()
        return "All memories cleared."
