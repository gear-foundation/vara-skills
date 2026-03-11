# AGENTS.md

## Purpose
This repository packages reusable Gear/Vara skill definitions, shared references, and validation scripts for Codex-compatible agents.

## Working Rules
- Use `writing-skills` before creating or editing any skill in `skills/`.
- Apply TDD to repository behavior: add or update tests before changing scripts, validation logic, or published skill contracts.
- Keep each skill directory flat and include `SKILL.md`, `assets/`, `references/`, and `scripts/`.
- Prefer shared repository references in `references/` and shared templates in `assets/`; skill files may reference them via relative paths.
- Do not embed machine-specific absolute paths in published docs or skills unless the file is an explicit local validation target.

## Verification
- Run `make verify` before claiming the repo is ready.
- Keep installation working through `scripts/install-codex-skills.sh`.
