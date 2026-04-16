# PHASE 1: Foundation

**Status:** Pending  
**Duration:** Week 1 (40 hours)  
**Dependencies:** None

---

## Objectives

1. Set up project with proper tooling
2. Implement domain layer (entities, ports)
3. Create LangGraph core
4. Integrate OpenRouter
5. Build basic TUI
6. Achieve 95%+ test coverage

---

## Tasks

### 1.1 Project Setup

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.1.1 | Create pyproject.toml | `pyproject.toml` | - | `chore: initialize project` |
| 1.1.2 | Set up ruff configuration | `.ruff.toml` | - | - |
| 1.1.3 | Set up black configuration | `black.toml` | - | - |
| 1.1.4 | Set up mypy configuration | `mypy.ini` | - | - |
| 1.1.5 | Create .env.example | `.env.example` | - | - |
| 1.1.6 | Create .gitignore | `.gitignore` | - | - |
| 1.1.7 | Initialize __init__.py files | `src/agento/__init__.py` | - | - |

### 1.2 Domain Entities

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.2.1 | Create Task entity | `domain/entities/task.py` | `test_task.py` | `feat(domain): add task entity` |
| 1.2.2 | Create Plan entity | `domain/entities/plan.py` | `test_plan.py` | `feat(domain): add plan entity` |
| 1.2.3 | Create Memory entity | `domain/entities/memory.py` | `test_memory.py` | `feat(domain): add memory entity` |
| 1.2.4 | Create Spec entity | `domain/entities/spec.py` | `test_spec.py` | `feat(domain): add spec entity` |

### 1.3 Domain Ports (Interfaces)

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.3.1 | Create LLM port | `domain/ports/llm_port.py` | - | `feat(domain): add LLM port` |
| 1.3.2 | Create Memory port | `domain/ports/memory_port.py` | - | `feat(domain): add memory port` |
| 1.3.3 | Create Tool port | `domain/ports/tool_port.py` | - | `feat(domain): add tool port` |

### 1.4 Infrastructure - LLM

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.4.1 | Create base LLM adapter | `infrastructure/llm/base.py` | - | `feat(llm): create base adapter` |
| 1.4.2 | Implement OpenRouter client | `infrastructure/llm/openrouter.py` | `test_openrouter.py` | `feat(llm): implement OpenRouter` |
| 1.4.3 | Implement model router | `infrastructure/llm/router.py` | `test_router.py` | `feat(llm): add model router` |
| 1.4.4 | Implement rate limiter | `infrastructure/llm/rate_limiter.py` | `test_rate_limiter.py` | `feat(llm): add rate limiter` |
| 1.4.5 | Add cost estimator | `infrastructure/llm/cost.py` | `test_cost.py` | `feat(llm): add cost estimator` |

### 1.5 Core - LangGraph

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.5.1 | Define AgentState | `core/state.py` | `test_state.py` | `feat(core): define state` |
| 1.5.2 | Create graph structure | `core/graph.py` | `test_graph.py` | `feat(core): create graph` |
| 1.5.3 | Implement nodes | `core/nodes.py` | `test_nodes.py` | `feat(core): implement nodes` |
| 1.5.4 | Add checkpointer | `core/checkpointer.py` | `test_checkpointer.py` | `feat(core): add checkpointer` |

### 1.6 UI Layer

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.6.1 | Create Rich console | `ui/console.py` | `test_console.py` | `feat(ui): create console` |
| 1.6.2 | Build TUI app | `ui/app.py` | `test_app.py` | `feat(ui): build TUI app` |
| 1.6.3 | Create widgets | `ui/widgets.py` | `test_widgets.py` | `feat(ui): create widgets` |
| 1.6.4 | Add command parser | `ui/parser.py` | `test_parser.py` | `feat(ui): add parser` |

### 1.7 Application Layer

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.7.1 | Create main agent | `application/agent.py` | `test_agent.py` | `feat(application): create agent` |
| 1.7.2 | Implement commands | `application/commands.py` | `test_commands.py` | `feat(application): implement commands` |
| 1.7.3 | Create pipeline | `application/pipeline.py` | `test_pipeline.py` | `feat(application): create pipeline` |

### 1.8 Entry Point

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 1.8.1 | Create main.py | `main.py` | - | `feat: add entry point` |
| 1.8.2 | Create config.py | `config.py` | `test_config.py` | `feat: add configuration` |

---

## Test Files

| File | Target | Type |
|------|--------|------|
| `tests/unit/domain/test_task.py` | 100% | Unit |
| `tests/unit/domain/test_plan.py` | 95% | Unit |
| `tests/unit/domain/test_memory.py` | 95% | Unit |
| `tests/unit/infrastructure/llm/test_openrouter.py` | 95% | Unit |
| `tests/unit/infrastructure/llm/test_router.py` | 95% | Unit |
| `tests/unit/infrastructure/llm/test_rate_limiter.py` | 95% | Unit |
| `tests/unit/core/test_state.py` | 100% | Unit |
| `tests/unit/core/test_graph.py` | 95% | Unit |
| `tests/unit/core/test_nodes.py` | 90% | Unit |
| `tests/unit/ui/test_console.py` | 90% | Unit |
| `tests/unit/ui/test_app.py` | 90% | Unit |
| `tests/unit/application/test_agent.py` | 90% | Unit |
| `tests/integration/test_agent.py` | 85% | Integration |

---

## Commits

```
1. chore: initialize project structure
2. feat(domain): add task entity
3. feat(domain): add plan entity  
4. feat(domain): add memory entity
5. feat(domain): add spec entity
6. feat(domain): add LLM/memory/tool ports
7. feat(llm): create base adapter
8. feat(llm): implement OpenRouter client
9. feat(llm): add model router with cost selection
10. feat(llm): add rate limiter
11. feat(llm): add cost estimator
12. feat(core): define state
13. feat(core): create graph
14. feat(core): implement nodes
15. feat(core): add checkpointer
16. feat(ui): create console
17. feat(ui): build TUI app
18. feat(ui): create widgets
19. feat(ui): add parser
20. feat(application): create agent
21. feat(application): implement commands
22. feat(application): create pipeline
23. feat: add entry point
24. feat: add configuration
25. test(domain): add entity tests
26. test(llm): add OpenRouter tests
27. test(llm): add router tests
28. test(core): add state tests
29. test(core): add graph tests
30. test(ui): add console tests
31. test(application): add agent tests
32. docs(specs): add foundation specification
33. ci: add test workflow
```

---

## Acceptance Criteria

- [ ] Agent runs in terminal with TUI
- [ ] Can chat with OpenRouter models
- [ ] Model routing works correctly
- [ ] Rate limit handling implemented
- [ ] Cost preview shown before requests
- [ ] 95%+ test coverage on new code
- [ ] All linting/typing checks pass
- [ ] All tests pass

---

## Next Phase

[PHASE-02: Memory](PHASE-02.md)
