NEW

# GTKB-ISOLATION-016 Phase 8 Wave 3 Execution

**Status:** NEW
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** Wave 2 umbrella GO at `bridge/gtkb-isolation-016-phase8-wave2-implementation-004.md`; all 11 Wave 2 slices VERIFIED (latest `slice11-016.md`).

---

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md` (this file)
- `bridge/INDEX.md` updated with the `Document: gtkb-isolation-016-phase8-wave3-execution` entry at the top

This commit does **not** modify the manifest, the `_common.py` validation, the driver dispatch table, or land the new sub-script. Those changes ship in the implementation commit after Codex GO. This explicit scope statement preempts the Wave 2 `-001`/`-002` divergence pattern (claim asserted manifest landed; commit deferred it).

## Owner Decisions Encoded

Two S325 owner decisions are encoded by this proposal and become manifest values at implementation time:

1. **`db_reconciliation_strategy = "manifest_driven_filter"`** — owner decision 2026-05-01 in response to the Wave 3 trade-off investigation. Resolves §3.6 of the source manifest (the `OWNER_DECISION_REQUIRED` placeholder Codex `-004` flagged as the Wave 3 boundary blocker).
2. **`unclassified_disposition = "leave_behind_with_warning"`** — owner decision 2026-05-01 in the same exchange. Rows where `_membase_export.py` cannot determine framework/adopter scope are surfaced as warnings and excluded from the filtered preview DB; cutover (ISOLATION-018) reads the warning list as the manual-reclassification queue.

Both decisions will be archived as Deliberation Archive records (`DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` and `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`, `source_type='owner_conversation'`, `outcome='owner_decision'`) as part of the implementation commit.

## Specification Links

The following specifications, rules, and decisions govern this proposal. Tests in the Test Plan section derive from the linked clauses noted.

- **`ADR-ISOLATION-APPLICATION-PLACEMENT-001`** (upstream commit `affa5a05` per manifest header) — the parent architecture decision establishing application/platform separation under `applications/<app>/`. The DB reconciliation strategy must satisfy the ADR's "GT-KB platform records remain outside ordinary app mutation scope" principle.
- **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`** — authority matrix row for `groundtruth.db` (line 115) classifying it as `legacy-exception` with split-required disposition; Owner-Decision-Pending row 1 (lines 143-146) explicitly anticipates "decide whether app-local DA/MemBase remains local, becomes service-backed, or splits into app and product stores during migration." The `manifest_driven_filter` strategy is the app-local-records branch of that decision.
- **`.claude/rules/operating-model.md` §3** ("Implemented vs. Intended Surfaces") — names "DA/MemBase service surface" as intended-not-implemented. Wave 3 must not adopt a strategy that depends on absent infrastructure; `manifest_driven_filter` is implementable against existing Slice 8 output.
- **`.claude/rules/project-root-boundary.md`** — all Wave 3 sources, tests, and outputs must reside under `E:\GT-KB`. The runbook artifact under `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/` is in-root; the runtime output dir (`C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}`) remains the sandbox per §3.3 owner decision and Rule M2.
- **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate, Mandatory Specification-Derived Verification Gate.
- **`.claude/rules/codex-review-gate.md`** — implementation cannot proceed without Codex GO; tests must derive from linked specifications.
- **`bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md`** §3.1 (Rule M1 contract for `db_reconciliation_strategy` at wave>=3) and `-004.md` Recommended Actions clause "Wave 3 must reject the unresolved `db_reconciliation_strategy` placeholder before verification/reconciliation work" — the conditions Wave 3 must close.
- **`bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md`** (Codex GO) — the partition-manifest contract this proposal consumes: schema-discovery, four-category classification (`framework` / `adopter` / `unclassified` / orphan), per-table cutover policy. Constraint 1 (unknown table → `status=error`), Constraint 2 (telemetry exclusion policy), Constraint 4 (silent default to adopter is rejected) propagate forward.
- **`scripts/rehearse/_membase_export.py`** lines 1-228 — the existing classifier this lane consumes. The proposal adds zero reclassification logic and zero new content markers.
- **`bridge/gtkb-isolation-016-phase8-rehearsal-implementation-018.md`** (VERIFIED, Wave 1) — the driver-dispatch contract this proposal extends with one new lane.
- **`GOV-09`** (CLAUDE.md governance index) — Owner Input Classification Rule; the Owner Decisions section captures the §1 owner decisions as DA records before implementation acts on them.
- **`GOV-20`** (CLAUDE.md governance index) — Architecture Decision Workflow. This work item touches an ADR-tagged surface (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`); the implementation step will create an IPR document linking Wave 3 work to the ADR per Phase 1 advisory pilot.

## Strategy Decision Rationale (carried forward from owner exchange)

Five candidate strategies were investigated in the pre-proposal exchange. Recap of why `manifest_driven_filter` was selected over the alternatives:

1. **Replay log (rejected)** — would require designing custom change-data-capture; SQLite has no built-in WAL-replay-into-foreign-DB primitive that respects row-level partitioning. Cost out of proportion to a one-shot cutover.
2. **Read-only legacy + deferred split (rejected)** — defers the hardest reconciliation problem to ISOLATION-018, the highest-stakes moment; inverts the rehearsal's purpose.
3. **Service-backed split (rejected for this rehearsal)** — DA/MemBase service is intended-not-implemented per `operating-model.md` §3; would block TOP-priority isolation program on absent platform infrastructure. Remains the long-term direction per authority matrix Owner-Decision-Pending row 1 default recommendation, but is not a Wave 3 candidate.
4. **Snapshot copy + freeze, no filter (rejected)** — leaves all 8,400+ specs and 1,514 deliberations classified as `framework` inside the adopter child root; defeats the program's intent.
5. **Manifest-driven filter at cutover with brief freeze window (selected)** — reuses Slice 8's row-level partition manifest; Wave 3 implements only a deterministic consumer; telemetry-exclusion already removes ~99% of the 1.0 GB DB size from the filter payload; reversibility preserved (legacy DB untouched).

## Implementation Plan

Implementation commit (after Codex GO) lands the following changes. Each change cites the linked spec it satisfies.

### Manifest update (one file)

**File:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

**Changes:**

```toml
# Replaces existing line 36:
db_reconciliation_strategy = "manifest_driven_filter"

# New field (added below db_reconciliation_strategy):
# Owner decision 2026-05-01 (S325): unclassified rows in the
# Slice 8 partition manifest are excluded from the filtered preview
# DB and emitted as warnings. Cutover (ISOLATION-018) reads the
# warning list as the manual-reclassification queue.
unclassified_disposition = "leave_behind_with_warning"
```

Header comment block updated to reflect the 2026-05-01 owner decisions and cite this bridge.

**Satisfies:** `wave2-implementation-004.md` Recommended Action "Wave 3 must reject the unresolved `db_reconciliation_strategy` placeholder"; authority matrix Owner-Decision-Pending row 1.

### `_common.py` Wave 3 validation (Rule M6)

**File:** `scripts/rehearse/_common.py`

**Changes:** Add positive validation for the two new manifest fields. The existing M1 rejection of `OWNER_DECISION_REQUIRED` (`_common.py:332-338`) remains; M6 layers on top by rejecting any value not in the known set.

```python
# Module-level constants (near _VALID_GIT_STRATEGIES):
_VALID_DB_RECONCILIATION_STRATEGIES: frozenset[str] = frozenset({
    "manifest_driven_filter",
})
_VALID_UNCLASSIFIED_DISPOSITIONS: frozenset[str] = frozenset({
    "leave_behind_with_warning",
    "carry_forward_to_adopter",
    "manual_review_gate",
})

# Inside load_manifest, after the existing M1 wave>=3 rejection block:
if wave >= 3:
    # Rule M6 — db_reconciliation_strategy positive validation.
    strategy = data.get("db_reconciliation_strategy")
    if strategy not in _VALID_DB_RECONCILIATION_STRATEGIES:
        raise ManifestValidationError(
            f"M6: manifest.db_reconciliation_strategy = {strategy!r} "
            f"not in {sorted(_VALID_DB_RECONCILIATION_STRATEGIES)}."
        )
    disposition = data.get("unclassified_disposition")
    if disposition not in _VALID_UNCLASSIFIED_DISPOSITIONS:
        raise ManifestValidationError(
            f"M6: manifest.unclassified_disposition = {disposition!r} "
            f"not in {sorted(_VALID_UNCLASSIFIED_DISPOSITIONS)}."
        )
```

Wave 1 and Wave 2 callers retain existing behavior (M6 gated on `wave>=3`).

**Satisfies:** Wave 2 `-003.md` §3.1 Rule M1 contract (positive complement); `wave2-implementation-004.md` Recommended Action.

### New sub-script: `scripts/rehearse/_db_filter_dryrun.py`

**File:** `scripts/rehearse/_db_filter_dryrun.py` (new, ~280 LOC estimated).

**Lane name:** `db-filter-dryrun`
**Stage:** D (cross-cutting consumer; depends on `membase` lane output).
**Signature:** `def run(manifest, output_dir, *, args=None) -> dict` — same envelope as existing lanes per `_split_helper.emit_result`.

**Algorithm:**

1. Read partition manifest from `{output_dir}/membase/membase-partition-manifest.json` (canonical Slice 8 output path). If missing, return `status=error` with `reason="partition_manifest_missing"` (defends against running this lane before `membase`).
2. Read manifest field `unclassified_disposition` — drives the filter behavior.
3. Open legacy DB read-only via `_open_readonly()` (the helper already exists in `_membase_export.py:245` and is reusable).
4. Create output DB at `{output_dir}/db-filter-dryrun/groundtruth-filtered-preview.db`.
5. Copy schema from legacy via `sqlite_master` `CREATE TABLE` statements (no data yet).
6. For each table category from the partition manifest:
   - **Versioned-artifact tables (12):** insert rows where classification == `adopter`. Skip rows where classification == `framework`. For `unclassified` rows: under `leave_behind_with_warning`, skip and emit one warning per row to `db-filter-warnings.txt`. Other dispositions (`carry_forward_to_adopter`, `manual_review_gate`) are explicitly out-of-scope for this proposal; the validator accepts them so future bridges can add behaviors, but `_db_filter_dryrun.py` raises `NotImplementedError` for non-`leave_behind_with_warning` dispositions in this Wave 3 commit.
   - **Relationship tables (2):** insert rows whose parent (`deliberation_id` / `spec_id` / `work_item_id`) was inserted in the versioned step. Orphan rows (parent not in adopter set) emit a warning per the Slice 8 Constraint 3 contract.
   - **Excluded telemetry (4):** skip entirely. Tables remain empty in the output DB (schema present, zero rows). Per Slice 8 Constraint 2 cutover policy `regenerate_at_new_root_*`.
   - **Per-session tables (3):** insert rows whose classification is `adopter` per the Slice 8 per-session classifier (`session_id` ownership signal).
   - **Unknown tables:** Slice 8 already emits `status=error` for unknown tables; if the partition manifest has `status=error`, this lane refuses to run and propagates the error. Re-classification is never performed; the lane trusts Slice 8.
7. Run `PRAGMA integrity_check` on the output DB. If the result string is not exactly `"ok"`, return `status=error` with the integrity-check output.
8. Write `db-filter-summary.json` with row counts per category.
9. Write `db-filter-warnings.txt` (one line per unclassified or orphan row).
10. Write `db-filter-rejects.txt` (one line per framework-classified row excluded).
11. Emit standard `result.json` envelope via `emit_result`.

**Read-only on legacy:** the lane opens legacy DB with `mode=ro` URI. Same pattern as Slice 8; no writes to `E:/GT-KB/groundtruth.db`.

**Satisfies:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (filtered output excludes framework rows); authority matrix `groundtruth.db` row split-required disposition; `wave2-implementation-004.md` Recommended Action.

### Driver dispatch wire-up

**File:** `scripts/rehearse_isolation.py`

**Changes:** add one entry to `DISPATCH_TABLE` (after `("membase", ...)` since `db-filter-dryrun` consumes its output):

```python
("db-filter-dryrun", "rehearse._db_filter_dryrun", "run"),
```

`PHASE_CHOICES` updates automatically via the existing tuple-comprehension at line 58.

Driver loads manifest with `wave=3` when this phase is requested (or `--phase all` is run after Wave 2 manifest is in place). The wave parameter at the driver level is already plumbed; the new behavior is just M6 firing on the wave=3 load.

**Satisfies:** `rehearsal-implementation-018.md` driver dispatch contract.

### Freeze-window runbook

**File:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/AGENT-RED-CUTOVER-FREEZE-WINDOW-RUNBOOK-2026-05-01.md` (new).

**Sections:**
- Pre-freeze checks: legacy DB integrity, no in-flight bridge proposals, last membase-export age under 1 hour
- Freeze announcement protocol (owner-only single-harness operation)
- Run `_db_filter_dryrun` against latest legacy DB
- Smoke checks against filtered DB: schema parity, integrity_check, expected row counts, framework-row absence
- Activation/swap (placeholder cross-reference to ISOLATION-018; this runbook documents the rehearsal's freeze model only)
- Rollback procedure: delete child DB, resume on legacy, no other state change required
- Post-freeze validation checklist

This artifact is rehearsal evidence, not the cutover script. ISOLATION-018 will produce its own runbook informed by what this one surfaces.

**Satisfies:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001` operational evidence requirement; project-root-boundary rule (artifact is in-root).

### Tests

**File:** `tests/scripts/test_rehearse_db_filter_dryrun.py` (new). Test plan in the Specification-Derived Verification section below.

## Output Layout

**Per-run output structure** (under `{output_dir}/`, where `output_dir = "C:/temp/agent-red-rehearsal-{ISO_TIMESTAMP}"`):

```
{output_dir}/
  ├── inventory/                          (from Wave 2 Slice 1)
  ├── membase/
  │   ├── membase-partition-manifest.json (Slice 8 input to this lane)
  │   ├── membase-partition-manifest-preview.md
  │   └── result.json
  ├── db-filter-dryrun/                   (NEW — this proposal)
  │   ├── groundtruth-filtered-preview.db
  │   ├── db-filter-summary.json
  │   ├── db-filter-warnings.txt
  │   ├── db-filter-rejects.txt
  │   └── result.json
  ├── ... (other Wave 2 lanes' outputs)
```

`db-filter-summary.json` schema:

```json
{
  "lane": "db-filter-dryrun",
  "manifest_input_path": "...",
  "legacy_db_path": "E:/GT-KB/groundtruth.db",
  "output_db_path": "{output_dir}/db-filter-dryrun/groundtruth-filtered-preview.db",
  "unclassified_disposition": "leave_behind_with_warning",
  "row_counts": {
    "adopter_inserted": <int>,
    "framework_excluded": <int>,
    "unclassified_warned": <int>,
    "telemetry_skipped": <int>,
    "orphan_relationship_warned": <int>
  },
  "tables": {
    "<table_name>": {
      "category": "versioned_artifact | relationship | excluded_telemetry | per_session",
      "adopter": <int>,
      "framework": <int>,
      "unclassified": <int>
    }
  },
  "integrity_check": "ok | <error_text>",
  "elapsed_seconds": <float>
}
```

## Specification-Derived Verification

Each test maps to a linked specification clause from the Specification Links section. Tests live in `tests/scripts/test_rehearse_db_filter_dryrun.py`.

| # | Test name | Derives from |
|---|---|---|
| T1 | `test_filtered_db_excludes_all_framework_classified_rows` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (framework rows outside app mutation scope); authority matrix `groundtruth.db` row |
| T2 | `test_filtered_db_telemetry_tables_have_zero_rows` | Slice 8 Constraint 2 (`_EXCLUDED_TELEMETRY_POLICY`) |
| T3 | `test_filtered_db_adopter_row_count_matches_partition_manifest_summary` | Slice 8 contract (manifest is authoritative classification) |
| T4 | `test_unclassified_rows_emit_warning_and_are_not_inserted_under_default_disposition` | Owner decision 2026-05-01 (`unclassified_disposition = "leave_behind_with_warning"`); Slice 8 Constraint 4 (silent default to adopter is rejected) |
| T5 | `test_lane_refuses_when_partition_manifest_missing` | Implementation Plan algorithm step 1; Slice 8 dependency contract |
| T6 | `test_lane_propagates_partition_manifest_status_error_for_unknown_table` | Slice 8 Constraint 1 (unknown table → `status=error`) |
| T7 | `test_legacy_db_is_opened_read_only` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (rehearsal non-destructive on legacy); §3.5 owner decision (clone strategy preserves legacy) |
| T8 | `test_filtered_db_passes_pragma_integrity_check` | Implementation Plan algorithm step 7; SQLite consistency contract |
| T9 | `test_orphan_relationship_rows_emit_warning_not_silent_drop` | Slice 8 Constraint 3 |
| T10 | `test_lane_is_idempotent_on_re_run` | Slice 3 idempotency contract (`-001.md` §4.3) |
| T11 | `test_lane_writes_only_under_output_dir` | Rule M2 sandbox-output-dir contract |
| T12 | `test_load_manifest_wave_3_rejects_unknown_db_reconciliation_strategy` | Rule M6 (positive complement to existing M1 rejection) |
| T13 | `test_load_manifest_wave_3_rejects_unknown_unclassified_disposition` | Rule M6 |
| T14 | `test_load_manifest_wave_3_accepts_manifest_driven_filter` | Rule M6 (positive case) |
| T15 | `test_load_manifest_wave_2_still_accepts_owner_decision_required_for_db_reconciliation` | Rule M1 backward compatibility (Wave 2 callers must not break) |
| T16 | `test_db_filter_summary_json_has_required_keys` | Output Layout schema contract |
| T17 | `test_lane_raises_NotImplementedError_for_non_default_dispositions` | Implementation Plan explicit scope-deferral for `carry_forward_to_adopter` and `manual_review_gate` |

Plus regression coverage by re-running existing `tests/scripts/test_rehearse_isolation.py` (66 tests) and `tests/scripts/test_rehearse_dashboard_regen.py` (51 tests + 1 skip per Slice 11) — must remain green.

**Test execution commands** (for the post-implementation report):

```bash
python -m pytest tests/scripts/test_rehearse_db_filter_dryrun.py -q --tb=short --timeout=60
python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
python -m ruff check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py tests/scripts/test_rehearse_db_filter_dryrun.py
python -m ruff format --check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py tests/scripts/test_rehearse_db_filter_dryrun.py
```

Plus a live smoke run:

```bash
python scripts/rehearse_isolation.py --phase membase --execute --output-dir C:/temp/agent-red-rehearsal-wave3-smoke
python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute --output-dir C:/temp/agent-red-rehearsal-wave3-smoke
```

Smoke output captured in the post-implementation report.

## Risk / Impact

**Filter correctness risk (medium).** The lane's correctness depends entirely on the Slice 8 partition manifest. If Slice 8 misclassifies a row, this lane faithfully propagates the misclassification. Mitigation: (a) Slice 8 was VERIFIED with explicit constraints against silent defaults; (b) the warnings + rejects files make every excluded/unclassified row owner-auditable; (c) ISOLATION-018 cutover gets a separate review gate before activating any filtered DB.

**Concurrent-session risk (low for rehearsal, deferred for cutover).** Rehearsal runs read-only on legacy; sessions writing concurrently produce a snapshot-time-consistent filtered DB at output. Real cutover requires the freeze-window runbook and is not in this proposal's scope; this proposal produces the runbook artifact for ISOLATION-018 to consume.

**Forward compatibility (low).** `_VALID_UNCLASSIFIED_DISPOSITIONS` accepts three values but `_db_filter_dryrun.py` only implements `leave_behind_with_warning`; the other two raise `NotImplementedError`. Future bridges add behaviors without re-validating M6's accepted set. T17 enforces that the explicit scope-deferral is intentional and traceable.

**Rollback (trivial).** All outputs live under `{output_dir}` (sandbox per Rule M2). Rollback = delete the directory. Legacy DB untouched.

**Token cost (low).** ~280 LOC sub-script, ~30 LOC `_common.py` change, 17 tests, ~50-line runbook. Estimated implementation envelope under 600 LOC total.

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. Specification Links section covers all relevant governing artifacts.
2. Owner decisions are clearly attributed and will be archived as DA records before implementation acts on them.
3. Test plan maps every test to a linked specification clause.
4. Output Layout matches the file enumeration in Implementation Plan.
5. Wave 2 backward compatibility is preserved (Rule M6 gated on `wave>=3`; T15 covers).
6. Scope of the proposal commit is unambiguous and matches what will land.

This proposal closes Codex `wave2-implementation-004.md` Recommended Action conditions:
- "Wave 3 must reject the unresolved `db_reconciliation_strategy` placeholder before verification/reconciliation work" — addressed by the manifest update + Rule M6.
- The Wave 2 verification matrix boundary is reached.

## Decision Needed From Owner

**Nothing required at GO time.** The two owner decisions referenced earlier are already captured. Optional follow-up after VERIFIED:

- Whether ISOLATION-018 cutover should run the freeze-window from the runbook, or extend it. (Not blocking Wave 3.)
- Whether the warning list of unclassified rows should drive a separate work item to reclassify each ambiguous row before ISOLATION-018, or whether ISOLATION-018 absorbs that step. (Not blocking Wave 3.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
