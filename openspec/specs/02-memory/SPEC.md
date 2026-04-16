# Phase 2: Memory System

## Overview

Memory phase implements persistent vector storage using FAISS for semantic search over conversations, code snippets, and learned patterns.

## Objectives

1. Implement FAISS vector store
2. Create embedding pipeline
3. Add memory commands
4. Implement conversation history
5. Enable cross-session memory recall

## Deliverables

### 2.1 Vector Store

| Component | File | Description |
|-----------|------|-------------|
| FAISS Store | `infrastructure/memory/faiss_store.py` | Vector storage |
| Index Manager | `infrastructure/memory/index_manager.py` | Index operations |
| Persistence | `infrastructure/memory/persistence.py` | Save/load index |

### 2.2 Embeddings

| Component | File | Description |
|-----------|------|-------------|
| Embedder | `infrastructure/memory/embedder.py` | Sentence transformer |
| Batch Processor | `infrastructure/memory/batch_processor.py` | Batch operations |
| Cache | `infrastructure/memory/cache.py` | Embedding cache |

### 2.3 Memory Domain

| Component | File | Description |
|-----------|------|-------------|
| Memory Entry | `domain/entities/memory.py` | Memory entity |
| Memory Service | `domain/services/memory_service.py` | Memory operations |

### 2.4 Commands

| Command | Description |
|---------|-------------|
| `/memory search <query>` | Semantic search |
| `/memory save` | Save current session |
| `/memory list` | Show all memories |
| `/memory forget <id>` | Delete memory |
| `/memory clear` | Clear all |

## Technical Requirements

### Dependencies

```toml
# Memory
faiss-cpu>=1.8.0
sentence-transformers>=3.0.0
numpy>=1.26.0
```

### Architecture

```
infrastructure/memory/
├── faiss_store.py      # FAISS vector store
├── embedder.py         # Embedding generation
├── index_manager.py    # Index operations
├── persistence.py      # Save/load
└── cache.py           # LRU cache
```

## Memory Types

| Type | Content | Recall Method |
|------|---------|---------------|
| Conversation | Full chat history | By date, topic |
| Code Snippets | Useful code blocks | Semantic search |
| Patterns | Learned behaviors | Context matching |
| Preferences | User settings | User ID lookup |
| Projects | Project metadata | Name, tech stack |

## Acceptance Criteria

- [ ] Vector store supports add/search/delete
- [ ] Embeddings generated correctly
- [ ] Memory persists across sessions
- [ ] Semantic search returns relevant results
- [ ] Conversation history stored
- [ ] Memory commands work

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_faiss_store.py` | 95% |
| `test_embedder.py` | 90% |
| `test_memory_service.py` | 95% |
| `test_conversation_store.py` | 90% |

## Commit Structure

```
feat(memory): implement FAISS vector store
feat(memory): add embedding pipeline
feat(memory): implement memory service
feat(domain): add memory entity
feat(commands): add memory search command
feat(commands): add memory save/list commands
test(memory): add FAISS store tests
test(memory): add embedding tests
docs(specs): add memory phase specification
```

## Dependencies

- Phase 1: Foundation (completed)

## Time Estimate

30 hours / 1 week
