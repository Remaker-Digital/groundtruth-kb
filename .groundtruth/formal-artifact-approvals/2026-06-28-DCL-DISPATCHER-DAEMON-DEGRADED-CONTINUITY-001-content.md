## Constraint

When automatic recovery exhausts retries for a component, the dispatcher daemon
must disable or circuit-break only the failing component, raise visible owner
alert state, and continue dispatching across the healthy remainder of the fleet
when doing so is safe.

The daemon must not silently halt the entire fleet for one component failure,
and it must not silently continue without surfacing the degraded condition.

## Applicability

This constraint applies to harness-specific provider outages, repeated worker
crashes, repeated timeout failures, daemon-supervisor failures, state recovery
failure, and any future component-level failure that can be isolated from the
rest of the dispatch fleet.

## Rationale

The owner selected "alert + keep fleet degraded" as the escalation policy.
That policy preserves owner visibility without making the owner part of the
steady-state recovery loop and prevents one unhealthy component from stopping
all dispatch when healthy alternatives exist.

## Required Behavior

1. Component failure must be isolated to the narrowest safe component boundary.
2. Healthy components remain eligible when dispatch can safely continue.
3. Degraded state must be visible in daemon status and next-session reporting.
4. A bridge ADVISORY entry or successor owner-visible alert must be created when
   retries are exhausted and degraded state persists.
5. Recovery from degraded state must be explicit and auditable.
6. Degraded operation must still respect role eligibility, dispatch caps, and
   project authorization.

## Verification Expectations

- A simulated failing LO harness causes that harness to be circuit-broken while
  other LO harnesses remain eligible.
- A simulated failing PB harness in a two-PB topology reroutes GO implementation
  work to the other eligible PB when policy permits.
- A simulated all-role-unavailable condition stops dispatch safely and surfaces
  a visible owner alert.
- Status output distinguishes healthy, degraded, and blocked.

## Source Decisions

- `DELIB-20266276` D4: alert plus keep fleet degraded.
- `DELIB-20266276` D6: either PB by dispatcher ranking.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`: one centralized dispatch service
  resolves targets from the registry and records dispatch evidence.

