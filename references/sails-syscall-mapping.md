# Sails `Syscall` API Mapping

Use `Syscall::*` for all runtime accessors in service code. Do not use raw `gcore::*`, `msg::*`, or `exec::*` calls.

Source of truth: `rs/src/gstd/syscalls.rs` and [docs/syscall-mapping-spec.md](../../docs/syscall-mapping-spec.md).

## Type Aliases

- `ValueUnit = u128`
- `GasUnit = u64`

## Mapping

### Message Context

| `Syscall` method | Return type | Underlying call | `ethexe` gating |
| --- | --- | --- | --- |
| `Syscall::message_id()` | `MessageId` | `gcore::msg::id()` | |
| `Syscall::message_size()` | `usize` | `gcore::msg::size()` | |
| `Syscall::message_source()` | `ActorId` | `gcore::msg::source()` | |
| `Syscall::message_value()` | `ValueUnit` | `gcore::msg::value()` | |
| `Syscall::reply_to()` | `Result<MessageId, Error>` | `gcore::msg::reply_to()` | |
| `Syscall::reply_code()` | `Result<ReplyCode, Error>` | `gcore::msg::reply_code()` | |
| `Syscall::signal_from()` | `Result<MessageId, Error>` | `gcore::msg::signal_from()` | non-ethexe only |
| `Syscall::signal_code()` | `Result<Option<SignalCode>, Error>` | `gcore::msg::signal_code()` | non-ethexe only |
| `Syscall::read_bytes()` | `Result<Vec<u8>, Error>` | alloc + `gcore::msg::read()` | |

### Execution Context

| `Syscall` method | Return type | Underlying call | `ethexe` gating |
| --- | --- | --- | --- |
| `Syscall::program_id()` | `ActorId` | `gcore::exec::program_id()` | |
| `Syscall::block_height()` | `u32` | `gcore::exec::block_height()` | |
| `Syscall::block_timestamp()` | `u64` | `gcore::exec::block_timestamp()` | |
| `Syscall::value_available()` | `ValueUnit` | `gcore::exec::value_available()` | |
| `Syscall::gas_available()` | `GasUnit` | `gcore::exec::gas_available()` | |
| `Syscall::env_vars()` | `EnvVars` | `gcore::exec::env_vars()` | |
| `Syscall::exit(inheritor_id)` | `!` | `gcore::exec::exit(inheritor_id)` | |
| `Syscall::panic(data)` | `!` | `gcore::ext::panic(data)` | |
| `Syscall::system_reserve_gas(amount)` | `Result<(), Error>` | `gcore::exec::system_reserve_gas(amount)` | non-ethexe only |

## Common Patterns

- **Self-message guard**: `Syscall::message_source() == Syscall::program_id()`
- **Gas-guarded loop**: check `Syscall::gas_available()` before expensive iterations
- **Raw payload access**: `Syscall::read_bytes()` bypasses SCALE decode

## Non-WASM Behavior

On non-`wasm32` + `std`: `Syscall` reads from thread-local mock state. Matching `with_*` setters exist for tests (`with_message_id`, `with_message_source`, `with_program_id`, etc.).

On non-`wasm32` without `std`: all methods are unimplemented and panic.
