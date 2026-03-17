# Token GTest Matrix

Use this as the minimum verification matrix for token-related work.

## Base VFT Tests

### Transfer
- transfer succeeds with sufficient balance
- transfer fails with insufficient balance
- transfer updates sender and receiver balances correctly
- transfer emits the expected event

### Approval / Allowance
- approve sets allowance
- approve overwrites or updates allowance as intended by the chosen implementation
- transfer_from succeeds within allowance
- transfer_from fails above allowance
- allowance decreases correctly after transfer_from when applicable
- approval emits the expected event

### Supply / Queries
- initial total supply is correct
- balance queries return expected values
- metadata queries return expected values when metadata is enabled

## Admin / Extended Token Tests

### Mint
- authorized minter can mint
- unauthorized actor cannot mint
- mint updates total supply
- mint updates recipient balance
- mint emits `Minted`

### Burn
- authorized burner can burn
- unauthorized actor cannot burn
- burn updates total supply
- burn updates target balance correctly
- burn emits `Burned`

### Role Management
- bootstrap admin is configured correctly
- admin can grant roles
- non-admin cannot grant roles
- admin can revoke roles
- role queries reflect current assignments

### Pause
- paused token blocks protected mutation paths
- unpaused token restores expected behavior

## Optional Extension Tests

### Enumeration / Cleanup
- allowance enumeration returns expected entries
- balance enumeration returns expected entries
- expired allowance cleanup removes only intended records

### Transfer All
- `transfer_all` moves the full balance
- sender balance becomes zero
- receiver balance increases by the full transferred amount

### Native Exchange
- native value sent in mints the expected token amount
- burn returns the expected native value
- admin recovery or reply path behaves as designed

## Events

For every enabled mutation path, assert:
- the correct event type
- the correct actor fields
- the correct value fields
- the correct entity identifiers

## Fatal Paths

Where exported commands use fail-fast semantics, assert the expected fatal behavior:
- unauthorized privileged action fails
- malformed state transition fails
- tests expect the corresponding fatal exported-path behavior instead of silent partial success

## Completion Rule

Do not call token integration complete until:
- the selected crate surface is covered
- all privileged flows are tested
- event emission is asserted
- the gtest report is written
