---
name: sails-local-smoke
description: Use when a builder has a standard Gear/Vara Sails app with green gtest coverage and needs typed validation against a local node. Do not use before gtest passes, for remote networks, or for non-Sails programs.
---

# Sails Local Smoke

## Goal

Validate the generated client path against a local node after `gtest` is already green.

## Deploy Artifact And Tooling

- The deploy artifact is the `.opt.wasm` file (optimized WASM), not the plain `.wasm`. The `.opt.wasm` is produced by `wasm-opt` during the Sails build and is significantly smaller. Uploading the unoptimized `.wasm` to a node will often fail with `CodeTooLarge`.
- Prefer `vara-wallet` for deploying to a local node. It handles account management and program upload without requiring a Gear source checkout or Rust-specific tooling.
- For Rust-native test harnesses that already use `gclient`, the `GearApi` + `GclientEnv` path remains valid as a secondary option.

## Identity Rules

- Use local dev accounts or user-provided account addresses in `SS58` form for standard Vara account flows; do not default to Ethereum `0x` addresses for normal local-node work.
- Record the real deployed `program id` from the deploy step and pass that into the typed client. If the flow uses vouchers, issue one first and use the returned voucher ID. Do not invent either identifier.
- Keep seed phrases and private keys out of committed scripts, docs, and examples. Use local keyrings, environment input, or interactive setup instead.

## Inputs

- `../../references/sails-gtest-and-local-validation.md`
- `../../references/sails-idl-client-pipeline.md`
- `../vara-wallet/SKILL.md`
- `../../references/sails-cheatsheet.md`
- `../../references/voucher-and-signless-flows.md`

## Sequence — Primary Path (vara-wallet + sails-js)

1. Confirm the `docs/plans/...-gtest.md` note shows a green test loop.
2. Start or reuse a local node on the default port (ws://localhost:9944).
3. Set the endpoint for the session: `export VARA_WS=ws://localhost:9944`. The default is mainnet — always override for local work.
4. Import a funded dev account: `$VW wallet import --seed '//Alice' --name alice`.
5. Deploy the `.opt.wasm` artifact and record the program id:
   ```bash
   UPLOAD=$($VW --account alice program upload ./target/wasm32-unknown-unknown/release/my_program.opt.wasm)
   PROGRAM_ID=$(echo $UPLOAD | jq -r .programId)
   ```
   If the constructor does non-trivial work, override gas with `--gas-limit`.
6. If the program uses delayed messages, transfer VARA to the program address: `$VW --account alice transfer $PROGRAM_ID 100`.
7. Exercise one command and one query to prove the integration works:
   ```bash
   $VW --account alice call $PROGRAM_ID MyService/DoSomething --args '["hello"]' --idl ./my_program.idl
   $VW call $PROGRAM_ID MyService/GetState --args '[]' --idl ./my_program.idl
   ```

## Sequence — Secondary Path (Rust gclient)

Use this path when the project already has a Rust test harness that uses `gclient` and `GclientEnv`.

1. Confirm gtest is green.
2. Start or reuse a local node and connect with `GearApi::init(WSAddress::dev())` for local node on default port. Do not use `GearApi::dev_from_path()` — that expects a filesystem path to the node binary, not a WebSocket URL.
3. Deploy the `.opt.wasm` and record the actual program id returned by the deploy flow. If the constructor does non-trivial work, override gas with an explicit limit.
4. If the program uses delayed messages, transfer VARA to the program address before exercising commands. On-chain programs need balance to pay for future gas — this is not required in `gtest`.
5. Use the typed generated-client path through `GclientEnv`, wiring in the actual deployed program id.
6. Exercise one command or query path that proves the typed integration works on a local node.

## References

- `../../references/gtest-cheatsheet.md`

## Guardrails

- Keep this step typed and local.
- Do not invent account addresses, program ids, or voucher ids in guidance that pretends they already exist.
- Do not replace local smoke with explorer queries or ad hoc CLI poking.
- If `gtest` is red or missing, stop and go back to `../sails-gtest/SKILL.md`.
- Use `.opt.wasm` as the default deploy artifact. The plain `.wasm` is an intermediate build output that may exceed on-chain size limits.
- When targeting a local node with `vara-wallet`, always set `VARA_WS=ws://localhost:9944`. The default endpoint is mainnet.
- Do not embed machine-specific absolute paths in deploy commands or documentation. Use project-relative paths or skill-pack-relative references.
