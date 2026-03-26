# Sails Frontend And Gear-JS

This note captures the standard frontend path for Vara Sails applications and the justified fallback path for lower-level Gear-JS work.

## Default Decision

For a standard Vara Sails frontend, use this order:

1. The Sails `.idl` is the interface source of truth.
2. Prefer `sails-js-cli` generated client code for typed access.
3. Prefer `@gear-js/react-hooks` for React integration, queries, commands, and typed events.
4. Use `useSails` only when you intentionally choose runtime IDL parsing instead of generated client code.
5. Use `@gear-js/api` only as an explicit escape hatch for cases the typed Sails path does not cover.

Do not start with manual SCALE payload assembly when an IDL and generated client are available.
Do not switch to low-level Gear-JS just because a UI flow is custom.

## Typical Package Surface

A typical Vara frontend built around Sails usually has three layers.

### Core Sails layer
- `sails-js`
- `@gear-js/react-hooks`
- `@gear-js/api`
- `@polkadot/api`
- `@tanstack/react-query`
- React

### Wallet and UI layer
Add these only if the app uses packaged wallet/UI components:
- `@gear-js/ui`
- `@gear-js/vara-ui`
- `@gear-js/wallet-connect`

### Optional low-level layer
Add low-level metadata, mailbox, voucher, or raw API helpers only when the app genuinely needs escape-hatch behavior.

Version resolution order:
1. Follow the target repository lockfile first.
2. Then check current `peerDependencies`, especially for `@gear-js/react-hooks`.
3. If bootstrapping a new app, resolve a compatible package set from current package metadata before writing `package.json`.

Do not pin Gear/Vara frontend package versions from memory.

## Root Provider Composition

The normal React root is:

- TanStack Query provider
- Gear API provider
- account provider
- alert provider
- router and app-specific providers

The official hooks documentation requires a TanStack `QueryClientProvider` together with `ApiProvider`, `AccountProvider`, and `AlertProvider`.

A practical app wrapper looks like this:

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import {
  ApiProvider,
  AccountProvider,
  AlertProvider,
} from '@gear-js/react-hooks';
import { Alert, alertStyles } from '@gear-js/ui';

const queryClient = new QueryClient();

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <ApiProvider initialArgs={{ endpoint: import.meta.env.VITE_NODE_ADDRESS }}>
        <AccountProvider appName="My Vara App">
          <AlertProvider template={Alert} containerClassName={alertStyles.root}>
            {children}
          </AlertProvider>
        </AccountProvider>
      </ApiProvider>
    </QueryClientProvider>
  );
}
```
If the app uses packaged Gear wallet/UI components, import their required styles at the app entrypoint before validating wallet UX.

Also validate required env values, such as node endpoint and program IDs, before rendering the provider tree. Missing env configuration must fail visibly, not silently.

Project-specific providers such as auth, routing, balances, feature flags, or domain contexts should sit around or under this base tree.

## Wallet And Account Flow

For a standard dApp, prefer browser wallet flows rather than local keyrings:

- `useAccount` for detected wallets, selected account, login, and logout
- `@gear-js/wallet-connect` `Wallet` component for a ready-made wallet button and modal

If you need a custom signer path, the generated Sails transaction builder also supports browser wallet injection:

```ts
import { web3Accounts, web3FromSource } from '@polkadot/extension-dapp';

const [account] = await web3Accounts();
const injector = await web3FromSource(account.meta.source);

transaction.withAccount(account.address, { signer: injector.signer });
```

Do not place `GearKeyring.fromMnemonic`, seeds, or test mnemonics in a shipped browser frontend.

### Required wallet readiness states

At minimum, the UI should distinguish these states:

- `!isAccountReady`: wallet discovery is still loading
- `isAccountReady && !isAnyWallet`: no Vara-compatible wallet extension found
- `isAnyWallet && !account`: wallet exists but no account is connected
- `account`: wallet connected and account ready for signing

Do not render write actions as active until the account path is ready.
Disabled actions should explain why they are disabled.

## Typed Sails Client Path

Generate the client from the program IDL:

```bash
npx sails-js-cli generate path/to/program.idl -o src/lib --no-project
```

Then wire the generated `Program` class:

```ts
import { useProgram } from '@gear-js/react-hooks';
import { Program } from '@/lib';

const { data: program } = useProgram({
  library: Program,
  id: programId,
});
```

Use `useSails` only when you intentionally want runtime IDL parsing instead of a generated library.

Use generated client code as the default for product code.
Reserve runtime IDL parsing for dynamic integrations, tooling, playgrounds, or cases where the IDL is not known at build time.

If the program `.idl` changes, regenerate the client before treating the frontend as up to date.

## Queries

For Sails queries, prefer `useProgramQuery`:

```ts
const { data, isLoading, error } = useProgramQuery({
  program,
  serviceName: 'counter',
  functionName: 'value',
  args: [],
  watch: false,
});
```

Guidance:

- Use `watch: false` by default.
- Turn `watch: true` on only for screens that truly need live updates.
- Use `watch: true` only for narrow screens that genuinely benefit from live updates.
- Document the extra network traffic when enabling subscriptions.
- Prefer query + explicit refetch after successful mutations as the default data freshness model.
- Do not depend on broad live subscriptions for ordinary CRUD freshness.

For low-level reads, use:

- `api.programState.read` with `ProgramMetadata` for the full state
- `api.programState.readUsingWasm` for state functions backed by `state.meta.wasm`

## SCALE Decode Decision

When the frontend drops below the generated Sails path, classify the bytes before decoding:

- standard Sails constructors, service calls, replies, and events:
  - prefer the generated client
  - use runtime `parseIdl` only when dynamic control is explicitly required

- full state reads:
  - use `api.programState.read` with `ProgramMetadata`

- state-function outputs:
  - use `api.programState.readUsingWasm` with `state.meta.wasm`

Do not decode arbitrary Sails-facing bytes as a bare DTO until you have ruled out routing framing.
Do not use `.idl` and `ProgramMetadata` interchangeably.
Do not use full-state metadata where `state.meta.wasm` is the correct artifact.

## Commands And Transactions

For standard Sails writes, prefer hooks over manual extrinsic assembly.

### Send directly with hooks

```ts
const { sendTransactionAsync } = useSendProgramTransaction({
  program,
  serviceName: 'counter',
  functionName: 'increment',
});

const result = await sendTransactionAsync({
  args: [1],
  value: 0n,
});

const reply = await result.response;
```

Key points:

- `args` maps to the Sails function arguments.
- `account` is optional when the connected wallet account should sign.
- `value` defaults to `0`.
- `gasLimit` is auto-calculated if omitted.
- `voucherId` can be provided for voucher-backed sends.
- The frontend should usually await the decoded `response`, not just the extrinsic submission.

### Minimal UI mutation pattern with alerts

```ts
import { useState } from 'react';
import {
  useAccount,
  useAlert,
  useSendProgramTransaction,
} from '@gear-js/react-hooks';

type Props = {
  program: any;
  onSuccess: () => Promise<void> | void;
};

export function CreateCampaignButton({ program, onSuccess }: Props) {
  const alert = useAlert();
  const { account, isAnyWallet, isAccountReady } = useAccount();
  const [inlineError, setInlineError] = useState<string | null>(null);

  const { sendTransactionAsync, isPending } = useSendProgramTransaction({
    program,
    serviceName: 'crowdfunding',
    functionName: 'createCampaign',
  });

  const handleClick = async () => {
    setInlineError(null);

    if (!isAccountReady) {
      setInlineError('Wallets are still loading');
      return;
    }

    if (!isAnyWallet) {
      setInlineError('No Vara wallet extension found');
      return;
    }

    if (!account) {
      setInlineError('Connect a wallet first');
      return;
    }

    if (!program) {
      setInlineError('Program is not ready yet');
      return;
    }

    const alertId = alert.loading('Awaiting wallet confirmation...');

    try {
      const result = await sendTransactionAsync({
        args: [
          'My campaign',
          'Short description',
          1_000_000_000_000n,
          1000,
          [{ title: 'Prototype', amount: 1_000_000_000_000n }],
        ],
        value: 0n,
        awaitFinalization: true,
      });

      await result.response;

      alert.update(alertId, 'Campaign created successfully');
      await onSuccess();
    } catch (error) {
      const message =
        error instanceof Error ? error.message : 'Transaction failed';

      alert.update(alertId, message);
      setInlineError(message);
    }
  };

  return (
    <div>
      {inlineError && <p>{inlineError}</p>}

      <button onClick={handleClick} disabled={isPending || !account}>
        {isPending ? 'Submitting...' : 'Create campaign'}
      </button>
    </div>
  );
}
```

### Prepare before send

Use `usePrepareProgramTransaction` when you need the transaction fee, gas limit, or extrinsic before the user confirms:

```ts
const { prepareTransactionAsync } = usePrepareProgramTransaction({
  program,
  serviceName: 'counter',
  functionName: 'increment',
});

const transaction = await prepareTransactionAsync({
  args: [1],
});

const fee = await transaction.transactionFee();
```

This is the right place for:

- balance validation
- fee previews
- custom confirmation modals
- voucher checks

A common wrapper pattern is to run a balance check before calling `transaction.signAndSend()`, then await `response()` and raise a UI alert on failure.

### Transaction builder without hooks

Outside React hooks, the generated client returns a Sails transaction builder:

```ts
const tx = program.counter.increment(1);

tx.withAccount(account.address, { signer: injector.signer });
await tx.calculateGas();

const { response } = await tx.signAndSend();
const reply = await response();
```

Use this path for custom orchestration, batch flows, or non-React helpers.

### Canonical mutation pattern

Every write action should follow this sequence:

1. Check runtime prerequisites:
   - program instance is ready
   - wallet discovery is ready
   - wallet exists
   - account is connected
2. Validate form and domain constraints before sending.
3. Show a visible pending state.
4. Send the transaction.
5. Await the decoded `response`, not only extrinsic submission.
6. Surface success or failure visibly.
7. Refetch the affected queries after success.

Do not rely only on console logs or implicit alerts.

## Events

Use `useProgramEvent` for typed event subscriptions:

```ts
useProgramEvent({
  program,
  serviceName: 'counter',
  functionName: 'Incremented',
  onData: (event) => console.log(event),
});
```

Do not subscribe globally to every event. Scope subscriptions to the screen or feature that actually needs them.

## Low-Level Gear-JS Fallback

Use low-level `@gear-js/api` only when there is a concrete reason the typed Sails path does not cover.

Low-level Gear-JS is an escape hatch, not a parallel default architecture.
Do not replace ordinary Sails command flows with raw message sends just because the UI is custom.

Use low-level `@gear-js/api` when you need one of these cases:

- direct `api.message.send` or `api.message.sendReply`
- mailbox flows
- voucher issue, revoke, or update flows
- metadata parsing with `ProgramMetadata` or `getProgramMetadata`
- full-state reads without a generated Sails client
- dynamic multi-program or multi-IDL integrations

### Connection

For direct API work, the docs note that `VaraApi` and `VaraTestnetApi` are preferable to the generic `GearApi` on Vara networks because runtime versions and signatures may differ. Keep that recommendation in mind when you are building non-hook or non-provider utilities.

### Metadata

Use `getProgramMetadata` with metadata hex when you need `ProgramMetadata`. The old `gear-meta` CLI is deprecated in the official docs.

### Raw send

```ts
const gas = await api.program.calculateGas.handle(
  account.address,
  programId,
  payload,
  0,
  false,
  metadata,
);

const extrinsic = api.message.send(
  {
    destination: programId,
    payload,
    gasLimit: gas.min_limit,
    value: 0,
  },
  metadata,
);

await extrinsic.signAndSend(account, ({ events }) => {
  console.log(events);
});
```

Rules:

- calculate gas before sending in production-like flows
- prefer Sails command builders when the program is a Sails app
- use low-level message send only when you need a true escape hatch

### Gas Calculation Methods

| Method | Use When |
|--------|----------|
| `api.program.calculateGas.handle(source, destination, payload, value, allowOtherPanics, metadata)` | Sending a message to an existing program |
| `api.program.calculateGas.reply(source, messageId, payload, value, allowOtherPanics, metadata)` | Replying to a message in the user's mailbox |
| `api.program.calculateGas.initUpload(source, code, payload, value, allowOtherPanics, metadata)` | Uploading code and initializing in one step |
| `api.program.calculateGas.initCreate(source, codeId, payload, value, allowOtherPanics, metadata)` | Creating a program from already-uploaded code |

All methods return `{ min_limit, reserved, burned }`. Use `min_limit` as the gas limit for the extrinsic. Set `allowOtherPanics` to `false` for strict error checking or `true` to tolerate panics in downstream programs.

### Raw state reads

```ts
const state = await api.programState.read({ programId }, metadata);
```

Or:

```ts
const state = await api.programState.readUsingWasm(
  {
    programId,
    fn_name: 'state_function',
    stateWasm,
    argument: { input: 'payload' },
  },
  stateMetadata,
);
```

## Vouchers, Gasless, And Signless

Voucher-aware flows exist at both levels:

- hooks and Sails transaction builders accept `voucherId`
- low-level Gear-JS exposes `api.voucher.issue`, `api.voucher.call`, `api.voucher.revoke`, and `api.voucher.update`

For product-level gasless and signless UX, the current docs point to the EZ-transactions package and its providers and hooks. Treat this as an explicit product decision rather than a hidden default.

For the canonical voucher lifecycle, builder recipes, signless sessions, and failure modes, see `references/voucher-and-signless-flows.md`.

## Mailbox And Replies

If the frontend needs user mailbox handling rather than direct Sails commands:

- use low-level mailbox APIs and extrinsics
- remember that user-facing messages can land in the mailbox
- `sendReply` and `claimValue` are separate flows from a normal command send

This is an advanced path. Name it explicitly in the plan instead of blending it into ordinary Sails UI work.

## Environment Contract

Keep the environment contract explicit and validated at startup.

Typical frontend env keys include:
- node endpoint, for example `VITE_NODE_ADDRESS`
- one or more deployed program IDs
- optional auxiliary contract IDs such as VFT program IDs

Rules:
- validate required env values before rendering feature screens
- fail visibly when endpoint or required program IDs are missing
- document the intended network and deployment assumptions explicitly

## Default Review Checklist

Before closing frontend work, verify:

- every UI action is mapped to a Sails command, query, or event
- the provider tree is present once at app root
- the generated client matches the latest `.idl`
- package versions were resolved from the target repo and current peer dependency expectations, not memory
- wallet connect UI is visible, usable, and styled correctly
- missing wallet/account states are rendered explicitly
- one read path works in the UI
- one write path shows disabled, pending, and success or error states
- transaction flows await decoded replies where applicable
- affected queries refetch after successful mutations
- `watch` subscriptions are intentional
- gas and fee assumptions are explicit
- voucher or gasless usage is explicit
- required env vars are validated
- no secrets are embedded in the frontend
