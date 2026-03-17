# Token Crate Chooser

Choose the smallest `awesome-sails` surface that satisfies the feature.

## Base Cases

### Use base VFT when the app only needs:
- `transfer`
- `approve`
- `transfer_from`
- `allowance`
- `balance_of`
- `total_supply`

This is the standard fungible-token baseline.

### Add metadata when the token must expose:
- `name`
- `symbol`
- `decimals`

Use this for user-facing tokens that should look complete to frontend consumers.

### Add admin when the token needs:
- mint
- burn
- pause
- privileged maintenance operations
- role-based protected operations

Use this when issuance and sensitive maintenance are not fully fixed at initialization.

## Extended Cases

### Add extension when the token needs:
- `transfer_all`
- expired allowance cleanup
- balance or allowance enumeration
- explicit shard-management helpers

Do not add it by default. Add it only when the feature or operational model needs those capabilities.

### Add native exchange when the design requires:
- native value sent in -> token minted
- token burned -> native value returned

This is an exchange-backed token flow, not a standard token default.

### Add msg-tracker when the design requires:
- async message orchestration
- status tracking by `MessageId`
- saga-like token-related flows
- explicit user-visible tracking for delayed or reply-driven steps

## Infrastructure Helpers

### Add access-control when:
- the project outgrows a single hard-coded admin
- the role model is explicit and multi-role
- role enumeration or batch grant/revoke is needed

### Add storage abstractions when:
- services should be portable across storage backends
- the app uses reusable service composition
- wrapper-based storage access is part of the architecture

## Selection Notes

- Start from the minimum needed token surface.
- Add metadata for user-facing tokens almost by default.
- Add admin only when supply or maintenance operations are privileged.
- Add extension only when the feature set requires it.
- Add native exchange only when value conversion is part of the product.
- Add msg-tracker only when token flows have async lifecycle or status visibility requirements.

## Output

Write the chosen stack in this format:

- token shape:
- crate or feature set:
- dedicated token program or embedded service:
- role model:
- event model:
- required gtests:
