ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 469b6155-827b-44cb-a56d-f838893bffa3
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task system-statusprogress-check; resolved role loyal-opposition

bridge_kind: governance_advisory
Document: gtkb-lo-sysprobe-membase-pipeline-events-unbounded-growth
Version: 001
Author: Loyal Opposition (claude, harness B)
Date: 2026-08-01 UTC

## Source

Scheduled system status/progress probe (system-statusprogress-check), 2026-08-01,
session context 469b6155-827b-44cb-a56d-f838893bffa3. Evidence from read-only
SQLite queries against groundtruth.db and from gt project doctor.

This advisory files the companion advisory that
gtkb-lo-sysprobe-cli-latency-and-gate-false-positives-001.md (2026-07-31) twice
refers to but which was never filed. That advisory says "see the companion
advisory on pipeline_events growth"; a search of the whole bridge/ corpus returns
only the two 2026-07-31 sysprobe files. The referenced companion does not exist.
This closes that gap and supplies the measurement the earlier advisory asserted
without evidence.

## Claim

pipeline_events is an unbounded projection whose assertion-run shadow is
approximately 13x larger than the canonical assertion_runs table it mirrors, over
a SHORTER time window. The retention path exists in the schema own event
vocabulary but has executed exactly once in project history.

## Evidence

MemBase at groundtruth.db: 808.8 MB, pragma integrity_check = ok, 56 tables
(doctor: "Schema OK (56 tables)").

| Table | Rows | Window |
| --- | --- | --- |
| pipeline_events | 1,510,457 | 2026-04-12T01:04:07Z .. 2026-08-01T07:00:34Z |
| assertion_runs (canonical) | 114,238 | 2026-03-09T03:13:08Z .. 2026-08-01T07:00:34Z |

pipeline_events composition by event type:

| event_type | Rows | Share |
| --- | --- | --- |
| assertion_run | 1,494,916 | 98.97% |
| test_executed | 8,292 | 0.55% |
| wi_created | 2,914 | 0.19% |
| wi_resolved | 2,088 | 0.14% |
| spec_transition | 1,527 | 0.10% |
| test_created | 717 | 0.05% |
| wi_reopened | 2 | - |
| pipeline_events_retention | 1 | - |

Three facts follow directly and should not be conflated:

1. Amplification. The assertion-run projection (1,494,916) exceeds the canonical
   assertion_runs table (114,238) by ~13x, despite covering a shorter window
   (canonical starts 2026-03-09; the projection starts 2026-04-12). The canonical
   table is retention-capped. Its projection is not.
2. Retention is inert. Exactly one pipeline_events_retention event exists across
   1.5 M rows. The mechanism is not missing - it is not running.
3. Growth is current, not historical. Per-day insert counts for the trailing 10
   days: 2026-07-23 12,298; 07-24 23,597; 07-25 15,947; 07-26 17,779; 07-27
   16,907; 07-28 21,506; 07-29 26,802; 07-30 12,551; 07-31 7,805; 08-01
   (partial, probe ran 07:00Z) 2,424.

## Risk / Impact

- groundtruth.db is git-tracked. Every commit that touches it re-hashes the whole
  808.8 MB blob. WI-5431 already records recurring Git object-store bloat from the
  re-hashed tracked DB (~5 GB/day regrowth). This advisory identifies a
  contributing driver of the DB size that WI-5431 treats as a given: ~99% of the
  largest table is a redundant projection.
- Unbounded projection growth raises the cost of every full-table read path and of
  snapshot / restore.
- The single retention event means no operator has evidence that retention was
  ever reasoned about; a future prune has no established window to prune to.

## Scope Boundary - What This Advisory Does NOT Claim

The companion residue advisory gtkb-lo-sysprobe-runtime-residue-census-cost
establishes that the dominant gt project doctor cost is whole-root file census,
not MemBase size. Do NOT attribute CLI latency to pipeline_events without
re-baselining. The 2026-07-31 advisory assertion that latency "scales with corpus
size ... MemBase is 844 MB with 1.5 M pipeline events" conflates two independent
costs and should be read with that correction.

## Owner Decision Needed

None to file this advisory. A retention WINDOW is an owner-facing policy choice
and should be captured via AskUserQuestion when Prime Builder scopes the work.

## Recommended Prime Action

1. Determine whether the assertion-run projection into pipeline_events has any
   consumer that the canonical assertion_runs table does not serve. If not, the
   correct fix is to stop writing it, not to prune it.
2. If the projection is load-bearing, apply the same retention window already
   applied to assertion_runs, and schedule it.
3. Establish why pipeline_events_retention fired once and never again.
4. Re-measure groundtruth.db size after any prune and report the delta into
   WI-5431 as an input to the Git bloat work.
5. Add a doctor check for pipeline_events row count and retention recency so this
   is detected rather than discovered by probe.

## Related Backlog

- WI-5854 (filed this session, P2) - records this defect in MemBase work_items.
  Backlog capture is not implementation approval.
- WI-5431 (open) - Git object-store bloat from the re-hashed tracked DB.
  Adjacent, not duplicate: WI-5431 owns the Git-layer symptom; this owns the
  DB-layer driver.
- WI-3158 (resolved) - created the pipeline_events table. No retention work item
  existed before WI-5854.

## Prior Deliberations

- DELIB-20260724-DISPATCHER-QUIESCENCE-MANUAL-LO - establishes that several
  concurrent WARN surfaces are owner-decided posture. Cited here to mark that this
  finding is NOT covered by that decision and is a live defect.
- gtkb-sot-access-latency-append-only-growth-cost-advisory-001.md (2026-07-30) -
  prior advisory on append-only growth cost at the SoT-access layer. Adjacent
  surface; this advisory measures the MemBase table layer.
- gtkb-fab-13-retention-policy-umbrella-001.md - prior retention-policy umbrella
  thread. Prime Builder should check whether this belongs under that umbrella
  rather than as a standalone project.

## Classification Slot

adapt.

This advisory is not implementation approval. It does not authorize protected
edits, does not open an implementation-start packet, does not authorize any
MemBase prune or schema change, and does not bypass the Prime Builder proposal,
Loyal Opposition GO, or verification gates.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
