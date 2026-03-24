---
name: sails-program-evolution
description: Use when a builder needs to evolve a released Gear or Vara Sails contract, prepare a new deployed contract version, plan safe cutover, or design state migration from V1 to V2. Do not use for greenfield feature work on an unreleased contract, non-Sails repositories, or ethexe-first paths.
---

# Sails Program Evolution

## Overview

Plan how a released Sails contract evolves after deployment.

Use this skill when the work is no longer just “implement a feature”, but instead requires thinking about versioning, compatibility, cutover, `ReadOnly` handling, frontend/indexer impact, or migration from `V1` to `V2`.

## Start Here

Read `../../references/contract-interface-evolution.md`, `../../references/gear-sails-production-patterns.md`, `../../references/sails-idl-client-pipeline.md`, and `../../references/sails-program-and-service-architecture.md`.

Use `../../assets/architecture-template.md` for the architecture note and `../../assets/task-plan-template.md` for the ordered task plan.

Write outputs to:

- `docs/plans/YYYY-MM-DD-<topic>-architecture.md`
- `docs/plans/YYYY-MM-DD-<topic>-tasks.md`

## Route Here When

- a released contract must gain a new deployed version
- public routes, replies, or events may change
- frontend or indexer compatibility must be preserved during cutover
- the old contract may need `ReadOnly` or write-disable behavior
- a future migration path must be designed even if migration is not implemented now
- state migration from `V1` to `V2` is part of scope

## Working Model

1. Classify the change first: additive, breaking, migration-readiness only, or migration now.
2. Treat Gear/Sails evolution as `V1 -> V2 -> cutover`, not as hot-swapping live contract code in place.
3. Keep public routes, reply shapes, and emitted events stable unless the architecture explicitly versions them.
4. Make contract version, status, and cutover behavior explicit.
5. If migration is required, split responsibilities across `V1`, `V2`, and the off-chain migrator.
6. Record frontend, generated-client, and indexer implications before implementation begins.
7. Route implementation to `../sails-architecture/SKILL.md`, `../task-decomposer/SKILL.md`, `../sails-rust-implementer/SKILL.md`, `../sails-idl-client/SKILL.md`, and `../sails-local-smoke/SKILL.md` as needed.

## Default Outputs

The resulting architecture and task artifacts should make these points explicit when relevant:

- whether the change is additive or breaking
- whether a new deployed contract version is required
- whether `ReadOnly` or write-disable behavior is required
- whether migration is in scope now or only prepared for later
- how frontend and indexer switch to the new version
- what rollback target exists during cutover

## Guardrails

- Do not describe Gear/Sails evolution as in-place replacement of live contract code.
- Do not hide compatibility-sensitive changes inside generic “update contract” wording.
- Do not change released public routes or event payloads casually.
- Do not treat IDL regeneration alone as proof of safe rollout.
- Do not merge `V1`, `V2`, and migrator responsibilities into one vague implementation step.
