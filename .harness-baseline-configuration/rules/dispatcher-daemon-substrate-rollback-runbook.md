# RETIRED — Dispatcher Daemon Incident Runbook

This runbook operated the legacy dispatcher daemon. **The legacy dispatcher is
deliberately disabled and is being purged** (owner directive, 2026-08-16), so
the procedure it described has no live subject and has been removed rather than
annotated.

Nothing here is current direction. Do not restore the daemon, its health checks,
its dispatchability toggles, or any other automated dispatch substrate.

## Current state

Bridge dispatch is **manual owner assignment**. Dispatcher Next is the single
future dispatcher and is not yet activated.

Authority: `{{HARNESS_RULES_DIR}}/bridge-essential.md` § Operational Mode.

This stub remains only so the path does not 404 for consumers that still
reference it. It should be removed once those references are purged; removal is
a governed deletion, not something to perform incidentally.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
