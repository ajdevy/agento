"""Rate limiter for LLM requests."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class RateLimit:
    """Rate limit configuration."""

    requests_per_minute: int = 20
    requests_per_day: int = 200
    tokens_per_minute: int = 100_000


@dataclass
class UsageTracker:
    """Track usage for rate limiting."""

    requests: list[datetime] = field(default_factory=list)
    tokens_used: int = 0
    daily_reset: datetime = field(default_factory=datetime.now)

    def _reset_if_needed(self) -> None:
        """Reset daily counters if needed."""
        now = datetime.now()
        if now.date() > self.daily_reset.date():
            self.requests = []
            self.tokens_used = 0
            self.daily_reset = now

    def can_make_request(self, limit: RateLimit) -> tuple[bool, str]:
        """Check if a request can be made."""
        self._reset_if_needed()

        now = datetime.now()

        # Check minute limit
        minute_ago = now - timedelta(minutes=1)
        recent_requests = [r for r in self.requests if r > minute_ago]

        if len(recent_requests) >= limit.requests_per_minute:
            return False, "requests_per_minute"

        # Check daily limit
        if len(self.requests) >= limit.requests_per_day:
            return False, "requests_per_day"

        return True, ""

    def record_request(self, tokens: int = 0) -> None:
        """Record a request."""
        self._reset_if_needed()
        self.requests.append(datetime.now())
        self.tokens_used += tokens


class RateLimiter:
    """Rate limiter for LLM API calls."""

    def __init__(self) -> None:
        self._trackers: dict[str, UsageTracker] = {}
        self._limits: dict[str, RateLimit] = {}
        self._initialize_limits()

    def _initialize_limits(self) -> None:
        """Initialize rate limits for different models."""
        # Free models
        free_limit = RateLimit(
            requests_per_minute=20,
            requests_per_day=200,
        )

        # Set default limits
        self._limits["*"] = free_limit

    def _get_tracker(self, model: str) -> UsageTracker:
        """Get or create usage tracker for a model."""
        if model not in self._trackers:
            self._trackers[model] = UsageTracker()
        return self._trackers[model]

    def _get_limit(self, model: str) -> RateLimit:
        """Get rate limit for a model."""
        # Check if model matches any specific limit
        for pattern, limit in self._limits.items():
            if pattern != "*" and pattern.lower() in model.lower():
                return limit

        return self._limits.get("*", RateLimit())

    async def acquire(
        self,
        model: str,
        tokens: int = 0,
        wait: bool = True,
        timeout: float = 60.0,
    ) -> bool:
        """Acquire permission to make a request."""
        tracker = self._get_tracker(model)
        limit = self._get_limit(model)

        can_proceed, _ = tracker.can_make_request(limit)

        if can_proceed:
            tracker.record_request(tokens)
            return True

        if not wait:
            return False

        # Wait and retry
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            await asyncio.sleep(5)  # Wait 5 seconds

            tracker = self._get_tracker(model)
            can_proceed, _ = tracker.can_make_request(limit)

            if can_proceed:
                tracker.record_request(tokens)
                return True

        return False

    def get_status(self, model: str) -> dict[str, Any]:
        """Get rate limit status for a model."""
        tracker = self._get_tracker(model)
        limit = self._get_limit(model)

        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        recent_requests = [r for r in tracker.requests if r > minute_ago]

        return {
            "model": model,
            "requests_this_minute": len(recent_requests),
            "requests_per_minute_limit": limit.requests_per_minute,
            "requests_today": len(tracker.requests),
            "requests_per_day_limit": limit.requests_per_day,
            "tokens_today": tracker.tokens_used,
            "minute_remaining": max(
                0, limit.requests_per_minute - len(recent_requests)
            ),
            "daily_remaining": max(0, limit.requests_per_day - len(tracker.requests)),
        }

    def is_limited(self, model: str) -> bool:
        """Check if model is currently rate limited."""
        tracker = self._get_tracker(model)
        limit = self._get_limit(model)

        can_proceed, _ = tracker.can_make_request(limit)
        return not can_proceed

    def get_alternatives(self, model: str) -> list[str]:
        """Get alternative models when rate limited."""
        alternatives = []

        # Check free alternatives
        if "free" not in model.lower():
            alternatives.append("openrouter/free")

        alternatives.extend(
            [
                "deepseek/deepseek-chat-v3-0324",  # Budget option
                "google/gemini-2.0-flash",  # Free Google option
            ]
        )

        return alternatives
