"""Retry logic with exponential backoff."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

from typing_extensions import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


class RetryStrategy(Enum):
    """Retry strategy types."""

    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class RetryError(Exception):
    """Error raised when retry limit exceeded."""

    def __init__(self, message: str, attempts: int, last_error: Exception):
        super().__init__(message)
        self.attempts = attempts
        self.last_error = last_error


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,)
    non_retryable_exceptions: tuple[type[Exception], ...] = ()

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        if self.strategy == RetryStrategy.FIXED:
            return self.initial_delay
        elif self.strategy == RetryStrategy.LINEAR:
            return self.initial_delay * attempt
        else:
            delay = self.initial_delay * (self.multiplier ** (attempt - 1))
            return min(delay, self.max_delay)


@dataclass
class RetryResult:
    """Result of a retry operation."""

    success: bool
    attempts: int
    total_time: float
    result: Any = None
    error: Exception | None = None


@dataclass
class AttemptRecord:
    """Record of a single attempt."""

    attempt_number: int
    started_at: datetime
    completed_at: datetime | None = None
    success: bool = False
    error: Exception | None = None
    delay: float = 0.0


class RetryPolicy:
    """Policy for retry behavior."""

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()
        self._attempt_history: list[AttemptRecord] = []

    async def execute(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> RetryResult:
        """Execute function with retry logic."""
        start_time = datetime.now()
        last_error: Exception | None = None

        for attempt in range(1, self.config.max_attempts + 1):
            record = AttemptRecord(
                attempt_number=attempt,
                started_at=datetime.now(),
            )

            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                record.completed_at = datetime.now()
                record.success = True
                self._attempt_history.append(record)

                total_time = (datetime.now() - start_time).total_seconds()
                return RetryResult(
                    success=True,
                    attempts=attempt,
                    total_time=total_time,
                    result=result,
                )

            except self.config.non_retryable_exceptions as e:
                record.completed_at = datetime.now()
                record.error = e
                self._attempt_history.append(record)
                total_time = (datetime.now() - start_time).total_seconds()
                return RetryResult(
                    success=False,
                    attempts=attempt,
                    total_time=total_time,
                    error=e,
                )

            except self.config.retryable_exceptions as e:
                record.completed_at = datetime.now()
                record.error = e
                self._attempt_history.append(record)
                last_error = e

                if attempt < self.config.max_attempts:
                    delay = self.config.get_delay(attempt)
                    record.delay = delay
                    await asyncio.sleep(delay)

        total_time = (datetime.now() - start_time).total_seconds()
        return RetryResult(
            success=False,
            attempts=self.config.max_attempts,
            total_time=total_time,
            error=last_error,
        )

    def should_retry(self, exception: Exception) -> bool:
        """Determine if exception should trigger retry."""
        if isinstance(exception, self.config.non_retryable_exceptions):
            return False

        if isinstance(exception, self.config.retryable_exceptions):
            return True

        return True

    def get_attempt_history(self) -> list[AttemptRecord]:
        """Get attempt history."""
        return self._attempt_history.copy()

    def clear_history(self) -> None:
        """Clear attempt history."""
        self._attempt_history.clear()


def with_retry(
    config: RetryConfig | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator to add retry logic to a function."""

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        policy = RetryPolicy(config)

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            result = await policy.execute(func, *args, **kwargs)
            if not result.success and result.error:
                raise result.error
            return result.result

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            policy_sync = RetryPolicy(config)

            async def run_async():
                return await policy_sync.execute(func, *args, **kwargs)

            result = asyncio.run(run_async())
            if not result.success and result.error:
                raise result.error
            return result.result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


async def retry_with_backoff(
    func: Callable[..., T],
    *args: Any,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    multiplier: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs: Any,
) -> T:
    """Simple retry with exponential backoff."""
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        except exceptions as e:
            last_error = e
            if attempt < max_attempts - 1:
                delay = initial_delay * (multiplier**attempt)
                await asyncio.sleep(delay)

    if last_error:
        raise last_error
    raise RetryError(
        "Retry failed", max_attempts, last_error or Exception("Unknown error")
    )


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type[Exception] = Exception,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self._failure_count = 0
        self._last_failure_time: datetime | None = None
        self._state = "closed"

    @property
    def state(self) -> str:
        """Get current circuit breaker state."""
        if self._state == "open":
            if self._last_failure_time:
                elapsed = (datetime.now() - self._last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self._state = "half-open"
        return self._state

    def record_success(self) -> None:
        """Record a successful call."""
        self._failure_count = 0
        self._state = "closed"

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()

        if self._failure_count >= self.failure_threshold:
            self._state = "open"

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute function through circuit breaker."""
        if self.state == "open":
            raise Exception("Circuit breaker is open")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self.record_success()
            return result
        except self.expected_exception as e:
            self.record_failure()
            raise e
