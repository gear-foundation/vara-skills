---
name: sails-architecture
description: Use when a builder needs to shape or correct standard Gear/Vara Sails program and service boundaries, state ownership, or message flow. Do not use for pure deployment work, Vara.eth or ethexe targets, or non-Sails programs.
---

# Sails Architecture

## Goal

Turn an approved spec into a Sails-specific architecture artifact before implementation starts.

## Inputs

- `../../assets/architecture-template.md`
- `../../references/vara-domain-overview.md`
- `../../references/sails-cheatsheet.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/gear-gas-reservations-and-waitlist.md`

Write the result to `docs/plans/YYYY-MM-DD-<topic>-architecture.md`.

## Execution Model Checks

- Model deferred work with delayed messages across future blocks, not off-chain cron as the default. A program can send a delayed message to itself or another actor when it must revisit state later.
- If the design depends on future execution budget, call out reserved gas or `ReservationId` usage and duration explicitly. Reservation keeps gas available for later sends, including delayed sends, but it is not free, permanent, or a value transfer.
- Treat the Waitlist as on-chain storage for messages awaiting processing or conditions, not as a normal mempool.
- Waitlisted messages incur rent or locked-fund costs over time, can expire at a maximum duration, and cannot be prolonged indefinitely.

## Route Deeper When Needed

- If the architecture question is whether Gear or Sails exposes the right API family, review `../gear-gstd-api-map/SKILL.md` first.
- If the architecture risk is mostly around replies, timeouts, delayed work, or reservations, review `../gear-message-execution/SKILL.md`.

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

## Guardrails

- If the spec is missing, stop and create it first.
- Prefer Sails service composition over ad hoc raw Gear layering.
- Treat generated clients as the default route contract for constructor and service calls.
- Do not assume delayed automation works without future gas availability.
- Do not treat Waitlist storage as free or indefinitely prolongable.
- Keep implementation detail out of the architecture note unless it changes the public contract.
