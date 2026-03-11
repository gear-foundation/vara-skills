---
name: task-decomposer
description: Use when approved spec and architecture artifacts must become an ordered implementation plan for Gear or Vara work. Do not use when the architecture is still unsettled or when the request is only asking for a high-level idea.
---

# Task Decomposer

## Overview

Break the approved spec and architecture into a small, reviewable task plan for disciplined implementation.

## Start Here

Use `../../assets/task-plan-template.md` as the output shape.

Write the result to `docs/plans/YYYY-MM-DD-<topic>-tasks.md`.

## Workflow

1. Confirm both the spec and architecture artifacts exist.
2. Split work into dependency-ordered tasks with clear handoff points.
3. Attach explicit verification steps and review checkpoints to each task.
4. Make gtest expectations and artifact updates part of the task order.
5. Record rollback notes for risky or stateful changes.

## Guardrails

- Keep tasks small enough for TDD and frequent commits.
- Do not merge planning, coding, and validation into one step.
- Make prereqs explicit instead of relying on tribal knowledge.
- Keep the plan executable from the artifact chain alone.
