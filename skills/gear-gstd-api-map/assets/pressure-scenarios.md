# Pressure Scenarios

## Scenario 1

A builder wants a program to send work to another actor, wait for a reply, and time out cleanly if the reply is late.

Expected guidance:
- start in `gstd::msg`
- prefer typed `_for_reply` helpers over raw bytes unless codec debugging is the point
- call out reply deposit and timeout handling as separate design concerns
- trace the flow to `gcore::msg` and the reply-related `gr_send*` plus reply-hook machinery only if needed

## Scenario 2

A feature needs to schedule work for a future block and guarantee gas is still available when that work resumes.

Expected guidance:
- model delayed execution first
- add reservation only if the later path truly needs preserved gas
- point to `ReservationId::reserve`, `send_delayed`, reservation-backed send or reply variants, and the waitlist or expiry constraints
- mention `gr_reserve_gas` and delayed send syscalls only as a secondary confirmation layer

## Scenario 3

An architecture note needs to decide whether a factory program should create child programs and optionally await the init reply.

Expected guidance:
- start in `gstd::prog`
- choose between bytes and encoded create helpers based on the contract
- mention delayed or gas-explicit create variants when relevant
- trace to `gcore::prog` and `gr_create_program` or `gr_create_program_wgas` only when confirming low-level behavior
