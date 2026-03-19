---
name: sails-idl-client
description: Use when a builder needs to wire or repair the standard Gear/Vara Sails IDL and generated client pipeline in app, client, or test crates. Do not use for raw payload-only testing, Vara.eth or ethexe codegen, or non-Sails repositories.
---

# Sails IDL Client

## Goal

Keep Sails builders on the typed pipeline for IDL generation, Rust client generation, and integration wiring.

## Default JS Or TS Path

- Treat the program `.idl` as the source of truth for the interface.
- Generate the normal client with `sails-js` or `sails-js-cli` so the workspace gets `lib.ts` and typed program or service classes instead of hand-written payload code.
- Pair the generated client with `GearApi` from `@gear-js/api` for node connectivity.
- Use `parseIdl` from the `sails-js` and `sails-js-parser` path only when you explicitly need dynamic runtime control rather than pre-generated files.

## Build Script Path

- Check the repo's `build.rs` before inventing a manual IDL step.
- For a dedicated Rust client crate, prefer the standard Sails build-helper path:
  - `[build-dependencies] sails-rs = { version = "...", features = ["build"] }`
  - `fn main() { sails_rs::build_client::<Program>(); }`
- If the repo needs more control over generation, use the configurable Sails path:
  - `sails_rs::ClientBuilder::<Program>::from_env().build_idl().generate()`
- Treat direct `sails-idl-gen` plus `sails-client-gen` wiring as a manual fallback for non-standard layouts or explicitly custom generation needs.
- Do not assume a single fixed output location. Depending on the repo, generated `.idl` and Rust client artifacts may land in `OUT_DIR`, the client crate output path, or another repo-defined location.

## Inputs

- `../../references/sails-cheatsheet.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../assets/task-plan-template.md`

## Route Here When

- Check `build.rs` or generation wiring when it no longer generates the expected artifacts
- the client crate drifted from program changes
- Check output paths and artifact freshness before deeper debugging
- tests are building raw payloads instead of using generated clients
- local smoke needs a typed client path

## Guardrails

- Keep generated artifacts aligned with the program contract before deeper debugging.
- Prefer generated client flows in tests and smoke runs when the workspace supports them.
- Do not treat `sails-js` as a runtime target; it is the JavaScript client library used by generated and dynamic IDL-driven flows.
- Do not replace the standard path with raw ABI, ethers-style bindings, or hand-written SCALE payloads for a standard Vara Sails app.
- Do not treat missing codegen as a reason to bypass the Sails pipeline.
- Do not document `sails-idl-gen` + `sails-client-gen` as the default dedicated-client path when the repo can use `sails-rs` build helpers.
