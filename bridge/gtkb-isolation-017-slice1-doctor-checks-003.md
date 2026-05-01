REVISED

# GTKB-ISOLATION-017 Slice 1 Implementation: Isolation Doctor Checks (Revision 1)

**Status:** REVISED (awaits Codex GO)
**Date:** 2026-05-01 (S325)
**Author:** Prime Builder (Claude Opus 4.7)
**Supersedes:** `bridge/gtkb-isolation-017-slice1-doctor-checks-001.md` (NO-GO at `-002`)
**Addresses:** Codex `-002` findings F1 (Phase 7 work-subject linkage missing; wrong subject surface), F2 (`manifest.find_project_root()` doesn't exist), F3 (Check 4 registry source needs ownership metadata, not just `artifacts_for_doctor`).

---

## Delta-Style Revision

This REVISED-1 is a delta against `-001`. **All sections of `-001` stand unchanged except as noted in NO-GO Acknowledgement below.** Specifically: the severity-model addition (`info` literal), the new module location (`doctor_isolation.py`), the JSON output, the determinism guarantee, the IPR/CVR creation steps, and the proposal-commit scope all carry forward.

## NO-GO Acknowledgement

Codex `-002` identified three real defects in `-001`. All accepted in full; fixes below.

### F1 (P1) - Phase 7 work-subject specification missing; Check 3 wrong surface

**Acknowledged.** The `-001` proposal cited `harness-state/*/operating-role.md` for Check 3 (durable work subject = application). That conflates **role** (`prime-builder`/`loyal-opposition`) with **work subject** (`application`/`gt-kb`). Phase 7 specifies the canonical surface as `<application_root>/.claude/session/work-subject.json` with schema `{schema_version, current_subject, updated_at, updated_by, source, application_root, gtkb_product_root, role_slot, topology_mode}`.

**Fix:**
- Add Phase 7 plan to Specification Links.
- Check 3 now reads `<target>/.claude/session/work-subject.json` and asserts `current_subject == "application"`.
- Phase 7 compatibility: if canonical file absent, read `<target>/.claude/hooks/.workstream-focus-state.json` (one migration window per Phase 7 line 154).
- Phase 7 invalid/stale state behavior: missing file → info ("default to application"); invalid JSON → warning; unknown subject → warning; root mismatch → warning (per Phase 7 lines 159-164).
- T5/T6/T-DEF (new) construct canonical Phase 7 state files, not operating-role records.

### F2 (P1) - `manifest.find_project_root()` does not exist

**Acknowledged.** The `-001` proposal referenced `manifest.find_project_root()` for Check 1's product-root fallback; `manifest.py` only exposes `read_manifest()` / `write_manifest()` (no root discovery). Implementation would have failed at import.

**Fix:**
- Remove the fallback to a nonexistent API.
- `run_isolation_checks(target, profile, *, product_root)` makes `product_root` a **required** keyword argument (no default; no fallback).
- `run_doctor()` derives `product_root = Path(__file__).resolve().parents[3]` from `doctor.py`'s location (since `doctor.py` lives at `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `parents[3]` is `groundtruth-kb/`). This is the canonical GT-KB platform installation root.
- New T-PROD test asserts `run_isolation_checks` raises `TypeError` when `product_root` is omitted (confirming no silent-info fallback).
- Documentation comment in `doctor_isolation.py` makes the contract explicit.

### F3 (P2) - Check 4 registry source needs ownership metadata

**Acknowledged.** `-001` used `managed_registry.artifacts_for_doctor(profile)` for Check 4. Per `managed_registry.py:704-709` that helper excludes `ownership-glob` rows, but ownership-glob rows carry path ownership metadata for GT-KB-managed runtime paths. Check 4 would miss any product-scope path expressed only as ownership-glob.

**Fix:**
- Check 4 now uses `OwnershipResolver` from `groundtruth_kb.project.ownership` (per `managed_registry.py:697`: "Callers needing every record (including ownership-glob) should use ... the OwnershipResolver query API").
- Concrete query: enumerate both FILE-class registry rows and ownership-glob rows; for each, call `resolver.classify_by_id(record_id)`; check filters to `OwnershipMeta.ownership in {"product", "shared-evolved"}` (per `ownership.py` enum) where the path is product-scope and not adopter-divergent.
- New T-OWN test: at least one ownership-glob-backed product path is included in the writable-test set.
- Tightened T7 assertion: enumerate ALL product-scope paths (FILE + glob), not just the doctor-required subset.

## Specification Links

All Specification Links from `-001` carry forward. New addition for F1:

- **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md` lines 120-164** — Durable State Contract specifying `.claude/session/work-subject.json` location and schema; compatibility window for `.claude/hooks/.workstream-focus-state.json`; invalid/stale state behavior. Check 3 derives directly from these clauses.

Re-cited briefly here for compliance-gate verification:

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 199-228 (9 isolation checks + severity model)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 226-228 (JSON output for dashboard)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 404-405 (determinism)
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` line 410 (workstream-focus-hook deprecation continues at adopter level)
- **`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md`** (NEW per F1)
- `bridge/gtkb-isolation-017-scoping-003.md` Slice 1 acceptance + `-004.md` Codex GO scoping authority
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (1872 LOC)
- `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py` lines 688-763 (`load_managed_artifacts`/`artifacts_for_*`/`OwnershipResolver` callout at line 697-698)
- **`groundtruth-kb/src/groundtruth_kb/project/ownership.py`** lines 141-200 — `OwnershipResolver.classify_by_id()` and `classify_path()` (NEW per F3)
- `groundtruth-kb/src/groundtruth_kb/project/profiles.py`
- **`groundtruth-kb/src/groundtruth_kb/project/manifest.py`** lines 33+64 — actual exported APIs (`read_manifest`, `write_manifest`); no `find_project_root` exists (per F2)
- `groundtruth-kb/tests/`
- `.claude/rules/{project-root-boundary, file-bridge-protocol, codex-review-gate}.md`
- `GOV-09`, `GOV-20`

## Replacements To `-001`

The following sections of `-001` are **replaced** by the text below. All other sections of `-001` carry forward unchanged.

### Replaces `-001` Implementation Plan §2 Check 3 (per F1 fix)

**Check 3 — durable work subject = application** (per Phase 7 Durable State Contract):

```python
def _check_isolation_durable_work_subject_application(target: Path) -> ToolCheck:
    """Check 3 per Phase 9 §4 line 208-209.

    Reads canonical Phase 7 state at `<target>/.claude/session/work-subject.json`
    per Phase 7 §"Durable State Contract" lines 120-164. Falls back to
    `<target>/.claude/hooks/.workstream-focus-state.json` for one migration
    window per Phase 7 line 154.
    """
    canonical = target / ".claude" / "session" / "work-subject.json"
    legacy = target / ".claude" / "hooks" / ".workstream-focus-state.json"

    state_path = canonical if canonical.exists() else (legacy if legacy.exists() else None)

    if state_path is None:
        # Per Phase 7 line 161: missing file → default to application; info status.
        return ToolCheck(name="isolation:work-subject", required=True, found=False,
                         status="info", message="work-subject.json absent; defaults to application")

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ToolCheck(name="isolation:work-subject", required=True, found=True,
                         status="warning", message=f"invalid JSON at {state_path}; defaulting to application")

    subject = data.get("current_subject")
    if subject == "application":
        return ToolCheck(name="isolation:work-subject", required=True, found=True,
                         status="pass", message="current_subject=application")
    if subject in (None, ""):
        return ToolCheck(name="isolation:work-subject", required=True, found=True,
                         status="info", message="current_subject unset; defaults to application")

    # Phase 7 lines 162-164: unknown subject → warn; root mismatch → warn.
    app_root = data.get("application_root")
    if app_root and Path(app_root).resolve() != target.resolve():
        return ToolCheck(name="isolation:work-subject", required=True, found=True,
                         status="warning", message=f"application_root mismatch: {app_root} vs {target}")
    return ToolCheck(name="isolation:work-subject", required=True, found=True,
                     status="warning", message=f"current_subject={subject!r}; expected application")
```

**Satisfies:** Phase 9 §4 check 3; Phase 7 Durable State Contract lines 120-164.

### Replaces `-001` Implementation Plan §2 Check 1 derivation + signature (per F2 fix)

**Check 1 signature change:** `product_root` becomes a required keyword argument (no fallback).

```python
def _check_isolation_adopter_root_not_under_product_root(
    target: Path,
    product_root: Path,
) -> ToolCheck:
    """Check 1 per Phase 9 §4 line 205. Requires product_root explicitly."""
    target_resolved = target.resolve()
    product_resolved = product_root.resolve()
    try:
        target_resolved.relative_to(product_resolved)
        return ToolCheck(name="isolation:adopter-root-placement", required=True, found=True,
                         status="fail",
                         message=f"adopter root {target} is under product root {product_root}; per ADR-ISOLATION-APPLICATION-PLACEMENT-001 adopters live at <gt-kb-root>/applications/<name>/")
    except ValueError:
        return ToolCheck(name="isolation:adopter-root-placement", required=True, found=True,
                         status="pass", message=f"adopter root {target} is outside product root {product_root}")
```

**Orchestrator signature change:**

```python
def run_isolation_checks(target: Path, profile: str, *, product_root: Path) -> list[ToolCheck]:
    """Returns 9 checks in preflight order. product_root is REQUIRED.

    Per Codex `-002` F2 fix: no `find_project_root` fallback because
    `manifest.py` does not export that API. Caller must supply product_root.
    `run_doctor()` derives it from `Path(__file__).resolve().parents[3]`
    (doctor.py at `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
    means parents[3] is `groundtruth-kb/`).
    """
```

**`run_doctor()` wiring update:**

```python
# In doctor.py:
from groundtruth_kb.project.doctor_isolation import run_isolation_checks
_PRODUCT_ROOT = Path(__file__).resolve().parents[3]
checks.extend(run_isolation_checks(target, profile, product_root=_PRODUCT_ROOT))
```

**New test T-PROD:**

```python
def test_run_isolation_checks_requires_product_root_kwarg(tmp_path):
    """T-PROD per F2 fix: no silent fallback when product_root is omitted."""
    with pytest.raises(TypeError):
        run_isolation_checks(tmp_path, "dual-agent")  # missing product_root
```

**Satisfies:** Phase 9 §4 check 1; F2 closure.

### Replaces `-001` Implementation Plan §2 Check 4 registry source (per F3 fix)

**Check 4 — no writable product paths** (per Phase 9 §4 line 210-211 + authority matrix):

```python
def _check_isolation_no_writable_product_paths(target: Path, profile: str) -> ToolCheck:
    """Check 4 per Phase 9 §4 line 210-211.

    Enumerates ALL product-scope paths (FILE-class + ownership-glob) via
    OwnershipResolver per `managed_registry.py:697` callout. Tests
    writability of each by attempting a write probe wrapped in try/except.
    Probe touches a temp marker file under the path then immediately removes;
    permission errors → not writable; success → writable (violation).
    """
    from groundtruth_kb.project.ownership import OwnershipResolver

    resolver = OwnershipResolver()
    product_paths: list[Path] = []
    for record in resolver.all_records():
        meta = record.ownership_meta()  # method documented in ownership.py
        if meta.ownership in ("product", "shared-evolved"):
            # Resolve path against target adopter root.
            rel = record.target_path() if record.is_file_class() else record.path_glob_literal_prefix()
            if rel:
                product_paths.append(target / rel)

    writable: list[str] = []
    for path in product_paths:
        if not path.exists():
            continue
        probe = path.parent / ".isolation-probe-tmp" if path.is_file() else path / ".isolation-probe-tmp"
        try:
            probe.touch()
            probe.unlink()
            writable.append(str(path))
        except (OSError, PermissionError):
            pass  # not writable — desired

    if writable:
        return ToolCheck(name="isolation:no-writable-product-paths", required=True, found=True,
                         status="fail",
                         message=f"product-scope paths writable from app session: {writable[:5]}{'...' if len(writable) > 5 else ''}")
    return ToolCheck(name="isolation:no-writable-product-paths", required=True, found=True,
                     status="pass", message=f"checked {len(product_paths)} product paths; none writable")
```

Note: the exact `OwnershipResolver` accessor names (`all_records()`, `ownership_meta()`, `target_path()`, `is_file_class()`, `path_glob_literal_prefix()`) are placeholders. Implementation pass will use the actual `ownership.py` API surface (verified at IPR-write time). If the API requires extension to support this query, that is a Slice 1 sub-task documented in the IPR.

**Satisfies:** Phase 9 §4 check 4; authority-matrix `groundtruth.db` row + ownership-glob coverage; F3 closure.

### Replaces `-001` Specification-Derived Verification table (per F1, F3 additions)

| # | Test name | Derives from |
|---|---|---|
| T1 | `test_check_isolation_adopter_root_not_under_product_root_fails_when_under` | Phase 9 §4 check 1; ADR application-placement |
| T2 | `test_check_isolation_adopter_root_not_under_product_root_passes_when_outside` | Phase 9 §4 check 1 |
| T3 | `test_check_isolation_service_endpoint_fails_on_raw_db_path` | Phase 9 §4 check 2 |
| T4 | `test_check_isolation_service_endpoint_passes_on_scoped_service_url` | Phase 9 §4 check 2 |
| **T5** | `test_check_isolation_durable_work_subject_passes_on_phase7_canonical_application` | **Phase 7 Durable State Contract; F1 fix** |
| **T6** | `test_check_isolation_durable_work_subject_warns_on_phase7_canonical_gtkb_subject` | **Phase 7 lines 162-164; F1 fix** |
| **T-DEF** | `test_check_isolation_durable_work_subject_info_when_canonical_absent` | **Phase 7 line 161 (missing file → default-to-application info); F1 fix (NEW)** |
| **T-COMPAT** | `test_check_isolation_durable_work_subject_reads_legacy_workstream_focus_state_json` | **Phase 7 line 154 (compatibility window); F1 fix (NEW)** |
| T7 | `test_check_isolation_no_writable_product_paths_fails_when_writable` | Phase 9 §4 check 4; authority matrix |
| **T-OWN** | `test_check_isolation_no_writable_product_paths_includes_ownership_glob_backed_path` | **F3 fix; ownership-glob coverage (NEW)** |
| T8 | `test_check_isolation_hooks_point_to_wrappers_warns_on_embedded_logic` | Phase 9 §4 check 5 |
| T9 | `test_check_isolation_workstream_focus_hook_absent_fails_when_present` | Phase 9 §4 check 6; line 410 |
| T10 | `test_check_isolation_workstream_focus_hook_absent_passes_when_absent` | Phase 9 §4 check 6 |
| T11 | `test_check_isolation_work_list_no_product_entries_warns_on_product_id` | Phase 9 §4 check 7 |
| T12 | `test_check_isolation_release_readiness_app_subject_header_warns_on_combined_claim` | Phase 9 §4 check 8 |
| T13 | `test_check_isolation_chroma_regeneratable_warns_on_orphan_cache` | Phase 9 §4 check 9 |
| T14 | `test_run_isolation_checks_returns_checks_in_preflight_order` | Phase 9 §4 lines 224-226 |
| T15 | `test_severity_model_info_does_not_affect_overall` | Phase 9 §4 lines 221-223 |
| T16 | `test_format_doctor_report_json_schema_v1` | Phase 9 §4 lines 226-228 |
| **T-PROD** | `test_run_isolation_checks_requires_product_root_kwarg` | **F2 fix (NEW)** |
| T-DET | `test_repeated_runs_produce_identical_output` | Phase 9 lines 404-405 |
| T-IPR-CVR | `test_ipr_and_cvr_slice1_documents_exist_with_adr_tag` | GOV-20 Phase 1 advisory pilot |

Tests added or replaced in this revision: T5 (replaced; canonical surface), T6 (replaced; canonical surface), T-DEF (new; Phase 7 missing-file behavior), T-COMPAT (new; Phase 7 legacy compat window), T-OWN (new; ownership-glob coverage), T-PROD (new; required-kwarg contract).

Total tests: 22 (up from 17 in `-001`).

## Risk / Impact Delta

`-001` Risk/Impact carries forward. Two additions for the F1/F2/F3 fixes:

**Phase 7 schema dependency (low after F1).** Check 3 now consumes a versioned schema (`schema_version: 1` per Phase 7 line 140). If Phase 7 schema evolves, Check 3 becomes stale. Mitigation: T5-T-COMPAT explicitly cite the schema version; future schema revisions will surface via test failures.

**OwnershipResolver API surface assumptions (medium after F3).** The `-003` Check 4 implementation references accessor methods (`all_records`, `ownership_meta`, `target_path`, `is_file_class`, `path_glob_literal_prefix`) whose exact names will be verified at implementation time against `ownership.py`. If the actual API surface is narrower, the IPR explicitly notes any required extension as a Slice 1 sub-task. T-OWN exercises whatever shape lands.

**Required-kwarg behavior (low after F2).** `run_isolation_checks(target, profile, *, product_root)` rejects calls missing `product_root`. T-PROD asserts the TypeError. Existing callers do not exist yet (this is a new entry point), so backward-compat is moot.

## Acceptance Criteria

`-001` acceptance carries forward. F1, F2, F3 add the following:

- **F1:** Phase 7 plan in Specification Links (re-cited above); Check 3 reads `<target>/.claude/session/work-subject.json` per Phase 7 schema; T5/T6/T-DEF/T-COMPAT verify Phase 7-specific behavior.
- **F2:** `run_isolation_checks` requires `product_root` keyword; `run_doctor` derives it from `Path(__file__).resolve().parents[3]`; T-PROD asserts the contract.
- **F3:** Check 4 enumerates product-scope paths via `OwnershipResolver`, including ownership-glob rows; T-OWN includes at least one ownership-glob-backed path in the writable-test set.

## Decision Needed From Owner

**Nothing required at GO time.** All three F1/F2/F3 fixes are mechanical and Codex `-002` explicitly confirmed no owner decision needed for any of them.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
