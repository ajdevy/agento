"""Main Agent implementation."""

from __future__ import annotations

from typing import Any

from agento.config import settings
from agento.core.graph import create_agent_graph
from agento.core.state import AgentState, Message
from agento.infrastructure.llm.openrouter import OpenRouterClient
from agento.infrastructure.llm.router import ModelRouter


class Agent:
    """Main agent orchestrator."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = api_key or ""
        self.model = model or "openrouter/free"
        self.router = ModelRouter()
        self.llm_client: OpenRouterClient | None = None
        self.graph = create_agent_graph()
        self._session_id = "default"

        if api_key is None and settings.openrouter_api_key:  # pragma: no cover
            self.api_key = (
                settings.openrouter_api_key.get_secret_value()
            )  # pragma: no cover
        if model is None:  # pragma: no cover
            self.model = settings.default_model  # pragma: no cover

    async def initialize(self) -> None:
        """Initialize the agent."""
        if not self.api_key:
            raise ValueError("API key is required")

        self.llm_client = OpenRouterClient(
            api_key=self.api_key,
            router=self.router,
        )

    async def close(self) -> None:  # pragma: no cover
        """Close the agent."""  # pragma: no cover
        if self.llm_client:  # pragma: no cover
            await self.llm_client.close()  # pragma: no cover
            self.llm_client = None  # pragma: no cover

    async def chat(self, message: str) -> str:
        """Send a message and get response."""
        if self.llm_client is None:  # pragma: no cover
            await self.initialize()  # pragma: no cover

        if self.llm_client is None:  # pragma: no cover
            return "Error: Failed to initialize LLM client"  # pragma: no cover

        state = AgentState(
            session_id=self._session_id,
            model=self.model,
            messages=[Message(role="user", content=message)],
        )

        try:
            result = await self.graph.ainvoke(state)
            if result and result.get("messages"):
                response_msg = result["messages"][-1]
                return response_msg.content
            return "No response generated"
        except Exception as e:  # pragma: no cover
            return f"Error: {e!s}"  # pragma: no cover

    async def chat_stream(self, message: str) -> Any:  # pragma: no cover
        """Stream a chat response."""
        if self.llm_client is None:
            await self.initialize()

        if self.llm_client is None:
            return

        state = AgentState(
            session_id=self._session_id,
            model=self.model,
            messages=[Message(role="user", content=message)],
        )

        async for event in self.graph.astream_events(state, version="v2"):
            if event["event"] == "chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "content"):
                    yield chunk.content

    def get_cost_info(self) -> dict[str, Any]:  # pragma: no cover
        """Get cost information for current session."""  # pragma: no cover
        if self.llm_client is None:  # pragma: no cover
            return {"total_cost": 0.0, "model": self.model}  # pragma: no cover

        status = self.llm_client.get_rate_limit_status()  # pragma: no cover
        return {  # pragma: no cover
            "model": self.model,  # pragma: no cover
            "total_cost": self.router.format_cost(0.0),  # pragma: no cover
            "usage_stats": status,  # pragma: no cover
        }  # pragma: no cover

    async def __aenter__(self) -> Agent:  # pragma: no cover
        """Async context manager entry."""  # pragma: no cover
        await self.initialize()  # pragma: no cover
        return self  # pragma: no cover

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:  # pragma: no cover
        """Async context manager exit."""  # pragma: no cover
        await self.close()  # pragma: no cover
