---
name: polybaskets-basket-create
description: Use when the agent needs to create a new prediction basket on-chain via vara-wallet. Do not use for betting, querying, or settlement.
---

# Basket Create

Create a new prediction basket on PolyBaskets via `vara-wallet`.

## Setup

```bash
BASKET_MARKET="0x4d47cb784a0b1e3788181a6cedb52db11aad0cef4268848e612670f7d950f089"
IDL="idl/polybaskets/polymarket-mirror.idl"
```

Ensure you have a wallet and VARA for gas:

```bash
vara-wallet wallet list
vara-wallet balance
```

## Finding Polymarket Markets

Search for active markets on Polymarket to use as basket items:

```bash
# Search by keyword
curl -s "https://gamma-api.polymarket.com/markets?closed=false&limit=5" \
  | python3 -c "
import sys, json
for m in json.load(sys.stdin):
    prices = m.get('outcomePrices', ['?','?'])
    print(f\"id={m['id']}  slug={m['slug']}\")
    print(f\"  {m['question'][:80]}\")
    print(f\"  YES={prices[0]}  NO={prices[1]}\")
    print()
"
```

**Important:** `poly_market_id` is the **numeric Polymarket ID** (e.g. `"540816"`), not the hex `conditionId`. Use the `id` field from the API response.

## Pre-Check

Most deployments run in CHIP-only mode. Check VARA status:

```bash
vara-wallet call $BASKET_MARKET BasketMarket/IsVaraEnabled --args '[]' --idl $IDL
```

If false (typical), create a `"Bet"` basket (CHIP lane).

## Validation Rules

Before sending the transaction, validate locally:

| Rule | Constraint |
|------|-----------|
| Name | Non-empty, max 48 characters |
| Description | Max 256 characters |
| Items | 1 to 10 items |
| Weights | All `weight_bps` must sum to exactly 10000 |
| No duplicates | Same `poly_market_id` + `selected_outcome` cannot appear twice |
| poly_market_id | Max 128 characters |
| poly_slug | Max 128 characters |
| asset_kind | `"Vara"` or `"Bet"` |

## Create Basket

### Arguments

```
CreateBasket(name: str, description: str, items: vec BasketItem, asset_kind: BasketAssetKind) -> u64
```

Each `BasketItem`:
```json
{
  "poly_market_id": "<polymarket condition_id>",
  "poly_slug": "<polymarket slug>",
  "weight_bps": 5000,
  "selected_outcome": "YES"
}
```

### Example: 2-item VARA basket

```bash
vara-wallet --account agent call $BASKET_MARKET BasketMarket/CreateBasket \
  --args '[
    "Tech Rally Basket",
    "Betting on major tech milestones",
    [
      {
        "poly_market_id": "0x1234abcd",
        "poly_slug": "will-btc-hit-100k",
        "weight_bps": 6000,
        "selected_outcome": "YES"
      },
      {
        "poly_market_id": "0x5678efgh",
        "poly_slug": "will-eth-hit-5k",
        "weight_bps": 4000,
        "selected_outcome": "YES"
      }
    ],
    "Vara"
  ]' \
  --idl $IDL
```

### Example: 3-item BET basket

```bash
vara-wallet --account agent call $BASKET_MARKET BasketMarket/CreateBasket \
  --args '[
    "AI Regulation Bundle",
    "Outcomes related to AI policy",
    [
      {
        "poly_market_id": "condition_id_1",
        "poly_slug": "ai-regulation-2025",
        "weight_bps": 4000,
        "selected_outcome": "YES"
      },
      {
        "poly_market_id": "condition_id_2",
        "poly_slug": "openai-ipo-2025",
        "weight_bps": 3500,
        "selected_outcome": "YES"
      },
      {
        "poly_market_id": "condition_id_3",
        "poly_slug": "eu-ai-act-enforcement",
        "weight_bps": 2500,
        "selected_outcome": "NO"
      }
    ],
    "Bet"
  ]' \
  --idl $IDL
```

## Parse Result

The call returns a `u64` basket ID:

```bash
RESULT=$(vara-wallet --account agent call $BASKET_MARKET BasketMarket/CreateBasket \
  --args '[...]' --idl $IDL)
BASKET_ID=$(echo $RESULT | jq -r '.result // .ok // .')
echo "Created basket: $BASKET_ID"
```

## After Creation

- Verify: `vara-wallet call $BASKET_MARKET BasketMarket/GetBasket --args "[$BASKET_ID]" --idl $IDL`
- Place a bet: see `../polybaskets-basket-bet/SKILL.md`
- Share the basket ID for others to bet on

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `InvalidWeights` | Weights don't sum to 10000 | Adjust weight_bps values |
| `NoItems` | Empty items array | Add at least 1 item |
| `TooManyItems` | More than 10 items | Remove items |
| `DuplicateBasketItem` | Same market+outcome twice | Remove duplicate |
| `VaraDisabled` | VARA mode off | Use `"Bet"` asset_kind instead |
| `NameTooLong` | Name > 48 chars | Shorten name |

See `../../references/polybaskets-error-codes.md` for all error variants.
