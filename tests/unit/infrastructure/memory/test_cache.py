"""Tests for embedding cache."""

import time

import pytest

from agento.infrastructure.memory.cache import CacheStats, EmbeddingCache
from agento.infrastructure.memory.embedder import EmbeddingResult


@pytest.fixture
def cache():
    """Create a fresh cache."""
    return EmbeddingCache(max_size=10)


@pytest.fixture
def sample_embedding():
    """Create a sample embedding."""
    return EmbeddingResult(
        embedding=[0.1] * 384,
        model="test",
        dimension=384,
    )


class TestEmbeddingCache:
    """Test cache functionality."""

    def test_put_and_get(self, cache, sample_embedding):
        """Test putting and getting from cache."""
        cache.put("test text", sample_embedding)
        result = cache.get("test text")

        assert result is not None
        assert result.model == "test"

    def test_get_miss(self, cache):
        """Test cache miss."""
        result = cache.get("nonexistent")
        assert result is None

    def test_invalidate(self, cache, sample_embedding):
        """Test invalidating a cache entry."""
        cache.put("test text", sample_embedding)
        result = cache.invalidate("test text")

        assert result is True
        assert cache.get("test text") is None

    def test_invalidate_nonexistent(self, cache):
        """Test invalidating nonexistent entry."""
        result = cache.invalidate("nonexistent")
        assert result is False

    def test_clear(self, cache, sample_embedding):
        """Test clearing cache."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)

        cache.clear()

        assert cache.get("text1") is None
        assert cache.get("text2") is None

    def test_get_stats(self, cache, sample_embedding):
        """Test getting cache statistics."""
        cache.put("text1", sample_embedding)
        cache.get("text1")
        cache.get("text1")
        cache.get("nonexistent")

        stats = cache.get_stats()
        assert stats.total_entries == 1
        assert stats.hits == 2
        assert stats.misses == 1

    def test_hit_rate_calculation(self, cache, sample_embedding):
        """Test hit rate calculation."""
        cache.put("text", sample_embedding)

        cache.get("text")
        cache.get("text")
        cache.get("nonexistent")

        stats = cache.get_stats()
        assert stats.hit_rate == pytest.approx(2 / 3)

    def test_lru_eviction(self, sample_embedding):
        """Test LRU eviction."""
        cache = EmbeddingCache(max_size=3)

        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)
        cache.put("text3", sample_embedding)

        cache.get("text1")
        cache.put("text4", sample_embedding)

        assert cache.get("text1") is not None
        assert cache.get("text2") is None

    def test_len(self, cache, sample_embedding):
        """Test len operation."""
        assert len(cache) == 0

        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)

        assert len(cache) == 2

    def test_contains(self, cache, sample_embedding):
        """Test contains operation."""
        cache.put("text", sample_embedding)

        assert "text" in cache
        assert "nonexistent" not in cache

    def test_get_hot_entries(self, cache, sample_embedding):
        """Test getting hot entries."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)
        cache.put("text3", sample_embedding)

        cache.get("text1")
        cache.get("text1")
        cache.get("text2")

        hot = cache.get_hot_entries(2)
        assert len(hot) <= 2
        assert hot[0].hit_count >= hot[1].hit_count

    def test_cleanup_expired(self, sample_embedding):
        """Test cleaning up expired entries."""
        cache = EmbeddingCache(max_size=10, ttl_seconds=1)

        cache.put("text", sample_embedding)
        time.sleep(1.1)

        expired = cache.cleanup_expired()
        assert expired >= 1

    def test_resize(self, cache, sample_embedding):
        """Test resizing cache."""
        cache.put("text1", sample_embedding)
        cache.put("text2", sample_embedding)
        cache.put("text3", sample_embedding)

        evicted = cache.resize(2)
        assert evicted >= 1
        assert len(cache) <= 2


class TestCacheStats:
    """Test cache statistics."""

    def test_default_stats(self):
        """Test default stats values."""
        stats = CacheStats()
        assert stats.total_entries == 0
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.hit_rate == 0.0
