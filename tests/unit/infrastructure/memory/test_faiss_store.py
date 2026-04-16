"""Tests for FAISS store."""

import pytest

from agento.infrastructure.memory.faiss_store import FAISSStore


@pytest.fixture
def store():
    """Create a fresh FAISS store."""
    return FAISSStore(dimension=128)


class TestFAISSStore:
    """Test FAISS store functionality."""

    @pytest.mark.asyncio
    async def test_add_memory(self, store):
        """Test adding a memory."""
        memory_id = await store.add("Test content", {"key": "value"})
        assert memory_id is not None
        assert len(memory_id) > 0

    @pytest.mark.asyncio
    async def test_add_with_vector(self, store):
        """Test adding a memory with vector."""
        vector = [0.1] * 128
        memory_id = await store.add_with_vector("Test with vector", vector)
        assert memory_id is not None

        entry = await store.get(memory_id)
        assert entry is not None
        assert entry.content == "Test with vector"
        assert entry.vector == vector

    @pytest.mark.asyncio
    async def test_get_memory(self, store):
        """Test getting a memory."""
        memory_id = await store.add("Test content")
        entry = await store.get(memory_id)

        assert entry is not None
        assert entry.id == memory_id
        assert entry.content == "Test content"

    @pytest.mark.asyncio
    async def test_get_nonexistent_memory(self, store):
        """Test getting a nonexistent memory."""
        entry = await store.get("nonexistent-id")
        assert entry is None

    @pytest.mark.asyncio
    async def test_delete_memory(self, store):
        """Test deleting a memory."""
        memory_id = await store.add("Test content")
        result = await store.delete(memory_id)
        assert result is True

        entry = await store.get(memory_id)
        assert entry is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_memory(self, store):
        """Test deleting a nonexistent memory."""
        result = await store.delete("nonexistent-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_clear(self, store):
        """Test clearing all memories."""
        await store.add("Content 1")
        await store.add("Content 2")
        await store.add("Content 3")

        await store.clear()

        count = await store.count()
        assert count == 0

    @pytest.mark.asyncio
    async def test_count(self, store):
        """Test counting memories."""
        assert await store.count() == 0

        await store.add("Content 1")
        assert await store.count() == 1

        await store.add("Content 2")
        assert await store.count() == 2

    @pytest.mark.asyncio
    async def test_search(self, store):
        """Test searching memories."""
        await store.add_with_vector("Python is a programming language", [1.0] * 128)
        await store.add_with_vector("JavaScript is for web development", [0.5] * 128)
        await store.add_with_vector("Rust is a systems language", [0.3] * 128)

        results = await store.search("python", top_k=2)
        assert len(results) > 0
        assert "Python" in results[0].content or "python" in results[0].content.lower()

    @pytest.mark.asyncio
    async def test_search_with_no_vectors(self, store):
        """Test searching with no vectors."""
        results = await store.search("query", top_k=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_search_top_k(self, store):
        """Test search with top_k parameter."""
        await store.add_with_vector("Content A", [1.0] * 128)
        await store.add_with_vector("Content B", [0.5] * 128)
        await store.add_with_vector("Content C", [0.3] * 128)

        results = await store.search("test", top_k=2)
        assert len(results) <= 2

    @pytest.mark.asyncio
    async def test_get_all_entries(self, store):
        """Test getting all entries."""
        await store.add("Content 1")
        await store.add("Content 2")

        entries = store.get_all_entries()
        assert len(entries) == 2

    @pytest.mark.asyncio
    async def test_get_stats(self, store):
        """Test getting store statistics."""
        await store.add("Content 1")
        await store.add_with_vector("Content 2", [0.1] * 128)

        stats = store.get_stats()
        assert stats["total_entries"] == 2
        assert stats["total_vectors"] == 1
        assert stats["dimension"] == 128

    @pytest.mark.asyncio
    async def test_search_by_vector(self, store):
        """Test searching by vector."""
        await store.add_with_vector("Content A", [1.0] * 128)
        await store.add_with_vector("Content B", [0.1] * 128)

        results = await store.search_by_vector([0.9] * 128, top_k=2)
        assert len(results) <= 2
        assert all(isinstance(r[0].content, str) for r in results)
        assert all(isinstance(r[1], float) for r in results)

    @pytest.mark.asyncio
    async def test_search_by_vector_empty_store(self, store):
        """Test searching by vector with empty store."""
        results = await store.search_by_vector([0.1] * 128, top_k=5)
        assert results == []
