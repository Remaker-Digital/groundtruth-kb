ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: a9243194-6d33-4c8e-b28c-0f6a9fed084f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition
author_metadata_source: session runtime

# LO Advisory - The Advisory Router Silently Starves: Slug-Keyed Dedup Has Frozen The Advisory Corpus At Version 001, Stranding The P0 Root Cause Where No Owner Will See It

bridge_kind: governance_advisory
Document: gtkb-lo-advisory-router-slug-dedup-starvation-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5424

---

## Source

Read-only observation during a scheduled Loyal Opposition queue run in session
`a9243194-6d33-4c8e-b28c-0f6a9fed084f`, branch `research`, HEAD `1c82158e8`,
2026-07-28 UTC. The LO queue was empty, so this run produced no verdicts; this
finding comes from the surrounding state.

Evidence surfaces: `scripts/advisory_backlog_router.py` (read in full),
`.gtkb-state/advisory-candidates/candidates.jsonl` (238 records),
`.gtkb-state/advisory-router/last-scan.json`, `groundtruth.db`
(`current_work_items`), `gt deliberations search`, `gt bridge state-report`.

Queue state for the record: `LO_ACTIONABLE_LATEST_NEW_REVISED_NO_ACTION = 0`,
confirmed by `gt bridge state-report --json` (`lo_actionable: []`) and an
independent on-disk latest-version-per-slug scan. The nine `UNKNOWN`-status
threads were individually inspected and are all terminal legacy files (eight
Codex verification reports, one misfiled GOV spec); none conceals LO-actionable
work.

## Claim

The advisory-to-backlog router deduplicates on **thread slug**, not on advisory
version or content. Once any version of a slug has been staged, every
subsequent advisory filed on that slug is permanently and silently skipped. Of
the 15 advisories currently on disk, 13 are unreachable by the drain. The P0
root cause of the VERIFIED-finalization deadlock is among them.

This finding **falsifies two prior published claims** and is not a restatement
of either:

- `gtkb-lo-auto-finalize-sweep-zero-success-advisory-001` Finding D asserts the
  advisory channel "has no drain." That is false. A drain exists, is VERIFIED
  (`DELIB-20264768`), is registered as a live `Stop` hook, runs on every turn,
  and has staged 238 candidates and produced 1,663 router-attributed
  `work_items` historically.
- The same Finding D attributes the burial to "only the latest version is a
  thread head." That is the wrong mechanism. The router's thread-head fold is
  correct: it does select `-011` as the head of the tooling-defect chain. The
  head is then discarded by a separate dedup check. Fixing the thread-head
  logic would change nothing.

The real mechanism is worse than either published account, because the drain
reports success while draining nothing.

### E1 - The dedup key is the slug

`scripts/advisory_backlog_router.py`, `collect_bridge_advisories` line 402 sets
`source_key=doc_id`, where `doc_id` is the **slug** captured by the `-NNN.md`
filename regex - not the versioned filename, not a content hash.

`run()` lines 603-612 then short-circuit on
`if advisory.source_key in status_map` into `skipped_existing`. `status_map`
(`current_candidate_status`, lines 483-496) folds the append-only candidate log
to the latest record per `source_key`. The check matches on **any** prior
status; a `rejected` candidate is equally never re-staged.

Enumeration itself is sound: `_latest_bridge_threads` line 357 uses
`Path.glob("*.md")`, so untracked files are visible to the router.
Untrackedness was tested as a hypothesis and rejected - it is not the cause.

### E2 - The live candidate store confirms one stage per slug

| Slug | Versions on disk | Records staged |
|---|---|---|
| `gtkb-lo-tooling-defect-advisory` | 11 | 1 |
| `gtkb-lo-auto-finalize-sweep-zero-success-advisory` | 2 | 1 |
| `gtkb-lo-verdict-filing-path-advisory` | 1 | 1 |
| `gtkb-lo-verified-finalization-packet-freshness-advisory` | 1 | 1 |

### E3 - The frozen record points at version 001

The single staged record for the eleven-version chain, verbatim in relevant
part:

```
"relative_path": "bridge/gtkb-lo-tooling-defect-advisory-001.md",
"description":   "... Document: gtkb-lo-tooling-defect-advisory Version: 001",
"title":         "LO Advisory - Six Tooling Defects Observed While Processing
                  The LO Bridge Queue",
"recorded_at":   "2026-07-26T21:09:19Z",
"status":        "staged"
```

This is the load-bearing consequence. The owner's promotion queue will present
a candidate titled "Six Tooling Defects" pointing at `-001`. The actual P0 root
cause of the finalization deadlock - the pre-commit checker querying
`sot_registry_observation_capabilities` instead of
`sot_registry_bridge_publication_capabilities`, published in `-007` and
confirmed in `-008` - is not in that record, not in its title, not in its path,
and cannot be staged as long as `-001` occupies the slug.

### E4 - The starvation is silent and reports success

`.gtkb-state/advisory-router/last-scan.json`, written by this session's own
`Stop` hook minutes before this advisory was drafted:

```
"last_scan_finished_at": "2026-07-28T05:08:37Z",
"scanned": 15,
"staged_count": 0,
"skipped_existing_count": 15,
"errors_count": 0
```

Fifteen advisories scanned, zero staged, zero errors. A slug-starved run is
byte-indistinguishable from a healthy no-op run. Compounding this, the `Stop`
wrapper `.claude/hooks/advisory-router-scan.py` is fail-silent by construction
(lines 86-105): every exception path returns `{}` and exit 0, so neither
starvation nor outright failure surfaces in the transcript.

### E5 - Empirically consistent with the historical record

The most recent advisory-routed work item in MemBase is the
`sp1-dispatch-reliability-prime-handoff` routing row, `changed_at 2026-07-24`.
Every advisory filed since - 13 of the 15 on disk - reused an existing slug and
was skipped. The drain has not moved an LO advisory in four days, while LO
advisory output over that window was at its highest.

### E6 - The prior workaround was discovered but not diagnosed

`gtkb-lo-auto-finalize-sweep-zero-success-advisory-001` was deliberately filed
on a fresh slug, and its Finding D reasons about burial. That instinct was
correct and it did reach the store (E2, row 2). But because the mechanism was
misattributed to thread-head selection rather than slug dedup, the workaround
was recorded as a presentation concern rather than as the sole functioning
route to the owner. The consequence is that `-002` of that same fresh slug -
which retracts a stale finding - is itself already starved.

### Risk and impact

Severity: P0 for governance throughput.

- Roughly 25 of the 28 distinct defects catalogued across the current advisory
  corpus are staged nowhere and are unreachable by any owner-facing promotion
  path. This includes the sole identified root cause of the terminal-VERIFIED
  commit deadlock, which is currently blocking finalization repeatedly.
- The failure is silent, reports `errors_count: 0`, and its symptom ("nothing
  new to route") is identical to correct behavior. It cannot be detected by
  watching the router.
- The defect is self-concealing at the process level: the natural LO reflex -
  append the next finding to the established chain - is the exact action that
  guarantees the finding is never seen. Higher LO diligence produces less owner
  visibility, not more.
- It silently converts the append-only advisory chain, which is the correct
  audit-trail shape under `GOV-FILE-BRIDGE-AUTHORITY-001`, into a write-only
  sink.

### Verification performed

- Read `scripts/advisory_backlog_router.py` in full, including
  `_latest_bridge_threads` (352-370), `collect_bridge_advisories` (402),
  `_existing_wi_for` (424-440), `current_candidate_status` (483-496),
  `stage_advisory_candidate` (499-529), and `run()` (572-638).
- Tallied `candidates.jsonl` (238 records) and grouped by `source_key`.
- Read the frozen tooling-defect candidate record verbatim.
- Read `last-scan.json` from the run that completed at 05:08:37Z.
- Queried `groundtruth.db` for `source_spec_id='GOV-STANDING-BACKLOG-001'`
  (1,663 rows) and inspected the five most recent by `changed_at`.
- Cross-checked against `DELIB-20264768` (router VERIFIED) and
  `DELIB-20261055` (router output-volume advisory).

## Owner Decision Needed

None. This advisory reports a mechanical defect with a determinate root cause
and requires no owner decision to be understood or actioned. It is filed for
Prime Builder disposition under the standard advisory loop; any resulting
implementation requires its own proposal, owner grilling where the
peer-solution advisory loop applies, and bridge `GO`.

## Recommended Prime Action

Offered as analysis for Prime Builder disposition. This advisory is not an
implementation approval and does not authorize source mutation.

1. **Re-key dedup to slug+version** (or a content hash of the versioned file),
   so a new version on an existing slug stages as a distinct candidate. This is
   the minimal correct fix and is confined to `source_key` construction at
   `advisory_backlog_router.py:402` plus the two skip checks at lines 603-625.
   The `work_items` check `_existing_wi_for` (lines 424-440) uses a substring
   `LIKE` and will need the same treatment, or it re-introduces the skip
   through the second gate.
2. **Add a liveness assertion.** A run where `scanned > 0`,
   `staged_count == 0`, and `skipped_existing_count == scanned` should emit a
   distinguishable signal rather than presenting as a healthy no-op. This is
   the same silent-zero-success class as the auto-finalization sweep
   (`...zero-success-advisory-001` Finding A); the two share a remedy shape.
3. **Backfill the 13 starved advisories** once (1) lands, so the existing
   corpus reaches the promotion queue rather than remaining stranded.
4. **Until (1) lands, file every LO advisory on a fresh unique slug.** This is
   currently the only route by which an LO finding reaches the owner. It should
   be recorded in the LO advisory guidance rather than rediscovered per
   session.
5. **Consider the Codex parity gap** noted incidentally: the router is
   registered as a `Stop` hook in `.claude/settings.json` and
   `.cursor/hooks.json` but not in `.codex/hooks.json`, so advisories filed in
   a Codex-only session are never scanned at all. Separately, two divergent
   registry entries name different canonical hook paths
   (`.claude/hooks/advisory-router-scan.py` vs
   `config/hooks/gtkb-advisory-router-scan.py`). Both are outside this
   advisory's claim and are surfaced only as adjacent observations.

## Classification Slot

Proposed classification: `adopt`.

Rationale: the defect is mechanical, the root cause is located to specific
lines, and the minimal fix is confined to the router's dedup key. No peer
system is involved and no design alternative is being weighed, so `adapt` does
not apply. `defer` and `monitor` are inappropriate because the defect is
actively suppressing the entire LO advisory channel, including the root-cause
finding for a deadlock that is blocking finalization now.

Prime Builder retains disposition authority; this slot records the LO
recommendation only.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
