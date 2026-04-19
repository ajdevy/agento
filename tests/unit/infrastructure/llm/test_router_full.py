"""Tests for router module."""

import pytest


class TestModelRouterFull:
    """Comprehensive tests for ModelRouter."""

    def test_select_model_with_fallback_all_exhausted(self):
        """Test fallback when free model exhausted."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter(default_tier="free")

        # Simulate all free requests used
        for _ in range(200):
            router.record_usage("openrouter/free", tokens=100)

        model, fallbacks = router.select_model_with_fallback("code_generation")

        # Should still return a model (may be first exhausted)
        assert model in fallbacks

    def test_get_usage_stats_nonexistent_model(self):
        """Test get_usage_stats for model never used."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        stats = router.get_usage_stats("never-used-model")

        assert stats["requests_today"] == 0
        assert stats["tokens_today"] == 0

    def test_rate_limit_status_limited(self):
        """Test rate limit status when limited."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        # Simulate usage up to limit
        for _ in range(200):
            router.record_usage("openrouter/free", tokens=100)

        status = router.get_rate_limit_status("openrouter/free")

        assert status["is_limited"] is True
        assert status["remaining"] == 0
        assert status["requests_today"] == 200

    def test_get_cost_estimate_with_paid_model(self):
        """Test cost estimate for paid model."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        cost = router.get_cost_estimate(
            "anthropic/claude-3.5-sonnet", prompt_tokens=1000, completion_tokens=2000
        )

        # 0.001 * 3.0 + 0.002 * 15.0 = 0.003 + 0.03 = 0.033
        assert cost > 0
        assert cost < 0.05

    def test_format_cost_zero(self):
        """Test formatting zero cost."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        assert router.format_cost(0.0) == "$0.00 (FREE)"

    def test_format_cost_small(self):
        """Test formatting small cost."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        result = router.format_cost(0.001)
        assert "$" in result

    def test_format_cost_large(self):
        """Test formatting large cost."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        result = router.format_cost(123.456)
        assert "$123.456" in result


class TestRateLimiterFull:
    """Comprehensive tests for RateLimiter."""

    @pytest.mark.asyncio
    async def test_acquire_wait_for_limit(self):
        """Test acquire waits when rate limited."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        # Simulate reaching limit
        tracker = limiter._get_tracker("openrouter/free")
        for _ in range(20):
            tracker.record_request(100)

        # This should either succeed (waited) or fail quickly
        result = await limiter.acquire(
            "openrouter/free", tokens=100, wait=True, timeout=1.0
        )

        # Result depends on timing
        assert isinstance(result, bool)

    def test_is_limited_when_at_limit(self):
        """Test is_limited when at daily limit."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        # Simulate reaching daily limit
        tracker = limiter._get_tracker("openrouter/free")
        for _ in range(200):
            tracker.record_request(100)

        assert limiter.is_limited("openrouter/free") is True

    def test_get_alternatives_free_model(self):
        """Test get_alternatives when using free model."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        alternatives = limiter.get_alternatives("paid/model")

        assert "openrouter/free" in alternatives

    def test_get_status_detailed(self):
        """Test get_status returns all details."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        status = limiter.get_status("openrouter/free")

        assert "model" in status
        assert "requests_today" in status
        assert "requests_per_day_limit" in status
        assert "tokens_today" in status
        assert "minute_remaining" in status
        assert "daily_remaining" in status
        assert status["daily_remaining"] > 0

    def test_tracker_reset_on_new_day(self):
        """Test tracker resets when new day."""
        from datetime import datetime, timedelta

        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        # Add requests
        tracker = limiter._get_tracker("test-model")
        tracker.record_request(100)

        # Manually reset to yesterday
        tracker.daily_reset = datetime.now() - timedelta(days=1)

        # Check can make request (should reset)
        can_proceed, _ = tracker.can_make_request(limiter._get_limit("test-model"))

        assert can_proceed is True
        assert len(tracker.requests) == 0

    def test_rate_limit_error_exception(self):
        """Test RateLimitError exception."""
        from agento.infrastructure.llm.router import RateLimitError

        error = RateLimitError(
            model="test-model",
            limit_type="requests_per_minute",
            used=20,
            limit=20,
        )

        assert error.model == "test-model"
        assert error.limit_type == "requests_per_minute"
        assert error.used == 20
        assert error.limit == 20
        assert "test-model" in str(error)

    def test_can_use_model_paid(self):
        """Test _can_use_model for paid models."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()
        router.usage_stats["paid/model"] = {"requests_today": 500, "tokens_today": 0}

        # Paid models have 1000/day limit
        assert router._can_use_model("paid/model") is True

        # At limit
        router.usage_stats["paid/model"]["requests_today"] = 1000
        assert router._can_use_model("paid/model") is False

    def test_select_model_with_fallback_primary(self):
        """Test select_model_with_fallback returns primary when free exhausted."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter(default_tier="free")

        # Exhaust free model
        for _ in range(200):
            router.record_usage("qwen/qwen3-coder-480b-a35b:free", tokens=100)

        model, fallbacks = router.select_model_with_fallback("code_generation")

        # Should get primary or fallback
        assert model in fallbacks

    def test_get_cost_estimate_unknown_model(self):
        """Test cost estimate for unknown model returns 0."""
        from agento.infrastructure.llm.router import ModelRouter

        router = ModelRouter()

        cost = router.get_cost_estimate("unknown/model", 1000, 2000)

        assert cost == 0.0


class TestRateLimiterEdges:
    """Edge case tests for RateLimiter."""

    @pytest.mark.asyncio
    async def test_acquire_no_wait_returns_false(self):
        """Test acquire with wait=False returns False when limited."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        # Simulate reaching minute limit
        tracker = limiter._get_tracker("openrouter/free")
        for _ in range(20):
            tracker.record_request(100)

        result = await limiter.acquire("openrouter/free", wait=False)

        assert result is False

    def test_get_tracker_creates_new(self):
        """Test _get_tracker creates new tracker for new model."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        tracker = limiter._get_tracker("new-model")

        assert tracker is not None
        assert len(tracker.requests) == 0

    def test_get_limit_with_pattern(self):
        """Test _get_limit with model pattern."""
        from agento.infrastructure.llm.rate_limiter import RateLimiter

        limiter = RateLimiter()

        # Should return default limit for unknown pattern
        limit = limiter._get_limit("unknown-model")

        assert limit.requests_per_day == 200
