---
name: gear-architecture-planner
description: Use when an approved Gear or Vara spec must be mapped onto program boundaries, services, message flow, and integration surfaces. Do not use when the feature is still undefined or when the task is already reduced to code edits.
---

# Gear Architecture Planner

## Overview

Turn an approved spec into a concrete Gear/Sails architecture note.

## Start Here

Read `../../references/vara-domain-overview.md`, `../../references/sails-cheatsheet.md`, `../../references/sails-program-and-service-architecture.md`, `../../references/gear-messaging-and-replies.md`, and `../../references/sails-idl-client-pipeline.md`.

If the architecture choice depends on what Gear programs can express through `gstd`, review `../gear-gstd-api-map/SKILL.md` before locking the design.

Use `../../assets/architecture-template.md` as the output shape.

Write the result to `docs/plans/YYYY-MM-DD-<topic>-architecture.md`.

## Workflow

1. Confirm the spec artifact exists and is approved.
2. Choose program constructors and service boundaries.
3. Map state ownership, routing, messages, replies, and events.
4. Record generated-IDL or generated-client implications.
5. Capture off-chain components, failure paths, and explicit non-goals.

## Guardrails

- Keep `#[program]` thin and push business logic into services.
- Make the constructor shape and storage pattern explicit instead of leaving them to implementation guesswork.
- Treat generated clients or equivalent route-prefixed encoding as the default Sails message contract.
- Treat actor boundaries and async flow as design constraints.
- Call out remote-call failure policy instead of leaving it implicit.
- Do not collapse architecture into a file-by-file coding checklist.
