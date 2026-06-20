NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ee28b-40f4-71f0-b0de-189b442286aa
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: reasoning_effort=xhigh
author_metadata_source: codex_request_meta

# GT-KB Bridge Implementation Report - agent-disposition-wi4591-bridge-disposition-workflow-slice1 - 003

bridge_kind: implementation_report
Document: agent-disposition-wi4591-bridge-disposition-workflow-slice1
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/agent-disposition-wi4591-bridge-disposition-workflow-slice1-002.md
Approved proposal: bridge/agent-disposition-wi4591-bridge-disposition-workflow-slice1-001.md
Recommended commit type: feat:

## Implementation Claim

Implemented WI-4591 Slice 1 by adding a shared bridge disposition matrix and wiring both bridge actionability consumers to it.

The new `groundtruth_kb.bridge.disposition` module defines canonical status, role, owner-visibility, terminal, dispatchability, reason-code, and next-action decisions for `prime-builder` and `loyal-opposition` recipients. `groundtruth_kb.bridge.notify` now sources its compatibility status sets, bridge-kind token sets, dispatchability decision, and recipient actionability from that matrix. `.claude/skills/bridge/helpers/scan_bridge.py` now uses the same matrix for role/status routing while preserving its existing terminal-kind GO suppression and GO activatability preflight.

Regression coverage was added for the shared matrix contract, ADVISORY manual Prime-only behavior, wrong-role reason codes, notify status-set parity, and manual scan helper parity with the shared matrix.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-PROTOCOL-001`
- `.claude/rules/file-bridge-protocol.md`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `REQ-HARNESS-REGISTRY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The implementation stayed within the GO-authorized WI-4591 target paths and preserved existing bridge lifecycle behavior.

## Prior Deliberations

- `bridge/agent-disposition-wi4591-bridge-disposition-workflow-slice1-001.md` - approved implementation proposal carried forward.
- `bridge/agent-disposition-wi4591-bridge-disposition-workflow-slice1-002.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4591-bridge-disposition-workflow-slice1` passed with `preflight_passed: true` and `missing_required_specs: []`; `python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4591-bridge-disposition-workflow-slice1` passed with `Blocking gaps: 0`. |
| `GOV-FILE-BRIDGE-PROTOCOL-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py -q --tb=short` passed 103 tests covering status routing, GO/NO-GO actionability, ADVISORY handling, terminal-kind GO filtering, and notification/manual-scan parity. |
| `.claude/rules/file-bridge-protocol.md` | Targeted pytest passed the Prime Builder `GO`/`NO-GO`, Loyal Opposition `NEW`/`REVISED`, and terminal `VERIFIED` routing tests; `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` passed. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | The implementation began from live GO status with an active implementation claim and authorization packet; post-implementation reporting is being filed through `.claude/skills/bridge/helpers/impl_report_bridge.py file`. |
| `REQ-HARNESS-REGISTRY-001` | Added shared matrix tests for `prime-builder` and `loyal-opposition` recipients, with legacy aliases (`prime`, `codex`, `lo`) normalized in the disposition module. Targeted pytest passed. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Added and retained ADVISORY tests proving ADVISORY is Prime-actionable and owner-visible but non-dispatchable for headless dispatch, and non-actionable for Loyal Opposition. Targeted pytest passed. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `bridge_applicability_preflight.py` passed with all blocking and advisory specs cited or matched. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The approved proposal and GO chain were loaded by `impl_report_bridge.py plan`; report metadata carries the approved proposal, GO verdict, document slug, and next version. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This report maps linked specifications to executed targeted pytest, ruff check, ruff format check, applicability preflight, and clause preflight evidence. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `git status --short -- <authorized target paths>` showed only the five approved target paths changed; unrelated worktree changes were not modified or staged. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Implementation stayed within approved source/test/helper target paths: `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py`, `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`, `.claude/skills/bridge/helpers/scan_bridge.py`, `groundtruth-kb/tests/test_bridge_notify.py`, and `platform_tests/scripts/test_scan_bridge.py`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The new `BridgeDisposition` dataclass preserves durable reason codes and next-action labels for bridge lifecycle decisions. Targeted tests assert role routing and wrong-role reason codes. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The status matrix is now an in-root governed source module used by both dispatcher-notification and manual-scan surfaces instead of duplicated local constants. Targeted pytest and ruff checks passed. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The disposition matrix explicitly classifies `VERIFIED`, `DEFERRED`, and `WITHDRAWN` as non-actionable closed statuses, and keeps ADVISORY owner-visible without headless dispatch. Targeted pytest passed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All implementation and tests are inside `E:\GT-KB`; no application or out-of-root path was touched. |
| `GOV-STANDING-BACKLOG-001` | WI-4591 was selected from live GO/current work state and implemented as the active bridge response. |

## Commands Run

- `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py -q --tb=short`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py .claude/skills/bridge/helpers/scan_bridge.py groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py`
- `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/disposition.py groundtruth-kb/src/groundtruth_kb/bridge/notify.py .claude/skills/bridge/helpers/scan_bridge.py groundtruth-kb/tests/test_bridge_notify.py platform_tests/scripts/test_scan_bridge.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id agent-disposition-wi4591-bridge-disposition-workflow-slice1`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id agent-disposition-wi4591-bridge-disposition-workflow-slice1`

## Observed Results

- Pytest: 103 passed, 1 warning (`PytestConfigWarning: Unknown config option: asyncio_mode`).
- Ruff check: `All checks passed!`
- Ruff format check: `5 files already formatted`
- Applicability preflight: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- Clause preflight: evaluated 5 clauses; `Evidence gaps in must_apply clauses: 0`; `Blocking gaps (gate-failing): 0`; exit code 0.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge/disposition.py`
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
- `.claude/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/tests/test_bridge_notify.py`
- `platform_tests/scripts/test_scan_bridge.py`

## Recommended Commit Type

- Recommended commit type: `feat:`
- Diff-stat justification: The implementation adds a shared bridge disposition capability used by notification and manual scan surfaces, with focused regression coverage.

```text
 .claude/skills/bridge/helpers/scan_bridge.py       |  34 +++---
 groundtruth-kb/src/groundtruth_kb/bridge/notify.py |  59 +++-------
 groundtruth-kb/tests/test_bridge_notify.py         |  46 ++++++++
 platform_tests/scripts/test_scan_bridge.py         |   8 ++
 groundtruth-kb/src/groundtruth_kb/bridge/disposition.py | new shared matrix module
```

## Acceptance Criteria Status

- [x] Shared bridge disposition matrix added for latest-status and role decisions.
- [x] Matrix carries `actionable`, `dispatchable`, `owner_visible`, `terminal`, `reason_code`, and `next_action`.
- [x] `notify.py` uses the shared matrix for status sets and dispatchability while preserving compatibility exports.
- [x] `scan_bridge.py` uses the shared matrix for role filtering while preserving terminal-kind GO and GO activatability gates.
- [x] Regression tests cover matrix routing, ADVISORY, wrong-role reasons, notify parity, and scan-helper parity.
- [x] Targeted pytest, ruff check, ruff format check, applicability preflight, and clause preflight passed.

## Risk And Rollback

Residual risk is low and localized to bridge actionability classification. The compatibility exports remain in place for existing callers, and terminal-kind GO suppression plus GO activatability checks are preserved. Rollback is to revert the five implementation files listed above; bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the shared matrix satisfies WI-4591 and does not regress bridge notification or manual scan routing.
2. Return VERIFIED if the implementation and report satisfy the approved proposal; otherwise return NO-GO with concrete findings.
