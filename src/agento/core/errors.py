"""Error classification and handling."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar


class ErrorCategory(Enum):
    """Error category classification."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    RESOURCE = "resource"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class ErrorSeverity(Enum):
    """Error severity level."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ErrorInfo:
    """Structured error information."""

    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    recoverable: bool
    suggestion: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorPattern:
    """Pattern for error matching."""

    pattern: str
    category: ErrorCategory
    severity: ErrorSeverity
    recoverable: bool = True
    suggestion: str | None = None


class ErrorClassifier:
    """Classify and analyze errors."""

    PATTERNS: ClassVar[list[ErrorPattern]] = [
        ErrorPattern(
            pattern="authentication",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            suggestion="Check API key or authentication credentials",
        ),
        ErrorPattern(
            pattern="401",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            suggestion="Invalid or expired authentication token",
        ),
        ErrorPattern(
            pattern="403",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            suggestion="Insufficient permissions for this operation",
        ),
        ErrorPattern(
            pattern="rate.limit",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            suggestion="Wait before retrying or reduce request frequency",
        ),
        ErrorPattern(
            pattern="429",
            category=ErrorCategory.RATE_LIMIT,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            suggestion="Too many requests - implement backoff strategy",
        ),
        ErrorPattern(
            pattern="timeout|timed.out",
            category=ErrorCategory.TIMEOUT,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            suggestion="Increase timeout or check network connectivity",
        ),
        ErrorPattern(
            pattern="connection|refused|unreachable",
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            suggestion="Check network connection and service availability",
        ),
        ErrorPattern(
            pattern="404|not.found",
            category=ErrorCategory.NOT_FOUND,
            severity=ErrorSeverity.LOW,
            recoverable=False,
            suggestion="Verify resource identifier or endpoint URL",
        ),
        ErrorPattern(
            pattern="409|conflict",
            category=ErrorCategory.CONFLICT,
            severity=ErrorSeverity.MEDIUM,
            recoverable=True,
            suggestion="Resolve conflict before retrying",
        ),
        ErrorPattern(
            pattern="500|internal.error",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            recoverable=True,
            suggestion="Service may be experiencing issues - retry later",
        ),
        ErrorPattern(
            pattern="502|503|504",
            category=ErrorCategory.INTERNAL,
            severity=ErrorSeverity.HIGH,
            recoverable=True,
            suggestion="Service temporarily unavailable - retry later",
        ),
        ErrorPattern(
            pattern="memory|disk|quota",
            category=ErrorCategory.RESOURCE,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            suggestion="Resource limit reached - free up resources",
        ),
        ErrorPattern(
            pattern="validation|invalid|malformed",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.MEDIUM,
            recoverable=False,
            suggestion="Fix input data format or content",
        ),
    ]

    def __init__(self) -> None:
        self._error_history: list[ErrorInfo] = []

    def classify(
        self,
        error: Exception | str,
        context: dict[str, Any] | None = None,
    ) -> ErrorInfo:
        """Classify an error."""
        error_str = str(error).lower()
        context = context or {}

        for pattern in self.PATTERNS:
            if re.search(pattern.pattern, error_str, re.IGNORECASE):
                info = ErrorInfo(
                    category=pattern.category,
                    severity=pattern.severity,
                    message=str(error),
                    recoverable=pattern.recoverable,
                    suggestion=pattern.suggestion,
                    context=context,
                )
                self._error_history.append(info)
                return info

        info = ErrorInfo(
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.MEDIUM,
            message=str(error),
            recoverable=True,
            suggestion="Review error details and take appropriate action",
            context=context,
        )
        self._error_history.append(info)
        return info

    def get_category_from_http_code(self, code: int) -> ErrorCategory:
        """Get error category from HTTP status code."""
        category_map = {
            400: ErrorCategory.VALIDATION,
            401: ErrorCategory.AUTHENTICATION,
            403: ErrorCategory.AUTHORIZATION,
            404: ErrorCategory.NOT_FOUND,
            409: ErrorCategory.CONFLICT,
            429: ErrorCategory.RATE_LIMIT,
            500: ErrorCategory.INTERNAL,
            502: ErrorCategory.INTERNAL,
            503: ErrorCategory.INTERNAL,
            504: ErrorCategory.TIMEOUT,
        }
        return category_map.get(code, ErrorCategory.UNKNOWN)

    def get_severity_from_category(self, category: ErrorCategory) -> ErrorSeverity:
        """Get default severity for error category."""
        severity_map = {
            ErrorCategory.AUTHENTICATION: ErrorSeverity.HIGH,
            ErrorCategory.AUTHORIZATION: ErrorSeverity.HIGH,
            ErrorCategory.VALIDATION: ErrorSeverity.MEDIUM,
            ErrorCategory.NETWORK: ErrorSeverity.MEDIUM,
            ErrorCategory.TIMEOUT: ErrorSeverity.MEDIUM,
            ErrorCategory.RATE_LIMIT: ErrorSeverity.LOW,
            ErrorCategory.RESOURCE: ErrorSeverity.HIGH,
            ErrorCategory.NOT_FOUND: ErrorSeverity.LOW,
            ErrorCategory.CONFLICT: ErrorSeverity.MEDIUM,
            ErrorCategory.INTERNAL: ErrorSeverity.HIGH,
            ErrorCategory.UNKNOWN: ErrorSeverity.MEDIUM,
        }
        return severity_map.get(category, ErrorSeverity.MEDIUM)

    def should_retry(self, error_info: ErrorInfo) -> bool:
        """Determine if error should trigger retry."""
        return error_info.recoverable

    def get_recovery_suggestion(self, error_info: ErrorInfo) -> str:
        """Get recovery suggestion for error."""
        if error_info.suggestion:
            return error_info.suggestion

        suggestion_map = {
            ErrorCategory.AUTHENTICATION: "Check and update authentication credentials",
            ErrorCategory.AUTHORIZATION: "Request necessary permissions",
            ErrorCategory.VALIDATION: "Fix input data format",
            ErrorCategory.NETWORK: "Check network connectivity",
            ErrorCategory.TIMEOUT: "Increase timeout or retry",
            ErrorCategory.RATE_LIMIT: "Implement rate limiting or backoff",
            ErrorCategory.RESOURCE: "Free up or increase resources",
            ErrorCategory.NOT_FOUND: "Verify resource exists",
            ErrorCategory.CONFLICT: "Resolve conflict before retry",
            ErrorCategory.INTERNAL: "Retry after delay or contact support",
            ErrorCategory.UNKNOWN: "Review error and take appropriate action",
        }
        return suggestion_map.get(error_info.category, "Review and resolve error")

    def get_error_history(self) -> list[ErrorInfo]:
        """Get error history."""
        return self._error_history.copy()

    def get_error_summary(self) -> dict[str, Any]:
        """Get summary of error history."""
        if not self._error_history:
            return {"total": 0, "by_category": {}, "by_severity": {}}

        by_category: dict[str, int] = {}
        by_severity: dict[str, int] = {}

        for error in self._error_history:
            cat = error.category.value
            sev = error.severity.value
            by_category[cat] = by_category.get(cat, 0) + 1
            by_severity[sev] = by_severity.get(sev, 0) + 1

        return {
            "total": len(self._error_history),
            "by_category": by_category,
            "by_severity": by_severity,
            "recoverable_count": sum(1 for e in self._error_history if e.recoverable),
        }

    def clear_history(self) -> None:
        """Clear error history."""
        self._error_history.clear()


def format_error_for_user(error_info: ErrorInfo) -> str:
    """Format error for user-friendly display."""
    lines = [
        f"Error: {error_info.message}",
    ]

    if error_info.suggestion:
        lines.append(f"Suggestion: {error_info.suggestion}")

    lines.append(f"Category: {error_info.category.value}")
    lines.append(f"Severity: {error_info.severity.value}")

    if error_info.context:
        lines.append(f"Context: {error_info.context}")

    return "\n".join(lines)
