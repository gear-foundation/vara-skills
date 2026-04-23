---
name: sails-idl-client
description: Use when a builder needs to wire or repair the standard Gear/Vara Sails IDL and generated client pipeline in app, client, or test crates. Do not use for raw payload-only testing, Vara.eth or ethexe codegen, or non-Sails repositories.
---

# Sails IDL Client

## Goal

Keep Sails builders on the typed pipeline for IDL generation, Rust client generation, and integration wiring.

If a released contract evolves or a new deployed contract version is introduced, keep the generated-client path compatible with the approved cutover plan instead of assuming one regenerated client can replace all consumers immediately.

## Default JS Or TS Path

- Treat the program `.idl` as the source of truth for the interface.
- Generate the normal client with `sails-js` or `sails-cli` so the workspace gets `lib.ts` and typed program or service classes instead of hand-written payload code.
- Pair the generated client with `GearApi` from `@gear-js/api` for node connectivity.
- Use `parseIdl` from the `sails-js` and `sails-js-parser` path only when you explicitly need dynamic runtime control rather than pre-generated files.

## Build Script Path

- Check the repo's `build.rs` before inventing a manual IDL step.
- For a dedicated Rust client crate, prefer the standard Sails build-helper path:
  - `[build-dependencies] sails-rs = { version = "...", features = ["build"] }`
  - `fn main() { sails_rs::build_client::<Program>(); }`
- Treat direct `sails-idl-gen` plus `sails-client-gen-v2` wiring as a manual fallback for non-standard layouts or explicitly custom generation needs.
- Do not assume a single fixed output location. Depending on the repo, generated `.idl` and Rust client artifacts may land in `OUT_DIR`, the client crate output path, or another repo-defined location.

## Generated Client Pitfalls

- **Custom `BTreeMap` key types**: Public IDL-facing map keys should prefer primitive or tuple types (e.g. `u64`, `(u32, u32)`, `ActorId`). Custom struct keys (e.g. `BTreeMap<Pos, V>`) may fail client-side decoding because the generated type may lack the required ordered-key traits. Stick to primitives or tuples unless generated-client support for that custom key type is confirmed.

## Released Contract Evolution

- Treat each `.idl` as the interface contract for one deployed program version.
- If a new deployed contract version changes the public surface, do not assume every consumer can switch at once.
- Keep old and new generated clients available during cutover when frontend, tests, scripts, or migration tooling still depend on the previous version.
- Regenerate clients as part of release work, but do not treat regeneration alone as compatibility validation.

## Frontend IDL Handoff

When a Sails program's IDL is consumed by a frontend in a separate workspace or repo:

- Check in an IDL snapshot in the frontend project so the frontend toolchain can build independently.
- Document the refresh command: after regenerating the IDL from the Rust workspace, copy it to the frontend snapshot location and regenerate the TypeScript client.
- If the IDL is only generated in `OUT_DIR` during Rust builds, it will not be available to the frontend at build time.

See `../../references/sails-idl-client-pipeline.md` for the canonical frontend export pattern.

## Inputs

- `../../references/sails-idl-v2-syntax.md` — IDL v2 grammar, annotations, types, service/program declarations
- `../../references/sails-header-wire-format.md` — Sails Header layout, interface/entry ID derivation, wire examples
- `../../references/sails-cheatsheet.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../assets/task-plan-template.md`
- `../../references/contract-interface-evolution.md`

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
- Do not document `sails-idl-gen` + `sails-client-gen-v2` as the default dedicated-client path when the repo can use `sails-rs` build helpers.
