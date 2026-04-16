# Gear Builtin Actors — Reference

Builtin actors are chain-provided pseudo-programs: Substrate-native code registered by `pallet-gear-builtin` and reachable at a hardcoded `ActorId`. A standard Gear/Vara Sails program calls a builtin through the normal `msg::send_for_reply` family — but the request and reply types come from the `gbuiltin-*` helper crates, not from a Sails IDL.

Upstream docs: <https://wiki.gear.foundation/docs/developing/build/builtinactors>

## What a builtin actor is

- Lives in the runtime, not in WASM. Has no program code, no memory, no `read_state`.
- Claims a `BuiltinId` (a `u64`). At registration time the pallet derives a stable `ActorId` from that id.
- Dispatches incoming messages by decoding their payload into a per-actor `Request` enum and executing the mapped Substrate call.
- Replies synchronously from the program's perspective: a success reply decodes as the actor's `Response` (where one is defined) or is empty; a failure surfaces as an error reply with a `BuiltinActorError`.
- Charges the sender's block gas allowance for the underlying extrinsic weight (`max_gas()`).

Authoritative sources:
- Pallet: `gear/pallets/gear-builtin/src/lib.rs`
- Per-actor impls: `gear/pallets/gear-builtin/src/{bls12_381,staking,proxy}.rs`
- ETH bridge actor: `gear/pallets/gear-eth-bridge/` (registered through the same tuple)
- Helper crates (what a Sails program imports): `gear/gbuiltins/{bls381,staking,proxy,eth-bridge}/src/lib.rs`
- Vara registration tuple: `gear/runtime/vara/src/lib.rs` lines 1174–1186

## ActorId derivation

```text
SEED     = b"built/in"           // 8 bytes, from pallet-gear-builtin
ActorId  = blake2_256((SEED, builtin_id).encode())
```

Source: `gear/pallets/gear-builtin/src/lib.rs:165,212`.

The `builtin_id` is a `u64` assigned explicitly to each actor via `ActorWithId<N, Actor>` in the runtime's `BuiltinActors` tuple. The `ActorId` is a hash of that explicit `N`, not of the tuple position — reordering the tuple while keeping every `N` constant does not change any `ActorId`. What does change an `ActorId`: changing the numeric `N` for an actor, or switching to a runtime that assigns a different `N`. **Treat hardcoded `ActorId` constants as bound to the `N` in the target runtime.**

## Vara runtime registry

Source: `gear/runtime/vara/src/lib.rs:1174-1186`.

| Builtin ID | Actor        | Helper crate         | Stable `ActorId` (current Vara runtime)                              |
|------------|--------------|----------------------|----------------------------------------------------------------------|
| 1          | BLS12-381    | `gbuiltin-bls381`    | `0x6b6e292c382945e80bf51af2ba7fe9f458dcff81ae6075c46f9095e1bbecdc37` |
| 2          | Staking      | `gbuiltin-staking`   | `0x77f65ef190e11bfecb8fc8970fd3749e94bed66a23ec2f7a3623e785d0816761` |
| 3          | ETH Bridge   | `gbuiltin-eth-bridge`| derived from id `3`; see note below                                  |
| 4          | Proxy        | `gbuiltin-proxy`     | `0x8263cd9fc648e101f1cd8585dc0b193445c3750a63bf64a39cdf58de14826299` |

ETH bridge note: the Vara runtime computes the bridge `ActorId` at startup via `GearBuiltin::generate_actor_id(ETH_BRIDGE_BUILTIN_ID)` (see `runtime/vara/src/lib.rs:1202-1205`). Always reconfirm against that file for the target runtime version; do not copy a literal from another project.

## Canonical calling pattern

A builtin call is a normal `send_for_reply` against a non-program `ActorId`:

```rust
use gbuiltin_staking::{Request, RewardAccount};
use gstd::{msg, ActorId};
use hex_literal::hex;
use parity_scale_codec::Encode;

const STAKING_BUILTIN: ActorId = ActorId::new(hex!(
    "77f65ef190e11bfecb8fc8970fd3749e94bed66a23ec2f7a3623e785d0816761"
));

#[gstd::async_main]
async fn main() {
    let value = msg::value();
    let payload = Request::Bond {
        value,
        payee: RewardAccount::Program,
    }
    .encode();

    let reply = msg::send_bytes_for_reply(STAKING_BUILTIN, &payload[..], 0, 0)
        .expect("send failed")
        .await
        .expect("builtin returned error reply");

    // `reply` is empty for Bond; for ActiveEra decode as gbuiltin_staking::Response.
}
```

Notes:
- Prefer `send_bytes_for_reply` when encoding with `parity_scale_codec::Encode` directly. Use the typed `send_for_reply` only if you share a matching type the compiler can encode on your behalf.
- `value` transfers follow Substrate ED rules for the underlying pallet. Staking `Bond` requires `value` ≥ the network minimum bond.
- `reply_deposit` argument is the last `0` in the example; set a non-zero value only if the service depends on downstream reply fees (rare for builtins).
- An `Err` from `.await` is a real error reply (typically a `BuiltinActorError`), not a transport failure. Treat it like any other error reply in the `gear-messaging-and-replies.md` playbook.

## Per-actor reference

### Staking (`gbuiltin-staking`)

Source: `gear/gbuiltins/staking/src/lib.rs`. Broker example: `gear/examples/staking-broker/src/wasm.rs`.

`Request` variants (SCALE-indexed):
- `Bond { value, payee }` — index 0
- `BondExtra { value }` — index 1
- `Unbond { value }` — index 2
- `WithdrawUnbonded { num_slashing_spans }` — index 3
- `Nominate { targets: Vec<ActorId> }` — index 4
- `Chill` — index 5
- `PayoutStakers { validator_stash, era }` — index 6
- `Rebond { value }` — index 7
- `SetPayee { payee }` — index 8
- `ActiveEra` — index 9

`RewardAccount`: `Staked | Program | Custom(ActorId) | None`.

`Response::ActiveEra { info: ActiveEraInfo, executed_at, executed_at_gear_block }` is the only defined reply shape (for the `ActiveEra` request). Other requests reply with an empty payload on success.

### Proxy (`gbuiltin-proxy`)

Source: `gear/gbuiltins/proxy/src/lib.rs`. Broker example: `gear/examples/proxy-broker/src/wasm.rs`.

`Request` variants:
- `AddProxy { delegate: ActorId, proxy_type: ProxyType }` — index 0
- `RemoveProxy { delegate: ActorId, proxy_type: ProxyType }` — index 1

`ProxyType`: `Any | NonTransfer | Governance | Staking | IdentityJudgement | CancelProxy` (mirror of `vara-runtime`).

No `Response` type defined — success replies are empty; failures return `BuiltinActorError` via error reply.

### BLS12-381 (`gbuiltin-bls381`)

Source: `gear/gbuiltins/bls381/src/lib.rs`. Example: `gear/examples/bls381/src/wasm.rs`.

`Request` variants carry `Vec<u8>` fields that are **pre-encoded `ArkScale` payloads** (from the `ark-scale` crate bridging `arkworks` ↔ SCALE). The helper crate re-exports `ark_bls12_381`, `ark_ec`, `ark_ff`, `ark_scale`, `ark_serialize`.

- `MultiMillerLoop { a, b }` — index 0
- `FinalExponentiation { f }` — index 1
- `MultiScalarMultiplicationG1 { bases, scalars }` — index 2
- `MultiScalarMultiplicationG2 { bases, scalars }` — index 3
- `ProjectiveMultiplicationG1 { base, scalar }` — index 4
- `ProjectiveMultiplicationG2 { base, scalar }` — index 5
- `AggregateG1 { points }` — index 6
- `MapToG2Affine { message }` — index 7

`Response` mirrors each request variant with the same index and a single `Vec<u8>` (`ArkScale`-encoded) result. The `REQUEST_*` constants in the crate pin these indexes; gas charging is per-variant and depends on the decoded vector sizes.

### ETH Bridge (`gbuiltin-eth-bridge`)

Source: `gear/gbuiltins/eth-bridge/src/lib.rs`. Pallet: `gear/pallets/gear-eth-bridge/`.

`Request`:
- `SendEthMessage { destination: H160, payload: Vec<u8> }` — index 0

`Response`:
- `EthMessageQueued { block_number: u32, hash: H256, nonce: U256, queue_id: u64 }` — index 0

`destination` is an Ethereum 20-byte address. `payload` is the raw bridge payload (validated by the pallet). For bridge flows, addresses, and fee semantics see the separate `vara-eth-bridge-flows.md` and `vara-eth-bridge-contracts.md` references.

## Reply decoding checklist

When debugging a builtin reply:

1. Confirm the sender targeted a builtin `ActorId`, not a program. If it was a program, this skill does not apply — go to `gear-message-execution`.
2. Identify the matching helper crate by source `ActorId` ↔ builtin id.
3. Classify: empty success, typed `Response`, or error reply.
4. Decode as `gbuiltin_*::Response` using `parity_scale_codec::Decode` — not a Sails generated client, not `ProgramMetadata`. There is no Sails route prefix on a builtin reply.
5. On error replies, inspect the payload as `BuiltinActorError` (defined in `utils/builtins-common`, re-exported from `pallet-gear-builtin` via `builtins_common::BuiltinActorError`). Common variants: `InsufficientGas` when the caller-supplied `gas_limit` is below the call's weight; `GasAllowanceExceeded` when the block-level allowance is exhausted; `InsufficientValue`; `DecodingError`; and `Custom(LimitedStr)` for actor-specific errors.

## Gas and ED

- Each builtin declares a `max_gas()` covering the worst-case underlying extrinsic. The pallet upfront-charges this against the caller's message gas_limit (→ `InsufficientGas` if the caller supplied too little) and against the current block allowance (→ `GasAllowanceExceeded` if the block is saturated). Both cases surface as `BuiltinActorError` replies, not panics.
- Value-bearing requests (staking `Bond`, proxy ops with a deposit, etc.) follow the pallet's ED rules. First-time calls to a new builtin address require ED to be minted — runtime migrations do this for shipped builtins (`runtime/vara/src/migrations.rs` → `LockEdForBuiltin`), so application code only needs to worry about ED on brand-new chains or newly-registered actors.
- Keep reservations out of the critical path unless the calling flow already relies on them; a builtin reply typically arrives within the same message-queue pass.

## Guardrails

- **Do not hardcode an `ActorId` without citing a runtime file.** Re-derive with `hash((b"built/in", id).encode())` or copy from `runtime/vara/src/lib.rs`, and note the source.
- **Do not decode builtin replies with a Sails client.** There is no route prefix; use the helper crate's `Response` type.
- **Do not call a builtin from a sync handler.** The call is `_for_reply`; the handler must be async.
- **Do not assume a reply shape across runtime versions.** Helper crates evolve — pin to a workspace version that matches the target runtime.
- **Do not wrap a builtin behind a service handler that loses idempotency.** Broker services should carry their own retry and reconciliation state; the builtin has no memory.
- **Do not confuse this with runtime-maintenance work.** Adding or changing a builtin actor happens inside the gear repo (`pallets/gear-builtin/` + `runtime/vara/src/lib.rs`) and is out of scope for this pack.
