---
name: gtest-tdd-loop
description: Use when Gear or Vara behavior changes need a deterministic local gtest loop before the work can be considered complete. Do not use for deploy-only work, live-node-only smoke checks, or features without a local test target.
---

# Gtest Tdd Loop

## Overview

Drive local verification through a red-green loop and summarize failures in a machine-readable form.

## Start Here

Read `../../references/gtest-cheatsheet.md`.

Use `../../assets/gtest-report-template.md` as the output shape.

Write the result to `docs/plans/YYYY-MM-DD-<topic>-gtest.md`.

Use `../../scripts/run_gtest.sh` to execute the loop and `../../scripts/parse_test_output.py` to summarize failures.

**REQUIRED SUB-SKILLS:** Use `gtest-core-workflows` and `gear-test-sails-program`.

## Workflow

1. Write or update the smallest failing gtest case for the current task.
2. Verify the test fails for the expected reason.
3. Apply the minimal implementation change.
4. Run the local loop through `../../scripts/run_gtest.sh`.
5. Capture the parser output and record the final green or remaining gap state.

## Guardrails

- Do not skip the failing-test step.
- Do not claim success from compile output alone.
- Keep gtest evidence tied to the current task, not a generic workspace run.
- Escalate if the workspace cannot produce a stable local gtest target.
