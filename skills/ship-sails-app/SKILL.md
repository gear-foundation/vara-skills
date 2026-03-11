---
name: ship-sails-app
description: Use when a builder needs the top-level router for a standard Gear/Vara Sails app workflow from spec through gtest and local smoke. Do not use for Vara.eth or ethexe work, raw gstd-only programs, or non-Sails tasks.
---

# Ship Sails App

## Role

Use this as the first stop for the provisional Sails-builder pack. Route the builder by repo state and next required artifact, then hand off to the narrower skill.

## Local Handbook

- `../../references/gear-execution-model.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/gear-gas-reservations-and-waitlist.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../references/sails-gtest-and-local-validation.md`

## Standard Defaults

- Start with Sails for standard Vara work, not raw low-level `gstd`. In standard Sails repos, `cargo build` runs `build.rs`: program or wasm crates usually call `sails_rs::build_wasm()`, while the repo may also emit `.idl` and typed client outputs from that same build flow.
- Standard Vara account addresses are Substrate `SS58` addresses, not Ethereum `0x` addresses. Local tooling commonly uses Vara prefix `137`.
- Treat the program `.idl` as the source of truth. The normal JS or TS path is `sails-js` or `sails-js-cli` plus `GearApi`, generating outputs such as `lib.ts` and typed program or service classes. Use `parseIdl` only for an explicitly dynamic runtime path.
- Deferred work uses delayed messages measured in blocks. A program can send a delayed message to itself or another actor. If the flow needs gas to survive across blocks, use reserved gas or `ReservationId`; reservation duration is bounded and is not a value top-up.
- Gasless flows use vouchers so a sponsor covers gas and fees for scoped interactions; the chain is not simply free. Signless flows add a temporary delegated account, sub-account, or session for the app. Prefer existing frontend tooling such as EZ-transactions or signless or gasless hooks.
- For local validation, use dev accounts or user-provided `SS58` addresses, keep seed phrases and private keys out of commit-ready examples, and do not invent program IDs, voucher IDs, or account addresses.
- Check the repo's `build.rs` before inventing manual generation commands. Common patterns in `../sails` include `sails_rs::build_client::<Program>()`, `ClientBuilder::<Program>::from_env().build_idl().generate()`, or explicit `sails_idl_gen::generate_idl_to_file::<Program>(...)`.

## Route By Situation

- No repo or greenfield workspace request: `../sails-new-app/SKILL.md`
- Existing Sails repo with feature or behavior change: `../sails-feature-workflow/SKILL.md`
- Confusion about `#[program]`, `#[service]`, state, or service boundaries: `../sails-architecture/SKILL.md`
- Need to reason about replies, delays, timeouts, reservations, or waitlist behavior: `../gear-message-execution/SKILL.md`
- Broken `build.rs`, missing IDL, or generated client drift: `../sails-idl-client/SKILL.md`
- Need to author or debug `gtest`: `../sails-gtest/SKILL.md`
- `gtest` is green and the next step is a typed live-node smoke run: `../sails-local-smoke/SKILL.md`

## Required Artifact Chain

Keep the builder on this document chain inside `docs/plans/`:

`YYYY-MM-DD-<topic>-spec.md -> ...-architecture.md -> ...-tasks.md -> ...-gtest.md`

Use shared templates from:

- `../../assets/spec-template.md`
- `../../assets/architecture-template.md`
- `../../assets/task-plan-template.md`
- `../../assets/gtest-report-template.md`

## Routing Reminder

- Route to the new-app path when the builder is starting from scratch.
- Mention later architecture, `gtest`, and local-node validation so the builder sees the full Sails path instead of just the first step.

## Guardrails

- Treat this as a candidate first-wave catalog, not a frozen public taxonomy.
- Keep the flow standard Gear/Vara Sails only.
- If the task jumps straight to deployment or a live network without green `gtest`, redirect to testing first.
