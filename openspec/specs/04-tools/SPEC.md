# Phase 4: Tools

## Overview

Tools phase implements the core toolset including file operations, bash execution (Docker-isolated), Git operations, and web search.

## Objectives

1. Implement file operations tool
2. Create bash tool with Docker isolation
3. Add Git operations tool
4. Implement web search tool
5. Create tool registry

## Deliverables

### 4.1 Tool Base

| Component | File | Description |
|-----------|------|-------------|
| Base Tool | `infrastructure/tools/base.py` | Tool interface |
| Tool Result | `infrastructure/tools/base.py` | Result wrapper |
| Tool Registry | `infrastructure/tools/registry.py` | Tool management |

### 4.2 Tool Implementations

| Tool | File | Description |
|------|------|-------------|
| File Ops | `infrastructure/tools/file_ops.py` | CRUD operations |
| Bash | `infrastructure/tools/bash.py` | Docker-isolated execution |
| Git | `infrastructure/tools/git_ops.py` | Git operations |
| Web Search | `infrastructure/tools/web_search.py` | Search functionality |
| Docker | `infrastructure/tools/docker_ops.py` | Container management |

### 4.3 Safety

| Component | File | Description |
|-----------|------|-------------|
| Command Validator | `infrastructure/tools/validator.py` | Security checks |
| Danger Detector | `infrastructure/tools/danger.py` | Flag dangerous commands |

## Safety Features

```
┌─────────────────────────────────────────────────────────────────────┐
│  COMMAND SAFETY                                                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  SAFE (Level 1 Auto-Execute)                                         │
│  ├── ls, pwd, cat, grep, find                                       │
│  ├── git status, git log, git diff                                  │
│  ├── docker ps, docker images                                       │
│  └── npm test, cargo test, go test                                  │
│                                                                      │
│  REQUIRES CONFIRMATION                                               │
│  ├── rm, mv, cp (destructive)                                       │
│  ├── git commit, git push                                           │
│  ├── docker run, docker build                                       │
│  └── File write operations                                          │
│                                                                      │
│  FORBIDDEN (Always Ask)                                              │
│  ├── sudo, chmod, chown                                             │
│  ├── rm -rf (system)                                                │
│  ├── DROP DATABASE                                                  │
│  └── Any with --force without warning                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Acceptance Criteria

- [ ] File operations work (read/write/edit)
- [ ] Bash commands execute in Docker
- [ ] Dangerous commands detected and warned
- [ ] Git operations functional
- [ ] Web search returns results
- [ ] Tool registry works

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_file_ops.py` | 95% |
| `test_bash.py` | 90% |
| `test_git_ops.py` | 90% |
| `test_registry.py` | 95% |
| `test_validator.py` | 95% |

## Commit Structure

```
feat(tools): implement base tool interface
feat(tools): implement file operations tool
feat(tools): implement bash tool with Docker
feat(tools): implement git operations tool
feat(tools): implement web search tool
feat(tools): add command validator
feat(tools): create tool registry
test(tools): add file ops tests
test(tools): add bash tool tests
test(tools): add validator tests
docs(specs): add tools phase specification
```

## Dependencies

- Phase 1: Foundation (completed)

## Time Estimate

40 hours / 1 week
