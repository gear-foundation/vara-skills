# Sails Cheatsheet

## Program Shape
- `#[program]` owns constructors and exposes services.
- `#[service]` owns business logic and exported commands or queries.
- One application has one `#[program]`, but it may expose multiple services.

## Export Rules
- `&mut self` exports are commands and may mutate state.
- `&self` exports are queries and should be read-only.
- `#[export(route = "...")]` is the stable routing contract for services or methods.
- `CommandReply<T>` is the value-returning command path.

## IDL And Clients
- Sails generates IDL from Rust types at build time.
- Generated clients are the default typed integration surface for Rust and TypeScript.
- Architecture decisions must keep exported DTO names distinct from service names.
- Events are part of the public interface and should map to meaningful state transitions.

## Skill Implications
- Specs should talk in terms of service routes, commands, queries, and events.
- Architecture plans should keep `#[program]` thin and push logic into services.
- Implementation guidance should prefer Sails-first patterns over raw payload handling.

## See Also
- `references/sails-program-and-service-architecture.md`
- `references/sails-idl-client-pipeline.md`
