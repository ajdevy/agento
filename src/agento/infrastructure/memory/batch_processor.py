"""Batch processing for embeddings."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from agento.infrastructure.memory.embedder import EmbedderBase, EmbeddingResult


@dataclass
class BatchConfig:
    """Batch processing configuration."""

    batch_size: int = 32
    max_concurrent_batches: int = 4
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class BatchResult:
    """Batch processing result."""

    total_items: int
    successful: int
    failed: int
    results: list[EmbeddingResult]
    errors: list[str]


class BatchProcessor:
    """Process embeddings in batches."""

    def __init__(
        self,
        embedder: EmbedderBase,
        config: BatchConfig | None = None,
    ):
        self.embedder = embedder
        self.config = config or BatchConfig()

    async def process(
        self,
        texts: list[str],
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> BatchResult:
        """Process texts in batches."""
        total = len(texts)
        successful = 0
        failed = 0
        results: list[EmbeddingResult] = []
        errors: list[str] = []

        batches = self._create_batches(texts)

        for i, batch in enumerate(batches):
            batch_results, batch_errors = await self._process_batch(batch)

            results.extend(batch_results)
            errors.extend(batch_errors)
            successful += len(batch_results)
            failed += len(batch_errors)

            if progress_callback:
                await progress_callback(i + 1, len(batches))

        return BatchResult(
            total_items=total,
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
        )

    async def _process_batch(
        self,
        texts: list[str],
    ) -> tuple[list[EmbeddingResult], list[str]]:
        """Process a single batch with retry."""
        for attempt in range(self.config.retry_attempts):
            try:
                results = await self.embedder.embed_batch(texts)
                return results, []
            except Exception as e:
                if attempt < self.config.retry_attempts - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    return [], [f"Batch failed after {attempt + 1} attempts: {e}"]

        return [], ["Batch processing failed"]

    def _create_batches(
        self,
        items: list[str],
    ) -> list[list[str]]:
        """Split items into batches."""
        batches = []
        for i in range(0, len(items), self.config.batch_size):
            batches.append(items[i : i + self.config.batch_size])
        return batches

    async def process_with_semaphore(
        self,
        texts: list[str],
    ) -> BatchResult:
        """Process texts with concurrency limit."""
        semaphore = asyncio.Semaphore(self.config.max_concurrent_batches)

        async def process_batch_with_limit(
            batch: list[str],
        ) -> tuple[list[EmbeddingResult], list[str]]:
            async with semaphore:
                return await self._process_batch(batch)

        batches = self._create_batches(texts)
        tasks = [process_batch_with_limit(batch) for batch in batches]

        batch_results = await asyncio.gather(*tasks)

        all_results: list[EmbeddingResult] = []
        all_errors: list[str] = []
        successful = 0
        failed = 0

        for results, errors in batch_results:
            all_results.extend(results)
            all_errors.extend(errors)
            successful += len(results)
            failed += len(errors)

        return BatchResult(
            total_items=len(texts),
            successful=successful,
            failed=failed,
            results=all_results,
            errors=all_errors,
        )

    def get_stats(self) -> dict[str, Any]:
        """Get processor statistics."""
        return {
            "batch_size": self.config.batch_size,
            "max_concurrent_batches": self.config.max_concurrent_batches,
            "retry_attempts": self.config.retry_attempts,
            "retry_delay": self.config.retry_delay,
        }
