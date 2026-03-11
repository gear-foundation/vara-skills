---
name: sails-rust-implementer
description: Use when approved Gear or Vara tasks require Rust or Sails code changes in a real workspace. Do not use when the spec or architecture is still unsettled, or when the task is only review or deployment.
---

# Sails Rust Implementer

## Overview

Implement approved tasks in Sails-first Rust workspaces without freelancing new scope.

## Start Here

Read `../../references/sails-cheatsheet.md`, `../../references/vara-domain-overview.md`, `../../references/gear-messaging-and-replies.md`, and `../../references/gear-gas-reservations-and-waitlist.md`.

Consume the approved `spec`, `architecture`, and `tasks` artifacts before changing code.

If the target crate explicitly builds an `ethexe` path, stop and hand back to a dedicated ethexe workflow instead of extending this standard Sails pack.

## Workflow

1. Confirm the task is already specified and architecture-approved.
2. Identify the smallest code change that satisfies the current task.
3. Preserve routing, IDL, and client-facing contract stability unless the task explicitly changes them.
4. Keep failure handling aligned with Gear/Vara async semantics.
5. Hand local verification to the gtest loop before claiming the task is done.

## Guardrails

- Do not redesign the feature while coding.
- Prefer Sails-level interfaces over raw payload work unless the task says otherwise.
- Treat value flow, replies, and async ordering as first-class behavior.
- Stop and hand back to planning if implementation uncovers a real architecture gap.
