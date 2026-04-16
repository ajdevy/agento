"""Tests for memory service."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from agento.domain.entities.memory import Memory, MemoryType
from agento.domain.ports.memory_port import MemoryEntry, MemoryPort
from agento.domain.services.memory_service import MemorySearchResult, MemoryService


@pytest.fixture
def mock_port():
    """Create a mock memory port."""
    port = MagicMock(spec=MemoryPort)
    port.add = AsyncMock(return_value="test-id")
    port.search = AsyncMock(return_value=[])
    port.get = AsyncMock(return_value=None)
    port.delete = AsyncMock(return_value=True)
    port.clear = AsyncMock(return_value=None)
    port.count = AsyncMock(return_value=0)
    return port


@pytest.fixture
def service(mock_port):
    """Create a memory service with mock port."""
    return MemoryService(mock_port)


class TestMemoryService:
    """Test memory service functionality."""

    @pytest.mark.asyncio
    async def test_store_memory(self, service, mock_port):
        """Test storing a memory."""
        memory_id = await service.store_memory("Test content")

        assert memory_id == "test-id"
        mock_port.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_store_memory_with_type(self, service, mock_port):
        """Test storing a memory with type."""
        await service.store_memory(
            "Code snippet",
            memory_type=MemoryType.CODE_SNIPPET,
        )

        call_args = mock_port.add.call_args
        metadata = (
            call_args[0][1] if len(call_args[0]) > 1 else call_args[1]["metadata"]
        )
        assert metadata["memory_type"] == "code_snippet"

    @pytest.mark.asyncio
    async def test_search_memories(self, service, mock_port):
        """Test searching memories."""
        mock_port.search = AsyncMock(
            return_value=[
                MemoryEntry(
                    id="1",
                    content="Python code",
                    metadata={"memory_type": "code_snippet"},
                ),
                MemoryEntry(
                    id="2",
                    content="Python JavaScript code",
                    metadata={"memory_type": "code_snippet"},
                ),
            ]
        )

        results = await service.search_memories("python", top_k=5)

        assert len(results) == 2
        assert any(r.memory.content == "Python code" for r in results)
        assert any(r.memory.content == "Python JavaScript code" for r in results)

    @pytest.mark.asyncio
    async def test_search_memories_with_type_filter(self, service, mock_port):
        """Test searching with type filter."""
        mock_port.search = AsyncMock(
            return_value=[
                MemoryEntry(
                    id="1",
                    content="Python code",
                    metadata={"memory_type": "code_snippet"},
                ),
                MemoryEntry(
                    id="2",
                    content="General chat",
                    metadata={"memory_type": "conversation"},
                ),
            ]
        )

        results = await service.search_memories(
            "python",
            memory_type=MemoryType.CODE_SNIPPET,
        )

        assert len(results) == 1
        assert results[0].memory.memory_type == MemoryType.CODE_SNIPPET

    @pytest.mark.asyncio
    async def test_get_memory(self, service, mock_port):
        """Test getting a specific memory."""
        mock_port.get = AsyncMock(
            return_value=MemoryEntry(
                id="test-id",
                content="Test content",
                metadata={"memory_type": "conversation"},
            )
        )

        memory = await service.get_memory("test-id")

        assert memory is not None
        assert memory.id == "test-id"

    @pytest.mark.asyncio
    async def test_get_memory_not_found(self, service, mock_port):
        """Test getting nonexistent memory."""
        mock_port.get = AsyncMock(return_value=None)

        memory = await service.get_memory("nonexistent")

        assert memory is None

    @pytest.mark.asyncio
    async def test_delete_memory(self, service, mock_port):
        """Test deleting a memory."""
        result = await service.delete_memory("test-id")

        assert result is True
        mock_port.delete.assert_called_once_with("test-id")

    @pytest.mark.asyncio
    async def test_get_memories_by_type(self, service, mock_port):
        """Test getting memories by type."""
        mock_port.search = AsyncMock(
            return_value=[
                MemoryEntry(
                    id="1",
                    content="Code 1",
                    metadata={"memory_type": "code_snippet"},
                ),
                MemoryEntry(
                    id="2",
                    content="Code 2",
                    metadata={"memory_type": "code_snippet"},
                ),
            ]
        )

        memories = await service.get_memories_by_type(MemoryType.CODE_SNIPPET)

        assert len(memories) == 2
        assert all(m.memory_type == MemoryType.CODE_SNIPPET for m in memories)

    @pytest.mark.asyncio
    async def test_get_recent_memories(self, service, mock_port):
        """Test getting recent memories."""
        mock_port.search = AsyncMock(
            return_value=[
                MemoryEntry(id="1", content="Recent 1"),
                MemoryEntry(id="2", content="Recent 2"),
            ]
        )

        memories = await service.get_recent_memories(limit=10)

        assert len(memories) == 2

    @pytest.mark.asyncio
    async def test_get_stats(self, service, mock_port):
        """Test getting memory statistics."""
        mock_port.count = AsyncMock(return_value=2)
        mock_port.search = AsyncMock(
            return_value=[
                MemoryEntry(
                    id="1",
                    content="Test",
                    metadata={"memory_type": "conversation", "access_count": 3},
                ),
                MemoryEntry(
                    id="2",
                    content="Test",
                    metadata={"memory_type": "code_snippet", "access_count": 1},
                ),
            ]
        )

        stats = await service.get_stats()

        assert stats.total_memories == 2
        assert stats.average_access_count == 2.0
        assert stats.most_accessed_type == "conversation"

    @pytest.mark.asyncio
    async def test_clear_memories(self, service, mock_port):
        """Test clearing all memories."""
        await service.clear_memories()

        mock_port.clear.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_memories_by_type(self, service, mock_port):
        """Test clearing memories by type."""
        mock_port.search = AsyncMock(
            return_value=[
                MemoryEntry(
                    id="1", content="Test", metadata={"memory_type": "conversation"}
                ),
                MemoryEntry(
                    id="2", content="Test", metadata={"memory_type": "conversation"}
                ),
            ]
        )
        mock_port.delete = AsyncMock(return_value=True)

        count = await service.clear_memories(MemoryType.CONVERSATION)

        assert count == 2


class TestMemorySearchResult:
    """Test memory search result."""

    def test_create_result(self):
        """Test creating a search result."""
        memory = Memory(
            id="test-id",
            content="Test content",
        )
        result = MemorySearchResult(
            memory=memory,
            score=0.95,
        )

        assert result.memory.id == "test-id"
        assert result.score == 0.95
        assert result.distance is None

    def test_create_result_with_distance(self):
        """Test creating a result with distance."""
        memory = Memory(id="test-id", content="Test")
        result = MemorySearchResult(
            memory=memory,
            score=0.8,
            distance=0.2,
        )

        assert result.distance == 0.2
