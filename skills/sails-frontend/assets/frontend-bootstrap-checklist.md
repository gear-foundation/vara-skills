# Frontend Bootstrap Checklist

Use this before writing UI code for a Vara Sails application.

## Before Writing UI Code

- Confirm the deployed `programId` for each environment.
- Confirm the node endpoint for local, testnet, or other target networks.
- Confirm the intended network and API assumptions for the target node.
- If using Next.js App Router: confirm `transpilePackages` includes Gear/Sails packages in `next.config.js`.
- If using Next.js App Router: confirm all Gear provider and hook code is in `'use client'` files.
- If using Next.js App Router: confirm heavy Gear imports use `dynamic(() => import(...), { ssr: false })` or runtime `await import(...)`.
- If the repo has a Rust `app/` crate and the frontend framework expects `app/`: confirm one has been renamed (e.g. frontend in `frontend/`).
- Confirm the current `.idl` and whether the frontend should generate `lib.ts` or parse IDL dynamically.
- Confirm the `.idl` file is checked into the frontend project or the copy/generation command is documented.
- If the IDL is generated in the Rust workspace `OUT_DIR`, confirm the handoff path to the frontend is explicit. See `sails-idl-client-pipeline.md`.
- Confirm whether the app stays fully on the provider-and-hooks path or needs a justified low-level `@gear-js/api` escape hatch.
- List each Sails service function as one of: command, query, or event subscription.
- Mark each write action as wallet-bound or not wallet-bound.
- Decide which screens need `useProgramQuery`, which need `useSendProgramTransaction`, and which need `useProgramEvent`.
- Decide which queries must refetch after successful mutations.
- Decide which screens truly need `watch: true`; keep the default path as query + mutation + explicit refetch.
- Decide whether the UX needs preflight transaction preparation with `usePrepareProgramTransaction`.
- Decide whether vouchers, gasless, or signless flows are part of scope.
- Define loading, empty, success, and error states for each async path.
- Define wallet readiness states separately:
  - wallets are still loading
  - no wallet extension found
  - wallet available but no account connected
  - account connected and ready for signing
- Define API readiness states separately:
  - endpoint is connecting
  - API is ready
- Define at least one invalid form path that must fail before sending a transaction.
- Confirm how user-facing token values are converted to raw on-chain amounts.
- Avoid plain JavaScript `Number` for balance-sensitive flows.
- Confirm that no private keys or seed phrases are embedded in the frontend.
- Confirm the runtime and API compatibility assumptions for the chosen node.

## Mandatory Smoke Checks Before Handoff

- Confirm packaged wallet/UI components are styled correctly if they are used; otherwise confirm the custom wallet flow is visible and usable.
- Confirm wallet loading, no-wallet, disconnected, and connected states are visible in the UI.
- Confirm wallet modal opens if a packaged wallet modal is used.
- Confirm selected account is shown in the UI.
- Confirm API-not-ready state is visible before feature screens try to use the program.
- Confirm signed submit actions are blocked when no wallet is connected.
- Confirm at least one invalid form submission is handled without opening a wallet prompt or sending a transaction.
- Confirm at least one transaction path shows pending, success, and error states visibly.
- Confirm alerts are visible on screen if alerts are part of the UX.
- Confirm at least one write action awaits the decoded program response, not only extrinsic submission.
- Confirm at least one successful mutation refetches the affected query data.
- Confirm env vars are documented and actually used.
- Confirm the app fails visibly when required env vars are missing.
- Confirm one full happy-path action can be performed from the UI.
- Confirm the installed `sails-js` API surface matches the code: `signAndSend` (not `sendAndWait`), positional args, query builder with `.call()`.
- If runtime IDL parsing is used, confirm `sails-js-parser` is installed and `new Sails(parser)` initialization is present.

## Verification Order (Next.js App Router)

When the frontend is a Next.js App Router project:

1. `next build` first (generates route types under `.next/types`)
2. `tsc --noEmit` second (type-check against generated types)
3. Manual or automated smoke of the running app

Do not run `tsc --noEmit` before `next build`; route parameter types will be missing.

## Dependency Resolution Checks

- Read `package.json` and lockfile first if they exist.
- Check current peer dependency expectations for `@gear-js/react-hooks`.
- Confirm `@polkadot/api` expectations are satisfied when using `@gear-js/react-hooks`.
- If packaged wallet/UI components are used, confirm the required style imports are present at the app entrypoint.
- Do not downgrade package versions unless there is a documented compatibility reason.
- Record the final chosen package set explicitly.
- Mark which dependencies are:
  - core Sails frontend dependencies
  - wallet/UI-only dependencies
  - low-level escape-hatch-only dependencies
