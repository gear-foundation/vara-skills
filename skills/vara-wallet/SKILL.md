---
name: vara-wallet
description: Use when an agent needs to interact with Vara Network on-chain — deploy programs, call Sails methods, manage wallets, transfer tokens, monitor events. Not for building Sails programs (use vara-skills for that).
---

# Vara Wallet

CLI tool for AI agents to interact with Vara Network on-chain.

**Repository:** https://github.com/gear-foundation/vara-wallet
**Install:** `npm install -g vara-wallet`

## Role

Use this skill for **on-chain interaction** with Vara Network: deploying programs, calling Sails methods, managing wallets, transferring VARA, querying state, and monitoring events.

Do NOT use this skill for:
- Writing Sails Rust programs — use `vara-skills/skills/sails-feature-workflow/`
- Running gtest — use `vara-skills/skills/sails-gtest/`
- Setting up Rust/Gear toolchain — use `vara-skills/skills/sails-dev-env/`

## Setup

```bash
# Check if installed
if command -v vara-wallet &>/dev/null; then
  VW="vara-wallet"
else
  npm install -g vara-wallet
  VW="vara-wallet"
fi
```

**Minimum version: 0.16.0** — required for structured `PROGRAM_ERROR`, `INVALID_ARGS_FORMAT`, sharper v1 `IDL_NOT_FOUND`, and the `Result::unwrap` strip the case-switches below depend on. Pre-0.16 emits only `{error, code}`. See *Structured Errors (0.16+)*.

## Zero-Setup Wallet

On first use, create a wallet. Encryption and passphrase are automatic — no human setup required.

```bash
# Creates wallet, auto-generates passphrase, encrypts, suppresses secrets
$VW wallet create --name agent

# Verify
$VW wallet list
# → [{ "name": "agent", "address": "kG...", "encrypted": true, "isDefault": true }]
```

The passphrase is stored at `~/.vara-wallet/.passphrase` (0600). The agent never sees or handles it.

## Command Quick Reference

### Read (no account needed)

| Command | Purpose |
|---------|---------|
| `$VW node info` | Chain name, genesis, latest block |
| `$VW balance [address]` | Account balance in VARA |
| `$VW program info <id>` | Program status and codeId |
| `$VW program list [--count N] [--all]` | List on-chain programs (default: 100) |
| `$VW code info <codeId>` | Code blob metadata |
| `$VW code list [--count N]` | List uploaded code blobs |
| `$VW call <pid> Service/Query --args '[]' [--idl <path>]` | Sails read-only query (free; v2 IDL auto-resolved from on-chain WASM) |
| `$VW discover <pid> [--idl <path>]` | Introspect Sails services, methods, events (v2 auto-resolved) |
| `$VW idl import <path.idl> (--code-id <hex> \| --program <hex\|ss58>)` | Seed local IDL cache (v1 programs or out-of-band IDLs) |
| `$VW idl list` | List cached IDL entries (codeId, version, source, importedAt, idlSizeBytes) |
| `$VW idl remove <code-id>` | Remove one cache entry (idempotent) |
| `$VW idl clear [--yes]` | Wipe entire cache (terraform-style: bare invocation previews; `--yes` commits) |
| `$VW state read <pid>` | Read raw program state |
| `$VW mailbox read [address]` | Read mailbox messages |
| `$VW inbox list [--since <duration>] [--limit <n>]` | Query captured mailbox messages from event store |
| `$VW inbox read <messageId>` | Read a specific captured message |
| `$VW events list [--type <t>] [--since <d>] [--program <id>]` | Query captured events from event store |
| `$VW events prune [--older-than <duration>]` | Delete old events |
| `$VW query <pallet> <method> [args...]` | Generic storage query |
| `$VW vft balance <token> [account] --idl <path>` | Fungible token balance |
| `$VW vft info <token> --idl <path>` | Token name, symbol, decimals, total supply |
| `$VW vft allowance <token> <owner> <spender> --idl <path>` | Token allowance |
| `$VW dex pairs --factory <addr>` | List DEX trading pairs |
| `$VW dex pool <t0> <t1> --factory <addr>` | Pool reserves and prices |
| `$VW dex quote <tIn> <tOut> <amount> --factory <addr>` | Swap quote with price impact |

### Write (account required — add `--account <name>`)

| Command | Purpose |
|---------|---------|
| `$VW transfer <to> <amount>` | Transfer VARA tokens |
| `$VW program upload <wasm> [--idl <path>] [--init <name>] [--args <json>] [--payload <hex>] [--value <v>]` | Upload + init program (use --idl for auto-encoding) |
| `$VW program deploy <codeId> [--idl <path>] [--init <name>] [--args <json>] [--payload <hex>] [--value <v>]` | Deploy from existing code (use --idl for auto-encoding) |
| `$VW code upload <wasm>` | Upload code blob only |
| `$VW message send <dest> [--payload <hex>] [--value <v>] [--voucher <id>]` | Send message to any actor (program, user, wallet) |
| `$VW message reply <mid> [--payload <hex>] [--voucher <id>]` | Reply to a message |
| `$VW mailbox claim <messageId>` | Claim value from mailbox message |
| `$VW call <pid> Service/Function --args '[...]' --value <v> --units human\|raw [--idl <path>]` | Sails state-changing call (response includes decoded `events: [...]`) |
| `$VW call <pid> Service/Function --estimate [--idl <path>]` | Estimate gas cost without sending |
| `$VW call <pid> Service/Function --dry-run [--idl <path>]` | Encode SCALE payload + return `destination` — no signing, no submit, no wallet |
| `$VW call <pid> Service/Function --dry-run --estimate [--idl <path>]` | Encode AND estimate gas (compose, account required since 0.15.0) |
| `$VW call <pid> Service/Function --args-file <path> [--idl <path>]` | Read `--args` JSON from file (use `-` for stdin) — avoids shell-escape on nested JSON |
| `$VW vft transfer <token> <to> <amount> --idl <path>` | Transfer fungible tokens |
| `$VW vft transfer-from <token> <from> <to> <amount> --idl <path>` | Transfer from approved allowance |
| `$VW vft approve <token> <spender> <amount> --idl <path>` | Approve token spender |
| `$VW vft mint <token> <to> <amount> --idl <path>` | Admin token minting |
| `$VW vft burn <token> <from> <amount> --idl <path>` | Admin token burning |
| `$VW dex swap <tIn> <tOut> <amount> --factory <addr> [--slippage <bps>]` | Swap tokens (auto-approves) |
| `$VW dex add-liquidity <t0> <t1> <a0> <a1> --factory <addr>` | Add pool liquidity |
| `$VW dex remove-liquidity <t0> <t1> <lp> --factory <addr>` | Remove pool liquidity |
| `$VW voucher issue <spender> <value>` | Issue gas voucher (see `../../references/voucher-and-signless-flows.md`) |
| `$VW voucher revoke <spender> <voucherId>` | Revoke voucher |
| `$VW faucet [address]` | Request testnet TVARA tokens (auto-connects to testnet) |
| `$VW sign <data> [--hex]` | Sign arbitrary data with wallet key (raw sr25519) |
| `$VW tx <pallet> <method> [args...]` | Submit generic extrinsic |

### Verify (no account needed)

| Command | Purpose |
|---------|---------|
| `$VW verify <data> <signature> <address> [--hex]` | Verify signature against data and address |

### Monitor

| Command | Purpose |
|---------|---------|
| `$VW wait <messageId> [--timeout <s>]` | Wait for message reply |
| `$VW watch <pid> [--event Service/Event\|pallet:Name] [--idl <path>] [--no-decode]` | Stream program events (NDJSON; IDL adds `decoded.kind === 'sails'` block) |
| `$VW subscribe blocks [--finalized]` | Stream new/finalized blocks (NDJSON + SQLite) |
| `$VW subscribe messages <pid> [--event Service/Event\|pallet:Name] [--idl <path>] [--no-decode]` | Stream program messages/events (IDL-aware decoding; `--type` was renamed to `--event` in 0.15) |
| `$VW subscribe mailbox <address>` | Capture mailbox messages (survives between runs) |
| `$VW subscribe balance <address>` | Stream balance changes |
| `$VW subscribe transfers [--from <a>] [--to <a>]` | Stream transfer events |
| `$VW subscribe program <pid>` | Stream program state changes |

### Wallet Management

| Command | Purpose |
|---------|---------|
| `$VW wallet create [--name <n>]` | Create encrypted wallet |
| `$VW wallet import [--seed <s>] [--mnemonic <m>] [--json <path>]` | Import existing key |
| `$VW wallet list` | List all wallets |
| `$VW wallet export <name> [--decrypt]` | Export keyring JSON |
| `$VW wallet default [name]` | Get/set default wallet |
| `$VW init [--name <n>]` | Initialize config + default wallet |
| `$VW config list` | Show all config values |
| `$VW config set network testnet` | Persist network endpoint |
| `$VW config set <key> <value>` | Set any config key |
| `$VW config get <key>` | Get a config value |

## Common Workflows

### Deploy and interact with a Sails program

```bash
# 1. Upload program (auto-encodes Sails constructor from IDL)
UPLOAD=$($VW --account agent program upload ./target/wasm32-unknown-unknown/release/my_program.opt.wasm \
  --idl ./target/idl/my_program.idl --args '["MyToken", "MTK", 18]')
PROGRAM_ID=$(echo $UPLOAD | jq -r .programId)

# 2. Discover interface
$VW discover $PROGRAM_ID --idl ./target/idl/my_program.idl

# 3. Estimate gas before calling
$VW --account agent call $PROGRAM_ID MyService/DoSomething --args '["hello"]' --idl ./my_program.idl --estimate

# 4. Call a function (state-changing)
$VW --account agent call $PROGRAM_ID MyService/DoSomething --args '["hello"]' --idl ./my_program.idl

# 5. Query state (read-only, free)
$VW call $PROGRAM_ID MyService/GetState --args '[]' --idl ./my_program.idl
```

### Local node deployment

When deploying to a local dev node, use `--network local` or set the endpoint explicitly.

```bash
# Use --network shorthand (recommended)
$VW --network local wallet import --seed '//Alice' --name alice

# Or persist in config
$VW config set network local

# Or set for the session
export VARA_WS=ws://localhost:9944

# Deploy with IDL-based constructor encoding
UPLOAD=$($VW --account alice program upload ./target/wasm32-unknown-unknown/release/my_program.opt.wasm \
  --idl ./my_program.idl --args '["arg1"]')
PROGRAM_ID=$(echo $UPLOAD | jq -r .programId)

# Verify
$VW call $PROGRAM_ID MyService/GetState --args '[]' --idl ./my_program.idl
```

### Send message and wait for reply

```bash
RESULT=$($VW --account agent message send $PROGRAM_ID --payload 0x00)
MSG_ID=$(echo $RESULT | jq -r .messageId)

REPLY=$($VW wait $MSG_ID --timeout 60)
echo $REPLY | jq .payload
```

### Monitor program events

```bash
# Raw NDJSON
$VW watch $PROGRAM_ID | while read -r line; do
  echo "$line" | jq .
done

# IDL-aware: each UserMessageSent gets a `decoded: { kind: 'sails', service, event, data }` block
$VW watch $PROGRAM_ID --idl ./my-program.idl | jq '.decoded // .'

# Filter by Sails event (qualified or bare when unambiguous)
$VW watch $PROGRAM_ID --idl ./my-program.idl --event MyService/Transferred
$VW subscribe messages $PROGRAM_ID --idl ./my-program.idl --event Transferred --count 1 --timeout 30

# Force pallet vocab even with IDL loaded — replaces the dropped --pallet-event flag
$VW watch $PROGRAM_ID --idl ./my-program.idl --event pallet:UserMessageSent
```

Bare event names that resolve to multiple services hard-fail with `AMBIGUOUS_EVENT` listing the alternatives — qualify as `Service/Event` or use `pallet:Name` to force pallet vocabulary. `--no-decode` disables the opportunistic IDL auto-load entirely. The `decoded.kind` discriminator future-proofs the surface for additional decoder types.

### Preview a call without signing

`--dry-run` encodes the SCALE payload and exits with `willSubmit: false`. Works on machines with no wallet configured — useful for previewing payloads in CI, code review, or read-only environments.

```bash
# call dry-run — no account needed
$VW call $PROGRAM_ID MyService/DoSomething --args '["hello"]' --idl ./my-program.idl --dry-run

# program upload dry-run — reports resolved constructor + encoded init payload
$VW program upload ./my-program.opt.wasm --idl ./my-program.idl --args '["MyToken", "MTK", 18]' --dry-run
```

### Pass nested JSON via stdin (avoids shell-escape footguns)

`--args-file <path>` (or `-` for stdin) eliminates double-escape failures when the JSON contains hex actor IDs, 64-byte `vec u8` signatures, or other punctuation-heavy payloads.

```bash
echo '[["0xabcd...", 1000]]' | $VW --account agent call $PROGRAM_ID MyService/BatchTransfer --args-file - --idl ./my-program.idl
```

`--args` and `--args-file` are mutually exclusive (`INVALID_ARGS_SOURCE`). Stdin without a pipe attached fails fast with `STDIN_IS_TTY` instead of hanging on EOF.

### Subscribe to events (with persistence)

```bash
# Catch mailbox messages (they vanish after ~1 block)
$VW subscribe mailbox $MY_ADDRESS

# Wait for exactly 1 transfer, then exit (agent-friendly)
$VW subscribe transfers --count 1 --timeout 30

# Query captured events between runs
$VW inbox list --since 1h
$VW events list --type mailbox --limit 10
```

### Token operations

```bash
# Token info
$VW vft info $TOKEN_PROGRAM --idl ./vft.idl

# Check balance
$VW vft balance $TOKEN_PROGRAM --idl ./vft.idl

# Transfer
$VW --account agent vft transfer $TOKEN_PROGRAM $RECIPIENT 1000 --idl ./vft.idl

# Approve
$VW --account agent vft approve $TOKEN_PROGRAM $SPENDER 1000 --idl ./vft.idl
```

### DEX operations (Rivr)

```bash
# Check available pairs
$VW dex pairs --factory $FACTORY

# Get swap quote with price impact
$VW dex quote $TOKEN_IN $TOKEN_OUT 100 --factory $FACTORY

# Swap tokens (auto-approves input token)
$VW --account agent dex swap $TOKEN_IN $TOKEN_OUT 100 --factory $FACTORY --slippage 100
```

### Fund an account with a voucher

```bash
$VW --account sponsor voucher issue $SPENDER_ADDRESS 100 --duration 14400
```

### Sign and verify data

```bash
# Sign arbitrary data
SIG=$($VW --account agent sign "hello world" | jq -r .signature)

# Verify signature
$VW verify "hello world" $SIG $ADDRESS
```

## IDL Resolution

Sails commands (`call`, `discover`, `vft`, `dex`) need an IDL. Resolution order (since vara-wallet 0.13):

1. **`--idl <path>`** — local file, always works, takes precedence
2. **Local cache** — `~/.vara-wallet/idl-cache/<codeId>.cache.json`, populated automatically by previous fetches or by `idl import`
3. **On-chain WASM** — for v2 programs (sails ≥ 1.0.0-beta.1), IDL is extracted from the `sails:idl` custom section of the program's original WASM via `gearProgram.originalCodeStorage(codeId)` and cached
4. **Bundled IDLs** — standard VFT and Rivr DEX IDLs are bundled and validator-gated for `vft` / `dex` commands

For v2 programs the agent never needs `--idl` after the first call against the program — the cache handles subsequent calls for free. For v1 programs (no embedded IDL section), seed the cache once with `idl import`:

```bash
# Resolves codeId via RPC
$VW idl import ./my-program.idl --program <programId>

# Fully offline if you already know the codeId
$VW idl import ./my-program.idl --code-id 0x<hex>
```

> **v1 is the expected path for stable Sails builders.** This pack's stable baseline is `sails-rs 0.10.x`, which produces v1 WASM with no `sails:idl` custom section. vara-wallet 0.16+ surfaces this as `IDL_NOT_FOUND` with the explicit message "This is a v1 contract" and the `idl import` command pre-filled. Treat it as routine: pass `--idl <path>` for one-off use or run `idl import` once per machine. Pre-0.16 hedged "may be v1 or sails < 1.0.0-beta.1" with no clear next step.

The previous `metaStorageUrl` config key and `VARA_META_STORAGE` env var were **removed in 0.15.0** — the meta-storage endpoint had near-zero usable IDL coverage in practice. Stale entries in pre-0.15 config files are silently ignored.

## Output Parsing

All commands output JSON to stdout. Errors go to stderr as `{ error, code }`.

```bash
# Extract a field
$VW balance | jq -r .balance

# Check transaction success
RESULT=$($VW --account agent transfer $TO 1)
echo $RESULT | jq '.events[] | select(.section == "balances")'

# Verbose debug (stderr, won't break JSON parsing)
$VW --verbose balance 2>/dev/null | jq .
```

## Structured Errors (0.16+)

Program-execution failures surface as flat JSON on stderr — `reason` and `programMessage` are top-level keys, not nested under `meta`:

```json
{"code":"PROGRAM_ERROR","reason":"panic","programMessage":"<BareVariant>","error":"<full text>"}
```

`reason` ∈ `panic` | `unreachable` | `inactive` | `not_found`. `programMessage` is the bare Sails error variant — 0.16 strips the `called \`Result::unwrap()\` on an \`Err\` value:` wrapper that `#[export(unwrap_result)]` adds, so agents can switch on it directly:

```bash
ERR=$(vara-wallet --account agent call $PID Service/Method --args '[...]' --idl ./my.idl 2>&1 1>/dev/null)
case "$(echo "$ERR" | jq -r '.programMessage // ""')" in
  InsufficientBalance) refill ;;
  Unauthorized)        switch_account ;;
  *)                   echo "unhandled: $ERR" ;;
esac
```

`jq -r '.programMessage // ""'` returns empty string on pre-0.16 builds, so the case-switch degrades safely to the default branch. Pre-0.16 emitted only `{error, code}`.

## Network Switching

```bash
# Shorthand (recommended)
$VW --network testnet balance

# Per-command with full URL
$VW --ws wss://testnet.vara.network balance

# Persist across sessions
$VW config set network testnet

# Session-wide env var
export VARA_WS=wss://testnet.vara.network
```

**Endpoint resolution order:** `--ws` > `--network` > `VARA_WS` env > `config.wsEndpoint` > default.

| Network | Endpoint | `--network` shorthand |
|---------|----------|----------------------|
| Mainnet | `wss://rpc.vara.network` (default) | `--network mainnet` |
| Testnet | `wss://testnet.vara.network` | `--network testnet` |
| Local | `ws://localhost:9944` | `--network local` |

Connection timeout is 10s. Bad endpoints fail fast with `CONNECTION_TIMEOUT` error instead of hanging.

For full network endpoint and account format details, see `../../references/vara-network-endpoints.md`.

## Units

1 VARA = 10^12 minimal units (12 decimals). Amounts default to VARA.

```bash
$VW transfer $TO 1.5                        # 1.5 VARA
$VW transfer $TO 1500000000000 --units raw   # same in raw units
```

All `--units` flags use a unified `human|raw` vocabulary (since vara-wallet 0.15):
- **Native commands** (`balance`, `transfer`, `message`, `call`, `voucher`, `program`): `human` (default) = VARA decimals (12). `raw` = minimal units passthrough.
- **VFT** and **DEX** commands: `raw` (default) = minimal units passthrough. `human` = use the token's declared decimals (queried at runtime).
- The legacy literals `vara` (native commands) and `token` (VFT/DEX) used pre-0.15 are **rejected** with `INVALID_UNITS`. Update any committed agent scripts written against vara-wallet@0.10.x.

Existential deposit is ~10 VARA on mainnet.

## Error Recovery

| Code | Meaning | Action |
|------|---------|--------|
| `NO_ACCOUNT` | No signing account | Add `--account <name>` |
| `PASSPHRASE_REQUIRED` | Encrypted wallet, no passphrase | Check `~/.vara-wallet/.passphrase` exists |
| `DECRYPT_FAILED` | Wrong passphrase | Verify passphrase file content |
| `CONNECTION_TIMEOUT` | WS/light client connect timed out (10s) | Check endpoint URL, network connectivity |
| `WRONG_NETWORK` | Command not available on this network | Use `--network testnet` for faucet |
| `TX_TIMEOUT` | Transaction didn't land in 60s | Retry — network congestion |
| `TX_FAILED` | On-chain failure | Inspect `.events` in output |
| `IDL_NOT_FOUND` | No Sails IDL | v1 contracts (stable Sails 0.10.x baseline): error says "This is a v1 contract" and prints the `idl import` command in 0.16+. Pass `--idl <path>` for one-off use or `idl import` once per machine. v2 programs auto-resolve from on-chain WASM |
| `METHOD_NOT_FOUND` | Method not in IDL | Check `discover` output; cross-service hint is suggested in the error |
| `AMBIGUOUS_EVENT` | Bare Sails event name maps to multiple services | Qualify as `--event Service/Event` or use `pallet:Name` |
| `INVALID_ARGS_FORMAT` | `--args` shape mismatch (0.16+) | Sails methods take POSITIONAL args. Pass as a JSON array: `'[arg1, arg2]'`. Single-struct-arg methods also accept the bare object form: `'{"field": ...}'`. Multi-arg methods reject named-arg objects |
| `INVALID_ADDRESS` | Typed `actor_id` field got the wrong shape (0.16+) | Read the field name from the error (`Invalid ActorId for "<field>": ...`) and fix that field — use hex (`0x` + 64 chars), SS58, or 32-byte array. Don't rewrite the whole payload |
| `INVALID_ARGS_SOURCE` | `--args` and `--args-file` used together | Pick one |
| `STDIN_IS_TTY` | `--args-file -` used with no pipe attached | Pipe JSON in or pass a real path |
| `CONFLICTING_OPTIONS` | Mutually exclusive options (e.g. `--network` + `--ws`) | Pick one. Note: `--dry-run` + `--estimate` *compose* on `call` since 0.15 |
| `INVALID_UNITS` | `--units` value isn't `human` or `raw` | Use the unified vocabulary; legacy `vara` / `token` literals were retired in 0.15 |
| `PROGRAM_ERROR` | Sails program execution failed | Inspect top-level `reason` and `programMessage`. State problem — do NOT bump `--gas-limit`. See *Structured Errors (0.16+)* for the JSON shape, `reason` enum, and case-switch pattern |
| `PERMISSION_DENIED` | OS-level permission error (e.g. `idl clear --yes` on a read-only dir) | Check filesystem permissions on `~/.vara-wallet/` |
| `INVALID_NETWORK` | Unknown `--network` value | Use mainnet, testnet, or local |
| `INVALID_CONFIG_KEY` | Unknown config key | Use `config list` to see valid keys (note: `metaStorageUrl` removed in 0.15.0) |

## Guardrails

- Never pass secrets (seeds, mnemonics, passphrases) as CLI arguments in committed scripts. Use wallet files.
- Never use `--show-secret` in automated flows. Secrets should stay in encrypted wallet files.
- Always use `--account <name>` for signing, not `--seed`.
- Gas is auto-calculated — omit `--gas-limit` unless you have a specific reason. `calculateGas` failures (program panic during dry-run) surface as classified `PROGRAM_ERROR` in 0.16+, not opaque gas errors — see Error Recovery.
- Messages are async. After `message send`, use `wait` to get the reply.
- `call` auto-detects queries vs functions — no need to specify.
- When targeting a local dev node, use `--network local` or `VARA_WS=ws://localhost:9944`. The default endpoint is mainnet.
- Use `config set network testnet` to persist network choice across sessions.
- `program list` returns 100 programs by default. Use `--all` for unlimited.
- `faucet` only works on testnet. It refuses mainnet endpoints automatically.
- If `sails-local-smoke` is green and you need to interact with a deployed program on a live network, switch to this skill.
