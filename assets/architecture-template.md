# Architecture Note

## Summary

## Program And Service Boundaries

## State Ownership

## Message Flow

## Routing And Public Interface
- Existing public routes that must remain stable
- New routes introduced by this release
- Any intentionally deprecated routes
- Whether any method signature or reply shape changes are proposed

## Event Contract
- Existing events that must remain stable
- Any new event surface introduced by this release
- Whether any existing event payload changes are proposed
- Whether event versioning is required

## Generated Client Or IDL Impact
- Does this release require IDL regeneration
- Which clients, scripts, or tools consume the IDL
- Whether old and new generated clients must coexist during cutover

## Contract Version And Status Surface
- How the contract exposes version information
- Whether the contract has lifecycle status such as `Active` or `ReadOnly`
- Whether old-version writes must be disabled after cutover

## Off-Chain Components
- Frontend program-id and config impact
- Indexer subscription or decoder impact
- Any automation or scripts affected by the new version

## Release And Cutover Plan
- Deploy order
- Frontend switch strategy
- Indexer switch strategy
- Whether the old version remains queryable
- Whether writes to the old version are disabled

## Failure And Recovery Paths
- Rollback target
- How to revert frontend and indexer back to the previous version
- What happens if the new version is deployed but not adopted

## Open Questions
