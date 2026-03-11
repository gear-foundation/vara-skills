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

- Check the repo's `build.rs` before inventing a manual IDL step. In the Sails examples, `cargo build` often refreshes generation because `build.rs` calls helpers such as `sails_rs::build_client::<Program>()`, `ClientBuilder::<Program>::from_env().build_idl().generate()`, or `sails_idl_gen::generate_idl_to_file::<Program>(...)`.
- Do not assume a single fixed output location. Depending on the repo, the generated `.idl` may land in the crate directory, a binpath-derived Wasm sibling path, or `OUT_DIR`.

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
