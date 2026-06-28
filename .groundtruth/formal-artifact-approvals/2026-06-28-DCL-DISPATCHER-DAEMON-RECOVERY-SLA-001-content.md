## Constraint

The dispatcher daemon must provide automatic recovery behavior for the failure
modes selected in `DELIB-20266276`, with bounded recovery expectations that are
measurable by tests or operational probes.

## Applicability

This constraint applies to daemon liveness monitoring, worker lifecycle
management, state checkpointing, harness saturation handling, provider
circuit-breaking, and dispatch retry logic.

## Required Recovery SLAs

| Failure mode | Required recovery behavior | Recovery expectation |
| --- | --- | --- |
| Daemon death | Scheduled supervisor restarts through ensure-alive. | Restart within roughly one supervisor interval plus startup time. |
| Worker hang | Daemon kills the worker at the configured lifetime cap and re-dispatches eligible work when safe. | Recovery begins immediately after lifetime-cap expiry. |
| Worker crash | Daemon reaps the crashed worker, records the failure, and re-dispatches eligible work when safe. | Recovery begins on the next daemon lifecycle sweep. |
| Spawn storm | Watchdog or daemon recovery reaps runaway workers and suppresses further unsafe spawning. | Recovery begins within one watchdog or daemon recovery cycle. |
| Corrupt daemon state | Daemon resets to the latest known-good checkpoint or safe empty state with audit evidence. | Recovery begins on detection; no silent use of corrupt state. |
| Harness saturation | Daemon backs off and does not exceed the per-harness one-worker cap. | Backoff applies immediately when saturation is detected. |
| Provider outage | Daemon circuit-breaks or suppresses the failing provider/harness and reroutes to eligible healthy alternatives. | Reroute begins after failure threshold is met. |

The system must not require owner action for ordinary recovery within these
modes.

## Rationale

The owner selected full auto-recovery for all listed modes. Recovery SLAs turn
that decision into testable constraints so later implementation phases cannot
claim resilience merely because a daemon process exists.

## Required Behavior

1. Each failure mode must have explicit detection and recovery logic.
2. Each recovery decision must leave enough audit evidence to diagnose what
   happened.
3. Recovery must respect the daemon single-instance invariant and the harness
   isolation invariant.
4. Recovery must not silently abandon bridge work. Work is either completed,
   re-dispatched, parked with evidence, or escalated visibly.
5. Recovery tests must prefer deterministic STUB workers for load and chaos
   cases, with real harness smoke checks only.

## Verification Expectations

- Deterministic STUB tests cover hang, crash, corrupt output or state, and load
  saturation without spending real provider calls.
- Real harness smoke tests prove the recovery pathway still composes actual
  harness commands at least once per harness class.
- Status or health commands expose enough state to tell healthy, degraded, and
  blocked recovery apart.

## Source Decisions

- `DELIB-20266276` D1: fleet-saturation load target.
- `DELIB-20266276` D2: full auto-recovery, all modes.
- `DELIB-20266276` D5: STUB load and chaos; real smoke only.

