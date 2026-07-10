REVISED

# Bridge Implementation Report - gtkb-wi5066-dispatch-wrapper-commandline-redaction - 009

bridge_kind: implementation_report
Document: gtkb-wi5066-dispatch-wrapper-commandline-redaction
Version: 009 (REVISED)
Responds to: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-008.md
Approved proposal: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md
GO verdict: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066
Recommended commit type: fix:

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::init gtkb pb

## Implementation Claim

Accepted the `-008` NO-GO correction. WI-5066 is independently finalizable now and is not blocked on WI-5041. This report claims exactly the two wrapper files that implement and test the `run_with_status.py --config-env` / `GTKB_RUN_WITH_STATUS_CONFIG_B64` contract:

- `scripts/run_with_status.py`
- `platform_tests/scripts/test_run_with_status.py`

The dirty dispatcher files are not claimed by WI-5066. The dispatcher-side opaque-runner/config-env invocation is already present in `HEAD`; the currently dirty dispatcher delta belongs to WI-5041 and must remain excluded from WI-5066 finalization.

## Findings Addressed

### F1 [P1] "WI-5066 is blocked on WI-5041" is contradicted by canonical state

Response: Accepted. This report withdraws the blocked-on-WI-5041 framing. WI-5066 should be VERIFIED with a two-file include set covering only `scripts/run_with_status.py` and `platform_tests/scripts/test_run_with_status.py`.

### F2 [P1] Broken-HEAD hazard: HEAD dispatcher invokes a wrapper contract HEAD wrapper cannot honor

Response: Accepted. The wrapper delta is the HEAD repair. It adds config-env payload mode while preserving the existing positional `<status> <cmd>` mode, so existing callers remain supported.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - finalization must use the bridge VERIFIED helper with a scoped include set.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this implementation report carries forward the approved WI-5066 proposal and GO thread.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - wrapper behavior is covered by the focused `test_run_with_status.py` suite and code-quality gates.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH, project, work item, and target-path metadata are preserved.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the requested finalization set is limited to WI-5066-owned files.

## Owner Decisions / Input

No new owner decision is required. This is a Prime-autonomous correction under the already approved WI-5066 GO and project authorization.

## Prior Deliberations

- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-004.md` - prior NO-GO on atomic-boundary isolation.
- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-006.md` - prior NO-GO that confirmed wrapper logic quality but rejected the falsely clean boundary.
- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-008.md` - current NO-GO correcting the WI-5041 dependency premise and identifying the broken-HEAD hazard.
- `bridge/gtkb-wi5041-dispatcher-thread-reoffer-backoff-003.md` - sibling implementation report that owns the dirty dispatcher delta and is excluded from this report.
- `DELIB-202665778` - prior finalization include-set discipline precedent cited by Loyal Opposition.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This report requests a two-file VERIFIED include set only: `scripts/run_with_status.py` and `platform_tests/scripts/test_run_with_status.py`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/test_run_with_status.py` passed and covers config-env payload mode plus legacy positional behavior. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `git status --short -- scripts/run_with_status.py platform_tests/scripts/test_run_with_status.py` shows exactly the two WI-5066 wrapper files dirty for this finalization boundary. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries PAUTH, project, and WI metadata. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_run_with_status.py -q --tb=short --basetemp .harness-tmp\wi5066-wrapper-refile`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\run_with_status.py platform_tests\scripts\test_run_with_status.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\run_with_status.py platform_tests\scripts\test_run_with_status.py`
- `git status --short -- scripts/run_with_status.py platform_tests/scripts/test_run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`

## Observed Results

- `pytest`: `13 passed, 1 warning`.
- `ruff check`: `All checks passed!`.
- `ruff format --check`: `2 files already formatted`.
- `git status` confirms the WI-5066 wrapper files are dirty; dirty dispatcher files remain excluded as WI-5041-owned.

## Files Changed

- `scripts/run_with_status.py`
- `platform_tests/scripts/test_run_with_status.py`

## Acceptance Criteria Status

- Implemented: wrapper accepts `--config-env` and decodes `GTKB_RUN_WITH_STATUS_CONFIG_B64`.
- Implemented: legacy positional mode remains covered.
- Implemented: finalization boundary is now exactly the two wrapper files.
- Excluded: `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are WI-5041-owned dirty files and must not be staged under WI-5066.

## Risk And Rollback

Risk is low. The wrapper delta is additive and preserves positional mode. Rollback is a two-file revert of `scripts/run_with_status.py` and `platform_tests/scripts/test_run_with_status.py`, but doing so would reintroduce the HEAD dispatcher/wrapper contract mismatch identified in `-008`.

## Loyal Opposition Asks

1. Verify with a two-file include set:
   - `scripts/run_with_status.py`
   - `platform_tests/scripts/test_run_with_status.py`
2. Do not include WI-5041 dispatcher files in the WI-5066 finalization commit.
