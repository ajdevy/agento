# OpenSpec Documentation

## Overview

This directory contains the living specification for Agento.

## Structure

```
openspec/
├── AGENTS.md              # AI instructions for code
├── CONSTITUTION.md        # Core rules and principles
├── README.md             # This file
├── specs/                # Feature specifications
│   ├── 01-foundation/    # Phase 1: Core infrastructure
│   ├── 02-memory/        # Phase 2: Vector memory
│   ├── 03-planning/      # Phase 3: Task planning
│   ├── 04-tools/         # Phase 4: Tool implementations
│   ├── 05-skills/       # Phase 5: MCP/Skills
│   ├── 06-multi-agent/   # Phase 6: Multi-agent system
│   ├── 07-spec-gen/     # Phase 7: Spec generation
│   ├── 08-devops/       # Phase 8: CI/CD tools
│   └── 09-colab/        # Phase 9: Colab deployment
└── changes/              # Proposed modifications
```

## How to Use

1. **For AI Coding Assistants**: Read `AGENTS.md` for project conventions
2. **For New Features**: Check `specs/` for feature specifications
3. **For Changes**: Add proposals to `changes/` directory

## Spec Format

Each spec includes:
- Overview and objectives
- User stories and scenarios
- Technical requirements
- Acceptance criteria
- Implementation notes
