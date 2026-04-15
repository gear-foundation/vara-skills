---
name: ship-sails-app
description: Use when a builder needs the top-level router for a standard Gear/Vara Sails app workflow from spec through gtest and local smoke. Do not use for Vara.eth or ethexe work, raw gstd-only programs, or non-Sails tasks.
---

## Preamble (run first)

```bash
_VS_DIR=""
for _d in \
  "${VARA_SKILLS_DIR:-}" \
  "$HOME/.claude/skills/vara-skills" \
  ".claude/skills/vara-skills" \
  "$HOME"/.claude/plugins/cache/vara-skills/vara-skills/*; do
  if [ -n "$_d" ] && [ -f "$_d/bin/vara-skills-update-check" ]; then
    _VS_DIR="$_d"; break
  fi
done
if [ -n "$_VS_DIR" ]; then
  export VARA_SKILLS_DIR="$_VS_DIR"
  _UPD=$("$_VS_DIR/bin/vara-skills-update-check" 2>/dev/null || true)
  [ -n "$_UPD" ] && echo "$_UPD" || true
fi
```

If output shows `UPGRADE_AVAILABLE <old> <new>`: read `../vara-skills-upgrade/SKILL.md` and follow the "Inline upgrade flow" (auto-upgrade if configured, otherwise ask user with 3 options, write snooze if declined). If `JUST_UPGRADED <from> <to>`: tell user "Running vara-skills v{to} (upgraded from v{from})!" and continue.

# Ship Sails App

## Role

Use this as the first stop for the provisional Sails-builder pack. Route the builder by repo state and next required artifact, then hand off to the narrower skill.

## Local Handbook

- `../../references/gear-execution-model.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/gear-gas-reservations-and-waitlist.md`
- `../../references/sails-rs-imports.md`
- `../../references/delayed-message-pattern.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../references/sails-gtest-and-local-validation.md`
- `../../references/scale-binary-decoding-guide.md`
- `../../references/voucher-and-signless-flows.md`

## Standard Defaults

- Start with Sails for standard Vara work, not raw low-level `gstd`. Use `sails-rs 0.10.3` as the current baseline unless the target repo already pins a different version. If the repo uses `1.0.0-beta+`, see the `sails-beta` branch of this pack.
- In standard Sails repos, `cargo build` runs `build.rs`: program or wasm crates usually call `sails_rs::build_wasm()`, while the repo may also emit `.idl` and typed client outputs from that same build flow.
- For dedicated Rust client crates, prefer `sails-rs = { version = "...", features = ["build"] }`
  with `sails_rs::build_client::<Program>()`.
- Treat direct `sails-client-gen` and `sails-idl-gen` wiring as a manual pipeline for explicitly non-standard repo layouts.
- In `#[program]`, public constructors return `Self`; name that constructor shape and the chosen state ownership pattern explicitly in planning artifacts.
- In `#[service]`, only methods tagged with `#[export]` are public Sails routes. Event-producing paths should use `emit_event`.
- Standard Vara account addresses are Substrate `SS58` addresses, not Ethereum `0x` addresses. Local tooling commonly uses Vara prefix `137`.
- Treat the program `.idl` as the source of truth. The normal JS or TS path is `sails-js` or `sails-js-cli` plus `GearApi`, generating outputs such as `lib.ts` and typed program or service classes. Use `parseIdl` only for an explicitly dynamic runtime path.
- For normal Sails constructor or service calls, generated clients or equivalent route-prefixed encoding are the default path; do not model the payload as a bare raw struct.
- If shared DTO derives or event derives start failing in a standard Sails crate, check the `#[codec(crate = sails_rs::scale_codec)]` and `#[scale_info(crate = sails_rs::scale_info)]` pattern before deeper debugging.
- Deferred work uses delayed messages measured in blocks. A program can send a delayed message to itself or another actor. If the flow needs gas to survive across blocks, use reserved gas or `ReservationId`; reservation duration is bounded and is not a value top-up.
- For delayed self-messages, use the named payload-plus-guard recipe in `../../references/delayed-message-pattern.md` instead of inventing a one-off byte layout.
- If the flow checks remaining execution budget, use `exec::gas_available()`.
- For gasless and signless UX patterns (vouchers, sessions, EZ-transactions), see `../../references/voucher-and-signless-flows.md`.
- For local validation, use dev accounts or user-provided `SS58` addresses, keep seed phrases and private keys out of commit-ready examples, and do not invent program IDs, voucher IDs, or account addresses.
- Check the repo's `build.rs` before inventing manual generation commands.
  Prefer this order:
  1. `sails_rs::build_client::<Program>()`
  2. explicit `sails_idl_gen::generate_idl_to_file::<Program>(...)` plus `ClientGenerator::from_idl_path(...)`
- For binary decoding questions, match the decoder to the source: generated client or `.idl` for standard Sails interface paths, `ProgramMetadata` for full state, and `state.meta.wasm` for state-function output. Use plain `Decode::<T>` only when the bytes are known to be a bare SCALE payload.

## Greenfield Bootstrap

- For a new Sails/Vara project from scratch, prefer the official template bootstrap:
  `cargo sails new <project-name>`.
- This creates the standard workspace layout with `app`, `client`, `src`, `tests`, top-level `build.rs`, and baseline Cargo wiring.
- For an existing repository, follow the repo’s current layout instead of re-bootstrapping it through the CLI template.

## Route By Situation

- Missing local Rust toolchains, Wasm targets, `cargo-sails`, or the `gear` binary: `../sails-dev-env/SKILL.md`
- No repo or greenfield workspace request: `../sails-new-app/SKILL.md`
- Existing Sails repo with feature or behavior change: `../sails-feature-workflow/SKILL.md`
- Confusion about `#[program]`, `#[service]`, state, or service boundaries: `../sails-architecture/SKILL.md`
- Need to reason about replies, delays, timeouts, reservations, or waitlist behavior: `../gear-message-execution/SKILL.md`
- Broken `build.rs`, missing IDL, or generated client drift: `../sails-idl-client/SKILL.md`
- Need to author or debug `gtest`: `../sails-gtest/SKILL.md`
- `gtest` is green and the next step is a typed live-node smoke run: `../sails-local-smoke/SKILL.md`
- Need to add a fungible token or token-backed accounting layer with awesome-sails: `../awesome-sails-vft/SKILL.md`
- Need a frontend for a Sails app (new or existing project without one): `npx create-vara-app <name> --idl <idl-path>`, then `../sails-frontend/SKILL.md` for customization
- Need to extend or repair an existing React or TypeScript frontend: `../sails-frontend/SKILL.md`
- Raw hex, reply-byte ambiguity, event decoding confusion, or metadata-vs-IDL uncertainty: `../gear-message-execution/SKILL.md`

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
