---
name: sails-ethexe-implementer
description: Use when approved tasks require Rust code changes in a Sails ethexe workspace with the ethexe feature enabled. Do not use for standard Gear/Vara Sails apps without ethexe, or when the spec or architecture is still unsettled.
---

# Sails Ethexe Implementer

## Overview

Implement approved tasks in Sails ethexe workspaces where the `ethexe` feature is enabled and methods may be exported via ethabi transport, accept value (payable), or emit Ethereum-style events.

If the task does NOT need the ethexe feature, use `../sails-rust-implementer/SKILL.md` instead.

## Inputs

- `../../references/sails-ethexe-patterns.md` — ethexe diff table, type requirements, transport rules, event patterns
- `../../references/sails-syscall-mapping.md` — `Syscall::*` API (note gated syscalls)
- `../../references/sails-cheatsheet.md` — core Sails patterns
- `../../references/sails-rs-imports.md` — import paths
- `../../references/sails-idl-v2-syntax.md` — IDL v2 annotations
- `../../references/sails-header-wire-format.md` — Sails Header routing

Consume the approved `spec`, `architecture`, and `tasks` artifacts before changing code.

## Workflow

1. Confirm the task is specified and architecture-approved.
2. Confirm the crate has `sails-rs` with `features = ["ethexe"]` in `Cargo.toml`.
3. Identify the smallest code change that satisfies the task.
4. Use `#[sails_type]` for all custom types. Types used in ethabi-exported methods must also be ABI-encodable as Solidity tuples (`SolValue`).
5. Choose the correct transport per method:
   - `#[export]` — both scale + ethabi (default with ethexe)
   - `#[export(scale)]` — scale only, no ethabi
   - `#[export(ethabi)]` — ethabi only
   - `#[export(ethabi, payable)]` — ethabi with value acceptance
6. Use `emit_eth_event()` for Ethereum-style events, `emit_event()` for standard Gear events. Do not mix them on the same event type without explicit architecture guidance.
7. Mark `#[indexed]` on up to 3 event fields per variant for Ethereum topic indexing.
8. Use `Syscall::*` for runtime accessors. Three syscalls are unavailable: `signal_from`, `signal_code`, `system_reserve_gas`.
9. Hand verification to the gtest loop before claiming done.

## Transport Decision Guide

| Scenario | Attribute |
|----------|-----------|
| Standard method, both transports | `#[export]` |
| Method only callable from Gear programs (no EVM) | `#[export(scale)]` |
| Method only callable from EVM | `#[export(ethabi)]` |
| Method that accepts value from EVM | `#[export(ethabi, payable)]` or `#[export(scale, ethabi, payable)]` |
| Query (read-only) | `#[export]` (transport flags orthogonal to query semantics) |

## Payable Methods

Non-payable methods panic at runtime if `msg::value() > 0`. To accept value:

```rust
#[export(payable)]
pub fn deposit(&mut self) -> u64 {
    let value = Syscall::message_value();
    // handle deposit...
    value as u64
}
```

Constructors can also be payable: `#[export(payable)] pub fn create() -> Self { ... }`

## Eth Events

```rust
#[event]
pub enum MyEvent {
    Transfer {
        #[indexed]
        from: ActorId,
        #[indexed]
        to: ActorId,
        value: u64,
    },
    Paused,
}

// In service method:
self.emit_eth_event(MyEvent::Transfer { from, to, value });
```

- Max 3 `#[indexed]` fields per variant
- Forbidden variant names: ExecutableBalanceTopUpRequested, Message, MessageQueueingRequested, Reply, ReplyQueueingRequested, StateChanged, ValueClaimed, ValueClaimingRequested

## Guardrails

- Do not use `signal_from()`, `signal_code()`, or `system_reserve_gas()` — they are gated out under ethexe.
- Do not use raw `gcore::*`, `msg::*`, or `exec::*` calls — use `Syscall::*`.
- Do not mark more than 3 fields as `#[indexed]` per event variant.
- Do not use reserved event variant names.
- Do not assume `payable` works with scale-only transport — it requires ethabi.
- Service names must be PascalCase and must not collide with Solidity reserved keywords.
- Preserve released routes, reply shapes, and events unless the task explicitly changes them.
- Use `Syscall::message_source() == Syscall::program_id()` for self-message guards.
- Hand verification to the gtest loop before claiming done.
