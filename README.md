# Agento - AI CLI/TUI Agent

CLI/TUI AI agent for code generation and DevOps automation.

## Features

- **Code Generation**: Generate and modify code in Python, Node, Rust, Go
- **DevOps**: CI/CD (GitHub Actions, GitLab CI), Docker, Kubernetes
- **Memory**: Vector-based semantic search with FAISS
- **Planning**: Autonomous task decomposition and reflection
- **Multi-Agent**: Specialized sub-agents working together
- **Skills**: MCP-based extensible plugin system
- **Spec Generation**: Auto-generate OpenSpec documentation

## Quick Start

```bash
# Install
pip install agento

# Or with Poetry
poetry add agento

# Set API key
export OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Run
agent
```

## Configuration

Create a `.env` file or set environment variables:

```bash
# Required (at least one)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Optional
DEFAULT_MODEL=openrouter/free
LOG_LEVEL=INFO
```

## Commands

| Command | Description |
|---------|-------------|
| `/code <prompt>` | Generate or modify code |
| `/devops <task>` | DevOps tasks (CI/CD, Docker, K8s) |
| `/memory search <query>` | Semantic search |
| `/plan <task>` | Create execution plan |
| `/multi <task>` | Run with multiple agents |
| `/model <action>` | Manage models |
| `/skills <action>` | Manage skills |
| `/spec <action>` | Spec generation |

## Architecture

```
src/agento/
├── ui/                    # PRESENTATION - Rich TUI
├── application/           # APPLICATION - Orchestration
├── domain/               # DOMAIN - Business logic
│   ├── entities/        # Task, Plan, Memory, Spec
│   ├── services/         # Planning, Execution
│   └── ports/           # Interfaces
├── infrastructure/       # INFRASTRUCTURE - Adapters
│   ├── llm/            # OpenRouter, DeepSeek, Gemini
│   ├── memory/          # FAISS, Conversation
│   ├── tools/           # File, Bash, Git, Docker
│   ├── mcp/            # MCP client/bridge
│   └── devops/         # GitHub Actions, GitLab CI, K8s
└── core/               # LangGraph state machine
```

## Development

```bash
# Clone
git clone https://github.com/ajdevy/agento.git
cd agento

# Install dependencies
poetry install

# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src/agento --cov-fail-under=95

# Lint
poetry run ruff check .

# Format
poetry run black .
```

## Model Configuration

Default: Free models first (cost-efficient)

```python
MODEL_ROUTING = {
    "code_generation": {
        "free": "qwen/qwen3-coder-480b-a35b:free",
        "primary": "anthropic/claude-3.5-sonnet",
        "fallback": "deepseek/deepseek-chat-v3-0324",
    },
}
```

## Docker

```bash
# Build
docker build -t agento .

# Run
docker run -it -v $(pwd):/app -e OPENROUTER_API_KEY=$OPENROUTER_API_KEY agento
```

## License

MIT
