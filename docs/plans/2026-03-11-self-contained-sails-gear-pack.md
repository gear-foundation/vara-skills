# Self-Contained Sails Gear Pack Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make this repository portable and self-contained for standard Gear/Vara Sails program-development knowledge, workflows, and skill routing.

**Architecture:** Keep the existing Sails-builder catalog as the public entry surface, move the imported Gear/Sails knowledge into local repo references, and rewrite each workflow skill to rely only on local files. Add a focused `gear-message-execution` skill if message/reply execution flow remains a routing gap after the local handbook is in place.

**Tech Stack:** Markdown skill docs, Python repo-contract tests, shell install script, repository-level verification via `make verify`

---

### Task 1: Lock The Self-Contained Repo Contract

**Files:**
- Modify: `tests/test_repo_layout.py`
- Modify: `tests/test_skill_catalog.py`
- Modify: `tests/test_install_codex_skills.py`
- Test: `tests/test_repo_layout.py`
- Test: `tests/test_skill_catalog.py`
- Test: `tests/test_install_codex_skills.py`

**Step 1: Write the failing tests**

Add assertions for:

- `docs/plans/2026-03-11-self-contained-sails-gear-pack-design.md`
- `docs/plans/2026-03-11-self-contained-sails-gear-pack.md`
- new repo references:
  - `references/gear-execution-model.md`
  - `references/gear-messaging-and-replies.md`
  - `references/gear-gas-reservations-and-waitlist.md`
  - `references/sails-program-and-service-architecture.md`
  - `references/sails-idl-client-pipeline.md`
  - `references/sails-gtest-and-local-validation.md`
- new skill directory:
  - `skills/gear-message-execution/`
- install-script expectations aligned with the current public catalog plus `gear-message-execution`
- skill-catalog assertions that local skills reference local handbook files instead of `../gear-skills` or `~/.codex/skills`

**Step 2: Run tests to verify they fail**

Run:

```bash
python3 tests/test_repo_layout.py
python3 tests/test_skill_catalog.py
python3 tests/test_install_codex_skills.py
```

Expected:

- `test_repo_layout.py` fails on missing new reference files and new skill directory.
- `test_skill_catalog.py` fails because current skills still delegate to external skill names and do not mention the new local references.
- `test_install_codex_skills.py` fails until expected installed skills match the current catalog.

**Step 3: Write minimal implementation**

Create placeholder handbook files with headings, add the `skills/gear-message-execution/` directory with required `assets/`, `references/`, `scripts/`, and update install-test expectations to the actual catalog.

**Step 4: Run tests to verify they pass**

Run:

```bash
python3 tests/test_repo_layout.py
python3 tests/test_install_codex_skills.py
```

Expected: PASS

Leave `tests/test_skill_catalog.py` red until the real skill rewrites land in later tasks.

**Step 5: Commit**

```bash
git add tests/test_repo_layout.py tests/test_skill_catalog.py tests/test_install_codex_skills.py references/gear-execution-model.md references/gear-messaging-and-replies.md references/gear-gas-reservations-and-waitlist.md references/sails-program-and-service-architecture.md references/sails-idl-client-pipeline.md references/sails-gtest-and-local-validation.md skills/gear-message-execution
git commit -m "test: lock self-contained pack contract"
```

### Task 2: Import The Gear And Sails Reference Handbook

**Files:**
- Modify: `references/vara-domain-overview.md`
- Modify: `references/sails-cheatsheet.md`
- Modify: `references/gtest-cheatsheet.md`
- Modify: `references/gear-execution-model.md`
- Modify: `references/gear-messaging-and-replies.md`
- Modify: `references/gear-gas-reservations-and-waitlist.md`
- Modify: `references/sails-program-and-service-architecture.md`
- Modify: `references/sails-idl-client-pipeline.md`
- Modify: `references/sails-gtest-and-local-validation.md`
- Test: `tests/test_skill_catalog.py`

**Step 1: Write the failing test**

Extend `tests/test_skill_catalog.py` so it asserts the new handbook covers:

- execution rollback and block progression
- send/reply/delayed/reply-hook semantics
- reservations and waitlist rent/expiry
- `#[program]` / `#[service]` boundaries and async revalidation
- `build.rs`, `build_client`, `ClientBuilder`, and `.idl` expectations
- `GtestEnv`, `BlockRunMode`, typed local smoke, and real program-id usage

**Step 2: Run test to verify it fails**

Run:

```bash
python3 tests/test_skill_catalog.py
```

Expected: FAIL because the new local reference files are still placeholders or missing required content.

**Step 3: Write minimal implementation**

Populate the new handbook files by adapting the useful builder-facing material from the upstream Gear/Sails skills. Rewrite all copied guidance to:

- remove machine-specific absolute paths
- remove dependency on sibling repos
- stay within standard Gear/Vara Sails scope
- keep the documents compact enough to remain searchable

Update the three existing cheatsheets only where they should summarize or point into the expanded handbook.

**Step 4: Run test to verify it passes**

Run:

```bash
python3 tests/test_skill_catalog.py
```

Expected: PASS for the new reference-content assertions or progress to the next red assertions in workflow skills.

**Step 5: Commit**

```bash
git add references/vara-domain-overview.md references/sails-cheatsheet.md references/gtest-cheatsheet.md references/gear-execution-model.md references/gear-messaging-and-replies.md references/gear-gas-reservations-and-waitlist.md references/sails-program-and-service-architecture.md references/sails-idl-client-pipeline.md references/sails-gtest-and-local-validation.md tests/test_skill_catalog.py
git commit -m "docs: add self-contained gear and sails handbook"
```

### Task 3: Rewrite The Public Skills To Use Only Local Content

**Files:**
- Modify: `SKILL.md`
- Modify: `skills/ship-sails-app/SKILL.md`
- Modify: `skills/sails-new-app/SKILL.md`
- Modify: `skills/sails-feature-workflow/SKILL.md`
- Modify: `skills/sails-architecture/SKILL.md`
- Modify: `skills/sails-idl-client/SKILL.md`
- Modify: `skills/sails-gtest/SKILL.md`
- Modify: `skills/sails-local-smoke/SKILL.md`
- Modify: `skills/gear-message-execution/SKILL.md`
- Test: `tests/test_skill_catalog.py`
- Test: `tests/test_skill_validation.py`

**Step 1: Write the failing test**

Add or tighten assertions in `tests/test_skill_catalog.py` so the public skills:

- route only to local skills
- mention the new handbook files where relevant
- keep the standard Gear/Vara Sails boundary explicit
- describe message flow, replies, delayed work, reservations, generated clients, `gtest`, and typed local smoke in the appropriate skill
- expose `gear-message-execution` through the top-level router

**Step 2: Run tests to verify they fail**

Run:

```bash
python3 tests/test_skill_catalog.py
python3 tests/test_skill_validation.py
```

Expected:

- `test_skill_catalog.py` fails because the current skill text still contains external delegations and lacks the new local-routing language.
- `test_skill_validation.py` may fail if the new skill frontmatter or directory layout is still incomplete.

**Step 3: Write minimal implementation**

Rewrite the skill docs so they are compact routers into the local handbook:

- keep trigger descriptions strict and portable
- remove references to upstream skill names that do not ship in this repo
- add the minimum local guidance needed at the point of use
- keep `gear-message-execution` focused on debugging/designing Gear execution and reply behavior for Sails builders

**Step 4: Run tests to verify they pass**

Run:

```bash
python3 tests/test_skill_catalog.py
python3 tests/test_skill_validation.py
```

Expected: PASS

**Step 5: Commit**

```bash
git add SKILL.md skills/ship-sails-app/SKILL.md skills/sails-new-app/SKILL.md skills/sails-feature-workflow/SKILL.md skills/sails-architecture/SKILL.md skills/sails-idl-client/SKILL.md skills/sails-gtest/SKILL.md skills/sails-local-smoke/SKILL.md skills/gear-message-execution/SKILL.md tests/test_skill_catalog.py
git commit -m "feat: make sails builder skills self-contained"
```

### Task 4: Align Product Docs And Packaging Surface

**Files:**
- Modify: `README.md`
- Modify: `openclaw-skill/SKILL.md`
- Modify: `openclaw-skill/README.md`
- Test: `tests/test_packaging_metadata.py`
- Test: `tests/test_repo_layout.py`

**Step 1: Write the failing test**

Extend repo and packaging tests to require:

- self-contained handbook language in `README.md`
- the new `gear-message-execution` route if it remains in the public catalog
- OpenClaw wrapper text that still constrains scope to standard Gear/Vara Sails while describing the local knowledge surface

**Step 2: Run tests to verify they fail**

Run:

```bash
python3 tests/test_packaging_metadata.py
python3 tests/test_repo_layout.py
```

Expected: FAIL until docs and wrapper text reflect the new local-content model.

**Step 3: Write minimal implementation**

Update the repo README and wrapper docs so the published pack description matches the self-contained handbook design and current catalog.

**Step 4: Run tests to verify they pass**

Run:

```bash
python3 tests/test_packaging_metadata.py
python3 tests/test_repo_layout.py
```

Expected: PASS

**Step 5: Commit**

```bash
git add README.md openclaw-skill/SKILL.md openclaw-skill/README.md tests/test_packaging_metadata.py tests/test_repo_layout.py
git commit -m "docs: describe self-contained sails builder pack"
```

### Task 5: Verify The Full Repository Surface

**Files:**
- Modify: `scripts/install-codex-skills.sh` only if verification exposes a real install mismatch
- Test: `Makefile`

**Step 1: Write the failing test**

No new test file is required. Use the existing repo verification surface as the release gate.

**Step 2: Run verification to verify current state**

Run:

```bash
make verify
```

Expected: PASS. If it fails, fix the smallest real contract mismatch and rerun.

**Step 3: Write minimal implementation**

Only if needed, adjust `scripts/install-codex-skills.sh` or test expectations so the install surface matches the final public skill catalog.

**Step 4: Run verification to verify it passes**

Run:

```bash
make verify
```

Expected: PASS

**Step 5: Commit**

```bash
git add Makefile scripts/install-codex-skills.sh tests/test_install_codex_skills.py
git commit -m "test: verify self-contained skill pack"
```
