---
name: gear-gstd-api-map
description: "Use when a builder needs to choose the right gstd API for messaging, execution, reservations, async reply flows, or program creation, and trace that API to gcore or gsys when behavior must be confirmed. Provides a design-time API map with quick reference tables and inline examples. Do not use for Vara.eth or ethexe-first work, non-Gear repositories, or broad runtime-maintenance tasks."
---

# Gear gstd API Map

## Goal

Keep design work API-first: start from `gstd`, then drop to `gcore` or `gsys` only when you need to confirm limits, gas shape, or low-level behavior.

## Inputs

- `../../references/gear-execution-model.md` — execution model and block lifecycle
- `../../references/gear-messaging-and-replies.md` — message flow and reply semantics
- `../../references/gear-gas-reservations-and-waitlist.md` — gas reservations and waitlist
- `../../references/gear-gstd-api-and-syscalls.md` — full API surface and syscall mapping

## Route Here When

- A spec or architecture note needs to know whether a Gear program can send, await replies, self-schedule, reserve gas, or create child programs.
- A builder is choosing between typed payloads, raw bytes, staged push-plus-commit, or input-forwarding APIs.
- A design depends on `#[gstd::async_main]`, `_for_reply` flows, delayed work, `ReservationId`, or `prog::*`.
- A debugging pass needs to confirm which `gr_*` syscall family a high-level API actually reaches.

## Workflow

1. **Identify builder intent** — start from what the program needs to do, not from raw syscalls.
2. **Choose the `gstd` family** — match intent to the correct module (see API Quick Reference below).
3. **Select API level** — prefer the highest-level API that preserves the contract:

   ```rust
   // Preferred: typed send with Sails encoding
   msg::send(dest, payload, value)?;

   // Only when intentional: raw bytes for codec debugging
   msg::send_bytes(dest, raw_bytes, value)?;
   ```

4. **Check design constraints** — block-delayed execution, reply deposit, reservation lifetime, waitlist exposure, gas budget, and route-prefix stability for Sails clients.
5. **Drop to lower layers when needed**:
   - `gcore` — to confirm wrapper behavior, exact signatures, and fallibility.
   - `gsys` — only for exact syscall names (`gr_*`) or control-vs-get distinctions.

## API Quick Reference

| Module | Key APIs | When to Use |
|--------|----------|-------------|
| `msg` | `send`, `reply`, `send_delayed`, `send_for_reply`, `send_bytes`, push-plus-commit | Sending messages, replying, delayed dispatch, awaiting replies |
| `exec` | `gas_available`, `block_height`, `wait`, `wait_for`, `wake`, `reply_deposit`, `exit` | Reading execution context, parking in waitlist, waking actors |
| `prog` | `create_program`, `create_program_bytes`, create-for-reply | Creating child programs with optional delay and gas limits |
| reservations | `ReservationId::reserve`, `.unreserve`, reservation pools | Future-block work that must keep a gas budget alive |

## Examples

**Sending a delayed self-message with reserved gas:**

```rust
// Reserve gas for future-block work
let reservation_id = ReservationId::reserve(gas_amount, duration_blocks)?;

// Send delayed message to self using reserved gas
msg::send_delayed_from_reservation(
    reservation_id,
    exec::program_id(),
    payload,
    value,
    delay_blocks,
)?;
```

**Awaiting a reply from another program:**

```rust
let reply: ReplyBytes = msg::send_for_reply(dest, payload, value, reply_deposit)?
    .await?;
```

## Guardrails

- Prefer `gstd` as the default public API for standard Gear/Vara builders.
- Treat raw `gsys::gr_*` names as confirmation tools, not the first design vocabulary.
- Keep design notes phrased in message flow, replies, blocks, and contracts, not in syscall sequences.
- If a Sails route depends on generated clients, preserve that route contract even for delayed or self-messaging paths.
- Stop if the task is really about runtime benchmarking, syscall-maintenance coverage, or ethexe-only behavior.
