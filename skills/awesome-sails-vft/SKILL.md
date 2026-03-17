---
name: awesome-sails-vft
description: Use when a builder wants to add a fungible token to a standard Gear/Vara Sails app using awesome-sails building blocks, choose the right VFT-related crates, and wire roles, events, tests, and client integration. Do not use for NFT or RMRK work, abstract tokenomics-only analysis, or non-Sails projects.
---

# Awesome Sails VFT

## Goal

Help the builder add a fungible token layer to a standard Gear/Vara Sails app through awesome-sails without reimplementing standard token behavior from scratch.

## Local Handbook

- `../../references/gear-sails-production-patterns.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../references/sails-gtest-and-local-validation.md`
- `../../references/sails-cheatsheet.md`
- `../../references/awesome-sails-token-patterns.md`

## Local Assets

- `assets/token-scope-checklist.md`
- `assets/token-crate-chooser.md`
- `assets/token-gtest-matrix.md`

## Required Sequence

1. Define token intent and deployment shape with `assets/token-scope-checklist.md`.
2. Choose the smallest `awesome-sails` token stack with `assets/token-crate-chooser.md`.
3. Decide whether the token lives as a dedicated program or as embedded token-related services.
4. Name the role model and event model explicitly.
5. Keep the IDL and generated client path intact.
6. Write and execute the selected tests from `assets/token-gtest-matrix.md`.
7. Route to local smoke only after green gtest.

## Crate Selection Rules

- Use the smallest awesome-sails surface that satisfies the feature.
- Prefer base VFT-compatible behavior over custom token logic.
- Add admin and RBAC layers only when the spec requires privileged token operations.
- Add native-exchange only when value↔token conversion is part of the design.

## Dependency Source Rules

Prefer one of:
- crates.io version dependencies
- pinned git dependencies
- repository-relative `path` dependencies only for intentional local co-development

Do not use absolute paths into `~/.cargo/git/checkouts`, `target`, or other machine-local caches.

## Guardrails

- Do not write a custom fungible token from scratch when awesome-sails already covers the standard path.
- Do not mix unrelated token policy decisions into implementation before the spec is written.
- Do not bypass IDL/generated clients for the normal token path.
- Do not treat token events as optional for production-facing state transitions.
- Do not make every app build its own mint/burn/allowance logic ad hoc.
- Do not point dependencies to `~/.cargo/git/checkouts/...` or other machine-local Cargo cache paths.
- Prefer crates.io versions, a pinned git dependency, or a repository-relative path only when the project intentionally vendors or co-develops the dependency.
