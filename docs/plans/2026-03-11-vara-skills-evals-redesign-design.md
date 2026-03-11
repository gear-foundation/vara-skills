# Vara Skills Evals Redesign

## Summary

Redesign `vara-skills-evals` around the EthSkills philosophy of measuring the specific things LLMs get wrong, not around the current provisional skill names.

The first milestone stays standard Gear/Vara Sails first and treats `gpt-5.4` as the primary evaluation target. Vara.eth-specific cases such as Mirror paths, injected interactions, and Executable Balance remain milestone-two extensions.

## Product Thesis

The eval suite should answer a narrow question:

`Would this agent be safe and correct enough to continue automatically on a Vara/Sails task?`

That means every eval should test one of these:

- factual knowledge the model tends to bluff;
- architecture or workflow choices the model tends to sequence badly;
- generated artifacts that must compile or integrate;
- safety-sensitive mistakes that should block autonomous continuation.

The suite should not be organized around whether an answer “sounds smart.”

## Scope Boundaries

### In scope for milestone one

- standard Gear/Vara Sails knowledge and workflow evals;
- a suite-oriented repo layout;
- explicit grader modes for factual, rubric, and artifact checks;
- fixtures for Rust/Sails artifacts and JavaScript client-library cases;
- a first pack of 12 evals;
- `gpt-5.4` as the first fully supported target.

### Out of scope for milestone one

- Vara.eth-first evals;
- Mirror vs injected interaction path cases;
- Executable Balance or reverse-gas cases;
- `0x` Mirror address cases;
- broad multi-model completion requirements before the `gpt-5.4` baseline is stable.

## Repo Layout

`vara-skills-evals` should be reshaped into type-based suites:

- `evals/knowledge/`
- `evals/design/`
- `evals/codegen/`
- `evals/workflow/`
- `evals/safety/`
- `fixtures/sails-rust/`
- `fixtures/js-client/`
- `judges/`
- `runner/`
- `results/`

This keeps the suite stable even when the public skill catalog changes.

## Case Schema

Each eval file should use a case-oriented schema rather than today’s skill-oriented YAML shape.

Required fields:

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

Optional fields:

- `artifact_checks`
- `fixtures`
- `notes`

## Grader Modes

Three grading modes are needed.

### 1. `assert`

Use for short factual checks and deployment-order assertions.

The answer either names the required fact or it does not.

### 2. `rubric`

Use for design and workflow cases.

The rubric should check whether the model chose the right Vara/Sails primitive and whether it avoided the expected bad instinct.

### 3. `artifact`

Use for generated Rust and JavaScript client artifacts.

The pass condition is not plausibility. The pass condition is:

- the artifact is produced;
- it compiles or runs the expected check;
- it does not invent APIs or imports;
- it uses the right abstraction layer.

## Milestone-One Eval Taxonomy

The first milestone should launch these 12 evals.

### Knowledge

1. `sails-default-path`
2. `idl-client-path`
3. `delayed-messages`
4. `gas-reservation`
5. `waitlist-rent`
6. `voucher-signless`
7. `address-format-ss58`

### Codegen

8. `rust-sails-compile`
9. `js-client-from-idl`

### Workflow

10. `sails-feature-flow`

### Safety

11. `no-low-level-bypass`
12. `no-key-address-hallucination`

## Milestone-One Interpretation

The first milestone intentionally mixes:

- short factual sanity checks;
- scenario-level workflow checks;
- artifact-backed compile or integration checks;
- explicit safety gates.

That is enough to compare agents meaningfully without prematurely expanding into Vara.eth.

## Milestone-Two Extensions

Once the standard Sails path is stable, add extension suites for:

- Executable Balance and reverse-gas;
- Mirror vs injected interaction choice;
- Mirror or `0x` address behavior;
- classic vs Ethereum-facing deployment order;
- other Vara.eth-specific safety pitfalls.

## Fixtures

The fixture layout should match the actual artifact types:

- `fixtures/sails-rust/` for program or workspace generation checks;
- `fixtures/js-client/` for Sails JavaScript client-library usage.

`Sails-JS` is treated as a client library, not as a runtime target.

## Success Criteria

The redesign is successful if:

- every first-milestone eval fits the new suite taxonomy;
- `gpt-5.4` can run the first 12 cases under one consistent runner contract;
- results distinguish measured winners from still-provisional skills or workflows;
- the eval suite now reflects real Vara/Sails wrong instincts rather than only the current public skill names.

## Assumptions

- `vara-skills-evals` remains a separate repo from the product pack.
- `gpt-5.4` is the only model that must be fully supported in this milestone.
- current skill-oriented eval YAML files can be retired or migrated if the new taxonomy makes them redundant.
- standard Gear/Vara Sails remains the only first-class path during this redesign.
