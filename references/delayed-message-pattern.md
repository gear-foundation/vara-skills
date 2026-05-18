# Delayed Message Pattern

## Use Case

Use this pattern for future-block work such as reminders, auctions, inactivity cleanup, vesting steps, and timeout enforcement.

## Canonical Self-Message Payload

For a Sails 1.0 self-call, build the same Sails Header v1 plus SCALE-encoded params that generated clients use. In generated Rust client code this is the `io::<Call>::encode_call(route_idx, args...)` helper:

```rust
use reminder_board_client::{
    ReminderBoardClientProgram,
    reminder_board::io::TriggerReminder,
};

let payload = TriggerReminder::encode_call(
    ReminderBoardClientProgram::ROUTE_ID_REMINDER_BOARD,
    id,
);
```

- This is the header-routed byte shape to use when a delayed internal message cannot go through a generated client send directly.
- Keep the route constant and generated `io` type aligned with the exported Sails route.
- If generated client code is unavailable, manually encode the Sails Header v1 followed by SCALE-encoded params. See `../../references/sails-header-wire-format.md` for the header layout.
- The legacy SCALE-string route form (`service`, `method`, then args) is not a valid Sails 1.0 delayed self-message payload.

## Sending The Delayed Message

```rust
// Dynamic gas: if this handler also does work, a fixed gas_limit will fail
// when execution already consumed most of the budget.
let gas_for_next = Syscall::gas_available() * 9 / 10;
msg::send_bytes_with_gas_delayed(Syscall::program_id(), payload, gas_for_next, 0, delay)
    .expect("failed to schedule delayed self-message");
```

- Use `Syscall::program_id()` when the program is scheduling work for itself.
- Use `Syscall::gas_available()` to compute the gas budget dynamically. Do not use a fixed `gas_limit` for self-scheduling loops — if the handler does work AND schedules the next tick, the remaining gas may be insufficient for the delayed message. A common pattern is `Syscall::gas_available() * 9 / 10` to reserve 90% of remaining gas for the next invocation.
- Runtime accessors use `Syscall::*`; outbound delayed sends still use the normal `msg::send*` family.
- Keep transferred value at `0` unless the delayed route truly needs value.

## Internal-Only Guard

- The internal-only check is `Syscall::message_source() == Syscall::program_id()`.
- Enforce it at the start of the exported handler so outside callers cannot trigger the internal route directly.

```rust
#[export]
pub fn trigger_reminder(&mut self, id: u64) {
    assert_eq!(Syscall::message_source(), Syscall::program_id(), "internal only");
    self.finish_trigger(id);
}
```

## Reservation And Gas Notes

- Use `ReservationId` only when later execution budget must survive across blocks.
- If a plain delayed send is enough, keep the flow simpler and derive gas from `Syscall::gas_available()`.
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
- If debugging the raw byte route, assert the payload starts with the Sails Header v1 bytes (`GM`, version `0x01`, header length `0x10`) before blaming gas or timing.
