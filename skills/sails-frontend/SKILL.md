---
name: sails-frontend
description: Use when a builder needs to build or extend a React or TypeScript frontend for a standard Gear/Vara Sails app, using Sails-JS, generated clients, React hooks, and low-level Gear-JS only where it adds value. Do not use for Rust-only contract work, raw gstd service design, or non-Vara frontends.
---

# Sails Frontend

## Goal

Keep frontend work on the typed Sails path first: generated `lib.ts` plus `@gear-js/react-hooks`, with `@gear-js/api` reserved for low-level fallback cases that the Sails stack does not cover cleanly.

## Inputs

- `assets/frontend-bootstrap-checklist.md`
- `../../references/sails-frontend-and-gear-js.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../references/sails-cheatsheet.md`
- `../../references/sails-gtest-and-local-validation.md`
- `../../references/scale-binary-decoding-guide.md`
- `../../references/voucher-and-signless-flows.md`

## Standard Path

1. Treat the program `.idl` as the frontend source of truth.
2. Generate or refresh the typed client with `sails-js-cli` before wiring screens, hooks, or forms.
3. Compose the React root around TanStack Query plus Gear providers: query client, API provider, account provider, and alert provider.
4. Prefer `useProgram` with the generated `Program` class for typed service access.
5. Use `useProgramQuery` for Sails queries and `useProgramEvent` only where live subscriptions are actually needed.
6. Use `usePrepareProgramTransaction` to obtain `gasLimit`, `extrinsic`, or fee data before send when the UX needs validation or previews.
7. Use `useSendProgramTransaction` for commands, await `result.response`, and surface pending, success, and failure states in the UI instead of relying only on extrinsic submission.
8. Pass `voucherId` only when the flow is intentionally voucher-backed or prepaid. Treat full gasless or signless UX as a separate product decision; use the dedicated EZ-transactions path when the product spec requires it.
9. Drop to low-level `@gear-js/api` only for dynamic multi-IDL control, metadata work, raw mailbox or voucher flows, or direct `api.message.send`, `api.programState.read`, and `api.programState.readUsingWasm` cases. On those paths, identify whether the bytes are IDL-driven, metadata-driven, or `state.meta.wasm`-driven before decoding.

## Next.js App Router Compatibility

When the target frontend is a Next.js App Router project:

- `@gear-js/api`, `sails-js`, and wallet subdependencies use browser globals and WASM that break in Server Components. Add them to `transpilePackages` in `next.config.js` and mark all Gear provider/hook files with `'use client'`.
- If `@gear-js/react-hooks` or its wallet subdependencies cause persistent server-build failures after `transpilePackages`, fall back to a lower-level `sails-js` + `@gear-js/api` integration path with runtime-only `await import(...)` boundaries in client components. If falling back, commit to the lower-level path for the entire project.
- On the lower-level fallback path, add `@polkadot/util` and `@polkadot/util-crypto` as explicit dependencies — they are no longer pulled in transitively without the hooks stack.
- `next/font/google` fetches fonts at build time and will fail in offline CI or proof-loop environments. Use `next/font/local` or system fonts instead.
- Run `next build` before `tsc --noEmit` in App Router projects; route types are generated during the build step.

See `../../references/sails-frontend-and-gear-js.md` for the full Next.js compatibility guide.

## Repo Layout For Mixed Workspaces

In monorepos with both a Rust Sails program and a web frontend, check for `app/` directory collisions. The Rust program crate conventionally uses `app/` and Next.js App Router also expects `app/`. Common resolution: keep the Rust `app/` crate and place the frontend in `frontend/` or `web/`.

## sails-js-parser Initialization

When using `sails-js` for runtime IDL parsing (not the generated `lib.ts` client path), the `Sails` class requires an explicit parser instance from the separate `sails-js-parser` package. See `../../references/sails-frontend-and-gear-js.md` for the initialization pattern.

## API Surface Validation

Before handoff, validate the installed `sails-js` API surface against the conventions in `../../references/sails-frontend-and-gear-js.md`. Key points:

- The transaction builder method is `signAndSend()`, not `sendAndWait()`.
- Function arguments are positional, not wrapped in objects.
- Confirm `program.<serviceName>.<functionName>` exists on the generated client before wiring UI.

## Dependency Freshness Policy

Before generating or editing a Vara frontend, resolve package versions from the target project and the current package metadata, not from memory.

Order of precedence:
1. Existing repo lockfile and `package.json`
2. Current `peerDependencies` of `@gear-js/react-hooks` and related packages
3. Current published package versions if this is a new project

Rules:
- Do not pin Gear/Vara frontend package versions from memory.
- If the repo already has a lockfile, preserve it unless there is a clear compatibility issue.
- If starting a new frontend, first determine the current compatible package set, then write `package.json`.
- If using `@gear-js/wallet-connect`, also verify the required UI package set and required styles.
- Name the resolved versions explicitly in the output.

## Wallet UI Styling Rule

If the frontend uses packaged Gear wallet/UI components such as:
- `@gear-js/wallet-connect`
- `@gear-js/ui`
- `@gear-js/vara-ui`

then import the required package styles at the app entrypoint before considering the wallet integration complete.

Minimum check:
- wallet button renders correctly
- modal is visually positioned and styled correctly
- alert container is visible and not collapsed

## Wallet Readiness Rule

For wallet-bound actions, distinguish at least these states in the UI:

- wallets are still loading
- no Vara-compatible wallet extension is available
- wallet exists but no account is connected
- account is connected and ready for signing

Do not collapse these states into a single generic “wallet not ready” message.

Disabled signed actions should expose a visible reason, such as:
- wallets are still loading
- no wallet extension found
- connect a wallet first
- program is not ready yet

## Env Validation Rule

Validate required env values such as endpoint and program IDs before rendering feature screens.

Missing env values must fail visibly, not silently.

## Definition of Done

Do not hand off a Vara frontend until all of the following are true:

- dependency versions were resolved from the actual project/package metadata, not memory
- app root includes `QueryClientProvider`, `ApiProvider`, `AccountProvider`, and `AlertProvider`
- if packaged wallet/UI components are used, their styles are imported and the wallet UI is usable; otherwise, the custom wallet flow is visible and usable
- at least one read query works
- at least one signed transaction path is wired and shows disabled, pending, and success or error states in the UI
- signed write actions are disabled when wallet/account prerequisites are missing
- at least one invalid form path is handled without sending a transaction
- affected queries refetch after successful mutations unless an explicit live-subscription strategy is used
- build passes
- installed `sails-js` API surface was validated: `signAndSend` method, positional arguments, and query builder pattern match the conventions in the reference doc
- if runtime IDL parsing is used, `sails-js-parser` is installed and parser initialization is present
- if using Next.js App Router, `transpilePackages` and `'use client'` boundaries are confirmed
- IDL snapshot is checked in or the generation command is documented
- the final note includes exact run commands and required env vars

## Transaction UX Rule

Every write action must expose at least:
- disabled state when prerequisites are missing
- pending state
- success state
- error state with a visible message

Do not rely only on console logs or implicit alerts.

## Final Validation Pass

Before handoff, review the frontend specifically for:
- provider setup
- wallet connection assumptions
- wallet readiness states
- required CSS imports for packaged UI
- transaction status rendering
- disabled states for unauthenticated actions
- query refetch after successful mutations
- invalid form handling before send
- env variable wiring
- package version freshness

## Route Here When

- the builder asks for a React, Vite, or TypeScript dApp on Vara
- the task is wallet connect, account selection, transaction signing, or voucher-aware sends
- the task is wiring Sails queries, commands, events, and typed generated clients
- the task needs program IDs, endpoint env vars, loading states, error states, or response handling in the UI
- the task needs a justified low-level fallback with `@gear-js/api`

## Required Output Shape

Name these decisions explicitly in the work product:

- chosen frontend stack and package surface
- `.idl` and generated client path
- endpoint and program ID env contract
- provider composition at app root
- per-screen mapping of queries, commands, and events
- signing, gas, voucher, and response-handling strategy
- low-level escape hatches, if any
- chosen integration path: hooks-based or lower-level fallback (if Next.js App Router)

## Guardrails

- Prefer generated clients and hooks over hand-built SCALE payloads for standard Sails apps.
- Do not ship seed phrases, private keys, or test mnemonics in frontend code.
- On manual transaction-builder or low-level Gear-JS paths, make the gas strategy explicit.
- Do not enable `watch` subscriptions everywhere by default; only subscribe where the UX truly benefits.
- Do not mix Sails IDL-driven calls with metadata-driven low-level calls unless the reason is named explicitly.
- Do not decode arbitrary raw bytes with plain SCALE rules until you have named whether the source is a Sails interface path, a full-state metadata path, or a state-function path.
- Do not embed machine-specific absolute paths in generated configs, scripts, or documentation. Use project-relative paths.
- When handing off to a frontend, confirm the IDL snapshot is available. Cross-reference `sails-idl-client` for the canonical handoff pattern.
- Do not assume `sendAndWait()` exists on the `sails-js` transaction builder; the correct method is `signAndSend()`.
