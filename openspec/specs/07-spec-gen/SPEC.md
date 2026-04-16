# Phase 7: Spec Generation

## Overview

Spec-gen phase implements automatic OpenSpec documentation generation from agent behavior and code.

## Objectives

1. Implement OpenSpec structure generator
2. Create spec from code analyzer
3. Implement bidirectional sync
4. Add spec verification

## Deliverables

### 7.1 Generator

| Component | File | Description |
|-----------|------|-------------|
| Spec Generator | `infrastructure/spec/generator.py` | Create specs |
| Template Engine | `infrastructure/spec/templates.py` | Template rendering |
| Analyzer | `infrastructure/spec/analyzer.py` | Code analysis |

### 7.2 Sync

| Component | File | Description |
|-----------|------|-------------|
| Spec Sync | `infrastructure/spec/sync.py` | Bidirectional sync |
| Diff Engine | `infrastructure/spec/diff.py` | Spec diffing |
| Merger | `infrastructure/spec/merger.py` | Merge changes |

### 7.3 Verification

| Component | File | Description |
|-----------|------|-------------|
| Spec Verifier | `infrastructure/spec/verifier.py` | Validate specs |
| Coverage Checker | `infrastructure/spec/coverage.py` | Check coverage |
| Consistency Checker | `infrastructure/spec/consistency.py` | Verify consistency |

### 7.4 Commands

| Command | Description |
|---------|-------------|
| `/spec generate` | Generate spec for project |
| `/spec update` | Update spec from code |
| `/spec verify` | Check implementation vs spec |
| `/spec propose <feature>` | Create change proposal |
| `/spec diff <id>` | Show spec changes |

## OpenSpec Structure

```
openspec/
├── AGENTS.md              # AI instructions
├── CONSTITUTION.md        # Rules
├── specs/
│   ├── feature-name/
│   │   ├── SPEC.md       # Specification
│   │   └── scenarios/    # Test scenarios
└── changes/
    └── feature-id/
        ├── proposal.md
        ├── design.md
        └── tasks.md
```

## Spec Template

```markdown
# Feature: [Name]

## Overview
[Description]

## Requirements
- [Requirement 1]
- [Requirement 2]

## Acceptance Criteria
Given [context]
When [action]
Then [result]

## Scenarios
- src/tests/test_feature.py

## Implementation Status
- [ ] Item 1
- [ ] Item 2
```

## Acceptance Criteria

- [ ] Specs generated from code
- [ ] Code changes reflected in specs
- [ ] Spec verification works
- [ ] Change proposals functional
- [ ] Bidirectional sync working

## Test Requirements

| Test File | Coverage Target |
|-----------|----------------|
| `test_spec_generator.py` | 95% |
| `test_spec_verifier.py` | 95% |
| `test_sync.py` | 90% |

## Commit Structure

```
feat(spec): implement spec generator
feat(spec): add template engine
feat(spec): create analyzer
feat(spec): implement spec verifier
feat(spec): add bidirectional sync
feat(commands): add spec commands
test(spec): add generator tests
test(spec): add verifier tests
docs(specs): add spec-gen phase specification
```

## Dependencies

- Phase 1: Foundation (completed)

## Time Estimate

25 hours / 1 week
