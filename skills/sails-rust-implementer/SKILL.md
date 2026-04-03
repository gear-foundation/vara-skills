---
name: sails-rust-implementer
description: "Use when approved Gear or Vara tasks require Rust or Sails code changes in a real workspace and the spec and architecture are settled. Implements approved tasks as service, program, or crate code while preserving released routes, reply shapes, and IDL expectations. Do not use when the spec or architecture is still unsettled, or when the task is only review or deployment."
---

# Sails Rust Implementer

## Overview

Implement approved tasks in Sails-first Rust workspaces without freelancing new scope. If the task touches a released contract, preserve public routes, reply shapes, emitted events, and generated-client expectations unless the approved architecture explicitly changes them.

## Inputs

- `../../references/sails-cheatsheet.md` — core Sails patterns and APIs
- `../../references/sails-rs-imports.md` — import paths for sails-rs types
- `../../references/delayed-message-pattern.md` — delayed self-message recipe
- `../../references/vara-domain-overview.md` — Vara domain context
- `../../references/gear-sails-production-patterns.md` — production patterns
- `../../references/gear-messaging-and-replies.md` — messaging and reply flows
- `../../references/gear-gas-reservations-and-waitlist.md` — gas and waitlist

Additional references by task type:
- Token work: `../../references/awesome-sails-token-patterns.md`
- Released contract changes: `../../references/contract-interface-evolution.md`

Read the approved `spec`, `architecture`, and `tasks` artifacts in `docs/plans/` before changing code. If the target crate explicitly builds an `ethexe` path, stop and hand back to a dedicated ethexe workflow.

## Workflow

1. **Confirm readiness** — verify the task has an approved spec and architecture artifact.
2. **Scope the change** — identify the smallest code change that satisfies the current task.
3. **Match Sails conventions** — apply current release patterns before improvising:

   ```rust
   // Public service route
   #[service]
   impl MyService {
       #[export]
       pub fn do_something(&mut self, input: InputType) -> OutputType {
           // emit events via emit_event
           self.emit_event(MyEvent::SomethingDone { input });
           output
       }
   }

   // Shared derives for DTOs
   #[derive(Encode, Decode, TypeInfo)]
   #[codec(crate = sails_rs::scale_codec)]
   #[scale_info(crate = sails_rs::scale_info)]
   pub struct MyDto { /* ... */ }
   ```

4. **Preserve stability** — keep released routes, reply shapes, emitted events, IDL expectations, and client-facing contracts unless the task explicitly changes them.
5. **Handle failure paths** — align failure handling with Gear/Vara async semantics; panic on fatal stateful command-path failures.
6. **Verify** — hand local verification to the gtest loop (`../sails-gtest/SKILL.md`) before claiming the task is done.

## Delayed Self-Message Pattern

When a feature needs deferred work across blocks, use the named payload-plus-guard recipe:

```rust
// Send delayed message to self
msg::send_delayed(exec::program_id(), payload, value, delay_blocks)?;

// Guard in handler
if msg::source() == exec::program_id() {
    // This is a self-scheduled call — process deferred work
}
```

See `../../references/delayed-message-pattern.md` for the full pattern.

## Guardrails

- Do not redesign the feature while coding — stop and hand back to planning if implementation uncovers a real architecture gap.
- Prefer Sails-level interfaces over raw payload work unless the task says otherwise.
- Keep constructor shape and state ownership consistent with the approved architecture.
- Use generated clients or route-prefixed encoding for normal Sails calls; do not substitute bare raw structs for payloads.
- Use `exec::gas_available()` for remaining-gas checks in execution paths.
- Treat value flow, replies, and async ordering as first-class behavior.
- Do not change a released public route shape or event payload in place without explicit versioning or cutover guidance.
- Do not assume IDL regeneration alone makes a breaking interface change safe.
- Do not leave old-version write behavior undefined if the architecture requires `ReadOnly` or write-disable handling.
