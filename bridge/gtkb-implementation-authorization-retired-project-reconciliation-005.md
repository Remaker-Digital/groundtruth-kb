REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019eecf8-b8d2-7d53-a35a-41a1c4634889
author_model: GPT-5
author_model_version: GPT-5 Codex desktop session 2026-06-22
author_model_configuration: Codex desktop default reasoning configuration
author_metadata_source: explicit-codex-runtime-env

# Bridge Revision - Implementation Authorization Retired-Project Reconciliation

bridge_kind: implementation_report
Document: gtkb-implementation-authorization-retired-project-reconciliation
Version: 005 (REVISED; post-implementation report revision)
Responds to: bridge/gtkb-implementation-authorization-retired-project-reconciliation-004.md
Prior implementation report: bridge/gtkb-implementation-authorization-retired-project-reconciliation-003.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4747
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]
Recommended commit type: fix:

## Revision Claim

This revision resolves NO-GO -004 P1 by splitting the unclaimed `target_paths` / `design-only` extraction hunk out of `scripts/implementation_authorization.py`. The live diff for the approved source path now contains only the retired-project PAUTH reconciliation behavior:

- adds `PROJECT_RETIREMENT_RECONCILIATION_CLASS = "project_retirement_reconciliation"`;
- adds `_project_status(...)`;
- preserves `_project_is_active(...)` behavior via `_project_status(...) == "active"`;
- allows a PAUTH attached to a `retired` project only when `allowed_mutation_classes` contains `project_retirement_reconciliation`;
- keeps retired PAUTHs without that mutation class, and all other non-active project statuses, denied through the existing active-project authorization error.

The test file still adds only isolated SQLite coverage for active-project pass-through, retired-project allow, and retired-project deny. No closure project DB mutation was performed while addressing this NO-GO.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `.claude/rules/file-bridge-protocol.md`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `WI-4747`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing reliability fast-lane authorization cited by the proposal.
- `bridge/gtkb-implementation-authorization-retired-project-reconciliation-001.md` - approved implementation proposal.
- `bridge/gtkb-implementation-authorization-retired-project-reconciliation-002.md` - GO verdict authorizing the bounded source/test repair.
- `bridge/gtkb-implementation-authorization-retired-project-reconciliation-004.md` - NO-GO requiring the unclaimed target-path/design-only hunk to be removed or separately governed.

## Owner Decisions / Input

No new owner input is required. This revision narrows the worktree to the already-approved WI-4747 reliability repair instead of expanding scope.

## Findings Addressed

### P1 - VERIFIED finalization would commit unclaimed behavior in `scripts/implementation_authorization.py`

Response: Resolved by removing the unclaimed target-path/design-only extraction hunk from `scripts/implementation_authorization.py`.

Current `git diff -- scripts\implementation_authorization.py platform_tests\scripts\test_implementation_authorization.py` shows no changes to `TARGET_PATHS_RE` and no `design-only` handling in `extract_target_paths(...)`. The source diff now contains only the retired-project reconciliation hunk and the focused tests.

## Scope Changes

Scope is narrowed relative to report -003:

- Removed from the live repair diff: the pre-existing `target_paths` / `design-only` extraction behavior.
- Retained in scope: the GO-002 retired-project PAUTH reconciliation source/test repair.

No WI-3350 parent/subproject inheritance behavior, WI-3510 `included_work_item_ids` behavior, public CLI/schema/bridge runtime change, formal GOV/ADR/DCL/SPEC mutation, deployment, credential work, or closure project DB mutation is included.

## Pre-Filing Preflight Subsection

Commands executed before filing:

```text
groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation
-> preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []

groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation
-> Evidence gaps in must_apply clauses: 0; Blocking gaps (gate-failing): 0; exit code 0
```

## Specification-Derived Verification Plan

| Specification | Executed evidence |
| --- | --- |
| `GOV-RELIABILITY-FAST-LANE-001` | Cleaned diff is a single-concern reliability repair in two approved files. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `begin --bridge-id gtkb-implementation-authorization-retired-project-reconciliation --no-write` succeeded after NO-GO with packet `sha256:063b03157634271232a0ded53b12cff0836d0527026289a605fcd110cf8a3b69`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Source gate reads PAUTH `allowed_mutation_classes` and permits retired project only for `project_retirement_reconciliation`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Work intent was reacquired and implementation-start authorization succeeded before the cleanup edit. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` and `.claude/rules/file-bridge-protocol.md` | This file is the next numbered REVISED response after NO-GO -004. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification links are carried forward above. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests, full auth test module, ruff check, ruff format check, whitespace check, and bridge preflights all passed. |
| `GOV-STANDING-BACKLOG-001` and `WI-4747` | Work remains bound to WI-4747 and the reliability fast-lane PAUTH. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched files are under `E:\GT-KB`; no Agent Red or external-root files were used. |

## Commands Run

- `python scripts\bridge_claim_cli.py claim gtkb-implementation-authorization-retired-project-reconciliation` -> acquired revision claim rowid `16756`.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py begin --bridge-id gtkb-implementation-authorization-retired-project-reconciliation --no-write` -> succeeded; packet_hash `sha256:063b03157634271232a0ded53b12cff0836d0527026289a605fcd110cf8a3b69`; target_path_globs `["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q -k "project_authorization"` -> `3 passed, 89 deselected, 1 warning in 1.86s`.
- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py -q` -> `92 passed, 1 warning in 26.75s`.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` -> `All checks passed!`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` -> `1 file reformatted, 1 file left unchanged`.
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py` -> `2 files already formatted`.
- `git diff --check -- scripts\implementation_authorization.py platform_tests\scripts\test_implementation_authorization.py` -> no output, exit code 0.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation` -> passed.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-implementation-authorization-retired-project-reconciliation` -> passed.

The pytest warning is the existing repository warning `PytestConfigWarning: Unknown config option: asyncio_mode`; it did not fail the suite.

## Files Changed

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_authorization.py`

## Risk And Rollback

Residual risk is limited to PAUTH rows whose `allowed_mutation_classes` JSON is malformed; existing `_json_list` behavior treats malformed/non-list JSON as empty, so retired-project reconciliation remains denied. Rollback is to revert only the two changed files above. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that NO-GO -004 P1 is resolved by the cleaned source diff.
2. Verify the retired-project reconciliation behavior against the tests and preflight evidence above.
3. Return VERIFIED if satisfied; otherwise return NO-GO with findings.
