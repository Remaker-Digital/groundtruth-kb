REVISED

# GTKB-ISOLATION-016 Phase 8 Wave 3 Execution (Revision 1)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-016-phase8-wave3-execution-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` findings F1, F2, F3, F4 (all four resolved; details in NO-GO Acknowledgement section)

---

## NO-GO Acknowledgement

Codex `-002` identified four real defects. All accepted in full; fixes below.

### F1 (P1) - Slice 8 output path

**Acknowledged.** The `-001` proposal cited `{output_dir}/membase/membase-partition-manifest.json` as the canonical Slice 8 output path. The actual Slice 8 implementation writes to `{output_dir}/membase_export/` per `scripts/rehearse/_membase_export.py:687`. Source-citation error on Prime's part; should have grepped before claiming. Fix: every reference to `membase/` in the implementation plan is replaced with `membase_export/`. Plus a new test asserts the path consumed matches the path produced by Slice 8.

### F2 (P1) - Driver wave plumbing

**Acknowledged.** The `-001` proposal asserted "the wave parameter at the driver level is already plumbed". This is incorrect: `scripts/rehearse_isolation.py:241` always calls `load_manifest(args.manifest, wave=2)`. M6's positive validation cannot be reached through the CLI path until the driver selects `wave=3` for Wave 3 phases. Fix: implementation plan now includes a phase-to-wave mapping in the driver, plus two new tests covering the CLI path (T18, T19).

### F3 (P1) - Project-root-boundary conflict

**Acknowledged.** The `-001` proposal cited `project-root-boundary.md` while keeping runtime output under `C:/temp/`. These are in conflict. Owner directive 2026-05-01 (S325) resolves the conflict by amending `project-root-boundary.md` to add an explicit sandbox-output exception clause rather than moving runtime output in-root. Owner rationale archived as `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`: Google Drive is syncing `E:`, so moving the rehearsal output in-root would re-introduce the cloud-sync-driven DB corruption pattern that motivated the original §3.3 manifest decision (S311). The amendment text is included inline (see Sandbox Output Exception Amendment section) and lands in the implementation commit alongside the rest of the Wave 3 changes.

### F4 (P2) - DA records archived before proposal references

**Acknowledged.** The three S325 owner decisions are archived in `groundtruth.db` as durable DA records BEFORE this REVISED-1 proposal references them:

- `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE` (v1, `outcome=owner_decision`, `session_id=S325`)
- `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE` (v1, `outcome=owner_decision`, `session_id=S325`)
- `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` (v1, `outcome=owner_decision`, `session_id=S325`)

Approval packet at `.groundtruth/formal-artifact-approvals/2026-05-01-s325-wave3-owner-decisions.json`; SHA256 `f4acfb61132405204d2430b6e09708ce96dae061dc2622d10c6f010b681ffe52`. Inserts performed under `GTKB_FORMAL_APPROVAL_PACKET` env-var-gated `insert_deliberation` calls.

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-isolation-016-phase8-wave3-execution-003.md` (this file)
- `bridge/INDEX.md` updated with `REVISED:` line
- `.groundtruth/formal-artifact-approvals/2026-05-01-s325-wave3-owner-decisions.json` (already landed for F4)

This commit does **not** modify the manifest, `_common.py`, `project-root-boundary.md`, the driver, or land the new sub-script. Those changes ship in the implementation commit after Codex GO. The DA records were committed separately (F4 prerequisite).

## Owner Decisions Encoded (DA-archived)

The three S325 owner decisions cited above govern this proposal. Decision content:

1. `db_reconciliation_strategy = "manifest_driven_filter"` — selected over four alternatives in pre-proposal investigation; resolves §3.6 placeholder.
2. `unclassified_disposition = "leave_behind_with_warning"` — selected over two alternatives; rows where Slice 8 cannot disambiguate are excluded with warnings.
3. Amend `.claude/rules/project-root-boundary.md` to add sandbox-output exception clause permitting `C:/temp/*` runtime paths under owner-approved manifest control.

## Specification Links

The following specifications, rules, decisions, and DA records govern this proposal. Tests in the Specification-Derived Verification section derive from the linked clauses noted.

- **`DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE`** (v1) — owner decision authorizing `manifest_driven_filter` strategy.
- **`DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`** (v1) — owner decision authorizing `leave_behind_with_warning` default.
- **`DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`** (v1) — owner decision authorizing the sandbox-output exception amendment to `project-root-boundary.md`.
- **`ADR-ISOLATION-APPLICATION-PLACEMENT-001`** (upstream commit `affa5a05` per manifest header) — parent architecture decision establishing application/platform separation under `applications/<app>/`. The DB reconciliation strategy must satisfy the ADR's "GT-KB platform records remain outside ordinary app mutation scope" principle.
- **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`** — authority matrix row for `groundtruth.db` (line 115) classifying it as `legacy-exception` with split-required disposition; Owner-Decision-Pending row 1 (lines 143-146) explicitly anticipates "decide whether app-local DA/MemBase remains local, becomes service-backed, or splits into app and product stores during migration." `manifest_driven_filter` is the app-local-records branch of that decision.
- **`.claude/rules/operating-model.md` §3** ("Implemented vs. Intended Surfaces") — names "DA/MemBase service surface" as intended-not-implemented. Wave 3 must not adopt a strategy that depends on absent infrastructure.
- **`.claude/rules/project-root-boundary.md`** — current text mandates all GT-KB artifacts within `E:\GT-KB`. The Sandbox Output Exception Amendment section of this proposal adds a constrained carve-out per `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`. Implementation lands the amendment.
- **`.claude/rules/file-bridge-protocol.md`** — Mandatory Specification Linkage Gate, Mandatory Specification-Derived Verification Gate.
- **`.claude/rules/codex-review-gate.md`** — implementation cannot proceed without Codex GO; tests must derive from linked specifications.
- **`bridge/gtkb-isolation-016-phase8-wave2-implementation-003.md`** §3.1 (Rule M1 contract for `db_reconciliation_strategy` at wave>=3) and `-004.md` Recommended Actions clause "Wave 3 must reject the unresolved `db_reconciliation_strategy` placeholder before verification/reconciliation work" — the conditions Wave 3 must close.
- **`bridge/gtkb-isolation-016-phase8-wave2-slice8-006.md`** (Codex GO) — partition-manifest contract this proposal consumes: schema-discovery, four-category classification, per-table cutover policy. Constraint 1 (unknown table → `status=error`), Constraint 2 (telemetry exclusion), Constraint 4 (silent default to adopter rejected) propagate forward.
- **`scripts/rehearse/_membase_export.py`** lines 1-228, 612, 687, 854 — the existing Slice 8 classifier this lane consumes, with output written to `{output_dir}/membase_export/` (corrected from `-001` per F1).
- **`bridge/gtkb-isolation-016-phase8-rehearsal-implementation-018.md`** (VERIFIED, Wave 1) — driver-dispatch contract this proposal extends with one new lane and a phase-to-wave mapping (per F2).
- **`scripts/rehearse_isolation.py`** line 241 — current driver site that hardcodes `wave=2`; F2 fix changes this to a phase-to-wave mapping.
- **`tests/scripts/test_rehearse_isolation.py`** lines 247-268 — existing driver-wave regression coverage; F2 fix updates to assert the phase-to-wave mapping.
- **`tests/scripts/test_rehearse_membase_export.py`** line 116 — existing Slice 8 path coverage confirming `membase_export/` is the canonical path (corroborates F1 fix).
- **`bridge/gtkb-isolation-016-phase8-wave2-slice8-010.md`** line 45 — Codex live verification recorded the verified artifact at `membase_export/membase-partition-manifest.json` (corroborates F1 fix).
- **`GOV-09`** (CLAUDE.md governance index) — Owner Input Classification Rule; Owner Decisions cited as DA records per F4 fix.
- **`GOV-20`** (CLAUDE.md governance index) — Architecture Decision Workflow; this work item touches an ADR-tagged surface; implementation step creates an IPR document linking Wave 3 work to `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.
- **`.groundtruth/formal-artifact-approvals/2026-05-01-s325-wave3-owner-decisions.json`** — approval packet for the three DA-record inserts that closed F4.

## Sandbox Output Exception Amendment (per F3 / DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE)

The implementation commit lands the following addition to `.claude/rules/project-root-boundary.md` (appended after the existing "Operational Consequences" section):

```markdown
## Sandbox Output Exception

GT-KB rehearsal-class operations may emit runtime output to a path outside
`E:\GT-KB` when ALL of the following hold:

1. The path is declared in an owner-approved manifest field (currently
   `output_dir` in
   `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`).
2. The path matches a sandbox-allowlist pattern enforced by Rule M2 in
   `scripts/rehearse/_common.py` (currently `C:/temp/*`).
3. The output is regenerable evidence (preview artifacts, classification
   manifests, dry-run DBs), not canonical project state.
4. The output is documented in the bridge proposal that authorizes the
   operation, and the bridge passes Codex review with the path explicit.

Source: `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE` and the
manifest §3.3 owner decision recorded at S311 (commit `12538b97` context).
Rationale: rehearsal output must avoid cloud-sync corruption (Google Drive
currently syncs `E:`); the in-root `.driveignore` mechanism per commit
`12538b97` adds a per-path enumeration burden that does not scale with
rehearsal cardinality.

Outputs covered by this exception remain outside the scope of GT-KB
canonical state, audit history, release evidence, regression tests
(except as preview-evidence inputs), and dependency closure.

Owner approval is per-manifest, not per-run; adding new sandbox paths
requires a new owner-approved manifest update through the bridge protocol.
```

This amendment is constrained: it does not open `E:\GT-KB`'s root-boundary to arbitrary external paths. Sandbox paths are owner-approved-per-manifest, allowlist-enforced, regenerable, and documented in the authorizing bridge.

## Strategy Decision Rationale (carried forward, unchanged from `-001`)

Five candidate strategies investigated. `manifest_driven_filter` selected because: (a) reuses Slice 8's row-level partition manifest; (b) avoids absent infrastructure (DA/MemBase service is intended-not-implemented); (c) telemetry exclusion drops ~99% of 1.0 GB DB size from filter payload; (d) reversibility preserved (legacy DB untouched, mode=ro). Full alternative analysis at `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE`.

## Implementation Plan

Implementation commit (after Codex GO) lands the following changes. Each change cites the linked spec it satisfies.

### Manifest update

**File:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/rehearsal/manifest.toml`

```toml
# Replaces existing line 36:
db_reconciliation_strategy = "manifest_driven_filter"

# New field (added below db_reconciliation_strategy):
unclassified_disposition = "leave_behind_with_warning"
```

Header comment block updated to cite this bridge and the three S325 DELIB IDs.

**Satisfies:** `DELIB-S325-DB-RECONCILIATION-STRATEGY-CHOICE`, `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`, `wave2-implementation-004.md` Recommended Action.

### `_common.py` Wave 3 validation (Rule M6)

**File:** `scripts/rehearse/_common.py`

Adds positive validation for the two new manifest fields. The existing M1 rejection of `OWNER_DECISION_REQUIRED` (`_common.py:332-338`) remains; M6 layers on top by rejecting any value not in the known set.

```python
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

**Satisfies:** Wave 2 `-003.md` §3.1 Rule M1 contract (positive complement).

### `project-root-boundary.md` amendment

**File:** `.claude/rules/project-root-boundary.md`

Append the Sandbox Output Exception section verbatim from this proposal's Sandbox Output Exception Amendment section.

**Satisfies:** `DELIB-S325-PROJECT-ROOT-BOUNDARY-SANDBOX-EXCEPTION-CHOICE`, F3.

### Driver phase-to-wave mapping (per F2)

**File:** `scripts/rehearse_isolation.py`

Two changes:

1. Add a phase-to-wave mapping table:

```python
# Phase-to-wave mapping. Phases that consume Wave 3 manifest fields
# (db_reconciliation_strategy, unclassified_disposition) require wave=3
# manifest validation; all others run with wave=2.
_WAVE_3_PHASES: frozenset[str] = frozenset({"db-filter-dryrun"})

def _wave_for_phase(phase: str) -> int:
    """Return the manifest wave required for a given --phase value.

    `--phase all` is treated as wave=3 once any Wave 3 phase is in the
    DISPATCH_TABLE, because `all` runs every lane including Wave 3.
    """
    if phase in _WAVE_3_PHASES:
        return 3
    if phase == "all":
        return 3 if _WAVE_3_PHASES else 2
    return 2
```

2. Replace the line 241 hardcoded `wave=2` call with:

```python
wave = _wave_for_phase(args.phase)
manifest = load_manifest(args.manifest, wave=wave)
```

**Satisfies:** F2 (CLI path now enforces M6 for Wave 3 phases); `wave2-implementation-004.md` Recommended Action.

### `DISPATCH_TABLE` entry for new lane

**File:** `scripts/rehearse_isolation.py`

Add entry after `("membase", ...)`:

```python
("db-filter-dryrun", "rehearse._db_filter_dryrun", "run"),
```

`PHASE_CHOICES` updates automatically via the existing tuple-comprehension at line 58.

**Satisfies:** `rehearsal-implementation-018.md` driver dispatch contract.

### New sub-script: `scripts/rehearse/_db_filter_dryrun.py`

**File:** `scripts/rehearse/_db_filter_dryrun.py` (new, ~280 LOC estimated).

**Lane name:** `db-filter-dryrun`
**Stage:** D (cross-cutting consumer; depends on `membase` lane output).
**Signature:** `def run(manifest, output_dir, *, args=None) -> dict` — same envelope as existing lanes.

**Algorithm:**

1. Read partition manifest from `{output_dir}/membase_export/membase-partition-manifest.json` (canonical Slice 8 output path per `_membase_export.py:687`+`:854`). If missing, return `status=error` with `reason="partition_manifest_missing"`.
2. Read manifest field `unclassified_disposition` — drives the filter behavior.
3. Open legacy DB read-only via `_open_readonly()` (helper exists in `_membase_export.py:245`).
4. Create output DB at `{output_dir}/db-filter-dryrun/groundtruth-filtered-preview.db`.
5. Copy schema from legacy via `sqlite_master` `CREATE TABLE` statements.
6. For each table category from the partition manifest:
   - **Versioned-artifact tables (12):** insert rows where classification == `adopter`. Skip rows where classification == `framework`. For `unclassified` rows: under `leave_behind_with_warning`, skip and emit one warning per row to `db-filter-warnings.txt`. `carry_forward_to_adopter` and `manual_review_gate` raise `NotImplementedError` in this Wave 3 commit (validator accepts them for forward compatibility).
   - **Relationship tables (2):** insert rows whose parent was inserted in the versioned step. Orphan rows emit warning per Slice 8 Constraint 3.
   - **Excluded telemetry (4):** skip entirely. Per Slice 8 Constraint 2.
   - **Per-session tables (3):** insert rows whose classification is `adopter`.
   - **Unknown tables:** propagate Slice 8's `status=error`; never re-classify.
7. Run `PRAGMA integrity_check`; non-`"ok"` returns `status=error`.
8. Write `db-filter-summary.json` with per-category row counts.
9. Write `db-filter-warnings.txt` (one line per unclassified or orphan row).
10. Write `db-filter-rejects.txt` (one line per framework-classified row excluded).
11. Emit standard `result.json` envelope via `emit_result`.

**Read-only on legacy:** `mode=ro` URI. No writes to `E:/GT-KB/groundtruth.db`.

**Satisfies:** `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, authority matrix `groundtruth.db` row, `wave2-implementation-004.md` Recommended Action.

### Freeze-window runbook

**File:** `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/runbooks/AGENT-RED-CUTOVER-FREEZE-WINDOW-RUNBOOK-2026-05-01.md` (new).

Sections: pre-freeze checks; freeze announcement protocol; run `_db_filter_dryrun`; smoke checks; activation/swap (cross-reference to ISOLATION-018); rollback procedure (delete child DB, resume on legacy); post-freeze validation. In-root per `project-root-boundary.md` (no exception needed for the runbook itself; only the runtime output uses the sandbox exception).

**Satisfies:** ADR operational evidence requirement.

### Tests

**File:** `tests/scripts/test_rehearse_db_filter_dryrun.py` (new). Plus driver-wave regression updates in `tests/scripts/test_rehearse_isolation.py`. Test plan in the Specification-Derived Verification section.

## Output Layout

**Per-run output structure** (corrected per F1):

```
{output_dir}/
  ├── inventory/                          (from Wave 2 Slice 1)
  ├── membase_export/                     (Slice 8 — corrected from -001 'membase/')
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

`db-filter-summary.json` schema unchanged from `-001` Output Layout section.

## Specification-Derived Verification

Each test maps to a linked specification clause. Tests in `tests/scripts/test_rehearse_db_filter_dryrun.py` (T1-T17) and `tests/scripts/test_rehearse_isolation.py` (T18, T19 added per F2).

| # | Test name | Derives from |
|---|---|---|
| T1 | `test_filtered_db_excludes_all_framework_classified_rows` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; authority matrix `groundtruth.db` row |
| T2 | `test_filtered_db_telemetry_tables_have_zero_rows` | Slice 8 Constraint 2 |
| T3 | `test_filtered_db_adopter_row_count_matches_partition_manifest_summary` | Slice 8 contract |
| T4 | `test_unclassified_rows_emit_warning_and_are_not_inserted_under_default_disposition` | `DELIB-S325-UNCLASSIFIED-DISPOSITION-CHOICE`; Slice 8 Constraint 4 |
| T5 | `test_lane_refuses_when_partition_manifest_missing_at_canonical_path` | Algorithm step 1; Slice 8 dependency contract; F1 |
| T6 | `test_lane_propagates_partition_manifest_status_error_for_unknown_table` | Slice 8 Constraint 1 |
| T7 | `test_legacy_db_is_opened_read_only` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; §3.5 owner decision |
| T8 | `test_filtered_db_passes_pragma_integrity_check` | Algorithm step 7 |
| T9 | `test_orphan_relationship_rows_emit_warning_not_silent_drop` | Slice 8 Constraint 3 |
| T10 | `test_lane_is_idempotent_on_re_run` | Slice 3 idempotency contract |
| T11 | `test_lane_writes_only_under_output_dir_db_filter_dryrun_subdir` | Rule M2 sandbox-output-dir contract; sandbox-output exception amendment |
| T12 | `test_load_manifest_wave_3_rejects_unknown_db_reconciliation_strategy` | Rule M6 |
| T13 | `test_load_manifest_wave_3_rejects_unknown_unclassified_disposition` | Rule M6 |
| T14 | `test_load_manifest_wave_3_accepts_manifest_driven_filter` | Rule M6 |
| T15 | `test_load_manifest_wave_2_still_accepts_owner_decision_required_for_db_reconciliation` | Rule M1 backward compatibility |
| T16 | `test_db_filter_summary_json_has_required_keys` | Output Layout schema |
| T17 | `test_lane_raises_NotImplementedError_for_non_default_dispositions` | Implementation Plan explicit scope-deferral |
| **T18** | **`test_main_loads_manifest_at_wave_3_when_db_filter_dryrun_phase_requested`** | **F2 fix; phase-to-wave mapping contract** |
| **T19** | **`test_main_rejects_unresolved_db_reconciliation_strategy_via_cli_when_db_filter_dryrun_requested`** | **F2 fix; CLI must enforce M6 end-to-end** |

Plus a path-corroboration test (T-F1) added to test_rehearse_db_filter_dryrun.py to guard F1: `test_lane_input_path_matches_slice8_output_path_constant` — uses the same module constant as `_membase_export.py` to assert the consumer reads where the producer writes (defense against future drift).

Plus regression coverage: existing `tests/scripts/test_rehearse_isolation.py` (66 tests, with the wave-2 assertion at lines 247-268 updated to assert the phase-to-wave mapping per F2) and `tests/scripts/test_rehearse_dashboard_regen.py` (51 tests + 1 skip per Slice 11) — must remain green.

**Test execution commands** (for the post-implementation report):

```bash
python -m pytest tests/scripts/test_rehearse_db_filter_dryrun.py -q --tb=short --timeout=60
python -m pytest tests/scripts/test_rehearse_isolation.py -q --tb=short --timeout=60
python -m pytest tests/scripts/test_rehearse_membase_export.py -q --tb=short --timeout=60
python -m ruff check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py scripts/rehearse_isolation.py tests/scripts/test_rehearse_db_filter_dryrun.py
python -m ruff format --check scripts/rehearse/_db_filter_dryrun.py scripts/rehearse/_common.py scripts/rehearse_isolation.py tests/scripts/test_rehearse_db_filter_dryrun.py
```

Live smoke run:

```bash
python scripts/rehearse_isolation.py --phase membase --execute --output-dir C:/temp/agent-red-rehearsal-wave3-smoke
python scripts/rehearse_isolation.py --phase db-filter-dryrun --execute --output-dir C:/temp/agent-red-rehearsal-wave3-smoke
```

CLI Wave 3 enforcement smoke (negative test):

```bash
# With manifest still at db_reconciliation_strategy = "OWNER_DECISION_REQUIRED",
# `--phase db-filter-dryrun` must reject:
python scripts/rehearse_isolation.py --phase db-filter-dryrun --manifest path/to/wave2-manifest.toml
# Expected: exit USAGE; stderr cites M1 rejection of OWNER_DECISION_REQUIRED at wave=3.
```

## Risk / Impact

**Filter correctness risk (medium, unchanged from `-001`).** Lane correctness depends entirely on Slice 8 partition manifest. Mitigation: VERIFIED Slice 8 constraints; warnings + rejects auditable; ISOLATION-018 has separate review gate.

**Concurrent-session risk (low for rehearsal, deferred for cutover).** Rehearsal read-only on legacy. Real cutover requires the freeze-window runbook (deferred to ISOLATION-018).

**Forward compatibility (low).** `_VALID_UNCLASSIFIED_DISPOSITIONS` accepts three values; `_db_filter_dryrun.py` only implements `leave_behind_with_warning`; T17 asserts the explicit deferral.

**Sandbox exception scope-creep risk (low-medium).** The amendment opens a constrained carve-out. Mitigation: amendment text restricts the exception to (a) owner-approved manifest control, (b) M2 allowlist patterns, (c) regenerable evidence only, (d) bridge-documented authorization. Future expansion requires owner-approved manifest update through bridge protocol.

**Rollback (trivial).** All outputs under `{output_dir}` (sandbox per Rule M2). Rollback = delete the directory. Legacy DB untouched. Amendment to `project-root-boundary.md` is reversible by revert.

**Token cost (low).** ~280 LOC sub-script, ~30 LOC `_common.py` change, ~25 LOC driver change, ~50 LOC rule amendment, 19 tests, ~50-line runbook. Estimated implementation envelope under 700 LOC total.

## Acceptance Criteria

This REVISED-1 is GO-able when Codex confirms:

1. F1 fix is concrete: every reference to Slice 8 output path uses `membase_export/`.
2. F2 fix is concrete: phase-to-wave mapping in driver + T18 + T19 + updated `test_rehearse_isolation.py:247-268` regression.
3. F3 fix is concrete: sandbox-output exception amendment text inline; constrained scope; cited DA record.
4. F4 fix is concrete: three DELIB-S325-* records exist in `groundtruth.db` and are cited by ID.
5. Specification Links covers all relevant governing artifacts (including the three new DELIB IDs and the rule amendment).
6. Test plan maps every test to a linked specification clause.
7. Output Layout matches the file enumeration in Implementation Plan.
8. Wave 2 backward compatibility is preserved (T15 covers).
9. Scope of the proposal commit is unambiguous and matches what will land.

This proposal closes Codex `wave2-implementation-004.md` Recommended Action and Codex `-002` findings F1, F2, F3, F4.

## Decision Needed From Owner

**Nothing required at GO time.** All three S325 owner decisions are archived.

Optional follow-up after VERIFIED:

- Whether ISOLATION-018 cutover should run the freeze-window runbook or extend it. (Not blocking Wave 3.)
- Whether the warning list of unclassified rows should drive a separate work item for reclassification before ISOLATION-018, or whether ISOLATION-018 absorbs that step. (Not blocking Wave 3.)
- Whether the sandbox-output exception clause should be promoted to a more formal artifact (e.g., a DCL) once the amendment ships. (Not blocking Wave 3.)

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
