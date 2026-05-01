NEW

# GTKB-ISOLATION-017 Slice 1 Implementation: Isolation Doctor Checks

**Status:** NEW (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Predecessor:** `bridge/gtkb-isolation-017-scoping-003.md` REVISED-1, GO at `-004`. Slice 1 is the first slice in the 8-slice plan.
**Owner pre-approval:** per `memory/work_list.md` autonomous-execution clause + S324 priority elevation banner placing GTKB-ISOLATION program at TOP.

---

## Scope Of This Commit

This proposal commit lands ONLY:

- `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md` (this file)
- `bridge/INDEX.md` updated with the `Document: gtkb-isolation-017-slice1-doctor-checks` entry

This commit does **not** modify `doctor.py`, add new modules, land tests, or insert KB documents. Those changes ship in the implementation commit after Codex GO. This explicit scope statement preempts proposal-vs-implementation divergence (a recurring class flagged in GTKB-ISOLATION-016 Wave 3 Codex `-002` F1 and `-010` F1).

## Specification Links

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 199-228 — the 9 isolation doctor checks to implement; severity model definition; preflight order.
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 226-228 — "Doctor output is machine-readable JSON plus a human-readable summary; both feed the adopter's dashboard per Phase 5".
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 404-405 — "Doctor output must be deterministic for identical inputs. A non-deterministic doctor check is a defect, not a feature".
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` line 410 — "Deprecation of `.claude/hooks/workstream-focus.py` continues at the adopter level: doctor warns if it reappears in any adopter root" (this slice implements the doctor side).
- `bridge/gtkb-isolation-017-scoping-003.md` lines 65-77 — Slice 1 acceptance criteria carried forward.
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO) — scoping authority for this implementation slice.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (upstream commit `affa5a05`) — the 9 checks enforce ADR clauses at runtime (especially adopter-root-not-under-product-root, no-writable-product-paths).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md` — authority matrix that the "no writable product paths" check (#4) reads from at runtime.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — existing 1872-LOC doctor surface that Slice 1 extends (`ToolCheck` dataclass, `DoctorReport`, `run_doctor`, `format_doctor_report`).
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` — registry consulted by check #4 (no-writable-product-paths) and check #2 (service-endpoint shape).
- `groundtruth-kb/src/groundtruth_kb/project/profiles.py` — profile system controlling which checks run.
- `groundtruth-kb/tests/` — existing test directory; new test file lands here.
- `.claude/rules/project-root-boundary.md` — all Slice 1 implementation lands under `E:\GT-KB`. Sandbox-output exception does not apply (no runtime output-dir; this is in-source code).
- `.claude/rules/file-bridge-protocol.md` — Specification Linkage Gate, Specification-Derived Verification Gate.
- `.claude/rules/codex-review-gate.md` — Codex GO required before implementation; tests must derive from linked specs.
- `GOV-09`, `GOV-20` — governance: no owner decisions in Slice 1; IPR/CVR documents per Phase 1 advisory pilot.

## Owner Decisions

**None for Slice 1.** Per the scoping Decision Map (`gtkb-isolation-017-scoping-003.md` lines 39-55), all 7 Phase 9 owner decisions are owned by Slices 4, 6, 7, or 8. Slice 1 owns 0.

## Implementation Plan

Implementation commit (after Codex GO) lands the following changes. Each cites the linked spec it satisfies.

### 1. Severity model addition (per Phase 9 §4 lines 221-223)

Phase 9 specifies three severity levels: `error` / `warning` / `info`. The existing `ToolCheck.status` literal accepts `"pass" | "fail" | "warning"`. Mapping:

- Phase 9 `error` → existing `"fail"` (semantics match: blocks upgrade and release-readiness for required checks).
- Phase 9 `warning` → existing `"warning"` (semantics match).
- Phase 9 `info` → NEW `"info"` value added to the literal.

**File:** `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

**Changes:**

```python
# ToolCheck.status literal:
status: Literal["pass", "fail", "warning", "info"] = "pass"

# DoctorReport._compute_overall update — info-status checks are
# informational and never affect overall verdict:
def _compute_overall(self) -> None:
    if any(c.status == "fail" and c.required for c in self.checks):
        self.overall = "fail"
    elif any(c.status == "warning" for c in self.checks):
        self.overall = "warning"
    else:
        self.overall = "pass"  # "info" status checks treated as "pass"
```

The change is purely additive. Existing checks with `status="pass"|"fail"|"warning"` are unaffected. Backward compatibility is preserved because `_compute_overall` already ignores values not matching `fail` or `warning` for the overall verdict.

**`format_doctor_report` update:**

```python
status_icons = {"pass": "[OK]", "fail": "[FAIL]", "warning": "[WARN]", "info": "[INFO]"}
```

**Satisfies:** Phase 9 §4 severity-model line 221.

### 2. New isolation-checks module: `doctor_isolation.py`

Per the established pattern in `groundtruth-kb/src/groundtruth_kb/project/` (separate modules like `preflight.py`, `ownership.py`), the 9 isolation checks live in a new sibling module.

**File (new):** `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py` (~450 LOC estimated).

**Module exports:** 9 functions, one per check. Each returns a `ToolCheck`.

```python
def _check_isolation_adopter_root_not_under_product_root(target: Path, product_root: Path | None = None) -> ToolCheck: ...
def _check_isolation_service_endpoint_not_raw_db(target: Path) -> ToolCheck: ...
def _check_isolation_durable_work_subject_application(target: Path) -> ToolCheck: ...
def _check_isolation_no_writable_product_paths(target: Path, profile: str) -> ToolCheck: ...
def _check_isolation_hooks_point_to_wrappers(target: Path, profile: str) -> ToolCheck: ...
def _check_isolation_workstream_focus_hook_absent(target: Path) -> ToolCheck: ...
def _check_isolation_work_list_no_product_entries(target: Path) -> ToolCheck: ...
def _check_isolation_release_readiness_app_subject_header(target: Path) -> ToolCheck: ...
def _check_isolation_chroma_regeneratable(target: Path) -> ToolCheck: ...

def run_isolation_checks(target: Path, profile: str, *, product_root: Path | None = None) -> list[ToolCheck]: ...
```

The orchestrator function `run_isolation_checks()` returns the 9 checks in **preflight order** per Phase 9 §4 line 224-226:

> environment boundary (Phase 3) → service reachability (Phase 4) → subject assertion (Phase 7) → registry compliance → app-local governed state health.

Mapping the 9 checks to that order:

1. `_check_isolation_adopter_root_not_under_product_root` — environment boundary; severity `error` (`status="fail"`)
2. `_check_isolation_service_endpoint_not_raw_db` — service reachability; severity `error`
3. `_check_isolation_durable_work_subject_application` — subject assertion; severity `warning` (allows unset on fresh root)
4. `_check_isolation_no_writable_product_paths` — registry compliance; severity `error`
5. `_check_isolation_hooks_point_to_wrappers` — registry compliance; severity `warning`
6. `_check_isolation_workstream_focus_hook_absent` — registry compliance; severity `error` (per Phase 9 line 410: deprecation continues at adopter level)
7. `_check_isolation_work_list_no_product_entries` — app-local state health; severity `warning`
8. `_check_isolation_release_readiness_app_subject_header` — app-local state health; severity `warning`
9. `_check_isolation_chroma_regeneratable` — app-local state health; severity `warning`

Each check function follows the existing `_check_*` pattern: load relevant file/state, evaluate, return `ToolCheck(name=..., required=True, found=..., status=..., message=...)`.

**Per-check decision rules:**

- Check 1: `target.resolve()` MUST NOT be a descendant of `product_root.resolve()` when `product_root` is supplied. If `product_root` is None, derive it from `manifest.find_project_root()` of the GT-KB platform package; if unavailable, status=info ("product root unknown; cannot verify").
- Check 2: read `groundtruth.toml`'s service-endpoint key (`[service]` section, key `endpoint`); if absent → info; if present and value matches a raw DB path pattern (`*.db`, `sqlite:///*.db`) → fail with remediation message; if a scoped service URL (`http://`, `https://`, scheme:adopter-id) → pass.
- Check 3: read durable work-subject record (Phase 7 surface; check `harness-state/*/operating-role.md` or equivalent); if `application` → pass; if unset on fresh-init root → info; if `gt-kb` or other → warning.
- Check 4: from `managed_registry.artifacts_for_doctor(profile)`, get product-scope paths; for each, attempt a write probe (touch a temp file under the path, then immediately remove); if any succeed → fail listing the writable paths.
- Check 5: parse `.claude/settings.json` hook registrations; for each registered command, assert it points to a path under `groundtruth-kb` package or wrapped via `${CLAUDE_PLUGIN_ROOT}`; non-wrapper paths → warning.
- Check 6: existence test: `(target / ".claude/hooks/workstream-focus.py").exists()`; if True → fail (per Phase 9 line 410).
- Check 7: read `memory/work_list.md`; scan for product-scope entries (heuristic: lines mentioning `groundtruth-kb`, GT-KB platform-only IDs, or `gt-kb` subject); count > 0 → warning with line numbers.
- Check 8: read `memory/release-readiness.md`; assert first non-blank header line contains "application" (case-insensitive); assert no combined-subject claim (line containing both "GT-KB" and a green-readiness keyword like "ready" / "verified"); violations → warning.
- Check 9: existence test on `target/.groundtruth-chroma/`; if present, verify regeneratable by checking that authoritative records exist (e.g., `groundtruth.db` non-empty); presence without backing → warning.

**Satisfies:** Phase 9 §4 lines 199-228 (one function per listed check); preflight ordering at line 224-226.

### 3. Wiring into `run_doctor()` (per Phase 9 §4 + scoping bridge)

**File:** `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

Add the call after the existing project-level checks block:

```python
# Isolation checks per Phase 9 §4. Run for all profiles since application/product
# isolation applies regardless of bridge/docker/cloud presence.
from groundtruth_kb.project.doctor_isolation import run_isolation_checks
checks.extend(run_isolation_checks(target, profile))
```

The import is local (inside `run_doctor`) to keep the existing top-of-module imports list small and to allow `doctor_isolation` to import from `doctor` (`ToolCheck`) without circular-import risk.

**Satisfies:** scoping bridge Slice 1 acceptance ("9 new `_check_isolation_*` functions … wired into the doctor flow").

### 4. JSON output: `format_doctor_report_json()` (per Phase 9 §4 line 226-228)

**File:** `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

Add a new sibling to the existing `format_doctor_report()`:

```python
def format_doctor_report_json(report: DoctorReport) -> dict:
    """Machine-readable JSON shape for dashboard ingestion.

    Per Phase 9 §4 line 226-228: doctor output is machine-readable JSON
    plus human-readable summary; both feed the adopter's dashboard per Phase 5.
    """
    return {
        "schema_version": "1",
        "profile": report.profile,
        "overall": report.overall,
        "checks": [
            {
                "name": c.name,
                "required": c.required,
                "found": c.found,
                "version": c.version,
                "min_version": c.min_version,
                "status": c.status,
                "message": c.message,
            }
            for c in report.checks
        ],
    }
```

The function returns a `dict` (caller serializes via `json.dumps()`). Schema is versioned for forward-compat.

**Satisfies:** Phase 9 §4 line 226-228 ("machine-readable JSON … feeds the adopter's dashboard per Phase 5").

### 5. Determinism guarantee (per Phase 9 lines 404-405)

The 9 checks must produce identical output on identical input. Concretely:

- Each check reads filesystem state at call time; deterministic by definition for stable filesystem.
- No use of `time.time()`, `random`, `uuid`, dictionary iteration order across Python invocations (Python 3.7+ dict order is insertion-stable; safe).
- Tests assert this property (T-DET below).

No code changes for determinism beyond standard practice; the test (T-DET) is the load-bearing artifact.

**Satisfies:** Phase 9 §"Regression Visibility" lines 404-405.

### 6. Tests

**File (new):** `groundtruth-kb/tests/test_doctor_isolation.py` (~400 LOC estimated).

Test plan in §Specification-Derived Verification below.

### 7. KB documents (per GOV-20 Phase 1 advisory pilot)

- Pre-implementation: `IPR-SLICE1-DOCTOR-CHECKS-001` document inserted via `db.insert_document()` before code lands. Tagged `GOV-20`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GTKB-ISOLATION-017`, `slice-1`.
- Post-implementation: `CVR-SLICE1-DOCTOR-CHECKS-001` document inserted after smoke + tests pass. Same tags. Documents test-to-spec mapping and live evidence.

## Output Layout (no runtime output for Slice 1)

Slice 1 has no runtime output directory (it's in-source code). The doctor JSON output is consumed in-process by callers; this slice does not write JSON files to disk. The Phase 5 dashboard ingestion consumer will deserialize from `format_doctor_report_json()` results in memory.

## Specification-Derived Verification

Tests in `groundtruth-kb/tests/test_doctor_isolation.py`. Each test maps to a Phase 9 spec clause.

| # | Test name | Derives from |
|---|---|---|
| T1 | `test_check_isolation_adopter_root_not_under_product_root_fails_when_under` | Phase 9 §4 check 1 (line 205); ADR application-placement |
| T2 | `test_check_isolation_adopter_root_not_under_product_root_passes_when_outside` | Phase 9 §4 check 1 |
| T3 | `test_check_isolation_service_endpoint_fails_on_raw_db_path` | Phase 9 §4 check 2 (line 206-207) |
| T4 | `test_check_isolation_service_endpoint_passes_on_scoped_service_url` | Phase 9 §4 check 2 |
| T5 | `test_check_isolation_durable_work_subject_application_passes_on_application` | Phase 9 §4 check 3 (line 208-209) |
| T6 | `test_check_isolation_durable_work_subject_application_warns_on_gt_kb` | Phase 9 §4 check 3 |
| T7 | `test_check_isolation_no_writable_product_paths_fails_when_writable` | Phase 9 §4 check 4 (line 210-211); authority matrix |
| T8 | `test_check_isolation_hooks_point_to_wrappers_warns_on_embedded_logic` | Phase 9 §4 check 5 (line 212-213) |
| T9 | `test_check_isolation_workstream_focus_hook_absent_fails_when_present` | Phase 9 §4 check 6 (line 214-215); Phase 9 line 410 |
| T10 | `test_check_isolation_workstream_focus_hook_absent_passes_when_absent` | Phase 9 §4 check 6 |
| T11 | `test_check_isolation_work_list_no_product_entries_warns_on_product_id` | Phase 9 §4 check 7 (line 216) |
| T12 | `test_check_isolation_release_readiness_app_subject_header_warns_on_combined_claim` | Phase 9 §4 check 8 (line 217-218) |
| T13 | `test_check_isolation_chroma_regeneratable_warns_on_orphan_cache` | Phase 9 §4 check 9 (line 219-220) |
| T14 | `test_run_isolation_checks_returns_checks_in_preflight_order` | Phase 9 §4 line 224-226 (preflight order) |
| T15 | `test_severity_model_info_does_not_affect_overall` | Phase 9 §4 line 221-223 (severity model) |
| T16 | `test_format_doctor_report_json_schema_v1` | Phase 9 §4 line 226-228 (JSON output) |
| T-DET | `test_repeated_runs_produce_identical_output` | Phase 9 §"Regression Visibility" lines 404-405 (determinism) |
| T-IPR-CVR | `test_ipr_and_cvr_slice1_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot |

Plus regression coverage: existing `groundtruth-kb/tests/` suite must remain green (the severity-model addition is purely additive).

**Test execution commands** (post-implementation report):

```bash
cd E:/GT-KB/groundtruth-kb
python -m pytest tests/test_doctor_isolation.py -q --tb=short --timeout=60
python -m pytest tests/ -q --tb=short --timeout=120  # full regression
python -m ruff check src/groundtruth_kb/project/doctor.py src/groundtruth_kb/project/doctor_isolation.py tests/test_doctor_isolation.py
python -m ruff format --check src/groundtruth_kb/project/doctor.py src/groundtruth_kb/project/doctor_isolation.py tests/test_doctor_isolation.py
```

Live smoke run: against the live `E:\GT-KB` adopter root (which is itself an Agent-Red-shaped mixed root) — `gt project doctor --target E:/GT-KB --profile dual-agent` (or equivalent direct call); expect specific failures because the live root has known mixed-state surfaces (this is the realistic baseline that ISOLATION-018 cutover will resolve).

## Risk / Impact

**Severity-model backward compatibility (low):** the literal-type widening from `Literal["pass", "fail", "warning"]` to `Literal["pass", "fail", "warning", "info"]` is a strict superset; existing call sites that use only the original three values are unaffected. The `_compute_overall` logic explicitly ignores `info` — confirmed by T15.

**Check 4 write-probe risk (medium-low):** check 4 attempts a write to product-scope paths; on systems where the test harness has write permissions but production doesn't, the test could behave differently. Mitigation: the write probe is wrapped in try/except; permission errors → `pass` (not writable); successful write → `fail` (writable). The check tolerates filesystem permission variability.

**Heuristic checks (medium):** checks 5, 7, 8 use heuristic patterns to detect violations. Mitigation: heuristics are documented in code with the matching regex patterns; tests fix specific known-violation strings to assert correct flagging; future tightening is a separate slice if false-positive rate proves problematic.

**Determinism risk (low):** the 9 checks read filesystem state at call time; standard Python without random/time-based logic is deterministic. T-DET asserts this.

**Cross-test fixture isolation (low):** each test runs in an isolated `tmp_path` (pytest fixture); no shared state.

**Token cost (low-medium):** ~450 LOC source + ~400 LOC tests + IPR/CVR documents. Estimated implementation envelope under 900 LOC.

## Acceptance Criteria

This proposal is GO-able when Codex confirms:

1. All 9 isolation checks from Phase 9 §4 lines 205-220 are mapped to one `_check_isolation_*` function each.
2. Each check has a defined severity (`error`/`warning`/`info`) consistent with Phase 9.
3. Severity-model addition is backward-compatible (T15 covers).
4. JSON output schema is versioned for forward-compat (T16 covers).
5. Determinism is testable (T-DET covers).
6. Preflight ordering matches Phase 9 §4 lines 224-226 (T14 covers).
7. Test plan maps every test to a linked spec clause; every spec clause has a test.
8. IPR/CVR document creation steps are in scope (T-IPR-CVR covers post-impl).
9. Specification Links covers all governing artifacts.
10. Scope of the proposal commit matches what will land (proposal + INDEX only).

## Decision Needed From Owner

**Nothing required at GO time.** Slice 1 owns 0 of the 7 Phase 9 owner decisions per the scoping Decision Map.

Optional follow-up after VERIFIED:
- Whether check 4 (no-writable-product-paths) should escalate to `error` for all profiles, or remain `error` only for `dual-agent` and weaker for `local-only`. (Not blocking Slice 1; can be tightened in a later cleanup slice if false-positive rate suggests.)
- Whether checks 5, 7, 8 (heuristic) should be supplemented with stricter machine-checkable patterns once registry coverage stabilizes (Slice 2).

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
