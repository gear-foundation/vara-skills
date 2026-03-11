---
name: idea-to-spec
description: Use when a user has a new Gear or Vara feature idea, product request, or protocol change that must become an implementable spec. Do not use for deployment-only work, runtime review, or post-release observation.
---

# Idea To Spec

## Overview

Convert a rough request into a spec that is specific enough for architecture and implementation planning.

## Start Here

Read `../../references/vara-domain-overview.md` first.

Use `../../assets/spec-template.md` as the output shape.

Write the result to `docs/plans/YYYY-MM-DD-<topic>-spec.md`.

## Workflow

1. Clarify the user goal, scope, and non-goals.
2. Identify actors, state changes, messages, replies, and events.
3. Record invariants, failure paths, and edge cases that follow from Gear/Vara actor semantics.
4. Turn the result into explicit acceptance criteria.
5. Stop when the next step is architecture, not coding.

## Guardrails

- Treat async messaging as the default execution model.
- Name recovery and retry behavior when the feature crosses actor boundaries.
- Keep the spec implementation-agnostic enough that architecture still has work to do.
- Do not skip invariants or acceptance criteria.
