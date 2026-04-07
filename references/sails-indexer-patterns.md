# Sails Indexer Patterns

> **Usage note**: This is a comprehensive reference handbook, not a document to load in full on every task. The `sails-indexer` skill cross-references specific sections by name for each workflow step. Consult the relevant section for the step at hand rather than reading top to bottom.

## Decide Whether The Project Needs An Indexer First

Add an indexer only when the project needs a persistent read model that direct chain queries cannot provide cheaply or cleanly. Typical signals are historical views, activity feeds, pagination, filtering, joins across multiple programs, rolling aggregates, charts, rankings, or a read API that must stay fast even when the chain or RPC is slow.

Stay with direct chain queries when the frontend only needs a few live reads from a small number of programs and there is no requirement for replayable history, searchable lists, or derived windows. Do not build an indexer just because the project has events. Build one when projected read models are part of the product surface.

Before writing processor, handler, or schema code, make the decision explicit in plain project notes: either direct chain reads are enough, or a projected read model is required because the product needs durable history, filtering, joins, aggregates, or a fast dedicated read API.

Use this reference when implementing a read-side indexer for a standard Gear/Vara Sails project.

Treat the indexer as a projection pipeline:

`archive or chain -> typed Gear event boundary -> Sails IDL decode -> project -> enrich -> persist -> expose thin GraphQL API`

This reference assumes GraphQL is the default read surface. Do not treat REST and GraphQL as interchangeable defaults. If another read surface is added for a specific integration, GraphQL should still remain the primary contract for frontend and developer inspection.

The most important rule is to preserve a clean boundary between:

- what happened on chain
- how it is decoded off chain
- what gets persisted as the read model
- how that read model is exposed to consumers

This reference uses a single canonical layout and flow. The names below are generic, but the structure is intentionally close to a real working implementation.

---

## Canonical Runtime Flow

### 1. Start with configuration, not hardcoded endpoints

Keep archive, RPC, rate limits, block range, and root program IDs in one place.

```ts
// src/config.ts
import { HexString } from "@gear-js/api";
import dotenv from "dotenv";

dotenv.config();

const getEnv = (key: string, fallback?: string): string => {
  const value = process.env[key] || fallback;
  if (!value) {
    throw new Error(`Environment variable ${key} is not set`);
  }
  return value;
};

export const config = {
  archiveUrl: getEnv(
    "VARA_ARCHIVE_URL",
    "https://v2.archive.subsquid.io/network/vara-testnet"
  ),
  rpcUrl: getEnv("VARA_RPC_URL"),
  rateLimit: Number(getEnv("VARA_RPC_RATE_LIMIT", "20")),
  fromBlock: Number(getEnv("VARA_FROM_BLOCK", "0")),
  registryProgramId: getEnv("REGISTRY_PROGRAM_ID") as HexString,
};
```

`rpcUrl` should point to a Vara archive node endpoint. Subsquid performs historical queries during indexing and a live non-archive node is not sufficient. Keep the Subsquid gateway URL (`archiveUrl`) and the Vara archive RPC URL (`rpcUrl`) as separate config entries — they serve different ingestion roles but both require archive-capable backing.

Why this shape matters:

- the processor must be restartable from a known `fromBlock`
- program IDs must not be scattered through handlers
- RPC and archive concerns should stay outside domain projection code

---

### 2. Build one shared batch processor and export its derived types

Every other file should consume the exported processor-derived types instead of redefining Subsquid payloads ad hoc.

```ts
// src/processor.ts
import {
  BlockHeader as _BlockHeader,
  DataHandlerContext,
  SubstrateBatchProcessor,
  SubstrateBatchProcessorFields,
  Event as _Event,
  Call as _Call,
  Extrinsic as _Extrinsic,
} from "@subsquid/substrate-processor";
import { Store } from "@subsquid/typeorm-store";
import { hostname } from "node:os";

import { config } from "./config";

export const processor = new SubstrateBatchProcessor()
  .setGateway(config.archiveUrl)
  .setRpcEndpoint({
    url: config.rpcUrl,
    rateLimit: config.rateLimit,
    headers: {
      "User-Agent": hostname(),
    },
  })
  .setBlockRange({ from: config.fromBlock })
  .setFields({
    event: {
      args: true,
      extrinsic: true,
      call: true,
    },
    extrinsic: {
      hash: true,
      fee: true,
      signature: true,
    },
    call: {
      args: true,
    },
    block: {
      timestamp: true,
    },
  });

export type Fields = SubstrateBatchProcessorFields<typeof processor>;
export type BlockHeader = _BlockHeader<Fields> & { timestamp: number };
export type Event = _Event<Fields>;
export type Call = _Call<Fields>;
export type Extrinsic = _Extrinsic<Fields>;
export type ProcessorContext = DataHandlerContext<Store, Fields>;
```

Why this shape matters:

- the entire indexer gets one consistent type boundary
- handler code stays focused on projection work, not processor wiring
- any future field expansion happens in one file

---

### 3. Create a typed boundary for Gear events before touching business payloads

Do not let raw processor `Event` values leak through the whole codebase.

```ts
// src/types/gear-events.ts
import { Call, Event, Extrinsic } from "../processor";

export interface MessageQueuedExtrinsic extends Extrinsic {
  readonly hash: `0x${string}`;
}

export interface MessageQueuedCall extends Omit<Call, "args"> {
  readonly args: {
    readonly destination: `0x${string}`;
    readonly payload: `0x${string}`;
    readonly gasLimit: string;
    readonly value: string;
  };
}

export type MessageQueuedEvent = Omit<Event, "args" | "extrinsic" | "call"> & {
  args: MessageQueuedArgs;
  extrinsic: MessageQueuedExtrinsic;
  call: MessageQueuedCall;
};

export interface MessageQueuedArgs {
  readonly id: string;
  readonly source: string;
  readonly destination: string;
  readonly entry: "Init" | "Handle" | "Reply";
}

export interface GearRunExtrinsic extends Extrinsic {
  readonly hash: `0x${string}`;
}

export type UserMessageSentEvent = Omit<Event, "args" | "extrinsic"> & {
  args: UserMessageSentArgs;
  extrinsic: GearRunExtrinsic;
};

export interface UserMessageSentArgs {
  readonly message: {
    readonly id: `0x${string}`;
    readonly source: `0x${string}`;
    readonly destination: `0x${string}`;
    readonly payload: `0x${string}`;
    readonly value: string;
    readonly details?: UserMessageSentDetails;
  };
}

export interface UserMessageSentDetails {
  readonly code: {
    readonly __kind: "Success" | "Error";
  };
  readonly to: `0x${string}`;
}
```

Add explicit tracked-program descriptors as their own type instead of passing plain tuples around.

```ts
// src/types/tracked-program.ts
export interface TrackedProgramInfo {
  address: `0x${string}`;
  tags: `0x${string}`[];
}
```

Why this shape matters:

- typed Gear boundary and typed projection boundary are different concerns
- event filtering becomes safer and easier to review
- generic projection code can depend on `TrackedProgramInfo` instead of domain-specific ad hoc objects

---

### 4. Keep chain event guards in small helpers

The handlers should not repeat event-name checks everywhere.

```ts
// src/helpers/is.ts
import { MessageQueuedEvent, UserMessageSentEvent } from "../types";
import { Event } from "../processor";

export function isUserMessageSentEvent(
  event: Event
): event is UserMessageSentEvent {
  return event.name === "Gear.UserMessageSent";
}

export function isMessageQueuedEvent(
  event: Event
): event is MessageQueuedEvent {
  return event.name === "Gear.MessageQueued";
}

export function isSailsEvent(event: UserMessageSentEvent): boolean {
  return !Boolean(event.args.message.details);
}
```

Why this shape matters:

- handler code stays readable
- protocol-level checks are centralized
- the event classification logic is easy to test separately

---

### 5. Centralize all IDL decoding behind one decoder

All `.idl` parsing, prefix detection, event decoding, query encoding, and query result decoding should live in one place.

```ts
// src/sails-decoder.ts
import { isHex } from "@subsquid/util-internal-hex";
import { existsSync, readFileSync } from "node:fs";
import { getFnNamePrefix, getServiceNamePrefix, Sails } from "sails-js";
import { SailsIdlParser } from "sails-js-parser";
import { MessageQueuedEvent, UserMessageSentEvent } from "./types";

interface Message {
  service: string;
  method: string;
}

interface InputMessage<T> extends Message {
  params: T;
}

interface OutputMessage<T> extends Message {
  payload: T;
}

export class SailsDecoder {
  constructor(private readonly program: Sails) {}

  static async new(idlPath: string): Promise<SailsDecoder> {
    if (!existsSync(idlPath)) {
      throw new Error(`File ${idlPath} does not exist`);
    }

    const parser = await SailsIdlParser.new();
    const sails = new Sails(parser);
    sails.parseIdl(readFileSync(idlPath, "utf8"));

    return new SailsDecoder(sails);
  }

  service(data: string): string {
    if (!isHex(data)) {
      throw new Error(`Invalid hex string: ${data}`);
    }
    return getServiceNamePrefix(data as `0x${string}`);
  }

  method(data: string): string {
    if (!isHex(data)) {
      throw new Error(`Invalid hex string: ${data}`);
    }
    return getFnNamePrefix(data as `0x${string}`);
  }

  decodeInput<T>({
    call: {
      args: { payload },
    },
  }: MessageQueuedEvent): InputMessage<T> {
    const service = this.service(payload);
    const method = this.method(payload);
    const params =
      this.program.services[service].functions[method].decodePayload<T>(
        payload
      );

    return { service, method, params };
  }

  decodeOutput<T>({
    args: {
      message: { payload },
    },
  }: UserMessageSentEvent): OutputMessage<T> {
    const service = this.service(payload);
    const method = this.method(payload);
    const result =
      this.program.services[service].functions[method].decodeResult<T>(payload);

    return { service, method, payload: result };
  }

  decodeEvent<T>({
    args: {
      message: { payload },
    },
  }: UserMessageSentEvent): OutputMessage<T> {
    const service = this.service(payload);
    const method = this.method(payload);
    const result = this.program.services[service].events[method]?.decode(payload);

    return { service, method, payload: result };
  }

  encodeQueryInput(service: string, fn: string, data: any[]): `0x${string}` {
    return this.program.services[service].queries[fn].encodePayload(...data);
  }

  decodeQueryOutput<T>(service: string, fn: string, data: string): T {
    return this.program.services[service].queries[fn].decodeResult<T>(
      data as `0x${string}`
    );
  }
}
```

Why this shape matters:

- handlers never need to know payload prefix details
- IDL-driven decode stays consistent across events, replies, and queries
- query enrichment uses the same protocol boundary as event projection

---

### 6. Wire the runtime in `main.ts`, but do not place projection logic there

The entrypoint should only compose the processor, API, decoders, and handlers.

```ts
// src/main.ts
import { TypeormDatabase } from "@subsquid/typeorm-store";
import { GearApi } from "@gear-js/api";

import { BaseHandler } from "./handlers/base";
import { RegistryHandler, ProgramsHandler } from "./handlers";
import { config } from "./config";
import { processor } from "./processor";

export class GearProcessor {
  private readonly handlers: BaseHandler[] = [];

  public addUserMessageSent(programIds: string[]) {
    for (const id of programIds) {
      console.log(`[*] Adding UserMessageSent events for program ${id}`);
    }

    processor.addGearUserMessageSent({
      programId: undefined,
      extrinsic: true,
      call: true,
    });
  }

  public registerHandler(handler: BaseHandler) {
    this.handlers.push(handler);

    const programIds = handler.getUserMessageSentProgramIds();
    if (programIds.length > 0) {
      this.addUserMessageSent(programIds);
    }
  }

  public async run() {
    const db = new TypeormDatabase({
      supportHotBlocks: true,
      stateSchema: "gear_processor",
    });

    processor.run(db, async (ctx) => {
      for (const handler of this.handlers) {
        await handler.process(ctx);
      }

      for (const handler of this.handlers) {
        await handler.save();
      }
    });
  }
}

async function main() {
  const api = await GearApi.create({ providerAddress: config.rpcUrl });
  const app = new GearProcessor();

  const programsHandler = new ProgramsHandler();
  const registryHandler = new RegistryHandler(
    config.registryProgramId,
    programsHandler
  );

  await registryHandler.init(api);
  await programsHandler.init(api);

  app.registerHandler(registryHandler);
  app.registerHandler(programsHandler);

  await app.run();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

Why this shape matters:

- startup order is explicit
- handler lifecycle is deterministic
- runtime composition stays separate from domain projection logic

---

### 7. Give every handler the same lifecycle contract

The clean pattern is:

- `init()` for one-time startup work
- `process(ctx)` for current batch work
- `save()` for persistence
- `clear()` for resetting batch-local state

```ts
// src/handlers/base.ts
import { Logger } from "@subsquid/logger";
import { GearApi } from "@gear-js/api";
import { ProcessorContext } from "../processor";

export abstract class BaseHandler {
  protected events: string[] = [];
  protected userMessageSentProgramIds: string[] = [];
  protected messageQueuedProgramIds: string[] = [];
  protected _logger!: Logger;
  protected _ctx!: ProcessorContext;

  public getEvents(): string[] {
    return this.events;
  }

  public getUserMessageSentProgramIds(): string[] {
    return this.userMessageSentProgramIds;
  }

  public getMessageQueuedProgramIds(): string[] {
    return this.messageQueuedProgramIds;
  }

  public init(_api: GearApi): Promise<void> {
    return Promise.resolve();
  }

  abstract clear(): void;

  async process(ctx: ProcessorContext): Promise<void> {
    this._ctx = ctx;
    this.clear();
  }

  abstract save(): Promise<void>;
}
```

Why this shape matters:

- batch processing and persistence are separated
- handlers can keep controlled in-memory state between `process()` and `save()`
- the same lifecycle works for discovery handlers and projection handlers

---

### 8. Split dynamic discovery from domain projection

If the topology is fixed from day one, skip discovery entirely. A single known program ID, or a small fixed set of program IDs, should be loaded from configuration and projected directly. Add a discovery handler only when the product truly creates or tracks programs dynamically.

If one program creates or registers child programs, keep that logic in a dedicated handler.

```ts
// src/handlers/registry.ts
import { isSailsEvent, isUserMessageSentEvent } from "../helpers";
import { ProcessorContext } from "../processor";
import { SailsDecoder } from "../sails-decoder";
import { UserMessageSentEvent, TrackedProgramInfo } from "../types";
import { BaseHandler } from "./base";
import { ProgramsHandler } from "./programs";

interface ProgramRegisteredPayload {
  program_id: `0x${string}`;
  tags: `0x${string}`[];
}

export class RegistryHandler extends BaseHandler {
  private decoder!: SailsDecoder;

  constructor(
    private readonly registryProgramId: string,
    private readonly programsHandler: ProgramsHandler
  ) {
    super();
    this.userMessageSentProgramIds = [registryProgramId];
  }

  public async init(): Promise<void> {
    this.decoder = await SailsDecoder.new("assets/registry.idl");
  }

  public clear(): void {}

  public async save(): Promise<void> {
    const entitiesToSave = this.programsHandler.getPrimaryEntitiesToSave();
    if (entitiesToSave.length > 0) {
      await this._ctx.store.save(entitiesToSave);
    }
  }

  public async process(ctx: ProcessorContext): Promise<void> {
    await super.process(ctx);

    for (const block of ctx.blocks) {
      for (const event of block.events) {
        if (
          isUserMessageSentEvent(event) &&
          event.args.message.source === this.registryProgramId
        ) {
          await this.handleUserMessageSentEvent(event);
        }
      }
    }
  }

  private async handleUserMessageSentEvent(event: UserMessageSentEvent) {
    if (!isSailsEvent(event)) return;

    const { service, method, payload } =
      this.decoder.decodeEvent<ProgramRegisteredPayload>(event);

    if (service === "Registry" && method === "ProgramRegistered") {
      const info: TrackedProgramInfo = {
        address: payload.program_id,
        tags: payload.tags,
      };

      this.programsHandler.registerProgram(info);
    }
  }
}
```

Why this shape matters:

- discovery and projection do not get tangled together
- dynamic program creation works after restarts and replays
- the domain handler can focus on projecting activity from tracked programs

---

### 9. Keep explicit runtime state per tracked program

A projection handler usually needs memory for:

- tracked program metadata
- the current primary entity
- pending activity records for this batch
- pending snapshot records for this batch
- dirty flags
- last periodic-update timestamp
- active or inactive status

```ts
// src/handlers/programs.ts
import { GearApi, HexString } from "@gear-js/api";
import { MoreThanOrEqual } from "typeorm";

import { BaseHandler } from "./base";
import { ProcessorContext } from "../processor";
import { isSailsEvent, isUserMessageSentEvent } from "../helpers";
import { SailsDecoder } from "../sails-decoder";
import { TrackedProgramInfo, UserMessageSentEvent } from "../types";
import {
  TrackedProgram,
  ActivityRecord,
  MetricSnapshot,
  Resource,
  ResourcePriceSnapshot,
} from "../model";

interface TrackedProgramState {
  info: TrackedProgramInfo;
  entity: TrackedProgram | null;
  activity: Map<string, ActivityRecord>;
  snapshots: Map<string, MetricSnapshot>;
  isEntityUpdated: boolean;
  isSnapshotsUpdated: boolean;
  lastPeriodicUpdate: Date | null;
  isActive: boolean;
}

export class ProgramsHandler extends BaseHandler {
  private decoder!: SailsDecoder;
  private api!: GearApi;
  private existingProgramsLoaded = false;
  private programs = new Map<string, TrackedProgramState>();
  private resources = new Map<string, Resource>();
  private prices = new Map<string, number>();
  private resourceIdsToSave = new Set<string>();
  private priceSnapshots = new Map<string, ResourcePriceSnapshot>();

  public async init(api: GearApi): Promise<void> {
    this.api = api;
    this.decoder = await SailsDecoder.new("assets/program.idl");
  }

  public registerProgram(info: TrackedProgramInfo): void {
    this.getOrCreateState(info);
  }

  public getPrimaryEntitiesToSave(): TrackedProgram[] {
    const out: TrackedProgram[] = [];

    for (const state of this.programs.values()) {
      if (state.isEntityUpdated && state.entity) {
        if (!state.isActive) {
          state.entity.isActive = false;
        }
        out.push(state.entity);
      }
    }

    return out;
  }

  public clear(): void {
    this.priceSnapshots.clear();
    this.resourceIdsToSave.clear();

    for (const state of this.programs.values()) {
      state.activity.clear();
      state.isEntityUpdated = false;
      state.isSnapshotsUpdated = false;

      if (!state.isActive) {
        this.programs.delete(state.info.address);
      }
    }
  }

  private getOrCreateState(info: TrackedProgramInfo): TrackedProgramState {
    const existing = this.programs.get(info.address);
    if (existing) return existing;

    const state: TrackedProgramState = {
      info,
      entity: null,
      activity: new Map(),
      snapshots: new Map(),
      isEntityUpdated: false,
      isSnapshotsUpdated: false,
      lastPeriodicUpdate: null,
      isActive: true,
    };

    this.programs.set(info.address, state);
    return state;
  }
}
```

Why this shape matters:

- one tracked program can accumulate multiple writes inside one batch
- dirty flags prevent unnecessary writes
- restart-safe rehydration becomes straightforward

---

### 10. Rehydrate tracked programs from the database on first processing run

The projection handler must not depend on a perfect never-failing runtime. After a restart, it should rebuild in-memory tracking from persisted primary entities.

```ts
public async loadExistingPrograms(ctx: ProcessorContext): Promise<void> {
  const existing = await ctx.store.find(TrackedProgram);

  for (const entity of existing) {
    const info: TrackedProgramInfo = {
      address: entity.id as HexString,
      tags: entity.tags as HexString[],
    };

    const state = this.getOrCreateState(info);
    state.entity = entity;
    state.isActive = entity.isActive;
  }
}
```

Use it at the top of `process()`.

```ts
public async process(ctx: ProcessorContext): Promise<void> {
  await super.process(ctx);

  if (!this.existingProgramsLoaded) {
    await this.loadExistingPrograms(ctx);
    this.existingProgramsLoaded = true;
  }

  if (!this.programs.size) {
    return;
  }

  // continue with current batch processing
}
```

Why this shape matters:

- the indexer can restart without losing tracked program memory
- discovery is no longer a one-time event that must remain in RAM forever
- live processing and replay use the same code path

---

### 11. Initialize missing primary entities from on-chain queries

Apply this pattern only when the discovery event does not carry enough information to construct the primary entity — for example, when the event contains only a program address but the entity also requires fields like `title`, `owner`, or `status` that must come from a direct chain read. If the event payload is sufficient, build the entity from it directly and skip the on-chain query.

If the tracked program exists in memory but the primary projected entity is missing, initialize it from chain.

```ts
private async ensurePrimaryEntity(state: TrackedProgramState): Promise<void> {
  if (state.entity || !state.isActive) {
    return;
  }

  try {
    const metadata = await this.queryProgramMetadata(state.info.address);

    state.entity = new TrackedProgram({
      id: state.info.address,
      title: metadata.title,
      owner: metadata.owner,
      status: metadata.status,
      tags: state.info.tags,
      totalCount: BigInt(metadata.totalCount),
      volume: 0,
      isActive: true,
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    state.isEntityUpdated = true;
  } catch {
    state.isActive = false;
    state.isEntityUpdated = true;
  }
}
```

This is the right pattern when events tell you that a program exists, but some initial fields should come from a query.

Why this shape matters:

- discovery and entity bootstrap are separated
- chain state can confirm the canonical initial projection
- failure can deactivate a tracked program cleanly

---

### 12. Initialize supporting entities lazily and cache them in memory

If the projection depends on related on-chain resources, load them from the database first and only then fall back to live queries.

```ts
private async ensureResource(resourceId: string): Promise<void> {
  let resource = this.resources.get(resourceId);

  if (!resource) {
    resource = await this._ctx.store.findOneBy(Resource, { id: resourceId });
  }

  if (!resource) {
    resource = await this.createResourceFromContract(resourceId);
  }

  if (!resource) {
    throw new Error(`Failed to load resource ${resourceId}`);
  }

  this.resources.set(resource.id, resource);
  this.resourceIdsToSave.add(resource.id);
}
```

Why this shape matters:

- repeat queries are avoided during one run
- restart rehydration can reuse persisted rows
- enrichment logic remains explicit and testable

---

### 13. Process a batch in a stable order

The canonical order is:

1. clear batch-local memory
2. rehydrate persisted tracked programs if needed
3. bootstrap missing primary entities
4. bootstrap supporting entities
5. initialize latest snapshots
6. perform periodic updates if needed
7. iterate current block events
8. persist batch results

A concrete `process()` body can look like this:

```ts
public async process(ctx: ProcessorContext): Promise<void> {
  await super.process(ctx);

  if (!this.existingProgramsLoaded) {
    await this.loadExistingPrograms(ctx);
    this.existingProgramsLoaded = true;
  }

  if (!this.programs.size) {
    return;
  }

  const firstBlockTimestamp = new Date(ctx.blocks[0].header.timestamp);

  for (const state of this.programs.values()) {
    await this.ensurePrimaryEntity(state);
    await this.initResources(state);
    await this.initSnapshots(state, firstBlockTimestamp);
  }

  for (const block of ctx.blocks) {
    const blockTimestamp = new Date(block.header.timestamp);
    const blockNumber = BigInt(block.header.height);

    for (const state of this.programs.values()) {
      if (this.shouldPerformPeriodicUpdates(state, blockTimestamp)) {
        await this.performPeriodicUpdates(state, blockTimestamp, blockNumber);
      }
    }

    for (const event of block.events) {
      if (!isUserMessageSentEvent(event)) continue;

      const state = this.programs.get(event.args.message.source);
      if (!state || !state.isActive) continue;

      await this.handleUserMessageSentEvent(state, event, {
        blockNumber,
        blockTimestamp,
      });
    }
  }

  for (const state of this.programs.values()) {
    if (!state.entity || !state.isActive) continue;

    await this.updateRollingMetrics(state, firstBlockTimestamp);
    this.updateCurrentSummary(state);
    state.isEntityUpdated = true;
  }
}
```

Why this shape matters:

- the code path is deterministic and reviewable
- periodic work and event-driven work are both supported
- all writes for one batch are staged before `save()`

---

### 14. Decode only after confirming that the message is a Sails event or message

The handler should first reject non-Sails messages, then decode once, then dispatch by service and method.

For `UserMessageSent` events (outbound from a program), use `isSailsEvent` to guard before decoding:

```ts
private async handleUserMessageSentEvent(
  state: TrackedProgramState,
  event: UserMessageSentEvent,
  common: { blockNumber: bigint; blockTimestamp: Date }
) {
  if (!isSailsEvent(event)) {
    return;
  }

  const { service, method, payload } = this.decoder.decodeEvent(event);

  if (service === "Domain") {
    await this.handleDomainService(state, method, payload, common, event);
  }
}
```

If the indexer needs to track inbound messages (command inputs) or replies, use the corresponding `MessageQueued` events and a matching decoder path. The dispatch pattern is the same — guard first, decode once, route by service and method — but use `this.decoder.decodeInput` for inbound command payloads and `this.decoder.decodeOutput` for outbound reply payloads rather than `decodeEvent`.

Why this shape matters:

- transport-level filtering happens before domain dispatch
- handlers consume structured payloads, not raw SCALE hex
- service routing is explicit and the same pattern applies to events, messages, and replies

---

### 15. Convert events into append-only activity records with deterministic IDs

The safe default is to use a chain-derived ID such as `message.id` when the event represents one logical action.

```ts
private createActivityRecord(
  state: TrackedProgramState,
  event: UserMessageSentEvent,
  common: { blockNumber: bigint; blockTimestamp: Date },
  type: string,
  additionalFields: Partial<ActivityRecord> = {}
): ActivityRecord {
  if (!state.entity) {
    throw new Error("Primary entity is not initialized");
  }

  return new ActivityRecord({
    id: event.args.message.id,
    type,
    blockNumber: common.blockNumber,
    timestamp: common.blockTimestamp,
    program: { id: state.entity.id } as TrackedProgram,
    ...additionalFields,
  });
}
```

Why this shape matters:

- replay naturally overwrites or skips the same record instead of duplicating it
- activity entities remain append-only and easy to inspect
- the handler can compute aggregates from an explicit transaction log

---

### 16. Keep per-method projection logic small and explicit

The common pattern is: decode payload -> create activity record -> enrich -> update summary -> mark dirty.

```ts
interface ActionStartedPayload {
  user_id: string;
  resource_id: string;
  amount: string;
}

interface ActionCompletedPayload {
  user_id: string;
  output_id: string;
  total: string;
}

private async handleDomainService(
  state: TrackedProgramState,
  method: string,
  payload: unknown,
  common: { blockNumber: bigint; blockTimestamp: Date },
  event: UserMessageSentEvent
) {
  switch (method) {
    case "ActionStarted": {
      const p = payload as ActionStartedPayload;
      const activity = this.createActivityRecord(
        state, event, common, "ACTION_STARTED",
        { user: p.user_id, resourceId: p.resource_id, amount: BigInt(p.amount) }
      );
      await this.processActivity(state, activity, common);
      break;
    }

    // Additional cases follow the same shape:
    // cast payload, create activity record, process it.

    default:
      this._ctx.log.debug({ method }, "Unhandled domain event");
  }
}
```

Why this shape matters:

- every indexed event has one obvious projection path
- review does not require reading a huge polymorphic event processor
- adding a new event remains localized

---

### 17. Separate activity projection from current-state refresh

When an event fires, it is often correct to:

- create an append-only activity record from the event payload
- refresh current state from an on-chain query

That gives one record of what happened and one canonical current summary.

```ts
private async processActivity(
  state: TrackedProgramState,
  activity: ActivityRecord,
  common: { blockNumber: bigint; blockTimestamp: Date }
): Promise<void> {
  await this.calculateDisplayFields(activity);
  await this.refreshCurrentState(state, common);
  this.updateMetricSnapshots(state, activity);

  state.activity.set(activity.id, activity);
  state.isEntityUpdated = true;
  state.isSnapshotsUpdated = true;
}
```

A state refresh should update the current primary entity, not the append-only record.

```ts
private async refreshCurrentState(
  state: TrackedProgramState,
  common: { blockTimestamp: Date }
): Promise<void> {
  if (!state.entity) return;

  try {
    const current = await this.queryProgramState(state.info.address);

    state.entity.status = current.status;
    state.entity.totalCount = BigInt(current.totalCount);
    state.entity.owner = current.owner;
  } catch (error) {
    this._ctx.log.error(
      { error, programId: state.info.address },
      "Failed to refresh state; keeping previous values"
    );
  }

  state.entity.updatedAt = common.blockTimestamp;
}
```

Why this shape matters:

- event payloads do not have to carry the full canonical state
- the read model can preserve both activity history and current summary
- on-chain queries remain explicit rather than hidden inside random helpers

---

### 18. Support periodic derived updates, not only event-driven updates

The reference pattern includes periodic updates for snapshots and derived metrics.

```ts
private shouldPerformPeriodicUpdates(
  state: TrackedProgramState,
  currentTime: Date
): boolean {
  const oneHourMs = 60 * 60 * 1000;
  return (
    !state.lastPeriodicUpdate ||
    currentTime.getTime() - state.lastPeriodicUpdate.getTime() >= oneHourMs
  );
}

private async performPeriodicUpdates(
  state: TrackedProgramState,
  timestamp: Date,
  blockNumber: bigint
): Promise<void> {
  await this.updateResourcePrices(state, timestamp, blockNumber);

  if (!state.entity) {
    return;
  }

  const snapshot = MetricSnapshot.createEmptyHourly(
    state.entity.id,
    timestamp
  );

  state.snapshots.set(snapshot.id, snapshot);
  state.lastPeriodicUpdate = timestamp;
  state.isSnapshotsUpdated = true;
  state.isEntityUpdated = true;
}
```

Why this shape matters:

- charts and rolling metrics keep moving even if the program is idle
- periodic projections are modeled explicitly instead of being hidden in API queries
- the same batch pipeline can handle events and time-based snapshots

---

### 19. Build rolling metrics from persisted and pending snapshots together

When computing current windows, include both database rows and not-yet-saved in-memory snapshots.

```ts
private async calculateCurrentMetrics(
  state: TrackedProgramState,
  currentTime: Date
): Promise<{
  metric1h: number;
  metric24h: number;
  metric7d: number;
}> {
  if (!state.entity) {
    return {
      metric1h: 0,
      metric24h: 0,
      metric7d: 0,
    };
  }

  const oneYearAgo = new Date(currentTime.getTime() - 365 * 24 * 60 * 60 * 1000);

  const dbSnapshots = await this._ctx.store.find(MetricSnapshot, {
    where: {
      program: { id: state.entity.id },
      timestamp: MoreThanOrEqual(oneYearAgo),
    },
    order: { timestamp: "DESC" },
  });

  const pendingSnapshots = Array.from(state.snapshots.values());
  const allSnapshots = [...dbSnapshots, ...pendingSnapshots];

  return MetricSnapshot.calculateWindows(allSnapshots, currentTime);
}
```

Why this shape matters:

- the summary entity can be accurate before the current batch is saved
- rolling windows work correctly during live processing
- derived metrics do not depend on stale persisted data alone

---

### 20. Save in groups and only write what changed

The projection handler should persist accumulated writes in `save()`, grouped by entity type and guarded by dirty flags.

```ts
public async save(): Promise<void> {
  for (const state of this.programs.values()) {
    if (state.isSnapshotsUpdated) {
      const snapshots = Array.from(state.snapshots.values());
      if (snapshots.length > 0) {
        await this._ctx.store.save(snapshots);
      }
    }

    const activity = Array.from(state.activity.values());
    if (activity.length > 0) {
      await this._ctx.store.save(activity);
    }
  }

  if (this.resourceIdsToSave.size > 0) {
    const resources = Array.from(this.resourceIdsToSave)
      .map((id) => this.resources.get(id))
      .filter((value): value is Resource => value !== undefined);

    if (resources.length > 0) {
      await this._ctx.store.save(resources);
    }
  }

  if (this.priceSnapshots.size > 0) {
    await this._ctx.store.save(Array.from(this.priceSnapshots.values()));
  }
}
```

Why this shape matters:

- multiple event-derived changes collapse into one batch write set
- the handler owns its persistence strategy
- the database is not hammered with tiny uncontrolled writes inside event loops

---

### 21. Keep the SQL schema read-model oriented

Do not mirror contract storage blindly. Persist what the frontend or integration layer actually reads.

A good generic pattern is:

- one current summary entity per tracked program
- one append-only activity entity
- one snapshot entity for rolling windows or charts
- optional supporting entities such as resources and price snapshots

```graphql
# schema.graphql
type Resource @entity {
  id: ID!
  symbol: String!
  name: String
  decimals: Int!
  totalSupply: BigInt
  createdAt: DateTime! @index
  updatedAt: DateTime! @index
}

type ResourcePriceSnapshot @entity {
  id: ID!
  resource: Resource!
  priceUsd: Float!
  timestamp: DateTime! @index
  blockNumber: BigInt! @index
}

type TrackedProgram @entity {
  id: ID!
  owner: String! @index
  title: String
  status: String! @index
  tags: [String!]!
  totalCount: BigInt!
  volume: Float
  metric1h: Float
  metric24h: Float
  metric7d: Float
  isActive: Boolean! @index
  createdAt: DateTime! @index
  updatedAt: DateTime! @index
  activity: [ActivityRecord!] @derivedFrom(field: "program")
  snapshots: [MetricSnapshot!] @derivedFrom(field: "program")
}

type MetricSnapshot @entity {
  id: ID!
  program: TrackedProgram!
  value: Float!
  transactionCount: Int!
  timestamp: DateTime! @index
  createdAt: DateTime! @index
}

type ActivityRecord @entity {
  id: ID!
  type: String! @index
  program: TrackedProgram!
  user: String! @index
  blockNumber: BigInt! @index
  timestamp: DateTime! @index
  resourceId: String
  outputId: String
  amount: BigInt
  total: BigInt
  valueUsd: Float
}
```

Why this shape matters:

- the read model is optimized for queries, not for contract serialization symmetry
- history and current summary are separated
- charts and feed pages become cheap to serve

---

### 22. Expose a thin API layer on top of PostgreSQL

A good default is to keep business logic in the processor and let the API expose already projected data.

This section intentionally targets the PostGraphile v4 library API. Pin `postgraphile@4.14.1` and `postgraphile-plugin-connection-filter@2.3.0` when following the snippet below. Do not mix these examples with PostGraphile v5 setup until the API bootstrap is rewritten as a separate migration.

```ts
// src/api.ts
import express from "express";
import { postgraphile, PostGraphileOptions } from "postgraphile";
import ConnectionFilterPlugin from "postgraphile-plugin-connection-filter";
import { createServer } from "node:http";
import { Pool } from "pg";
import cors from "cors";
import dotenv from "dotenv";

dotenv.config();

const isDev = process.env.NODE_ENV === "development";

async function main() {
  const dbPool = new Pool({
    connectionString: process.env.DATABASE_URL || "postgres://indexer",
  });

  const frontendUrl = process.env.FRONTEND_URL || "http://localhost:3000";

  const options: PostGraphileOptions = {
    watchPg: isDev,
    graphiql: true,
    enhanceGraphiql: isDev,
    subscriptions: true,
    dynamicJson: true,
    disableDefaultMutations: true,
    ignoreRBAC: false,
    showErrorStack: isDev ? "json" : true,
    legacyRelations: "omit",
    appendPlugins: [ConnectionFilterPlugin],
    graphqlRoute: "/graphql",
    graphiqlRoute: "/graphiql",
  };

  const middleware = postgraphile(dbPool, "public", options);
  const app = express();

  app.use(cors({ origin: frontendUrl }));
  app.use(middleware);

  const server = createServer(app);
  const port = Number(process.env.GQL_PORT || 4350);

  server.listen({ host: "0.0.0.0", port }, () => {
    console.log(`GraphQL listening at http://0.0.0.0:${port}/graphql`);
    console.log(`GraphiQL listening at http://0.0.0.0:${port}/graphiql`);
  });
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
```

Why this shape matters:

- the API layer stays thin
- request-time logic does not re-derive chain meaning from scratch
- frontend reads from projected tables instead of hot chain queries

---

## Frontend-Safe GraphQL Exposure

A local browser frontend must be able to reach the GraphQL endpoint without origin-policy surprises. Name the local access strategy explicitly and implement it in code.

Use one of these patterns:

- enable CORS on the indexer API for the frontend origin
- serve GraphQL through the frontend development proxy
- serve frontend and GraphQL behind the same origin gateway

Do not leave this implicit. If the frontend reads `http://127.0.0.1:4350` directly, the indexer must either allow that origin explicitly or the frontend must proxy requests through its own development server.

A local verification step should always include a browser-origin request to the GraphQL endpoint, not only a curl request from the terminal.

## Standard Project Layout

A practical indexer layout should look like this:

```text
src/
  api.ts
  config.ts
  processor.ts
  sails-decoder.ts
  helpers/
    is.ts
    block.ts
  handlers/
    base.ts
    registry.ts
    programs.ts
    index.ts
  model/
    generated/*
    dataSource.ts
    index.ts
  services/
    query-client.ts
    calculators/*
    caches/*
  types/
    gear-events.ts
    tracked-program.ts
    block.ts
schema.graphql
assets/
  registry.idl
  program.idl
```

This layout fits projects with multiple event types, separate handlers, and enrichment services. For programs with few events or simple business logic, a flatter structure (e.g., one or two handler files, no `services/` subdirectory) is equally valid. Adapt the layout to what the business logic actually requires rather than applying the full tree mechanically.

---

## Source-Of-Truth Rules

Every projection path should state one of these models explicitly.

### Event-first

Use this when the event payload already contains everything needed for the append-only record.

```ts
const activity = this.createActivityRecord(state, event, common, "ACTION", {
  user: payload.user_id,
  amount: BigInt(payload.amount),
});
```

### Event plus query confirmation

Use this when the event tells you something happened, but the current summary should come from a query.

```ts
await this.processActivity(state, activity, common);
await this.refreshCurrentState(state, common);
```

### Periodic derived updates

Use this when snapshots or windows should continue to advance on time boundaries.

```ts
if (this.shouldPerformPeriodicUpdates(state, blockTimestamp)) {
  await this.performPeriodicUpdates(state, blockTimestamp, blockNumber);
}
```

Do not mix these models implicitly.

---

## Idempotency And Restart Rules

A production-ready indexer must survive replay and restart.

### Deterministic IDs

Use chain-derived IDs whenever possible.

```ts
const record = new ActivityRecord({
  id: event.args.message.id,
  // ...
});
```

### Rehydrate tracked programs on first run

```ts
if (!this.existingProgramsLoaded) {
  await this.loadExistingPrograms(ctx);
  this.existingProgramsLoaded = true;
}
```

### Combine persisted and pending snapshots before computing windows

```ts
const allSnapshots = [...dbSnapshots, ...Array.from(state.snapshots.values())];
```

### Remove inactive programs from memory only after they are marked inactive for persistence

```ts
if (!state.isActive) {
  state.entity!.isActive = false;
  // save phase will persist the inactive mark
}
```

These rules prevent duplicate records, stale rolling metrics, and lost tracked-program memory after restarts.

---

## What To Reuse Across Projects

These parts are usually reusable almost verbatim:

- `config.ts` environment contract
- `processor.ts` batch processor setup and exported derived types
- `types/gear-events.ts` typed Gear boundary
- `helpers/is.ts` chain event guards
- `sails-decoder.ts` IDL decoder
- `handlers/base.ts` lifecycle contract
- the split between discovery handler and domain projection handler
- the `process -> save` batch flow
- the restart rehydration pattern
- the periodic snapshot update pattern
- the thin PostGraphile GraphQL API pattern
- the explicit frontend-access policy for local GraphQL usage: CORS, proxy, or same-origin

These parts usually need domain adaptation:

- payload interfaces per service event
- current summary entity fields
- append-only activity entity fields
- snapshot entity fields
- query enrichment methods
- calculators for metrics, rankings, or prices

---

## Guardrails

- Do not write a generic command-side backend in place of an indexer.
- Do not let raw Subsquid `Event` objects leak through the whole codebase.
- Do not decode payload prefixes inside handlers when a central decoder exists.
- Do not mix discovery logic with domain projection logic.
- Do not build the SQL schema as a blind mirror of contract storage.
- Do not trust event payloads as canonical current state unless that choice is explicit.
- Do not recompute core domain meaning in `api.ts`; project it earlier and serve it from the database.
- Do not skip restart rehydration, duplicate safety, or replay behavior.
- Do not default to listening to the entire chain unless the broad filter tradeoff is understood and accepted.
- Do not describe the indexer as complete unless a real GraphQL endpoint is mounted at a known path such as `/graphql`.
- Do not rely on terminal-only checks for API reachability; verify browser-facing frontend access as well.
- Do not keep a null, placeholder, or no-op ingestion adapter once the indexer is claimed to ingest chain data.
- Do not leave frontend access strategy implicit when GraphQL is served on a different local origin.
---

## Minimal Build Order

When implementing a new indexer, follow this order:

1. `config.ts`
2. `processor.ts`
3. typed Gear events in `src/types/`
4. `sails-decoder.ts`
5. `schema.graphql`
6. `handlers/base.ts`
7. discovery handler (skip this step for fixed-program topologies)
8. projection handler with rehydration
9. enrichment or calculator services
10. `api.ts`
11. replay and restart verification
12. browser-origin GraphQL verification against the local frontend access path

That order matches the canonical flow above and keeps the project stable while it grows.
