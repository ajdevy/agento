# Phase 1: Foundation

## Overview

Foundation phase establishes the core infrastructure for Agento including:
- Project setup with proper tooling
- Domain layer (entities, ports, services)
- LangGraph core state machine
- OpenRouter LLM integration
- Basic TUI interface

## Objectives

1. Create a complete, runnable agent with basic chat
2. Establish layered architecture patterns
3. Implement OpenRouter client with model routing
4. Create TUI with Rich library
5. Achieve 95%+ test coverage

## Deliverables

### 1.1 Project Setup

| Item | File | Description |
|------|------|-------------|
| Package config | `pyproject.toml` | Dependencies, metadata |
| Poetry config | `poetry.lock` | Locked dependencies |
| Linting | `.ruff.toml` | Ruff configuration |
| Formatting | `black.toml` | Black configuration |
| Type checking | `mypy.ini` | MyPy configuration |
| Env example | `.env.example` | Environment template |
| Git ignore | `.gitignore` | Git ignore patterns |

### 1.2 Domain Layer

| Entity | File | Description |
|--------|------|-------------|
| Task | `domain/entities/task.py` | Task representation |
| Plan | `domain/entities/plan.py` | Execution plan |
| Memory | `domain/entities/memory.py` | Memory entry |
| Spec | `domain/entities/spec.py` | Specification entity |

| Port | File | Description |
|------|------|-------------|
| LLM Port | `domain/ports/llm_port.py` | LLM interface |
| Memory Port | `domain/ports/memory_port.py` | Memory interface |
| Tool Port | `domain/ports/tool_port.py` | Tool interface |

### 1.3 Infrastructure Layer

| Adapter | File | Description |
|---------|------|-------------|
| OpenRouter | `infrastructure/llm/openrouter.py` | OpenRouter API client |
| Model Router | `infrastructure/llm/router.py` | Model selection |
| Rate Limiter | `infrastructure/llm/rate_limiter.py` | Rate limit handling |

### 1.4 Core Layer

| Component | File | Description |
|-----------|------|-------------|
| State | `core/state.py` | LangGraph state definition |
| Graph | `core/graph.py` | Main graph structure |
| Nodes | `core/nodes.py` | Graph nodes |
| Checkpointer | `core/checkpointer.py` | State persistence |

### 1.5 UI Layer

| Component | File | Description |
|-----------|------|-------------|
| Console | `ui/console.py` | Rich console setup |
| App | `ui/app.py` | TUI application |
| Widgets | `ui/widgets.py` | Custom widgets |

### 1.6 Application Layer

| Component | File | Description |
|-----------|------|-------------|
| Agent | `application/agent.py` | Main agent |
| Commands | `application/commands.py` | Command handler |
| Pipeline | `application/pipeline.py` | Execution pipeline |

## Technical Requirements

### Dependencies

```toml
# Core
langgraph>=0.4.0
langchain-core>=0.3.0
pydantic>=2.6.0

# LLM
openai>=1.12.0

# UI
rich>=13.7.0

# Utilities
python-dotenv>=1.0.0
httpx>=0.27.0

# Testing
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
ruff>=0.3.0
mypy>=1.9.0
```

### Architecture

```
src/agento/
├── domain/           # Pure business logic
│   ├── entities/    # Task, Plan, Memory, Spec
│   └── ports/       # Interfaces only
├── infrastructure/  # External adapters
│   └── llm/        # OpenRouter implementation
├── core/           # LangGraph
├── application/     # Orchestration
└── ui/             # TUI
```

## Acceptance Criteria

- [ ] Agent runs in terminal with TUI
- [ ] Can chat with OpenRouter models
- [ ] Model routing works correctly
- [ ] Rate limit handling implemented
- [ ] Cost preview shown before requests
- [ ] 95%+ test coverage on new code
- [ ] All linting/typing checks pass

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_state.py` | 100% |
| `test_openrouter.py` | 95% |
| `test_router.py` | 95% |
| `test_console.py` | 90% |
| `test_agent.py` | 90% |

## Commit Structure

```
feat(core): initialize LangGraph state machine
feat(llm): implement OpenRouter API client
feat(llm): add model router with cost-based selection
feat(ui): create Rich-based TUI console
feat(application): implement main agent class
test(core): add state serialization tests
test(llm): add OpenRouter client tests
test(llm): add model router tests
docs(specs): add foundation phase specification
```

## Dependencies

None (initial phase)

## Time Estimate

40 hours / 1 week
