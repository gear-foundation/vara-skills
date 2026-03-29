# Sails RS Imports And Release Defaults

## Current Baseline

- Use `sails-rs 0.10.2` as the pack baseline unless the target repo already pins a different version.
- If the target repo uses `sails-rs 1.0.0-beta+`, follow its version. See the `sails-beta` branch of this pack for beta-specific patterns (ReflectHash, binary header protocol, IDL V2, edition 2024).
- Prefer teaching the current template defaults instead of older blog posts or copied snippets.

## Cargo Defaults

### App Or Wasm Crate

```toml
[dependencies]
sails-rs = "0.10.2"

[build-dependencies]
sails-rs = { version = "0.10.2", features = ["build"] }

[dev-dependencies]
sails-rs = { version = "0.10.2", features = ["gtest"] }
```

- Add `gclient` features or dependencies only when the crate also runs local-node smoke or off-chain integration tests. For deployment and CLI interaction without a Rust test harness, use `vara-wallet` instead.
- Do not add `sails-idl-gen` to the default app/wasm baseline unless the repo intentionally uses a more manual IDL pipeline.

### Dedicated Client Crate

```toml
[dependencies]
sails-rs = "0.10.2"

[build-dependencies]
sails-rs = { version = "0.10.2", features = ["build"] }
```

- In current official examples, dedicated Rust client crates commonly use sails-rs with features = ["build"].
- Reach for direct sails-client-gen / sails-idl-gen only when the repo intentionally uses a manual generation pipeline.

## Workspace Feature Conflict Warning

In `0.10.x`, `sails-rs` compiles `client/gstd_env.rs` even when only the `gtest` feature is enabled. That module references `::gstd` types. When Cargo feature unification enables both `gstd` and `gtest` on `sails-rs` in the same workspace, the build breaks.

On Rust 1.94+ the `dyn` trait object without the `dyn` keyword (`E0782`) is a hard error, triggering additional failures in `gstd_env.rs`.

Prevention:

- Use one workspace per program. Do not combine multiple programs and a shared test crate in a single top-level workspace.
- Always bootstrap with `cargo sails program <name>`, which generates the correct isolated layout.
- If you must share types across programs, extract them into a standalone `no_std` types crate with no `sails-rs` dependency.

## Canonical Workspace Layout

`cargo sails program <name>` generates:

```
<name>/
├── Cargo.toml          # resolver = "2", edition = "2021"
├── build.rs            # sails_rs::build_wasm()
├── src/
│   └── lib.rs          # wasm re-export + WASM_BINARY code module
├── app/
│   ├── Cargo.toml      # sails-rs (no features) — business logic, no_std
│   └── src/lib.rs
├── client/
│   ├── Cargo.toml      # sails-rs with features = ["build"]
│   ├── build.rs        # sails_rs::build_client::<Program>()
│   └── src/lib.rs
├── tests/
│   └── gtest.rs        # sails-rs with features = ["gtest"] in dev-dependencies
└── rust-toolchain.toml # channel = "stable", targets = ["wasm32-unknown-unknown"]
```

Key constraints:

- `resolver = "2"` and `edition = "2021"` are the current defaults.
- `gtest` and `gclient` belong in `[dev-dependencies]` only, never in `[dependencies]`. `gclient` is for Rust-native test harnesses; for deployment and on-chain interaction, `vara-wallet` is the primary tool.
- Each program is its own workspace root, not a member of a shared multi-program workspace.

## Common Imports

```rust
use sails_rs::{cell::RefCell, prelude::*};
use sails_rs::collections::BTreeMap;
use sails_rs::gstd::{exec, msg};
```

- Reach for `RefCell` when the program owns mutable state and services borrow it.
- Use `sails_rs::collections::*` when you want `no_std`-friendly collections through the framework path. Note that `sails_rs::collections::BTreeMap` is a `no_std` re-export and may lack some `std` methods. In particular, `drain()` is not available. Use `keys().cloned().collect::<Vec<_>>()` then iterate and remove as a workaround.
- Import `exec` and `msg` from `sails_rs::gstd` for standard Gear or Vara Sails programs. The `prelude::*` does not re-export `msg` or `exec`; guards like `msg::source()` and delayed-message helpers like `exec::program_id()` require the explicit import.
- `gstd::prog` (program creation via `create_program_bytes`) is not re-exported through `sails_rs::gstd`. If a Sails program needs to create child programs, add `gstd` as a direct dependency: `gstd = "1.10.0"`.

## Builder Defaults

- For the root program crate, the default `build.rs` calls:
  ```rust
  fn main() {
      sails_rs::build_wasm();
  }
  ```
  In 1.0.0-beta+ workspaces, the build.rs chains wasm build with IDL generation. See the `sails-beta` branch for that pattern.
- For a Rust client-generation crate, use `sails_rs::build_client::<Program>()` as the default shorthand.
- Use the Wasm path when the crate’s job is to build the on-chain artifact.
- Use the client path when the crate’s job is to generate a typed Rust client from a program interface.
- Reach for direct `sails-idl-gen` / `sails-client-gen` only when the repo intentionally requires a manual pipeline.
- If the repo needs custom client-generation control, prefer the official configurable builder path instead of dropping immediately to fully manual generators.

## Export And Event Rules

- Treat `#[export]` as mandatory for every service method that should be publicly callable.
- Public Rust methods without `#[export]` are implementation details, not remote Sails routes.
- `#[export(unwrap_result)]` allows internal use of `Result<T, E>` and `?` while exposing the unwrapped success path to clients.
- Use `self.emit_event(...)`, not `notify_on(...)`.

```rust
#[sails_rs::event]
#[derive(Encode, Decode, TypeInfo)]
#[codec(crate = sails_rs::scale_codec)]
#[scale_info(crate = sails_rs::scale_info)]
pub enum Event {
    Updated(u64),
}

#[service(events = Event)]
impl CounterService<'_> {
    #[export]
    pub fn add(&mut self, by: u64) {
        self.value += by;
        self.emit_event(Event::Updated(self.value))
            .expect("Event error");
    }
}
```

## SCALE Derive Boilerplate

Note: In 1.0.0-beta+, types also require `ReflectHash` derive, and messages use a 16-byte binary header protocol instead of string-based routing. See the `sails-beta` branch for those patterns.

- When shared DTOs or events derive SCALE traits in a `no_std` Sails crate, prefer:
  - `#[codec(crate = sails_rs::scale_codec)]`
  - `#[scale_info(crate = sails_rs::scale_info)]`
- This avoids proc-macro confusion when the crate does not depend on `parity-scale-codec` or `scale-info` directly.

## Agent Notes

- If the repo already pins a specific version, follow the repo version instead of forcing the pack baseline.
- Do not tell builders to hand-roll routes or event wiring when generated clients and `emit_event` already cover the standard path.
