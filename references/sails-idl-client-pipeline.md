# Sails IDL Client Pipeline

## Source Of Truth

- Treat the program `.idl` as the typed interface contract.
- Generated Rust and TypeScript clients should follow the `.idl`, not a hand-maintained parallel contract.
- If the program interface changed, refresh the `.idl` and generated clients before deeper debugging.

## `build.rs` Modes

### Template Workspace Pattern

- A standard Sails workspace may generate Wasm, `.idl`, and Rust client artifacts through build scripts.
- For dedicated Rust client crates, the normal path is:
  - `[build-dependencies] sails-rs = { version = "...", features = ["build"] }`
  - `fn main() { sails_rs::build_client::<Program>(); }`
- If the repo needs custom generation controls, use:
  - `sails_rs::ClientBuilder::<Program>::from_env().build_idl().generate()`
- Use direct `sails_idl_gen::generate_idl_to_file::<Program>(...)` plus
  `ClientGenerator::from_idl_path(...).generate_to(...)` only for explicitly manual or non-standard pipelines.

### Shorthand Builder

- `sails_rs::build_client::<Program>()`

Use this when default paths and workspace layout are conventional.

### Configurable Builder

- `ClientBuilder::<Program>::from_env().build_idl().generate()`

Use this when the repo needs controlled output paths or additional generation settings.

### Manual Generation (Non-default)

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
3. Confirm whether the crate is a program or a dedicated client crate before changing Cargo features.
4. Regenerate the Rust or TS client from the current `.idl`.
5. Verify tests and smoke flows use the generated client instead of hand-built payload encoders.
6. Keep generated artifacts deterministic and avoid unstable output locations.
