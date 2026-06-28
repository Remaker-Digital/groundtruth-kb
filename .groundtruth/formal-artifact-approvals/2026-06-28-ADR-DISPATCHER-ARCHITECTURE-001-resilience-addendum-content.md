## Context

GT-KB dispatch previously suffered a harness-hook-triggered storm on 2026-06-25:
`cross_harness_bridge_trigger.py` fired from every harness PostToolUse/Stop hook,
creating a self-feeding worker -> trigger -> worker loop. The trigger stripped
`GTKB_NO_CROSS_HARNESS_TRIGGER` from spawned workers, so neither that kill switch
nor a host restart could stop the loop. Dispatcher-config intervention was
required to quiesce the system.

Owner decisions `DELIB-20265882` and `DELIB-20265888` established the dispatcher
target architecture: dispatch is a GT-KB-owned black-box service; harnesses are
consumers only; dispatch is triggered by artifact deposit plus explicit
ownership release; harnesses must not trigger dispatch, select targets, choose
timing, or suspend each other.

The daemon foundation and PHASE-Y daemon go-live decisions were later recorded
in `DELIB-20266084` and `DELIB-20266272`. The daemon-resilience scope-lock in
`DELIB-20266276` now adds the reliability constraints required before the full
fleet is considered resilient under maximum reasonable load.

## Decision

GT-KB dispatch remains a persistent daemon-owned black-box service. The daemon
architecture is extended with the following resilience addendum:

1. Exactly one live GTKB-DispatcherDaemon instance may own queue state,
   dispatch decisions, worker lifecycle tracking, liveness state, and recovery
   decisions for a project root at a time.
2. A dedicated Windows scheduled task named GTKB-DispatcherDaemon is the daemon
   supervisor. It runs the idempotent ensure-alive path roughly once per minute:
   no-op when the daemon is healthy, restart when absent or stale, and never
   bypass the daemon single-instance lock.
3. The daemon must self-heal the failure modes selected in `DELIB-20266276`:
   daemon death, worker hang, worker crash, spawn storm, corrupt daemon state,
   harness saturation, and provider outage.
4. Full auto-recovery is the steady-state posture. Owner action is not required
   for ordinary recovery loops.
5. When retries are exhausted for one component, the daemon keeps the fleet in a
   degraded-but-operating mode by disabling only the failing component,
   surfacing a visible owner alert, and continuing dispatch across healthy
   components.
6. The maximum reasonable load target is fleet saturation with one worker per
   harness: two Prime Builder workers and four Loyal Opposition workers when the
   six-harness topology from `DELIB-20266276` is active.
7. Load and chaos verification for the daemon uses deterministic STUB workers;
   real harnesses receive limited smoke checks only.
8. Prime Builder routing under the two-PB topology is selected by dispatcher
   ranking, not by affinity. Both Prime Builder harnesses are stateless
   implementation consumers.

## Rationale

The prior architecture removed harnesses from the dispatch control plane, but a
persistent daemon is not sufficient by itself. A daemon that can die silently,
spawn duplicate owners, lose corrupt state, or halt the entire fleet for one
provider outage would preserve the harness-isolation shape while failing the
owner's reliability goal.

The resilience addendum keeps the architecture conservative: one owner of the
queue, one external supervisor, local self-healing first, degraded continuity
when a component fails, deterministic tests for expensive or destructive failure
modes, and no new harness influence over routing or suspension.

## Failed Approaches

| Approach | Why it failed |
| --- | --- |
| Harness-hook event-driven trigger | Produced the 2026-06-25 dispatch storm and violates harness isolation. |
| Manual owner restart for daemon death | Fails the `DELIB-20266276` full auto-recovery decision. |
| Multiple daemon instances for redundancy | Violates single-writer queue ownership unless a later governed design adds distributed coordination. |
| Halt whole fleet on one component failure | Fails the alert-and-degrade escalation decision in `DELIB-20266276`. |
| Real harness load/chaos tests for all failure modes | Too costly and non-deterministic; `DELIB-20266276` selects STUB load/chaos plus real smoke. |

## Consequences

### Positive

- Gives downstream implementation phases citable daemon-resilience constraints.
- Preserves the black-box dispatcher architecture while adding operational
  recovery expectations.
- Keeps owner burden focused on decisions and alerts, not routine daemon repair.
- Enables cheap, repeatable verification through deterministic STUB workers.

### Negative

- Requires follow-on implementation work for supervisor task creation, recovery
  state, component circuit breakers, and load/chaos tests.
- Some requirements are Windows-host-local because the selected supervisor is a
  Windows scheduled task.
- Degraded continuity intentionally permits reduced capacity during component
  outage rather than treating all capacity loss as a hard stop.

### Risks

- Over-eager auto-recovery can create churn if liveness checks are too shallow.
  Mitigation: recovery decisions must use explicit liveness and stale-state
  semantics, not process existence alone.
- Duplicate daemon ownership can corrupt queue state. Mitigation: single-instance
  lock is mandatory and must be enforced by both daemon and supervisor paths.
- Owner alerts can become noise. Mitigation: alert only when automatic retries
  are exhausted or degraded state persists beyond the relevant SLA.

## Alternatives Considered

| Alternative | Why rejected |
| --- | --- |
| Keep manual recovery as normal operations | Conflicts with the full auto-recovery owner decision. |
| Fold supervisor behavior into the storm watchdog | A watchdog defect could also take down daemon supervision; `DELIB-20266276` selected a dedicated task. |
| Add PB affinity for GO implementation routing | Conflicts with the "either PB by dispatcher ranking" decision and stateless worker model. |
| Test real harnesses under full chaos/load | Higher cost and lower determinism than the selected STUB load/chaos plus real smoke model. |

## Related Specs / Deliberations

- `DELIB-20265888` - owner harness/dispatch isolation architecture.
- `DELIB-20266084` - dispatcher daemon foundation authorization.
- `DELIB-20266272` - PHASE-Y full daemon go-live.
- `DELIB-20266276` - daemon-resilience program scope-lock.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - centralized dispatch service.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001`.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001`.
- `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001`.
- `DCL-HARNESS-DISPATCH-ISOLATION-INVARIANT-001`.

