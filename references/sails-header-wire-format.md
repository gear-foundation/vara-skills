# Sails Header v1 Wire Format

Source of truth: [docs/sails-header-v1-spec.md](https://github.com/gear-tech/sails/blob/master/docs/sails-header-v1-spec.md).

## Overview

Every Sails 1.0 message begins with a 16-byte header prepended to the SCALE-encoded payload. The header lives entirely within the Gear message payload — no runtime or consensus changes required.

## Base Header Layout

```
Byte offset  Field          Size (bytes)  Description
0–1          Magic          2             ASCII "GM" (0x47 0x4D)
2            Version        1             0x01
3            Header length  1             Must be 0x10 in v1
4–11         Interface ID   8             64-bit ID from interface hash
12–13        Entry ID       2             Little-endian 16-bit entry identifier
14           Route Index    1             0x00 = infer route if unambiguous
15           Reserved       1             Must be 0x00 in v1
>15          Payload        variable      SCALE-encoded params or body
```

Extension-sized headers are reserved for future versions. A v1 decoder must reject header lengths other than `0x10`.

## Identifier Derivation

### Interface ID

Deterministic 64-bit hash derived from the canonical interface structure. Service names never influence `interface_id`. See [docs/reflect-hash-spec.md](https://github.com/gear-tech/sails/blob/master/docs/reflect-hash-spec.md) and [docs/interface-id-spec.md](https://github.com/gear-tech/sails/blob/master/docs/interface-id-spec.md).

### Entry ID

Commands, queries, and events are sorted lexicographically by name within their interface. `entry_id` is assigned sequentially starting at 0. Use `@entry_id: N` in IDL to override.

### Route Index

- `0x00` — infer route (valid only when exactly one matching `interface_id` instance exists)
- Non-zero — explicit route selector mapped via per-program manifest

## Impact on Clients

Generated clients encode/decode the header automatically. When debugging wire payloads, the first 16 bytes are the Sails Header, not SCALE data.

## Interface ID Stability

- Adding or removing methods/types **changes** the interface ID
- Renaming public methods **changes** the interface ID because the exported function route name is hashed
- `@entry_id` overrides allow pinning specific entry points across versions, but they do not preserve the interface ID after a method rename
- Programs hosting V1 and V2 services simultaneously can use `route_idx` to disambiguate

## Validation Checklist

1. Magic: first two bytes are `0x47 0x4D`
2. Version: `0x01`
3. Header length: must equal `0x10` for v1; reject smaller, larger, or extension-sized v1 headers
4. Reserved byte: must be `0x00` in v1
5. Route inference (`0x00`): resolve only if exactly one matching instance exists

## Wire Examples

Route inference (`route_idx = 0`):
```
47 4D  01   10     18 07 F6 E5 D4 C3 B2 A1  02 00     00     00
^magic ^ver ^hlen  ^interface_id LE         ^entry_id ^route ^reserved
```

Explicit route (`route_idx = 2`):
```
47 4D 01 10   EF CD AB 89 67 45 23 01   05 00   02   00
```
