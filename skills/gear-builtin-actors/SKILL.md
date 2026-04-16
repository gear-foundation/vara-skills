---
name: gear-builtin-actors
description: Use when a builder needs to design or debug calls from a standard Gear/Vara Sails program into runtime builtin actors such as BLS12-381, staking, proxy, or ETH bridge, including ActorId derivation, request encoding, reply decoding, and gas or ED budgeting. Do not use for regular program-to-program messaging, Vara.eth or ethexe-only work, non-Sails repositories, or runtime-maintenance tasks inside the Gear repo.
---

# Gear Builtin Actors

## Goal

Treat builtin actors as a distinct call target: runtime-provided pseudo-programs at hardcoded `ActorId`s, reached via the normal `msg::send_for_reply` family but with request and reply types defined in the `gbuiltin-*` helper crates, not in a Sails IDL.

## Inputs

- `../../references/gear-builtin-actors.md` — actor catalog, ActorId derivation, per-actor request/response shapes, calling pattern
- `../../references/gear-messaging-and-replies.md` — reply semantics for `send_for_reply`
- `../../references/gear-gas-reservations-and-waitlist.md` — gas budgeting and waitlist interaction when awaiting builtin replies
- `../../references/gear-gstd-api-and-syscalls.md` — the underlying `gstd::msg` API family

## Route Here When

- a feature needs staking, nominating, proxy management, BLS12-381 pairings, or ETH bridging from inside a Sails program
- a `send_for_reply` targets a hardcoded non-program `ActorId` and the reply does not decode as a Sails route
- a reply bytes stream is expected to decode as a `gbuiltin_*::Response` rather than a Sails-routed payload
- a builder is unsure whether to call a builtin directly from a service handler or wrap it behind a dedicated broker service
- a gtest or local-smoke run fails at the builtin call site with gas or ED errors
- a runtime upgrade changes the set of registered builtins and existing hardcoded `ActorId` constants need revalidation

## Working Model

1. Confirm the actor is registered in the target runtime. For Vara, the authoritative tuple is `BuiltinActors` in `runtime/vara/src/lib.rs` (IDs 1 = BLS12-381, 2 = staking, 3 = ETH bridge, 4 = proxy). IDs are runtime-version-bound.
2. Pick the correct `gbuiltin-*` helper crate: `gbuiltin-staking`, `gbuiltin-proxy`, `gbuiltin-bls381`, `gbuiltin-eth-bridge`. Import its `Request` (and `Response` where defined).
3. Derive the `ActorId` from the builtin ID via `hash((b"built/in", id).encode())`, or take the stable hex from the reference. Store as a `const ActorId` in the module that owns the call.
4. Call from an async handler: `msg::send_bytes_for_reply(ACTOR_ID, &payload[..], value, reply_deposit)?.await`. Value and reply deposit follow Substrate ED rules for the builtin's underlying pallet.
5. Classify the reply: success reply decodes as `gbuiltin_*::Response` (where one is defined) or is empty for fire-and-forget variants; an error reply surfaces as the `.await` Err arm and carries a `BuiltinActorError` payload.
6. Budget gas against the builtin's declared `max_gas()` weight; block allowance failures manifest as error replies, not panics.
7. For first-time interactions with a new builtin address, confirm ED is minted (runtime migrations handle this for shipped builtins — only relevant on fresh chains or new actors).
8. When a service wraps a builtin (broker pattern), keep the wrapping service responsible for idempotency, reply routing, and state reconciliation — the builtin itself has no memory, no `read_state`, and no code.

## Guardrails

- Do not hardcode `ActorId` literals without citing the runtime file or using `hash((b"built/in", id).encode())` — IDs are runtime-version-bound and change with registration changes.
- Do not expect a Sails route prefix on builtin replies. Decode with `Response::decode(&mut &bytes[..])` from the matching `gbuiltin-*` crate, not with a generated Sails client.
- Do not call builtins from a sync handler that cannot await; use `#[gstd::async_main]` or an async service method.
- Do not treat builtin calls as free. Gas is charged against the sender's block allowance, and ED rules apply to any `value` transferred.
- Do not confuse builtin IDs with actor IDs in broker examples; the ID is a `u64` registration key, the `ActorId` is its hashed account.
- If the task is really about adding a new builtin actor to the runtime itself, stop — that is runtime-maintenance work inside the gear repo, not Sails application work covered by this pack.
- If the target chain is Vara.eth or ethexe, stop — the builtin-actor set differs and routes through a different pack.
