# Gear Messaging And Replies

## Send And Reply Families

- Use encoded send and reply APIs for normal SCALE-encoded payload types.
- Use bytes variants only when debugging route or codec mismatches, or when a raw transport path is intentional.
- Use delayed variants when execution must happen in a future block.
- Use reservation-backed variants when later execution needs preserved gas.
- Use staged payload flows only when the payload must be built incrementally.

## Message Lifecycle Checklist

1. Choose the payload style: typed, bytes, or forwarded input.
2. Choose delivery mode: immediate, delayed, explicit gas, or reservation-backed.
3. Choose interaction pattern: fire-and-forget or `for_reply`.
4. Choose reply mode: one-shot reply or staged push-plus-commit.

## Async `for_reply` Flows

- `for_reply` flows wait on a reply-producing message and return a future.
- Timeouts are a distinct outcome and should be handled separately from error replies.
- A reply hook needs non-zero reply deposit to register.
- A timed-out future does not guarantee the reply hook never runs later if the reply eventually arrives.

## Staged Payload Rules

- A staged send or reply is incomplete until its matching commit step runs.
- If a code path pushes payload pieces but never commits, the staged payload is dropped.
- Keep staged flow use narrow; it is easier to miss a commit than with one-shot replies.

## Context-Specific Semantics

- Reply metadata belongs in reply-handler context only.
- Signal metadata belongs only in signal-handler context where that entrypoint is supported.
- Do not assume a generic message handler can safely read reply or signal context APIs.

## Sails Routing Notes

- Generated Sails clients encode the correct service and method route prefixes for you.
- If a payload uses the wrong route prefix, decode fails even when the payload body type is otherwise correct.
- Treat generated clients as the default path and use low-level byte encoding only to isolate transport or codec bugs.

## Guardrails

- Outbound send and reply effects appear only after successful execution.
- Handle timeout, transport failure, and error reply as different branches.
- Always close staged payload paths with the correct commit call.
