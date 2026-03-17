# Awesome Sails Token Patterns

This note captures the reusable default patterns for adding fungible-token functionality to a standard Gear/Vara Sails app with `awesome-sails`.

Code snippets in this note are schematic patterns meant to guide composition and API shape. Adapt types, imports, and storage wrappers to the target repo instead of copying them blindly.

It is intentionally general and production-biased:

- preserve the standard VFT surface unless the spec explicitly needs more
- choose the smallest `awesome-sails` token stack that satisfies the feature
- keep token state explicit and composable
- keep typed events and generated clients on the normal path
- separate token logic from orchestration when the product has bridge, payment, staking, or other async workflows

## Core Rule

Start from standard VFT-compatible behavior first.

On Vara, the VFT standard is the ERC-20 analogue. The default surface is:

- `Approve`
- `Transfer`
- `TransferFrom`
- `Allowance`
- `BalanceOf`
- `TotalSupply`
- `Name`
- `Symbol`
- `Decimals`

and the standard event surface is:

- `Approval`
- `Transfer`

Do not start from a custom fungible-token design unless the spec clearly cannot fit the standard VFT model.

## Choose The Smallest Awesome Sails Surface

`awesome-sails` is intentionally split into reusable token-related building blocks.

Use the smallest set that satisfies the feature:

- `vft`: standard fungible-token behavior
- `vft_metadata`: metadata access (`name`, `symbol`, `decimals`)
- `vft_admin`: privileged mint, burn, pause, and RBAC-secured admin operations
- `vft_extension`: allowance cleanup, `transfer_all`, enumeration, and shard-management helpers
- `vft_native_exchange`: native value <-> VFT conversion
- `vft_native_exchange_admin`: admin and recovery flows around native exchange
- `access_control`: explicit roles instead of ad hoc admin checks
- `storage`: reusable storage wrappers for service composition
- `msg_tracker`: async message/status tracking when token flows are message-driven

Default decision order:

1. Start with `vft`.
2. Add `vft_metadata` if the token is user-facing.
3. Add `vft_admin` only when mint, burn, pause, or maintenance operations are real requirements.
4. Add `vft_extension` only when cleanup, enumeration, `transfer_all`, or shard helpers are needed.
5. Add `vft_native_exchange` only when wrapping/unwrapping native value is part of the product.

## Dependency Pattern

Prefer explicit feature selection.

### Meta-crate pattern

```toml
[dependencies]
sails-rs = { version = "*", default-features = false, features = ["gstd"] }

awesome-sails = { version = "x.y.z", default-features = false, features = [
  "storage",
  "vft",
  "vft-metadata",
] }
```

Add more features only when the spec needs them.

### Direct subcrate pattern

Use direct crates when the project wants narrow imports or explicit dependency boundaries.

```toml
[dependencies]
sails-rs = { version = "*", default-features = false, features = ["gstd"] }

awesome-sails-storage = "x.y.z"
awesome-sails-vft-metadata = "x.y.z"
awesome-sails-utils = "x.y.z"
```
This style is valid when the app composes token functionality from helpers rather than depending on the full meta-crate surface.

## Storage Composition Pattern

The default reusable pattern is:

- keep balances, allowances, metadata, pause state, and admin/RBAC state in program-owned storage
- expose helper accessors that wrap those storages
- construct token-related services from wrappers instead of duplicating token logic across unrelated services

The following shape is schematic: `Balances`, `Allowances`, and `Metadata` represent app-defined storage types or wrappers chosen by the token implementation.

Minimal shape:

```rust
use sails_rs::{cell::RefCell, prelude::*};
use awesome_sails_storage::StorageRefCell;

pub struct Program {
    balances: RefCell<Balances>,
    allowances: RefCell<Allowances>,
    metadata: RefCell<Metadata>,
    pause: Pause,
}

pub struct TokenService<'a> {
    balances: &'a RefCell<Balances>,
    allowances: &'a RefCell<Allowances>,
    metadata: &'a RefCell<Metadata>,
    pause: &'a Pause,
}

impl<'a> TokenService<'a> {
    fn balances_ref(&self) -> StorageRefCell<'_, Balances> {
        StorageRefCell::new(self.balances)
    }

    fn allowances_ref(&self) -> StorageRefCell<'_, Allowances> {
        StorageRefCell::new(self.allowances)
    }
}
```

Why this pattern is the default:

- state ownership is explicit
- services stay composable
- wrappers can be reused by VFT, metadata, admin, and extension layers
- the code scales better than one monolithic token service with hidden state

## Metadata Pattern

Do not hand-roll metadata queries when the standard metadata service is enough.

Prefer delegating metadata through `awesome-sails-vft-metadata`:

```rust
use awesome_sails_vft_metadata::{Metadata, VftMetadata, VftMetadataExposure};
use awesome_sails_storage::StorageRefCell;

fn metadata_svc(&self) -> VftMetadataExposure<VftMetadata<StorageRefCell<'_, Metadata>>> {
    VftMetadata::new(StorageRefCell::new(self.metadata)).expose(self.route())
}

#[export]
pub fn name(&self) -> String {
    self.metadata_svc().name()
}

#[export]
pub fn symbol(&self) -> String {
    self.metadata_svc().symbol()
}

#[export]
pub fn decimals(&self) -> u8 {
    self.metadata_svc().decimals()
}
```

Default rule: if the token is user-facing, metadata should usually be present and exposed in the standard way.

## Event Pattern

Events are part of the token contract, not optional decoration.

Preserve the standard token events and add custom events only when the application has real domain facts beyond base token movement.

Minimal pattern:

```rust

#[event]
#[derive(Debug, Clone, Encode, Decode, TypeInfo, PartialEq, Eq)]
#[codec(crate = sails_rs::scale_codec)]
#[scale_info(crate = sails_rs::scale_info)]
pub enum Events {
    Approval { owner: ActorId, spender: ActorId, value: U256 },
    Transfer { from: ActorId, to: ActorId, value: U256 },

    // Add only when the chosen token policy needs them:
    Minted { to: ActorId, value: U256 },
    Burned { from: ActorId, value: U256 },
}

#[service(events = Events)]
impl TokenService<'_> {}
```

Default rules:

- keep `Approval` and `Transfer` when the service behaves like VFT
- add `Minted`, `Burned`, `Paused`, `RoleGranted`, or similar only when the feature set actually needs them
- emit events from successful state-changing paths, not from queries

## Exported Command Pattern

For stateful token commands, prefer `Result<_, Error>` plus `#[export(unwrap_result)]`.

Minimal pattern:

```rust
#[service(events = Events)]
impl TokenService<'_> {
    #[export(unwrap_result)]
    pub fn transfer(&mut self, to: ActorId, value: U256) -> Result<bool, Error> {
        let from = msg::source();

        // mutate balances here

        self.emit_event(Events::Transfer { from, to, value })
            .map_err(|_| EmitError)?;

        Ok(true)
    }

    #[export(unwrap_result)]
    pub fn approve(&mut self, spender: ActorId, value: U256) -> Result<bool, Error> {
        let owner = msg::source();

        // mutate allowances here

        self.emit_event(Events::Approval {
            owner,
            spender,
            value,
        })
        .map_err(|_| EmitError)?;

        Ok(true)
    }
}
```

Why this is the default:

- internal control flow stays typed and readable
- exported command failure remains fail-fast
- tests can explicitly expect fatal exported-path failures where appropriate

## Admin Pattern

Do not introduce privileged token operations unless the spec actually needs them.

When the token needs mint, burn, pause, or operational maintenance, prefer the dedicated admin layer rather than growing ad hoc privileged methods.

Use an app-local admin guard only for small, clearly bounded cases. Escalate to RBAC when:

- there are multiple privileged concerns
- roles differ by capability
- grant/revoke is part of the design
- long-term maintainability matters

Default rule:

- fixed-supply token: no admin layer unless there is another real privileged operation
- mutable-supply token: prefer `vft_admin` or an equivalent explicit RBAC design

## Extension Pattern

`vft_extension` is optional.

Use it when the product truly needs one or more of:

- expired allowance cleanup
- `transfer_all`
- balance enumeration
- allowance enumeration
- explicit shard management

Do not add extension helpers to every token by default.

A token that only needs standard transfers, approvals, balances, supply, and metadata should stay smaller.

## Native Exchange Pattern

`vft_native_exchange` is not a generic token default.

Use it only when the product explicitly requires:

- native value sent in -> VFT minted
- VFT burned -> native value returned

If the token does not wrap the chain’s native value, leave native exchange out.

## Separate Token Logic From Orchestration

When the token participates in a larger async protocol, prefer this split:

- a dedicated token program or token service that owns balances, allowances, supply, metadata, and token-standard events
- a separate manager/orchestrator that owns bridge, payment, staking, claim, or delayed-message workflows

This pattern is strongly reinforced by the Gear bridge architecture:

- VFT owns token logic
- VFT-Manager owns bridge workflow
- the user first performs approve
- the manager then performs the higher-level protocol action

Default rule: if another subsystem needs to move user tokens, start from approval-based ingress before inventing a custom authorization flow.

## Testing Defaults

A token integration is not complete until it covers the minimum matrix.

### Base VFT behavior

- transfer success
- transfer failure on insufficient balance
- approve success
- allowance correctness
- `transfer_from` success within allowance
- `transfer_from` failure above allowance
- total supply correctness
- metadata correctness when metadata is enabled

### Event behavior

- assert Approval
- assert Transfer
- assert custom events only when that feature exists

### Admin behavior

- authorized privileged action succeeds
- unauthorized privileged action fails
- mint/burn/pause flows are covered only when they exist

### Extension behavior

- cleanup, enumeration, transfer_all, and shard operations are tested only when enabled

### Fatal-path behavior

- for exported commands using #[export(unwrap_result)], assert fatal exported-path failures where appropriate

## Anti-Patterns

- writing a custom fungible token before checking whether standard VFT plus one or two awesome-sails layers are enough
- mixing token storage, protocol orchestration, and bridge/payment workflow into one giant service
- adding admin, extension, or native-exchange features “just in case”
- treating Approval / Transfer events as optional on a VFT-like token
- hiding supply policy instead of deciding explicitly between fixed supply, mint/burn, or lock/unlock semantics
- bypassing generated clients on the normal token path
- making every app invent its own allowance and transfer semantics ad hoc

## Practical Decision Order

When another agent has to choose quickly, bias toward this order:

- Preserve the standard VFT surface.
- Add metadata if the token is user-facing.
- Keep token state explicit and wrapper-based.
- Use typed events at the service boundary.
- Use `#[export(unwrap_result)]` for stateful exported token commands.
- Add admin only when privileged operations are real.
- Add extension only when cleanup, enumeration, `transfer_all`, or shard helpers are required.
- Add native exchange only when wrapping/unwrapping native value is part of the product.
- Split token logic from orchestration when the product has async protocol workflow.
- Test events and failure paths, not only final balances.
