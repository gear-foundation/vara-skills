# Vara Domain Overview

## Core Model
- Gear/Vara programs are isolated actors with private state.
- State changes happen only while handling a message.
- Messages are asynchronous; ordering is preserved between a given pair of actors.
- The network maintains a global message queue and routes messages during block construction.

## What A Skill Should Assume
- Programs never share memory.
- Program code is immutable Wasm plus persistent memory.
- Async design is normal, not an edge case.
- Cross-program work is a distributed transaction problem, not a single atomic call.

## Reliability Patterns
- Prefer explicit message flows, reply handling, and event emission.
- For multi-step workflows, model failures up front with idempotency, retries, and compensation.
- Use delayed messages and gas reservation only when the design truly needs deferred recovery.
- Treat actor boundaries and execution ordering as architecture constraints, not implementation details.

## First-Wave Skill Guidance
- Specs should name actors, messages, replies, events, invariants, and recovery paths.
- Architecture notes should explain ownership, message flow, and off-chain observation points.
- Implementation skills should default to Gear/Vara semantics before considering Vara.eth extensions.
