"""Tests for OpenRouter client."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest


class TestOpenRouterClient:
    """Tests for OpenRouter client."""

    def test_client_creation(self):
        """Test client creation."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        assert client.api_key == "test-key"
        assert client.BASE_URL == "https://openrouter.ai/api/v1"

    def test_client_with_router(self):
        """Test client creation with router."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()
        client = OpenRouterClient(api_key="test-key", router=router)

        assert client.router is router

    def test_get_cost(self):
        """Test get_cost method."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        cost = client.get_cost("openrouter/free", 1000)
        assert cost == 0.0

        cost = client.get_cost("anthropic/claude-3.5-sonnet", 1000)
        assert cost > 0

    def test_get_cost_unknown_model(self):
        """Test get_cost with unknown model."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        cost = client.get_cost("unknown/model", 1000)
        assert cost == 0.0

    def test_get_rate_limit_status(self):
        """Test get_rate_limit_status method."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")
        status = client.get_rate_limit_status()

        assert "router" in status

    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")
        await client.close()

        assert client._client is None

    @pytest.mark.asyncio
    async def test_chat_with_mock(self):
        """Test chat with mocked response."""
        from agento.domain.ports.llm_port import Message
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Hello!"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "model": "openrouter/free",
        }

        client._client = AsyncMock()
        client._client.post = AsyncMock(return_value=mock_response)

        messages = [Message(role="user", content="Hi")]
        response = await client.chat(messages)

        assert response.content == "Hello!"
        assert response.model == "openrouter/free"
        assert response.usage["total_tokens"] == 15

    @pytest.mark.asyncio
    async def test_chat_with_specific_model(self):
        """Test chat with specific model."""
        from agento.domain.ports.llm_port import Message
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Code generated!"}}],
            "usage": {"prompt_tokens": 20, "completion_tokens": 30, "total_tokens": 50},
            "model": "qwen/qwen3-coder-480b-a35b:free",
        }

        client._client = AsyncMock()
        client._client.post = AsyncMock(return_value=mock_response)

        messages = [Message(role="user", content="Write a function")]
        response = await client.chat(messages, model="qwen/qwen3-coder-480b-a35b:free")

        assert response.content == "Code generated!"
        assert response.model == "qwen/qwen3-coder-480b-a35b:free"

    @pytest.mark.asyncio
    async def test_chat_error_handling(self):
        """Test chat error handling."""
        from agento.domain.ports.llm_port import Message
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        client._client = AsyncMock()
        client._client.post = AsyncMock(side_effect=httpx.HTTPError("API Error"))

        messages = [Message(role="user", content="Hi")]

        with pytest.raises(httpx.HTTPError):
            await client.chat(messages)

    def test_context_manager(self):
        """Test async context manager."""
        from agento.infrastructure.llm.openrouter import OpenRouterClient

        client = OpenRouterClient(api_key="test-key")

        assert hasattr(client, "__aenter__")
        assert hasattr(client, "__aexit__")
