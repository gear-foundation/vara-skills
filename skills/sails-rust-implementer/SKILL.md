---
name: sails-rust-implementer
description: Use when approved Gear or Vara tasks require Rust or Sails code changes in a real workspace. Do not use when the spec or architecture is still unsettled, or when the task is only review or deployment.
---

# Sails Rust Implementer

## Overview

Implement approved tasks in Sails-first Rust workspaces without freelancing new scope.
If the task touches a released contract, preserve public routes, reply shapes, emitted events, and generated-client expectations unless the approved architecture explicitly changes them.

## Inputs

- `../../references/sails-cheatsheet.md` — core Sails patterns and APIs
- `../../references/sails-rs-imports.md` — import paths for sails-rs types
- `../../references/delayed-message-pattern.md` — delayed self-message recipe
- `../../references/vara-domain-overview.md` — Vara domain context
- `../../references/gear-sails-production-patterns.md` — production patterns
- `../../references/gear-messaging-and-replies.md` — messaging and reply flows
- `../../references/gear-gas-reservations-and-waitlist.md` — gas and waitlist
- `../../references/sails-syscall-mapping.md` — `Syscall::*` API mapping (use instead of raw `gcore::*`/`msg::*`/`exec::*`)

Additional references by task type:
- Token work: `../../references/awesome-sails-token-patterns.md`
- Released contract changes: `../../references/contract-interface-evolution.md`

Consume the approved `spec`, `architecture`, and `tasks` artifacts before changing code.

If the target crate explicitly builds an `ethexe` path, stop and hand back to a dedicated ethexe workflow instead of extending this standard Sails pack.

## Workflow

1. Confirm the task is already specified and architecture-approved.
2. Identify the smallest code change that satisfies the current task.
3. Match the current Sails release conventions before improvising: public service routes use `#[export]`, events use `emit_event`, and shared types use `#[sails_type]` (expands to `Encode + Decode + TypeInfo + ReflectHash` with correct crate paths). Prefer `#[sails_type]` over manual derives for all service types, command/query params, and event payloads. Use `#[sails_type(crate = my_crate)]` when re-exporting from a different crate.
4. Preserve released routes, reply shapes, emitted events, IDL expectations, and client-facing contract stability unless the task explicitly changes them.
5. Keep failure handling aligned with Gear/Vara async semantics.
6. Hand local verification to the gtest loop before claiming the task is done.

## Guardrails

- Do not redesign the feature while coding.
- Prefer Sails-level interfaces over raw payload work unless the task says otherwise.
- Keep constructor shape and state ownership consistent with the approved architecture instead of inventing a new storage pattern mid-implementation.
- Use generated clients or equivalent route-prefixed encoding for normal Sails calls; do not substitute bare raw structs for constructor or service payloads.
- If the feature needs a delayed self-message, use the shared payload recipe and the `Syscall::message_source() == Syscall::program_id()` guard pattern instead of ad hoc routing bytes.
- Preserve fail-fast command behavior; panic on fatal stateful command-path failures instead of introducing partial-commit recovery.
- Use `Syscall::gas_available()` for remaining-gas checks in execution paths.
- Use `Syscall::*` for all runtime accessors instead of raw `gcore::*`, `msg::*`, or `exec::*` calls. Full mapping: [docs/syscall-mapping-spec.md](docs/syscall-mapping-spec.md).
- Treat value flow, replies, and async ordering as first-class behavior.
- Stop and hand back to planning if implementation uncovers a real architecture gap.
- Do not change a released public route shape in place unless the approved architecture explicitly allows it.
- Do not change a released event payload in place without explicit versioning or cutover guidance.
- Do not assume IDL regeneration alone makes a breaking interface change safe.
- Do not leave old-version write behavior undefined if the architecture requires `ReadOnly` or write-disable handling.

## `#[export]` Usage

All public service methods must be annotated with `#[export]`. For standard (non-ethexe) Sails apps, no transport flags are needed — `#[export]` enables SCALE transport by default. Transport flags (`scale`, `ethabi`, `payable`) are ethexe-specific; see the `sails-ethexe-implementer` skill for details.

