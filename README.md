# Agento - AI Coding Assistant

Interactive CLI/TUI AI agent for code generation and DevOps automation.

## Install from Source

```bash
git clone https://github.com/ajdevy/agento.git
cd agento
pip install -e .
```

## Setup

```bash
# Get free API key from https://openrouter.ai/keys
export OPENROUTER_API_KEY=sk-or-v1-xxxxx

# Run
agento
```

## Options

```bash
agento -m openrouter/free     # Use specific model
agento --no-cost             # Hide cost preview
```

## Build

```bash
# Bash (Mac/Linux)
./scripts/build.sh --dev

# Windows PowerShell
.\scripts\build.ps1 -Dev

# Or Make
make dev
```

## Development

```bash
pytest tests/ -q --cov=src/agento --cov-fail-under=95
ruff check src/agento tests/
```

## License

MIT