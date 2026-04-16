"""Test configuration."""

from __future__ import annotations

import pytest


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from agento.config import Settings

    settings = Settings(
        openrouter_api_key="sk-test-key",
        default_model="openrouter/free",
    )
    return settings


@pytest.fixture
def mock_llm_response():
    """Mock LLM response."""
    return {
        "content": "Test response",
        "model": "openrouter/free",
        "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        "cost": 0.0,
    }


@pytest.fixture
def sample_messages():
    """Sample chat messages."""
    return [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"},
    ]
