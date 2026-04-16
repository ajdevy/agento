"""Tests for Pipeline."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestPipelineConfig:
    """Tests for PipelineConfig."""

    def test_config_defaults(self):
        """Test config defaults."""
        from agento.application.pipeline import PipelineConfig

        config = PipelineConfig()

        assert config.model == "openrouter/free"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096
        assert config.show_cost is True
        assert config.show_model is True

    def test_config_custom(self):
        """Test config with custom values."""
        from agento.application.pipeline import PipelineConfig

        config = PipelineConfig(
            model="custom/model",
            temperature=0.5,
            show_cost=False,
        )

        assert config.model == "custom/model"
        assert config.temperature == 0.5
        assert config.show_cost is False


class TestPipeline:
    """Tests for Pipeline class."""

    def test_pipeline_creation(self):
        """Test pipeline creation."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        assert pipeline.api_key == "test-key"
        assert pipeline.router is not None
        assert pipeline.llm_client is not None

    def test_pipeline_with_config(self):
        """Test pipeline with config."""
        from agento.application.pipeline import Pipeline, PipelineConfig

        config = PipelineConfig(model="custom/model")
        pipeline = Pipeline(api_key="test-key", config=config)

        assert pipeline.config.model == "custom/model"

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test pipeline initialization."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        with patch.object(pipeline.console, "print_info") as mock_print:
            await pipeline.initialize()
            mock_print.assert_called()

        assert pipeline._running is True

    @pytest.mark.asyncio
    async def test_chat(self):
        """Test pipeline chat."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        mock_state = MagicMock()
        mock_state.__getitem__ = MagicMock(
            return_value=[MagicMock(role="assistant", content="Hello!")]
        )
        pipeline.graph = MagicMock()
        pipeline.graph.ainvoke = AsyncMock(return_value=mock_state)

        response = await pipeline.chat("Hi")

        assert response == "Hello!"

    @pytest.mark.asyncio
    async def test_chat_no_response(self):
        """Test pipeline chat with no response."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        pipeline.graph = MagicMock()
        pipeline.graph.ainvoke = AsyncMock(return_value=None)

        response = await pipeline.chat("Hi")

        assert response == "No response generated"

    @pytest.mark.asyncio
    async def test_close(self):
        """Test pipeline close."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        mock_client = MagicMock()
        mock_client.close = AsyncMock()
        pipeline.llm_client = mock_client
        pipeline._running = True

        await pipeline.close()

        mock_client.close.assert_called_once()
        assert pipeline.llm_client is None
        assert pipeline._running is False

    def test_show_help(self):
        """Test show help."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        with patch.object(pipeline.console, "print_markdown") as mock_print:
            pipeline._show_help()
            mock_print.assert_called_once()

    def test_context_manager(self):
        """Test async context manager."""
        from agento.application.pipeline import Pipeline

        pipeline = Pipeline(api_key="test-key")

        assert hasattr(pipeline, "__aenter__")
        assert hasattr(pipeline, "__aexit__")
