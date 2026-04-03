---
name: sails-gtest
description: "Use when a builder needs the standard Sails-first gtest verification loop — writing, running, or debugging gtest tests with generated clients and GtestEnv, verifying feature behavior, regression coverage, and reply or event assertions before local-node smoke. Do not use for live-network-only validation, deployment-first workflows, or non-Sails programs."
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

Write the result to `docs/plans/YYYY-MM-DD-<topic>-gtest.md`.

## Workflow

1. **Confirm readiness** — verify the implementation target is ready for verification.
2. **Set up the test environment** — use generated clients or `GtestEnv`:

   ```rust
   use sails_rs::gtest::calls::*;

   let env = GtestEnv::new(WASM_BINARY_PATH)?;
   let mut program = MyProgram::new(env.gear_remoting());
   // Deploy with constructor
   let program_id = program.new(init_args).send_recv(code_id, salt).await?;
   ```

3. **Write assertions against behavior, not just compilation**:

   ```rust
   // Call a service method and assert the reply
   let result = program
       .my_service()
       .do_something(input)
       .send_recv(program_id)
       .await?;
   assert_eq!(result, expected_output);

   // Assert events were emitted
   let mut service = program.my_service();
   let mut listener = service.listener();
   let event = listener.listen().await.unwrap();
   assert!(matches!(event, MyEvent::SomethingDone { .. }));
   ```

4. **Handle raw payloads when needed** — if the test must go below generated clients, decide whether bytes are Sails-routed, plain SCALE, or metadata-driven state output. The raw mental model: `send_bytes*` returns a `MessageId`, `run_next_block` returns the `BlockRunResult`, and reply evidence lives in the block result.
5. **Advance blocks explicitly** — pick the right `BlockRunMode` when replies or deferred effects depend on block progression. Use `run_to_block` for delayed work or timeout behavior spanning multiple blocks.
6. **Record evidence** — capture failure mode, fix, and passing command output in the gtest note.
7. **Route forward** — proceed to `../sails-local-smoke/SKILL.md` only after the full suite is green.

## Common Pitfalls

- **Rust 2024 listener lifetime**: Under edition 2024 capture rules, chained calls like `program.service().listener().listen().await` fail with "temporary value dropped while borrowed". Bind each intermediate to a longer-lived variable:

  ```rust
  // Wrong — temporary dropped
  let event = program.service().listener().listen().await.unwrap();

  // Correct — each binding extends the lifetime
  let mut service = program.service_name();
  let mut listener = service.listener();
  let event = listener.listen().await.unwrap();
  ```

- **Program balance accounting in gtest**: The deployed program account has an existential deposit. Absolute balance assertions like `== wager` or `== 0` fail even when contract logic is correct. Assert deltas relative to the initial balance:

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
- Do not decode raw reply or event bytes as a bare business DTO until Sails routing framing has been checked.
