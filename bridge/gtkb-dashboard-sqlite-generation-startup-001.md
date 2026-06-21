NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Dashboard SQLite not generated; gt status dashboard=UNKNOWN, dashboard reachability degraded at startup

bridge_kind: prime_proposal
Document: gtkb-dashboard-sqlite-generation-startup
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3489

target_paths: ["groundtruth-kb/src/groundtruth_kb/operating_state.py", "groundtruth-kb/tests/test_operating_state.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The dashboard operating-state probe `_probe_dashboard` in `groundtruth-kb/src/groundtruth_kb/operating_state.py` returns `UNKNOWN` with a bare, non-actionable detail ("dashboard SQLite database not generated") when the dashboard SQLite cache is absent. Because `STATUS_ORDER` ranks `UNKNOWN` (1) strictly above `PASS` (0) and `_overall_status` takes the max severity across components, an absent-but-regenerable derived cache degrades the overall `gt status` result and the session-start operating-state line, with no guidance on how to regenerate it. The dashboard SQLite is an explicitly regenerable derived cache (operating-model.md §3 classifies the dashboard as intended-but-partial), and the sibling `_probe_chroma` probe already handles the identical "absent-but-regenerable cache" case with a clear, actionable detail. The dashboard probe should mirror that precedent.

## Defect / Reproduction

Observed incident (origin of WI-3489): at S373 session start, `gt status --component dashboard` reported `UNKNOWN` with detail "dashboard SQLite database not generated", coinciding with degraded dashboard reachability (Grafana health endpoint and GT-KB dashboard URL both unavailable, WinError 10061). The dashboard SQLite at `.groundtruth/dashboard/gtkb-dashboard.sqlite` had simply never been generated for that checkout; it is regenerable via `gt dashboard refresh`.

Reproduction (deterministic): in a project root with no `.groundtruth/dashboard/gtkb-dashboard.sqlite`, call `collect_operating_state(root, components=("dashboard",))`. The current code path (`_probe_dashboard`, line 292-295) returns status `UNKNOWN` with detail `"dashboard SQLite database not generated"`, and the detail names no remediation. Because `UNKNOWN` outranks `PASS` in `STATUS_ORDER`, a project that is otherwise healthy reports a degraded `overall_status` solely due to the absent derived cache. Expected: an absent regenerable cache is reported with an actionable detail that names the regeneration command (paralleling `_probe_chroma`'s "ChromaDB cache is absent and can be regenerated when needed" at line 223), so startup guidance is actionable rather than a bare unknown.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/operating_state.py`, `groundtruth-kb/tests/test_operating_state.py`. No path outside the GT-KB root is read, written, verified, or required.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this defect fix proceeds through the file-bridge protocol (NEW -> GO -> implement -> report -> VERIFIED); bridge `VERIFIED` remains the authoritative terminal signal for the work.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification for the change (mandatory linkage gate).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each test from a cited spec clause and runs them against the implementation (mandatory spec-derived testing gate).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries the Project Authorization / Project / Work Item linkage lines (mandatory project linkage).
- `GOV-STANDING-BACKLOG-001` - WI-3489 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES; the fix is selected from the canonical backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform package (`groundtruth-kb/src/...`) and its platform tests; no adopter/application surface or placement boundary is crossed.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the deterministic operating-state probe surface as a durable, accurate artifact by making the dashboard probe's absent-cache reporting consistent with the regenerable-cache lifecycle.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the operating-state probe is a derived status artifact; the change keeps its reported state consistent with the actual regenerable-cache artifact lifecycle rather than over-reporting degradation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the dashboard probe's "absent regenerable cache" reporting with the regenerable/derived lifecycle state it should reflect, matching the established `_probe_chroma` precedent for the same lifecycle case.

## Requirement Sufficiency

Existing requirements sufficient. The governing authority is the deterministic operating-state probe contract embodied by `operating_state.py` and the regenerable-cache reporting precedent already set by `_probe_chroma` (an absent regenerable cache is reported `UNKNOWN` with an actionable "can be regenerated" detail). `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` already require accurate, durable artifact reporting. This fix brings `_probe_dashboard` into line with that existing contract; it does not introduce or revise any requirement or specification. The WI's alternative framing ("model/display that the dashboard is intended-but-partial") would be a behavior/contract change requiring a new requirement and is explicitly out of scope for this fast-lane defect fix.

## Prior Deliberations

- `DELIB-20262417` - Bridge thread `gtkb-startup-dashboard-reachability-probe` (6 versions, ORPHAN) - prior work on the startup dashboard-reachability probe surface; directly adjacent to this defect's reporting behavior.
- `DELIB-20261035` - GT-KB Dashboard Operations Cockpit Advisory Proposal - dashboard-operations context; confirms the dashboard surface is an intended-but-partial cockpit whose derived cache is regenerable.
- `DELIB-1001` - Loyal Opposition Review, GTKB Dashboard Industry Alignment Slice 1 - dashboard-slice review history establishing the dashboard SQLite as a generated/derived surface.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing authorization via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3489 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, and is bounded to ~1 source file + ~1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active PROJECT-GTKB-RELIABILITY-FIXES membership.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane direction that established PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING; authorizes small reliability/defect fixes to proceed through the bridge under the standing envelope.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3489 (P3 defect) is in that batch.

## Proposed Scope

1. In `groundtruth-kb/src/groundtruth_kb/operating_state.py`, modify the absent-cache branch of `_probe_dashboard` (currently line 292-295). Keep status `UNKNOWN` (the absent regenerable cache is genuinely a not-yet-known state, not a failure), but replace the bare detail with an actionable one that names the regeneration path, mirroring `_probe_chroma` (line 223). Proposed detail: `"dashboard SQLite cache is absent and can be regenerated via 'gt dashboard refresh'"`. The `source` (the dashboard DB path) is retained unchanged so the evidence still points at `.groundtruth/dashboard/gtkb-dashboard.sqlite`.
2. No change to `STATUS_ORDER`, `_overall_status`, the probe registry, the `dashboard` component name, the present/readable branches (lines 296-301), or any other probe. No auto-generation of the SQLite is performed by the status probe (a read-only status probe must not mutate state or run a refresh; generation remains the responsibility of `gt dashboard refresh` / `gt dashboard init`).
3. Add regression tests in `groundtruth-kb/tests/test_operating_state.py` (see verification plan), following the established `test_missing_chromadb_is_unknown_not_crash` pattern.

This is the defect-removal path: it makes the dashboard probe's absent-cache reporting accurate and actionable, consistent with the existing regenerable-cache precedent, without changing platform behavior or adding a requirement.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (probe reports an accurate, actionable artifact state) / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (regenerable-cache lifecycle) | `test_absent_dashboard_cache_is_unknown_with_regeneration_guidance` | With no `.groundtruth/dashboard/gtkb-dashboard.sqlite`, the `dashboard` component status is `UNKNOWN` and its detail names the regeneration path (contains `"regenerated"` and `"gt dashboard refresh"`); it is no longer the bare `"dashboard SQLite database not generated"`. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (derived-status probe must not over-report degradation; no behavior change) | `test_absent_dashboard_cache_does_not_crash_and_keeps_source_path` | The absent-cache probe returns without raising, the `source` still resolves to the `.groundtruth/dashboard/gtkb-dashboard.sqlite` path under the project root, and evidence is an empty dict (parity with the prior absent-cache contract). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no regression to present/readable branch) | `test_present_dashboard_cache_reports_pass_with_table_count` | When a dashboard SQLite with at least one table exists, the `dashboard` component status is `PASS`, the detail is the readable-cache message, and `evidence["tables"]` is the table count (the present/readable branch is unchanged). |

Execution commands:
- `python -m pytest groundtruth-kb/tests/test_operating_state.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/operating_state.py groundtruth-kb/tests/test_operating_state.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/operating_state.py groundtruth-kb/tests/test_operating_state.py`

## Acceptance Criteria

1. With the dashboard SQLite absent, `_probe_dashboard` returns status `UNKNOWN` with an actionable detail that names the regeneration path (`gt dashboard refresh`), instead of the bare "dashboard SQLite database not generated".
2. No platform behavior change: `STATUS_ORDER`, `_overall_status`, the probe registry, the component name, and the present/readable branches are unchanged; the status probe performs no SQLite generation or other mutation.
3. The three derived tests pass; `ruff check` and `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: a downstream consumer asserts on the exact prior detail string "dashboard SQLite database not generated". Mitigation: a repo-wide read-only search shows the string is referenced only in `operating_state.py` itself; no test asserts on it. The new tests assert on the regeneration-guidance substrings rather than the full string, reducing brittleness.
- Risk: over-reach into other probes or into `overall_status` aggregation. Mitigation: the change is confined to the single absent-cache branch of `_probe_dashboard`; `STATUS_ORDER`/`_overall_status` and all sibling probes are untouched, and the present/readable branch is covered by a non-regression test.
- Risk: ambiguity about whether the probe should auto-generate the cache. Mitigation: explicitly out of scope; a read-only status probe must not mutate state. Generation remains with `gt dashboard refresh` / `gt dashboard init`.
- Rollback: revert the single detail-string change in `_probe_dashboard` plus the added tests; the change is a one-line message edit plus tests, fully reversible with no migration.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/operating_state.py`
- `groundtruth-kb/tests/test_operating_state.py`

## Recommended Commit Type

`fix`
