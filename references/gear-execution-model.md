# Gear Execution Model

## Core Rules

- Gear and Vara programs are isolated actors with private state.
- State changes happen only while a program handles one incoming message.
- Sending a message enqueues work and returns a message id; it does not execute the queue immediately.
- The runtime drains the global message queue during block execution, so time and ordering are block-shaped concerns.
- In `gtest`, the first message to a program is often initialization and still requires explicit block execution.

## Message Lifecycle

1. A program enters `handle`, `handle_reply`, or another valid entrypoint for the current message.
2. It reads context such as source, value, payload, and prior reply linkage.
3. It stages outbound sends, replies, events, or delayed work while execution is still in progress.
4. The runtime materializes those outbound effects only after the current execution completes successfully.

## Successful Execution And Rollback

- A successful execution commits state changes and materializes staged outbound messages, replies, and events.
- A panic or unrecoverable failure rolls back the current message execution, including state updates and staged outbound effects.
- Sails events follow the same rule because they are ordinary messages under the hood. If the command rolls back, the expected event is absent.
- This rollback boundary matters for design: mutate-before-send logic is safe only if failure panics and reverts the message.

## Builder Implications

- Model multi-step workflows as distributed transactions across messages, not as one atomic call stack.
- Name actors, commands, queries, replies, events, and failure paths in specs before implementation starts.
- Use delayed messages for future block work when the program really must revisit state later.
- Use gas reservation only when future work needs a preserved execution budget across blocks.
- Prefer generated Sails clients for normal app paths so route prefixes and reply decoding stay aligned with the program contract.

## Validation Implications

- Advance blocks explicitly in `gtest`; `send` alone is not execution.
- Assert effects after the block that should have produced them.
- When smoke-testing against a local node, use the real deployed program id and observe the same async message boundaries you modeled in tests.

## Program Lifecycle

1. **Upload code** — submit compiled Wasm to the network. The runtime validates the Wasm is well-formed and stores the code blob identified by its code hash.
2. **Create program** — send an init message that instantiates a program from the validated code. The runtime allocates state and runs the init handler.
3. **Active** — the program handles messages, mutates state, stages outbound sends, and emits events. Balance must stay above the existential deposit.
4. **Exit** — the program calls `gr_exit` to terminate, or init fails and the program is never activated. Locked deposit is released on exit.

A program that runs out of balance or is not accessed for the initial rent period risks being paused or removed by the rent system.

## Rent

- Programs occupy on-chain state and must maintain at least the existential deposit (~1 VARA on mainnet).
- The initial rent period is approximately 173 days (5,000,000 blocks on Vara Network).
- If a program's balance drops below the threshold and the rent period expires, the program may be removed from active state.
- For long-lived programs, ensure the account is topped up periodically or funded sufficiently at creation.
