NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f17f9-c5d6-7562-b210-add13e01ed78
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Report - Windows push governance preflight command and wrapper

bridge_kind: implementation_report
Document: gtkb-wi4257-windows-push-preflight
Version: 003
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE
Work Item: WI-4257

Implemented from: `bridge/gtkb-wi4257-windows-push-preflight-001.md`
Authorized by: `bridge/gtkb-wi4257-windows-push-preflight-002.md`

## Summary

Implemented `WI-4257` by adding a Windows-native `gt push preflight` command and Windows pre-push wrappers that delegate to that command. The implementation mirrors the existing Bash `.githooks/pre-push` behavior: parse Git pre-push stdin tuples, skip deleted refs, scan `remote_sha..local_sha` for existing refs, discover a safe merge-base for new refs, and fail closed when a safe base cannot be determined.

## Implementation Claim

Prime Builder implemented only the approved `WI-4257` target-path scope:

- `groundtruth-kb/src/groundtruth_kb/cli.py` - added the `gt push preflight` command surface.
- `groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py` - added the redacted push range-scan orchestration.
- `.githooks/pre-push.cmd` - added native Windows command-wrapper delegation.
- `.githooks/pre-push.ps1` - added native Windows PowerShell-wrapper delegation.
- `platform_tests/groundtruth_kb/governance/test_push_preflight.py` - added focused tests for range computation, fail-closed new-ref handling, deleted-ref skip behavior, CLI JSON output, and wrapper delegation.

The broader worktree was dirty before this run. This report intentionally lists only the target paths above as this implementation's changed scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-SEC-HOOK-PORTABILITY-001`
- `SPEC-SEC-SCANNER-CLI-001`

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-WINDOWS-GOVERNANCE-PREFLIGHT-SURFACE-BOUNDED-IMPLEMENTATION-2026-06-23` - active project authorization covering `WI-4257`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Work-intent claim acquired for `gtkb-wi4257-windows-push-preflight`; implementation-start packet created from latest `GO` before protected edits. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Implementation report preserves bridge, work item, project, PAUTH, files changed, commands run, and acceptance evidence. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal's Specification Links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused tests exercise each approved acceptance path and were executed against the implementation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Report includes Project Authorization, Project, and Work Item metadata matching the approved proposal. |
| `SPEC-AUQ-POLICY-ENGINE-001` | The implementation consumes existing project authorization evidence and does not request or infer new owner decisions. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Implementation is in platform CLI/governance/hook/test paths, not adopter application scope. |
| `GOV-STANDING-BACKLOG-001` | Implementation is tied to MemBase work item `WI-4257` through the approved bridge thread. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Windows wrappers prefer the project venv and call the Python CLI without Bash-only behavior. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Evidence is preserved in tests and this implementation report. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Report follows the bridge lifecycle after implementation of a latest `GO`. |
| `SPEC-SEC-HOOK-PORTABILITY-001` | Wrapper tests confirm `.cmd` and `.ps1` delegate to `gt push preflight` and avoid direct scanner duplication. |
| `SPEC-SEC-SCANNER-CLI-001` | Push-preflight tests assert the exact redacted `groundtruth_kb secrets scan --range ... --fail-on verified-provider` command behavior. |

## Commands Run

- `python -m pytest platform_tests/groundtruth_kb/governance/test_push_preflight.py platform_tests/groundtruth_kb/governance/test_push_readiness.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py groundtruth-kb/src/groundtruth_kb/governance/push_readiness.py platform_tests/groundtruth_kb/governance/test_push_preflight.py platform_tests/groundtruth_kb/governance/test_push_readiness.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py groundtruth-kb/src/groundtruth_kb/governance/push_readiness.py platform_tests/groundtruth_kb/governance/test_push_preflight.py platform_tests/groundtruth_kb/governance/test_push_readiness.py`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py`

## Observed Results

- Pytest: `11 passed in 0.83s`.
- Ruff check over new governance modules/tests: `All checks passed!`.
- Ruff format check over new governance modules/tests: `4 files already formatted`.
- Ruff check over `cli.py`: `All checks passed!`.
- Ruff format check over `cli.py`: `1 file already formatted`.

## Acceptance Criteria Status

- PASS - Existing-branch updates run a redacted verified-provider range scan for `remote_sha..local_sha`; covered by `test_existing_branch_update_runs_redacted_range_scan`.
- PASS - New-branch pushes discover a safe upstream/origin/main/origin/develop/main/develop base or fail closed; covered by `test_new_branch_uses_safe_merge_base_before_scan` and `test_new_branch_without_safe_base_fails_closed`.
- PASS - Deleted refs are skipped; covered by `test_deleted_ref_is_skipped_without_scan`.
- PASS - Windows wrappers delegate to the canonical command while preferring the project venv; covered by `test_windows_pre_push_wrappers_delegate_to_push_preflight_and_prefer_project_venv`.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/src/groundtruth_kb/governance/push_preflight.py`
- `.githooks/pre-push.cmd`
- `.githooks/pre-push.ps1`
- `platform_tests/groundtruth_kb/governance/test_push_preflight.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: Adds a new CLI/hook capability plus focused test coverage.

## Risk And Rollback

Residual risk is low to moderate because the command is a new push-time gate. The command fails closed on malformed stdin, unsafe new-ref base discovery, scanner runtime failure, or credential-shaped scan findings. Rollback is a revert of the files listed in `Files Changed`; bridge files and project authorization evidence remain append-only.

## Loyal Opposition Asks

1. Verify that `gt push preflight` preserves the approved Bash pre-push scanner semantics.
2. Verify that `.cmd` and `.ps1` wrappers delegate to the canonical CLI and do not duplicate scanner logic.
3. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
