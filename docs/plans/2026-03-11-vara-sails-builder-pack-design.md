# Vara Sails Builder Pack Design

## Summary

Build a Vara analogue to `ethskills`, but optimized for standard Gear/Vara Sails app builders instead of general Ethereum development.

The first release is not a website. It is a portable markdown-first skill pack plus a separate eval suite that proves whether the pack creates measurable uplift for Codex, Claude, and OpenClaw users.

## Product Thesis

`ethskills` is useful because it does three things at once:

1. publishes URL-stable, fetchable skill documents;
2. routes agents through a small set of relevant topic and workflow skills;
3. measures whether those skills actually improve model behavior.

The Vara version should copy that pattern, but adapt it to Sails builders:

- focus on standard Gear/Vara Sails first, not Vara.eth;
- optimize for both new app creation and existing app feature work;
- keep the first wave narrow and opinionated;
- define the catalog by measured uplift, not by intuition.

## Audience

The first audience is `Sails app builders`.

This includes:

- developers starting a new Sails app;
- developers adding features to an existing Sails app;
- agent users who need correct Sails architecture, IDL/client wiring, `gtest`, and local-node validation.

This does not initially target:

- general Gear runtime contributors;
- broad protocol research users;
- Vara.eth-first builders.

## Scope Boundaries

### In scope for v1

- portable `SKILL.md` content for Codex, Claude, and OpenClaw;
- one top-level Sails-builder router skill;
- approximately 6-8 candidate first-wave skills;
- Sails-first workflow routing;
- benchmark-driven skill selection;
- standard Gear/Vara Sails only.

### Out of scope for v1

- the public website;
- large topic encyclopedias or protocol catalogs;
- Vara.eth / ethexe as a first-class path;
- command-first platform integrations;
- shipping a broad public taxonomy before the pack proves itself locally.

## Repo Split

The work should live in two repos.

### 1. `vara-skills`

This is the product repo. It owns:

- the portable skill documents;
- shared references and templates;
- Codex installation flow;
- Claude plugin metadata;
- OpenClaw wrapper metadata or entry skills;
- later website publication inputs.

This repo should stay focused on `builder-facing content and packaging`.

### 2. `vara-skills-evals`

This is the measurement repo. It owns:

- eval definitions;
- A/B runner scripts;
- judge prompt;
- model configuration;
- results and regression history;
- release-gate logic for candidate skills.

This repo should stay focused on `proving uplift`.

## Content Architecture

The pack should be `portable, markdown-first, and workflow-first`.

### Source of truth

The repo is the source of truth. The website is added later as a publication surface mirroring the same markdown files.

### Delivery adapters

- `Codex`: installable local skills repo with an install script
- `Claude`: plugin metadata that points at the same skill directories
- `OpenClaw`: a lightweight wrapper or top-level portable skill

The design principle is:

`one content model, three runtime adapters`

## First-Wave Skill Shape

The first release should expose one router plus a narrow candidate pack.

### Router

- `ship-sails-app`

This is the top-level entrypoint. It routes agents based on builder intent and stage.

### Candidate first-wave skills

- `sails-new-app`
- `sails-feature-workflow`
- `sails-architecture`
- `sails-idl-client`
- `sails-gtest`
- `sails-local-smoke`

An optional seventh or eighth candidate can be added later if the evals prove it creates uplift, but the pack should stay narrow.

## Measurement Model

Candidate skills must be defined by measured uplift, not by assumed blind spots.

The eval suite should follow the `ethskills-evals` pattern:

- run prompts with the skill loaded;
- run the same prompts against a bare baseline model;
- score with a separate judge;
- record pass, partial, fail, and uplift;
- use results to keep, revise, merge, or cut skills.

## Eval Mix

The first benchmark set should be a mix of:

- `short factual prompts` for unstable or easily hallucinated Vara/Sails facts;
- `realistic builder-task prompts` for architecture, codegen, testing, and workflow behavior.

The suite should be weighted toward `realistic builder tasks`, because the product goal is better Sails-building behavior, not just better recall.

## Execution Order

The first milestone should happen in this order:

1. bootstrap `vara-skills-evals`;
2. create a provisional `vara-skills` router plus candidate skill set;
3. run A/B evals on target models;
4. revise or cut candidate skills based on measured uplift;
5. freeze the first public pack;
6. publish the website later.

The milestone is not “ship a large skill library.” It is:

`stand up the eval harness and use it to discover the real first-wave Sails skills`

## Success Criteria

The first release is successful if:

- stock agents improve materially on the benchmark suite when the pack is loaded;
- the uplift is visible on at least two target model families;
- the resulting first-wave pack remains narrow and opinionated;
- the pack is portable across Codex, Claude, and OpenClaw.

## Assumptions

- The current `/Users/ukintvs/Documents/projects/gear-agent-skills` repo evolves into the `vara-skills` product repo, even if the directory name changes later.
- A sibling repo will be created for `vara-skills-evals`.
- Standard Gear/Vara Sails remains the only first-class builder path in v1.
- Website delivery is deferred until the first skill set is finalized and benchmarked.
