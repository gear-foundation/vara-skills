# Gtest Cheatsheet

## Baseline Flow
1. Create exactly one `System`.
2. Fund the sender before sending.
3. Submit or deploy the program.
4. Send messages and keep their ids.
5. Advance blocks explicitly.
6. Assert logs, mailbox state, reply behavior, and spent value.

## Things To Not Assume
- `send` does not execute the queue immediately.
- The first message is often initialization.
- Time-dependent behavior needs explicit block advancement.
- Program funding and user funding are not interchangeable.

## Sails-First Testing
- Prefer generated clients in `GtestEnv` over hand-authored payload bytes.
- Assert one constructor path and one command/query path in the happy case.
- Add event assertions when the service exposes events.
- Use a deterministic block run mode when the workflow depends on async replies or exits.

## What The Core Skills Should Capture
- The task plan must call out required gtest coverage.
- The implementer should not claim completion without a green local gtest loop.
- The gtest loop skill should summarize failures in a form that is patchable by an agent.
