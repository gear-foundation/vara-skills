# Gear/Sails Production Patterns

This note is a portable, production-biased companion to the narrower execution, architecture, IDL, and gtest references in this pack.

It is distilled from local research across official `sails` examples, reusable `awesome-sails` service patterns, and larger `dapps` codebases. The snippets below are intentionally inlined so another machine does not need those sibling repos.

Evidence weighting matters:

- Treat official `sails` patterns as the primary source for current framework defaults.
- Treat `awesome-sails` as strong evidence for reusable service and storage patterns.
- Treat `dapps` as real-world evidence, but some of those projects are older or outdated.
- Older `dapps` patterns should not override current Sails-first defaults just because they exist in production code.
- Do not copy older `dapps` code blindly; validate it against the current Sails routing, client-generation, and state-management guidance in this pack.

## Recommended Defaults

- Prefer program-owned state in `RefCell` fields and pass references into services.
- Keep `#[program]` thin: constructor/init, service exposure, and reply wiring only.
- Keep business rules, guards, and events inside `#[service]`.
- Prefer generated clients and IDL-backed routing over hand-built payload bytes.
- Treat stateful command failure as fatal: panic and let the current message revert.
- Use delayed self-messages and `ReservationId` only when future-block execution is part of the design.

## Awesome Sails As An External Dependency

`awesome-sails` is not just local reference material. It is organized as publishable crates that can be added to a Sails project from crates.io.

Use it when an agent should compose proven building blocks instead of reimplementing them:

- role-based access control
- reusable storage abstractions
- VFT and related admin/exchange services
- message-status tracking for async flows
- pause wrappers, checked math, compact integer wrappers, and sharded maps

For project dependencies, prefer explicit features instead of the meta-crate default:

```toml
[dependencies]
sails-rs = { version = "*", default-features = false, features = ["gstd"] }

# Meta-crate, but feature-selected on purpose.
awesome-sails = { version = "x.y.z", default-features = false, features = [
  "storage",
  "access-control",
  "vft",
  "vft-admin",
  "vft-extension",
  "vft-metadata",
  "vft-native-exchange",
  "vft-native-exchange-admin",
  "msg-tracker",
] }

# Separate utility crate when you want the low-level helpers directly.
awesome-sails-utils = "x.y.z"
```

Important packaging facts:

- the `awesome-sails` meta-crate defaults to `all`
- for agent-authored production code, prefer `default-features = false`
- the meta-crate exposes feature flags for `storage`, `access-control`, `vft`, `vft-utils`, `vft-admin`, `vft-extension`, `vft-metadata`, `vft-native-exchange`, `vft-native-exchange-admin`, and `msg-tracker`
- the meta-crate also has a `test` feature that forwards to `awesome-sails-vft-utils/test`
- `awesome-sails-utils` is a separate crate, not a feature of the meta-crate

### Feature/Crate Chooser

- `storage` / `awesome-sails-storage`: choose this when a service should be generic over storage backends. It provides `Storage`, `StorageMut`, `InfallibleStorage`, `InfallibleStorageMut`, and `StorageRefCell`.
- `access-control` / `awesome-sails-access-control`: choose this when privileged operations outgrow a single-admin check. It provides `AccessControl`, `RolesStorage`, role hierarchy support, enumeration, and batch grant/revoke flows.
- `vft-utils` / `awesome-sails-vft-utils`: choose this when you need the underlying token storage/value types. It provides `Allowances`, `Balances`, compact `Allowance` and `Balance` wrappers, shard-aware storage helpers, and related errors.
- `vft` / `awesome-sails-vft`: choose this for a standard VFT service with transfers, approvals, allowance handling, and balance/total-supply queries.
- `vft-admin` / `awesome-sails-vft-admin`: choose this when the token needs privileged mint, burn, pause, and admin-managed maintenance operations.
- `vft-extension` / `awesome-sails-vft-extension`: choose this when the token needs `transfer_all`, expired-allowance cleanup, balance/allowance enumeration, or explicit shard-management helpers.
- `vft-metadata` / `awesome-sails-vft-metadata`: choose this when the token should expose metadata like name, symbol, and decimals.
- `vft-native-exchange` / `awesome-sails-vft-native-exchange`: choose this when native value should mint VFT and burning VFT should return native value.
- `vft-native-exchange-admin` / `awesome-sails-vft-native-exchange-admin`: choose this when the exchange flow needs admin recovery, `burn_from`, or failed-value-transfer handling via `handle_reply`.
- `msg-tracker` / `awesome-sails-msg-tracker`: choose this for async orchestration, saga-style flows, or any path that needs per-`MessageId` status tracking. It provides `MsgTracker`, `Pagination`, `MessageStorage`, `BTreeMap` support, and `FixedStorage` for bounded-capacity tracking.

### Separate Utility Crate Chooser

`awesome-sails-utils` is the low-level helper crate. Reach for it when the project needs reusable primitives rather than a whole service.

- `error`: shared error types such as a generic `Error`, `BadInput`, `BadOrigin`, `BadValue`, and `EmitError`.
- `map`: a sharded-map implementation for controlled-capacity storage layouts.
- `math`: `CheckedMath`, compact `LeBytes<N>` integers, `NonZero<T>`, and the common numeric re-exports used across the token crates.
- `pause`: `Pause`, `PausableRef`, `PausableStorage`, and pause-related errors for emergency-stop style guards.
- `macros`: shared helper macros used by the ecosystem.

If an agent only needs `CheckedMath`, `LeBytes`, `NonZero`, `PausableRef`, or a sharded map, depend on `awesome-sails-utils` directly instead of pulling in the full service stack.

## 1. Program-Owned State Is The Default

This is the cleanest default for standard Gear/Sails programs. The program owns lifetime and storage; the service owns behavior.

```rust
use sails_rs::{cell::RefCell, prelude::*};

pub struct CounterData {
    value: u32,
}

pub struct Program {
    counter: RefCell<CounterData>,
}

pub struct CounterService<'a> {
    counter: &'a RefCell<CounterData>,
}

impl<'a> CounterService<'a> {
    pub fn new(counter: &'a RefCell<CounterData>) -> Self {
        Self { counter }
    }
}

#[service]
impl CounterService<'_> {
    #[export]
    pub fn add(&mut self, by: u32) -> u32 {
        let mut data = self.counter.borrow_mut();
        data.value += by;
        data.value
    }
}

#[program]
impl Program {
    pub fn new() -> Self {
        Self {
            counter: RefCell::new(CounterData { value: 0 }),
        }
    }

    pub fn counter(&self) -> CounterService<'_> {
        CounterService::new(&self.counter)
    }
}
```

Why this is the default:

- state ownership is explicit at the program boundary
- constructor/setup is deterministic
- tests can inject or reset state cleanly
- services stay reusable and mostly stateless

## 2. Wrap Storage When Reusable Services Need It

`awesome-sails` shows a stronger reusable pattern: accept storage abstractions instead of hard-coding raw `RefCell` everywhere.

```rust
use awesome_sails_storage::StorageRefCell;
use awesome_sails_utils::pause::{PausableRef, Pause};
use sails_rs::{cell::RefCell, prelude::*};

pub struct Program {
    pause: Pause,
    balances: RefCell<Balances>,
}

impl Program {
    pub fn balances(&self) -> PausableRef<'_, Balances> {
        PausableRef::new(&self.pause, StorageRefCell::new(&self.balances))
    }

    pub fn token(&self) -> TokenService<'_> {
        TokenService::new(self.balances())
    }
}
```

Use `StorageRefCell`, `PausableRef`, or similar wrappers when:

- the same business service should work with different storage backends
- you need guards around every mutation path
- reusable domain modules should be portable across programs

Production implication: expose helper methods like `balances()` or `access_control_storage()` on the program and construct the service from those helpers instead of borrowing raw fields everywhere.

## 3. Static Hidden State Is Allowed, But Not The Default

Some real apps use static hidden state to keep a service self-contained. This is valid, but it has sharper edges than program-owned state.

```rust
#![allow(static_mut_refs)]

use sails_rs::prelude::*;

static mut STORAGE: Option<MyStorage> = None;

#[derive(Default)]
struct MyStorage {
    next_id: u64,
}

pub struct MyService;

impl MyService {
    pub fn seed() {
        unsafe {
            STORAGE = Some(MyStorage::default());
        }
    }

    fn storage_mut(&mut self) -> &'static mut MyStorage {
        unsafe { STORAGE.as_mut().expect("MyService::seed() should be called") }
    }
}

#[program]
impl Program {
    pub fn new() -> Self {
        MyService::seed();
        Self
    }
}
```

If you choose static hidden state:

- the service must have an explicit `seed()` or `init()` path before first use
- the program constructor must call that setup exactly once
- tests must re-seed or isolate initialization
- helper accessors should fail loudly if initialization was skipped

Costs:

- weaker test isolation
- more hidden coupling between constructor flow and service behavior
- easier async stale-state bugs
- harder refactors when multiple services need shared storage visibility

Use static hidden state only when the self-contained boundary is materially better than explicit program-owned state.

## 4. Hybrid State Is Common In Larger Apps

A practical production split is:

- program-owned `RefCell<SessionStorage>` or other cross-cutting identity/session state
- static hidden state for one dominant domain service

That hybrid model is acceptable when:

- one subsystem like session/signless routing needs explicit shared ownership
- the main game/service state is intentionally encapsulated behind one service

Guardrail: name the split explicitly in design docs. Hybrid state that is not documented becomes accidental architecture.

## 5. Keep `#[program]` Thin

The stable boundary is:

- `#[program]`: constructors, service exposure, reply wiring
- `#[service]`: commands, queries, guards, events, domain logic

```rust
#[program]
impl Program {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn handle_reply(&mut self) {
        self.exchange_admin().handle_reply();
    }

    pub fn exchange_admin(&self) -> ExchangeAdmin<'_> {
        ExchangeAdmin::new(self.access_control(), self.balances())
    }
}
```

If a `#[program]` method starts making domain decisions beyond setup and exposure, the boundary is already drifting.

## 6. Use Shallow `extends` Composition

Composition is good. Inheritance-like complexity is not.

```rust
pub struct DogService {
    mammal: MammalService,
    walker: WalkerService,
}

impl From<DogService> for (MammalService, WalkerService) {
    fn from(value: DogService) -> Self {
        (value.mammal, value.walker)
    }
}

#[service(extends = [MammalService, WalkerService], events = DogEvents)]
impl DogService {
    #[export]
    pub fn make_sound(&mut self) -> &'static str {
        self.emit_event(DogEvents::Barked).unwrap();
        "Woof! Woof!"
    }
}
```

Use `extends` when:

- the inherited API is part of the intended public contract
- route and event interactions stay understandable
- the service can clearly convert into the extended services

Do not use `extends` to hide a messy architecture. Keep it shallow and intentional.

## 7. Put Guards Near The Service Boundary

The stronger patterns keep access control, pause checks, and session validation close to exported methods.

```rust
#[service]
impl AdminService<'_> {
    #[export]
    pub fn add_admin(&mut self, admin: ActorId) {
        self.ensure_is_admin();
        self.storage_mut().admins.insert(admin);
    }

    fn ensure_is_admin(&self) {
        assert!(self.storage().admins.contains(&msg::source()), "Not admin");
    }
}
```

Production defaults:

- grant bootstrap roles in constructor/init
- keep one guard helper per privileged concern
- fail before mutating state
- prefer reusable guard wrappers over repeated inline checks when the same rule protects multiple mutation paths

## 8. Async Rules: Re-Read State After `.await`

Any shared mutable state read before `.await` may be stale after resume.

```rust
#[service]
impl ResourceService<'_> {
    #[export]
    pub async fn attach_part(&mut self, id: u32, part_id: u32) -> Result<(), Error> {
        self.ensure_is_admin()?;

        let base = self.storage().resources.get(&id).ok_or(Error::Missing)?.base;

        let part = self
            .catalog_client
            .part(part_id)
            .with_destination(base)
            .await
            .unwrap();

        if part.is_none() {
            return Err(Error::MissingPart);
        }

        let resource = self.storage_mut().resources.get_mut(&id).ok_or(Error::Missing)?;
        resource.parts.push(part_id);
        Ok(())
    }
}
```

Production rules:

- do not hold mutable-borrow assumptions across `.await`
- after `.await`, re-read or revalidate shared state before mutating it
- if a command cannot tolerate drift, redesign it into smaller messages or stricter validation steps

## 9. Use Fail-Fast Command Semantics

Across `sails`, `awesome-sails`, and `dapps`, the safer production stance is fail-fast for stateful commands.

```rust
pub fn panicking<T, E: core::fmt::Debug, F: FnOnce() -> Result<T, E>>(f: F) -> T {
    match f() {
        Ok(v) => v,
        Err(e) => panic!("{e:?}"),
    }
}

#[service]
impl BattleService<'_> {
    #[export]
    pub fn cancel_tournament(&mut self) {
        let event = panicking(|| self.cancel_tournament_impl());
        self.emit_event(event).expect("Notification Error");
    }
}
```

Recommended practice:

- separate transport failure, timeout, and error reply
- panic on stateful command failure unless the spec explicitly models compensation
- expect `UserspacePanic` in tests for fatal command-path failures

For reply-driven flows:

- use generated clients when available
- configure `reply_deposit` when the flow depends on reply hooks or awaited replies
- treat low-level byte payloads as a diagnostic path, not the normal Sails route

## 10. Generated Clients First, Raw Bytes Only As Escape Hatch

The stable default is IDL plus generated clients.

```rust
// build.rs
fn main() {
    sails_rs::ClientBuilder::<demo::DemoProgram>::from_env()
        .build_idl()
        .with_mocks("with_mocks")
        .generate()
        .unwrap();
}
```

```rust
let reply = DemoProgram::client(program_id)
    .counter()
    .add(10)
    .with_reply_deposit(10_000_000_000)
    .await
    .unwrap();
```

Use generated clients by default because they preserve:

- route-prefix correctness
- reply decoding
- test mocks
- consistency between Rust and TS consumers

Hand-roll raw bytes only at low-level integration boundaries or when isolating codec/routing bugs.

## 11. Delayed Work And `ReservationId` Need Explicit Design

Delayed self-messages and reservations are for genuinely future-block workflows, not for vague “maybe later” logic.

```rust
fn send_timeout_from_reservation(
    reservation_id: ReservationId,
    player_id: ActorId,
    delay: u32,
) {
    let request = [
        "Battle".encode(),
        "AutomaticMove".to_string().encode(),
        player_id.encode(),
    ]
    .concat();

    msg::send_bytes_delayed_from_reservation(
        reservation_id,
        exec::program_id(),
        request,
        0,
        delay,
    )
    .expect("Error in sending message");
}
```

```rust
fn send_cleanup(player: ActorId, gas: u64, delay: u32) {
    let payload = [
        "Game".encode(),
        "RemoveInstance".encode(),
        player.encode(),
    ]
    .concat();

    msg::send_bytes_with_gas_delayed(exec::program_id(), payload, gas, 0, delay)
        .expect("Error in sending message");
}
```

Production rules:

- use delayed self-messages for scheduled in-protocol work, not off-chain cron assumptions
- persist enough state to make the delayed handler idempotent or safely repeatable
- use `ReservationId` only when later execution budget must survive across executions
- unreserve or remove reservations when the lifecycle ends
- derive gas budgets from explicit config and `exec::gas_available()`, not hard-coded hope

If delayed work is essential, the architecture should name:

- who sends the follow-up
- which route receives it
- which gas source pays for it
- how stale or duplicate messages are handled

## 12. Test Like Production, Not Like A Synchronous Call Stack

Use `GtestEnv` modes intentionally.

```rust
use sails_rs::client::{BlockRunMode, GtestEnv};

let env = GtestEnv::new(system, ACTOR_ID.into()).with_block_run_mode(BlockRunMode::Next);
let reply = program.counter().add(10).send_for_reply().unwrap();

env.run_next_block();
let value = reply.await.unwrap();
```

Why `BlockRunMode` matters:

- `Auto` is convenient for simple one-step calls
- `Next` exposes whether the reply actually lands in the expected next block
- `Manual` is right when the test must drive multi-block behavior explicitly

Also prefer:

- unit-level service tests when state can be injected through `RefCell` or wrappers
- assertions on events and reply errors, not only local state
- explicit expectations for `UserspacePanic` on fatal command paths

## Practical Defaults For Agents

When another agent has to choose quickly, bias toward this order:

1. Program-owned state plus thin service wrappers.
2. `StorageRefCell` or `PausableRef` when reusable storage-aware services are justified.
3. Generated clients plus `build.rs` IDL/client generation.
4. Fail-fast command handlers that test for `UserspacePanic`.
5. Delayed self-messages only when the feature is genuinely block-shaped.
6. `ReservationId` only when a later execution budget must be preserved.
7. Static hidden state only with explicit `seed()` or `init()` discipline.

## Anti-Patterns

- fat `#[program]` methods that own domain logic
- static hidden state without `seed()` or `init()` discipline
- mixing generated clients with ad hoc raw payloads on the same normal path
- mutating shared state before `.await` and assuming it is still authoritative afterward
- delayed work without explicit gas-budget and replay/idempotency thinking
- deep `extends` graphs that obscure the public contract
- soft-error command handlers that leave partially-updated state alive
