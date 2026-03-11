---
name: gear-message-execution
description: Use when a builder needs to design or debug Gear message flow, replies, delayed execution, reservations, or waitlist behavior inside a standard Gear/Vara Sails app. Do not use for Vara.eth or ethexe-first work, non-Sails repositories, or broad protocol research.
---

# Gear Message Execution

## Goal

Provide a focused local path for reasoning about message flow and execution behavior in standard Gear/Vara Sails work.

## Inputs

- `../../references/gear-execution-model.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/gear-gas-reservations-and-waitlist.md`

## Route Here When

- replies, timeouts, or error replies are surprising
- delayed work spans future blocks
- reservations or waitlist behavior affect the design
- a builder is mixing raw payload handling into an otherwise standard Sails flow

## Working Model

1. Confirm what executes now versus after the next block.
2. Identify whether the path is fire-and-forget, reply-driven, delayed, or reservation-backed.
3. Separate transport failure, timeout, and error reply.
4. Check whether rollback should revert local state if a send or reply path fails.
5. If the path is in tests, confirm the block-advance pattern and expected reply timing.

## Guardrails

- Treat reply, timeout, and late hook execution as distinct states.
- Keep staged payload flows paired with their commit step.
- Treat reservation duration and waitlist expiry as architecture constraints.
- Prefer generated Sails clients unless debugging the route or codec layer.
- Keep the guidance on the standard Gear/Vara Sails path.
- Prefer local repo references over external skill dependencies.
