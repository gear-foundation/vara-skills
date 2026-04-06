# PolyBaskets Program IDs and Network Config

## Shell Variables

Copy-paste this block at the start of any PolyBaskets interaction session:

```bash
# Program IDs (Vara mainnet)
# TODO: update these with mainnet deployment addresses before launch
BASKET_MARKET="0x4d47cb784a0b1e3788181a6cedb52db11aad0cef4268848e612670f7d950f089"
BET_TOKEN="0x0a54e06ac29344f127d90b669f4fcd9de86efa4a67c3b8568f6182cf203d4294"
BET_LANE="0x1764868fba789527b9ded67a8bd0052517ceb308e7b2f08b9c7cf85efbed5dbc"

# IDL paths (relative to vara-skills root)
IDL="idl/polybaskets/polymarket-mirror.idl"
BET_TOKEN_IDL="idl/polybaskets/bet_token_client.idl"
BET_LANE_IDL="idl/polybaskets/bet_lane_client.idl"
```

## Program Roles

| Program | Purpose |
|---------|---------|
| BasketMarket | Core contract: baskets, CHIP bets, settlements, claims |
| BetToken | CHIP fungible token with daily claim and streak bonuses |
| BetLane | Betting lane using CHIP tokens |

## Network

Vara mainnet (`wss://rpc.vara.network`) is vara-wallet's default. No `--network` flag or env var needed.

```bash
# Just works — mainnet by default
vara-wallet call $BASKET_MARKET BasketMarket/GetBasketCount --args '[]' --idl $IDL
```

## Gas — Voucher System

Agents get gas through the PolyBaskets voucher claim process. No VARA purchase needed.

```bash
# TODO: add voucher claim command/URL when the process is finalized
```

## Actor ID Format

Sails `actor_id` args require **hex format** — SS58 addresses are rejected:

```bash
# Get your hex address
MY_ADDR=$(vara-wallet balance | jq -r .address)
# → 0xe00801c1a5b8aef60d3a...
```

## Token Units

Both VARA and CHIP use 12 decimals. Method args for `u256`/`u128` amounts expect **raw units**:
- 100 CHIP = `"100000000000000"` (100 * 10^12)
- 1 CHIP = `"1000000000000"` (10^12)
- `--value` flag (for VARA lane) auto-converts from VARA by default

## vara-wallet Response Format

All vara-wallet output is JSON:

```bash
# Queries return:
{"result": <value>}                          # plain types (u64, bool, str)
{"result": {"ok": {...}}}                    # Result<T, E> success
{"result": {"err": "ErrorVariant"}}          # Result<T, E> error

# Mutations return:
{"txHash": "0x...", "blockHash": "0x...", "blockNumber": 123, "messageId": "0x...", "result": <value>}
```

Extract values with jq:
```bash
# Query result
vara-wallet ... | jq -r '.result'
vara-wallet ... | jq '.result.ok'

# Mutation result
vara-wallet ... | jq -r '.result'
```
