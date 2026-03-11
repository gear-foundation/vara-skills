# Vara.eth Extension Notes

## Scope
This is an extension layer for the first release, not the default execution path.

## Mental Model Differences
- Programs have both a Gear-style actor identity and an Ethereum-facing Mirror address.
- Router validates code, creates programs, and emits lifecycle events.
- Each program Mirror needs executable balance to pay for execution.
- Pre-confirmed state can be newer than the last committed on-chain state.

## Design Warnings
- Do not assume a plain Gear deploy flow maps directly to Vara.eth.
- Message execution depends on executable balance, not only the sender account.
- `callReply` and async reply handling matter for user-visible behavior.
- ABI, IDL, and deployment mode must stay aligned or queries and messages fail at the edge.

## First-Wave Usage
- Mention Vara.eth only when the target project explicitly needs it.
- Use this note to flag Router/Mirror/executable-balance concerns during planning.
- Defer full Vara.eth-specific skills to the next milestone.
