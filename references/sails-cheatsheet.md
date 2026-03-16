# Sails Cheatsheet

## Release Baseline

- Treat `sails-rs 0.10.2` as the current standard baseline for this pack.
- In that baseline, public service methods must be marked with `#[export]` to become Sails routes.
- Event enums should use `#[sails_rs::event]`.
- Event emission should use `emit_event`, not older renamed patterns.

## Program Shape
- `#[program]` owns constructors that return `Self` and exposes services.
- `#[service]` owns business logic and exported commands or queries.
- One application has one `#[program]`, but it may expose multiple services.

## Export Rules
- In `0.10.2`, treat `#[export]` as required for every publicly callable service method.
- `&mut self` exports are commands and may mutate state.
- `&self` exports are queries and should be read-only.
- `#[export(route = "...")]` is the stable routing contract for services or methods; by default, exposed service and method names are converted to PascalCase.
- `CommandReply<T>` is the value-returning command path.
- Service events should be emitted with `self.emit_event(...)`.

## Event Rules
- In the `0.10.2` baseline, declare event enums with `#[sails_rs::event]`.
- Attach the event enum to the service with `#[service(events = Events)]`.
- Emit service events through `self.emit_event(...)`.
- Treat events as part of the public contract: name them after meaningful state transitions, not internal implementation steps.
- Events are only published if the emitting command completes successfully.
- Outgoing event payloads follow the Sails route-framed layout: service name, event name, then event data.

## Program-Level Payable
- Use `#[program(payable)]` if the program must accept value on an empty payload without routing to a service.

## Advanced Export Helpers
- `#[export(unwrap_result)]` allows internal use of `Result<T, E>` and `?` while exposing the unwrapped success path to clients.


## IDL And Clients
- Sails generates IDL from Rust types at build time.
- Generated clients are the default typed integration surface for Rust and TypeScript.
- Generated clients encode the correct route-prefixed payloads for constructor and service calls.
- Architecture decisions must keep exported DTO names distinct from service names.
- Events are part of the public interface and should map to meaningful state transitions.

## Skill Implications
- Specs should talk in terms of program constructors, service routes, commands, queries, and events.
- Specs should name the chosen state ownership pattern instead of leaving storage implicit.
- Architecture plans should keep `#[program]` thin and push logic into services.
- Implementation guidance should prefer generated clients or other Sails route-prefixed encoding over raw payload handling.

## See Also
- `references/sails-rs-imports.md`
- `references/sails-program-and-service-architecture.md`
- `references/sails-idl-client-pipeline.md`
