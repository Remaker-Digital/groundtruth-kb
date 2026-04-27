GO

# GTKB-BRIDGE-POLLER-P2 - Codex Review of Registry REVISED-2

**Status:** GO
**Date:** 2026-04-27
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gtkb-bridge-poller-p2-registry-005.md`

## Claim

GO for the revised static-only P2 registry scope.

The revision addresses the prior NO-GO by removing the unevidenced
harness-PID/session environment variables, deleting heartbeat/liveness behavior,
and making `recording_pid` / `recording_ppid` diagnostic fields rather than
authority fields.

## Evidence

The revised scope removes the disputed pieces from `-003`:

- no heartbeat writer;
- no PID-based liveness checks;
- no process-name allowlist;
- no stale/live classification;
- no `psutil` dependency;
- no claim that `os.getpid()` or `os.getppid()` identifies the durable harness.

The static record shape is now honest about what P2 can know before the P2.5
spike produces live harness evidence.

## GO Conditions

Implementation should preserve these constraints:

1. Code and docs must not describe `recording_pid` or `recording_ppid` as the
   harness PID.
2. Consumers must not treat registry records as live/stale authoritative in P2.
3. Any future liveness interpretation must be gated on P2.5 or equivalent live
   evidence.
4. The Codex hook sample remains explicitly verification-gated on Windows.

## Decision Needed From Owner

None for scoping. The proposed `since_days` default can be handled during
implementation or future owner review if Prime wants a different retention
window.

