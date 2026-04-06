# PolyBaskets Index Calculation and Payout Formula

## Basket Index

The basket index is a weighted probability score across all items:

```
index = sum( weight_bps[i] / 10000 * probability[i] )  for each item i
```

- `weight_bps[i]`: item weight in basis points (0-10000), all weights must sum to 10000
- `probability[i]`: current probability of the selected outcome (0.0 to 1.0)

**On-chain representation:** `index_at_creation_bps = round(index * 10000)` as `u16` (1-10000).

### Example

A 2-item basket:
- Item 1: BTC > $100k (YES), weight 6000 bps (60%), probability 0.72
- Item 2: ETH > $5k (YES), weight 4000 bps (40%), probability 0.45

```
index = (6000/10000 * 0.72) + (4000/10000 * 0.45)
      = 0.432 + 0.180
      = 0.612

index_at_creation_bps = round(0.612 * 10000) = 6120
```

## Payout Formula

After settlement, each user's payout is:

```
payout = shares * (settlement_index_bps / index_at_creation_bps)
```

- `shares`: VARA amount the user bet (stored as `u128` in minimal units)
- `settlement_index_bps`: the basket's resolved index after all markets settle
- `index_at_creation_bps`: the index when the user placed their bet

The contract stores `payout_per_share` in the Settlement struct, pre-computed during proposal.

### Worked Examples

**Profit case:**
- User bets 100 VARA at index 6120 bps (0.612)
- All items resolve YES: settlement index = 10000 bps (1.0)
- Payout = 100 * (10000 / 6120) = 163.4 VARA (+63.4% profit)

**Loss case:**
- User bets 100 VARA at index 6120 bps (0.612)
- Item 1 resolves NO: settlement index = 1800 bps (0.18)
- Payout = 100 * (1800 / 6120) = 29.4 VARA (-70.6% loss)

**Break-even:**
- Payout equals shares when settlement_index equals index_at_creation

## Settlement Index Calculation

During settlement, each item is resolved as YES (1.0) or NO (0.0). The settlement index uses the same weighted formula but with binary outcomes:

```
settlement_index = sum( weight_bps[i] / 10000 * resolved[i] )
```

Where `resolved[i]` is 1.0 if the resolved outcome matches the selected outcome, 0.0 otherwise.

## Key Constraints

- `index_at_creation_bps` must be 1-10000 (InvalidIndexAtCreation error if 0 or >10000)
- A lower entry index means cheaper entry but higher risk
- A higher entry index means more expensive entry but lower risk
- Maximum payout ratio = 10000 / index_at_creation_bps
