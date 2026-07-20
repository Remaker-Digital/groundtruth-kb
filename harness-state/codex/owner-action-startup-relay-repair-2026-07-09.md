# Owner Action: Startup Relay Repair

## Context

On 2026-07-09, the Codex interactive `::init gtkb pb` handler reached the
startup-disclosure relay path and failed closed. The selected Prime Builder
cache and sidecar had matching hashes, but their `generated_at` timestamp was
outside the freshness window and the bounded refresh did not complete.

## Owner Decision

Mike authorized: `file startup repair`.

## Authorized Next Step

Create and route a derived implementation proposal that restores bounded
startup-relay refresh for Codex without bypassing cache freshness or integrity
checks. The proposal must include a focused regression test and follow the
ordinary independent Loyal Opposition review cycle before implementation.
