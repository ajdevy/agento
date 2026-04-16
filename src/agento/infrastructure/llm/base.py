"""LLM base configuration and costs."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LLMCost:
    """LLM cost information."""

    input_cost_per_million: float
    output_cost_per_million: float
    context_window: int
    supports_function_calling: bool = True
    supports_streaming: bool = True


# Model costs (from OpenRouter pricing as of 2026)
MODEL_COSTS: dict[str, LLMCost] = {
    # Free models
    "openrouter/free": LLMCost(
        input_cost_per_million=0.0,
        output_cost_per_million=0.0,
        context_window=200_000,
    ),
    "qwen/qwen3-coder-480b-a35b:free": LLMCost(
        input_cost_per_million=0.0,
        output_cost_per_million=0.0,
        context_window=262_000,
    ),
    "deepseek/deepseek-r1-0528:free": LLMCost(
        input_cost_per_million=0.0,
        output_cost_per_million=0.0,
        context_window=128_000,
    ),
    "deepseek/deepseek-chat-v3-0324:free": LLMCost(
        input_cost_per_million=0.0,
        output_cost_per_million=0.0,
        context_window=128_000,
    ),
    # Anthropic
    "anthropic/claude-3.5-sonnet": LLMCost(
        input_cost_per_million=3.0,
        output_cost_per_million=15.0,
        context_window=200_000,
    ),
    "anthropic/claude-3.5-opus": LLMCost(
        input_cost_per_million=5.0,
        output_cost_per_million=25.0,
        context_window=200_000,
    ),
    "anthropic/claude-3.5-haiku": LLMCost(
        input_cost_per_million=1.0,
        output_cost_per_million=5.0,
        context_window=200_000,
    ),
    # DeepSeek
    "deepseek/deepseek-chat-v3-0324": LLMCost(
        input_cost_per_million=0.14,
        output_cost_per_million=0.28,
        context_window=128_000,
    ),
    # Google
    "google/gemini-2.0-flash": LLMCost(
        input_cost_per_million=0.0,
        output_cost_per_million=0.0,
        context_window=1_000_000,
    ),
    "google/gemini-2.5-flash": LLMCost(
        input_cost_per_million=0.15,
        output_cost_per_million=0.60,
        context_window=1_000_000,
    ),
    # OpenAI
    "openai/gpt-4o-mini": LLMCost(
        input_cost_per_million=0.15,
        output_cost_per_million=0.60,
        context_window=128_000,
    ),
    "openai/gpt-4o": LLMCost(
        input_cost_per_million=2.50,
        output_cost_per_million=10.0,
        context_window=128_000,
    ),
}


@dataclass
class LLMConfig:
    """LLM configuration."""

    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 120


def get_model_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for a model and token counts."""
    cost_info = MODEL_COSTS.get(model)
    if not cost_info:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * cost_info.input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * cost_info.output_cost_per_million

    return input_cost + output_cost
