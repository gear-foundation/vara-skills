---
name: sails-feature-workflow
description: Use when a builder is changing behavior inside an existing standard Gear/Vara Sails app and needs the correct stage-by-stage workflow. Do not use for greenfield scaffolding, Vara.eth or ethexe paths, or non-Sails repositories.
---

# Sails Feature Workflow

## Goal

Keep feature work inside an existing Sails repo on an explicit sequence instead of skipping straight to code edits or bypassing the typed client path.

If the request targets a released contract, a new deployed contract version, or V1->V2 evolution, route through `../sails-program-evolution/SKILL.md` before normal implementation work continues.

## Required Sequence

1. Clarify the feature in `docs/plans/YYYY-MM-DD-<topic>-spec.md` with `idea-to-spec` and `../../assets/spec-template.md`.
2. Plan architecture or public interface in `...-architecture.md` with `../sails-architecture/SKILL.md` and `../../assets/architecture-template.md`.
3. If the work targets a released contract, introduces a new deployed version, requires cutover planning, or prepares V1->V2 migration, review `../sails-program-evolution/SKILL.md` before task breakdown and coding.
4. If the feature needs API selection across `gstd`, review `../gear-gstd-api-map/SKILL.md` before coding.
5. If the feature changes async behavior, replies, delays, reservations, or waitlist semantics, review `../gear-message-execution/SKILL.md` before coding.
6. Break the work into tasks in `...-tasks.md` with `task-decomposer` and `../../assets/task-plan-template.md`.
7. If the feature introduces a fungible token, mint/burn roles, token-backed accounting, or native-value exchange, review `../awesome-sails-vft/SKILL.md` before coding.
8. Implement the Rust changes through `sails-rust-implementer`.
9. If the public interface changed, refresh the `.idl` and regenerate the typed client through the repo's standard `build.rs` path first. For dedicated Rust client crates, prefer the `sails-rs` build-helper path before a manual generator pipeline.
10. Run `gtest` through `../sails-gtest/SKILL.md`.
11. Run smoke validation only after green `gtest`, using `../sails-local-smoke/SKILL.md`.

## Sponsored UX Cases

- If the feature includes gasless UX, define the voucher flow in the spec and architecture. A voucher lets a sponsor pay gas and fees for approved interactions; it does not make Vara free.
- If the feature includes signless UX, model the temporary delegated account, sub-account, or session flow up front. Prefer existing EZ-transactions or signless or gasless hooks over ad hoc wallet-sign-every-action code.

## References

- `../../references/vara-domain-overview.md`
- `../../references/sails-cheatsheet.md`
- `../../references/gtest-cheatsheet.md`
- `../../references/gear-execution-model.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/sails-gtest-and-local-validation.md`
- `../../references/contract-interface-evolution.md`

## Guardrails

- Do not skip the document chain for “small” features.
- Do not bypass the generated client path with raw payload encoders, hand-built SCALE payloads, or EVM-style bindings.
- Do not claim completion before `gtest` is green and documented.
- Do not treat local-node smoke as a substitute for `gtest`.
- Do not treat released-contract evolution, cutover, or V1->V2 migration as ordinary feature work without routing through the program-evolution flow.
