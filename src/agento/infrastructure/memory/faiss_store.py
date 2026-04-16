"""FAISS vector store implementation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from agento.domain.ports.memory_port import MemoryEntry, MemoryPort


@dataclass
class MemoryRecord:
    """Internal memory record with vector."""

    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    vector: np.ndarray | None = None


class FAISSStore(MemoryPort):
    """FAISS-based vector store."""

    def __init__(
        self,
        dimension: int = 384,
        index_type: str = "flat",
    ):
        self.dimension = dimension
        self.index_type = index_type
        self._entries: dict[str, MemoryEntry] = {}
        self._vectors: dict[str, np.ndarray] = {}
        self._id_to_vector_idx: dict[str, int] = {}
        self._next_idx = 0
        self._index = None

    async def add(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a memory entry."""
        memory_id = str(uuid.uuid4())
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            metadata=metadata or {},
        )
        self._entries[memory_id] = entry
        return memory_id

    async def add_with_vector(
        self,
        content: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a memory entry with pre-computed vector."""
        memory_id = str(uuid.uuid4())
        vector_array = np.array(vector, dtype=np.float32)

        if len(vector_array.shape) == 1:
            vector_array = vector_array.reshape(1, -1)

        entry = MemoryEntry(
            id=memory_id,
            content=content,
            metadata=metadata or {},
            vector=vector,
        )
        self._entries[memory_id] = entry
        self._vectors[memory_id] = vector_array
        self._id_to_vector_idx[memory_id] = self._next_idx
        self._next_idx += 1

        self._rebuild_index()
        return memory_id

    async def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[MemoryEntry]:
        """Search for relevant memories (semantic search)."""
        results: list[tuple[float, MemoryEntry]] = []

        if not self._vectors:
            return []

        query_lower = query.lower()
        for _memory_id, entry in self._entries.items():
            content_lower = entry.content.lower()
            score = self._calculate_similarity(query_lower, content_lower)
            results.append((score, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:top_k]]

    def _calculate_similarity(self, query: str, content: str) -> float:
        """Calculate simple text similarity score."""
        query_words = set(query.split())
        content_words = set(content.split())

        if not query_words or not content_words:
            return 0.0

        intersection = query_words & content_words
        union = query_words | content_words

        return len(intersection) / len(union) if union else 0.0

    async def search_by_vector(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[tuple[MemoryEntry, float]]:
        """Search by vector similarity."""
        if not self._vectors:
            return []

        query_array = np.array(query_vector, dtype=np.float32)
        if len(query_array.shape) == 1:
            query_array = query_array.reshape(1, -1)

        results: list[tuple[float, MemoryEntry]] = []

        for memory_id, vector in self._vectors.items():
            if vector.shape[1] != query_array.shape[1]:
                continue

            similarity = self._cosine_similarity(query_array, vector)
            entry = self._entries[memory_id]
            results.append((similarity, entry))

        results.sort(key=lambda x: x[0], reverse=True)
        return [(entry, score) for score, entry in results[:top_k]]

    def _cosine_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray,
    ) -> float:
        """Calculate cosine similarity between vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(vec1, vec2.T).flatten()[0] / (norm1 * norm2))

    async def get(self, memory_id: str) -> MemoryEntry | None:
        """Get a specific memory."""
        return self._entries.get(memory_id)

    async def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        if memory_id not in self._entries:
            return False

        del self._entries[memory_id]
        if memory_id in self._vectors:
            del self._vectors[memory_id]
        if memory_id in self._id_to_vector_idx:
            del self._id_to_vector_idx[memory_id]

        self._rebuild_index()
        return True

    async def clear(self) -> None:
        """Clear all memories."""
        self._entries.clear()
        self._vectors.clear()
        self._id_to_vector_idx.clear()
        self._next_idx = 0
        self._index = None

    async def count(self) -> int:
        """Count total memories."""
        return len(self._entries)

    def _rebuild_index(self) -> None:
        """Rebuild FAISS index when vectors change."""
        if not self._vectors:
            self._index = None
            return

        try:
            import faiss

            vectors = list(self._vectors.values())
            if not vectors:
                return

            matrix = np.vstack(vectors)

            if self.index_type == "flat":
                self._index = faiss.IndexFlatL2(matrix.shape[1])
            elif self.index_type == "ip":
                self._index = faiss.IndexFlatIP(matrix.shape[1])
            else:
                self._index = faiss.IndexFlatL2(matrix.shape[1])

            self._index.add(matrix)

        except ImportError:
            pass

    def get_all_entries(self) -> list[MemoryEntry]:
        """Get all memory entries."""
        return list(self._entries.values())

    def get_stats(self) -> dict[str, Any]:
        """Get store statistics."""
        return {
            "total_entries": len(self._entries),
            "total_vectors": len(self._vectors),
            "dimension": self.dimension,
            "index_type": self.index_type,
            "has_index": self._index is not None,
        }
