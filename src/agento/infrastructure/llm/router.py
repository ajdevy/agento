"""Model router with cost-based selection."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from agento.infrastructure.llm.base import MODEL_COSTS


class ModelRoutingConfig(BaseModel):
    """Model routing configuration."""

    free: str
    primary: str
    fallback: str


MODEL_ROUTING: dict[str, ModelRoutingConfig] = {
    "code_generation": ModelRoutingConfig(
        free="qwen/qwen3-coder-480b-a35b:free",
        primary="anthropic/claude-3.5-sonnet",
        fallback="deepseek/deepseek-chat-v3-0324",
    ),
    "devops": ModelRoutingConfig(
        free="openrouter/free",
        primary="anthropic/claude-3.5-sonnet",
        fallback="deepseek/deepseek-chat-v3-0324",
    ),
    "planning": ModelRoutingConfig(
        free="deepseek/deepseek-r1-0528:free",
        primary="anthropic/claude-3.5-sonnet",
        fallback="openrouter/free",
    ),
    "reflection": ModelRoutingConfig(
        free="deepseek/deepseek-r1-0528:free",
        primary="anthropic/claude-3.5-opus",
        fallback="anthropic/claude-3.5-sonnet",
    ),
}


class RateLimitError(Exception):
    """Rate limit exceeded error."""

    def __init__(self, model: str, limit_type: str, used: int, limit: int):
        self.model = model
        self.limit_type = limit_type
        self.used = used
        self.limit = limit
        super().__init__(
            f"Rate limit exceeded for {model}: {used}/{limit} {limit_type}"
        )


class ModelRouter:
    """Router for selecting models based on task and cost."""

    def __init__(self, default_tier: str = "free"):
        self.default_tier = default_tier
        self.usage_stats: dict[str, dict[str, int]] = {}
        self._initialize_usage_stats()

    def _initialize_usage_stats(self) -> None:
        """Initialize usage statistics for all models."""
        for routing in MODEL_ROUTING.values():
            for model in [routing.free, routing.primary, routing.fallback]:
                if model not in self.usage_stats:
                    self.usage_stats[model] = {
                        "requests_today": 0,
                        "tokens_today": 0,
                    }

    def get_model(
        self,
        task_type: str = "code_generation",
        tier: str | None = None,
    ) -> str:
        """Get the best model for a task."""
        tier = tier or self.default_tier
        routing = MODEL_ROUTING.get(task_type, MODEL_ROUTING["code_generation"])

        return getattr(routing, tier, routing.primary)

    def select_model_with_fallback(
        self,
        task_type: str = "code_generation",
    ) -> tuple[str, list[str]]:
        """Select model with fallbacks."""
        routing = MODEL_ROUTING.get(task_type, MODEL_ROUTING["code_generation"])

        # Try in order: free, primary, fallback
        models = [routing.free, routing.primary, routing.fallback]

        for model in models:
            if self._can_use_model(model):
                return model, models

        # All models exhausted
        return models[0], models

    def _can_use_model(self, model: str) -> bool:
        """Check if a model can be used (rate limits)."""
        stats = self.usage_stats.get(model, {})
        daily_requests = stats.get("requests_today", 0)

        # Free models typically have 200 requests/day limit
        if "free" in model.lower():
            return daily_requests < 200

        # Paid models have higher limits
        return daily_requests < 1000

    def record_usage(self, model: str, tokens: int) -> None:
        """Record model usage."""
        if model not in self.usage_stats:
            self.usage_stats[model] = {
                "requests_today": 0,
                "tokens_today": 0,
            }

        self.usage_stats[model]["requests_today"] += 1
        self.usage_stats[model]["tokens_today"] += tokens

    def get_usage_stats(self, model: str) -> dict[str, int]:
        """Get usage stats for a model."""
        return self.usage_stats.get(model, {"requests_today": 0, "tokens_today": 0})

    def get_rate_limit_status(self, model: str) -> dict[str, Any]:
        """Get rate limit status for a model."""
        stats = self.usage_stats.get(model, {"requests_today": 0, "tokens_today": 0})

        is_free = "free" in model.lower()
        daily_limit = 200 if is_free else 1000

        return {
            "model": model,
            "requests_today": stats["requests_today"],
            "daily_limit": daily_limit,
            "remaining": max(0, daily_limit - stats["requests_today"]),
            "is_limited": stats["requests_today"] >= daily_limit,
        }

    def get_cost_estimate(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Get cost estimate for a request."""
        cost_info = MODEL_COSTS.get(model)
        if not cost_info:
            return 0.0

        input_cost = (prompt_tokens / 1_000_000) * cost_info.input_cost_per_million
        output_cost = (completion_tokens / 1_000_000) * cost_info.output_cost_per_million

        return input_cost + output_cost

    def format_cost(self, cost: float) -> str:
        """Format cost for display."""
        if cost == 0.0:
            return "$0.00 (FREE)"
        return f"${cost:.4f}"
