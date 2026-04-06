# PolyBaskets Error Codes

## BasketMarketError

| Error | Trigger | Recovery |
|-------|---------|----------|
| `Unauthorized` | Caller lacks required role (admin/settler) | Use the correct account with the assigned role |
| `BasketNotFound` | Invalid basket_id | Query `GetBasketCount` to check valid range |
| `BasketNotActive` | Basket is in SettlementPending or Settled status | Cannot bet on non-active baskets |
| `BasketAssetMismatch` | Betting with wrong asset kind (e.g., VARA bet on a Bet basket) | Check basket's `asset_kind` field |
| `NoItems` | Creating basket with empty items array | Add at least 1 item |
| `InvalidWeights` | Item weights don't sum to exactly 10000 | Ensure `sum(weight_bps) == 10000` |
| `DuplicateBasketItem` | Same poly_market_id + selected_outcome appears twice | Remove duplicate items |
| `TooManyItems` | More than 10 items in basket | Reduce to 10 or fewer items |
| `NameTooLong` | Basket name exceeds 48 characters | Shorten the name |
| `DescriptionTooLong` | Description exceeds 256 characters | Shorten the description |
| `MarketIdTooLong` | poly_market_id exceeds 128 characters | Use valid Polymarket condition ID |
| `SlugTooLong` | poly_slug exceeds 128 characters | Use valid Polymarket slug |
| `PayloadTooLong` | Settlement payload string too long | Trim payload data |
| `VaraDisabled` | VARA betting is disabled in config | Use BetToken lane, or admin enables VARA |
| `SettlementAlreadyExists` | Settlement already proposed for this basket | Wait for existing settlement to finalize |
| `SettlementNotFound` | No settlement proposed for this basket | Propose settlement first |
| `SettlementNotProposed` | Settlement status is not Proposed | Check settlement status |
| `SettlementNotFinalized` | Trying to claim before settlement is finalized | Wait for finalization |
| `ChallengeDeadlineNotPassed` | Finalizing before 12-minute challenge window | Wait until `challenge_deadline` timestamp passes |
| `InvalidIndexAtCreation` | index_at_creation_bps is 0 or > 10000 | Use value between 1 and 10000 |
| `InvalidBetAmount` | No VARA value attached to bet transaction | Add `--value <amount>` to vara-wallet call |
| `InvalidResolutionCount` | Resolution count doesn't match basket items count | Provide exactly one resolution per item |
| `DuplicateResolutionIndex` | Same item_index appears twice in resolutions | Each item_index must be unique |
| `ResolutionIndexOutOfBounds` | item_index >= basket items count | Use indices 0 to items.length-1 |
| `ResolutionSlugMismatch` | poly_slug in resolution doesn't match basket item | Use exact slug from basket's items |
| `InvalidResolution` | Malformed resolution data | Check ItemResolution struct format |
| `AlreadyClaimed` | User already claimed payout for this basket | No action needed — already claimed |
| `NothingToClaim` | User has no position in this basket | Verify position exists with GetPositions |
| `TransferFailed` | On-chain VARA transfer failed | Check account balance, retry |
| `MathOverflow` | Arithmetic overflow in payout calculation | Bug — report to maintainers |
| `EventEmitFailed` | Failed to emit on-chain event | Retry transaction |
| `InvalidConfig` | Invalid configuration parameters | Check BasketMarketConfig values |

## BetLaneError

| Error | Trigger | Recovery |
|-------|---------|----------|
| `AccessDenied` | Caller lacks admin role | Use admin account |
| `Paused` | BetLane contract is paused | Wait for admin to resume |
| `InvalidConfig` | Invalid BetLaneConfig values | Check min_bet, max_bet |
| `InvalidAmount` | Bet amount is zero | Provide non-zero amount |
| `AmountBelowMinBet` | Amount < min_bet from config | Increase bet amount |
| `AmountAboveMaxBet` | Amount > max_bet from config | Decrease bet amount |
| `InvalidIndexAtCreation` | index_at_creation_bps is 0 or > 10000 | Use value between 1 and 10000 |
| `BasketQueryFailed` | Failed to query BasketMarket contract | Check BasketMarket program is active |
| `BasketNotFound` | Invalid basket_id | Verify basket exists |
| `BasketNotActive` | Basket not in Active status | Cannot bet on settled baskets |
| `BasketAssetMismatch` | Basket's asset_kind is not Bet | Use VARA lane for Vara baskets |
| `SettlementQueryFailed` | Failed to query settlement | Check BasketMarket program |
| `SettlementNotFound` | No settlement for this basket | Wait for settlement |
| `SettlementNotFinalized` | Settlement not yet finalized | Wait for finalization |
| `NothingToClaim` | No position in this basket | Verify position exists |
| `AlreadyClaimed` | Already claimed | No action needed |
| `OperationInProgress` | Concurrent operation on same position | Wait and retry |
| `BetTokenTransferFromFailed` | BET token transfer failed | Check BET balance and approval |
| `BetTokenPayoutFailed` | Payout transfer failed | Retry or contact admin |
| `BetTokenRefundFailed` | Refund transfer failed | Retry or contact admin |
| `MathOverflow` | Arithmetic overflow | Bug — report |
| `InvalidPageSize` | Invalid pagination params | Use reasonable offset/limit values |
| `EventEmitFailed` | Event emission failed | Retry |
| `RoleManagementFailed` | Role grant/revoke failed | Check admin permissions |
