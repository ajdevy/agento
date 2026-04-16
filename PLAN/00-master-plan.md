# AGENTO - Master Implementation Plan

**Project:** agento
**GitHub:** github.com/ajdevy/agento
**Created:** 2026-04-16

---

## Overview

Agento is a CLI/TUI AI agent for code generation and DevOps automation, built with:
- Layered architecture (SOLID/DRY principles)
- LangGraph for orchestration
- OpenRouter for LLM access (free-first)
- MCP for tool extensibility
- FAISS for vector memory
- 95%+ test coverage

---

## Quick Reference

### Architecture

```
src/agento/
├── ui/                    # PRESENTATION - Rich TUI
├── application/           # APPLICATION - Orchestration
├── domain/               # DOMAIN - Business logic (NO deps)
│   ├── entities/         # Task, Plan, Memory, Spec
│   ├── services/         # Planning, Execution
│   └── ports/            # Interfaces (LLM, Memory, Tools)
├── infrastructure/       # INFRASTRUCTURE - Adapters
│   ├── llm/             # OpenRouter, DeepSeek, Gemini
│   ├── memory/           # FAISS, Conversation
│   ├── tools/            # File, Bash, Git, Docker
│   ├── mcp/             # MCP client/bridge
│   └── devops/          # GitHub Actions, GitLab CI, K8s
└── core/                # LangGraph state machine
```

### Model Configuration (Cost-Efficient)

| Task | Free | Primary | Fallback |
|------|------|---------|----------|
| Code | qwen3-coder:free | claude-3.5-sonnet | deepseek-chat |
| DevOps | openrouter/free | claude-3.5-sonnet | deepseek-chat |
| Planning | deepseek-r1:free | claude-3.5-sonnet | openrouter/free |
| Reflection | deepseek-r1:free | claude-3.5-opus | claude-3.5-sonnet |

### Features

| Feature | Command | Phase |
|---------|---------|-------|
| Code Generation | `/code` | 1 |
| DevOps | `/devops` | 8 |
| Memory | `/memory` | 2 |
| Planning | `/plan` | 3 |
| Skills | `/skills` | 5 |
| Multi-Agent | `/multi` | 6 |
| Spec-Gen | `/spec` | 7 |
| Model Selection | `/model` | 1 |

---

## Phases

| Phase | Name | Tasks | Tests | Commits | Week |
|-------|------|-------|-------|---------|------|
| 1 | Foundation | 25 | 15 | 5 | 1 |
| 2 | Memory | 20 | 12 | 4 | 2 |
| 3 | Planning | 18 | 10 | 4 | 3 |
| 4 | Tools | 22 | 14 | 5 | 4 |
| 5 | Skills | 15 | 8 | 3 | 5 |
| 6 | Multi-Agent | 16 | 10 | 4 | 6 |
| 7 | Spec-Gen | 14 | 8 | 3 | 7 |
| 8 | DevOps | 20 | 12 | 4 | 8 |
| 9 | Colab | 10 | 6 | 2 | 9 |
| **Total** | | **160** | **95** | **34** | **9** |

---

## Detailed Phase Plans

See individual phase files:
- [PHASE-01.md](PHASE-01.md) - Foundation
- [PHASE-02.md](PHASE-02.md) - Memory
- [PHASE-03.md](PHASE-03.md) - Planning
- [PHASE-04.md](PHASE-04.md) - Tools
- [PHASE-05.md](PHASE-05.md) - Skills
- [PHASE-06.md](PHASE-06.md) - Multi-Agent
- [PHASE-07.md](PHASE-07.md) - Spec-Gen
- [PHASE-08.md](PHASE-08.md) - DevOps
- [PHASE-09.md](PHASE-09.md) - Colab

---

## OpenSpec Documentation

See `openspec/` directory:
- `AGENTS.md` - AI instructions for codebase
- `CONSTITUTION.md` - Core rules and principles
- `specs/` - Feature specifications per phase

---

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 10 GB | 50 GB |
| Python | 3.11+ | 3.11+ |
| Docker | 20.10+ | 24.0+ |

### API Keys (at least one)

- **OpenRouter** (recommended) - 100+ models
- DeepSeek - Backup
- Google AI - Gemini

---

## Testing Requirements

- **Coverage Target:** 95%+
- **Tool:** coverage.py
- **CI:** GitHub Actions with coverage gate

---

## Commit Strategy

Format: `<type>(<scope>): <description>`

Types: feat, fix, docs, test, refactor, chore, ci

Examples:
```
feat(core): initialize LangGraph state machine
feat(llm): implement OpenRouter client
test(llm): add client tests
docs(specs): add foundation specification
```

---

## Getting Started

```bash
# Clone repo
git clone https://github.com/ajdevy/agento.git
cd agento

# Install dependencies
poetry install

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Run agent
poetry run agent

# Or with Docker
docker run -it -v $(pwd):/app -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY agento
```

---

## Project Structure

```
agento/
├── src/agento/           # Source code
│   ├── ui/              # PRESENTATION
│   ├── application/     # APPLICATION
│   ├── domain/          # DOMAIN
│   ├── infrastructure/  # INFRASTRUCTURE
│   └── core/           # LangGraph
├── tests/              # 95%+ coverage
├── openspec/           # Living docs
├── PLAN/               # Phase plans
├── notebooks/          # Colab
├── docker/             # Docker setup
└── scripts/            # Utilities
```

---

## Key Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| Architecture | Layered | SOLID/DRY compliance |
| LLM | OpenRouter | 100+ models, unified API |
| Default Model | openrouter/free | 100% free |
| Coding Model | qwen3-coder:free | Best free coder |
| Shell Isolation | Docker | Security |
| Memory | FAISS | Fast vector search |
| Testing | pytest + coverage | Standard tooling |
| CI/CD | GitHub Actions | GitHub repo |

---

## Rate Limit Handling

When rate limit reached:
1. Show current usage
2. Offer model options (cheapest first)
3. Show cost per 1M tokens
4. User selects or accepts default

---

## Status

- [x] Plan created
- [ ] Phase 1: Foundation (pending)
- [ ] Phase 2: Memory (pending)
- [ ] Phase 3: Planning (pending)
- [ ] Phase 4: Tools (pending)
- [ ] Phase 5: Skills (pending)
- [ ] Phase 6: Multi-Agent (pending)
- [ ] Phase 7: Spec-Gen (pending)
- [ ] Phase 8: DevOps (pending)
- [ ] Phase 9: Colab (pending)
