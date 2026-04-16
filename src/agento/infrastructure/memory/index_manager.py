"""Index manager for FAISS vector store."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np


class IndexType(Enum):
    """FAISS index types."""

    FLAT_L2 = "flat_l2"
    FLAT_IP = "flat_ip"
    IVF = "ivf"
    HNSW = "hnsw"


@dataclass
class IndexConfig:
    """Index configuration."""

    dimension: int = 384
    index_type: IndexType = IndexType.FLAT_L2
    metric: str = "l2"
    nlist: int = 100
    nprobe: int = 10
    m: int = 16
    ef_construction: int = 40
    ef_search: int = 16


@dataclass
class IndexStats:
    """Index statistics."""

    total_vectors: int = 0
    dimension: int = 0
    index_type: str = ""
    is_trained: bool = False
    memory_size_bytes: int = 0


class IndexManager:
    """Manage FAISS indices."""

    def __init__(
        self,
        config: IndexConfig | None = None,
    ):
        self.config = config or IndexConfig()
        self._index = None
        self._id_map: dict[str, int] = {}
        self._reverse_map: dict[int, str] = {}
        self._vectors: list[np.ndarray] = []
        self._is_dirty = False

    def create_index(self) -> Any:
        """Create a new FAISS index."""
        try:
            import faiss

            dimension = self.config.dimension

            if self.config.index_type == IndexType.FLAT_L2:
                self._index = faiss.IndexFlatL2(dimension)
            elif self.config.index_type == IndexType.FLAT_IP:
                self._index = faiss.IndexFlatIP(dimension)
            elif self.config.index_type == IndexType.IVF:
                quantizer = faiss.IndexFlatL2(dimension)
                self._index = faiss.IndexIVFFlat(
                    quantizer,
                    dimension,
                    self.config.nlist,
                )
            elif self.config.index_type == IndexType.HNSW:
                self._index = faiss.IndexHNSWFlat(
                    dimension,
                    self.config.m,
                )
                self._index.hnsw.efConstruction = self.config.ef_construction
                self._index.hnsw.efSearch = self.config.ef_search
            else:
                self._index = faiss.IndexFlatL2(dimension)

            self._is_dirty = True
            return self._index

        except ImportError:
            return None

    def add_vector(
        self,
        vector_id: str,
        vector: np.ndarray,
    ) -> bool:
        """Add a vector to the index."""
        if self._index is None:
            self.create_index()

        if self._index is None:
            return False

        if vector_id in self._id_map:
            return False

        vector = vector.reshape(1, -1).astype(np.float32)

        try:
            import faiss

            if isinstance(self._index, faiss.IndexIVFFlat):
                if not self._index.is_trained:
                    self._index.train(vector)

            self._index.add(vector)

            idx = len(self._vectors)
            self._id_map[vector_id] = idx
            self._reverse_map[idx] = vector_id
            self._vectors.append(vector)
            self._is_dirty = True

            return True

        except ImportError:
            return False

    def add_vectors_batch(
        self,
        vectors: dict[str, np.ndarray],
    ) -> int:
        """Add multiple vectors in batch."""
        count = 0
        for vector_id, vector in vectors.items():
            if self.add_vector(vector_id, vector):
                count += 1
        return count

    def search(
        self,
        query_vector: np.ndarray,
        k: int = 5,
    ) -> list[tuple[str, float]]:
        """Search for nearest neighbors."""
        if self._index is None or len(self._vectors) == 0:
            return []

        query_vector = query_vector.reshape(1, -1).astype(np.float32)

        try:
            import faiss

            if isinstance(self._index, faiss.IndexIVFFlat):
                self._index.nprobe = self.config.nprobe

            distances, indices = self._index.search(query_vector, k)

            results: list[tuple[str, float]] = []
            for dist, idx in zip(distances[0], indices[0], strict=True):
                if idx >= 0 and idx in self._reverse_map:
                    vector_id = self._reverse_map[int(idx)]
                    results.append((vector_id, float(dist)))

            return results

        except ImportError:
            return []

    def remove_vector(self, vector_id: str) -> bool:
        """Remove a vector from the index."""
        if vector_id not in self._id_map:
            return False

        idx = self._id_map[vector_id]
        del self._id_map[vector_id]
        del self._reverse_map[idx]
        self._vectors[idx] = np.zeros_like(self._vectors[0])
        self._is_dirty = True
        return True

    def get_vector(self, vector_id: str) -> np.ndarray | None:
        """Get a vector by ID."""
        if vector_id not in self._id_map:
            return None
        idx = self._id_map[vector_id]
        return self._vectors[idx]

    def clear(self) -> None:
        """Clear the index."""
        self._index = None
        self._id_map.clear()
        self._reverse_map.clear()
        self._vectors.clear()
        self._is_dirty = False

    def get_stats(self) -> IndexStats:
        """Get index statistics."""
        total_vectors = len(self._vectors)
        memory_size = 0

        if self._vectors:
            memory_size = sum(v.nbytes for v in self._vectors)

        return IndexStats(
            total_vectors=total_vectors,
            dimension=self.config.dimension,
            index_type=self.config.index_type.value,
            is_trained=self._index is not None,
            memory_size_bytes=memory_size,
        )

    def save(self, path: Path | str) -> bool:
        """Save index to disk."""
        if self._index is None:
            return False

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import faiss

            index_path = path.with_suffix(".index")
            faiss.write_index(self._index, str(index_path))

            metadata = {
                "id_map": self._id_map,
                "config": {
                    "dimension": self.config.dimension,
                    "index_type": self.config.index_type.value,
                },
            }

            import json

            meta_path = path.with_suffix(".meta.json")
            with open(meta_path, "w") as f:
                json.dump(metadata, f)

            return True

        except (ImportError, OSError):
            return False

    def load(self, path: Path | str) -> bool:
        """Load index from disk."""
        path = Path(path)

        if not path.exists():
            return False

        try:
            import json

            import faiss

            index_path = path.with_suffix(".index")
            meta_path = path.with_suffix(".meta.json")

            if not index_path.exists() or not meta_path.exists():
                return False

            self._index = faiss.read_index(str(index_path))

            with open(meta_path) as f:
                metadata = json.load(f)

            self._id_map = metadata["id_map"]
            self._reverse_map = {int(k): v for k, v in metadata["id_map"].items()}

            return True

        except (ImportError, OSError, json.JSONDecodeError):
            return False

    @property
    def is_dirty(self) -> bool:
        """Check if index has unsaved changes."""
        return self._is_dirty

    def mark_clean(self) -> None:
        """Mark index as saved."""
        self._is_dirty = False

    def get_index(self) -> Any:
        """Get the underlying FAISS index."""
        return self._index
