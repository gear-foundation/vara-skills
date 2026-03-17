# Gtest Patterns

## Default Path

- Prefer `GtestEnv` and generated clients for standard Sails verification.
- Drop to raw `gtest::Program` calls only when you are debugging routing, payload encoding, failure logs, or timing at a lower level than the generated client exposes.

## Raw `send_bytes` Mental Model

- `Program::send_bytes(...)` returns a `MessageId`.
- `System::run_next_block()` returns a `BlockRunResult`.
- Replies and failures are inspected from that `BlockRunResult`, not from the `send_bytes` return value.

```rust
let msg_id = program.send_bytes(sender, payload);
let r = system.run_next_block();

assert!(!r.failed.contains(&msg_id));

let reply = r
    .log()
    .iter()
    .find(|entry| entry.reply_to() == Some(msg_id))
    .expect("reply log missing");
```

## Init Semantics

The first message sent to a program is always treated as init, even if the program has no explicit init function.
Tests should account for this when choosing the first payload.

## What To Inspect

- `r.log()` contains the block logs and replies that landed in that block.
- `r.succeed`, `r.failed`, and `r.not_executed` are the first outcome buckets to inspect.
- `r.failed.contains(&msg_id)` is the first quick check for command-path failure.
- `reply.reply_code()` tells you whether the reply was a success or an error.
- `reply.reply_to()` links a reply log back to the original message id.
- `r.contains(&expected_log)` is the quickest structured assertion when a `Log` pattern is enough.
- `r.decoded_log::<T>()` is useful when you want typed log inspection instead of raw bytes.
- The payload still needs decoding after you extract the matching reply log entry.

## Panic Assertions

- For fatal-path validation, prefer `r.assert_panicked_with(msg_id, "...")` when you want to assert userspace panic text.
- Use raw `reply_code()` inspection when you need finer-grained low-level failure analysis.

## Multi-Block And Delayed Behavior

- Use `system.run_to_block(n)` when delayed sends, wakeups, or reservation expiry depend on block height.
- `run_next_block()` is enough only when the full effect should land in the very next block.
- For Sails `GtestEnv`, choose `BlockRunMode::Next` or `BlockRunMode::Manual` when the test must expose exact timing.
- `run_scheduled_tasks(n)` advances blocks while processing scheduled tasks only, without draining the message queue.
- `run_next_block_with_allowance(...)` is useful for low-level gas/allowance timing tests.

## Reply Decoding Reminder

- Generated clients handle reply prefixes for you.
- In raw tests for Sails programs, reply payloads may still include Sails routing framing (service + method + result), so decode them with Sails-aware helpers when the test is not intentionally validating raw framing.
- If the goal is not codec or routing debugging, go back to the generated client path.

## Setup Ergonomics

- `Program<'_>` borrows `System`, so a helper usually cannot return `(System, Program<'_>)` without running into lifetime friction.
- Prefer either:
  - a helper that returns only `System`, then build `Program` inside each test
  - a helper that performs the setup inline per test when the borrow would otherwise escape
- Also remember that only one System instance is allowed per thread.

## Failure Patterns

- `UserspacePanic` is often the expected assertion target for fatal command-path validation.
- `RanOutOfGas` and similar reply codes are best asserted through reply logs plus `failed.contains(&msg_id)`.
- For low-level debugging, record the `MessageId`, the block you ran, and the relevant `BlockRunResult` evidence in the test note.
