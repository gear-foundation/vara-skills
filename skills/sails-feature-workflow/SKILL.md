---
name: sails-feature-workflow
description: Use when a builder is changing behavior inside an existing standard Gear/Vara Sails app and needs the correct stage-by-stage workflow. Do not use for greenfield scaffolding, Vara.eth or ethexe paths, or non-Sails repositories.
---

# Sails Feature Workflow

## Goal

Keep feature work inside an existing Sails repo on an explicit sequence instead of skipping straight to code edits or bypassing the typed client path.

## Required Sequence

1. Clarify the feature in `docs/plans/YYYY-MM-DD-<topic>-spec.md` with `idea-to-spec` and `../../assets/spec-template.md`.
2. Plan architecture or public interface in `...-architecture.md` with `../sails-architecture/SKILL.md` and `../../assets/architecture-template.md`.
3. If the feature changes async behavior, replies, delays, reservations, or waitlist semantics, review `../gear-message-execution/SKILL.md` before coding.
4. Break the work into tasks in `...-tasks.md` with `task-decomposer` and `../../assets/task-plan-template.md`.
5. Implement the Rust changes through `sails-rust-implementer`.
6. If the interface changed or the app needs integration work, refresh the `.idl` and generated client or typed client path through `../sails-idl-client/SKILL.md`.
7. Run `gtest` through `../sails-gtest/SKILL.md`.
8. Run smoke validation only after green `gtest`, using `../sails-local-smoke/SKILL.md`.

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

## Guardrails

- Do not skip the document chain for “small” features.
- Do not bypass the generated client path with raw payload encoders, hand-built SCALE payloads, or EVM-style bindings.
- Do not claim completion before `gtest` is green and documented.
- Do not treat local-node smoke as a substitute for `gtest`.
