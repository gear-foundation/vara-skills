# Program Evolution And State Migration For Gear/Sails

## Goal

- Use this reference when the user asks how to evolve a Gear/Sails smart contract after deployment, how to release a new version safely, or how to migrate on-chain state from an old program to a new one without breaking frontend and indexer integrations.
- Frame the answer as a production maintenance problem, not only as a coding problem.
- Separate what the platform provides out of the box from what the project should implement as its own migration discipline.
- This reference focuses on released-contract evolution, cutover discipline, and state migration between program versions.
- It does not try to fully specify frontend rollout mechanics or indexer implementation details.

## Core Model

- For Gear/Vara, treat upgradeability as deploying a new program version and explicitly migrating state, not as hot-swapping code inside one live program.
- Build recommendations around a `V1 -> V2 -> cutover` model.
- Treat deployment, state reading, migration batching, and cutover as separate concerns.
- Keep the public contract surface stable for as long as possible.
- When internal Rust names change but public names must stay stable, preserve routes with `#[export(route = "...")]`.
- When extending services, use `overrides`, `route`, or `entry_id` deliberately so inherited methods keep compatibility intent explicit.
- Prefer program-owned business state passed into services via `RefCell`; this keeps ownership explicit and makes versioned state and migration planning easier.

## What Counts As Upgrade

- An upgrade is a release process with three parts:
  - old contract `V1`
  - new contract `V2`
  - off-chain migrator script
- `V1` is the source of truth for export.
- `V2` is deployed separately and is the destination for import.
- The off-chain migrator reads old state and writes new state.
- Read state through the platform primitives when possible:
  - `api.programState.read` for full-state reads or reads at a fixed block hash
  - `api.programState.readUsingWasm` for selected state functions or custom paginated reads

## What The Agent Must Recommend

- Always recommend a migration flow built on these rules:
  - freeze writes on `V1`
  - export state in deterministic chunks
  - import state into `V2` in deterministic chunks
  - make imports idempotent
  - verify counts, totals, and critical invariants
  - activate `V2`
  - switch frontend and indexer to `V2`
- Treat migration batches like any other retryable multi-step flow.
- Expect retries, partial completion, `Timeout`, and `RunOutOfGas`.
- Prefer tracked progress plus retry-safe behavior over one-shot bulk migration logic.

## Minimal Status Model

- Do not require a separate `Migration` status unless the user explicitly wants it.
- The default recommendation is:
  - `Active`
  - `ReadOnly`
- `ReadOnly` means user mutating calls are blocked but queries and export functions remain available.
- This is usually enough for the old version because migration itself is an explicit export/import process and state reading is already handled separately by Vara APIs.

## What Must Exist In The Old Contract `V1`

- `V1` should contain:
  - admin-only `set_read_only(bool)`
  - export methods for each business-relevant part of state
  - a stats or invariants export method for validation
  - no new writes once migration starts
- Prefer export APIs by business domain, not one giant dump.
- Good shapes include:
  - `export_config()`
  - `export_users_chunk(cursor, limit)`
  - `export_positions_chunk(cursor, limit)`
  - `export_balances_chunk(cursor, limit)`
  - `export_active_accounts_chunk(cursor, limit)`
  - `export_stats()`
- Use `api.programState.read` when full-state reading is feasible.
- Use `api.programState.readUsingWasm` when only selected parts should be read or when large state should be paginated through custom state functions.

## What Must Exist In The New Contract `V2`

- `V2` should contain:
  - initial `ReadOnly` mode until import is complete
  - admin-only import methods
  - batch progress tracking
  - idempotency checks
  - conflict detection
  - finalization step
- Good shapes include:
  - `import_config(...)`
  - `import_users_batch(batch_id, users)`
  - `import_positions_batch(batch_id, positions)`
  - `import_balances_batch(batch_id, balances)`
  - `import_active_accounts_batch(batch_id, accounts)`
  - `import_status()`
  - `finalize_import()`
- If the same `batch_id` is sent twice, prefer success without duplicating state changes.
- If the same key or entity arrives with different data, fail with a conflict instead of silently overwriting.
- Keep normal business writes blocked until import verification passes and finalization is complete.

## State Inventory Rules

- Before proposing migration, require a state inventory.
- For every field in the root program state and in nested structures, classify it as one of:
  - migrate as-is
  - migrate with transform
  - rebuild after migration
- Make the user list every business-significant collection explicitly.
- This includes:
  - `Vec`
  - `HashMap`
  - `HashSet`
  - nested combinations of them
- Do not assume caches, derived indexes, or recomputable aggregates need migration.
- Rebuild derived or cache-like data when it is safe and cheaper than migrating it.
- Keep the source of truth small and explicit.

## How To Migrate `Vec`

- Treat `Vec<T>` as an ordered sequence.
- Export by index range using:
  - `cursor`
  - `limit`
  - `next_cursor`
- Recommend chunked export/import by slices.
- This is the simplest collection to migrate because ordering is already defined.

## How To Migrate `HashMap`

- Never recommend migrating a `HashMap` by raw iteration order.
- Migrate it as a deterministic sequence of entries, for example `Vec<(K, V)>`.
- Required rule:
  - collect keys
  - sort keys into a canonical order
  - take a key range by cursor and limit
  - export entries for those keys
  - import entries into `V2`
- If repeated key sorting would be too expensive, recommend one of these improvements:
  - maintain a stable secondary index
  - use `BTreeMap` for the new version
  - flatten nested maps into explicit migration records
- For nested structures like `HashMap<UserId, HashMap<OrderId, Order>>`, flatten export into records such as `(user_id, order_id, order)` instead of trying to migrate one giant nested object.
- Flattening keeps batching, retries, and conflict checks tractable.

## How To Migrate `HashSet`

- Treat `HashSet<T>` like a set of records, not a raw memory object.
- Required rule:
  - collect elements
  - sort elements into canonical order
  - export by cursor and limit
  - import into `V2` with duplicate-safe semantics
- For large or critical membership sets, recommend `BTreeSet` in `V2` when deterministic ordering and simpler validation are useful.

## Snapshot Rule

- When possible, recommend freezing `V1` and then reading state from a fixed snapshot block.
- Use `api.programState.read({ at: ... })` when snapshot consistency matters across batches.
- This avoids drift between earlier and later export batches.

## Verification Rule

- Always require post-import verification before activating `V2`.
- At minimum compare:
  - entity counts
  - total balances, reserves, or supply-like totals
  - next-id counters
  - config values
  - membership set sizes
  - optional checksum or hash over exported data
- Do not recommend switching traffic to `V2` before these checks pass.

## Compatibility Rule For Frontend And Indexer

- Treat public routes, method signatures, and event payloads as compatibility-sensitive surfaces.
- If the public surface must evolve, prefer one of these strategies:
  - preserve old route names with `#[export(route = "...")]`
  - use `overrides`, `route`, or `entry_id` to maintain compatibility for inherited services
  - version events instead of silently changing payload shape
- Do not casually rename or reshape exported methods that current clients already use.
- Do not silently change event payload shape in place when an indexer already decodes it.
- Remember that Sails derives deterministic interface identifiers and entry identifiers from the canonical IDL and carries stable routing metadata in the header format.

## Recommended Migration Algorithm

- When the user asks for a practical flow, recommend this order:
  1. deploy `V2`
  2. initialize `V2` in `ReadOnly`
  3. call `V1.set_read_only(true)`
  4. record the snapshot block hash
  5. export config and scalar state from `V1`
  6. import config and scalar state into `V2`
  7. export all business collections from `V1` in deterministic chunks
  8. import all chunks into `V2` with idempotent batch methods
  9. compare stats and invariants
  10. call `V2.finalize_import()`
  11. switch frontend and indexer to `V2`
  12. keep `V1` read-only for a rollback window if needed
- Treat rollback planning as part of the release, not as an afterthought.

## Things The Agent Must Not Suggest

- Do not suggest replacing code in place as the default Gear/Sails strategy.
- Do not suggest one giant monolithic state dump for large production state.
- Do not suggest non-deterministic `HashMap` or `HashSet` export order.
- Do not suggest import methods without idempotency.
- Do not suggest changing public routes or event shapes casually.
- Do not suggest migrating caches as if they were the source of truth.

## Expected Output From The Agent

- When using this reference, the agent should produce:
  - a clear split between `V1`, `V2`, and off-chain migrator responsibilities
  - a state inventory plan
  - export/import API design
  - collection-specific migration rules
  - verification checklist
  - compatibility notes for frontend and indexer
  - explicit mention of which parts are platform-supported and which are project conventions

## Platform-Supported Pieces Versus Project Conventions

- Platform-supported primitives include:
  - deploying a new program via upload or create flows
  - reading full state
  - reading selected state using state functions
  - reading state at a specific block hash
- Project conventions in this reference include:
  - `V1 -> V2 -> cutover` release discipline
  - `Active` and `ReadOnly` as the default minimal status model
  - chunked deterministic export/import API design
  - idempotent batch import semantics
  - explicit verification before cutover

## Default Conclusion

- If the user asks for the safest default pattern, recommend:
  - immutable `V1`
  - deploy `V2`
  - `ReadOnly` freeze
  - chunked deterministic export/import
  - idempotent batches
  - verification
  - cutover
- This is the baseline production-friendly upgradability and migration pattern for Gear/Sails in this pack.
