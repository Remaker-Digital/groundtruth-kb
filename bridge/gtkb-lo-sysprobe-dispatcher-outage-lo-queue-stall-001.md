ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 78ae310b-82a3-4023-ba68-acaf32065c31
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task system-statusprogress-check; resolved role loyal-opposition

bridge_kind: governance_advisory
Document: gtkb-lo-sysprobe-dispatcher-outage-lo-queue-stall
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-07-31 UTC

## Source

Scheduled system status/progress probe (`system-statusprogress-check`),
2026-07-31, session context `78ae310b-82a3-4023-ba68-acaf32065c31`. Evidence
from `gt bridge dispatch health`, `gt bridge dispatch status`,
`gt bridge dispatch daemon status`, `gt bridge state-report`,
`Get-ScheduledTask`, and `.gtkb-state/bridge-poller/`. WI-5092 covers the
*misleading health display* while the daemon is down; it does not cover the
outage itself or the resulting queue stall.

## Claim

Bridge dispatch automation has been down for approximately 12 days, its
scheduled task is Disabled, and the Loyal Opposition actionable queue has
accumulated 26 items that no automated path is draining.

## Evidence

Daemon state:

| Aspect | Value |
| --- | --- |
| Mode | live |
| Active substrate | `dispatcher_daemon` |
| Running | **False** |
| Last heartbeat | 2026-07-19T20:52:37Z |
| Heartbeat age | 1,032,262 s (~11.9 days) |
| `GTKB-DispatcherDaemon` task | **Disabled** |
| `GTKB-DbSnapshot` task | **Disabled** |
| Operator quiesce | expired |

`gt bridge dispatch health` returns FAIL overall:

- `complex_lifecycle: WARN` — daemon not running; supervisor scheduled task
  state is `Disabled`, expected `Ready` or `Running`.
- `git_lock_health: FAIL` — `E:\GT-KB\.git\index.lock` held 11,589 s.
- `routing_config: WARN` — `loyal-opposition:D` stale failure evidence with
  `pending_count=2`; latest run
  `2026-07-19T20-22-25Z-loyal-opposition-D-fae3bc`
  `failure_class=subprocess_execution_failed exit_code=1`.

The `operator quiesce` is *expired*, so the outage is not an active
owner-directed pause. Note that `GTKB-DbSnapshot` being Disabled means the
disaster-recovery snapshot path is also inactive.

Resulting queue state from `gt bridge state-report` (2,405 threads total):

| Status | Count |
| --- | --- |
| VERIFIED | 1,733 |
| WITHDRAWN | 244 |
| NO-GO | 167 |
| GO | 121 |
| ADVISORY | 100 |
| NO-ACTION | 24 |
| DEFERRED | 4 |
| UNKNOWN | 10 |
| NEW | 2 |

**LO-actionable: 26** — 24 `NO-ACTION` plus 2 `NEW`
(`gtkb-wi5428-codex-hook-parity-restoration`,
`gtkb-wi5808-harness-probe-glm52-r3`).

The 24 `NO-ACTION` items are the material finding. Per
`DCL-NO-ACTION-STATUS-SEMANTICS-001`, `NO-ACTION` is Prime Builder rejecting an
LO verdict as governance-non-compliant and routing the thread *back* to LO for a
corrected verdict. Twenty-four simultaneous instances is not a set of unrelated
one-offs; it indicates LO verdicts are being produced in a form Prime Builder
systematically rejects. Affected threads include
`gtkb-wi5659-checker-verified-evidence-prefilter-030.md` (30 versions),
`gtkb-wi5166-modernization-nonimpairment-enforcement-017.md`, and
`gtkb-wi5172-canonical-carrier-nonauthority-evaluator-017.md` — high version
counts consistent with repeated failed verdict cycles.

Dispatch-failure telemetry: `.gtkb-state/bridge-poller/dispatch-failures.jsonl`
is 844 KB current with five rotations of ~10 MB each (~52 MB retained). The
most recent 400 KB contains only `dispatch_role_mismatch_authorized` (28
occurrences) under `run_id` values `test-run-001`, `test-run-002`, and
`test-relay-isolation` — test-harness traffic is being written into the
production dispatch-failure log, most recently 2026-07-31T16:42:17Z.

Dispatchable LO candidates D (ollama) and F (openrouter) recorded zero MemBase
writes in the trailing 7 days, consistent with the daemon outage.

## Risk / Impact

- The two-axis automation model in `.claude/rules/bridge-essential.md` has no
  live AXIS-1 substrate; all dispatch has silently reverted to the manual
  fallback without an owner directive establishing that state.
- 26 LO-actionable items cannot drain, and 24 of them are already
  round-tripping.
- The stale `.git/index.lock` blocks the `VERIFIED` commit-finalization path,
  which is the terminal step of the bridge protocol. Detection of this exact
  condition is already backlogged as WI-5819; this advisory records that the
  condition is *currently live* and is compounding the dispatch outage.
- Test traffic in the production failure log corrupts the evidence surface used
  to diagnose real dispatch failures.
- `GTKB-DbSnapshot` Disabled means no current DR snapshot cadence.

## Owner Decision Needed

Whether the ~12-day daemon outage and the Disabled scheduled tasks are
intentional or a fault. This determines whether disposition is "restore" or
"formalize the quiesce". The probe found expired quiesce state and no
authorizing directive, but cannot rule out an out-of-band owner decision.

## Recommended Prime Action

1. Establish whether the daemon outage is intentional. If not, restore
   `GTKB-DispatcherDaemon` and confirm heartbeat; if so, record the directive
   and reconcile `operator-quiesce.json`.
2. Clear the stale `.git/index.lock` (no live `git` process was observed;
   0-byte lock created 2026-07-31T09:21:28 local) to unblock `VERIFIED`
   finalization. Coordinate with WI-5819.
3. Triage the 24 `NO-ACTION` threads as a class, not individually — identify
   the shared governance defect in the LO verdict form that Prime Builder is
   rejecting.
4. Separate test-run dispatch telemetry from the production
   `dispatch-failures.jsonl`, and set a retention policy for the ~52 MB of
   rotations.
5. Determine the disposition of `GTKB-DbSnapshot` (Disabled).
6. Investigate `loyal-opposition:D` `subprocess_execution_failed exit_code=1`
   before relying on D as a dispatch target; note WI-5439 already records that
   the Ollama D substrate has no reboot autostart.

## Classification Slot

`adapt`.

This advisory is not implementation approval. It does not authorize protected
edits, does not open an implementation-start packet, and does not bypass the
Prime Builder proposal, Loyal Opposition `GO`, or verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

## Prior Deliberations

_No prior deliberations: <fill in reason before filing>._
