# Gear Gas Reservations And Waitlist

## When To Reserve Gas

- Reserve gas when the design needs to preserve execution budget for future work across blocks.
- Typical cases are delayed recovery flows, self-messaging that must survive later execution, or async paths that resume after waiting.
- Reservation is not free, permanent, or a value transfer. It is a bounded gas budget tied to duration and usage.

## Reservation Rules

- Create a reservation with an explicit amount and duration.
- Treat the reservation lifetime as part of the architecture, not an implementation footnote.
- Consuming, expiring, or unreserving the reservation changes what later messages can still do.
- Reusing an expired or already-consumed reservation id is a real failure mode and should be tested.

## Waitlist Model

- The Waitlist is on-chain storage for messages that are waiting on conditions or later processing.
- Waitlisted messages are not a free parking lot and are not a normal mempool.
- Waitlist storage incurs rent or locked-fund cost over time, has expiry behavior, and is bounded by maximum duration rules.
- Designs that rely on indefinite prolonging of waitlisted messages are wrong.

## Delayed Work Design

- Prefer delayed messages when the program must revisit state in a later block.
- Pair delayed execution with reservation only when the later path really needs preserved gas.
- Do not describe delayed automation as off-chain cron unless an off-chain agent is explicitly part of the design.

## Testing And Accounting

- In `gtest`, block advancement determines whether delayed work or expiry actually happens.
- Use `spent_value` and related accounting assertions when gas burn or attached value affects behavior.
- Keep sender funding, attached value, and existential-deposit constraints in the same reasoning frame.

## Failure Signatures

- Invalid or expired reservation id
- Timeout followed by later side effects
- Balance assertions that ignore gas burn or ED behavior
- Waitlist assumptions that ignore rent, expiry, or maximum duration
