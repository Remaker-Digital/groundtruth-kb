NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-19-project-completion-wi-auto-regex
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# Implementation Report - Project Completion Scanner WI-AUTO Regex Fix

bridge_kind: implementation_report
Document: gtkb-project-completion-scanner-wi-auto-regex-fix
Version: 003
Status: NEW
Author: Prime Builder (Codex / harness A)
Date: 2026-05-19 UTC
Responds to: `bridge/gtkb-project-completion-scanner-wi-auto-regex-fix-002.md`

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3335
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "scripts/project_verified_completion_scanner.py", "groundtruth-kb/tests/test_project_artifacts.py", "platform_tests/scripts/test_project_verified_completion_scanner.py"]

## Summary

Implemented the WI-3335 project-completion scanner regex fix approved in `-002`.

Both project-completion work-item metadata regexes now accept the spec-intake `WI-AUTO-[A-Z0-9-]+` id form while preserving existing `WI-\d+`, `GTKB-*`, and `WORKLIST-*` support. Regression tests cover the package lifecycle path and the standalone scanner path with mixed `WI-AUTO-*` plus numeric `WI-*` verified work items.

## Changes Made

- Updated `_WORK_ITEM_LINE_RE` in `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`.
- Updated `_WORK_ITEM_LINE_RE` in `scripts/project_verified_completion_scanner.py`.
- Added `test_complete_recognizes_wi_auto_verified_work_item` in `groundtruth-kb/tests/test_project_artifacts.py`.
- Added `test_scanner_recognizes_wi_auto_verified_work_item` in `platform_tests/scripts/test_project_verified_completion_scanner.py`.
- Ran `ruff format` on the four authorized target files; this normalized existing long lines in the same files in addition to the functional edits.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` - project completion must recognize VERIFIED work items, including existing spec-intake `WI-AUTO-*` ids.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this report advances the canonical bridge workflow.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - governing spec linkage is preserved.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps implementation behavior to executed tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched paths are in-root and non-application files.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-3335 is a small reliability defect fix.
- `GOV-STANDING-BACKLOG-001` - WI-3335 is tracked in the standing backlog.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, proposal, tests, and report are durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across sibling WI-3322 and this WI-3335 fix.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - GO triggered this implementation report.

## Prior Deliberations

- `gtkb-project-verified-completion-auq-trigger` bridge thread - parent implementation that authored the completion scanner and service paths under WI-3316.
- `gtkb-bridge-compliance-gate-wi-auto-regex-fix` bridge thread - sibling hook-surface fix for the same `WI-AUTO-*` id-shape issue, with no file overlap.

The `-002` Loyal Opposition review found no prior deliberation directly resolving this project-completion scanner defect.

## Spec-Derived Test Mapping

| Specification | Behavior verified | Test |
|---|---|---|
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | `complete_project_authorization()` treats a VERIFIED `WI-AUTO-*` bridge thread as completion evidence and still accepts numeric `WI-*` ids | `test_complete_recognizes_wi_auto_verified_work_item` |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | `completion_ready()` includes `WI-AUTO-*` in `verified_work_item_ids` and marks the authorization ready | `test_scanner_recognizes_wi_auto_verified_work_item` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Both regex copies have named regression coverage | the two tests above plus existing suite |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation paths are in-root target paths | target path inspection and bridge preflights |

## Verification Commands

```text
python -m pytest groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short
```

Observed result: `28 passed, 1 warning`.

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py scripts/project_verified_completion_scanner.py groundtruth-kb/tests/test_project_artifacts.py platform_tests/scripts/test_project_verified_completion_scanner.py
```

Observed result: `4 files already formatted`.

Drift check for the mirrored regex definitions:

```text
groundtruth-kb/src/groundtruth_kb/project/lifecycle.py
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)
scripts/project_verified_completion_scanner.py
_WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*`?(WI-AUTO-[A-Z0-9-]+|WI-\d+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)`?\s*$",
    re.MULTILINE,
)
byte_identical_regex_snippet: True
```

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-completion-scanner-wi-auto-regex-fix
```

Observed result: PASS; `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-completion-scanner-wi-auto-regex-fix
```

Observed result: PASS; `Blocking gaps (gate-failing): 0`.

## Scope Notes

This implementation does not touch the sibling bridge-compliance-gate hook files. It performs no MemBase mutation and no bridge scanner design refactor. The only behavior change is the additive regex branch for existing spec-intake `WI-AUTO-*` work-item ids.

The repository contains unrelated dirty files from other bridge continuations. This report claims only the four authorized target paths listed above.

## Recommended Commit Type

`fix:` because this corrects existing project-completion detection for an id form the platform already produces.

## Risk And Rollback

Risk is low. The new branch is anchored to the full `Work Item:` metadata line and follows the existing uppercase alphanumeric/hyphen shape already used by `GTKB-*` and `WORKLIST-*`. Rollback is removal of the `WI-AUTO-[A-Z0-9-]+` alternation from the two regexes plus deletion of the two new regression tests.

## Owner Action Required

None.
