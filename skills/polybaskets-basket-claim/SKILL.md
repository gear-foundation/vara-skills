---
name: polybaskets-basket-claim
description: Use when the agent needs to claim payout from a settled basket via vara-wallet. Do not use before settlement is finalized.
---

# Basket Claim

Claim payout from a settled PolyBaskets basket via `vara-wallet`.

## Setup

```bash
BASKET_MARKET="0x4d47cb784a0b1e3788181a6cedb52db11aad0cef4268848e612670f7d950f089"
BET_LANE="0x1764868fba789527b9ded67a8bd0052517ceb308e7b2f08b9c7cf85efbed5dbc"
IDL="idl/polybaskets/polymarket-mirror.idl"
BET_LANE_IDL="idl/polybaskets/bet_lane_client.idl"
```

## Pre-Check Workflow

### 1. Verify settlement is finalized

```bash
vara-wallet call $BASKET_MARKET BasketMarket/GetSettlement \
  --args '[<basket_id>]' --idl $IDL
```

Check the result:
- `status: "Finalized"` — ready to claim
- `status: "Proposed"` — challenge window not yet passed. If you have the settler role, see `../polybaskets-basket-settle/SKILL.md` to finalize. Otherwise, wait for the settler to finalize (challenge window is ~12 minutes from `proposed_at`).
- Error `SettlementNotFound` — not yet settled

```bash
# Parse settlement status
vara-wallet call $BASKET_MARKET BasketMarket/GetSettlement \
  --args '[<basket_id>]' --idl $IDL | jq '.ok.status'
```

Get your hex address first (SS58 won't work for actor_id args):
```bash
MY_ADDR=$(vara-wallet balance | jq -r .address)
```

### 2. Verify position exists and is unclaimed

```bash
# VARA lane
vara-wallet call $BASKET_MARKET BasketMarket/GetPositions \
  --args '["'$MY_ADDR'"]' --idl $IDL | jq '.[] | select(.basket_id == <basket_id>)'

# BET lane
vara-wallet call $BET_LANE BetLane/GetPosition \
  --args '["'$MY_ADDR'", <basket_id>]' --idl $BET_LANE_IDL
```

Check `claimed: false`.

## Claim (VARA Lane)

For baskets with `asset_kind: "Vara"`:

```bash
vara-wallet --account agent call $BASKET_MARKET BasketMarket/Claim \
  --args '[<basket_id>]' --idl $IDL
```

Returns `u128` — payout amount in minimal VARA units (divide by 10^12 for VARA).

### Example

```bash
# Claim from basket 0
PAYOUT=$(vara-wallet --account agent call $BASKET_MARKET BasketMarket/Claim \
  --args '[0]' --idl $IDL)
echo "Payout: $PAYOUT"
```

## Claim (BET Token Lane)

For baskets with `asset_kind: "Bet"`:

```bash
vara-wallet --account agent call $BET_LANE BetLane/Claim \
  --args '[<basket_id>]' --idl $BET_LANE_IDL
```

Returns `u256` — payout amount in BET token units.

### Example

```bash
# Claim from basket 1 via BET lane
vara-wallet --account agent call $BET_LANE BetLane/Claim \
  --args '[1]' --idl $BET_LANE_IDL
```

## Payout Calculation

```
payout = shares * (settlement_index / entry_index)
```

The `payout_per_share` is pre-computed in the Settlement struct during proposal. You can preview your expected payout before claiming:

```bash
# Get settlement payout_per_share
SETTLEMENT=$(vara-wallet call $BASKET_MARKET BasketMarket/GetSettlement \
  --args '[<basket_id>]' --idl $IDL)
echo $SETTLEMENT | jq '.ok.payout_per_share'
```

See `../../references/polybaskets-index-math.md` for detailed formula and examples.

## Verify After Claim

```bash
# Check position is now claimed
vara-wallet call $BASKET_MARKET BasketMarket/GetPositions \
  --args '["'$MY_ADDR'"]' --idl $IDL | jq '.[] | select(.basket_id == <basket_id>) | .claimed'

# Check VARA balance increased
vara-wallet balance
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `SettlementNotFinalized` | Settlement not yet finalized | Wait for finalization |
| `AlreadyClaimed` | Already claimed this basket | No action needed |
| `NothingToClaim` | No position in this basket | Verify position exists |
| `SettlementNotFound` | No settlement proposed | Wait for settler to propose |
| `TransferFailed` | VARA transfer failed | Check contract balance, retry |
