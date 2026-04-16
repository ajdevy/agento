# AGENTS.md - AI Instructions for Agento

## Project Overview

Agento is a CLI/TUI AI agent for code generation and DevOps automation, built with layered architecture and SOLID principles.

## MANDATORY RULES (Non-Negotiable)

### 1. Test Coverage: 95% Minimum

**THIS IS NOT OPTIONAL. ALL CODE MUST HAVE 95%+ COVERAGE.**

```
Configuration: pyproject.toml [tool.coverage.fail-under] min = 95
CI Gate: pytest --cov-fail-under=95
```

When implementing any feature:
1. Write unit tests FIRST
2. Run tests: `pytest --cov=src/agento --cov-fail-under=95`
3. If coverage drops below 95%, ADD MORE TESTS
4. Do NOT reduce coverage threshold

### 2. Lint After Each Implementation

**Run linting AFTER every implementation alongside test coverage.**

After completing any implementation (feature, fix, refactor):
1. Run `ruff check src/ --fix` to fix lint issues
2. Run `ruff format src/` to format code
3. Run tests: `pytest tests/ --cov=src/agento --cov-fail-under=95`
4. Verify coverage >= 95%

Do NOT skip linting - fix issues before committing.

### 3. CI Must Pass

All checks must pass before any merge:
- `pytest tests/ --cov=src/agento --cov-fail-under=95`
- `ruff check src/`
- `mypy src/`
- `black --check src/`

### 4. No Placeholder Code in Production

- Do NOT commit empty modules as placeholders
- Implement or remove - no stubs
- Exception: explicit `TODO` comments with issue reference

## Architecture

```
src/agento/
├── ui/                    # PRESENTATION LAYER - Rich TUI
├── application/           # APPLICATION LAYER - Orchestration
├── domain/               # DOMAIN LAYER - Business logic (NO external deps)
│   ├── entities/         # Task, Plan, Memory, Spec
│   ├── services/         # Planning, Execution, Reflection
│   └── ports/            # Interfaces (LLM, Memory, Tools)
├── infrastructure/       # INFRASTRUCTURE LAYER - External adapters
│   ├── llm/             # OpenRouter, DeepSeek, Gemini
│   ├── memory/           # FAISS, Conversation store
│   ├── tools/            # File, Bash, Git, Docker, Search
│   ├── mcp/             # MCP client/bridge
│   └── devops/          # GitHub Actions, GitLab CI, K8s
└── core/                # LangGraph state machine
```

## Layer Dependency Rules

1. **UI** can import: application, domain/ports, config
2. **Application** can import: domain, core, domain/ports
3. **Domain** can import: ONLY standard library
4. **Infrastructure** can import: domain/ports, domain/entities
5. **Core** can import: domain, domain/ports

## Core Principles

### SOLID Principles

- **S**: Each class/module has one reason to change
- **O**: Open for extension, closed for modification
- **L**: Subtypes can replace base types
- **I**: Many specific interfaces over one general
- **D**: Depend on abstractions, not concretions

### DRY Principles

- If code appears 3+ times, extract to shared location
- Use inheritance/composition for shared behavior
- Shared utilities go in common/ module

## Key Patterns

- LangGraph for state machine orchestration
- MCP protocol for tool extensibility
- FAISS for vector memory
- OpenRouter for unified LLM access

## Code Standards

- Type hints on ALL functions
- Docstrings on public APIs
- **Unit tests for ALL new features with 95%+ coverage**
- Linting with ruff, formatting with black
- Pydantic for data validation

## Git Workflow

- Conventional commits (feat:, fix:, docs:, test:, refactor:)
- One feature per commit
- **Tests pass AND coverage >= 95% before commit**
- **95%+ code coverage is MANDATORY - not optional**

## Model Configuration

### Priority: Free First

```python
MODEL_ROUTING = {
    "code_generation": {
        "free": "qwen/qwen3-coder-480b-a35b:free",
        "primary": "anthropic/claude-3.5-sonnet",
        "fallback": "deepseek/deepseek-chat-v3-0324",
    },
    "devops": {
        "free": "openrouter/free",
        "primary": "anthropic/claude-3.5-sonnet",
        "fallback": "deepseek/deepseek-chat-v3-0324",
    },
    "planning": {
        "free": "deepseek/deepseek-r1-0528:free",
        "primary": "anthropic/claude-3.5-sonnet",
        "fallback": "openrouter/free",
    },
    "reflection": {
        "free": "deepseek/deepseek-r1-0528:free",
        "primary": "anthropic/claude-3.5-opus",
        "fallback": "anthropic/claude-3.5-sonnet",
    },
}
```

## Rate Limit Handling

When rate limit reached:
1. Show current usage
2. Offer model switch options (prioritized by cost)
3. User selects or uses default (cheapest)

## Cost Preview

Show estimated cost before each LLM request:
- $0.00 for free models
- Estimated cost for paid models
