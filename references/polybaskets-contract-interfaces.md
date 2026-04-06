# PolyBaskets Contract Interfaces

Complete annotated interface for all three programs. IDL files bundled in `idl/polybaskets/`.

## BasketMarket (`polymarket-mirror.idl`)

### Types

```
BasketItem {
  poly_market_id: str      # Polymarket condition ID
  poly_slug: str           # Polymarket market slug
  weight_bps: u16          # Weight in basis points (0-10000)
  selected_outcome: Outcome # YES or NO
}

Outcome = YES | NO

BasketAssetKind = Vara | Bet

Basket {
  id: u64                  # Unique basket ID
  creator: actor_id        # Creator's address
  name: str                # Max 48 chars
  description: str         # Max 256 chars
  items: vec BasketItem    # 1-10 items, weights must sum to 10000
  created_at: u64          # Block timestamp
  status: BasketStatus     # Active | SettlementPending | Settled
  asset_kind: BasketAssetKind
}

Position {
  basket_id: u64
  user: actor_id
  shares: u128             # VARA amount bet (in minimal units)
  claimed: bool
  index_at_creation_bps: u16  # Entry index (1-10000)
}

Settlement {
  basket_id: u64
  proposer: actor_id
  item_resolutions: vec ItemResolution
  payout_per_share: u128   # Pre-computed payout ratio
  payload: str             # Settlement metadata/proof
  proposed_at: u64
  challenge_deadline: u64  # Must pass before finalization
  finalized_at: opt u64
  status: SettlementStatus # Proposed | Finalized
}

ItemResolution {
  item_index: u8           # Index into basket.items (0-based)
  resolved: Outcome        # Final outcome
  poly_slug: str           # Must match basket item's slug
  poly_condition_id: opt str
  poly_price_yes: u16      # Final YES price in bps
  poly_price_no: u16       # Final NO price in bps
}
```

### State-Changing Methods (require `--account`)

| Method | Args | Returns | Notes |
|--------|------|---------|-------|
| `CreateBasket` | `name, description, items, asset_kind` | `u64` (basket_id) | Weights must sum to 10000 |
| `BetOnBasket` | `basket_id, index_at_creation_bps` | `u128` (shares) | Requires `--value` in VARA |
| `Claim` | `basket_id` | `u128` (payout) | Only after settlement finalized |
| `ProposeSettlement` | `basket_id, item_resolutions, payload` | `null` | Settler role only |
| `FinalizeSettlement` | `basket_id` | `null` | Settler role, after challenge window |
| `SetConfig` | `config` | `null` | Admin role only |
| `SetVaraEnabled` | `enabled` | `null` | Admin role only |

### Query Methods (free, no `--account`)

| Method | Args | Returns |
|--------|------|---------|
| `GetBasket` | `basket_id` | `Result<Basket, Error>` |
| `GetBasketCount` | none | `u64` |
| `GetConfig` | none | `BasketMarketConfig` |
| `GetPositions` | `user` (actor_id) | `vec Position` |
| `GetSettlement` | `basket_id` | `Result<Settlement, Error>` |
| `IsVaraEnabled` | none | `bool` |

### Events

- `BasketCreated { basket_id, creator, asset_kind }`
- `VaraBetPlaced { basket_id, user, amount, user_total, index_at_creation_bps }`
- `SettlementProposed { basket_id, proposer, payout_per_share, challenge_deadline }`
- `SettlementFinalized { basket_id, finalized_at, payout_per_share }`
- `Claimed { basket_id, user, amount }`
- `VaraSupportUpdated { enabled }`
- `ConfigUpdated { config }`

---

## BetToken (`bet_token_client.idl`)

Fungible token (VFT) with daily claim system and streak bonuses.

### Key Methods

| Method | Args | Returns | Notes |
|--------|------|---------|-------|
| `Claim` | none | `ClaimState` | Daily token claim with streak bonus |
| `Transfer` | `to, value` | `bool` | Standard VFT transfer |
| `Approve` | `spender, value` | `bool` | Approve spending allowance |
| `TransferFrom` | `from, to, value` | `bool` | Transfer from approved allowance |
| `AdminMint` | `to, value` | `null` | Admin only |

### Key Queries (BetToken service)

| Method | Args | Returns |
|--------|------|---------|
| `BalanceOf` | `account` | `u256` |
| `GetClaimPreview` | `user` | `ClaimPreview { amount, streak_days, next_claim_at, can_claim_now }` |
| `GetClaimState` | `user` | `ClaimState { last_claim_at, streak_days, total_claimed, claim_count }` |
| `GetClaimConfig` | none | `ClaimConfig { base_claim_amount, max_claim_amount, streak_step, streak_cap_days, claim_period, claim_paused }` |
| `IsClaimPaused` | none | `bool` |
| `IsSpenderAllowed` | `spender` | `bool` |
| `Allowance` | `owner, spender` | `u256` |
| `TotalSupply` | none | `u256` |

### Metadata Service Queries

`Name`, `Symbol`, and `Decimals` are on the **Metadata** service, not BetToken:

| Method | Args | Returns | vara-wallet service prefix |
|--------|------|---------|---------------------------|
| `Name` | none | `str` | `Metadata/Name` |
| `Symbol` | none | `str` | `Metadata/Symbol` |
| `Decimals` | none | `u8` | `Metadata/Decimals` |

---

## BetLane (`bet_lane_client.idl`)

Alternative betting lane using BET tokens instead of VARA.

### Key Methods

| Method | Args | Returns | Notes |
|--------|------|---------|-------|
| `PlaceBet` | `basket_id, amount, index_at_creation_bps` | `u256` (shares) | Requires BET token approval first |
| `Claim` | `basket_id` | `u256` (payout) | After settlement finalized |

### Key Queries

| Method | Args | Returns |
|--------|------|---------|
| `GetPosition` | `user, basket_id` | `Position { shares: u256, claimed, index_at_creation_bps }` |
| `GetPositions` | `user, offset, limit` | `Result<vec UserPositionView, Error>` |
| `GetConfig` | none | `BetLaneConfig { min_bet, max_bet, payouts_allowed_while_paused }` |
| `IsPaused` | none | `bool` |
| `BasketProgramId` | none | `actor_id` |
| `BetTokenId` | none | `actor_id` |
| `GetDependencies` | none | `BetLaneDependencies { basket_program_id, bet_token_id }` |

Note: BetLane `Position.shares` is `u256` (BET token units), unlike BasketMarket `Position.shares` which is `u128` (VARA minimal units).
