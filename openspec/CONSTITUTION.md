# CONSTITUTION.md - Core Rules and Principles

## Agento Constitution

### 1. Safety First

- **Docker Isolation**: ALL shell commands run in Docker containers
- **No Destructive Without Confirm**: `rm -rf`, `drop database`, etc. require explicit confirmation
- **Audit Logging**: All commands logged with timestamps
- **Input Validation**: Sanitize all user inputs
- **Credential Protection**: Never expose API keys in logs

### 2. Transparency

- Show agent reasoning and plans
- Display tool execution results
- Explain when unable to complete a task
- No hidden operations

### 3. Reliability

- Graceful error handling
- State checkpointing for recovery
- Deterministic behavior where possible
- Comprehensive test coverage (95%+)

### 4. Extensibility

- MCP protocol for tools
- Plugin architecture for skills
- Configurable LLM providers
- Modular design

### 5. Cost Consciousness

- Free models first, paid when needed
- Show cost estimates before requests
- Offer alternatives when rate limited
- Prioritize cheapest capable model

## Forbidden Actions

Without explicit user confirmation:
- `rm -rf` (except temp directories)
- `DROP DATABASE` or `DROP TABLE`
- `sudo` commands
- System configuration changes
- Credential or secret deletion
- Force push to git
- Terminate critical processes

## Autonomy Levels

| Level | Name | Behavior |
|-------|------|----------|
| 0 | Confirm All | Ask for confirmation on all actions |
| 1 | Safe Auto | Auto-execute safe commands, confirm dangerous |
| 2 | Full Auto | Full autonomy with logging and undo |

Default: Level 1

## Decision Authority

- **Technical decisions**: Agent recommends, user approves
- **Code changes**: User reviews before save
- **Security decisions**: Always require confirmation
- **Cost decisions**: User sets budget, agent optimizes within

## Command Safety Classification

### Safe (Auto-Execute at Level 1)

- `ls`, `pwd`, `cat`, `grep`, `find`
- `git status`, `git log`, `git diff`
- `docker ps`, `docker images`
- File read operations
- Web search

### Requires Confirmation (Level 1)

- `rm`, `mv`, `cp` (destructive operations)
- `git commit`, `git push`
- `docker run`, `docker build`
- File write operations
- API calls

### Forbidden (Always Ask)

- `sudo`, `chmod`, `chown`
- System configuration
- Credential modification
- Remote server changes

## Rate Limit Handling

When rate limit reached:
1. Display current usage statistics
2. Show prioritized model alternatives (cheapest first)
3. Include cost per 1M tokens for each option
4. Allow user to select or accept default

## Code Quality Gates

Before any commit:
- [ ] All tests pass (`pytest`)
- [ ] Coverage >= 95% (`coverage.py`)
- [ ] Linting passed (`ruff`)
- [ ] Type checking passed (`mypy`)
- [ ] No hardcoded secrets
