---
name: sails-indexer
description: Use when a builder needs a read-side indexer and query API for a standard Gear/Vara Sails app using program events, IDL-driven decoding, projected read models, and optional on-chain query enrichment. Do not use for command-side backends, generic Node APIs, non-Sails repositories, Vara.eth or ethexe-first work.
---

# Sails Indexer

## Role

Design and implement the read-side backend for a standard Gear/Vara Sails app.

Use this skill when the frontend or integration layer needs history, pagination, filtering, search, aggregates, charts, timelines, or a fast read API that should not be rebuilt from direct chain queries on every screen load.

Treat the indexer as a projection pipeline:

`chain/archive -> Sails event decode -> optional on-chain enrichment -> Postgres read model -> thin GraphQL API`

## Local Handbook

- `../../references/gear-execution-model.md`
- `../../references/gear-messaging-and-replies.md`
- `../../references/sails-program-and-service-architecture.md`
- `../../references/sails-idl-client-pipeline.md`
- `../../references/sails-cheatsheet.md`
- `../../references/sails-gtest-and-local-validation.md`
- `../../references/scale-binary-decoding-guide.md`
- `../../references/contract-interface-evolution.md`
- `../../references/sails-indexer-patterns.md`

## Standard Defaults

- Default to an IDL-driven read-side indexer, not a generic command-side backend.
- Treat the program `.idl` as the event and route contract for normal Sails decoding work.
- Default stack: Subsquid-style archive ingestion, PostgreSQL read model, ORM-backed entities, and a thin GraphQL API.
- Always expose GraphQL as the default read surface for frontend and integration consumers. Do not downgrade the default to REST.
- Mount a real GraphQL endpoint such as `/graphql` and make it reachable from local frontend development without browser CORS failures.
- Prefer one of two frontend-safe API exposure strategies and name the choice explicitly: enable CORS on the indexer API, or serve GraphQL through the frontend dev proxy or same-origin gateway.
- Use a real ingestion adapter wired to chain or archive sources. Do not leave placeholder, null, or demo adapters in the runtime.
- Prefer event-driven projections first. Use live on-chain queries only for explicit enrichment or source-of-truth confirmation.
- Keep projection logic in processor or handler services. Keep the API layer thin.
- Model restart, replay, backfill, and duplicate safety as first-class requirements, not as later hardening.
- Prefer deterministic entity IDs derived from chain facts such as program ID, message ID, block number, extrinsic position, or explicit domain keys.
- If the repo already has an indexer stack, extend it instead of replacing it with a new framework casually.
- Pin PostGraphile to the v4 line for this skill pack. The reference code and templates target `postgraphile@4.14.1` and `postgraphile-plugin-connection-filter@2.3.0`. v5 uses a completely different plugin and middleware API that is incompatible with the current reference snippets. Do not install or document v5 until the API layer is intentionally rewritten against the v5 contract.
- Follow the canonical runtime order from `../../references/sails-indexer-patterns.md`, especially `Start with configuration, not hardcoded endpoints`, `Build one shared batch processor and export its derived types`, `Centralize all IDL decoding behind one decoder`, `Wire the runtime in main.ts, but do not place projection logic there`, `Give every handler the same lifecycle contract`, `Process a batch in a stable order`, `Save in groups and only write what changed`, and `Expose a thin API layer on top of PostgreSQL`.

## Route Here When

- the builder needs historical views, activity feeds, portfolio pages, or timelines
- the frontend needs pagination, filtering, sorting, or joins that are awkward or expensive through direct chain queries
- the project needs aggregated metrics, snapshots, counters, rankings, charts, or search
- the app has many dynamic child programs that cannot be enumerated upfront and whose events must be indexed
- the builder needs a query API backed by projected data rather than live state reads only
- the work requires event decoding from `.idl` and mapping those events into off-chain entities

## Do Not Route Here When

- the task is really a command-side backend, auth service, session service, cron worker, or general Node API
- the task only needs a few direct Sails queries from frontend or scripts and no persistent read model
- the project is Vara.eth or ethexe-first rather than standard Gear/Vara Sails
- the main problem is contract architecture, not read-side projection design
- the request is purely about frontend wiring without a new read model

## Required Input Contract

Before implementation, make these inputs explicit:

- target programs to index: fixed IDs, discovery source, or hybrid
- `.idl` files or generated decode artifacts for each indexed program
- `fromBlock` or backfill start rule
- list of events, services, and payloads that matter
- required read entities and the UI or integration surfaces that consume them
- enrichment needs: event-only, event-plus-query, or periodic derived updates
- GraphQL endpoint contract: route, local development origin policy, and whether frontend reaches it through direct CORS or dev proxy
- restart, replay, and cutover constraints for existing deployments

If any of these are unknown, stop and write the missing assumptions explicitly before coding.

Cross-check against `../../references/sails-indexer-patterns.md`:

- `Start with configuration, not hardcoded endpoints`, `Build one shared batch processor and export its derived types`, and `Create a typed boundary for Gear events before touching business payloads` for config, processor boundary, and typed Gear event boundary
- `Centralize all IDL decoding behind one decoder` for decoder setup and query encoding or decoding
- `Keep the SQL schema read-model oriented` before freezing the SQL or ORM schema

## Quick Start

Use this cold-start path when the repo does not already contain a working indexer scaffold.

Templates live in `skills/sails-indexer/assets/`:

- `package.json`
- `tsconfig.json`
- `docker-compose.yml`
- `.env.example`

Cold-start defaults:

- Node.js 20+
- PostgreSQL available locally (prefer a local service install; Docker is an alternative if a local service is not available)
- `reflect-metadata` imported once at the top of each runtime entrypoint before TypeORM entities or data source code is loaded
- `experimentalDecorators: true` and `emitDecoratorMetadata: true` enabled in `tsconfig.json`
- separate Subsquid gateway URL (`VARA_ARCHIVE_URL`) and Vara archive RPC URL (`VARA_RPC_URL`); Subsquid performs historical queries that require an archive node on the RPC side, so do not point `VARA_RPC_URL` at a live non-archive endpoint

Suggested first-run order:

1. Copy the files from `assets/` into the new indexer repo.
2. Fill `.env` from `.env.example`.
3. Install dependencies with `npm install`.
4. Start PostgreSQL (local service, or `docker compose up -d` if using Docker).
5. Generate TypeORM entities from `schema.graphql` with `npm run codegen`.
6. Build once with `npm run build`.
7. Generate a migration with `npm run db:generate`.
8. Apply the migration with `npm run db:apply`.
9. Start the processor with `npm run dev:processor`.
10. Start the API with `npm run dev:api`.
11. Verify that `/graphql` is reachable through the chosen local access path.

For schema updates, use this order:

1. update `schema.graphql`
2. `npm run codegen`
3. `npm run build`
4. `npm run db:generate`
5. `npm run db:apply`

For fixed-program projects, `.env` can stay minimal with one `VARA_PROGRAM_ID` and one `VARA_IDL_PATH`.
For discovery-driven projects, replace that pair with the explicit root IDs that serve as discovery sources — `REGISTRY_PROGRAM_ID`, `FACTORY_PROGRAM_ID`, or other domain-specific anchors — and keep discovery logic separate from projection logic. If the set of programs is small and known upfront, list them directly in config rather than building a discovery pipeline.

## Required Sequence

1. Confirm that an indexer is actually needed and that direct chain queries are not sufficient.
2. Classify the source topology: fixed program list, discovery-driven, or hybrid.
3. Build an event inventory from the relevant `.idl` files: service, event name, payload shape, and source program.
4. Design the read model around consumer needs, not as a blind mirror of contract storage.
5. For each entity, name the deterministic ID, update trigger, required fields, and replay behavior.
6. Decide the enrichment mode for each projection path: event-only, event-plus-query, or periodic derived aggregation.
7. Separate discovery handlers from domain projection handlers when programs can appear dynamically. Fixed-program topologies can skip discovery entirely and load the tracked program list from config at startup.
8. Define batch processing, duplicate safety, restart rehydration, and backfill rules before writing handlers.
9. Keep the API layer thin, GraphQL-first, and backed by projected tables or views rather than recomputing domain logic at request time.
10. Define the frontend access path to GraphQL explicitly: direct CORS-enabled access or frontend proxy or same-origin exposure.
11. Name the verification plan: backfill, replay, duplicate handling, restart recovery, live-sync sanity checks, GraphQL availability, and browser-safe frontend access.

Map this sequence to the reference before writing code:

- step 1 -> `Decide Whether The Project Needs An Indexer First`
- step 2 -> `Split dynamic discovery from domain projection`
- step 3 -> `Create a typed boundary for Gear events before touching business payloads`, `Keep chain event guards in small helpers`, `Centralize all IDL decoding behind one decoder`, and `Decode only after confirming that the message is a Sails event`
- step 4 -> `Keep the SQL schema read-model oriented` and `Expose a thin API layer on top of PostgreSQL`
- step 5 -> `Convert events into append-only activity records with deterministic IDs` and `Deterministic IDs`
- step 6 -> `Source-Of-Truth Rules`
- step 7 -> `Split dynamic discovery from domain projection` and `Keep explicit runtime state per tracked program`
- step 8 -> `Rehydrate tracked programs from the database on first processing run`, `Process a batch in a stable order`, `Save in groups and only write what changed`, and `Idempotency And Restart Rules`
- step 9 -> `Expose a thin API layer on top of PostgreSQL`
- step 10 -> `Expose a thin API layer on top of PostgreSQL`
- step 11 -> `Minimal Build Order`

## Working Model

### 1. Decide whether the indexer is event-led or state-confirming

For each projected entity, state which source answers which question:

- events tell us **what happened**
- on-chain queries tell us **what state should now be considered canonical**
- derived jobs tell us **what aggregate or snapshot should now exist**

Do not mix these roles implicitly.

Reference: `../../references/sails-indexer-patterns.md` section `Source-Of-Truth Rules`.

### 2. Keep discovery separate from domain projection

If one program emits “child created”, “resource registered”, “room opened”, “position created”, or similar discovery events, isolate that logic from the handler that projects activity inside the created child program.

Preferred split:

- discovery or registry handler
- domain handler per indexed program family

Reference: `../../references/sails-indexer-patterns.md` sections `Split dynamic discovery from domain projection`, `Keep explicit runtime state per tracked program`, and `Rehydrate tracked programs from the database on first processing run`.

### 3. Design read models for readers, not writers

The read model should answer frontend or integration questions efficiently.

Common projected entity types:

- current summary entity
- append-only activity or transaction entity
- snapshot entity by hour, day, or custom window
- search or ranking entity
- denormalized list entity for fast screen rendering

Do not copy every on-chain field into SQL unless a consumer actually needs it.

Reference: `../../references/sails-indexer-patterns.md` sections `Keep the SQL schema read-model oriented` and `Expose a thin API layer on top of PostgreSQL`.

### 4. Treat replay and idempotency as part of the architecture

A valid design must explain:

- how the indexer restarts without losing tracked programs
- how already-seen events avoid duplicate rows or double-counting
- how backfill from an older block range behaves
- how projected aggregates are recomputed or repaired

Reference: `../../references/sails-indexer-patterns.md` section `Idempotency And Restart Rules`.

### 5. Treat the read API as a facade over the read model

The API should expose projected data cleanly, but the API layer should not become the place where chain events are reinterpreted from scratch.

Reference: `../../references/sails-indexer-patterns.md` section `Expose a thin API layer on top of PostgreSQL`.

## Default Project Shape

A standard implementation usually needs these areas:

- `src/config.ts` for endpoints, IDs, and environment contract
- `src/processor.ts` for archive or chain batch ingestion
- `src/decoder/` or `src/sails-decoder.ts` for IDL-driven decode helpers
- `src/types/` and `src/helpers/` for typed Gear boundary and event guards
- `src/handlers/` for discovery and domain projection handlers
- `src/services/` for enrichment and aggregate calculations
- `src/model/` for entities and persistence mapping
- `src/api/` or `src/api.ts` for thin GraphQL API exposure
- `src/api/graphql.ts` or equivalent GraphQL bootstrap module with an explicit `/graphql` mount
- `schema.graphql` or ORM schema plus DB migrations

Reference path for this layout:

- `Start with configuration, not hardcoded endpoints` through `Give every handler the same lifecycle contract` for bootstrap and lifecycle
- `Split dynamic discovery from domain projection` through `Save in groups and only write what changed` for discovery, runtime state, projection, and persistence
- `Keep the SQL schema read-model oriented` for schema shape
- `Expose a thin API layer on top of PostgreSQL` for API exposure
- `Standard Project Layout` for the final filesystem view

Name any deviation from this shape explicitly.

## Required Output Shape

The work product must make these decisions explicit:

- why the indexer is needed instead of direct chain reads
- indexed programs and discovery strategy
- event inventory and decode path
- read-model entities and deterministic IDs
- enrichment strategy per entity or handler path
- replay, restart, and duplicate-safety model
- projected API surface and intended consumers
- environment contract, run commands, migration commands, and validation steps

When producing implementation plans or code, mirror the order from `../../references/sails-indexer-patterns.md` rather than jumping directly into handlers or schema work.

## Verification Minimum

Before handoff, require at least:

- one backfill run from the chosen `fromBlock`
- one replay or rerun check proving idempotent persistence
- one restart check proving rehydration of tracked programs and stateful projections
- one duplicate-event or repeated-batch check for aggregate safety
- one live-sync sanity check against current chain activity
- one GraphQL sanity check proving that `/graphql` is mounted and serves the projected read model
- one browser-facing frontend access check proving that local frontend can read the GraphQL endpoint without CORS failure
- one ingestion sanity check proving that the runtime uses a real chain or archive adapter rather than a null or placeholder source
- one API sanity check proving that projected data answers the target frontend or integration query

Reference checkpoints:

- `Rehydrate tracked programs from the database on first processing run` for restart rehydration
- `Process a batch in a stable order` for stable batch order
- `Build rolling metrics from persisted and pending snapshots together` for rolling metrics over persisted plus pending state
- `Save in groups and only write what changed` for grouped persistence
- `Idempotency And Restart Rules` for replay safety

## Guardrails

- Do not describe this skill as a generic backend generator.
- Do not merge command-side writes, auth, or session management into the indexer unless the task explicitly asks for a broader backend and the scope is renamed.
- Do not model the SQL schema as a blind mirror of contract storage.
- Do not skip the event inventory and jump straight into handlers.
- Do not trust event payloads as full canonical state unless the architecture names that choice explicitly.
- Avoid live on-chain queries in hot event-processing paths. Frequent on-chain calls after each event are a design smell and indicate poor architecture. Reserve on-chain queries for initial entity bootstrap or deliberate source-of-truth confirmation, and document the reason explicitly each time.
- Do not treat replay, reorg tolerance, restart recovery, or duplicate handling as optional polish.
- Do not listen to the entire chain without explaining why broad filtering is necessary and acceptable.
- Do not hardcode domain-specific entities, metrics, or pricing assumptions into this skill.
- Do not bypass `.idl` for normal Sails decoding work unless the task is intentionally about raw SCALE, metadata, or route-debugging.
- Do not ship a REST-only read API as the default output of this skill. The default read surface must be GraphQL.
- Do not leave the runtime on a placeholder, null, mock, or demo chain-source adapter once the indexer is claimed to be implemented.
- Do not expose a localhost GraphQL API to a browser-based frontend without naming and implementing the local access strategy: CORS, frontend proxy, or same-origin serving.
- Do not claim that GraphQL is part of the indexer unless a real `/graphql` endpoint is mounted and reachable.
- If the indexed contracts are already deployed and compatibility matters, cross-check `../sails-program-evolution/SKILL.md` before freezing the projection model.
- If runtime structure starts drifting, realign it to `../../references/sails-indexer-patterns.md`, especially the sections "Wire the runtime in main.ts, but do not place projection logic there", "Give every handler the same lifecycle contract", "Split dynamic discovery from domain projection", "Process a batch in a stable order", and "Save in groups and only write what changed".
