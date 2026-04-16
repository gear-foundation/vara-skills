---
name: gear-message-execution
description: Use when a builder needs to design or debug Gear message flow, replies, delayed execution, reservations, or waitlist behavior inside a standard Gear/Vara Sails app. Do not use for Vara.eth or ethexe-first work, non-Sails repositories, or broad protocol research.
---

# Gear Message Execution

## Goal

Provide a focused local path for reasoning about message flow and execution behavior in standard Gear/Vara Sails work.

## Inputs

- `../../references/gear-execution-model.md`
- `../../references/gear-sails-production-patterns.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/gear-gas-reservations-and-waitlist.md`
- `../../references/scale-binary-decoding-guide.md`

## Route Here When

- replies, timeouts, or error replies are surprising
- delayed work spans future blocks
- reservations or waitlist behavior affect the design
- a builder is mixing raw payload handling into an otherwise standard Sails flow
- raw hex, reply bytes, event bytes, or metadata-vs-IDL decoding path is unclear
- a reply from a hardcoded non-program `ActorId` does not decode as a Sails route; route to `gear-builtin-actors` for the matching `gbuiltin_*::Response` type

## Working Model

1. Confirm what executes now versus after the next block.
2. If raw bytes are involved, classify the source first: constructor, service payload, reply, event, full state, or state-function output.
3. Determine whether the bytes are Sails-routed, plain SCALE, or metadata-driven state output.
4. Match the decoder artifact to the source: generated client or `.idl`, `ProgramMetadata`, or `state.meta.wasm`.
5. Identify whether the path is fire-and-forget, reply-driven, delayed, or reservation-backed.
6. Separate transport failure, timeout, and error reply.
7. Check whether rollback should revert local state if a send or reply path fails.
8. If the path is in tests, confirm the block-advance pattern and expected reply timing.

## Guardrails

- Treat reply, timeout, and late hook execution as distinct states.
- Keep staged payload flows paired with their commit step.
- Treat reservation duration and waitlist expiry as architecture constraints.
- Use `exec::gas_available()` when checking available gas during the current execution.
- Prefer generated Sails clients unless debugging the route or codec layer.
- If a Sails route is involved, expect route-prefixed encoding rather than a raw struct payload.
- Keep the guidance on the standard Gear/Vara Sails path.
- Prefer local repo references over external skill dependencies.
- Do not start with plain `Decode::<T>` on arbitrary bytes when a Sails route may be involved.
- Match decode artifact to source: generated client or `.idl` for standard Sails interface paths, `ProgramMetadata` for full state, and `state.meta.wasm` for state-function output.
- Treat `gear-meta` as a debugging fallback, not the first-choice default path.
