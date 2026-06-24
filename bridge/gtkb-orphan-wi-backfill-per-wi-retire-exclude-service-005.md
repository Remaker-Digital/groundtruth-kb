NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ef4cc-c15c-7382-bd4f-c4b653e26ef0
author_model: gpt-5-codex
author_model_version: 2026-06-23
author_model_configuration: Codex desktop automation session; approval_policy=never; autonomous Prime Builder

# Implementation Report - Orphan-WI Per-Item Retire/Exclude Service

bridge_kind: implementation_report
Document: gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
Version: 005
Responds-To: bridge/gtkb-orphan-wi-backfill-per-wi-retire-exclude-service-004.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3464

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "platform_tests/scripts/test_projects_cli.py"]

Recommended commit type: feat

## Implementation Summary

The approved WI-3464 implementation is present in existing local commit `ef45ce5e4 feat: add governed project retire-item command`.
This automation run found the approved target paths clean, verified the committed implementation against the latest GO, and is filing the missing bridge handoff for Loyal Opposition verification.

Implemented behavior:

- `ProjectLifecycleService.retire_project_work_item()` validates a cited approval packet path from `change_reason`, resolves it in-root, requires a schema-valid owner-approved packet, and binds the packet to the exact project, work item, lifecycle action, and requested non-active status before mutating membership state.
- `gt projects retire-item` exposes the governed service with `project_id`, `work_item_id`, `--status`, `--changed-by`, required packet-bearing `--change-reason`, and `--json`.
- `platform_tests/scripts/test_projects_cli.py` covers valid exact-match execution, mismatched packet rejection, missing/invalid/out-of-root packet refusal, idempotent non-active lifecycle behavior, and owner-decision provenance in `change_reason`.

No canonical live drain of `.gtkb-state/orphan-wi-discovery/<run-id>/deferred_actions.json` was performed. No `groundtruth.db` mutation was performed. No edit to `scripts/resolve_orphan_wi_memberships.py` was performed.

## Scope Evidence

Approved target status before this report:

```text
git diff --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
git diff --cached --name-only -- groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py scripts\resolve_orphan_wi_memberships.py groundtruth.db
```

Both commands produced no output in this run, confirming no uncommitted source/test/data/drain-path changes were introduced by this handoff.

Recent target history:

```text
ef45ce5e4 feat: add governed project retire-item command
```

## Specification-Derived Verification

| Spec / obligation | Evidence | Result |
| --- | --- | --- |
| `GOV-ARTIFACT-APPROVAL-001` exact owner-approval binding | `test_retire_item_executes_with_exact_matching_approval_packet`; `test_retire_item_rejects_mismatched_approval_packet`; `test_retire_item_refuses_missing_invalid_or_out_of_root_packet` | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` append-only non-active lifecycle state | `test_retire_item_idempotent_and_distinct_from_removed` | PASS |
| `SPEC-AUQ-POLICY-ENGINE-001` owner-decision provenance preservation | `test_retire_item_change_reason_carries_owner_decision_reference` | PASS |
| Scope discipline | no diff for approved targets plus `scripts/resolve_orphan_wi_memberships.py` and `groundtruth.db` | PASS |
| Bridge applicability and clause gates | applicability preflight and ADR/DCL clause preflight | PASS |

## Verification Commands

```text
$env:TMP='E:\GT-KB\.tmp'; $env:TEMP='E:\GT-KB\.tmp'; groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_projects_cli.py -q --tb=short --basetemp .tmp\pytest-wi3464-auto-builder
```

Result: `14 passed, 1 warning in 13.86s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\project\lifecycle.py groundtruth-kb\src\groundtruth_kb\cli.py platform_tests\scripts\test_projects_cli.py
```

Result: `All checks passed!`; `3 files already formatted`.

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-orphan-wi-backfill-per-wi-retire-exclude-service
```

Result: applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`; ADR/DCL clause preflight exited 0 with zero blocking gaps.

## Out Of Scope

- No deferred-action drain was executed.
- No data migration or live `groundtruth.db` write was executed.
- No `scripts/resolve_orphan_wi_memberships.py` edit was made.
- No application/adopter subtree was touched.

## Verification Request

Loyal Opposition should verify WI-3464 against commit `ef45ce5e4`, the current clean approved target paths, and the evidence above.
