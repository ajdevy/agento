"""Cache for embeddings."""

from __future__ import annotations

import hashlib
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from agento.infrastructure.memory.embedder import EmbeddingResult


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: EmbeddingResult
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    hit_count: int = 0


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int = 0
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    hit_rate: float = 0.0


class EmbeddingCache:
    """LRU cache for embeddings."""

    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: int | None = None,
        enable_stats: bool = True,
    ):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enable_stats = enable_stats
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()

    def get(self, text: str) -> EmbeddingResult | None:
        """Get embedding from cache."""
        key = self._hash_key(text)

        if key not in self._cache:
            self._stats.misses += 1
            self._update_hit_rate()
            return None

        entry = self._cache[key]

        if self._is_expired(entry):
            del self._cache[key]
            self._stats.misses += 1
            self._stats.evictions += 1
            self._update_hit_rate()
            return None

        entry.last_accessed = datetime.now()
        entry.access_count += 1
        entry.hit_count += 1
        self._cache.move_to_end(key)

        self._stats.hits += 1
        self._update_hit_rate()
        return entry.value

    def put(
        self,
        text: str,
        embedding: EmbeddingResult,
    ) -> None:
        """Put embedding in cache."""
        key = self._hash_key(text)

        if key in self._cache:
            entry = self._cache[key]
            entry.value = embedding
            entry.last_accessed = datetime.now()
            self._cache.move_to_end(key)
            return

        if len(self._cache) >= self.max_size:
            self._evict_lru()

        entry = CacheEntry(
            key=key,
            value=embedding,
        )
        self._cache[key] = entry
        self._stats.total_entries = len(self._cache)

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._cache:
            self._cache.popitem(last=False)
            self._stats.evictions += 1
            self._stats.total_entries = len(self._cache)

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False

        age = datetime.now() - entry.created_at
        return age > timedelta(seconds=self.ttl_seconds)

    def _hash_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.sha256(text.encode()).hexdigest()

    def _update_hit_rate(self) -> None:
        """Update cache hit rate."""
        total = self._stats.hits + self._stats.misses
        if total > 0:
            self._stats.hit_rate = self._stats.hits / total

    def invalidate(self, text: str) -> bool:
        """Invalidate a specific entry."""
        key = self._hash_key(text)
        if key in self._cache:
            del self._cache[key]
            self._stats.total_entries = len(self._cache)
            return True
        return False

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._stats = CacheStats()

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        stats = CacheStats(
            total_entries=len(self._cache),
            hits=self._stats.hits,
            misses=self._stats.misses,
            evictions=self._stats.evictions,
            hit_rate=self._stats.hit_rate,
        )
        return stats

    def get_all_entries(self) -> list[CacheEntry]:
        """Get all cache entries."""
        return list(self._cache.values())

    def get_hot_entries(self, limit: int = 10) -> list[CacheEntry]:
        """Get most accessed entries."""
        sorted_entries = sorted(
            self._cache.values(),
            key=lambda x: x.hit_count,
            reverse=True,
        )
        return sorted_entries[:limit]

    def cleanup_expired(self) -> int:
        """Remove expired entries."""
        expired_keys = []
        for key, entry in self._cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)

        for key in expired_keys:
            del self._cache[key]

        self._stats.total_entries = len(self._cache)
        self._stats.evictions += len(expired_keys)
        return len(expired_keys)

    def resize(self, new_max_size: int) -> int:
        """Resize the cache, evicting entries if needed."""
        self.max_size = new_max_size
        evicted = 0

        while len(self._cache) > self.max_size:
            self._evict_lru()
            evicted += 1

        return evicted

    def __len__(self) -> int:
        """Get cache size."""
        return len(self._cache)

    def __contains__(self, text: str) -> bool:
        """Check if text is in cache."""
        key = self._hash_key(text)
        if key not in self._cache:
            return False

        if self._is_expired(self._cache[key]):
            del self._cache[key]
            return False

        return True
