---
name: vara-skills
description: Use when a builder needs the top-level router for the provisional standard Gear/Vara Sails skill pack across Codex, Claude, or OpenClaw. Do not use for Vara.eth or ethexe work, non-Sails programs, or broad protocol research.
---

# Vara Skills

This repository is the portable router for the provisional `vara-skills` pack.

Use `skills/ship-sails-app/SKILL.md` first when the task is about building or extending a standard Gear/Vara Sails application.

The repo is intended to be self-contained: use local `references/` handbook files before depending on sibling repositories or machine-local skill directories.

## What This Router Covers

- `Codex`: install the local skill directories with `bash scripts/install-codex-skills.sh`
- `Claude`: use the same repo content through plugin metadata
- `OpenClaw`: use the same markdown surface through the wrapper skill

## Route By Builder Intent

- Start a new Sails workspace: `skills/sails-new-app/SKILL.md`
- Add or change a feature in an existing Sails repo: `skills/sails-feature-workflow/SKILL.md`
- Rework service or program boundaries: `skills/sails-architecture/SKILL.md`
- Debug message flow, replies, delays, or reservations: `skills/gear-message-execution/SKILL.md`
- Fix `build.rs`, IDL, or generated clients: `skills/sails-idl-client/SKILL.md`
- Write or debug `gtest`: `skills/sails-gtest/SKILL.md`
- Run typed local-node smoke after green `gtest`: `skills/sails-local-smoke/SKILL.md`

## Guardrails

- This catalog is still provisional and is expected to change as `vara-skills-evals` measures uplift.
- Stay on the standard Gear/Vara Sails path for v1.
- If the task is Vara.eth or ethexe-specific, stop and use a dedicated ethexe skill instead of this pack.
