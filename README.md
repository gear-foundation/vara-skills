# gear-agent-skills

Provisional product repository for a `vara-skills` Sails-builder pack.

The current repo is the source-of-truth workspace for a portable, markdown-first skill pack targeting Codex, Claude, and OpenClaw. The public website comes later, after the first measured skill set is finalized.

The pack is being narrowed toward standard Gear/Vara Sails app builders:

- starting a new Sails app
- building features in an existing Sails app
- getting architecture, IDL/client wiring, `gtest`, and local-node validation right

The current public catalog is provisional and is expected to change as the eval suite identifies which candidate skills actually create uplift.

## Current Candidate Skills

- `ship-sails-app`
- `sails-new-app`
- `sails-feature-workflow`
- `sails-architecture`
- `sails-idl-client`
- `sails-gtest`
- `sails-local-smoke`

## Milestone-One Evaluation

The first measured target is `gpt-5.4`.

The first full `gpt-5.4` milestone-one suite now covers `12` cases across `knowledge`, `codegen`, `workflow`, and `safety`.

That suite produced `4` uplifts, `8` ties, and `0` regressions, with `2` artifact checks still recorded as `not-run` while compile-backed codegen execution remains scaffolded.

Measured winners in this run:

- `sails-default-path`
- `gas-reservation`
- `no-low-level-bypass`
- `js-client-from-idl` (textual uplift only; artifact execution is still blocked)

Still tied or unresolved in the current pack:

- `rust-sails-compile`
- `address-format-ss58`
- `delayed-messages`
- `idl-client-path`
- `voucher-signless`
- `waitlist-rent`
- `no-key-address-hallucination`
- `sails-feature-flow`

The supporting benchmark summary lives in the sibling `vara-skills-evals` repo at `results/2026-03-11-gpt54-suite-report.md`.

## Shared Layers

- `references/` contains agent-facing summaries of core Vara, Sails, gtest, and Vara.eth extension concepts.
- `assets/` contains canonical output shapes for spec, architecture, task-plan, and gtest artifacts.
- `scripts/` contains deterministic helper commands for install, validation, gtest execution, and parser output.
- `docs/plans/` captures approved design and implementation artifacts for the pack.

## Verification

```bash
make verify
```

This runs repository layout, skill-validator, skill-catalog, parser, and install tests for the current product repo surface.

## Installation

```bash
bash scripts/install-codex-skills.sh
```

## Current Direction

- the current repo evolves into `vara-skills`
- a sibling repo `vara-skills-evals` will own benchmark definitions and uplift results
- `gpt-5.4` is the first evaluation target for the pack
- the top-level router and candidate Sails-builder skills remain provisional until more targets are measured
- only measured winning skills should remain in the eventual first public pack
