# Sails Gtest And Local Validation

## Canonical `gtest` Harness

- Prefer the Sails-first path built around `GtestEnv` and generated clients.
- A typical harness creates one `System`, funds the sender, submits the Wasm, builds `GtestEnv`, and deploys the program through the generated constructor path.
- Use generated client methods for normal command and query assertions.

## Raw `gtest` Escape Hatch

- When you must debug below the generated client layer, remember the raw flow:
  - `Program::send_bytes*` returns a `MessageId`
  - `System::run_next_block()` returns a `BlockRunResult`
  - `BlockRunResult.log()` contains the reply log entries for that block
  - `BlockRunResult.failed` is the fast failure set for sent messages
- Use `run_to_block` when delayed sends or multi-block progress matter more than a single next-block reply.

## `BlockRunMode` Semantics

- `Auto`: run enough blocks to extract tracked replies automatically.
- `Next`: advance one block per reply extraction attempt; useful when timing matters.
- `Manual`: no automatic block running, so the test must call block-advance methods explicitly.

Pick `Next` or `Manual` for timing-sensitive flows, delayed work, reply absence, redirects, or wait/reservation behavior.

## What To Assert

- Happy-path command and query behavior
- Typed events through listener flow where the service exposes events
- Reply and timeout behavior for async paths
- Gas, value, or reservation-sensitive results when accounting matters
- Real route or codec bugs with a low-level byte path only when generated clients are insufficient

## Event Listener Pattern

- If the service declares `#[service(events = ...)]`, prefer asserting events through the generated listener API.
- A common flow is:
  - obtain the service client
  - create a listener from that service client
  - start listening before the command that should emit the event
  - call the command
  - read the next event from the stream and assert its typed payload
- Event assertions should be tied to the block that successfully executed the producing command.

## Sails-Specific Edge Cases

- `ReplyIsMissing` often means the wrong `BlockRunMode` or missing block advancement.
- `UserspacePanic` can appear after an async path that already waited or sent internally.
- A timeout result does not prove a later reply hook never runs.
- Event assertions should happen after the producing block and only expect events on successful execution.
- If you drop to raw `gtest`, inspect the matching `MessageId` in the `BlockRunResult` instead of expecting a direct typed return value.

## Typed Local Smoke

1. Start or reuse a local node.
2. Connect with `GearApi`.
3. Wrap the API in `GclientEnv` or the equivalent generated-client environment.
4. Upload the tested Wasm, deploy with a unique salt, and record the real program id.
5. Use the generated client for one command and one query path.
6. Use local dev accounts such as `//Alice` and `//Bob` only for local smoke, and keep seed phrases or private keys out of committed docs.

## Setup Ergonomics

- `sails_rs::gtest::constants` such as `DEFAULT_USER_ALICE`, `DEFAULT_USERS_INITIAL_BALANCE`, and `UNITS` improve readability in ordinary happy-path tests.
- Treat them as convenience fixtures, not as part of the behavioral contract under test.
- Use explicit custom accounts or balances when the test depends on caller identity, funding asymmetry, or boundary conditions.

## Guardrails

- Do not invent the deployed program id, voucher id, or account addresses.
- Do not treat local-node smoke as a substitute for `gtest`.
- Keep the smoke path typed unless you are isolating a transport bug.
