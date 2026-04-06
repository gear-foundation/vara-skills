---
name: polybaskets-basket-settle
description: Use when the agent has the settler role and needs to propose or finalize a basket settlement via vara-wallet. Do not use without settler role permissions. Do not use for regular user actions.
---

# Basket Settle

Propose and finalize settlement for PolyBaskets baskets. **Requires the settler role.**

## Setup

```bash
BASKET_MARKET="0x4d47cb784a0b1e3788181a6cedb52db11aad0cef4268848e612670f7d950f089"
IDL="idl/polybaskets/polymarket-mirror.idl"
```

## Verify Settler Role

Only the address assigned as `settler_role` in the contract config can call settlement methods.

```bash
# Check who has settler role
vara-wallet call $BASKET_MARKET BasketMarket/GetConfig --args '[]' --idl $IDL | jq '.settler_role'

# Check agent's address
vara-wallet wallet list | jq -r '.[0].address'
```

If your address does not match `settler_role`, you cannot settle. Contact the admin.

## Settlement Flow

```
1. Check basket is Active
2. Verify all items have resolved on Polymarket
3. ProposeSettlement → starts 12-minute challenge window
4. Wait for challenge_deadline to pass
5. FinalizeSettlement → basket becomes Settled, users can claim
```

## Step 1: Check Basket Status

```bash
vara-wallet call $BASKET_MARKET BasketMarket/GetBasket \
  --args '[<basket_id>]' --idl $IDL | jq '.ok.status'
```

Must be `"Active"`.

## Step 2: Check Polymarket Resolution

For each item in the basket, check if the market has resolved on Polymarket:

```bash
curl -s "https://gamma-api.polymarket.com/markets?slug=<poly_slug>" | jq '.[0] | {closed, outcomePrices}'
```

All items must be resolved (`closed: true`) with final prices near 0 or 1.

## Step 3: Propose Settlement

Build the `item_resolutions` array — one `ItemResolution` per basket item:

```json
{
  "item_index": 0,
  "resolved": "YES",
  "poly_slug": "will-btc-hit-100k",
  "poly_condition_id": "0xabc123...",
  "poly_price_yes": 9900,
  "poly_price_no": 100
}
```

Rules:
- Provide exactly one resolution per basket item
- `item_index` is 0-based, must be unique, and within basket items range
- `poly_slug` must match the basket item's slug exactly
- `poly_price_yes` + `poly_price_no` should reflect final Polymarket prices in bps
- `resolved` is the final outcome: `"YES"` or `"NO"`
- `poly_condition_id` is optional

### Example: Propose settlement for a 2-item basket

```bash
vara-wallet --account agent call $BASKET_MARKET BasketMarket/ProposeSettlement \
  --args '[
    0,
    [
      {
        "item_index": 0,
        "resolved": "YES",
        "poly_slug": "will-btc-hit-100k",
        "poly_condition_id": null,
        "poly_price_yes": 9900,
        "poly_price_no": 100
      },
      {
        "item_index": 1,
        "resolved": "NO",
        "poly_slug": "will-eth-hit-5k",
        "poly_condition_id": null,
        "poly_price_yes": 200,
        "poly_price_no": 9800
      }
    ],
    "Resolved via Polymarket API"
  ]' \
  --idl $IDL
```

After proposal, the basket enters `SettlementPending` status and the 12-minute challenge window begins.

## Step 4: Wait for Challenge Window

```bash
# Check challenge deadline
vara-wallet call $BASKET_MARKET BasketMarket/GetSettlement \
  --args '[<basket_id>]' --idl $IDL | jq '.ok | {status, challenge_deadline, proposed_at}'
```

The `challenge_deadline` is a block timestamp. The liveness window is configured in `liveness_ms` (default 720000ms = 12 minutes).

Wait until the current block timestamp exceeds `challenge_deadline`.

## Step 5: Finalize Settlement

```bash
vara-wallet --account agent call $BASKET_MARKET BasketMarket/FinalizeSettlement \
  --args '[<basket_id>]' --idl $IDL
```

After finalization:
- Basket status becomes `Settled`
- `finalized_at` is set
- Users can now claim payouts via `../polybaskets-basket-claim/SKILL.md`

## Verify

```bash
vara-wallet call $BASKET_MARKET BasketMarket/GetSettlement \
  --args '[<basket_id>]' --idl $IDL | jq '.ok | {status, payout_per_share, finalized_at}'
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Unauthorized` | Not the settler role | Check config for settler_role address |
| `BasketNotActive` | Basket already in settlement | Check status |
| `SettlementAlreadyExists` | Already proposed | Wait and finalize |
| `InvalidResolutionCount` | Wrong number of resolutions | Provide one per item |
| `ResolutionSlugMismatch` | Slug doesn't match basket item | Use exact slug from basket |
| `DuplicateResolutionIndex` | Same item_index twice | Make indices unique |
| `ResolutionIndexOutOfBounds` | Index >= items count | Use 0 to items.length-1 |
| `ChallengeDeadlineNotPassed` | Too early to finalize | Wait for challenge window |
| `SettlementNotProposed` | No proposal exists | Propose first |
| `SettlementNotFinalized` | Settlement not yet finalized | Call FinalizeSettlement after challenge window |
