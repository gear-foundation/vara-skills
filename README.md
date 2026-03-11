# gear-agent-skills

Canonical starter repository for curated Gear/Vara agent skills.

The first wave focuses on five orchestration skills:

- `idea-to-spec`
- `gear-architecture-planner`
- `task-decomposer`
- `sails-rust-implementer`
- `gtest-tdd-loop`

The repo also ships shared references, reusable plan templates, validation tests, and a Codex install script.

## Shared Layers

- `references/` contains agent-facing summaries of core Vara, Sails, gtest, and Vara.eth extension concepts.
- `assets/` contains canonical output shapes for spec, architecture, task-plan, and gtest artifacts.
- `scripts/` contains deterministic helper commands for install, validation, gtest execution, and parser output.

## Verification

```bash
make verify
```

This runs layout, skill-validator, skill-catalog, parser, and install tests.

## Installation

```bash
bash scripts/install-codex-skills.sh
```

## Intended Workflow

1. `idea-to-spec`
2. `gear-architecture-planner`
3. `task-decomposer`
4. `sails-rust-implementer`
5. `gtest-tdd-loop`

First-wave artifacts are written to `docs/plans/` in the consumer repository.
