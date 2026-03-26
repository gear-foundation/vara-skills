# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A portable, self-contained skill pack for Gear/Vara Sails smart contract builders. It ships as markdown skills, shared reference docs, and validation tooling — packaged for Claude Code (plugin), Codex, and OpenClaw.

Current version: **1.3.1**. The skill catalog is provisional until the sibling `vara-skills-evals` repo proves uplift.

## Commands

```bash
make verify          # Run the full validation suite (layout, skills, parser, install, packaging, update)
make test-layout     # Repo structure checks only
make test-skills     # Skill validation + catalog + gstd-api-map tests
make test-parser     # gtest output parser tests
make test-install    # Codex install script tests
make test-packaging  # Claude plugin metadata validation
make test-update     # Auto-update check script tests
```

All tests are Python 3 (`python3 tests/<file>.py`). No pip dependencies required.

## Architecture

### Content layers

- **`SKILL.md`** (root) — top-level router that dispatches by builder intent to specific skills
- **`skills/<name>/SKILL.md`** — individual workflow or topic skills (20 total), each may contain `assets/` subdirs
- **`references/`** — self-contained handbook covering Gear execution, Sails architecture, IDL/client pipeline, gtest patterns, and more. Skills reference these via relative paths.
- **`assets/`** — canonical output templates (spec, architecture, task-plan, gtest report)
- **`VERSION`** — single-line version file, kept in sync with `marketplace.json`
- **`bin/vara-skills-update-check`** — bash script that checks for new versions on each skill invocation. State cached in `~/.vara-skills/` (cache, snooze, upgrade marker). Controlled via env vars: `VARA_SKILLS_UPDATE_CHECK=false` to disable, `VARA_SKILLS_AUTO_UPGRADE=true` for silent upgrades.

### Packaging surfaces

- **Claude Code plugin**: `.claude-plugin/plugin.json` + `marketplace.json` define the plugin. Skills under `skills/` are loaded directly.
- **Codex**: `scripts/install-codex-skills.sh` installs skill directories locally.
- **OpenClaw**: `openclaw-skill/SKILL.md` wraps the same content.

### Validation

- `scripts/validate-skill.py` — validates individual skill structure
- `scripts/parse_test_output.py` — parses gtest output for evidence collection
- `scripts/run_gtest.sh` — runs gtest and captures output
- `tests/` — Python test suite covering repo layout, skill contracts, catalog completeness, parser correctness, install scripts, and Claude packaging metadata

## Working Rules (from AGENTS.md)

- Run `make verify` before claiming the repo is ready.
- Apply TDD: add or update tests before changing scripts, validation logic, or published skill contracts.
- Keep each skill directory flat with `SKILL.md` plus optional `assets/`, `references/`, `scripts/`.
- Prefer shared references in `references/` and templates in `assets/` over duplicating content in skills.
- The skill catalog is provisional — only measured winning skills should remain in the eventual public pack.
- Stay on the standard Gear/Vara Sails path. Vara.eth and ethexe work uses dedicated skills, not this pack.

## Skill Routing

`ship-sails-app` is the primary entry skill for Claude Code. It routes standard builder tasks to the correct stage:

1. **Planning**: `idea-to-spec` → `gear-architecture-planner` or `sails-architecture` → `task-decomposer`
2. **Implementation**: `sails-rust-implementer`, `sails-idl-client`
3. **Verification**: `sails-gtest` or `gtest-tdd-loop` → `sails-local-smoke` (only after green gtest)
