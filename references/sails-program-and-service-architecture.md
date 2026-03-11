# Sails Program And Service Architecture

## Baseline Structure

- `#[program]` should stay thin: constructors, wiring, and service exposure only.
- `#[service]` should own business logic, stateful commands, read-only queries, and events.
- One application has one `#[program]`, but it may expose multiple services by business boundary.

## State Ownership Patterns

- Program-owned state is the preferred default because ownership is explicit and test setup is simpler.
- Hidden static service state is acceptable only when deterministic seeding and test isolation are controlled.
- Use shallow `extends` composition when it improves reuse; do not build a maze of inherited service surfaces.

## Routes And Public Contract

- Treat exported service and method routes as a compatibility surface.
- Use explicit route policy when compatibility matters across refactors.
- Keep exported DTO names distinct from service names so generated clients stay readable.
- Events should represent externally meaningful state transitions, not every internal branch.

## Async And Failure Rules

- Any state read before `await` may be stale after resume.
- Revalidate or re-read shared mutable state after `await` before mutating it.
- In stateful command paths, treat transport failure and error reply as fatal unless the design explicitly models compensation.
- Panic is a valid transaction boundary for one message: state, replies, and events from that execution roll back together.

## Recommended Defaults

- Use program-owned state plus service wrappers.
- Keep access-control checks centralized in service-local guard helpers.
- Emit events close to the successful state transition they describe.
- Prefer fail-fast command semantics over soft-error partial commits.

## Common Anti-Patterns

- Fat `#[program]` methods with domain logic
- Mixed route policy with no stability intent
- Static state without deterministic seeding
- Async stale-state bugs after `await`
- Mutate-before-send logic that ignores rollback on failure
