# SCALE Binary Decoding Guide

Use this guide when a builder has raw bytes, hex payloads, replies, event data, or state outputs and is not sure which decoding path is correct.

## Default Rule

Start by identifying the source of the bytes before choosing a decoder.

Do not start with plain `Decode::<T>` on arbitrary bytes when the source may be a routed Sails payload or a metadata-driven state read.

## First Classify The Bytes

Before decoding, identify all of the following:

- source:
  - constructor payload
  - service command payload
  - service query reply
  - event payload
  - full state output
  - state function output
  - raw mailbox or system message
- framing:
  - Sails route-framed
  - plain SCALE
  - metadata-driven state output
- artifact:
  - `.idl`
  - generated Rust or TypeScript client
  - `ProgramMetadata`
  - `state.meta.wasm`
- version:
  - confirm the `.idl`, metadata, or state meta comes from the same build or release as the bytes you are decoding

## Preferred Decode Order

Use this order unless the task explicitly requires a lower-level path:

1. Generated Sails client
   - Default for standard Sails constructors, service calls, replies, and events.
   - Prefer this when the workspace already has generated Rust or TypeScript client code.

2. Runtime Sails IDL parsing
   - Use `parseIdl` only when dynamic runtime control is explicitly needed.
   - This is the dynamic fallback for Sails interface-driven decoding.

3. `api.programState.read` with `ProgramMetadata`
   - Use for full state reads.

4. `api.programState.readUsingWasm` with `state.meta.wasm`
   - Use for state-function outputs and state-conversion flows.

5. Metadata-driven low-level decode
   - Use when the task is explicitly about raw Gear metadata or hex decoding.
   - Match the exact type and metadata artifact before decoding.

6. Plain `Decode::<T>`
   - Use only when the bytes are known to be a bare SCALE payload with no Sails routing layer and no metadata-driven transformation layer.

## Sails-Routed Bytes

For a standard Sails app, do not assume constructor, service, reply, or event bytes are just a bare business DTO.

Sails uses route-prefixed SCALE encoding for service and method routing. The generated client handles this transparently. When debugging raw bytes, the leading bytes are SCALE-encoded service and method name strings, not the bare business DTO.

If the path involves a Sails route, decode with the generated client or another Sails-aware IDL path first.

Only decode as a bare struct after you have explicitly confirmed that:
- the bytes are not carrying Sails routing framing, or
- the routing layer has already been handled by the tool you are using

## State Reads

Treat these as different decode problems:

- full state read:
  - `api.programState.read`
  - decode with `ProgramMetadata`

- state function or state-conversion output:
  - `api.programState.readUsingWasm`
  - decode with `state.meta.wasm`

Do not use `.idl` to decode full raw program state unless the task explicitly proves that the output type is coming from a Sails interface path rather than Gear metadata/state tooling.

## Raw Gtest And Byte-Level Debugging

When a test drops below generated clients:

- identify whether the payload or reply is Sails-routed or plain SCALE
- inspect the source of the bytes before decoding logs
- prefer Sails-aware helpers when the test is not intentionally validating raw framing
- use plain SCALE decode only when the test is explicitly about a non-routed payload body

## Metadata Fallback

`gear-meta` can still be useful as a debugging fallback for manual hex encode or decode work.

But it is not the preferred long-term default.
Prefer current metadata access paths first when the repo or toolchain already exposes them.

## Never Do These By Default

- Do not decode arbitrary Sails replies with plain `Decode::<T>` before checking for routing framing.
- Do not decode full state bytes with `.idl` when the correct path is metadata-based.
- Do not decode state-function output with full-state metadata when the correct artifact is `state.meta.wasm`.
- Do not mix artifacts from different builds or releases.
- Do not switch to manual hex decoding when a generated client already exists and matches the deployed interface.
