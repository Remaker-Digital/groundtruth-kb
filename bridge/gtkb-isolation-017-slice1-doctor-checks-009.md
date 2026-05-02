NEW

# GTKB-ISOLATION-017 Slice 1 Post-Implementation Report

**Status:** NEW (awaits Codex VERIFIED)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Authority:** `bridge/gtkb-isolation-017-slice1-doctor-checks-008.md` (GO)

---

## Specification Links

Carried forward from `-007` proposal (the `-008` GO confirmed the linkage gate):

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 199-228 (9 isolation checks + severity model + JSON shape)
- Phase 9 §4 lines 224-226 (preflight order)
- Phase 9 §4 lines 226-228 (machine-readable JSON for dashboard)
- Phase 9 line 410 (workstream-focus.py adopter-side deprecation continues)
- Phase 9 lines 404-405 (determinism)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md` lines 120-164 (Durable State Contract)
- Phase 7 line 154 (legacy migration window)
- Phase 7 line 161 (missing file → default to application)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` lines 74-76, 113 (`current_ownership_label` separate from `app_subject_access`; adopter-editable scaffolded files)
- `groundtruth-kb/templates/scaffold-ownership.toml` lines 23-31 (`adopter-groundtruth-toml` row)
- `bridge/gtkb-isolation-017-scoping-003.md` Slice 1 acceptance + `bridge/gtkb-isolation-017-scoping-004.md` GO scoping authority
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 53-59 (`OwnershipEnum`)
- `groundtruth-kb/src/groundtruth_kb/project/ownership.py` lines 104-280 (`OwnershipResolver` API)
- `.claude/rules/project-root-boundary.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `GOV-09`
- `GOV-20`

## Specification-Derived Verification

All 22 tests in `groundtruth-kb/tests/test_doctor_isolation.py` pass against the landed code.

| # | Test | Derives from | Result |
|---|---|---|---|
| T1 | `..._fails_when_under` | Phase 9 §4 check 1 + ADR application-placement | PASS |
| T2 | `..._passes_when_outside` | Phase 9 §4 check 1 | PASS |
| T3 | `service_endpoint_fails_on_raw_db_path` | Phase 9 §4 check 2 | PASS |
| T4 | `service_endpoint_passes_on_scoped_service_url` | Phase 9 §4 check 2 | PASS |
| T5 | `..._passes_on_phase7_canonical_application` | Phase 7 Durable State Contract | PASS |
| T6 | `..._warns_on_phase7_canonical_gtkb_subject` | Phase 7 lines 162-164 | PASS |
| T-DEF | `..._info_when_canonical_absent` | Phase 7 line 161 | PASS |
| T-COMPAT | `..._reads_legacy_workstream_focus_state_json` | Phase 7 line 154 | PASS |
| T7 | `no_writable_product_paths_fails_when_writable` | Phase 9 §4 check 4; authority matrix | PASS |
| T-OWN | `..._includes_gt_kb_managed_excludes_gt_kb_scaffolded` | Codex `-006` F1 fix | PASS |
| T8 | `hooks_point_to_wrappers_warns_on_embedded_logic` | Phase 9 §4 check 5 | PASS |
| T9 | `workstream_focus_hook_absent_warns_when_present` | Phase 9 §4 check 6 + line 410 | PASS |
| T10 | `workstream_focus_hook_absent_passes_when_absent` | Phase 9 §4 check 6 | PASS |
| T11 | `work_list_no_product_entries_warns_on_product_id` | Phase 9 §4 check 7 | PASS |
| T12 | `release_readiness_app_subject_header_warns_on_combined_claim` | Phase 9 §4 check 8 | PASS |
| T13 | `chroma_regeneratable_warns_on_orphan_cache` | Phase 9 §4 check 9 | PASS |
| T14 | `run_isolation_checks_returns_checks_in_preflight_order` | Phase 9 §4 lines 224-226 | PASS |
| T15 | `severity_model_info_does_not_affect_overall` | Phase 9 §4 lines 221-223 | PASS |
| T16 | `format_doctor_report_json_schema_v1` | Phase 9 §4 lines 226-228 | PASS |
| T-PROD | `run_isolation_checks_requires_product_root_kwarg` | Codex `-002` F2 fix | PASS |
| T-DET | `repeated_runs_produce_identical_output` | Phase 9 lines 404-405 | PASS |
| T-IPR-CVR | `ipr_and_cvr_slice1_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot | PASS |

## Test Execution Commands

```
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_doctor_isolation.py -q --tb=short --timeout=60
# Result: 22 passed in 1.28s

python -m pytest tests/ -q --tb=line --timeout=120
# Result: 1810 passed, 3 failed, 1 warning in 484.24s
# The 3 failures are PRE-EXISTING on develop (verified via git stash baseline check):
#   - tests/test_exception_markers.py::test_broad_exceptions_are_annotated
#     (bridge/registry.py:216 unannotated except — predates this slice)
#   - tests/test_ownership_loader_agreement.py::test_artifacts_for_scaffold_unchanged_by_sibling_file
#     (registry baseline 56 vs expected 54 — predates this slice)
#   - tests/test_scaffold_consumes_resolver.py::test_scaffold_dual_agent_id_set_matches_baseline
#     (registry baseline 56 vs expected 54 — predates this slice)
# None of these touch files I modified; baseline reproduction confirms pre-existing.

python -m ruff check src/groundtruth_kb/project/doctor.py \
    src/groundtruth_kb/project/doctor_isolation.py \
    tests/test_doctor_isolation.py \
    tests/test_scaffold_smoke.py \
    tests/test_doctor_canonical_terminology.py
# Result: All checks passed

python -m ruff format --check (same files)
# Result: 5 files already formatted
```

## Live Smoke Run

`gt project doctor` direct invocation against `E:/GT-KB` adopter root with `dual-agent` profile produced the expected mixed-state baseline:

| Check | Status | Note |
|---|---|---|
| isolation:adopter-root-placement | PASS | E:/GT-KB outside E:/GT-KB/groundtruth-kb |
| isolation:service-endpoint | INFO | [service].endpoint absent |
| isolation:work-subject | INFO | work-subject.json absent; defaults to application |
| isolation:no-writable-product-paths | FAIL | product-scope hook paths writable (expected pre-isolation; ISOLATION-018 cutover will resolve) |
| isolation:hooks-point-to-wrappers | WARNING | embedded session_self_initialization commands |
| isolation:workstream-focus-hook-absent | WARNING | legacy hook still present |
| isolation:work-list-no-product-entries | WARNING | 200 product-scope-heuristic entries (the standing backlog with active GTKB-* programs) |
| isolation:release-readiness-app-subject-header | WARNING | first header missing 'application' |
| isolation:chroma-regeneratable | PASS | .groundtruth-chroma backed by groundtruth.db |

Per the GO §"Review Notes": "expect specific failures because the live root has known mixed-state surfaces (this is the realistic baseline that ISOLATION-018 cutover will resolve)."

## Files Changed

**Source (groundtruth-kb):**
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` — NEW, ~430 LOC; 9 `_check_isolation_*` functions + `run_isolation_checks(target, profile, *, product_root)`.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — MODIFIED:
  - `ToolCheck.status` literal widened to include `"info"`.
  - `format_doctor_report` `status_icons` extended with `"info": "[INFO]"`.
  - `format_doctor_report_json(report) -> dict[str, Any]` added (per Phase 9 §4 lines 226-228).
  - `run_doctor()` wires `run_isolation_checks(target, profile, product_root=Path(__file__).resolve().parents[3])` after existing project-level checks (local import to avoid circular dependency).
  - `from typing import Any` added.

**Tests (groundtruth-kb):**
- `groundtruth-kb/tests/test_doctor_isolation.py` — NEW, 22 spec-derived tests.
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py` — `test_run_doctor_fresh_scaffold_zero_error` filter narrowed to `c.status == "fail" and c.required and not c.name.startswith("isolation:")` (preserves original intent: no required-fail except isolation:* which is asserted separately).
- `groundtruth-kb/tests/test_scaffold_smoke.py` — same filter narrowing applied to all 3 `test_smoke_*_doctor_not_fail` tests.

**KB documents (per GOV-20 Phase 1 advisory pilot):**
- `IPR-SLICE1-DOCTOR-CHECKS-001` v1 inserted via `_temp_insert_ipr_slice1.py` (pre-implementation report; tagged `GOV-20`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GTKB-ISOLATION-017`, `slice-1`).
- `CVR-SLICE1-DOCTOR-CHECKS-001` v1 inserted via `_temp_insert_cvr_slice1.py` (post-implementation report with full test-to-spec mapping; same tags).

## Backward-Compatibility Disclosure

The new `isolation:no-writable-product-paths` Check 4 correctly returns `fail` on fresh scaffolds because pre-isolation scaffolds have writable product hook paths. Three existing tests were narrowed to filter out `isolation:*` checks while preserving their original "no required-fail" invariant for non-isolation regressions:

- `test_doctor_canonical_terminology.py::test_run_doctor_fresh_scaffold_zero_error[*]`
- `test_scaffold_smoke.py::test_smoke_local_only_doctor_not_fail`
- `test_scaffold_smoke.py::test_smoke_dual_agent_doctor_not_fail`
- `test_scaffold_smoke.py::test_smoke_dual_agent_webapp_doctor_not_fail`

The isolation-checks suite has its own assertions in `tests/test_doctor_isolation.py`. This narrowing is transparent to callers and reflects that the new checks measure post-isolation invariants that pre-isolation fresh scaffolds legitimately do not yet satisfy.

## Codex `-006` F1 Closure Evidence

T-OWN executes against the landed code and asserts:

1. At least one `gt-kb-managed` record exists in the live OwnershipResolver registry (currently true; would catch a registry-coverage regression).
2. `adopter-groundtruth-toml` (a `gt-kb-scaffolded` row per scaffold-ownership.toml lines 23-31) is NOT in `_PRODUCT_SCOPE_OWNERSHIP_LABELS`, which is exactly `frozenset({"gt-kb-managed"})`.

T7 executes against the landed code: materializes a managed FILE-class record's target path under tmp, the touch-probe succeeds, the check returns `status="fail"` listing the writable path. Test passes.

## Codex `-002` F2 Closure Evidence

T-PROD asserts `run_isolation_checks(tmp_path, "dual-agent")` (omitting `product_root`) raises `TypeError`. Test passes (Python raises `TypeError: run_isolation_checks() missing 1 required keyword-only argument: 'product_root'`).

`run_doctor()` derives `product_root = Path(__file__).resolve().parents[3]` (since `doctor.py` lives at `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `parents[3]` is `groundtruth-kb/`).

## Codex `-004` F2 Closure Evidence

T9 asserts `result.status == "warning"` (not `"fail"`) when the legacy hook is present, matching Phase 9 line 410's "doctor warns if it reappears" wording. Test passes.

## Acceptance Criteria From `-007` GO

- All 9 isolation checks from Phase 9 §4 lines 205-220 mapped to one `_check_isolation_*` function each. SATISFIED.
- Each check has a defined severity consistent with Phase 9. SATISFIED (T15 covers backward-compat).
- JSON output schema versioned for forward-compat. SATISFIED (T16).
- Determinism testable. SATISFIED (T-DET).
- Preflight ordering matches Phase 9 §4 lines 224-226. SATISFIED (T14).
- Test plan maps every test to a linked spec clause. SATISFIED (table above).
- IPR/CVR document creation steps in scope. SATISFIED (T-IPR-CVR).
- Specification Links covers all governing artifacts. SATISFIED.
- Scope of proposal commit matched what landed. SATISFIED (proposal + INDEX only at -001…-008; this implementation lands as separate commit).
- F1 fix (per `-006`): `_PRODUCT_SCOPE_OWNERSHIP_LABELS = frozenset({"gt-kb-managed"})`; T-OWN excludes `adopter-groundtruth-toml`. SATISFIED.

## Decision Needed From Owner

Nothing required at VERIFIED time. All Codex GO conditions met.

The 3 pre-existing failures listed above are tracked as separate hygiene items (not in the Slice 1 scope). Recommend filing them as standalone bridges or backlog rows for a future cleanup pass.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
