# Vara Skills Evals Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign `vara-skills-evals` around suite-based eval taxonomy and ship the first 12 standard Gear/Vara Sails evals with `gpt-5.4` as the first required target.

**Architecture:** Replace today’s skill-oriented YAML catalog with suite-oriented eval cases under `knowledge`, `design`, `codegen`, `workflow`, and `safety`. Keep the runner small but explicit: one case schema, three grader modes, fixtures for Rust and JavaScript client-library artifacts, and benchmark results written under `results/`.

**Tech Stack:** Markdown planning docs, YAML eval files, Bash runner scripts, Python 3 tests, Rust fixture workspaces, JavaScript client-library fixtures, `codex exec` for model runs.

---

### Task 1: Lock the redesign in repo documentation and failing tests

**Files:**
- Create: `/Users/ukintvs/Documents/projects/gear-agent-skills/docs/plans/2026-03-11-vara-skills-evals-redesign-design.md`
- Create: `/Users/ukintvs/Documents/projects/gear-agent-skills/docs/plans/2026-03-11-vara-skills-evals-redesign.md`
- Modify: `/Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_repo_layout.py`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py`

**Step 1: Add the failing suite-layout test**

Require the eval repo to expose:

- `evals/knowledge`
- `evals/design`
- `evals/codegen`
- `evals/workflow`
- `evals/safety`
- `fixtures/sails-rust`
- `fixtures/js-client`
- `judges`

**Step 2: Add the failing suite-catalog test**

Require the first 12 eval files to exist at their new suite paths.

**Step 3: Run tests to verify they fail**

Run:

```bash
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_repo_layout.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py
```

Expected:

- both tests `FAIL` because the new taxonomy does not exist yet.

**Step 4: Commit the planning docs and failing tests**

```bash
git -C /Users/ukintvs/Documents/projects/vara-skills-evals add tests/test_repo_layout.py tests/test_suite_catalog.py
git -C /Users/ukintvs/Documents/projects/gear-agent-skills add docs/plans/2026-03-11-vara-skills-evals-redesign-design.md docs/plans/2026-03-11-vara-skills-evals-redesign.md
git -C /Users/ukintvs/Documents/projects/vara-skills-evals commit -m "test: add suite-based eval repo expectations"
git -C /Users/ukintvs/Documents/projects/gear-agent-skills commit -m "docs: add evals redesign design and plan"
```

### Task 2: Create the suite layout and grader contracts

**Files:**
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/design/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/codegen/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/workflow/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/safety/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/fixtures/sails-rust/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/fixtures/js-client/.gitkeep`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/judges/assert.md`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/judges/rubric.md`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/judges/artifact.md`
- Modify: `/Users/ukintvs/Documents/projects/vara-skills-evals/README.md`

**Step 1: Create the suite directories**

Add the new `evals/`, `fixtures/`, and `judges/` layout.

**Step 2: Write the grader contract docs**

Document `assert`, `rubric`, and `artifact` expectations in separate markdown files.

**Step 3: Update the README**

Describe the new taxonomy, the first 12 evals, and the fact that `gpt-5.4` is the first required target.

**Step 4: Run layout tests**

Run:

```bash
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_repo_layout.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py
```

Expected:

- layout assertions get closer to green
- catalog still `FAIL` until the actual eval files land

**Step 5: Commit**

```bash
git -C /Users/ukintvs/Documents/projects/vara-skills-evals add README.md evals fixtures judges
git -C /Users/ukintvs/Documents/projects/vara-skills-evals commit -m "docs: add suite-based eval taxonomy"
```

### Task 3: Replace the current YAML schema with case-oriented eval files

**Files:**
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/sails-default-path.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/idl-client-path.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/delayed-messages.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/gas-reservation.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/waitlist-rent.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/voucher-signless.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/knowledge/address-format-ss58.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/codegen/rust-sails-compile.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/codegen/js-client-from-idl.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/workflow/sails-feature-flow.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/safety/no-low-level-bypass.yaml`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/evals/safety/no-key-address-hallucination.yaml`
- Modify: `/Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py`

**Step 1: Expand the suite-catalog test**

Require each new file to contain:

- `id`
- `suite`
- `topic`
- `target_models`
- `skill_paths`
- `kind`
- `prompt`
- `expected`
- `fail_if`
- `grader`

**Step 2: Run the test to verify it fails**

Run:

```bash
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py
```

Expected:

- `FAIL` because the files and schema do not exist yet.

**Step 3: Write the 12 eval files**

Use standard Gear/Vara Sails docs and local repos as the source of truth.

**Step 4: Re-run the catalog test**

Run:

```bash
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_eval_catalog.py
```

Expected:

- new suite-catalog test `PASS`
- old skill-catalog test can either be retired or updated as part of the migration decision

**Step 5: Commit**

```bash
git -C /Users/ukintvs/Documents/projects/vara-skills-evals add evals tests/test_suite_catalog.py tests/test_eval_catalog.py
git -C /Users/ukintvs/Documents/projects/vara-skills-evals commit -m "test: add first suite-based Vara eval cases"
```

### Task 4: Add Rust and JavaScript client fixtures plus artifact tests

**Files:**
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/fixtures/sails-rust/README.md`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/fixtures/js-client/README.md`
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_artifact_fixtures.py`
- Modify: `/Users/ukintvs/Documents/projects/vara-skills-evals/runner/run.sh`

**Step 1: Write the failing fixture test**

Require the fixture directories and their README contracts to exist.

**Step 2: Run the test to verify it fails**

Run:

```bash
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_artifact_fixtures.py
```

Expected:

- `FAIL` because the fixture contracts are not written yet.

**Step 3: Add the fixture contract docs**

Document what the Rust compile eval and the JavaScript client-library eval are allowed to generate and check.

**Step 4: Extend the runner contract**

Teach `runner/run.sh` to recognize `artifact` grader cases and dispatch fixture-aware checks, even if the first implementation is a minimal scaffold.

**Step 5: Re-run tests**

Run:

```bash
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_artifact_fixtures.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_runner_smoke.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_runner_slice.py
```

Expected:

- all tests `PASS`

**Step 6: Commit**

```bash
git -C /Users/ukintvs/Documents/projects/vara-skills-evals add fixtures runner/run.sh tests/test_artifact_fixtures.py
git -C /Users/ukintvs/Documents/projects/vara-skills-evals commit -m "feat: add artifact fixture contracts"
```

### Task 5: Run the first full `gpt-5.4` suite and record results

**Files:**
- Create: `/Users/ukintvs/Documents/projects/vara-skills-evals/results/YYYY-MM-DD-gpt54-suite-report.md`
- Modify: `/Users/ukintvs/Documents/projects/gear-agent-skills/README.md`
- Modify: `/Users/ukintvs/Documents/projects/gear-agent-skills/tests/test_skill_catalog.py`

**Step 1: Run the milestone-one suite**

Use `gpt-5.4` as the only required target and run the 12 cases through the new taxonomy.

**Step 2: Write the report**

Record:

- per-case result
- suite totals
- measured winners
- ties
- regressions
- blocked or incomplete artifact checks

**Step 3: Align the product repo docs**

Update the product README and catalog expectations so they refer to the milestone-one `gpt-5.4` eval suite rather than the earlier seven-skill builder slice.

**Step 4: Verify**

Run:

```bash
make -C /Users/ukintvs/Documents/projects/gear-agent-skills verify
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_repo_layout.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_suite_catalog.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_runner_smoke.py
python3 /Users/ukintvs/Documents/projects/vara-skills-evals/tests/test_runner_slice.py
```

Expected:

- all checks `PASS`

**Step 5: Commit**

```bash
git -C /Users/ukintvs/Documents/projects/vara-skills-evals add results README.md tests
git -C /Users/ukintvs/Documents/projects/vara-skills-evals commit -m "results: add first suite-based gpt-5.4 report"
git -C /Users/ukintvs/Documents/projects/gear-agent-skills add README.md tests/test_skill_catalog.py
git -C /Users/ukintvs/Documents/projects/gear-agent-skills commit -m "docs: align pack with suite-based gpt-5.4 evals"
```

## Assumptions

- `/Users/ukintvs/Documents/projects/vara-skills-evals` remains the measurement repo for the pack.
- `gpt-5.4` is the only model that must be fully green for this milestone.
- the current skill-oriented eval files may be migrated or retired during the redesign.
- milestone one remains standard Gear/Vara Sails only; Vara.eth-specific evals are deferred.
