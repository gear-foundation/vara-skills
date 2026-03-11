# Sails IDL Client Pipeline

## Source Of Truth

- Treat the program `.idl` as the typed interface contract.
- Generated Rust and TypeScript clients should follow the `.idl`, not a hand-maintained parallel contract.
- If the program interface changed, refresh the `.idl` and generated clients before deeper debugging.

## `build.rs` Modes

### Template Workspace Pattern

- A program or root crate builds the Wasm artifact.
- `cargo build` commonly produces `.opt.wasm` and may also refresh `.idl` output.
- Client generation may happen in the same crate or in a dedicated client crate.

### Shorthand Builder

- `sails_rs::build_client::<Program>()`

Use this when default paths and workspace layout are conventional.

### Configurable Builder

- `ClientBuilder::<Program>::from_env().build_idl().generate()`

Use this when the repo needs controlled output paths or additional generation settings.

### Manual Generation

- `sails_idl_gen::generate_idl_to_file::<Program>(...)`
- `ClientGenerator::from_idl_path(...).generate_to(...)`

Use this only when the repo layout or artifact wiring is genuinely non-standard.

## JavaScript And TypeScript Path

- Use `sails-js` or `sails-js-cli` for the normal JS or TS client flow.
- The usual output includes `lib.ts` and typed program or service classes.
- Pair the generated client with `GearApi` for node connectivity.
- Use `parseIdl` only when a dynamic runtime path is explicitly needed instead of pre-generated files.

## Pipeline Debugging Checklist

1. Check `build.rs` before adding an ad hoc generation command.
2. Confirm where the repo expects `.idl` output to land.
3. Regenerate the Rust or TS client from the current `.idl`.
4. Verify tests and smoke flows use the generated client instead of hand-built payload encoders.
5. Keep generated artifacts deterministic and avoid unstable output locations.
