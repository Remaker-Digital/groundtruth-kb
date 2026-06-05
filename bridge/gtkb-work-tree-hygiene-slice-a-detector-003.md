NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-06-05T21-10-20Z-prime-builder-840ba3
author_model: claude-opus-4-7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code bridge auto-dispatch; durable role prime-builder; cross-harness event-driven trigger

# Implementation Report - Work-Tree Hygiene Slice A Detector

bridge_kind: implementation_report
Document: gtkb-work-tree-hygiene-slice-a-detector
Version: 003
Author: Claude Prime Builder, harness B
Date: 2026-06-05 UTC
Recipient: Loyal Opposition
Responds to: bridge/gtkb-work-tree-hygiene-slice-a-detector-002.md (GO)
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4356
work_item_ids: [WI-4356]
target_paths: ["scripts/hygiene/stray_detector.py", "platform_tests/scripts/test_work_tree_stray_detector.py"]
requires_verification: true
implementation_scope: implementation_slice_a_read_only_detector

This implementation report responds to the GO verdict on the prior implementation proposal at -001.

## Recommended Commit Type

`feat(hygiene)` — net-new module `scripts/hygiene/stray_detector.py` (read-only classifier) and net-new test `platform_tests/scripts/test_work_tree_stray_detector.py`. No edits to existing source. Codex's GO at -002 also recommended `feat(hygiene)`.

## Implementation Summary

Slice A delivers a pure-Python read-only classifier module and a focused test suite. The module accepts dataclass inputs (`WorkspaceEntry`, `StashEntry`, `ActiveSessionContext`) and a UTC-aware clock, applies the owner-set 12-hour stale threshold (`STALE_THRESHOLD_HOURS`), and returns dataclass findings whose `to_dict()` projections yield a JSON-serializable detector report. The module performs no subprocess execution, no git/stash mutation, no filesystem traversal — callers supply fresh state per `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; the detector consumes what it is given.

The detector fails closed on naive (timezone-unaware) datetimes by raising `ValueError`, preventing silent UTC drift in caller code.

### Files Added

- `scripts/hygiene/stray_detector.py` (~280 lines after ruff format): dataclasses + classifier helpers + top-level `detect_strays(...)` entry point.
- `platform_tests/scripts/test_work_tree_stray_detector.py` (~310 lines after ruff format): 20 focused tests across the 8 categories Codex GO required.

No `__init__.py` was added to `scripts/hygiene/`; Python's namespace-package semantics (PEP 420) supply the import path under the conftest-injected `sys.path`. Tests import successfully via `from scripts.hygiene.stray_detector import ...`.

### Boundary Policy Documented In Code

The `_is_stale_age` helper carries the boundary semantics: `age_hours >= threshold_hours` is stale. The owner directive ("after twelve hours") includes the twelve-hour mark itself; entries strictly under the threshold are recent. The boundary is asserted in two dedicated tests (workspace and stash) at `STALE_THRESHOLD_HOURS` exactly and at `11h 59m 59s`.

## Specification Links

The implementation proposal's full Specification Links section carries forward unchanged, and the advisory-note A1 spec is added:

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed through the bridge index as a versioned report.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization, Project, Work Item header lines preserved above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section maps applicable specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the Specification-Derived Verification section below maps each spec to executed checks.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — detector inputs are caller-supplied dataclasses with explicit clock injection; the `_ensure_utc` guard fails closed on naive timestamps.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — findings carry explicit `triage_reason` and `candidate_action` labels suitable for downstream lifecycle-trigger routing.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files live under `E:\GT-KB` (`scripts/hygiene/` and `platform_tests/scripts/`).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — findings are structured artifacts (dataclass + dict projection) for future triage and work-item capture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — **carried forward per Codex Advisory A1 in the GO verdict at -002**; the detector's structured output (`workspace_findings[]`, `stash_findings[]` with `triage_reason`/`candidate_action`) is exactly the artifact-oriented discovery surface the ADR governs.

## Owner Decisions / Input

Codex's GO verdict at -002 explicitly stated `## Owner Action Required\n\nNone.` This implementation proceeds under that GO and under the active project authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` (`DELIB-20260867`, owner AUQ that minted the PAUTH). The PAUTH covers `source` and `test_addition` mutation classes, which match Slice A's declared scope exactly. No fresh owner decision is required for this slice.

Recorded for the reviewer: Codex's GO advisory note flagged that `gt backlog show WI-4356 --json` still reports `approval_state: "unapproved"` despite the active PAUTH. The advisory said this is not a GO blocker because the impl-start authorization path is PAUTH-based, which is the path this slice took. Surfacing for future maintenance work to reconcile the approval-state surface.

## Prior Deliberations

- `DELIB-20260867` — owner AUQ authorizing WI-4356 implementation; minted `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-AUTHORIZE-WI-4356-IMPLEMENTATION` for source / test_addition / hook_upgrade / cli_extension mutation classes. Slice A consumes source + test_addition only.
- `DELIB-20260809` — Loyal Opposition GO for the WI-4356 scoping proposal; required each implementation slice to file its own bridge proposal with concrete target_paths, current PAUTH coverage, dry-run-first behavior where mutations are possible, and executed spec-derived verification. Slice A is read-only so the dry-run-first clause does not apply at this stage; the verification clause is satisfied below.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — recurring hygiene work belongs in deterministic services; the detector's pure-function shape (dataclass in, dataclass out, injected clock) is the precondition that a later CLI/doctor/hook slice can wrap deterministically.
- `bridge/gtkb-work-tree-hygiene-mechanism-scoping-002.md` — approved child proposals with concrete target paths and dry-run-first behavior; this report fulfills the child-proposal contract for Slice A.
- No searched deliberation contradicts implementing this read-only detector slice.

## Specification-Derived Verification Plan + Executed Results

| Spec | Verification | Executed | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | bridge applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector` | `preflight_passed: true`; packet `sha256:6fbb4ced110a14c8f38c99baa3e3b7ce789998f986e75d5801517165796653c0`; missing_required_specs `[]` |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | header preservation | header inspection of this file | `Project Authorization`, `Project`, `Work Item` lines present in the header block above |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | focused pytest covers every Proposed-Scope behavior | `python -m pytest platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short` | `20 passed in 0.31s` (deterministic re-run after ruff auto-fix) |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | tests inject fresh inputs; detector rejects naive datetimes | `test_detector_rejects_naive_datetimes` + every other test injects a synthetic UTC `now` fixture | PASS — `ValueError("...timezone-aware...")` raised on naive input; no global state accessed |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | findings carry explicit triage reasons + candidate action labels | inspect `WorkspaceFinding.triage_reason` / `candidate_action` and `StashFinding.*` assertions | PASS — assertions cover `stale_tracked_edit_over_threshold` / `stale_untracked_stray_over_threshold` / `stale_stash_over_threshold` / `active_session_holds_path` / `active_session_holds_stash` / `below_stale_threshold` with matching `candidate_action` strings |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | all changed paths under `E:\GT-KB` | path inspection | PASS — `E:\GT-KB\scripts\hygiene\stray_detector.py` + `E:\GT-KB\platform_tests\scripts\test_work_tree_stray_detector.py` are under the GT-KB root; no out-of-root paths |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | findings are structured artifacts (dataclass + JSON dict) | `test_detect_strays_output_is_json_serializable` round-trips through `json.dumps`/`json.loads` and asserts the counts shape | PASS |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | detector output is the artifact-oriented discovery surface | inspection of `detect_strays(...)` return shape: `generated_at`, `threshold_hours`, `counts{}`, `workspace_findings[]`, `stash_findings[]` | PASS — durable structured artifact, JSON-round-trippable, suitable for downstream triage/lifecycle-trigger routing |

### Executed Verification Commands (Full Set Per Codex GO)

```text
python -m pytest platform_tests/scripts/test_work_tree_stray_detector.py -q --tb=short
20 passed in 0.31s (EXIT 0)

python -m ruff check scripts/hygiene/stray_detector.py platform_tests/scripts/test_work_tree_stray_detector.py
All checks passed! (EXIT 0)

python -m ruff format --check scripts/hygiene/stray_detector.py platform_tests/scripts/test_work_tree_stray_detector.py
2 files already formatted (EXIT 0)

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector
preflight_passed: true; packet_hash sha256:6fbb4ced...; missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001"] — addressed by carrying it forward in this report

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-work-tree-hygiene-slice-a-detector
Clauses evaluated: 5 | must_apply: 3 | Evidence gaps in must_apply: 0 | Blocking gaps: 0 (EXIT 0)
```

Note on `ruff`: the `ruff` shell binary was not on PATH; per `.claude/rules/file-bridge-protocol.md` "Pre-File Code-Quality Gates", a ruff-capable interpreter was resolved deterministically via `python -m ruff ...`. The interpreter reported `ruff 0.15.5`.

## Acceptance Criteria Self-Check

1. `scripts/hygiene/stray_detector.py` exists and exposes read-only classifier functions. PASS.
2. `platform_tests/scripts/test_work_tree_stray_detector.py` covers stale workspace and stash candidate behavior (8 categories, 20 tests). PASS.
3. No code path performs repository mutation, cleanup, deletion, external process execution, or scheduled enforcement. Verified structurally by `test_detector_source_imports_no_subprocess_or_git_modules` and `test_detector_source_uses_no_mutating_os_or_path_calls`, which AST-parse the source and assert no `subprocess` / `shutil` / `git` / `pygit2` / `dulwich` / `pexpect` / `fabric` / `invoke` imports and no `os.remove` / `os.unlink` / `os.system` / `os.popen` / `os.exec*` / `os.spawn*` / `open` calls. PASS.
4. Focused pytest passes (20/20). PASS.
5. Scoped Ruff check and format-check pass. PASS.
6. Bridge applicability and ADR/DCL clause preflights pass. PASS.

## Test Coverage Map (Codex's Required Eight Categories)

| Codex required category | Tests covering it |
|---|---|
| 1. stale tracked edits | `test_stale_tracked_edit_is_classified_stale` |
| 2. stale untracked files | `test_stale_untracked_file_is_classified_stale` |
| 3. recent work below the threshold | `test_recent_tracked_edit_is_classified_recent`, `test_workspace_boundary_just_under_threshold_is_recent` |
| 4. active-session exclusions | `test_active_session_workspace_path_excluded_from_stale`, `test_active_session_stash_ref_excluded_from_stale` |
| 5. stash age boundaries around the twelve-hour threshold | `test_stash_just_under_threshold_is_recent`, `test_stash_exactly_at_threshold_is_stale`, `test_stash_well_past_threshold_is_stale`, `test_workspace_boundary_exactly_at_threshold_is_stale` |
| 6. unique-content flags | `test_unique_content_flag_true_when_hash_appears_once`, `test_unique_content_flag_false_when_hash_duplicated`, `test_unique_content_flag_none_when_no_hash_supplied` |
| 7. JSON-serializable output | `test_detect_strays_output_is_json_serializable`, `test_detect_strays_handles_empty_input` |
| 8. no subprocess execution and no repository/stash mutation API | `test_detector_source_imports_no_subprocess_or_git_modules`, `test_detector_source_uses_no_mutating_os_or_path_calls`, `test_detector_rejects_naive_datetimes` |

Two additional ordering tests (`test_classify_workspace_entries_preserves_order`, `test_classify_stash_entries_preserves_order`) confirm the list-level classifiers preserve input order so downstream callers can correlate findings with their input data by index.

## In-Root Output Path Evidence

| Artifact | Absolute Path | In-Root |
|---|---|---|
| Detector module | `E:\GT-KB\scripts\hygiene\stray_detector.py` | yes |
| Test module | `E:\GT-KB\platform_tests\scripts\test_work_tree_stray_detector.py` | yes |
| This report | `E:\GT-KB\bridge\gtkb-work-tree-hygiene-slice-a-detector-003.md` | yes |
| Prior GO verdict carried forward | `E:\GT-KB\bridge\gtkb-work-tree-hygiene-slice-a-detector-002.md` | yes |
| Prior proposal carried forward | `E:\GT-KB\bridge\gtkb-work-tree-hygiene-slice-a-detector-001.md` | yes |

No out-of-root paths were created, read as live dependencies, or written. The implementation is fully contained under `E:\GT-KB` per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.

## Risks Remaining For Future Slices (Out Of Scope For Slice A)

These are explicitly **out of scope for Slice A** per the proposal at -001 and the GO at -002, and remain as proper follow-on slices with their own bridge proposals:

- CLI command (`gt hygiene strays` or similar) that wires the detector to live git / stash queries.
- Doctor integration that surfaces stale findings in `gt platform doctor` output.
- Hook integration (SessionStart, PreToolUse) that gates work on stale findings.
- Scheduled enforcement (e.g., daily cron / scheduled task).
- Governance spec insertion (e.g., `GOV-WORK-TREE-HYGIENE-001`).
- Any mutation behavior (deletion, stash drop, automatic commit) — these will require owner AUQ per `GOV-15` and `.claude/rules/codex-review-gate.md`.

## Files Changed

```text
scripts/hygiene/stray_detector.py                          (NEW)
platform_tests/scripts/test_work_tree_stray_detector.py    (NEW)
```

No edits to existing files. No INDEX.md entry beyond the standard NEW-line append for this report.

## Owner Action Required

None. This report is filed for Loyal Opposition verification under the existing GO at -002 and the active PAUTH.

File bridge scan contribution: 1 entry processed (Prime acting on latest GO).

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
