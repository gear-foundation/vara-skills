# Token Scope Checklist

Use this checklist before choosing crates or writing service code.

## Product Intent

- What is the token for?
  - user-facing transferable value
  - internal accounting unit
  - reward or incentive asset
  - redeemable or exchange-backed token
  - governance or admin-controlled supply
- Should the token be transferable between users?
- Is the token meant to be externally visible to wallets, indexers, or frontend consumers?

## Deployment Shape

- Is this a dedicated token program?
- Is this an app that embeds token-related services inside a larger program?
- Does the app depend on an already deployed external token instead of owning token logic?

## Minimal Surface

Check only the smallest required capability set:

- standard VFT transfers
- approvals and `transfer_from`
- balance and supply queries
- metadata: `name`, `symbol`, `decimals`
- mint
- burn
- pause
- role-based admin control
- allowance or balance enumeration
- expired allowance cleanup
- `transfer_all`
- explicit shard management
- native value <-> token exchange
- async message-status tracking around token workflows

## Supply Policy

- fixed supply at initialization
- mintable supply
- burnable supply
- both mintable and burnable
- who can mint?
- who can burn?
- should end users burn their own balance, or only privileged actors?

## Role Model

- single admin only
- admin + minter
- admin + burner
- admin + pauser
- enumerated multi-role model
- revocable roles
- bootstrap roles assigned in constructor

## Events

List the domain events that matter to off-chain consumers:

- Transfer
- Approval
- Minted
- Burned
- RoleGranted
- RoleRevoked
- Paused
- Unpaused
- ExchangeMinted
- ExchangeBurned

For each custom event, note:
- entity id or token owner involved
- actor who initiated the change
- value affected
- whether frontend or indexers will subscribe to it

## Integration Path

- Should the frontend use generated Sails clients?
- Does the feature require event subscriptions?
- Does the feature require indexer-facing observability?
- Does the token feature change the `.idl` surface?

## Guardrails

- Do not implement a custom fungible token from scratch before checking whether standard VFT behavior is sufficient.
- Do not pull in admin, extension, or exchange layers unless the spec actually needs them.
- Do not treat events as optional for production-facing token state transitions.
