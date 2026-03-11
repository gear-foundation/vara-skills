---
name: gear-architecture-planner
description: Use when an approved Gear or Vara spec must be mapped onto program boundaries, services, message flow, and integration surfaces. Do not use when the feature is still undefined or when the task is already reduced to code edits.
---

# Gear Architecture Planner

## Overview

Turn an approved spec into a concrete Gear/Sails architecture note.

## Start Here

Read `../../references/vara-domain-overview.md` and `../../references/sails-cheatsheet.md`.

Use `../../assets/architecture-template.md` as the output shape.

Write the result to `docs/plans/YYYY-MM-DD-<topic>-architecture.md`.

**REQUIRED SUB-SKILLS:** Use `sails-program-architecture-patterns`, `gear-messaging-model`, and `sails-idl-and-client-pipeline`.

## Workflow

1. Confirm the spec artifact exists and is approved.
2. Choose program and service boundaries.
3. Map state ownership, routing, messages, replies, and events.
4. Record generated-IDL or generated-client implications.
5. Capture off-chain components, failure paths, and explicit non-goals.

## Guardrails

- Keep `#[program]` thin and push business logic into services.
- Treat actor boundaries and async flow as design constraints.
- Call out remote-call failure policy instead of leaving it implicit.
- Do not collapse architecture into a file-by-file coding checklist.
