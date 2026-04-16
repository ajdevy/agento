"""Tests for LLM infrastructure."""

import pytest

from agento.infrastructure.llm.router import ModelRouter, RateLimitError
from agento.infrastructure.llm.rate_limiter import RateLimiter, RateLimit
from agento.infrastructure.llm.base import get_model_cost, MODEL_COSTS, LLMCost


class TestModelRouter:
    """Tests for ModelRouter."""

    def test_router_creation(self):
        """Test creating a router."""
        router = ModelRouter(default_tier="free")

        assert router.default_tier == "free"

    def test_get_model_free(self):
        """Test getting free model."""
        router = ModelRouter(default_tier="free")
        model = router.get_model("code_generation", tier="free")

        assert "free" in model.lower()

    def test_get_model_primary(self):
        """Test getting primary model."""
        router = ModelRouter(default_tier="free")
        model = router.get_model("code_generation", tier="primary")

        assert "claude" in model.lower()

    def test_select_model_with_fallback(self):
        """Test selecting model with fallbacks."""
        router = ModelRouter(default_tier="free")
        model, fallbacks = router.select_model_with_fallback("code_generation")

        assert model in fallbacks
        assert len(fallbacks) == 3

    def test_record_usage(self):
        """Test recording usage."""
        router = ModelRouter()
        router.record_usage("openrouter/free", tokens=1000)

        stats = router.get_usage_stats("openrouter/free")
        assert stats["requests_today"] == 1
        assert stats["tokens_today"] == 1000

    def test_rate_limit_status(self):
        """Test getting rate limit status."""
        router = ModelRouter()
        status = router.get_rate_limit_status("openrouter/free")

        assert "model" in status
        assert "requests_today" in status
        assert "daily_limit" in status
        assert status["is_limited"] is False

    def test_cost_estimate(self):
        """Test cost estimation."""
        router = ModelRouter()
        cost = router.get_cost_estimate(
            "anthropic/claude-3.5-sonnet",
            prompt_tokens=1000,
            completion_tokens=1000,
        )

        # 0.001 * 3.0 + 0.001 * 15.0 = 0.018
        assert cost == 0.018

    def test_format_cost(self):
        """Test cost formatting."""
        router = ModelRouter()

        assert router.format_cost(0.0) == "$0.00 (FREE)"
        assert router.format_cost(0.018) == "$0.0180"


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_limiter_creation(self):
        """Test creating a limiter."""
        limiter = RateLimiter()

        assert limiter is not None

    @pytest.mark.asyncio
    async def test_acquire_success(self):
        """Test successful acquire."""
        limiter = RateLimiter()
        result = await limiter.acquire("openrouter/free", tokens=100)

        assert result is True

    def test_get_status(self):
        """Test getting status."""
        limiter = RateLimiter()
        status = limiter.get_status("openrouter/free")

        assert "model" in status
        assert "requests_today" in status
        assert status["model"] == "openrouter/free"

    def test_is_limited(self):
        """Test checking if limited."""
        limiter = RateLimiter()
        is_limited = limiter.is_limited("openrouter/free")

        assert is_limited is False

    def test_get_alternatives(self):
        """Test getting alternatives."""
        limiter = RateLimiter()
        alternatives = limiter.get_alternatives("qwen/qwen3-coder-480b-a35b:free")

        assert len(alternatives) > 0
        assert "deepseek/deepseek-chat-v3-0324" in alternatives
        assert "google/gemini-2.0-flash" in alternatives


class TestModelCosts:
    """Tests for model costs."""

    def test_get_model_cost_free(self):
        """Test cost for free model."""
        cost = get_model_cost("openrouter/free", 1000, 1000)
        assert cost == 0.0

    def test_get_model_cost_paid(self):
        """Test cost for paid model."""
        cost = get_model_cost("anthropic/claude-3.5-sonnet", 1000, 1000)

        # 0.001 * 3.0 + 0.001 * 15.0 = 0.018
        assert cost == 0.018

    def test_get_model_cost_unknown(self):
        """Test cost for unknown model."""
        cost = get_model_cost("unknown/model", 1000, 1000)
        assert cost == 0.0

    def test_model_costs_defined(self):
        """Test that common models have costs defined."""
        assert "openrouter/free" in MODEL_COSTS
        assert "anthropic/claude-3.5-sonnet" in MODEL_COSTS
        assert "deepseek/deepseek-chat-v3-0324" in MODEL_COSTS
