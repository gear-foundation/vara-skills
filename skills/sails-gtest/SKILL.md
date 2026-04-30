---
name: sails-gtest
description: Use when a builder needs the standard Gear/Vara Sails gtest loop for feature verification, debugging, or regression coverage. Do not use for live-network-only validation, deployment-first workflows, or non-Sails programs.
---

# Sails Gtest

## Goal

Run the Sails-first test loop with generated clients and explicit `gtest` evidence before any live-node smoke step.

## Inputs

- `../../assets/gtest-report-template.md` — report format for gtest results
- `../../references/gtest-cheatsheet.md` — quick reference for gtest APIs
- `../../references/gtest-patterns.md` — common test patterns
- `../../references/sails-cheatsheet.md` — Sails patterns and APIs
- `../../references/sails-gtest-and-local-validation.md` — full gtest and validation guide
- `../../references/gear-gas-reservations-and-waitlist.md` — gas reasoning for tests
- `../../references/scale-binary-decoding-guide.md` — decoding raw reply bytes
- `../../references/sails-syscall-mapping.md` — `Syscall::*` API for gas, message, and execution context

Write the result to `docs/plans/YYYY-MM-DD-<topic>-gtest.md`.

## Expected Loop

1. Confirm the implementation target is ready for verification.
2. Use generated clients or `GtestEnv` instead of hand-built payloads where the workspace supports them.
3. If the test must go below generated clients, first decide whether the payload or reply bytes are Sails-routed, plain SCALE, or metadata-driven state output; then apply the raw mental model: `send_bytes*` returns a `MessageId`, `run_next_block` returns the `BlockRunResult`, and the reply evidence lives in the block result.
4. Pick the right `BlockRunMode` and advance blocks explicitly when replies or deferred effects depend on progression.
5. Use `run_to_block` when delayed work or timeout behavior spans multiple blocks.
6. Assert behavior, replies, events, or accounting in the test result, not just compilation.
7. Record failure mode, fix, and passing command output in the gtest note.
8. Route to `../sails-local-smoke/SKILL.md` only after the suite is green.

## Common Pitfalls

- **Program balance accounting in gtest**: The deployed program account has an existential deposit. Absolute balance assertions like `== wager` or `== 0` will fail even when the contract accounting logic is correct. Capture the initial balance after deploy and assert deltas relative to that baseline:
  ```rust
  let initial_balance = env.balance_of(program_id);
  // ... perform actions ...
  let final_balance = env.balance_of(program_id);
  assert_eq!(final_balance - initial_balance, expected_delta);
  ```

- **Missing block advancement**: Forgetting to call `run_next_block` after sending a message means the reply is never processed. Always advance at least one block after send operations that expect replies.

## Guardrails

- Do not use green `cargo test` output without Sails-appropriate assertions as proof.
- Do not start local-node smoke while `gtest` is still red.
- Do not skip gas or value reasoning when tests depend on it.
- Do not decode raw reply or event bytes as a bare business DTO until you have checked whether Sails routing framing is present.
- Use `#[sails_type]` for test-only types that mirror service types, ensuring encoding/decoding matches on-chain behavior exactly.
