# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2026-03-26

### Added
- Auto-update check that runs on each skill invocation via preamble in entry-point skills
- `bin/vara-skills-update-check` script with cache TTL, snooze system, and graceful degradation
- `skills/vara-skills-upgrade/` skill for inline and standalone upgrade flows
- `VERSION` file as single source of truth for version, kept in sync with `marketplace.json`
- 15 new tests for update check script covering all code paths
- `make test-update` target and VERSION tag verification in release workflow
