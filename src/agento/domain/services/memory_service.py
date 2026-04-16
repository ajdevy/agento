"""Memory service - domain logic for memory operations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agento.domain.entities.memory import Memory, MemoryType
from agento.domain.ports.memory_port import MemoryEntry, MemoryPort


@dataclass
class MemorySearchResult:
    """Memory search result."""

    memory: Memory
    score: float
    distance: float | None = None


@dataclass
class MemoryStats:
    """Memory statistics."""

    total_memories: int
    by_type: dict[str, int]
    average_access_count: float
    most_accessed_type: str | None


class MemoryService:
    """Domain service for memory operations."""

    def __init__(
        self,
        memory_port: MemoryPort,
    ):
        self._port = memory_port

    async def store_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.CONVERSATION,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Store a new memory."""
        meta = metadata or {}
        meta["memory_type"] = memory_type.value

        return await self._port.add(content, meta)

    async def search_memories(
        self,
        query: str,
        top_k: int = 5,
        memory_type: MemoryType | None = None,
    ) -> list[MemorySearchResult]:
        """Search memories by query."""
        entries = await self._port.search(query, top_k * 2)

        results = []
        for entry in entries:
            if memory_type and entry.metadata.get("memory_type") != memory_type.value:
                continue

            memory = self._entry_to_memory(entry)
            score = self._calculate_relevance(query, entry.content)

            results.append(
                MemorySearchResult(
                    memory=memory,
                    score=score,
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

    async def get_memory(
        self,
        memory_id: str,
    ) -> Memory | None:
        """Get a specific memory."""
        entry = await self._port.get(memory_id)
        if not entry:
            return None
        return self._entry_to_memory(entry)

    async def delete_memory(
        self,
        memory_id: str,
    ) -> bool:
        """Delete a memory."""
        return await self._port.delete(memory_id)

    async def get_memories_by_type(
        self,
        memory_type: MemoryType,
    ) -> list[Memory]:
        """Get all memories of a specific type."""
        entries = await self._port.search("", top_k=100)

        memories = []
        for entry in entries:
            if entry.metadata.get("memory_type") == memory_type.value:
                memories.append(self._entry_to_memory(entry))

        return memories

    async def get_recent_memories(
        self,
        limit: int = 10,
    ) -> list[Memory]:
        """Get recent memories."""
        entries = await self._port.search("", top_k=limit)
        return [self._entry_to_memory(entry) for entry in entries]

    async def get_stats(self) -> MemoryStats:
        """Get memory statistics."""
        count = await self._port.count()
        entries = await self._port.search("", top_k=1000)

        type_counts: dict[str, int] = {}
        total_access = 0

        for entry in entries:
            mem_type = entry.metadata.get("memory_type", "unknown")
            type_counts[mem_type] = type_counts.get(mem_type, 0) + 1
            total_access += entry.metadata.get("access_count", 0)

        most_accessed = (
            max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
        )
        avg_access = total_access / count if count > 0 else 0.0

        return MemoryStats(
            total_memories=count,
            by_type=type_counts,
            average_access_count=avg_access,
            most_accessed_type=most_accessed,
        )

    async def clear_memories(
        self,
        memory_type: MemoryType | None = None,
    ) -> int:
        """Clear memories, optionally by type."""
        if memory_type is None:
            await self._port.clear()
            count = await self._port.count()
            return 0

        entries = await self._port.search("", top_k=1000)
        count = 0

        for entry in entries:
            if entry.metadata.get("memory_type") == memory_type.value:
                if await self._port.delete(entry.id):
                    count += 1

        return count

    def _entry_to_memory(self, entry: MemoryEntry) -> Memory:
        """Convert memory entry to domain model."""
        return Memory(
            id=entry.id,
            content=entry.content,
            memory_type=MemoryType(entry.metadata.get("memory_type", "conversation")),
            metadata=entry.metadata,
        )

    def _calculate_relevance(
        self,
        query: str,
        content: str,
    ) -> float:
        """Calculate relevance score between query and content."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words or not content_words:
            return 0.0

        intersection = query_words & content_words
        union = query_words | content_words

        return len(intersection) / len(union) if union else 0.0

    async def update_memory_access(
        self,
        memory_id: str,
    ) -> bool:
        """Update memory access count."""
        entry = await self._port.get(memory_id)
        if not entry:
            return False

        current_count = entry.metadata.get("access_count", 0)
        entry.metadata["access_count"] = current_count + 1

        await self._port.delete(memory_id)
        await self._port.add(entry.content, entry.metadata)

        return True
