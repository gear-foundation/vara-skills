# Delayed Message Pattern

## Use Case

Use this pattern for future-block work such as reminders, auctions, inactivity cleanup, vesting steps, and timeout enforcement.

## Self-Message Payload Encoding

Prefer the generated client path for delayed self-messages when possible. If you must construct delayed message payloads manually, use the version matching your program's sails-rs dependency.

### 1.0.0-beta+ (Binary Header Protocol)

In 1.0.0-beta+, all Sails messages (including self-messages) use the 16-byte binary header protocol. Generated clients encode this automatically. For manual delayed messages, the header requires the Interface ID (8-byte service fingerprint) and Entry ID (2-byte method selector) from the program's IDL. No public runtime helper in `sails-rs` currently constructs the v2 header from service/method names at runtime.

If you cannot use a generated client for the self-message, verify your manual header bytes against the IDL's Interface ID before deploying on-chain. See `sails-rs-imports.md` section **Sails Header Protocol** for the byte layout.

### 0.10.x (SCALE-String Routing)

In 0.10.x, encode service, method, and arguments as SCALE-encoded strings and concatenate:

```rust
let payload = [
    "ReminderBoard".encode(),
    "TriggerReminder".encode(),
    id.encode(),
]
.concat();
```

- This is the route-prefixed byte shape for 0.10.x when a delayed internal message cannot go through a generated client call directly.
- Keep the service and method names aligned with the exported Sails routes.
- In gtest under 1.0.0-beta+, this pattern may still route correctly because the test runtime can support both encoding styles. However, its behavior on-chain with the beta.2 runtime is unverified. Prefer the binary header protocol or the generated client path for on-chain deployment.

## Sending The Delayed Message

```rust
// Dynamic gas: if this handler also does work, a fixed gas_limit will fail
// when execution already consumed most of the budget.
let gas_for_next = exec::gas_available() * 9 / 10;
msg::send_bytes_with_gas_delayed(exec::program_id(), payload, gas_for_next, 0, delay)
    .expect("failed to schedule delayed self-message");
```

- Use `exec::program_id()` when the program is scheduling work for itself.
- Use `exec::gas_available()` to compute the gas budget dynamically. Do not use a fixed `gas_limit` for self-scheduling loops — if the handler does work AND schedules the next tick, the remaining gas may be insufficient for the delayed message. A common pattern is `exec::gas_available() * 9 / 10` to reserve 90% of remaining gas for the next invocation.
- Keep transferred value at `0` unless the delayed route truly needs value.

## Internal-Only Guard

- The internal-only check is `msg::source() == exec::program_id()`.
- Enforce it at the start of the exported handler so outside callers cannot trigger the internal route directly.

```rust
#[export]
pub fn trigger_reminder(&mut self, id: u64) {
    assert_eq!(msg::source(), exec::program_id(), "internal only");
    self.finish_trigger(id);
}
```

## Reservation And Gas Notes

- Use `ReservationId` only when later execution budget must survive across blocks.
- If a plain delayed send is enough, keep the flow simpler and derive gas from `exec::gas_available()`.
- Recompute or validate critical state inside the delayed handler instead of trusting stale assumptions from the scheduling block.

## Gtest vs On-Chain Funding

- On a real node (local or remote), the program must hold VARA balance to pay for delayed message gas. Programs with zero balance cannot schedule delayed messages. Transfer VARA to the program address after deployment and before calling methods that schedule delayed work.
- In `gtest`, delayed messages succeed without explicit program funding. This asymmetry is a common source of "works in test, fails on chain" bugs. Test the funding requirement in local-smoke validation.

## Idempotency Rules

- Delayed routes must be safe if the target item was already canceled, completed, or cleaned up.
- Persist enough state to detect stale work.
- Prefer an idempotent no-op or explicit early return over a half-applied mutation.

## Test Guidance

- Use `run_to_block` for delay-sensitive assertions.
- Assert both the scheduler-side effect and the eventual handler-side effect.
- If debugging the raw byte route, test the payload shape directly before blaming gas or timing.
