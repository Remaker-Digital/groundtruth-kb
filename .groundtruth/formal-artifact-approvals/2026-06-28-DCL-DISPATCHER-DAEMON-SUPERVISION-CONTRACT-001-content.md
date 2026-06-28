## Constraint

GT-KB must supervise the dispatcher daemon through a dedicated
GTKB-DispatcherDaemon Windows scheduled task that runs an idempotent
ensure-alive operation approximately once per minute.

The scheduled task must be separate from storm-watchdog supervision. Its
ensure-alive operation must no-op when the daemon is healthy, restart when the
daemon is absent or stale, and rely on the daemon single-instance lock so the
supervisor cannot create duplicate daemon owners.

## Applicability

This constraint applies to daemon supervision, daemon installation or repair
commands, daemon doctor checks, and release-readiness checks that claim the
dispatcher daemon is supervised.

## Rationale

The daemon itself needs an independent watcher. The storm watchdog and daemon
supervisor address different failure classes; coupling them creates a single
bug domain where a watchdog defect can also remove daemon supervision. The
owner selected a dedicated scheduled task because it mirrors a proven host-local
pattern while preserving daemon single-instance semantics.

## Required Behavior

1. The scheduled task identity is GTKB-DispatcherDaemon or an explicitly
   documented successor approved through the bridge.
2. The task interval is approximately one minute unless a later governed change
   adjusts the SLA.
3. The task invokes an idempotent ensure-alive entrypoint.
4. The ensure-alive path must not dispatch work directly; it only ensures daemon
   process ownership.
5. The supervisor must log or surface restart attempts and failures.
6. Repeated supervisor failures must produce owner-visible alert state rather
   than silently degrading.

## Verification Expectations

- A dry-run or inspection command confirms the scheduled task definition.
- A stopped-daemon test confirms ensure-alive restarts the daemon.
- A healthy-daemon test confirms ensure-alive is a no-op.
- A duplicate-start test confirms the scheduled task cannot bypass the
  single-instance lock.

## Source Decisions

- `DELIB-20266276` D3: dedicated GTKB-DispatcherDaemon scheduled task.
- `DELIB-20266084`: independent heartbeat lesson for daemon death detection.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001`.

