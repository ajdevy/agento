# Agento - AI Coding Assistant

Interactive CLI/TUI AI agent for code generation and DevOps automation.

## Install

```bash
pip install agento
```

## Quick Start

```bash
# Get free API key from https://openrouter.ai/keys
export OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Run - just type agento
agento
```

## Options

```bash
agento -m openrouter/free     # Use specific model
agento --no-cost             # Hide cost preview
```

## Build from Source

```bash
git clone https://github.com/ajdevy/agento.git
cd agento

# Bash (Mac/Linux)
./scripts/build.sh --dev

# Windows PowerShell
.\scripts\build.ps1 -Dev

# Or Make
make dev
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -q --cov=src/agento --cov-fail-under=95
ruff check src/agento tests/
ruff format src/agento tests/
```

## License

MIT
