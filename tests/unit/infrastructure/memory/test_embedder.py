"""Tests for embedder."""

import pytest

from agento.infrastructure.memory.embedder import (
    SimpleEmbedder,
    create_embedder,
)


@pytest.fixture
def embedder():
    """Create a simple embedder."""
    return SimpleEmbedder(dimension=128)


class TestSimpleEmbedder:
    """Test simple embedder functionality."""

    @pytest.mark.asyncio
    async def test_embed(self, embedder):
        """Test embedding a single text."""
        result = await embedder.embed("Hello world")

        assert result is not None
        assert len(result.embedding) == 128
        assert result.model == "simple-hash"
        assert result.dimension == 128
        assert result.token_count == 2

    @pytest.mark.asyncio
    async def test_embed_batch(self, embedder):
        """Test embedding multiple texts."""
        texts = ["Hello", "World", "Test"]
        results = await embedder.embed_batch(texts)

        assert len(results) == 3
        for result in results:
            assert len(result.embedding) == 128

    @pytest.mark.asyncio
    async def test_embed_empty_text(self, embedder):
        """Test embedding empty text."""
        result = await embedder.embed("")

        assert result is not None
        assert len(result.embedding) == 128
        assert result.token_count == 0

    @pytest.mark.asyncio
    async def test_embed_long_text(self, embedder):
        """Test embedding long text."""
        text = " ".join(["word"] * 1000)
        result = await embedder.embed(text)

        assert result is not None
        assert len(result.embedding) == 128

    @pytest.mark.asyncio
    async def test_dimension_property(self, embedder):
        """Test dimension property."""
        assert embedder.dimension == 128

    @pytest.mark.asyncio
    async def test_model_name_property(self, embedder):
        """Test model name property."""
        assert embedder.model_name == "simple-hash"

    @pytest.mark.asyncio
    async def test_embed_consistency(self, embedder):
        """Test that same text produces same embedding."""
        text = "Test consistent embedding"
        result1 = await embedder.embed(text)
        result2 = await embedder.embed(text)

        assert result1.embedding == result2.embedding

    @pytest.mark.asyncio
    async def test_embed_different_texts(self, embedder):
        """Test that different texts produce different embeddings."""
        result1 = await embedder.embed("Hello world")
        result2 = await embedder.embed("World hello")

        assert result1.embedding != result2.embedding


class TestCreateEmbedder:
    """Test embedder factory function."""

    def test_create_simple_embedder(self):
        """Test creating simple embedder."""
        embedder = create_embedder("simple", dimension=64)
        assert embedder.dimension == 64

    def test_create_with_defaults(self):
        """Test creating embedder with defaults."""
        embedder = create_embedder("simple")
        assert embedder.dimension == 384

    def test_create_unknown_type_returns_simple(self):
        """Test that unknown type returns simple embedder."""
        embedder = create_embedder("unknown-type")
        assert isinstance(embedder, SimpleEmbedder)


class TestEmbedderWithDifferentDimensions:
    """Test embedder with different dimensions."""

    @pytest.mark.asyncio
    async def test_small_dimension(self):
        """Test with small dimension."""
        embedder = SimpleEmbedder(dimension=64)
        result = await embedder.embed("Test")
        assert len(result.embedding) == 64

    @pytest.mark.asyncio
    async def test_large_dimension(self):
        """Test with large dimension."""
        embedder = SimpleEmbedder(dimension=512)
        result = await embedder.embed("Test")
        assert len(result.embedding) == 512

    @pytest.mark.asyncio
    async def test_dimension_matches(self):
        """Test that dimension matches."""
        for dim in [64, 128, 256, 512]:
            embedder = SimpleEmbedder(dimension=dim)
            assert embedder.dimension == dim
            result = await embedder.embed("Test")
            assert len(result.embedding) == dim
