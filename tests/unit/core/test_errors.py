"""Tests for error module."""

import pytest

from agento.core.errors import (
    ErrorCategory,
    ErrorClassifier,
    ErrorInfo,
    ErrorPattern,
    ErrorSeverity,
    format_error_for_user,
)


class TestErrorInfo:
    """Tests for ErrorInfo dataclass."""

    def test_create_error_info(self):
        """Test creating an error info."""
        info = ErrorInfo(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message="Connection refused",
            recoverable=True,
        )
        assert info.category == ErrorCategory.NETWORK
        assert info.severity == ErrorSeverity.MEDIUM
        assert info.message == "Connection refused"
        assert info.recoverable is True
        assert info.suggestion is None
        assert info.context == {}

    def test_error_info_with_all_fields(self):
        """Test creating error info with all fields."""
        info = ErrorInfo(
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            message="Invalid input",
            recoverable=False,
            suggestion="Check input format",
            context={"field": "email", "value": "invalid"},
        )
        assert info.suggestion == "Check input format"
        assert info.context == {"field": "email", "value": "invalid"}


class TestErrorPattern:
    """Tests for ErrorPattern dataclass."""

    def test_create_pattern(self):
        """Test creating an error pattern."""
        pattern = ErrorPattern(
            pattern="timeout",
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
        )
        assert pattern.pattern == "timeout"
        assert pattern.category == ErrorCategory.TIMEOUT
        assert pattern.severity == ErrorSeverity.MEDIUM
        assert pattern.recoverable is True
        assert pattern.suggestion is None

    def test_pattern_with_all_fields(self):
        """Test creating pattern with all fields."""
        pattern = ErrorPattern(
            pattern="auth",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            suggestion="Check credentials",
        )
        assert pattern.recoverable is False
        assert pattern.suggestion == "Check credentials"


class TestErrorClassifier:
    """Tests for ErrorClassifier class."""

    @pytest.fixture
    def classifier(self):
        """Create an error classifier."""
        return ErrorClassifier()

    def test_classify_authentication_error(self, classifier):
        """Test classifying authentication error."""
        info = classifier.classify("Authentication failed")
        assert info.category == ErrorCategory.AUTHENTICATION
        assert info.severity == ErrorSeverity.HIGH
        assert info.recoverable is False

    def test_classify_401_error(self, classifier):
        """Test classifying 401 error."""
        info = classifier.classify("Error 401: Unauthorized")
        assert info.category == ErrorCategory.AUTHENTICATION

    def test_classify_403_error(self, classifier):
        """Test classifying 403 error."""
        info = classifier.classify("Error 403: Forbidden")
        assert info.category == ErrorCategory.AUTHORIZATION

    def test_classify_rate_limit_error(self, classifier):
        """Test classifying rate limit error."""
        info = classifier.classify("Rate limit exceeded")
        assert info.category == ErrorCategory.RATE_LIMIT
        assert info.recoverable is True

    def test_classify_429_error(self, classifier):
        """Test classifying 429 error."""
        info = classifier.classify("HTTP 429 Too Many Requests")
        assert info.category == ErrorCategory.RATE_LIMIT

    def test_classify_timeout_error(self, classifier):
        """Test classifying timeout error."""
        info = classifier.classify("Request timed out")
        assert info.category == ErrorCategory.TIMEOUT
        assert info.recoverable is True

    def test_classify_network_error(self, classifier):
        """Test classifying network error."""
        info = classifier.classify("Connection refused")
        assert info.category == ErrorCategory.NETWORK

    def test_classify_not_found_error(self, classifier):
        """Test classifying not found error."""
        info = classifier.classify("404 Not Found")
        assert info.category == ErrorCategory.NOT_FOUND

    def test_classify_conflict_error(self, classifier):
        """Test classifying conflict error."""
        info = classifier.classify("409 Conflict")
        assert info.category == ErrorCategory.CONFLICT

    def test_classify_500_error(self, classifier):
        """Test classifying 500 error."""
        info = classifier.classify("500 Internal Server Error")
        assert info.category == ErrorCategory.INTERNAL
        assert info.severity == ErrorSeverity.HIGH

    def test_classify_502_503_504_errors(self, classifier):
        """Test classifying 502/503/504 errors."""
        for code in ["502", "503", "504"]:
            info = classifier.classify(f"HTTP {code}")
            assert info.category == ErrorCategory.INTERNAL

    def test_classify_resource_error(self, classifier):
        """Test classifying resource error."""
        info = classifier.classify("Out of memory")
        assert info.category == ErrorCategory.RESOURCE

    def test_classify_validation_error(self, classifier):
        """Test classifying validation error."""
        info = classifier.classify("Invalid input data")
        assert info.category == ErrorCategory.VALIDATION

    def test_classify_unknown_error(self, classifier):
        """Test classifying unknown error."""
        info = classifier.classify("Something went wrong")
        assert info.category == ErrorCategory.UNKNOWN
        assert info.recoverable is True

    def test_classify_with_context(self, classifier):
        """Test classifying with context."""
        info = classifier.classify(
            "Connection refused",
            context={"host": "example.com", "port": 8080},
        )
        assert info.context == {"host": "example.com", "port": 8080}

    def test_classify_adds_to_history(self, classifier):
        """Test that classified errors are added to history."""
        classifier.classify("Error 1")
        classifier.classify("Error 2")
        assert len(classifier.get_error_history()) == 2

    def test_get_category_from_http_code(self, classifier):
        """Test getting category from HTTP code."""
        assert classifier.get_category_from_http_code(400) == ErrorCategory.VALIDATION
        assert (
            classifier.get_category_from_http_code(401) == ErrorCategory.AUTHENTICATION
        )
        assert (
            classifier.get_category_from_http_code(403) == ErrorCategory.AUTHORIZATION
        )
        assert classifier.get_category_from_http_code(404) == ErrorCategory.NOT_FOUND
        assert classifier.get_category_from_http_code(409) == ErrorCategory.CONFLICT
        assert classifier.get_category_from_http_code(429) == ErrorCategory.RATE_LIMIT
        assert classifier.get_category_from_http_code(500) == ErrorCategory.INTERNAL

    def test_get_category_from_unknown_code(self, classifier):
        """Test getting category from unknown HTTP code."""
        assert classifier.get_category_from_http_code(999) == ErrorCategory.UNKNOWN

    def test_get_severity_from_category(self, classifier):
        """Test getting severity from category."""
        assert (
            classifier.get_severity_from_category(ErrorCategory.AUTHENTICATION)
            == ErrorSeverity.HIGH
        )
        assert (
            classifier.get_severity_from_category(ErrorCategory.VALIDATION)
            == ErrorSeverity.MEDIUM
        )
        assert (
            classifier.get_severity_from_category(ErrorCategory.RATE_LIMIT)
            == ErrorSeverity.LOW
        )

    def test_should_retry_recoverable(self, classifier):
        """Test should_retry for recoverable error."""
        info = ErrorInfo(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message="Error",
            recoverable=True,
        )
        assert classifier.should_retry(info) is True

    def test_should_retry_non_recoverable(self, classifier):
        """Test should_retry for non-recoverable error."""
        info = ErrorInfo(
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            message="Error",
            recoverable=False,
        )
        assert classifier.should_retry(info) is False

    def test_get_recovery_suggestion_with_suggestion(self, classifier):
        """Test getting recovery suggestion when present."""
        info = ErrorInfo(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message="Error",
            recoverable=True,
            suggestion="Check network",
        )
        assert classifier.get_recovery_suggestion(info) == "Check network"

    def test_get_recovery_suggestion_without_suggestion(self, classifier):
        """Test getting recovery suggestion when absent."""
        info = ErrorInfo(
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            message="Error",
            recoverable=True,
        )
        suggestion = classifier.get_recovery_suggestion(info)
        assert "timeout" in suggestion.lower() or "retry" in suggestion.lower()

    def test_get_error_summary_empty(self, classifier):
        """Test error summary with no history."""
        summary = classifier.get_error_summary()
        assert summary["total"] == 0
        assert summary["by_category"] == {}
        assert summary["by_severity"] == {}

    def test_get_error_summary_with_data(self, classifier):
        """Test error summary with history."""
        classifier.classify("Error 401: Auth")
        classifier.classify("Error 401: Auth")
        classifier.classify("Error 404: Not found")

        summary = classifier.get_error_summary()
        assert summary["total"] == 3
        assert summary["by_category"]["authentication"] == 2
        assert summary["by_category"]["not_found"] == 1

    def test_clear_history(self, classifier):
        """Test clearing error history."""
        classifier.classify("Error 1")
        classifier.classify("Error 2")
        classifier.clear_history()
        assert len(classifier.get_error_history()) == 0


class TestErrorCategory:
    """Tests for ErrorCategory enum."""

    def test_all_categories_exist(self):
        """Test all error categories exist."""
        assert ErrorCategory.AUTHENTICATION is not None
        assert ErrorCategory.AUTHORIZATION is not None
        assert ErrorCategory.VALIDATION is not None
        assert ErrorCategory.NETWORK is not None
        assert ErrorCategory.TIMEOUT is not None
        assert ErrorCategory.RATE_LIMIT is not None
        assert ErrorCategory.RESOURCE is not None
        assert ErrorCategory.NOT_FOUND is not None
        assert ErrorCategory.CONFLICT is not None
        assert ErrorCategory.INTERNAL is not None
        assert ErrorCategory.UNKNOWN is not None

    def test_category_values(self):
        """Test error category values."""
        assert ErrorCategory.AUTHENTICATION.value == "authentication"
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.UNKNOWN.value == "unknown"


class TestErrorSeverity:
    """Tests for ErrorSeverity enum."""

    def test_all_severities_exist(self):
        """Test all error severities exist."""
        assert ErrorSeverity.CRITICAL is not None
        assert ErrorSeverity.HIGH is not None
        assert ErrorSeverity.MEDIUM is not None
        assert ErrorSeverity.LOW is not None

    def test_severity_values(self):
        """Test error severity values."""
        assert ErrorSeverity.CRITICAL.value == "critical"
        assert ErrorSeverity.HIGH.value == "high"
        assert ErrorSeverity.MEDIUM.value == "medium"
        assert ErrorSeverity.LOW.value == "low"


class TestFormatErrorForUser:
    """Tests for format_error_for_user function."""

    def test_format_basic_error(self):
        """Test formatting a basic error."""
        info = ErrorInfo(
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            message="Connection refused",
            recoverable=True,
        )
        formatted = format_error_for_user(info)
        assert "Connection refused" in formatted
        assert "network" in formatted
        assert "medium" in formatted

    def test_format_error_with_suggestion(self):
        """Test formatting error with suggestion."""
        info = ErrorInfo(
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            message="Request timed out",
            recoverable=True,
            suggestion="Increase timeout",
        )
        formatted = format_error_for_user(info)
        assert "Increase timeout" in formatted

    def test_format_error_with_context(self):
        """Test formatting error with context."""
        info = ErrorInfo(
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            message="Invalid input",
            recoverable=False,
            context={"field": "email"},
        )
        formatted = format_error_for_user(info)
        assert "email" in formatted
