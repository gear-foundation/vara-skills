# Changelog

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-04-27

vara-wallet 0.15.0 was the first npm publish since 0.10.0; 0.16.0 followed five days later with the agent-UX hardening pass. This release captures both surfaces in one cut. Skipping a separate 2.1.x for the 0.13-0.15 work because none of those versions reached npm.

### Updated — vara-wallet skill, 0.13/0.14 surface
- IDL Resolution: documented the on-chain WASM extraction path for v2 programs (`gearProgram.originalCodeStorage`), local cache at `~/.vara-wallet/idl-cache/`, and bundled VFT/Rivr DEX IDLs. v2 programs no longer need `--idl` after first call.
- Quick Reference: added `discover` introspection, `--dry-run` payload encoding (no signing/submit), `--args-file` (with stdin support), `idl import` for seeding the cache, `subscribe messages` IDL-aware decoding, and `watch` event streaming.
- Workflow examples: dry-run preview, stdin args-file for nested JSON, IDL-aware event monitoring.
- Error Recovery: added `AMBIGUOUS_EVENT`, `INVALID_ARGS_SOURCE`, `STDIN_IS_TTY`, `CONFLICTING_OPTIONS`, `PROGRAM_ERROR` (then refreshed in the 0.16 pass below).

### Updated — vara-wallet skill, 0.15.0 surface
- Units vocabulary unified to `human` / `raw` across `transfer`, `vft`, and `dex`. Legacy `vara` / `token` literals retired and now error with `INVALID_UNITS`.
- `--dry-run` and `--estimate` compose on `call` (account required); previously mutually exclusive.
- `subscribe messages --type` renamed to `--event` for consistency with `watch`.
- `metaStorageUrl` config key and `VARA_META_STORAGE` env var removed; meta-storage IDL fallback dropped.

### Updated — vara-wallet skill, 0.16.0 surface
- New **"Structured Errors (0.16+)"** section: `reason` + `programMessage` JSON shape, `Result::unwrap` strip, jq case-switch with pre-0.16 fallback.
- Error Recovery: added `INVALID_ARGS_FORMAT` and `INVALID_ADDRESS` rows; refreshed `PROGRAM_ERROR` and `IDL_NOT_FOUND` rows for the new structured fields and the "This is a v1 contract" diagnostic.
- IDL Resolution: framed v1 path as the expected route for stable Sails 0.10.x builders, not as a v2 fallback.
- Setup: minimum vara-wallet version pinned to 0.16.0.
- Guardrails: `calculateGas` failures now classified as `PROGRAM_ERROR` instead of opaque gas errors.

## [2.1.0] - 2026-04-02

### Updated
- `vara-wallet` skill updated for v0.9.0: `--network` shorthand, `config` CLI, `--estimate`, connection timeout, `--idl`/`--init`/`--args` constructor encoding, faucet command, program list default limit, SS58 output
- `sails-local-smoke` skill updated with `--network local` and `config set network local` alternatives
- `sails-gtest-and-local-validation` reference updated with `--network local`, IDL-based deploy, multi-constructor `--init` flag

## [2.0.0] - 2026-03-29

### Changed (BREAKING)
- **Baseline reverted to `sails-rs 0.10.2` (stable)** on main branch. The 1.0.0-beta.2 content is preserved on the `sails-beta` branch.
- Reason: beta.2 ecosystem has unresolved blockers (unpublished npm packages, vara-wallet v2 IDL incompatibility, no delayed message header helper). Stable builders should not hit these issues.
- All beta-specific patterns (ReflectHash, binary header protocol, IDL V2, edition 2024) moved to `sails-beta` branch
- Build.rs: reverted to standalone `sails_rs::build_wasm()` pattern
- Troubleshooting table kept but trimmed to stable-relevant errors only
- `cargo sails new` remains the default bootstrap command

### Added
- `sails-beta` branch created as the home for all 1.0.0-beta.2 content, including friction fixes (troubleshooting, constructor payload, delayed message versioning, JS ecosystem status)
- Cross-version notes in references pointing to `sails-beta` branch for beta patterns
- Post-deploy verification guidance in local-smoke skill and reference
- BTreeMap key types pitfall in sails-idl-client skill
- Troubleshooting table for top 3 stable compile errors in sails-cheatsheet

## [1.4.0] - 2026-03-27

### Added
- Sails 1.0.0-beta baseline: ReflectHash derive pattern, Sails Header Protocol reference, IDL V2 format guide, new `#[export]` options (`overrides`, `entry_id`, `throws`)
- `sails-new-app`: Troubleshooting section for broken scaffold recovery with fallback manual bootstrap sequence
- `sails-idl-client`: Generated Client Pitfalls section covering `no_std` double-injection in hand-assembled workspaces and custom `BTreeMap` key type decoding issues
- `sails-gtest`: Common Pitfalls section covering Rust 2024 listener lifetime bindings and program balance accounting with existential deposit
- IDL V2 Format section in `sails-idl-client-pipeline.md` with syntax overview (version header, Rust-like types, service-scoped types, `@query`, `throws`, `@partial`)
- `cargo sails client-js` CLI and `cargo sails idl -n` flag documented
- 0.10.x legacy notes in reference files where patterns differ from 1.0.0-beta (build.rs, ReflectHash, header protocol)
- Test assertions for new skill sections (Troubleshooting, Generated Client Pitfalls, Common Pitfalls, ReflectHash)

### Changed
- Scaffold command updated from `cargo sails program` to `cargo sails new` across all skills, references, README, and tests (9 content locations + 3 test assertions)
- Version baseline updated from `sails-rs 0.10.2` to `sails-rs 1.0.0-beta.1` across all references and skills
- Install command pinned to `cargo install sails-cli@1.0.0-beta.1 --locked` in `sails-dev-env`
- Root program `build.rs` pattern updated to chained `build_wasm()` + `ClientBuilder::from_wasm_path().build_idl()`
- Canonical workspace layout updated with new `src/lib.rs` wasm re-export pattern

## [1.3.1] - 2026-03-26

### Added
- `references/voucher-and-signless-flows.md` — procedural-first reference covering voucher lifecycle, signless sessions, EZ-transactions, JS API surface, on-chain extrinsics, testing guidance, and failure modes
- Builder recipes for voucher-only, signless session, and full gasless+signless flows
- Cross-references to voucher doc from ship-sails-app, sails-feature-workflow, sails-frontend, sails-local-smoke, and vara-wallet skills
- Test assertions for voucher reference content, cross-references, and wiki URL leakage prevention

### Changed
- Demoted inline voucher prose in ship-sails-app and sails-feature-workflow to one-line pointers to the canonical reference
- Corrected `api.voucher.exists` signature to `(accountId, programId)` and `api.voucher.issue` return type documentation
- Added backend sponsor service as explicit prerequisite for EZ-Transactions

### Fixed
- Duplicate `## Environment Contract` heading in sails-frontend-and-gear-js.md

## [1.3.0] - 2026-03-26

### Added
- Auto-update check that runs on each skill invocation via preamble in entry-point skills
- `bin/vara-skills-update-check` script with cache TTL, snooze system, and graceful degradation
- `skills/vara-skills-upgrade/` skill for inline and standalone upgrade flows
- `VERSION` file as single source of truth for version, kept in sync with `marketplace.json`
- 15 new tests for update check script covering all code paths
- `make test-update` target and VERSION tag verification in release workflow
