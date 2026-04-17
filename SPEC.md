# Agento Specification

## 1. Project Overview

**Project Name:** Agento
**Type:** CLI/TUI AI Coding Agent
**Core Functionality:** An interactive AI coding assistant that provides a TUI interface for code generation, DevOps automation, and autonomous task execution using LangGraph.
**Target Users:** Developers who want an AI assistant for coding tasks, CI/CD automation, and DevOps workflows.

## 2. UI/UX Specification

### Layout Structure

- **Single TUI Interface:** Interactive command-line interface
- **No subcommands:** Direct `agento` command launches TUI
- **Input/Output Pattern:** User types → AI responds → Loop continues

### Visual Design

- **Color Palette:**
  - Primary: Magenta (`#FF00FF`) for branding
  - Secondary: Cyan (`#00FFFF`) for accents
  - Success: Green (`#00FF00`) for ✓ checkmarks
  - Warning: Yellow (`#FFFF00`) for ⚠ warnings
  - Error: Red (`#FF0000`) for ✗ errors
  - Info: Blue (`#0000FF`) for ℹ info

- **Typography:** System monospace (terminal default)

- **Visual Effects:**
  - Box-drawing characters for panels
  - Rich text formatting (bold, dim, italic)
  - Markdown rendering for AI responses

### Components

- **Banner:** ASCII art header on startup
- **Input Prompt:** `> ` or `You: ` for user input
- **Markdown Output:** AI responses rendered as markdown
- **Error Messages:** Red prefixed with ✗
- **Success Messages:** Green prefixed with ✓

## 3. Functionality Specification

### Core Features

1. **Interactive TUI Chat**
   - Direct conversation with AI
   - Markdown code blocks with syntax highlighting
   - Cost estimation per request
   - Model information display

2. **Command-line Options**
   - `-m, --model`: Specify model
   - `--no-cost`: Hide cost preview
   - `--no-model`: Hide model info
   - `--version`: Show version

3. **API Key Configuration**
   - OpenRouter (recommended - free tier)
   - DeepSeek
   - Google AI (Gemini)

4. **Memory System**
   - FAISS vector store
   - Semantic search
   - Conversation history

5. **Planning & Execution**
   - Task decomposition
   - Sequential/parallel execution
   - Quality reflection

### User Interactions

1. **Start:** `agento` → Shows banner → Ready for input
2. **Chat:** Type message → Enter → AI responds
3. **Exit:** Ctrl+C or type `quit`/`exit`

### Data Handling

- API keys: Environment variables or `.env` file
- Session state: In-memory (future: persistence)
- Memory: Local FAISS index

### Edge Cases

- No API key: Show helpful error with setup instructions
- Invalid model: Fall back to default
- Network error: Show retry option
- Empty input: Ignore and prompt again

## 4. Technical Specifications

### Dependencies

- **Core:** langgraph, langchain-core, langchain-community
- **LLM:** openai, httpx
- **UI:** rich, textual, typer
- **Data:** pydantic, pydantic-settings, python-dotenv

### Entry Point

```python
# pyproject.toml
[project.scripts]
agento = "agento.main:main"
```

### Architecture

```
src/agento/
├── ui/console.py          # Rich console wrapper
├── ui/app.py              # TUI app (future)
├── main.py                # CLI entry point
├── application/
│   ├── pipeline.py        # Pipeline orchestration
│   └── agent.py           # Agent implementation
├── domain/
│   ├── services/          # Planning, Execution, Reflection
│   └── entities/          # Task, Plan, Memory
├── infrastructure/
│   ├── llm/               # OpenRouter, Router
│   ├── memory/             # FAISS, Embedder
│   └── tools/              # Bash, Git, Docker
└── core/
    ├── state.py           # AgentState
    ├── graph.py           # LangGraph
    ├── nodes.py           # Graph nodes
    └── errors.py          # Error classification
```

### Build System

- **Build Tool:** hatchling
- **Package Formats:** wheel, sdist
- **Entry Points:** `agento` CLI command

## 5. Acceptance Criteria

- [x] `agento` launches TUI interface
- [x] `agento --help` shows usage
- [x] `agento --version` shows version
- [x] No API key shows helpful error
- [x] Chat works with AI response
- [x] Markdown rendering works
- [x] Ctrl+C exits cleanly
- [x] Tests pass with 95%+ coverage
- [x] Cross-platform build scripts work
