# Phase 5: Skills & MCP

## Overview

Skills phase implements the MCP (Model Context Protocol) integration for extensible tool/plugin system.

## Objectives

1. Integrate MCP SDK
2. Create skill registry
3. Implement dynamic skill loading
4. Add built-in skills
5. Support skill configuration

## Deliverables

### 5.1 MCP Integration

| Component | File | Description |
|-----------|------|-------------|
| MCP Client | `infrastructure/mcp/client.py` | MCP protocol client |
| MCP Bridge | `infrastructure/mcp/bridge.py` | Bridge to agent |
| MCP Server | `infrastructure/mcp/server.py` | Server for exposing tools |

### 5.2 Skill System

| Component | File | Description |
|-----------|------|-------------|
| Skill Registry | `infrastructure/skills/registry.py` | Skill management |
| Skill Loader | `infrastructure/skills/loader.py` | Dynamic loading |
| Built-in Skills | `infrastructure/skills/builtins.py` | Default skills |

### 5.3 Commands

| Command | Description |
|---------|-------------|
| `/skills list` | Show available skills |
| `/skills enable <name>` | Enable a skill |
| `/skills disable <name>` | Disable a skill |
| `/skills add <url>` | Add new MCP server |

## Built-in Skills

| Skill | MCP Server | Description |
|-------|------------|-------------|
| file_ops | Built-in | File CRUD operations |
| bash_exec | Built-in | Shell commands |
| web_search | Built-in | Internet search |
| git_ops | Built-in | Git operations |
| docker_ops | Built-in | Container management |
| github_api | @modelcontextprotocol/server-github | GitHub REST API |
| slack_notify | @modelcontextprotocol/server-slack | Slack messaging |
| database | @modelcontextprotocol/server-sqlite | SQL queries |
| http | @modelcontextprotocol/server-http | HTTP client |

## MCP Discovery

| Directory | Servers | URL |
|-----------|---------|-----|
| Smithery | 7,000+ | smithery.ai |
| PulseMCP | 11,800+ | pulsemcp.com |
| Glama | 21,000+ | glama.ai |

## Acceptance Criteria

- [ ] MCP protocol supported
- [ ] Skills can be enabled/disabled
- [ ] Dynamic skill loading works
- [ ] Built-in skills functional
- [ ] Skill configuration persists

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_mcp_client.py` | 90% |
| `test_skill_loader.py` | 95% |
| `test_registry.py` | 95% |

## Commit Structure

```
feat(mcp): implement MCP client
feat(mcp): create MCP bridge
feat(skills): implement skill registry
feat(skills): add dynamic skill loader
feat(skills): add built-in skills
feat(commands): add skills commands
test(mcp): add MCP client tests
test(skills): add registry tests
docs(specs): add skills phase specification
```

## Dependencies

- Phase 4: Tools (completed)

## Time Estimate

30 hours / 1 week
