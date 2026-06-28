## Constraint

Harnesses must not trigger dispatch, choose dispatch targets, influence dispatch
timing, suspend or resume dispatch to another harness, or observe another
harness except through the governed registry and shared GT-KB artifacts.

Dispatch is triggered by daemon-observed artifact deposit plus explicit
ownership release. GT-KB owns the black-box harness-equivalence-maintainer
service, and that service is invisible to harnesses.

## Applicability

This constraint applies to all AI coding harnesses registered in GT-KB, all
headless worker launch paths, all dispatcher or daemon trigger paths, all
kill-switch or eligibility controls, and any future harness-equivalence or
quality-ranking service.

## Rationale

The 2026-06-25 dispatch storm was caused by harness hook behavior feeding the
dispatch control plane. The owner corrected the architecture: harnesses are
consumers of work and producers of artifacts, not dispatch controllers.

The daemon-resilience program must preserve this separation even while adding
auto-recovery, component circuit breakers, and two-Prime-Builder routing. Those
capabilities belong to GT-KB's daemon and governed registry, not to individual
harness sessions.

## Required Behavior

1. A harness session must not spawn another dispatch worker directly.
2. Harness hooks must not be the canonical dispatch trigger.
3. Harnesses must not set another harness's dispatch eligibility or suspension
   state.
4. Harnesses must not select their own replacement or counterpart for a bridge
   thread.
5. Harnesses may read governed registry state through canonical reader
   surfaces, but that read does not grant dispatch-control authority.
6. Dispatch target, timing, ranking, and degraded rerouting are daemon/registry
   decisions.
7. Any harness-equivalence-maintainer service is GT-KB-owned and
   harness-invisible.

## Verification Expectations

- Static or runtime checks prove canonical dispatch no longer depends on
  harness PostToolUse/Stop hooks.
- Dispatcher config or control commands reject harness-originated attempts to
  suspend another harness outside governed owner/daemon authority.
- Tests prove artifact deposit plus ownership release is the dispatch trigger
  model for the target architecture.
- Tests prove PB routing chooses by dispatcher ranking rather than harness
  affinity.

## Source Decisions

- `DELIB-20265888`: harness/dispatch isolation architecture and invariants
  1-8.
- `DELIB-20266276` D0: two PB plus four LO topology.
- `DELIB-20266276` D6: either PB by dispatcher ranking.
- `ADR-DISPATCHER-ARCHITECTURE-001`: daemon-owned dispatch black box.

