NO-GO

# Verification Verdict - WI-5071 no-window source fixes + reintroduction guard (NO-GO)

bridge_kind: lo_verdict
Document: gtkb-wi5071-no-window-source-fixes-reintroduction-guard
Version: 004
Author: Loyal Opposition (Claude Code, harness B)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-003.md

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 85e78bc0-61f1-4383-84cd-fb4128f29b95
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo

## Verdict: NO-GO (substance verified; report-structure finalize blocker)

WI-5071's implementation is substantively correct and VERIFIED-worthy - all
functional evidence re-ran clean (audit `violation_count: 0`, 11 + 72 tests pass,
ruff clean), the guard is genuinely enforced, the six declared files are
WI-5071-clean, and the commingling hygiene (descoping untracked goose) is exactly
right. The single blocker is a **report-structure defect that prevents clean
VERIFIED-finalization**: the report lists `scripts/goose_harness.py` inside the
`## Files Changed` section (under "NOT committed"), so the VERIFIED-finalize
covers-check (`_assert_include_set_covers_report_claims`) treats it as a required
include path. Including it would commingle WI-5072's untracked file under a WI-5071
commit; excluding it fails the finalize. This is empirically confirmed (below).
The fix is small and does not touch the implementation.

## Applicability Preflight

- packet_hash: `sha256:0f3263c37aea4807c5d3865beab1270f6a3cef253a08027288b886259db84bb0`
- bridge_document_name: `gtkb-wi5071-no-window-source-fixes-reintroduction-guard`
- operative_file: `bridge/gtkb-wi5071-no-window-source-fixes-reintroduction-guard-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"] (advisory only)

## Clause Applicability

- Clauses evaluated: 5; must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0; Blocking gaps: 0 (the NO-GO is a finalizability blocker, not a clause-evidence gap)

## Prior Deliberations

- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` - governing owner directive.
- `bridge/gtkb-wi5071-...-002.md` - the LO GO (Antigravity C, session `0072210b`).
- WI-5052 VERIFIED (`bridge/gtkb-wi5052-dispatcher-codex-no-window-containment-004.md`) - related containment.
- WI-5105 + LO advisory `LO-ADVISORY-2026-07-09-commingled-tree-root-cause.md` - the commingling-hygiene discipline the report correctly applied to goose.

## Specifications Carried Forward

- `GOV-RELIABILITY-FAST-LANE-001`, `ADR-CROSS-HARNESS-PARITY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-STANDING-BACKLOG-001`

## Spec-to-Test Mapping (all independently re-run and PASSING)

| Specification | Command | Executed | Result |
| --- | --- | --- | --- |
| `DELIB-20260707` + `GOV-RELIABILITY-FAST-LANE-001` + `ADR-CROSS-HARNESS-PARITY-001` | `python scripts/windows_no_window_spawn_audit.py` | yes | violation_count 0, release_ready true, exit 0 |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (guard enforced) | `pytest test_windows_no_window_spawn_audit.py` | yes | 11 passed |
| No-regression on touched modules | `pytest <5 touched-module test files>` | yes | 72 passed |
| Code quality | `ruff check` / `ruff format --check` on the 5 changed .py | yes | All passed / 5 already formatted |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (scoped finalization of the 6 files) | VERIFIED-finalize of the 6 files + bridge chain | no | **BLOCKED - see Finding 1** |

## Positive Confirmations (substance is VERIFIED-worthy)

- The three committed source fixes carry real no-window dispositions (`**no_window_subprocess_kwargs()` in verify_codex_dispatch.py; `creationflags = CREATE_NO_WINDOW` in service_sot.py; `-Hidden` in install_ollama_autostart_task.ps1); the audit classifies all fixed sites `compliant_no_window`.
- The reintroduction guard is genuinely enforced (not advisory): `_check_no_window_spawn_audit()` release-gate check converts audit exit-1 -> `GateFailure`; `test_real_tree_has_no_no_window_violations` asserts `violation_count == 0` on the git-tracked tree.
- All 6 declared files are WI-5071-only (every added line on-topic); `git diff --stat` = 53/-2, matching the report; `verify_codex_dispatch.py` +5 layers cleanly on WI-5065's committed repair logic.
- The three deviations (goose descoped; antigravity verifier excluded to preserve `violation_count == 0`, deferred to WI-5113; incidental goose ruff cleanup on-disk-only) are all sound scope calls that preserve the GO'd acceptance.
- Review independence: report author `fea7dd14-...` != reviewer `85e78bc0-...`.

## Findings

### [P2] Finding 1 - `scripts/goose_harness.py` in the `## Files Changed` section blocks VERIFIED-finalization

- **Observation:** The report's `## Files Changed` section lists `` `scripts/goose_harness.py` `` under "NOT committed by this WI". The VERIFIED-finalize covers-check `_claimed_paths_from_report` scans the `Files Changed` section and extracts every repo-path token - including goose - into the required-include set (`.claude/skills/verify/helpers/write_verdict.py` L351-368, L399-409). An actual finalize attempt with `--include` of the 6 committed files + the untracked bridge chain (goose deliberately excluded) failed:
  `VerifiedFinalizationError: VERIFIED finalization include set omits path(s) claimed by latest implementation report for 'gtkb-wi5071-...': scripts/goose_harness.py` (fail-closed; nothing was written or committed).
- **Deficiency rationale:** `scripts/goose_harness.py` is an untracked WI-5072 file the report correctly descoped to avoid commingling (per WI-5105/WI-5112). But because it is named in `Files Changed`, the finalize covers-check demands it in the commit. Including it would `git add -f` the untracked WI-5072 file (plus its incidental ruff cleanup) into a WI-5071-labeled commit - the exact mis-attribution the descope was meant to prevent. Excluding it fails the finalize. The report has no `By-Reference Finalization Waiver` section (the only covers-check bypass). So the report as structured cannot be VERIFIED-finalized, and a file-only VERIFIED is prohibited by the commit-finalization gate.
- **Proposed solution:** Re-file a REVISED report (`-005`) whose `## Files Changed` section lists ONLY the six committed tracked files, and move the `goose_harness.py` descope note entirely into `## Deviations / Scope Notes` (which the covers-check does NOT scan). No implementation change is needed; the on-disk goose fix and the pre-positioned `RELEASE_RUNTIME_FILES` guard entry stay as-is. On re-file, the finalize covers-check demands only the 6 files and completes cleanly.
- **Option rationale:** Restructuring `Files Changed` is the minimal, correct fix - it preserves the (correct) descope while making the committed-path set unambiguous to the finalize machinery. Rejected alternatives: (a) `--include` goose -> re-commingles WI-5072 (the failure mode this whole session has been about); (b) add a By-Reference Finalization Waiver -> inappropriate here (goose is descoped, not committed-by-reference elsewhere; a waiver requires owner evidence the descope does not have).
- **Prime Builder implementation context:**
  - Objective: make the WI-5071 report finalizable on exactly the 6 committed files.
  - Evidence path: `.claude/skills/verify/helpers/write_verdict.py` L351-409 (the covers-check that scans `Files Changed`).
  - File touchpoints: the WI-5071 `-005` REVISED report only (move goose from `Files Changed` to `Deviations / Scope Notes`); no source change.
  - Verification steps: on re-file, an independent LO re-runs the audit + tests (already green) and VERIFIED-finalizes the 6 tracked files + bridge chain.

## Required Revisions

1. Re-file the WI-5071 report (`-005` REVISED) with `## Files Changed` listing ONLY the six committed tracked files; relocate the `scripts/goose_harness.py` descope note to `## Deviations / Scope Notes` so the finalize covers-check demands only the committed set (Finding 1). No implementation change.

## Commands Executed

- Full re-verification (all PASS): `python scripts/windows_no_window_spawn_audit.py` (violation 0); `pytest test_windows_no_window_spawn_audit.py` (11 passed); `pytest <5 touched-module files>` (72 passed); `ruff check` / `ruff format --check` (clean).
- `git status --short` -> 6 files ` M`, goose `??` (untracked); `git diff --stat` -> 53/-2.
- VERIFIED-finalize attempt (6 files + bridge chain, no goose) -> `VerifiedFinalizationError: ... omits path(s) ...: scripts/goose_harness.py` (fail-closed).
- `bridge_applicability_preflight.py` -> preflight_passed true, missing_required_specs []; `adr_dcl_clause_preflight.py` -> exit 0, 0 blocking gaps.

## Owner Action Required

None. Standard NO-GO routed back to Prime Builder for a report-only restructure (no implementation change). No owner decision is required.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
