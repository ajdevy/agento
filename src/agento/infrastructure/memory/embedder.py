"""Embedding generation for memory."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass
class EmbeddingResult:
    """Embedding result."""

    embedding: list[float]
    model: str
    dimension: int
    token_count: int | None = None


class EmbedderBase(ABC):
    """Base class for embedding generators."""

    @abstractmethod
    async def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding for text."""
        ...  # pragma: no cover

    @abstractmethod
    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get embedding dimension."""
        ...  # pragma: no cover

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Get model name."""
        ...  # pragma: no cover


class SimpleEmbedder(EmbedderBase):
    """Simple hash-based embedder for testing."""

    def __init__(
        self,
        dimension: int = 384,
        model: str = "simple-hash",
    ):
        self._dimension = dimension
        self._model = model

    async def embed(self, text: str) -> EmbeddingResult:
        """Generate simple embedding using hash."""
        vector = self._text_to_vector(text)
        return EmbeddingResult(
            embedding=vector,
            model=self._model,
            dimension=self._dimension,
            token_count=len(text.split()),
        )

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        return [await self.embed(text) for text in texts]

    def _text_to_vector(self, text: str) -> list[float]:
        """Convert text to fixed-dimension vector."""
        words = text.lower().split()
        vector = np.zeros(self._dimension, dtype=np.float32)

        for i, word in enumerate(words[: self._dimension]):
            hash_val = hash(word) % 10000
            vector[i] = hash_val / 10000.0

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm

        return vector.tolist()

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model


class SentenceTransformersEmbedder(EmbedderBase):
    """Sentence transformers embedder."""

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        normalize: bool = True,
    ):
        self._model_name = model_name
        self.device = device
        self.normalize = normalize
        self._dimension = 384
        self._model = None

    def _load_model(self) -> Any:
        """Lazy load the model."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(
                    self._model_name,
                    device=self.device,
                )
                dim = self._model.get_sentence_embedding_dimension()
                if dim is not None:
                    self._dimension = dim

            except ImportError:
                return None

        return self._model

    async def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding using sentence-transformers."""
        model = self._load_model()

        if model is None:
            simple = SimpleEmbedder(dimension=self._dimension)
            return await simple.embed(text)

        embedding = model.encode(
            text,
            normalize_embeddings=self.normalize,
            convert_to_numpy=True,
        )

        return EmbeddingResult(
            embedding=embedding.tolist(),
            model=self._model_name,
            dimension=self._dimension,
            token_count=len(text.split()),
        )

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        model = self._load_model()

        if model is None:
            simple = SimpleEmbedder(dimension=self._dimension)
            return await simple.embed_batch(texts)

        embeddings = model.encode(
            texts,
            normalize_embeddings=self.normalize,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return [
            EmbeddingResult(
                embedding=emb.tolist(),
                model=self._model_name,
                dimension=self._dimension,
                token_count=len(text.split()),
            )
            for emb, text in zip(embeddings, texts, strict=True)
        ]

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self._model_name


class OpenAIEmbedder(EmbedderBase):
    """OpenAI embedding embedder."""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int | None = None,
    ):
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions
        self._client = None

        self._dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        self._dimension = self._dimension_map.get(model, 1536)

    def _get_client(self) -> Any:
        """Get OpenAI client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                return None
        return self._client

    async def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding using OpenAI."""
        client = self._get_client()

        if client is None:
            simple = SimpleEmbedder(dimension=self._dimension)
            return await simple.embed(text)

        try:
            response = await client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions,
            )

            embedding = response.data[0].embedding

            return EmbeddingResult(
                embedding=embedding,
                model=self.model,
                dimension=len(embedding),
                token_count=(
                    response.usage.prompt_tokens if hasattr(response, "usage") else None
                ),
            )

        except Exception:
            simple = SimpleEmbedder(dimension=self._dimension)
            return await simple.embed(text)

    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts."""
        client = self._get_client()

        if client is None:
            simple = SimpleEmbedder(dimension=self._dimension)
            return await simple.embed_batch(texts)

        try:
            response = await client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions,
            )

            return [
                EmbeddingResult(
                    embedding=data.embedding,
                    model=self.model,
                    dimension=len(data.embedding),
                    token_count=(
                        response.usage.prompt_tokens
                        if hasattr(response, "usage")
                        else None
                    ),
                )
                for data in response.data
            ]

        except Exception:
            simple = SimpleEmbedder(dimension=self._dimension)
            return await simple.embed_batch(texts)

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

    @property
    def model_name(self) -> str:
        """Get model name."""
        return self.model


def create_embedder(
    embedder_type: str = "simple",
    **kwargs: Any,
) -> EmbedderBase:
    """Factory function to create embedder."""
    if embedder_type == "simple":
        return SimpleEmbedder(**kwargs)
    elif embedder_type == "sentence-transformers":
        return SentenceTransformersEmbedder(**kwargs)
    elif embedder_type == "openai":
        return OpenAIEmbedder(**kwargs)
    else:
        return SimpleEmbedder(**kwargs)
