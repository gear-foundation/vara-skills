---
name: sails-architecture
description: Use when a builder needs to shape or correct standard Gear/Vara Sails program and service boundaries, state ownership, or message flow. Do not use for pure deployment work, Vara.eth or ethexe targets, or non-Sails programs.
---

# Sails Architecture

## Goal

Turn an approved spec into a Sails-specific architecture artifact before implementation starts.

If the work changes a released contract or introduces a new deployed contract version, the architecture note must also define compatibility expectations for public routes, replies, events, generated clients, and off-chain consumers such as frontend and indexer.

## Inputs

- `../../assets/architecture-template.md`
- `../../references/vara-domain-overview.md`
- `../../references/sails-cheatsheet.md`
- `../../references/gear-sails-production-patterns.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/gear-gas-reservations-and-waitlist.md`
- `../../references/awesome-sails-token-patterns.md`
- `../../references/contract-interface-evolution.md`
- `../../references/sails-header-wire-format.md` — interface ID stability, entry ID derivation, route index

Write the result to `docs/plans/YYYY-MM-DD-<topic>-architecture.md`.

## Execution Model Checks

- Model deferred work with delayed messages across future blocks, not off-chain cron as the default. A program can send a delayed message to itself or another actor when it must revisit state later.
- If the design depends on future execution budget, call out reserved gas or `ReservationId` usage and duration explicitly. Reservation keeps gas available for later sends, including delayed sends, but it is not free, permanent, or a value transfer.
- Treat the Waitlist as on-chain storage for messages awaiting processing or conditions, not as a normal mempool.
- Waitlisted messages incur rent or locked-fund costs over time, can expire at a maximum duration, and cannot be prolonged indefinitely.

## Route Deeper When Needed

- If the architecture question is whether Gear or Sails exposes the right API family, review `../gear-gstd-api-map/SKILL.md` first.
- If the architecture risk is mostly around replies, timeouts, delayed work, or reservations, review `../gear-message-execution/SKILL.md`.
- If the architecture introduces a fungible token, token-backed accounting, or token-manager split, review `../../references/awesome-sails-token-patterns.md`.

## Review Checklist

- Choose explicit service boundaries.
- Explain state ownership.
- Name the program constructor shape and the chosen storage pattern instead of implying them.
- Consider routing and events.
- If work is delayed, is it block-based and allowed to self-message later?
- If future automation matters, is reservation lifetime and gas budgeting explicit?
- If messages may sit in the Waitlist, does the design account for rent, expiry, and maximum duration?
- Are `#[program]` and `#[service]` boundaries explicit?
- Are routes, replies, and events stable enough for generated clients?
- If a delayed or self-call hits a Sails route, does the design keep generated clients or equivalent route-prefixed encoding in the contract?
- Does the design account for async Gear message flow and failure paths?
- If this changes a released contract, has the design classified the change as additive or breaking, and as interface-ID-preserving or interface-ID-breaking? (See `../../references/sails-header-wire-format.md` for how interface IDs are derived.)
- Are all public methods annotated with `#[export]`?
- Are existing public routes, replies, and events preserved unless the architecture explicitly versions them?
- Does the note define contract version and status surface such as `Active` and `ReadOnly` when relevant?
- Does the design explain frontend and indexer impact for a new deployed contract version?
- If a cutover is required, does the note say how old and new versions coexist during rollout?
- If migration is required, does the note define export/import responsibilities instead of hiding them inside vague “upgrade” wording?

## Released Contract Evolution Defaults

- If the work targets an already released contract, treat public routes, reply shapes, event payloads, and generated-client expectations as compatibility-sensitive surfaces.
- Prefer additive changes such as new routes, new services, or a new deployed contract version over mutating an existing public shape in place.
- If the user is preparing a new contract version, define how the old and new versions coexist during cutover.
- If the old version must stop accepting writes, make that lifecycle explicit in the architecture note.
- If state migration is required, define the split between `V1`, `V2`, and the off-chain migrator instead of implying an in-place code swap.

## Future Migration Readiness

If the contract is expected to live beyond its first production release, the architecture note must describe how state could later be exported from `V1`.

At minimum:
- identify business-significant state stored in the program
- distinguish source-of-truth data from derived or rebuildable data
- describe whether future export would rely on full-state reads, selective state functions, or explicit export methods
- note any collections that will require deterministic chunking or canonical ordering
- state whether the contract may need a `ReadOnly` lifecycle mode in a future release

## Guardrails

- If the spec is missing, stop and create it first.
- Prefer Sails service composition over ad hoc raw Gear layering.
- Treat generated clients as the default route contract for constructor and service calls.
- Do not assume delayed automation works without future gas availability.
- Do not treat Waitlist storage as free or indefinitely prolongable.
- Keep implementation detail out of the architecture note unless it changes the public contract.
- Do not change a released public route shape in place unless the architecture explicitly treats it as a breaking change.
- Do not change a released event payload in place without explicit versioning or cutover notes.
- Do not assume IDL regeneration alone makes a breaking interface change safe.
- Do not describe Gear/Sails evolution as an in-place hot swap of live contract code.
