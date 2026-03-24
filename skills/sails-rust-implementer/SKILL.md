---
name: sails-rust-implementer
description: Use when approved Gear or Vara tasks require Rust or Sails code changes in a real workspace. Do not use when the spec or architecture is still unsettled, or when the task is only review or deployment.
---

# Sails Rust Implementer

## Overview

Implement approved tasks in Sails-first Rust workspaces without freelancing new scope.
If the task touches a released contract, preserve public routes, reply shapes, emitted events, and generated-client expectations unless the approved architecture explicitly changes them.

## Start Here

Read `../../references/sails-cheatsheet.md`, `../../references/sails-rs-imports.md`, `../../references/delayed-message-pattern.md`, `../../references/vara-domain-overview.md`, `../../references/gear-sails-production-patterns.md`, `../../references/gear-messaging-and-replies.md`, and `../../references/gear-gas-reservations-and-waitlist.md`.

Read `../../references/awesome-sails-token-patterns.md` when the task adds a fungible token, token-backed accounting, or awesome-sails token services.

Read `../../references/contract-interface-evolution.md` when the task touches a released contract, a new deployed contract version, or migration-related code.

Consume the approved `spec`, `architecture`, and `tasks` artifacts before changing code.

If the target crate explicitly builds an `ethexe` path, stop and hand back to a dedicated ethexe workflow instead of extending this standard Sails pack.

## Workflow

1. Confirm the task is already specified and architecture-approved.
2. Identify the smallest code change that satisfies the current task.
3. Match the current Sails release conventions before improvising: public service routes use `#[export]`, events use `emit_event`, and shared derives may need `#[codec(crate = sails_rs::scale_codec)]` plus `#[scale_info(crate = sails_rs::scale_info)]`.
4. Preserve released routes, reply shapes, emitted events, IDL expectations, and client-facing contract stability unless the task explicitly changes them.
5. Keep failure handling aligned with Gear/Vara async semantics.
6. Hand local verification to the gtest loop before claiming the task is done.

## Guardrails

- Do not redesign the feature while coding.
- Prefer Sails-level interfaces over raw payload work unless the task says otherwise.
- Keep constructor shape and state ownership consistent with the approved architecture instead of inventing a new storage pattern mid-implementation.
- Use generated clients or equivalent route-prefixed encoding for normal Sails calls; do not substitute bare raw structs for constructor or service payloads.
- If the feature needs a delayed self-message, use the shared payload recipe and the `msg::source() == exec::program_id()` guard pattern instead of ad hoc routing bytes.
- Preserve fail-fast command behavior; panic on fatal stateful command-path failures instead of introducing partial-commit recovery.
- Use `exec::gas_available()` for remaining-gas checks in execution paths.
- Treat value flow, replies, and async ordering as first-class behavior.
- Stop and hand back to planning if implementation uncovers a real architecture gap.
- Do not change a released public route shape in place unless the approved architecture explicitly allows it.
- Do not change a released event payload in place without explicit versioning or cutover guidance.
- Do not assume IDL regeneration alone makes a breaking interface change safe.
- Do not leave old-version write behavior undefined if the architecture requires `ReadOnly` or write-disable handling.
