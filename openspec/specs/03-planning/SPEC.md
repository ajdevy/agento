# Phase 3: Planning & Reflection

## Overview

Planning phase implements autonomous task decomposition, step-by-step planning, and self-reflection using LangGraph state machines.

## Objectives

1. Implement task decomposition service
2. Create planner node in LangGraph
3. Implement reflection node
4. Add error recovery and retry logic
5. Implement checkpointing

## Deliverables

### 3.1 Domain Layer

| Component | File | Description |
|-----------|------|-------------|
| Task Entity | `domain/entities/task.py` | Task with status, dependencies |
| Plan Entity | `domain/entities/plan.py` | Execution plan |

### 3.2 Services

| Component | File | Description |
|-----------|------|-------------|
| Planning Service | `domain/services/planning_service.py` | Task decomposition |
| Reflection Service | `domain/services/reflection_service.py` | Self-evaluation |
| Execution Service | `domain/services/execution_service.py` | Task execution |

### 3.3 Core Nodes

| Component | File | Description |
|-----------|------|-------------|
| Planner Node | `core/nodes.py` | Task decomposition |
| Reflector Node | `core/nodes.py` | Self-reflection |
| Executor Node | `core/nodes.py` | Task execution |

## Planning Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  PLANNING CYCLE                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐   │
│    │  PLAN   │────▶│ EXECUTE │────▶│ VERIFY  │────▶│ REFLECT │   │
│    └─────────┘     └─────────┘     └─────────┘     └────┬────┘   │
│         ▲                                                   │       │
│         │                                                   │       │
│         └───────────────────────────────────────────────────┘       │
│                      (Iteration Loop)                               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Acceptance Criteria

- [ ] Complex tasks decomposed into steps
- [ ] Dependencies identified and tracked
- [ ] Progress shown during execution
- [ ] Errors handled with retry logic
- [ ] Sessions resumable from checkpoints
- [ ] Self-reflection improves outputs

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_planning_service.py` | 95% |
| `test_reflection_service.py` | 95% |
| `test_task.py` | 100% |
| `test_plan.py` | 95% |

## Commit Structure

```
feat(domain): add task entity with dependencies
feat(domain): add plan entity
feat(services): implement planning service
feat(services): implement reflection service
feat(core): add planner node
feat(core): add reflector node
feat(core): implement checkpointing
test(services): add planning service tests
test(services): add reflection service tests
test(domain): add task entity tests
docs(specs): add planning phase specification
```

## Dependencies

- Phase 1: Foundation (completed)

## Time Estimate

35 hours / 1 week
