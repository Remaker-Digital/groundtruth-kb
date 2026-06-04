## Status

proposed.

## Context

GT-KB has two bridge-dispatch substrates (cross-harness event-driven trigger; single-harness dispatcher), mutually exclusive at runtime and both bridge-INDEX-driven only. There is no path to dispatch a scheduled/calendar-based task or an arbitrary payload to a chosen {harness, role}. Recurring admin/review/audit work therefore falls on the owner or ad-hoc sessions, counter to operating-model.md §1 and DELIB-S312.

## Decision

Introduce one centralized dispatch service plus a first-class envelope abstraction. An envelope is a MemBase record `{cadence, target (harness-id OR role), payload_ref, specialization_ref, authorization, activity_gate, expiry}`. The service resolves the target via harness-state/harness-registry.json (invocation_surfaces.headless.argv + `::init gtkb (pb|lo)`), enforces singleton dispatch via the existing dispatch-state/lock discipline, and fires envelopes on schedule only after an activity-gate self-check returns work-to-do.

## Rationale

Consolidating dispatch behind one service plus a typed envelope abstraction eliminates duplicated logic between the existing event-driven trigger and the single-harness dispatcher, preserves the S308 lesson by requiring an activity gate before any schedule-driven fire, and gives recurring ops/review/audit work a governed home (operating-model.md §1, DELIB-S312). The envelope's mandatory authorization and activity-gate fields make scheduled firing safe by default: dispatch is refused without owner-evidence (PAUTH/DELIB) and without a positive read-only predicate.

## Alternatives Considered

- (a) Keep ad-hoc interactive dispatch — REJECTED: leaves recurring load on owner; violates the deterministic-services principle.
- (b) Re-enable an interval OS poller — REJECTED: reintroduces the S308 blind-automation failure mode; forbidden by bridge-essential.md.
- (c) A third independent substrate — REJECTED: worsens existing dual-substrate complexity; this ADR consolidates instead.
- (d) Mint new authority roles for specializations — REJECTED: the authority role set is closed (`prime-builder`/`loyal-opposition`; `acting-prime-builder` SET-rejected); specialization is a `specialization_ref` (skill/lane/subagent), not a new role.

## Consequences

- (+) Recurring ops/review/audit become governed idempotent services.
- (+) Consolidates two substrates toward one singleton dispatch path.
- (-) Reintroduces scheduled firing, which MUST be activity-gated to preserve the S308 lesson.
- (-) New MemBase schema + service code to maintain.

## Related

`ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`, `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `DELIB-S312`, `WI-4281`.
