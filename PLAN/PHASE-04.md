# PHASE 4: Tools

**Status:** Pending  
**Duration:** Week 4 (40 hours)  
**Dependencies:** Phase 1: Foundation

---

## Objectives

1. Implement file operations tool
2. Create bash tool with Docker isolation
3. Add Git operations tool
4. Implement web search tool
5. Create tool registry

---

## Tasks

### 4.1 Tool Base

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.1.1 | Create base tool | `infrastructure/tools/base.py` | `test_base.py` | `feat(tools): create base tool` |
| 4.1.2 | Create tool result | `infrastructure/tools/result.py` | - | `feat(tools): create tool result` |
| 4.1.3 | Create tool registry | `infrastructure/tools/registry.py` | `test_registry.py` | `feat(tools): create tool registry` |

### 4.2 File Operations

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.2.1 | Implement file tool | `infrastructure/tools/file_ops.py` | `test_file_ops.py` | `feat(tools): implement file tool` |
| 4.2.2 | Add path validation | `infrastructure/tools/path_validator.py` | `test_path_validator.py` | `feat(tools): add path validator` |

### 4.3 Bash Tool

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.3.1 | Create Docker executor | `infrastructure/tools/docker_executor.py` | `test_docker_executor.py` | `feat(tools): create Docker executor` |
| 4.3.2 | Add command validator | `infrastructure/tools/validator.py` | `test_validator.py` | `feat(tools): add command validator` |
| 4.3.3 | Add danger detector | `infrastructure/tools/danger.py` | `test_danger.py` | `feat(tools): add danger detector` |
| 4.3.4 | Create bash tool | `infrastructure/tools/bash.py` | `test_bash.py` | `feat(tools): create bash tool` |

### 4.4 Git Tool

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.4.1 | Implement git tool | `infrastructure/tools/git_ops.py` | `test_git_ops.py` | `feat(tools): implement git tool` |

### 4.5 Web Search

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.5.1 | Create search tool | `infrastructure/tools/web_search.py` | `test_web_search.py` | `feat(tools): create search tool` |

### 4.6 Docker Tool

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.6.1 | Create docker tool | `infrastructure/tools/docker_ops.py` | `test_docker_ops.py` | `feat(tools): create docker tool` |

### 4.7 Commands

| # | Task | File | Test | Commit |
|---|------|------|------|--------|
| 4.7.1 | Add code commands | `application/commands/code.py` | `test_code_commands.py` | `feat(commands): add code commands` |
| 4.7.2 | Add devops commands | `application/commands/devops.py` | `test_devops_commands.py` | `feat(commands): add devops commands` |

---

## Test Files

| File | Target |
|------|--------|
| `test_file_ops.py` | 95% |
| `test_bash.py` | 90% |
| `test_git_ops.py` | 90% |
| `test_registry.py` | 95% |
| `test_validator.py` | 95% |

---

## Commits

```
1. feat(tools): create base tool
2. feat(tools): create tool result
3. feat(tools): create tool registry
4. feat(tools): implement file tool
5. feat(tools): add path validator
6. feat(tools): create Docker executor
7. feat(tools): add command validator
8. feat(tools): add danger detector
9. feat(tools): create bash tool
10. feat(tools): implement git tool
11. feat(tools): create search tool
12. feat(tools): create docker tool
13. feat(commands): add code commands
14. feat(commands): add devops commands
15. test(tools): add file ops tests
16. test(tools): add bash tool tests
17. test(tools): add validator tests
18. docs(specs): add tools specification
```

---

## Acceptance Criteria

- [ ] File operations work (read/write/edit)
- [ ] Bash commands execute in Docker
- [ ] Dangerous commands detected and warned
- [ ] Git operations functional
- [ ] Web search returns results
- [ ] Tool registry works

---

## Next Phase

[PHASE-05: Skills](PHASE-05.md)
