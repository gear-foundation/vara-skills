# vara-skills

`vara-skills` is a portable, self-contained skill pack for standard Gear/Vara Sails builders.

It is designed to help coding agents start from the right builder workflow, then pull the narrow Gear and Sails knowledge they need without depending on sibling repos or machine-local notes. The current public catalog is provisional and is expected to change as the eval suite identifies which candidate skills actually create uplift.

## How It Works

Each skill is a markdown file.

- `SKILL.md` is the top-level router for the pack.
- `skills/<name>/SKILL.md` is a narrower workflow or topic skill.
- `references/` is the self-contained handbook for Gear execution, Sails architecture, IDL/client generation, `gtest`, local validation, voucher/signless flows, and network configuration.

The pack is being narrowed toward standard Gear/Vara Sails app builders:

- preparing the local Rust and Gear toolchain
- turning feature ideas into spec, architecture, and task artifacts
- starting a new Sails app
- building features in an existing Sails app
- implementing approved Rust or Sails changes
- reasoning about Gear message flow and execution behavior
- choosing the right `gstd` API when design depends on lower-level Gear behavior
- getting architecture, IDL or client wiring, `gtest`, and local-node validation right
- building or extending a React frontend for a standard Sails app with Sails-JS and Gear-JS
- wiring gasless (voucher) and signless (session) UX flows

## Installation

### Codex

Clone the repo and install the local skills:

```bash
git clone git@github.com:gear-foundation/vara-skills.git
cd vara-skills
bash scripts/install-codex-skills.sh
```

Then start a new Codex session and load the top-level `SKILL.md` when you want the pack router.

### Claude Code Plugin

Claude Code can install this repo directly as a plugin. You do not need a separate Claude-specific fork.

Recommended install from GitHub:

```bash
/plugin marketplace add https://github.com/gear-foundation/vara-skills
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

## Skill Catalog

### Router

- `ship-sails-app`: default entry skill for standard Gear/Vara Sails builder work. Routes the user to the next correct stage instead of jumping straight into code.

### Planning And Architecture

- `idea-to-spec`: turns a rough request into a concrete spec artifact with actors, state changes, messages, replies, events, invariants, and acceptance criteria.
- `gear-architecture-planner`: maps an approved spec onto program boundaries, service boundaries, message flow, state ownership, and client or IDL implications.
- `sails-architecture`: focuses on Sails-specific service and program boundaries, state patterns, routing, and architecture tradeoffs for standard Sails repos.
- `task-decomposer`: breaks approved spec and architecture work into dependency-ordered implementation tasks with verification checkpoints.

### Build And Implementation

- `sails-dev-env`: prepares or repairs the local Rust, Wasm, `cargo-sails`, and `gear` toolchain for standard Sails work.
- `sails-new-app`: greenfield workflow for creating a standard Sails workspace, typically starting from `cargo sails program <project-name>`, without skipping the planning artifacts.
- `sails-feature-workflow`: stage-by-stage workflow for changing behavior in an existing Sails repo.
- `sails-rust-implementer`: implements approved Rust or Sails tasks while preserving routing, IDL, and async contract behavior.
- `sails-idl-client`: fixes or wires the IDL and generated client pipeline in app, client, or test crates.
- `sails-frontend`: builds or extends a React/TypeScript frontend for a Sails app using Sails-JS, generated clients, and Gear-JS.
- `awesome-sails-vft`: adds a fungible token to a Sails app using awesome-sails building blocks, covering VFT crates, roles, events, and tests.
- `sails-program-evolution`: guides V1-to-V2 contract migration, interface evolution, and cutover planning for released Sails programs.
- `vara-wallet`: interacts with Vara Network on-chain — deploy programs, call Sails methods, manage wallets, transfer tokens, issue vouchers.

### Verification And Runtime Behavior

- `sails-gtest`: standard Sails-first `gtest` verification flow using generated clients or `GtestEnv`.
- `gtest-tdd-loop`: red-green loop for deterministic `gtest` work, using the repo scripts to capture failures and final green evidence.
- `sails-local-smoke`: typed local-node validation after `gtest` is already green.
- `gear-message-execution`: focused reasoning about replies, delays, waitlist behavior, reservations, rollback, and async execution order.

### Deep Capability Helpers

- `gear-gstd-api-map`: design-time API chooser for `gstd`, `gcore`, and `gsys` when a spec or architecture depends on exact Gear messaging or execution primitives.

### Maintenance

- `vara-skills-upgrade`: checks for new pack versions and handles inline or standalone upgrades.

## Recommended Workflows

### New app workflow

- `ship-sails-app` -> `sails-dev-env` when the machine is not ready.
- `ship-sails-app` -> `sails-new-app` to establish the greenfield path.
- For a standard new Sails/Vara project, bootstrap the workspace with `cargo sails program <project-name>` before custom wiring.
- `idea-to-spec` -> `gear-architecture-planner` or `sails-architecture` -> `task-decomposer` to create the artifact chain in `docs/plans/`.
- `sails-rust-implementer` for the approved code changes.
- `sails-idl-client` if the generated interface path needs wiring or repair.
- `sails-gtest` or `gtest-tdd-loop` for evidence-driven verification.
- `sails-local-smoke` only after green `gtest`.

### Existing feature workflow

- `ship-sails-app` -> `sails-feature-workflow` as the main router for existing Sails repos.
- `idea-to-spec` first, then `sails-architecture` for Sails-level structure.
- Add `gear-gstd-api-map` when the feature depends on exact `gstd` API choice.
- Add `gear-message-execution` when replies, delays, reservations, or timeout behavior are part of the change.
- `task-decomposer` -> `sails-rust-implementer` -> `sails-idl-client` -> `sails-gtest` or `gtest-tdd-loop`.
- `sails-local-smoke` only after the typed test loop is green.

### Verification workflow

- Use `sails-gtest` for the normal verification path.
- Use `gtest-tdd-loop` when the task must start from a failing test and produce parser-backed evidence from the repo scripts.
- Use `sails-local-smoke` only after `gtest`, not as a substitute for it.

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

This runs repository layout, skill-validator, skill-catalog, gstd-api-map, parser, install, packaging metadata, and update-check tests for the current product repo surface.

## Current Direction

- `vara-skills` is the product repo for the pack
- a sibling `vara-skills-evals` repo owns benchmark definitions and uplift results
- `gpt-5.4` is the first evaluation target
- the top-level router and candidate Sails-builder skills remain provisional until more targets are measured
- only measured winning skills should remain in the eventual first public pack
