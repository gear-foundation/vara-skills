# Sails IDL Client Pipeline

## Source Of Truth

- Treat the program `.idl` as the typed interface contract.
- Generated Rust and TypeScript clients should follow the `.idl`, not a hand-maintained parallel contract.
- If the program interface changed, refresh the `.idl` and generated clients before deeper debugging.

## `build.rs` Modes

### Template Workspace Pattern

- In 1.0.0-beta+, the root program crate's `build.rs` chains wasm build with IDL generation:
  ```rust
  fn main() {
      if let Some((_, wasm_path)) = sails_rs::build_wasm() {
          sails_rs::ClientBuilder::<app::Program>::from_wasm_path(
              wasm_path.with_extension(""),
          )
          .build_idl();
      }
  }
  ```
  In 0.10.x, the root build.rs uses standalone `sails_rs::build_wasm()`.
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
- In 1.0.0-beta+, `cargo sails client-js <idl_path> [out_path]` generates TypeScript client code directly from IDL.
- The `cargo sails idl` subcommand now supports `-n <program-name>` to set the program name in generated IDL.
- The usual output includes `lib.ts` and typed program or service classes.
- Pair the generated client with `GearApi` for node connectivity.
- Use `parseIdl` only when a dynamic runtime path is explicitly needed instead of pre-generated files.

## IDL V2 Format

In 1.0.0-beta+, the IDL uses V2 syntax. Key differences from V1:

- Version header: files start with `!@sails: 1.0.0-beta.2`
- Rust-like type names: `String` (not `str`), `Option<T>` (not `opt T`), `Result<T, E>` (not `result (T, E)`), `Vec<T>` (not `vec T`)
- Services have explicit blocks: `service Name@0x<interface_id> { events {} functions {} types {} extends {} }`
- Types are scoped inside service `types {}` blocks, not at file level
- `@query` annotation before functions instead of `query` keyword prefix
- `throws` keyword for error types: `Validate(v: u32) -> u32 throws ValidationError;`
- Program block: `program ProgramName { constructors {} services {} }`
- `@partial` and `@entry-id: N` annotations for subset client generation
- `!@include: path.idl` for file inclusion, `alias NewType = OldType;` for type aliases
- Generics are preserved in IDL (`GenericStruct<T>`) instead of monomorphized names

In 0.10.x, the IDL uses V1 syntax with `str`, `opt T`, `result (T, E)`, `query` keyword, and file-level type declarations.

## Pipeline Debugging Checklist

1. Check `build.rs` before adding an ad hoc generation command.
2. Confirm where the repo expects `.idl` output to land.
3. Confirm whether the crate is a program or a dedicated client crate before changing Cargo features.
4. Regenerate the Rust or TS client from the current `.idl`.
5. Verify tests and smoke flows use the generated client instead of hand-built payload encoders.
6. Keep generated artifacts deterministic and avoid unstable output locations.
