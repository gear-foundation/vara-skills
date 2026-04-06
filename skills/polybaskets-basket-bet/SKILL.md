---
name: polybaskets-basket-bet
description: Use when the agent needs to claim CHIP tokens and place a bet on an existing basket via vara-wallet. This is the primary agent action. Do not use for basket creation, querying, or claiming payouts.
---

# Basket Bet

Claim CHIP tokens and bet on a PolyBaskets basket via `vara-wallet`.

## Setup

```bash
BASKET_MARKET="0x4d47cb784a0b1e3788181a6cedb52db11aad0cef4268848e612670f7d950f089"
BET_TOKEN="0x0a54e06ac29344f127d90b669f4fcd9de86efa4a67c3b8568f6182cf203d4294"
BET_LANE="0x1764868fba789527b9ded67a8bd0052517ceb308e7b2f08b9c7cf85efbed5dbc"
IDL="idl/polybaskets/polymarket-mirror.idl"
BET_TOKEN_IDL="idl/polybaskets/bet_token_client.idl"
BET_LANE_IDL="idl/polybaskets/bet_lane_client.idl"
```

## CHIP Lane (Primary Path)

Most baskets use `asset_kind: "Bet"` (CHIP tokens). This is the default agent workflow.

### Step 1: Claim Daily CHIP

Agents get free CHIP tokens every day. Consecutive days build a streak that increases the amount (100 CHIP base, +8.33/day streak, max 150 CHIP at 7-day cap).

```bash
# Get your hex address (required for actor_id args — SS58 won't work)
MY_ADDR=$(vara-wallet balance | jq -r .address)

# Check if claim is available and how much you'll get
vara-wallet call $BET_TOKEN BetToken/GetClaimPreview \
  --args '["'$MY_ADDR'"]' --idl $BET_TOKEN_IDL

# Claim daily CHIP (do this every day to build streak)
vara-wallet --account agent call $BET_TOKEN BetToken/Claim \
  --args '[]' --idl $BET_TOKEN_IDL
```

The response includes your `streak_days` and `total_claimed`. Higher streak = more CHIP per claim.

### Step 2: Check CHIP Balance

```bash
vara-wallet call $BET_TOKEN BetToken/BalanceOf \
  --args '["'$MY_ADDR'"]' --idl $BET_TOKEN_IDL
```

### Step 3: Pick a Basket

Browse active baskets and find one to bet on:

```bash
# How many baskets exist
vara-wallet call $BASKET_MARKET BasketMarket/GetBasketCount --args '[]' --idl $IDL

# View a specific basket
vara-wallet call $BASKET_MARKET BasketMarket/GetBasket --args '[0]' --idl $IDL
```

Check that `status` is `"Active"` and `asset_kind` is `"Bet"`.

### Step 4: Approve CHIP Spend

Allow the BetLane contract to spend your CHIP:

```bash
vara-wallet --account agent call $BET_TOKEN BetToken/Approve \
  --args '["'$BET_LANE'", <amount>]' --idl $BET_TOKEN_IDL
```

### Step 5: Place Bet

```bash
vara-wallet --account agent call $BET_LANE BetLane/PlaceBet \
  --args '[<basket_id>, <amount>, <index_at_creation_bps>]' --idl $BET_LANE_IDL
```

Returns `u256` — shares received.

### Complete CHIP Lane Example

```bash
# 0. Get hex address (once per session)
MY_ADDR=$(vara-wallet balance | jq -r .address)

# 1. Claim daily CHIP
vara-wallet --account agent call $BET_TOKEN BetToken/Claim \
  --args '[]' --idl $BET_TOKEN_IDL

# 2. Approve BetLane to spend 100 CHIP
vara-wallet --account agent call $BET_TOKEN BetToken/Approve \
  --args '["'$BET_LANE'", "100000000000000"]' --idl $BET_TOKEN_IDL

# 3. Bet 100 CHIP on basket 0 at index 7500
vara-wallet --account agent call $BET_LANE BetLane/PlaceBet \
  --args '[0, "100000000000000", 7500]' --idl $BET_LANE_IDL

# 4. Verify position
vara-wallet call $BET_LANE BetLane/GetPosition \
  --args '["'$MY_ADDR'", 0]' --idl $BET_LANE_IDL
```

**Important:** CHIP has 12 decimals. 100 CHIP = `100000000000000` (100 * 10^12) in raw units. The `BetLane/PlaceBet` `amount` and `BetToken/Approve` `value` args use raw units (u256).

## Calculating index_at_creation_bps

The `index_at_creation_bps` is your entry price (1-10000). It determines your payout.

**Formula:** `index = sum(weight_bps[i] / 10000 * probability[i])` then `bps = round(index * 10000)`

**Step-by-step:** fetch live prices for each basket item, then compute:

```bash
# 1. Get the basket items
BASKET=$(vara-wallet call $BASKET_MARKET BasketMarket/GetBasket \
  --args '[3]' --idl $IDL)

# 2. Fetch prices for each item's slug from Polymarket
curl -s "https://gamma-api.polymarket.com/markets?slug=russia-ukraine-ceasefire-before-gta-vi-554" \
  | python3 -c "import sys,json; m=json.load(sys.stdin)[0]; print(f'YES={m[\"outcomePrices\"][0]} NO={m[\"outcomePrices\"][1]}')"

# 3. Calculate index (example: 3 items)
python3 -c "
items = [
    (4000, 0.535),  # weight_bps, probability of selected outcome
    (3500, 0.595),
    (2500, 0.650),
]
index = sum(w/10000 * p for w, p in items)
print(f'index_at_creation_bps = {round(index * 10000)}')
"
# → index_at_creation_bps = 5848
```

**Why it matters:** `payout = shares * (settlement_index / entry_index)`. Lower entry index = higher potential return if the basket resolves well. See `../../references/polybaskets-index-math.md`.

## VARA Lane (asset_kind: Vara)

Some baskets accept native VARA instead of CHIP. Check basket's `asset_kind`.

```bash
# Bet 100 VARA on basket 0 at index 6120
vara-wallet --account agent call $BASKET_MARKET BasketMarket/BetOnBasket \
  --args '[0, 6120]' \
  --value 100 \
  --idl $IDL
```

Returns `u128` — shares received (equal to VARA sent in minimal units).

Note: VARA lane may be disabled on some deployments. Check with:
```bash
vara-wallet call $BASKET_MARKET BasketMarket/IsVaraEnabled --args '[]' --idl $IDL
```

## After Betting

- Check your position: `../polybaskets-basket-query/SKILL.md`
- Wait for settlement, then claim payout: `../polybaskets-basket-claim/SKILL.md`
- Come back tomorrow for more CHIP: repeat Step 1

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidIndexAtCreation` | bps is 0 or > 10000 | Use value 1-10000 |
| `InvalidBetAmount` | No `--value` attached (VARA lane) | Add `--value <amount>` |
| `BasketNotActive` | Basket in settlement/settled | Cannot bet on non-active baskets |
| `BasketAssetMismatch` | Wrong lane for basket | Check basket's `asset_kind` |
| `VaraDisabled` | VARA betting off | Use CHIP lane instead |
| `AmountBelowMinBet` | CHIP amount too low | Check BetLane config for min_bet |
| `AmountAboveMaxBet` | CHIP amount too high | Check BetLane config for max_bet |
| `BetTokenTransferFromFailed` | Insufficient CHIP balance or approval | Claim more tokens or increase approval |
