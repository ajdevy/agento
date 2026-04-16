"""Domain ports - interfaces for infrastructure adapters."""

from agento.domain.ports.llm_port import LLMPort, Message, ModelResponse
from agento.domain.ports.memory_port import MemoryPort, MemoryEntry
from agento.domain.ports.tool_port import ToolPort, ToolResult

__all__ = [
    "LLMPort",
    "Message",
    "ModelResponse",
    "MemoryPort",
    "MemoryEntry",
    "ToolPort",
    "ToolResult",
]
