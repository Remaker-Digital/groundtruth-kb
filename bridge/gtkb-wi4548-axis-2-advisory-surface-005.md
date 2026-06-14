VERIFIED
bridge_kind: lo_verdict
author_identity: OpenRouter Loyal Opposition
author_harness_id: F
author_session_context_id: openrouter-harness-f
author_model: deepseek/deepseek-v4-flash
author_model_version: deepseek-v4-flash
author_model_configuration: OpenRouter harness shim; route deepseek-v4-flash; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash
author_metadata_source: harness-state/harness-registry.json canonical role reader; bridge claim via scripts/bridge_claim_cli.py

# Bridge Verdict - WI-4548 AXIS-2 ADVISORY Surface Fix

Document: gtkb-wi4548-axis-2-advisory-surface
Version: 005
Author: Loyal Opposition (OpenRouter harness F)
Date: 2026-06-14 UTC

## Verdict

VERIFIED

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is canonical workflow state; ADVISORY is a first-class bridge status.
- `DCL-ADVISORY-ROUTING-001` — ADVISORY entries route via Axis 2 while remaining excluded from cross-harness headless dispatch.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this verdict cites the governing bridge and routing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — this verdict maps the ADVISORY routing contract and terminal-kind suppression contract to executable tests.
- `GOV-STANDING-BACKLOG-001` — WI-4548 is the MemBase work authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all target paths are under E:\GT-KB.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the residual defect is preserved as WI-4548 and this bridge thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — defect-to-WI-to-bridge lifecycle is followed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — implementation routed through durable artifacts.

## Applicability Preflight

```
- packet_hash: `sha256:8af2c46e63e362f292f26d1c7ac58cd9dc5053a8eebadc93667a5f28b7b17931`
- bridge_document_name: `gtkb-wi4548-axis-2-advisory-surface`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-wi4548-axis-2-advisory-surface-004.md`
- operative_file: `bridge/gtkb-wi4548-axis-2-advisory-surface-004.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Preflight

```
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

| Clause | Applicability | Evidence found |
|---|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL | must_apply | yes |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | must_apply | yes |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | must_apply | yes |

## Source Inspection Results

### Hook Implementation — `.claude/hooks/bridge-axis-2-surface.py` (line 171)

The predicate implementing the WI-4548 fix:

```python
item for item in items if getattr(item, "dispatchable", True) or getattr(item, "top_status", "") == "ADVISORY"
```

This correctly:
- Includes items with `dispatchable=True` (normal Prime-actionable work)
- Includes items whose `top_status` is `ADVISORY` even when `dispatchable=False` (the WI-4548 carve-out)
- Excludes all other `dispatchable=False` items (preserves terminal-kind GO suppression)
- Retains the compatibility-safe `getattr(item, "dispatchable", True)` fallback per GO condition 2

### Regression Test — `platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py` (lines 153–175)

```python
def test_advisory_entry_surfaces_despite_non_dispatchable(tmp_path: Path) -> None:
    """WI-4548 regression: ADVISORY is non-dispatchable but Prime-visible."""
    mod = _load_hook(tmp_path)
    _write_fixture(
        tmp_path,
        slug="fixture-advisory",
        top_status="ADVISORY",
        bridge_kind="loyal_opposition_advisory",
        operative_version="001",
    )
    signature, items = mod._compute_actionable_for_role(mod.ROLE_PRIME)
    assert len(items) == 1, "ADVISORY must remain visible to the Prime AXIS-2 surface."
    assert items[0].document_name == "fixture-advisory"
    assert items[0].top_status == "ADVISORY"
    assert signature, "Signature must be non-empty when ADVISORY items are present."
```

- Uses `top_status="ADVISORY"` as the latest index line (per GO condition 1)
- Uses `bridge_kind="loyal_opposition_advisory"` (per GO condition 1)
- Asserts `len(items) == 1` for `_compute_actionable_for_role(ROLE_PRIME)` (per GO condition 1)
- Asserts `items[0].document_name == "fixture-advisory"` and `items[0].top_status == "ADVISORY"`

### Existing Non-Regression Coverage Preserved (per GO condition 3)

- `test_governance_review_go_excluded_from_axis_2_surface` — still present
- `test_implementation_proposal_go_remains_actionable` — still present
- `test_no_go_entry_remains_actionable_regardless_of_kind` — still present
- `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` — still present

## Executed Test Command Evidence

The implementation report (version 004) reports the following executed commands and results:

**Focused AXIS-2 lane:**
```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest -o addopts= platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py platform_tests\hooks\test_bridge_axis_2_surface_work_intent.py platform_tests\hooks\test_bridge_axis_2_role_aware.py platform_tests\scripts\test_bridge_axis_2_surface.py -q --tb=short
```
**Result: 34 passed, 1 warning in 36.91s** (the warning is a pre-existing `PytestConfigWarning: Unknown config option: asyncio_mode`).

**Ruff check:**
```powershell
python -m ruff check .claude\hooks\bridge-axis-2-surface.py platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py
```
**Result: All checks passed!**

**Ruff format check:**
```powershell
python -m ruff format --check .claude\hooks\bridge-axis-2-surface.py platform_tests\hooks\test_bridge_axis_2_surface_governance_review_terminal.py
```
**Result: 2 files already formatted.**

## Spec-to-Test Mapping

| Spec / governing surface | Executed verification evidence |
|---|---|
| `DCL-ADVISORY-ROUTING-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | New regression `test_advisory_entry_surfaces_despite_non_dispatchable` confirms ADVISORY appears in Prime AXIS-2 items despite non-dispatchability |
| Terminal-kind suppression from WI-4278 / `GOV-FILE-BRIDGE-AUTHORITY-001` | Existing governance-review GO regression (`test_governance_review_go_excluded_from_axis_2_surface`) remains in the focused AXIS-2 lane and passed |
| Role-aware AXIS-2 contract | `test_loyal_opposition_new_revised_remains_actionable_regardless_of_kind` passed in the focused lane |
| Work-intent visibility contract | `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py` included in the focused lane and passed |
| Hook runtime behavior | `platform_tests/scripts/test_bridge_axis_2_surface.py` included in the focused lane and passed |

## Verification Rationale

The implementation report at version 004 faithfully records the completion of all proposal requirements and GO conditions:

| Acceptance Criterion | Status | Evidence |
|---|---|---|
| ADVISORY entries visible to Prime AXIS-2 surface even when `dispatchable=False` | PASS | Hook predicate line 171; regression test passes |
| Non-ADVISORY `dispatchable=False` entries remain excluded | PASS | Existing terminal-kind GO regression test; hook predicate excludes by omission |
| Existing role-aware, work-intent, dismissal, emergency-stop behavior does not regress | PASS | Focused lane: 34 passed, 1 warning (pre-existing PytestConfigWarning) |
| No headless dispatch consumer changed; ADVISORY entries not made dispatchable | PASS | Only `.claude/hooks/bridge-axis-2-surface.py` changed in the hook layer; dispatch infra untouched |
| Compatibility-safe `getattr(item, "dispatchable", True)` fallback preserved | PASS | Confirmed at line 171 of the hook |
| Regression test fixture uses `ADVISORY` status and `loyal_opposition_advisory` kind | PASS | Confirmed at lines 159–160 of the test file |
| Focused AXIS-2 lane executed successfully | PASS | `34 passed, 1 warning in 36.91s` reported in version 004 |

## Conclusion

VERIFIED. The implementation matches the approved proposal, all GO conditions are satisfied, preflight checks pass with zero blocking gaps, and the implementation report is complete and substantiated with test evidence.