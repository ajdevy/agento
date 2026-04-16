"""OpenRouter LLM client implementation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import httpx

from agento.domain.ports.llm_port import LLMPort, Message, ModelResponse
from agento.infrastructure.llm.base import MODEL_COSTS, get_model_cost
from agento.infrastructure.llm.router import ModelRouter


# mypy: disable-error-code=override


class OpenRouterClient(LLMPort):
    """OpenRouter API client."""

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self, api_key: str, router: ModelRouter | None = None):
        self.api_key = api_key
        self.router = router or ModelRouter()
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:  # pragma: no cover
        """Get or create HTTP client."""  # pragma: no cover
        if self._client is None:  # pragma: no cover
            self._client = httpx.AsyncClient(  # pragma: no cover
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/ajdevy/agento",
                    "X-Title": "Agento AI Agent",
                },
                timeout=httpx.Timeout(120.0),
            )
        return self._client

    async def close(self) -> None:  # pragma: no cover
        """Close the HTTP client."""  # pragma: no cover
        if self._client is not None:  # pragma: no cover
            await self._client.aclose()  # pragma: no cover
            self._client = None  # pragma: no cover

    async def chat(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> ModelResponse:
        """Send chat request to OpenRouter."""
        client = self._get_client()

        if model is None:
            model, _ = self.router.select_model_with_fallback()
        else:
            self.router.record_usage(model, tokens=0)

        request_data: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            **kwargs,
        }

        response = await client.post("/chat/completions", json=request_data)
        response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]
        content = choice["message"]["content"]
        usage = data.get("usage", {})
        model_used = data.get("model", model)

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        cost = get_model_cost(model_used, prompt_tokens, completion_tokens)
        self.router.record_usage(model_used, tokens=total_tokens)

        return ModelResponse(
            content=content,
            model=model_used,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
            },
            cost=cost,
        )

    async def stream(  # pragma: no cover
        self,
        messages: list[Message],
        model: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:  # pragma: no cover
        """Stream chat response from OpenRouter."""  # pragma: no cover
        client = self._get_client()

        if model is None:
            model, _ = self.router.select_model_with_fallback()

        request_data: dict[str, Any] = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            **kwargs,
        }

        async with client.stream(
            "POST", "/chat/completions", json=request_data
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    import json

                    chunk = json.loads(data)
                    if "choices" in chunk and len(chunk["choices"]) > 0:
                        delta = chunk["choices"][0].get("delta", {})
                        if "content" in delta:
                            yield delta["content"]

    def get_cost(self, model: str, tokens: int) -> float:
        """Get cost for model and token count."""
        cost_info = MODEL_COSTS.get(model)
        if not cost_info:
            return 0.0
        return (tokens / 1_000_000) * (
            cost_info.input_cost_per_million + cost_info.output_cost_per_million
        )

    def get_rate_limit_status(self) -> dict[str, Any]:
        """Get current rate limit status."""
        return {"router": self.router.get_rate_limit_status("openrouter/free")}

    async def __aenter__(self) -> OpenRouterClient:  # pragma: no cover
        """Async context manager entry."""  # pragma: no cover
        return self  # pragma: no cover

    async def __aexit__(
        self, exc_type: Any, exc_val: Any, exc_tb: Any
    ) -> None:  # pragma: no cover
        """Async context manager exit."""  # pragma: no cover
        await self.close()  # pragma: no cover
