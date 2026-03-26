# Changelog

All notable changes to this project will be documented in this file.

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
