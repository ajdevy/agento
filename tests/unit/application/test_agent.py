"""Tests for Agent."""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestAgent:
    """Tests for Agent class."""

    def test_agent_creation(self):
        """Test agent creation."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key")

        assert agent.api_key == "test-key"
        assert agent.model == "openrouter/free"

    def test_agent_with_model(self):
        """Test agent with custom model."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key", model="custom/model")

        assert agent.model == "custom/model"

    @pytest.mark.asyncio
    async def test_initialize(self):
        """Test agent initialization."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key")
        await agent.initialize()

        assert agent.llm_client is not None

    @pytest.mark.asyncio
    async def test_initialize_no_key(self):
        """Test agent initialization without API key."""
        from agento.application.agent import Agent

        agent = Agent(api_key="")
        agent.api_key = ""

        with pytest.raises(ValueError):
            await agent.initialize()

    @pytest.mark.asyncio
    async def test_chat(self):
        """Test agent chat."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key")

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = "Hello!"
        mock_response.cost = 0.0

        mock_state = MagicMock()
        mock_state.__getitem__ = MagicMock(
            return_value=[MagicMock(role="assistant", content="Hello!")]
        )

        agent.llm_client = mock_client
        agent.graph = MagicMock()
        agent.graph.ainvoke = AsyncMock(return_value=mock_state)

        response = await agent.chat("Hi")

        assert response == "Hello!"

    @pytest.mark.asyncio
    async def test_get_cost_info(self):
        """Test get_cost_info."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key")

        info = agent.get_cost_info()

        assert "model" in info
        assert "total_cost" in info

    @pytest.mark.asyncio
    async def test_close(self):
        """Test agent close."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key")

        mock_client = MagicMock()
        mock_client.close = AsyncMock()
        agent.llm_client = mock_client

        await agent.close()

        mock_client.close.assert_called_once()
        assert agent.llm_client is None

    def test_context_manager(self):
        """Test async context manager."""
        from agento.application.agent import Agent

        agent = Agent(api_key="test-key")

        assert hasattr(agent, "__aenter__")
        assert hasattr(agent, "__aexit__")
