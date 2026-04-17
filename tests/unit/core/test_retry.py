"""Tests for retry module."""

import pytest

from agento.core.retry import (
    AttemptRecord,
    CircuitBreaker,
    RetryConfig,
    RetryError,
    RetryPolicy,
    RetryResult,
    RetryStrategy,
    retry_with_backoff,
    with_retry,
)


class TestRetryConfig:
    """Tests for RetryConfig dataclass."""

    def test_create_config(self):
        """Test creating a retry config."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.multiplier == 2.0
        assert config.strategy == RetryStrategy.EXPONENTIAL
        assert config.retryable_exceptions == (Exception,)
        assert config.non_retryable_exceptions == ()

    def test_config_with_custom_values(self):
        """Test creating config with custom values."""
        config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=30.0,
            multiplier=1.5,
            strategy=RetryStrategy.LINEAR,
        )
        assert config.max_attempts == 5
        assert config.initial_delay == 0.5
        assert config.max_delay == 30.0
        assert config.multiplier == 1.5
        assert config.strategy == RetryStrategy.LINEAR

    def test_get_delay_exponential(self):
        """Test exponential delay calculation."""
        config = RetryConfig(strategy=RetryStrategy.EXPONENTIAL)
        assert config.get_delay(1) == 1.0
        assert config.get_delay(2) == 2.0
        assert config.get_delay(3) == 4.0
        assert config.get_delay(4) == 8.0

    def test_get_delay_exponential_capped(self):
        """Test exponential delay capped at max_delay."""
        config = RetryConfig(
            initial_delay=10.0,
            max_delay=50.0,
            strategy=RetryStrategy.EXPONENTIAL,
        )
        assert config.get_delay(1) == 10.0
        assert config.get_delay(2) == 20.0
        assert config.get_delay(3) == 40.0
        assert config.get_delay(4) == 50.0
        assert config.get_delay(5) == 50.0

    def test_get_delay_linear(self):
        """Test linear delay calculation."""
        config = RetryConfig(
            initial_delay=1.0,
            strategy=RetryStrategy.LINEAR,
        )
        assert config.get_delay(1) == 1.0
        assert config.get_delay(2) == 2.0
        assert config.get_delay(3) == 3.0

    def test_get_delay_fixed(self):
        """Test fixed delay calculation."""
        config = RetryConfig(
            initial_delay=5.0,
            strategy=RetryStrategy.FIXED,
        )
        assert config.get_delay(1) == 5.0
        assert config.get_delay(2) == 5.0
        assert config.get_delay(3) == 5.0


class TestRetryResult:
    """Tests for RetryResult dataclass."""

    def test_create_success_result(self):
        """Test creating a successful retry result."""
        result = RetryResult(
            success=True,
            attempts=2,
            total_time=1.5,
            result="value",
        )
        assert result.success is True
        assert result.attempts == 2
        assert result.total_time == 1.5
        assert result.result == "value"
        assert result.error is None

    def test_create_failure_result(self):
        """Test creating a failed retry result."""
        error = ValueError("Test error")
        result = RetryResult(
            success=False,
            attempts=3,
            total_time=3.0,
            error=error,
        )
        assert result.success is False
        assert result.attempts == 3
        assert result.error == error


class TestAttemptRecord:
    """Tests for AttemptRecord dataclass."""

    def test_create_record(self):
        """Test creating an attempt record."""
        from datetime import datetime

        record = AttemptRecord(
            attempt_number=1,
            started_at=datetime.now(),
        )
        assert record.attempt_number == 1
        assert record.completed_at is None
        assert record.success is False
        assert record.error is None
        assert record.delay == 0.0


class TestRetryPolicy:
    """Tests for RetryPolicy class."""

    @pytest.fixture
    def policy(self):
        """Create a retry policy."""
        return RetryPolicy()

    @pytest.mark.asyncio
    async def test_execute_success_first_attempt(self, policy):
        """Test successful execution on first attempt."""
        result = await policy.execute(lambda: "success")
        assert result.success is True
        assert result.attempts == 1
        assert result.result == "success"

    @pytest.mark.asyncio
    async def test_execute_async_success(self, policy):
        """Test successful async execution."""

        async def async_func():
            return "async result"

        result = await policy.execute(async_func)
        assert result.success is True
        assert result.result == "async result"

    @pytest.mark.asyncio
    async def test_execute_failure_after_retries(self, policy):
        """Test failure after max retries."""

        def failing_func():
            raise ValueError("Always fails")

        result = await policy.execute(failing_func)
        assert result.success is False
        assert result.attempts == 3
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_execute_success_after_retry(self, policy):
        """Test success on second attempt."""
        call_count = 0

        def flaky_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("First failure")
            return "success"

        result = await policy.execute(flaky_func)
        assert result.success is True
        assert result.attempts == 2
        assert result.result == "success"

    @pytest.mark.asyncio
    async def test_non_retryable_exception(self, policy):
        """Test non-retryable exception doesn't retry."""

        class NonRetryableError(Exception):
            pass

        policy.config.non_retryable_exceptions = (NonRetryableError,)

        def failing_func():
            raise NonRetryableError("Non retryable")

        result = await policy.execute(failing_func)
        assert result.success is False
        assert result.attempts == 1

    def test_should_retry_retryable(self, policy):
        """Test should_retry for retryable exception."""
        assert policy.should_retry(ValueError("test")) is True

    def test_should_retry_non_retryable(self, policy):

        class NonRetryableError(Exception):
            pass

        policy.config.non_retryable_exceptions = (NonRetryableError,)
        assert policy.should_retry(NonRetryableError("test")) is False

    def test_get_attempt_history(self, policy):
        """Test getting attempt history."""
        assert policy.get_attempt_history() == []

    def test_clear_history(self, policy):
        """Test clearing attempt history."""
        policy._attempt_history.append(
            AttemptRecord(
                attempt_number=1,
                started_at=policy._attempt_history[0].started_at
                if policy._attempt_history
                else None,
            )
        )
        if policy._attempt_history:
            policy._attempt_history[0].completed_at = policy._attempt_history[
                0
            ].started_at
        policy.clear_history()
        assert len(policy.get_attempt_history()) == 0


class TestRetryError:
    """Tests for RetryError exception."""

    def test_create_error(self):
        """Test creating a retry error."""
        original_error = ValueError("Original")
        error = RetryError("Max retries exceeded", 3, original_error)
        assert str(error) == "Max retries exceeded"
        assert error.attempts == 3
        assert error.last_error == original_error


class TestWithRetryDecorator:
    """Tests for with_retry decorator."""

    def test_decorator_sync_success(self):
        """Test decorator on sync function that succeeds."""

        @with_retry()
        def sync_func():
            return "success"

        result = sync_func()
        assert result == "success"

    def test_decorator_sync_failure(self):
        """Test decorator on sync function that fails."""

        @with_retry(config=RetryConfig(max_attempts=1))
        def sync_fail():
            raise ValueError("Fail")

        with pytest.raises(ValueError):
            sync_fail()


class TestRetryWithBackoff:
    """Tests for retry_with_backoff function."""

    @pytest.mark.asyncio
    async def test_retry_success_first(self):
        """Test retry success on first attempt."""
        result = await retry_with_backoff(lambda: "success")
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_success_after_failure(self):
        """Test retry success after one failure."""
        call_count = 0

        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Fail")
            return "success"

        result = await retry_with_backoff(flaky, max_attempts=3)
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_raises_after_max_attempts(self):
        """Test that exception is raised after max attempts."""
        call_count = 0

        def always_fails():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            await retry_with_backoff(always_fails, max_attempts=3)
        assert call_count == 3


class TestCircuitBreaker:
    """Tests for CircuitBreaker class."""

    def test_initial_state(self):
        """Test circuit breaker initial state."""
        cb = CircuitBreaker()
        assert cb.state == "closed"
        assert cb._failure_count == 0

    def test_record_success(self):
        """Test recording success."""
        cb = CircuitBreaker()
        cb._failure_count = 2
        cb.record_success()
        assert cb.state == "closed"
        assert cb._failure_count == 0

    def test_record_failure(self):
        """Test recording failure."""
        cb = CircuitBreaker()
        cb.record_failure()
        assert cb._failure_count == 1
        assert cb._last_failure_time is not None

    def test_opens_after_threshold(self):
        """Test circuit opens after failure threshold."""
        cb = CircuitBreaker(failure_threshold=3)
        cb.record_failure()
        cb.record_failure()
        assert cb.state == "closed"
        cb.record_failure()
        assert cb.state == "open"

    def test_half_open_after_timeout(self):
        """Test circuit goes to half-open after timeout."""
        from datetime import datetime, timedelta

        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        cb.record_failure()
        assert cb.state == "open"

        cb._last_failure_time = datetime.now() - timedelta(seconds=1)
        assert cb.state == "half-open"

    @pytest.mark.asyncio
    async def test_call_success(self):
        """Test successful call through circuit breaker."""
        cb = CircuitBreaker()

        async def func():
            return "success"

        result = await cb.call(func)
        assert result == "success"
        assert cb._failure_count == 0

    @pytest.mark.asyncio
    async def test_call_failure(self):
        """Test failed call through circuit breaker."""

        async def failing_func():
            raise ValueError("Fail")

        cb = CircuitBreaker()
        with pytest.raises(ValueError):
            await cb.call(failing_func)
        assert cb._failure_count == 1

    @pytest.mark.asyncio
    async def test_call_open_circuit(self):
        """Test call when circuit is open."""
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.state == "open"

        with pytest.raises(Exception, match="Circuit breaker is open"):
            await cb.call(lambda: "test")


class TestRetryStrategy:
    """Tests for RetryStrategy enum."""

    def test_all_strategies_exist(self):
        """Test all retry strategies exist."""
        assert RetryStrategy.EXPONENTIAL is not None
        assert RetryStrategy.LINEAR is not None
        assert RetryStrategy.FIXED is not None

    def test_strategy_values(self):
        """Test retry strategy values."""
        assert RetryStrategy.EXPONENTIAL.value == "exponential"
        assert RetryStrategy.LINEAR.value == "linear"
        assert RetryStrategy.FIXED.value == "fixed"
