---
name: sails-new-app
description: Use when a builder is starting a new standard Gear/Vara Sails app and needs the correct greenfield sequence before implementation. Do not use for edits to an established repo, Vara.eth or ethexe targets, or non-Sails templates.
---

# Sails New App

## Goal

Move a greenfield request from scope to an approved Sails workspace path without skipping the planning artifacts that later implementation depends on.

## Sequence

1. If the machine does not already have `rustup`, the required Wasm targets, `cargo-sails`, and a local `gear` binary, start with `../sails-dev-env/SKILL.md`.
2. For a new standard Sails/Vara project, bootstrap the workspace first with `cargo sails program <project-name>` unless the user explicitly needs a custom non-template layout.
3. Write the feature or app goal to `docs/plans/YYYY-MM-DD-<topic>-spec.md` using `../../assets/spec-template.md`.
4. Route architecture decisions through `../sails-architecture/SKILL.md`.
5. Keep the standard template workspace shape created by `cargo sails program <project-name>` intact: `app`, `client`, `src`, `tests`, top-level `build.rs`, Wasm output, and generated-client path.
6. Keep the standard build-script pipeline intact. In a standard Sails workspace, use the repo-generated build path for `.idl` and Rust client artifacts. For a dedicated client crate, prefer `sails-rs` with `features = ["build"]` and `sails_rs::build_client::<Program>()` before introducing manual `sails-idl-gen` / `sails-client-gen` wiring.
7. Validate before moving to later phases by finishing with `../sails-gtest/SKILL.md`, then `../sails-local-smoke/SKILL.md`.

## Shared Inputs

- `../../references/vara-domain-overview.md`
- `../../references/sails-cheatsheet.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/sails-idl-client-pipeline.md`

## Guardrails

- Keep the builder on standard Sails scaffolding and generated clients.
- Keep the standard Sails workspace shape and build-generated `.idl` and `.opt.wasm` artifact path intact, and check the crate's `build.rs` before adding ad hoc generation steps.
- Do not jump into raw Gear primitives when a Sails path already exists.
- Do not skip the planning docs just because the repo is greenfield.
- Prefer the official `cargo sails program <project-name>` bootstrap for greenfield Sails/Vara work instead of hand-assembling the workspace from scratch.
