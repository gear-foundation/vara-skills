# Sails RS Imports And Release Defaults

## Current Baseline

- Use `sails-rs 0.10.2` as the pack baseline unless the target repo already pins a newer compatible patch.
- Prefer teaching the current template defaults from that release instead of older blog posts or copied snippets.

## Cargo Defaults

### App Or Wasm Crate

```toml
[dependencies]
sails-rs = "0.10.2"

[build-dependencies]
sails-rs = { version = "0.10.2", features = ["wasm-builder"] }

[dev-dependencies]
sails-rs = { version = "0.10.2", features = ["gtest"] }
```

- Add `gclient` features or dependencies only when the crate also runs local-node smoke or off-chain integration tests.
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

## Common Imports

```rust
use sails_rs::{cell::RefCell, prelude::*};
use sails_rs::collections::BTreeMap;
use sails_rs::gstd::{exec, msg};
```

- Reach for `RefCell` when the program owns mutable state and services borrow it.
- Use `sails_rs::collections::*` when you want `no_std`-friendly collections through the framework path.
- Import `exec` and `msg` from `sails_rs::gstd` for standard Gear or Vara Sails programs.

## Builder Defaults

- For an app / wasm crate, the default `build.rs` path is `sails_rs::build_wasm()`.
- For a Rust client-generation crate, use `sails_rs::build_client::<Program>()` as the default shorthand.
- Use the Wasm path when the crate’s job is to build the on-chain artifact.
- Use the client path when the crate’s job is to generate a typed Rust client from a program interface.
- Reach for direct `sails-idl-gen` / `sails-client-gen` only when the repo intentionally requires a manual pipeline.
- If the repo needs custom client-generation control, prefer the official configurable builder path instead of dropping immediately to fully manual generators.

## Export And Event Rules

- In `0.10.2`, treat `#[export]` as mandatory for every service method that should be publicly callable.
- Public Rust methods without `#[export]` are implementation details, not remote Sails routes.
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

- When shared DTOs or events derive SCALE traits in a `no_std` Sails crate, prefer:
  - `#[codec(crate = sails_rs::scale_codec)]`
  - `#[scale_info(crate = sails_rs::scale_info)]`
- This avoids proc-macro confusion when the crate does not depend on `parity-scale-codec` or `scale-info` directly.

## Agent Notes

- If the repo already pins a newer compatible patch, follow the repo version instead of forcing `0.10.2`.
- Do not tell builders to hand-roll routes or event wiring when generated clients and `emit_event` already cover the standard path.
