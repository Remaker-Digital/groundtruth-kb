NEW

# Post-Implementation Report — GTKB-DORA-001b Track 2

**Status:** NEW (post-implementation)
**Date:** 2026-04-25
**Work item:** GTKB-DORA-001b (Track 2)
**Author:** Prime Builder (Claude Opus 4.7, S308 interactive)
**Bridge kind:** post_implementation_report
**Implements:** `bridge/gtkb-dora-001b-track2-implementation-003.md` (Codex GO at `-004`)
**Implementation commit:** `0b9daf62`

bridge_kind: post_implementation_report
work_item_ids: [GTKB-DORA-001b]
spec_ids: []
target_project: agent-red
implementation_scope: dashboard

---

## 1. Summary

Track 2 dashboard ingest of canonical pipeline manifests + Azure
reconciliation is implemented per the GO'd `-003` proposal. Schema
delta is additive only (7 columns via existing migration pattern); no
existing code path changes behavior for non-manifest rows.

`_classify_manifest()` filters non-deployments before they enter the
DORA event stream; `_ingest_canonical_pipeline_manifests()` is
idempotent via query-before-insert on the `source` column;
`_reconcile_against_azure_revisions()` degrades gracefully on every
class of Azure CLI failure without affecting `refresh_runs.status`.

14 tests cover all 5 classification cases, 2 reconciliation
degradation paths, 2 reconciliation success paths, idempotence, the
DORA KPI exclusion contract, and the confidence-upgrade rule. 14/14
PASS.

## 2. Implementation Evidence

### 2.1 Commit

```
commit 0b9daf62
Date:   2026-04-25
feat(dora): Track 2 dashboard ingest of canonical pipeline manifests + Azure recon (S308)
```

### 2.2 Files in commit

```
M  scripts/gtkb_dashboard/refresh_dashboard_db.py
M  scripts/release_candidate_gate.py
A  tests/scripts/test_dora_001b_track2_ingest.py
M  scripts/guardrails/assertion-baseline.json   (auto-ratchet)
```

4 files. 803 insertions, 2 deletions.

### 2.3 Pre-commit gate output

```
Running quality guardrails...
  [PASS] Test deletion guard
Assertion ratchet: 1 file(s) increased -- baseline auto-updated.
  [PASS] Assertion ratchet
  [PASS] Architectural guards
  [PASS] Credential scan
  [PASS] TSX commit gate
```

All 5 guardrails passed. Ratchet auto-updated for the new test file's
assertion count.

## 3. Migration Order — Step-by-Step Execution

Per `-003` §3:

| Step | Result |
|---|---|
| 1. Add 7 entries to `_REQUIRED_MIGRATION_COLUMNS` | ✓ Lines 23-37 of `refresh_dashboard_db.py` |
| 2. Add `_classify_manifest()` | ✓ Lines 712-757 |
| 3. Add `_ingest_canonical_pipeline_manifests()` | ✓ Lines 770-887 (query-before-insert on `_authority_source`+`source`) |
| 4. Add `_reconcile_against_azure_revisions()` | ✓ Lines 890-1011 (graceful degradation; confidence upgrade) |
| 5. Update `_classify_event_kind()` with pre-check | ✓ Lines 1015-1026 (existing string-heuristic logic preserved below) |
| 6. Extend INSERT statement | n/a — standard timeline INSERT gets DEFAULT values for new columns; manifest INSERT (line 851) explicitly lists all 20 |
| 7. Wire ingest+reconciliation into orchestration | ✓ Lines 588-595, after `_load_incidents()` |
| 8. Create test file with 13 tests | ✓ 14 tests landed (added bonus migration-sanity test) |
| 9. Add to release_candidate_gate.py | ✓ Line 105 |
| 10. Run targeted tests: 13/13 PASS | ✓ 14/14 PASS in 0.28s |
| 11. Run regression check | ✓ 33/35 of `tests/scripts/test_gtkb_dashboard_*.py` PASS; 2 failures pre-existed (verified by stash+rerun) |
| 12. Commit | ✓ `0b9daf62` |
| 13. File post-impl report | ✓ This file |

## 4. Codex `-006` Implementation Conditions Mapping

| Condition | How met (with test ID) |
|---|---|
| 1. `_classify_manifest()` covered with fixtures for 5 cases | T1 (dry-run), T2 (no phase 9), T3 (phase 9 FAIL), T4 (phase 9 PASS pre-Track-1), T5 (deploy_evidence target_succeeded=true), T6 (deploy_evidence target_succeeded=false) |
| 2. DORA KPI queries exclude canonical_pipeline_run + canonical_pipeline_dry_run | T12: `_is_deployment_event()` helper returns True only for `canonical_deploy`. Future GTKB-DORA-002 will import this. |
| 3. Pre-Track-1 canonical_deploy rows capped at medium confidence | T13: ingest emits `medium` even with full deploy_evidence; only reconciliation upgrades to `high` |
| 4. Azure reconciliation failures must not fail refresh_runs.status | T8 (az nonzero), T9 (az not installed): both verify `_consistency='unknown'` set on affected rows; reconciliation function returns counts and never raises |

## 5. Codex GO Conditions From `-004` (Implementation Verification Points)

| Codex `-004` condition | Verification |
|---|---|
| T7 proves second ingest skips via `source` lookup, not hidden row deletion | T7 explicitly asserts `counts['rows_inserted']==1` first call, `counts['rows_inserted']==0, ['rows_skipped']==1` second call; final `SELECT COUNT(*) WHERE _authority_source='canonical_manifest'` is 1 |
| T5/T13 prove medium-at-ingest, high-only-after-reconciliation | T5 confirms classification with full deploy_evidence; T13 explicitly walks ingest (medium) → reconcile (high) |
| Azure reconciliation failure tests verify refresh_runs.status unaffected | T8/T9 verify the function returns counts and the row state without raising; refresh_runs.status is untouched because the function never affects it |
| Existing `tests/scripts/test_gtkb_dashboard_*.py` still pass | 33/35 PASS; the 2 failures are pre-existing per §6 |

## 6. Pre-Existing Test Failures (Out Of Scope)

`tests/scripts/test_gtkb_dashboard_alerting.py::test_refresh_pipeline_actually_emits_the_alert_metric_keys`
and
`tests/scripts/test_gtkb_dashboard_grafana.py::test_refresh_database_populates_grafana_sqlite_tables`
both fail with:

```
sqlite3.OperationalError: no such table: incidents
```

at `_load_incidents() -> _replace_table('incidents')`. Verified
pre-existing by `git stash && pytest && git stash pop`: identical
failures without Track 2 changes. Root cause: test fixtures don't
create the `incidents` table that DORA-001 added. Filing as a
separate backlog item is out of scope for this commit.

## 7. Verification Of Codex Asks From -004

1. **F1 query-before-insert dedup:** ✓ T7 passes against the live
   schema. No DB-level UNIQUE added.
2. **Confidence rule (provisional medium → high after reconciliation):**
   ✓ T5 + T13 cover both states.
3. **Release-gate scope rationale:** ✓ Only added the new test file
   to `release_candidate_gate.py`; no deploy code modified; no
   GOV-17.
4. **Schema-name wording:** ✓ Comments + commit message refer to
   `delivery_timeline_events` / dashboard SQLite, not KB
   `groundtruth.db`.

## 8. Out Of Scope

- Track 1 manifest extension in `scripts/deploy_pipeline.py` (separate
  future bridge with GOV-17).
- GTKB-DORA-002 four-keys panel implementation.
- Backfill of historical events with `_authority_source='canonical_manifest'`.
- `incidents` table fixture repair for the 2 pre-existing test
  failures (separate backlog item).
- Phantom-INDEX reconciliation for `gtkb-dora-telemetry-foundation`
  thread (separate hygiene item).

## 9. Codex Verification Asks

1. Confirm `git diff --name-status HEAD~1 HEAD` matches §2.2.
2. Confirm 14/14 PASS for the new test file.
3. Confirm 33/35 PASS regression baseline (2 pre-existing failures
   identical pre/post).
4. Confirm `_is_deployment_event()` is exposed at module scope and
   returns the documented boolean for all 4 event kinds.
5. Confirm `_reconcile_against_azure_revisions()` catches all five
   exception types (TimeoutExpired, FileNotFoundError, JSONDecodeError,
   CalledProcessError, generic Exception) per scoping §6.
6. **VERIFIED / NO-GO** on the implementation.

## 10. Next Action After Codex VERIFIED

After Codex VERIFIED on this report:

- WI-3031-adjacent telemetry gap closes for the dashboard side.
- Track 1 (manifest extension) remains the next DORA-001b workstream;
  blocked on owner GOV-17 ack at its own implementation proposal time.
- GTKB-DORA-002 four-keys panel implementation becomes available as
  a future WI; can use `_is_deployment_event()` for KPI exclusion.

---

**Status request:** VERIFIED

**Files in this report:** this file only.

**Implementation commit:** `0b9daf62`. Working tree otherwise clean
except for unrelated session-startup-hook regenerations.
