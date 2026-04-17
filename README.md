# Agento - AI Coding Assistant

A CLI/TUI AI agent for code generation and DevOps automation with LangGraph.

## Features

- **TUI Interface**: Interactive chat interface - just type `agento` to start
- **Code Generation**: Generate and modify code in Python, Node, Rust, Go
- **DevOps**: CI/CD (GitHub Actions, GitLab CI), Docker, Kubernetes
- **Memory**: Vector-based semantic search with FAISS
- **Planning**: Autonomous task decomposition and reflection
- **Multi-Agent**: Specialized sub-agents working together
- **Skills**: MCP-based extensible plugin system

## Quick Start

### 1. Get an API Key

Get a free API key from [OpenRouter](https://openrouter.ai/keys) (recommended) or set one of:

```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxx
DEEPSEEK_API_KEY=your-key
GOOGLE_API_KEY=your-key
```

### 2. Install

```bash
# From PyPI
pip install agento

# Or from source
git clone https://github.com/ajdevy/agento.git
cd agento
pip install -e .
```

### 3. Run

```bash
# Just run - launches TUI
agento

# With specific model
agento -m openrouter/free

# Hide cost preview
agento --no-cost
```

## Build Instructions

### Prerequisites

- Python 3.11+
- pip

### Option 1: Bash Script (macOS/Linux)

```bash
# Development mode
./scripts/build.sh --dev

# Run tests
./scripts/build.sh --test

# Build packages
./scripts/build.sh --package

# Install globally
./scripts/build.sh --install
```

### Option 2: PowerShell (Windows)

```powershell
# Development mode
.\scripts\build.ps1 -Dev

# Run tests
.\scripts\build.ps1 -Test

# Build packages
.\scripts\build.ps1 -Package

# Install globally
.\scripts\build.ps1 -Install
```

### Option 3: Make (Cross-platform)

```bash
make help        # Show all targets
make dev         # Dev environment (install + test)
make test        # Run tests
make lint        # Run linters
make format      # Format code
make build       # Build packages
make clean       # Clean artifacts
make all         # Full CI pipeline
```

### Option 4: Manual

```bash
# Clone
git clone https://github.com/ajdevy/agento.git
cd agento

# Create venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install
pip install -e ".[dev]"

# Run tests
pytest tests/ -q --cov=src/agento --cov-fail-under=95

# Run
agento
```

## Configuration

Create a `.env` file:

```bash
# Required (at least one)
OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Optional
DEFAULT_MODEL=openrouter/free
LOG_LEVEL=INFO
AUTONOMY_LEVEL=1
```

## Architecture

```
src/agento/
├── ui/                    # PRESENTATION - Rich TUI
├── application/           # APPLICATION - Orchestration
├── domain/               # DOMAIN - Business logic
│   ├── entities/        # Task, Plan, Memory, Spec
│   ├── services/         # Planning, Execution, Reflection
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
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -q --cov=src/agento --cov-fail-under=95

# Lint
ruff check src/agento tests/

# Format
ruff format src/agento tests/
black src/agento tests/

# Type check
mypy src/agento
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
