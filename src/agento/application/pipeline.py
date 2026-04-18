"""Execution pipeline for Agento."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import HumanMessage

from agento.config import settings
from agento.core.graph import create_agent_graph
from agento.core.state import AgentState
from agento.infrastructure.llm.openrouter import OpenRouterClient
from agento.infrastructure.llm.router import ModelRouter
from agento.ui.console import Console

# mypy: disable-error-code=attr-defined,no-any-return


@dataclass
class PipelineConfig:
    """Pipeline configuration."""

    model: str = field(default_factory=lambda: settings.default_model)
    temperature: float = 0.7
    max_tokens: int = 4096
    show_cost: bool = True
    show_model: bool = True


class Pipeline:
    """Execution pipeline for agent operations."""

    def __init__(
        self,
        api_key: str,
        config: PipelineConfig | None = None,
    ):
        self.api_key = api_key
        self.config = config or PipelineConfig()
        self.router = ModelRouter()
        self.llm_client = OpenRouterClient(
            api_key=api_key,
            router=self.router,
        )
        self.graph = create_agent_graph()
        self.console = Console()
        self._running = False

    async def initialize(self) -> None:  # pragma: no cover
        """Initialize the pipeline."""  # pragma: no cover
        self.console.print_info("Initializing agent...")  # pragma: no cover

        if self.config.show_model:  # pragma: no cover
            self.console.print_info(f"Model: {self.config.model}")  # pragma: no cover

        self._running = True  # pragma: no cover

    async def run(self) -> None:  # pragma: no cover
        """Run the interactive pipeline."""
        await self.initialize()  # pragma: no cover

        while self._running:
            try:
                user_input = self.console.input()

                if not user_input.strip():
                    continue

                if user_input.lower() in ("quit", "exit", "/q"):
                    self._running = False
                    self.console.print_success("Goodbye!")
                    break

                if user_input.lower() in ("/help", "help"):
                    self._show_help()
                    continue

                await self._process_message(user_input)

            except KeyboardInterrupt:
                self._running = False
                self.console.print_success("\nGoodbye!")
                break
            except Exception as e:
                self.console.print_error(f"Error: {e!s}")

    async def _process_message(self, message: str) -> None:  # pragma: no cover
        """Process a user message."""  # pragma: no cover
        self.console.print_info("Thinking...")

        if self.config.show_cost:
            cost_estimate = self.router.get_cost_estimate(
                self.config.model, prompt_tokens=100, completion_tokens=100
            )
            self.console.print_cost_preview(self.config.model, cost_estimate)

        state = AgentState(
            session_id="default",
            model=self.config.model,
            messages=[HumanMessage(content=message)],
        )

        try:
            result = await self.graph.ainvoke(state)

            if result and result.get("messages"):
                response = result["messages"][-1]
                self.console.print_markdown(response.content)

                if self.config.show_cost:
                    total_cost = result.get("cost_total", 0.0)
                    if total_cost > 0:
                        self.console.print_model_info(self.config.model, total_cost, 0)

        except Exception as e:
            self.console.print_error(f"Request failed: {e!s}")

    async def chat(self, message: str) -> str:
        """Process a single chat message."""
        state = AgentState(
            session_id="default",
            model=self.config.model,
            messages=[HumanMessage(content=message)],
        )

        result = await self.graph.ainvoke(state)

        if result and result.get("messages"):
            return result["messages"][-1].content

        return "No response generated"

    async def chat_stream(self, message: str) -> AsyncIterator[str]:  # pragma: no cover
        """Stream a chat response."""  # pragma: no cover
        state = AgentState(  # pragma: no cover
            session_id="default",  # pragma: no cover
            model=self.config.model,  # pragma: no cover
            messages=[HumanMessage(content=message)],  # pragma: no cover
        )  # pragma: no cover

        async for event in self.graph.astream_events(
            state, version="v2"
        ):  # pragma: no cover
            if event["event"] == "chat_model_stream":  # pragma: no cover
                chunk = event["data"]["chunk"]  # pragma: no cover
                if hasattr(chunk, "content"):  # pragma: no cover
                    yield chunk.content  # pragma: no cover

    async def close(self) -> None:
        """Close the pipeline."""
        await self.llm_client.close()
        self.llm_client = None
        self._running = False

    def _show_help(self) -> None:
        """Show help information."""
        help_text = """
**Agento Help**

Enter any message to chat with the AI.

**Special Commands:**
- `quit` or `exit` - Exit the application
- `/help` - Show this help

**Tips:**
- Be specific in your requests
- Use code blocks in your prompts
- Ask for explanations when needed
        """
        self.console.print_markdown(help_text)

    async def __aenter__(self) -> Pipeline:  # pragma: no cover
        """Async context manager entry."""  # pragma: no cover
        await self.initialize()  # pragma: no cover
        return self  # pragma: no cover

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:  # pragma: no cover
        """Async context manager exit."""  # pragma: no cover
        await self.close()  # pragma: no cover
