# Vara Core Skills Design

## Goal
Create a Gear/Vara-first starter pack that wraps the strongest existing specialist skills with a smaller orchestration layer.

## Decisions
- Five first-wave skills: `idea-to-spec`, `gear-architecture-planner`, `task-decomposer`, `sails-rust-implementer`, `gtest-tdd-loop`.
- Persist workflow artifacts in `docs/plans/` inside consumer repositories.
- Use local shared references as the primary agent-facing knowledge layer.
- Keep Vara.eth as an extension note in the first release, not a default path.

## Validation
- Repository-level tests enforce layout and skill metadata.
- Acceptance validation runs against the Sails `redirect` example.
