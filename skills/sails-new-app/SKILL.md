---
name: sails-new-app
description: Use when a builder is starting a new standard Gear/Vara Sails app and needs the correct greenfield sequence before implementation. Do not use for edits to an established repo, Vara.eth or ethexe targets, or non-Sails templates.
---

# Sails New App

## Goal

Move a greenfield request from scope to an approved Sails workspace path without skipping the planning artifacts that later implementation depends on.

## Sequence

1. If the machine does not already have `rustup`, the required Wasm targets, `cargo-sails`, and a local `gear` binary, start with `../sails-dev-env/SKILL.md`.
2. For a new standard Sails/Vara project, bootstrap the workspace first with `cargo sails new <project-name>` unless the user explicitly needs a custom non-template layout.
3. Write the feature or app goal to `docs/plans/YYYY-MM-DD-<topic>-spec.md` using `../../assets/spec-template.md`.
4. Route architecture decisions through `../sails-architecture/SKILL.md`.
5. Keep the standard template workspace shape created by `cargo sails new <project-name>` intact: `app`, `client`, `src`, `tests`, top-level `build.rs`, Wasm output, and generated-client path.
6. Keep the standard build-script pipeline intact. In a standard Sails workspace, use the repo-generated build path for `.idl` and Rust client artifacts. For a dedicated client crate, prefer `sails-rs` with `features = ["build"]` and `sails_rs::build_client::<Program>()` before introducing manual `sails-idl-gen` / `sails-client-gen` wiring.
7. Validate before moving to later phases by finishing with `../sails-gtest/SKILL.md`, then `../sails-local-smoke/SKILL.md`.

## Shared Inputs

- `../../references/vara-domain-overview.md`
- `../../references/sails-cheatsheet.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/sails-idl-client-pipeline.md`

## Troubleshooting: Broken Scaffold

If `cargo sails new <name>` fails or the `new` subcommand is not available:

1. **Verify the CLI version**: Run `cargo sails --help` and confirm the `new` subcommand exists. The older `cargo sails program` subcommand is broken in current releases (`not able to find subfolder 'templates/program'`).
2. **Reinstall with the correct version**: `cargo install sails-cli@1.0.0-beta.2 --locked`
3. **Fallback manual bootstrap** if the CLI still fails: assemble the standard workspace shape by hand:
   - `Cargo.toml` — workspace root with `resolver = "3"`, `edition = "2024"`, `rust-version = "1.91"`. Use workspace dependencies for `sails-rs`. Do NOT use a shared workspace `[dependencies]` that unifies `gstd` and `gtest` features.
   - `build.rs` — standard Sails build script (see `../../references/sails-rs-imports.md` for the current pattern).
   - `app/` — the program crate (`src/lib.rs` with `#[program]`).
   - `client/` — dedicated client crate using `sails_rs::build_client::<Program>()` in its `build.rs`.
   - `tests/` — gtest crate depending on `sails-rs` with `features = ["gtest"]` in dev-dependencies.
   - See `../../references/sails-rs-imports.md` for the full canonical layout reference.

## Guardrails

- Keep the builder on standard Sails scaffolding and generated clients.
- Keep the standard Sails workspace shape and build-generated `.idl` and `.opt.wasm` artifact path intact, and check the crate's `build.rs` before adding ad hoc generation steps.
- Do not jump into raw Gear primitives when a Sails path already exists.
- Do not skip the planning docs just because the repo is greenfield.
- Always use `cargo sails new <project-name>` for greenfield Sails/Vara work. Hand-assembled workspaces are a known source of errors: shared top-level workspaces cause Cargo feature unification to enable both `gstd` and `gtest` on `sails-rs` simultaneously, breaking the build. Older hand-scaffolded layouts also use `resolver = "2"` / `edition = "2021"` instead of the correct `resolver = "3"` / `edition = "2024"`. See `../../references/sails-rs-imports.md` for the canonical layout.
