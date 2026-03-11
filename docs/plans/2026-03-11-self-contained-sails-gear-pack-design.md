# Self-Contained Sails Gear Pack Design

## Goal
Turn this repository into a portable, self-contained skill pack that describes the standard Gear/Vara Sails program-development path without runtime dependence on sibling repos or personal skill directories.

## Product Constraint
- The repo must carry the builder-facing knowledge itself.
- Published skills must work when this repo is installed alone.
- Scope stays on standard Gear/Vara Sails program development, not Vara.eth-first or `ethexe`-specific work.

## Decision Summary
- Keep the existing Sails-builder catalog as the main public surface.
- Import useful Gear protocol, messaging, execution, and Sails workflow knowledge into local `references/`.
- Rewrite skills to point only at local skills, local references, and local scripts.
- Add one focused local skill for Gear message and execution reasoning if the existing catalog still leaves that path underspecified.

## Content Model

### Local Reference Handbook
Add compact local references for:

- Gear execution model
- Gear messaging and replies
- Gear gas, reservations, and waitlist behavior
- Sails program and service architecture
- Sails IDL and client generation pipeline
- Sails `gtest` and local-node validation

These references should absorb the useful material currently spread across `../gear-skills` and `~/.codex/skills`.

### Public Skill Surface
Keep the existing builder workflow skills:

- `ship-sails-app`
- `sails-new-app`
- `sails-feature-workflow`
- `sails-architecture`
- `sails-idl-client`
- `sails-gtest`
- `sails-local-smoke`

Add `gear-message-execution` if the current catalog still lacks a clear routing path for debugging or designing message flow, replies, delays, reservations, and timeout behavior.

## Skill Behavior Changes
- `ship-sails-app` becomes the local router into the repo handbook and narrower local skills.
- `sails-feature-workflow` bakes Gear execution and message-flow checkpoints into the default delivery path.
- `sails-architecture` absorbs local guidance for service boundaries, async state rules, delayed work, reservations, and waitlist constraints.
- `sails-idl-client` points to a local pipeline reference as the source of truth for `build.rs`, IDL generation, and generated clients.
- `sails-gtest` and `sails-local-smoke` absorb local `gtest`, generated-client, and typed smoke guidance instead of delegating outward.

## Portability Rules
- No published skill may require `../gear-skills`, `~/.codex/skills`, or another machine-specific source path.
- Skills may reference local repo paths only.
- Shared references carry the durable knowledge; skills should stay compact and route builders into those references at the right point.

## Validation Strategy
- Extend repository tests before changing published skill contracts.
- Add test expectations for new local references and any new skill directory.
- Keep `scripts/install-codex-skills.sh` and `make verify` working.
- Run full repo verification after content migration.

## Success Criteria
- The repo can be installed and used on another machine with no dependence on sibling repositories.
- A builder can discover Gear execution, messaging, Sails architecture, IDL/client, `gtest`, and local smoke knowledge from this repo alone.
- The public catalog remains coherent enough for later eval-driven trimming instead of exploding into an uncurated skill dump.
