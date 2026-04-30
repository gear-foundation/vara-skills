---
name: sails-ethexe-architecture
description: Use when a builder needs to design or review architecture for a Sails ethexe app with dual-transport, payable methods, Solidity interface generation, or Ethereum-style events. Do not use for standard Gear/Vara Sails apps without ethexe.
---

# Sails Ethexe Architecture

## Goal

Turn an approved spec into an ethexe-specific architecture artifact before implementation, covering transport strategy, payable design, event model, Solidity interface generation, and the constraints the ethexe feature imposes.

If the app does NOT need ethexe, use `../sails-architecture/SKILL.md` instead.

## Inputs

- `../../references/sails-ethexe-patterns.md` — ethexe diff table, transport rules, type requirements, gated syscalls
- `../../references/sails-header-wire-format.md` — interface ID stability, entry ID derivation
- `../../references/sails-idl-v2-syntax.md` — IDL v2 annotations
- `../../assets/architecture-template.md`
- `../../references/vara-domain-overview.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/gear-messaging-and-replies.md`

Write the result to `docs/plans/YYYY-MM-DD-<topic>-architecture.md`.

## Architecture Decisions Specific to Ethexe

### Transport Strategy

The architecture must name the transport per service and per method:

| Pattern | When to use |
|---------|-------------|
| Dual transport (default `#[export]`) | Methods callable from both Gear programs and EVM |
| Scale-only (`#[export(scale)]`) | Internal program-to-program calls, no EVM exposure needed |
| Ethabi-only (`#[export(ethabi)]`) | Methods only meaningful from EVM side |
| Payable (`#[export(ethabi, payable)]`) | Methods that accept value — requires ethabi |

Document the transport choice per method in the architecture artifact. Dual transport is the default but not always desirable — scale-only methods reduce the ABI surface.

### Payable Design

- Which methods accept value? Name each one.
- What happens to received value? (stored in program, forwarded, refunded on error?)
- Non-payable methods panic if value > 0 — is this acceptable for all non-payable paths?
- Constructors can also be payable — document if the program requires initial funding.

### Event Model

Decide between:
- `emit_event()` — standard Gear event (visible to Gear tooling, explorers)
- `emit_eth_event()` — Ethereum-style event (visible to EVM tooling, indexed topics)
- Both — if the same event must be visible to both ecosystems (requires two separate emissions)

For `emit_eth_event()`:
- Which fields are `#[indexed]`? (max 3 per variant, these become topics)
- Are any reserved variant names used? (forbidden list in reference)
- Is the event inventory aligned with what `sails-sol-gen` will produce in the Solidity interface?

### Solidity Interface

`sails-sol-gen` generates Solidity contract interfaces from the IDL. Architecture must consider:
- Will EVM consumers use the generated Solidity interface directly?
- Do method names, parameter types, and return types map cleanly to Solidity types?
- Are `payable` and `indexed` annotations in the IDL correct for the generated interface?

### Gated Syscalls

Three syscalls are unavailable under ethexe:
- `Syscall::signal_from()` — no signal handling
- `Syscall::signal_code()` — no signal handling
- `Syscall::system_reserve_gas()` — no system gas reservation

If the design depends on signals or system gas reservation, it cannot run under ethexe.

### Workspace Structure

Ethexe apps use a separate workspace (`rs/ethexe/` in the Sails repo). The architecture must name:
- Whether this is a new ethexe workspace or an addition to an existing one
- The dependency pattern: `sails-rs = { ..., features = ["ethexe"] }` for deps, build-deps, and dev-deps
- Whether the build script needs `features = ["ethexe", "wasm-builder"]`

## Review Checklist

- Is the transport strategy (scale/ethabi/dual) explicit per method?
- Are payable methods named, and is value handling documented?
- Is the event model clear (Gear events vs eth events vs both)?
- Are `#[indexed]` fields chosen and within the 3-field limit?
- Are there any signal or system_reserve_gas dependencies? (incompatible)
- Are service names PascalCase and free of Solidity reserved keywords?
- Is interface ID stability considered for contract evolution?
- Does the Solidity interface generation produce the expected ABI?
- Are type requirements met? (types in ethabi methods must be ABI-encodable)

## Guardrails

- If the spec is missing, stop and create it first.
- Do not design around signals or system gas reservation — they are gated out.
- Do not assume all methods need dual transport — name the strategy per method.
- Do not exceed 3 `#[indexed]` fields per event variant.
- Do not use reserved event variant names.
- Keep implementation detail out of the architecture note unless it changes the public contract.
- Route implementation to `../sails-ethexe-implementer/SKILL.md` after architecture approval.
