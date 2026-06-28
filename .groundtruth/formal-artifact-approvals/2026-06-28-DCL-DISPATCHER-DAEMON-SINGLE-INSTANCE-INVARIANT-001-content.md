## Constraint

For a given GT-KB project root, exactly one live GTKB-DispatcherDaemon instance
may own dispatch queue state, worker lifecycle state, dispatch decisions,
liveness state, and recovery decisions at any time.

The daemon and every supervisor or ensure-alive path must acquire and honor the
same single-instance lock before starting or resuming daemon ownership. If a
candidate daemon cannot acquire the lock, it must exit without modifying queue,
worker, health, or recovery state.

## Applicability

This constraint applies to:

- `scripts/gtkb_dispatcher_daemon.py` or successor daemon entrypoints.
- scheduled-task supervision for GTKB-DispatcherDaemon.
- any CLI command that starts, restarts, recovers, or ensures the daemon.
- any future daemon state migration or checkpoint recovery path.

It does not prohibit multiple harness workers. It prohibits multiple daemon
owners of the same queue and recovery state.

## Rationale

The dispatcher daemon is the single dispatch control plane. Duplicate daemon
owners can double-dispatch bridge work, corrupt state files, race worker reaping,
or create contradictory recovery decisions. The owner-approved architecture keeps
harnesses as consumers only; single daemon ownership is the corresponding
control-plane invariant.

## Required Behavior

1. A daemon start path must fail closed when the single-instance lock is held by
   a live daemon.
2. A stale lock may be recovered only through a liveness-aware recovery path that
   distinguishes a dead owner from a slow but live daemon.
3. Supervisor loops must be idempotent: healthy daemon means no-op; absent or
   stale daemon means attempt restart through the same lock.
4. State mutation before lock acquisition is prohibited.
5. Diagnostic status must expose whether the lock owner is healthy, stale, or
   absent.

## Verification Expectations

- A unit or integration test proves a second daemon start cannot acquire
  ownership while the first daemon is healthy.
- A stale-lock or dead-owner test proves recovery can restart the daemon without
  allowing simultaneous owners.
- A status test proves the daemon reports owner health accurately enough for the
  supervisor and recovery paths.

## Source Decisions

- `DELIB-20266276` D2: full auto-recovery, all modes.
- `DELIB-20266276` D3: dedicated scheduled-task supervision using the existing
  single-instance lock.
- `ADR-DISPATCHER-ARCHITECTURE-001`: daemon owns dispatch queue and decisions.

