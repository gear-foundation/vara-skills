# Voucher And Signless Flows

## When To Use Vouchers

- Does the dApp need users to interact without holding VARA? Use vouchers — a sponsor pays gas on behalf of users.
- Need seamless UX without per-action signing? Add signless sessions on top of vouchers.
- Need both gasless and signless? Use the EZ-Transactions package.
- A voucher is a bounded gas budget tied to a spender, duration, and optional program whitelist. It is not free chain access.
- Choosing vouchers, signless, or both is an explicit product decision. Name it in the spec and architecture, not as a hidden implementation detail.
- For general message sending patterns, see `references/gear-messaging-and-replies.md`. This doc covers only the voucher-specific wrapping and sponsored UX flows.

## Builder Recipe: Voucher-Only Flow

1. Sponsor issues a voucher for the user: `api.voucher.issue(spender, balance, duration, programs, codeUploading)`. The returned `VoucherId` is the handle for all subsequent operations.
2. Frontend checks the voucher exists before sending: `api.voucher.exists(accountId, voucherId)`.
3. Frontend wraps the transaction with the voucher: `api.voucher.call(voucherId, { SendMessage: tx })`.
4. User sends the wrapped transaction. Gas is paid from the voucher balance, not the user wallet.
5. Monitor voucher health: check remaining balance via `api.voucher.details()`, extend duration or top up balance via `api.voucher.update()` if needed.
6. Cleanup: after the voucher expires, sponsor revokes it via `api.voucher.revoke()` to reclaim unspent funds.

## Builder Recipe: Signless Session Flow

1. User creates a temporary session keypair (sub-account) in the frontend.
2. User signs a one-time transaction to register the session in the program: session key, expiry block, and allowed actions.
3. Sponsor issues a voucher to the temporary session account (not the user's main account).
4. App signs all subsequent transactions with the session key — no user signature prompts per action.
5. Session expires by block number or user explicitly revokes it. The temporary key becomes inert.

Guardrails:
- Sessions are bounded by duration, program scope, and allowed actions. The program must enforce these constraints.
- Session creation itself requires a real user signature. Only subsequent actions use the session key.
- One active session per user per program. Multi-session collision must be handled in program logic.
- Session expiry, revocation, and replay protection are program-level responsibilities. Design them explicitly.

## Builder Recipe: EZ-Transactions (Full Gasless + Signless)

- Wrap the app root with `GaslessTransactionsProvider` and `SignlessTransactionsProvider`.
- Use `useGaslessTransaction` and `useSignlessTransaction` hooks in components.
- The EZ-transactions package handles voucher issuance, session management, and transaction wrapping internally.
- This is a product-level integration. Document it in the feature spec, not as an afterthought.

## Voucher Lifecycle

- **Issue**: sponsor creates a voucher for a spender with a gas budget, duration, optional program whitelist, and code-uploading flag.
- **Use**: spender wraps a `SendMessage`, `SendReply`, or `UploadCode` call via `api.voucher.call()`. Gas is deducted from the voucher.
- **Update**: sponsor can top up balance, extend duration, add programs to whitelist, or transfer ownership via `api.voucher.update()`.
- **Decline**: spender voluntarily returns a voucher before expiry, marking it as expired so the sponsor can revoke.
- **Expire**: voucher reaches its block-number deadline and becomes unusable.
- **Revoke**: sponsor reclaims unused funds from an expired or declined voucher.

Duration is block-based and bounded by on-chain constants (`minDuration`, `maxDuration`). The program whitelist scopes which programs the voucher can interact with. If the whitelist is `None`, the voucher works with any program. The `code_uploading` flag controls whether `UploadCode` is permitted through this voucher.

## Voucher Parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| spender | AccountId | Who can use the voucher |
| balance | u128 | Gas allocation in smallest unit (use `BigInt` or string in JS to avoid precision loss above 2^53) |
| duration | BlockNumber | How many blocks the voucher is valid |
| programs | Option\<BTreeSet\<ProgramId\>\> | Authorized programs (None = any) |
| code_uploading | bool | Allow UploadCode via voucher |

## JS API Surface

| Intent | Method | Returns |
|--------|--------|---------|
| Issue | `api.voucher.issue(spender, balance, duration, programs?, codeUploading?)` | extrinsic, VoucherId via event |
| Check exists | `api.voucher.exists(accountId, voucherId)` | boolean |
| List all | `api.voucher.getAllForAccount(accountId)` | Record\<VoucherId, ProgramId[]\> |
| Details | `api.voucher.details(spender, voucherId)` | VoucherDetails (owner, programs, expiry, codeUploading) |
| Execute | `api.voucher.call(voucherId, { SendMessage \| SendReply \| UploadCode })` | extrinsic |
| Update | `api.voucher.update(spender, voucherId, opts)` | extrinsic |
| Decline | `api.voucher.decline(voucherId)` | extrinsic |
| Revoke | `api.voucher.revoke(spender, voucherId)` | extrinsic |
| Min duration | `api.voucher.minDuration()` | blocks |
| Max duration | `api.voucher.maxDuration()` | blocks |
| Max programs | `api.voucher.maxProgramsAmount()` | number |

Update options: `moveOwnership`, `balanceTopUp`, `appendPrograms`, `prolongValidity`. At least one is required.

## On-Chain Extrinsics

| Extrinsic | Signer | Purpose |
|-----------|--------|---------|
| `GearVoucher::issue` | Sponsor | Create a voucher for a spender |
| `GearVoucher::call` | Spender | Execute a prepaid action (PrepaidCall: SendMessage, SendReply, or UploadCode) |
| `GearVoucher::update` | Sponsor | Change balance, duration, programs, or code_uploading |
| `GearVoucher::revoke` | Sponsor | Reclaim unspent funds after expiry |
| `GearVoucher::decline` | Spender | Voluntarily return a voucher |

## Hooks And Transaction Builder Integration

- `useSendProgramTransaction` and `usePrepareProgramTransaction` both accept a `voucherId` option for voucher-backed sends.
- Transaction builder: pass `voucherId` in the options object to wrap the call automatically.
- Voucher existence check before sending is the caller's responsibility. The hooks do not auto-check.
- Fee preview via `usePrepareProgramTransaction` works with vouchers — the fee is still calculated but paid from the voucher.

## Testing Guidance

- Do not invent voucher IDs in tests. Issue a real voucher and use the returned ID.
- In `gtest`: voucher issuance is not natively supported. Test the program logic that receives voucher-backed messages, not the voucher issuance itself.
- In local-node smoke tests: issue a voucher via the JS API or CLI, then use it in the typed client flow.
- For signless flows: test session creation, action execution with the session key, and session expiry behavior at the program level.

## Failure Modes

- Voucher expired: duration exceeded, transaction rejected.
- Voucher balance exhausted: insufficient gas, transaction rejected.
- Program not in voucher whitelist: destination program not authorized, transaction rejected.
- `code_uploading` not enabled: `UploadCode` attempted through a voucher that does not permit it.
- Voucher already revoked or declined: voucher no longer usable.
- Spender mismatch: wrong account attempting to use the voucher.
- Duration out of bounds: below `minDuration` or above `maxDuration` at issuance time.
- Session expired (signless): session block deadline passed, session key rejected by program.
- Session action not allowed (signless): action type not in the session's allowed set, rejected by program.

## See Also

- `references/sails-frontend-and-gear-js.md`
- `references/gear-gas-reservations-and-waitlist.md`
- `references/gear-execution-model.md`
