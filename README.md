# vara-skills

`vara-skills` is a portable, self-contained skill pack for standard Gear/Vara Sails builders.

It is designed to help coding agents start from the right builder workflow, then pull the narrow Gear and Sails knowledge they need without depending on sibling repos or machine-local notes. The current public catalog is provisional and is expected to change as the eval suite identifies which candidate skills actually create uplift.

## How It Works

Each skill is a markdown file.

- `SKILL.md` is the top-level router for the pack.
- `skills/<name>/SKILL.md` is a narrower workflow or topic skill.
- `references/` is the self-contained handbook for Gear execution, Sails architecture, IDL/client generation, `gtest`, and local validation.

The pack is being narrowed toward standard Gear/Vara Sails app builders:

- preparing the local Rust and Gear toolchain
- starting a new Sails app
- building features in an existing Sails app
- reasoning about Gear message flow and execution behavior
- getting architecture, IDL/client wiring, `gtest`, and local-node validation right

## Installation

### Codex

Clone the repo and install the local skills:

```bash
git clone git@github.com:ukint-vs/vara-skills.git
cd vara-skills
bash scripts/install-codex-skills.sh
```

Then start a new Codex session and load the top-level `SKILL.md` when you want the pack router.

### Claude Code Plugin

Claude Code can install this repo directly as a plugin. You do not need a separate Claude-specific fork.

Recommended install from GitHub:

```bash
/plugin marketplace add https://github.com/ukint-vs/vara-skills
/plugin install vara-skills@vara-skills
```

If you are developing the plugin from a local checkout, run these commands from the repo root instead:

```bash
/plugin marketplace add .
/plugin install vara-skills@vara-skills
```

After local edits, reload the plugin without restarting Claude Code:

```bash
/reload-plugins
```

What Claude Code installs:

- the skill directories under `skills/`
- the same shared `references/` and `assets/` content those skills point at
- the provisional standard Gear/Vara Sails builder workflow centered on `ship-sails-app`

Important difference from Codex and OpenClaw: the repo-root `SKILL.md` is the portable pack router, but Claude Code loads plugin skills from `skills/`. In Claude Code, `ship-sails-app` is the broad entry skill that should trigger first for standard builder tasks.

### OpenClaw

Use `openclaw-skill/SKILL.md` as the wrapper entrypoint for the same pack.

## Current Skill Pack

- `sails-dev-env`
- `ship-sails-app`
- `sails-new-app`
- `sails-feature-workflow`
- `gear-message-execution`
- `sails-architecture`
- `sails-idl-client`
- `sails-gtest`
- `sails-local-smoke`

## Candidate Deep-Capability Skills

- `gear-gstd-api-map` is an installable design-time API map for `gstd`, `gcore`, and `gsys`. Use it when architecture or feature work needs to choose the right standard Gear API before dropping into debugging detail. It remains outside the top-level default router while the pack stays provisional.

## Repo Structure

- `SKILL.md` contains the top-level router.
- `skills/` contains installable skill directories.
- `references/` contains the self-contained handbook.
- `assets/` contains canonical output shapes for spec, architecture, task-plan, and gtest artifacts.
- `scripts/` contains install, validation, gtest execution, and parser helpers.

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

## Verification

```bash
make verify
```

This runs repository layout, skill-validator, skill-catalog, parser, and install tests for the current product repo surface.
It also validates the Claude packaging metadata in `.claude-plugin/`.

## Current Direction

- `vara-skills` is the product repo for the pack
- a sibling `vara-skills-evals` repo owns benchmark definitions and uplift results
- `gpt-5.4` is the first evaluation target
- the top-level router and candidate Sails-builder skills remain provisional until more targets are measured
- only measured winning skills should remain in the eventual first public pack
