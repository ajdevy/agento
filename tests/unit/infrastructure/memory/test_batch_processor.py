"""Tests for batch processor."""

import pytest

from agento.infrastructure.memory.batch_processor import BatchConfig, BatchProcessor
from agento.infrastructure.memory.embedder import SimpleEmbedder


@pytest.fixture
def embedder():
    """Create a simple embedder."""
    return SimpleEmbedder(dimension=64)


@pytest.fixture
def batch_processor(embedder):
    """Create a batch processor."""
    return BatchProcessor(embedder, BatchConfig(batch_size=5))


class TestBatchProcessor:
    """Test batch processor functionality."""

    @pytest.mark.asyncio
    async def test_process_single_batch(self, batch_processor):
        """Test processing a single batch."""
        texts = ["Hello", "World"]
        result = await batch_processor.process(texts)

        assert result.total_items == 2
        assert result.successful == 2
        assert result.failed == 0
        assert len(result.results) == 2

    @pytest.mark.asyncio
    async def test_process_multiple_batches(self, batch_processor):
        """Test processing multiple batches."""
        texts = [f"Text {i}" for i in range(20)]
        result = await batch_processor.process(texts)

        assert result.total_items == 20
        assert result.successful == 20
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_process_empty_list(self, batch_processor):
        """Test processing empty list."""
        result = await batch_processor.process([])

        assert result.total_items == 0
        assert result.successful == 0
        assert result.failed == 0

    @pytest.mark.asyncio
    async def test_process_with_progress_callback(self, batch_processor):
        """Test processing with progress callback."""
        progress = []

        async def callback(current: int, total: int) -> None:
            progress.append((current, total))

        texts = ["Text 1", "Text 2", "Text 3", "Text 4", "Text 5", "Text 6"]
        await batch_processor.process(texts, progress_callback=callback)

        assert len(progress) > 0

    @pytest.mark.asyncio
    async def test_create_batches(self, batch_processor):
        """Test batch creation."""
        texts = list(range(15))
        batches = batch_processor._create_batches(texts)

        assert len(batches) == 3
        assert len(batches[0]) == 5
        assert len(batches[1]) == 5
        assert len(batches[2]) == 5

    @pytest.mark.asyncio
    async def test_create_batches_small_list(self, batch_processor):
        """Test batch creation with small list."""
        texts = [1, 2, 3]
        batches = batch_processor._create_batches(texts)

        assert len(batches) == 1
        assert batches[0] == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_process_with_semaphore(self, batch_processor):
        """Test processing with semaphore."""
        texts = ["Text 1", "Text 2", "Text 3"]
        result = await batch_processor.process_with_semaphore(texts)

        assert result.total_items == 3
        assert result.successful == 3

    @pytest.mark.asyncio
    async def test_get_stats(self, batch_processor):
        """Test getting processor stats."""
        stats = batch_processor.get_stats()

        assert stats["batch_size"] == 5
        assert stats["max_concurrent_batches"] == 4


class TestBatchConfig:
    """Test batch configuration."""

    def test_default_config(self):
        """Test default configuration."""
        config = BatchConfig()

        assert config.batch_size == 32
        assert config.max_concurrent_batches == 4
        assert config.retry_attempts == 3
        assert config.retry_delay == 1.0

    def test_custom_config(self):
        """Test custom configuration."""
        config = BatchConfig(
            batch_size=10,
            max_concurrent_batches=8,
            retry_attempts=5,
        )

        assert config.batch_size == 10
        assert config.max_concurrent_batches == 8
        assert config.retry_attempts == 5
