---
name: sails-local-smoke
description: Use when a builder has a standard Gear/Vara Sails app with green gtest coverage and needs typed validation against a local node. Do not use before gtest passes, for remote networks, or for non-Sails programs.
---

# Sails Local Smoke

## Goal

Validate the generated client path against a local node after `gtest` is already green.

## Identity Rules

- Use local dev accounts or user-provided account addresses in `SS58` form for standard Vara account flows; do not default to Ethereum `0x` addresses for normal local-node work.
- Record the real deployed `program id` from the deploy step and pass that into the typed client. If the flow uses vouchers, issue one first and use the returned voucher ID. Do not invent either identifier.
- Keep seed phrases and private keys out of committed scripts, docs, and examples. Use local keyrings, environment input, or interactive setup instead.

## Inputs

- `../../references/sails-gtest-and-local-validation.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../references/sails-cheatsheet.md`
- `../../references/voucher-and-signless-flows.md`

## Sequence

1. Confirm the `docs/plans/...-gtest.md` note shows a green test loop.
2. Start or reuse a local node and connect with `GearApi::init(WSAddress::dev())` for local node on default port. Do not use `GearApi::dev_from_path()` — that expects a filesystem path to the node binary, not a WebSocket URL.
3. Deploy the tested Wasm and record the actual program id returned by the deploy flow. If the constructor does non-trivial work, override gas with an explicit limit.
4. If the program uses delayed messages, transfer VARA to the program address before exercising commands. On-chain programs need balance to pay for future gas — this is not required in `gtest`.
5. Use the typed generated-client path through a local client environment such as `GclientEnv`, wiring in the actual deployed program id.
6. Exercise one command or query path that proves the typed integration works on a local node.

## References

- `../../references/gtest-cheatsheet.md`

## Guardrails

- Keep this step typed and local.
- Do not invent account addresses, program ids, or voucher ids in guidance that pretends they already exist.
- Do not replace local smoke with explorer queries or ad hoc CLI poking.
- If `gtest` is red or missing, stop and go back to `../sails-gtest/SKILL.md`.
