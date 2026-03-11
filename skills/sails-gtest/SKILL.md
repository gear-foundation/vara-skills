---
name: sails-gtest
description: Use when a builder needs the standard Gear/Vara Sails gtest loop for feature verification, debugging, or regression coverage. Do not use for live-network-only validation, deployment-first workflows, or non-Sails programs.
---

# Sails Gtest

## Goal

Run the Sails-first test loop with generated clients and explicit `gtest` evidence before any live-node smoke step.

## Inputs

- `../../assets/gtest-report-template.md`
- `../../references/gtest-cheatsheet.md`
- `../../references/sails-cheatsheet.md`
- `../../references/sails-gtest-and-local-validation.md`
- `../../references/gear-gas-reservations-and-waitlist.md`

Write the result to `docs/plans/YYYY-MM-DD-<topic>-gtest.md`.

## Expected Loop

1. Confirm the implementation target is ready for verification.
2. Use generated clients or `GtestEnv` instead of hand-built payloads where the workspace supports them.
3. Pick the right `BlockRunMode` and advance blocks explicitly when replies or deferred effects depend on progression.
4. Assert behavior, replies, events, or accounting in the test result, not just compilation.
5. Record failure mode, fix, and passing command output in the gtest note.
6. Route to `../sails-local-smoke/SKILL.md` only after the suite is green.

## Guardrails

- Do not use green `cargo test` output without Sails-appropriate assertions as proof.
- Do not start local-node smoke while `gtest` is still red.
- Do not skip gas or value reasoning when tests depend on it.
