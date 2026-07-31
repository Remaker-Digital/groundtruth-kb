NEW

# GT-KB Bridge Implementation Report - gtkb-wi5233-dispatch-selection-order-cap-repair-implementation - 003

bridge_kind: implementation_report
Document: gtkb-wi5233-dispatch-selection-order-cap-repair-implementation
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-002.md
Approved proposal: bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI-5233-DISPATCH-SELECTION-CAP-IMPLEMENTATION
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5233
Implementation Authorization Packet: sha256:8dab3d23cb08330e2d17db9d1ea228d66db2aed6a89cbb3b1dceff45000c88f1
Implementation Start Packet: sha256:d1f842d351383dea35aad94f8cfde2c2202ba2140ff85b9728d96633755d1f79
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5
author_model_version: codex-desktop-2026-07-14
author_model_configuration: Codex Desktop; Prime Builder; danger-full-access; approval-policy-never
Recommended commit type: fix(governance):

## Implementation Claim

Implemented the WI-5233 dispatcher selection and cap repair in the two authorized target paths only.

- `scripts/dispatcher_runtime.py`: `_selected_oldest_first` now preserves the actionable queue head instead of reversing the queue before capping.
- `scripts/dispatcher_runtime.py`: `DispatchTarget` now carries `dispatch_max_items`, target resolution preserves ranked records returned by `select_dispatch_candidates`, and `_effective_max_items_for_target` prefers that dispatch cap before `dispatch` surface and `headless.max_items` fallback caps.
- `scripts/dispatcher_runtime.py`: Prime and Loyal Opposition launch paths no longer reverse `dispatched_selected` before `_spawn_harness` builds the prompt.
- `platform_tests/scripts/test_dispatcher_runtime.py`: added focused WI-5233 coverage for queue-order preservation and dispatch-config max-items propagation when no `headless.max_items` cap is present.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
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

## Owner Decisions / Input

No new owner decision is required. This implementation follows the owner-resumed fleet goal and the WI-5233 implementation PAUTH named above. OpenRouter F is currently out of budget; this report does not depend on F for verification.

## Prior Deliberations

- `DELIB-202666200` - owner decision backing the WI-5233 implementation PAUTH.
- `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-001.md` - approved implementation proposal.
- `bridge/gtkb-wi5233-dispatch-selection-order-cap-repair-implementation-002.md` - D Loyal Opposition GO verdict authorizing implementation.
- `bridge/gtkb-wi5226-openrouter-diagnostic-telemetry-004.md` - C dispatcher-produced VERIFIED verdict, which also provided live evidence that a misrouted C dispatch received two items despite C's one-item cap.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused dispatcher runtime tests prove queue-order selection and ranked dispatch cap propagation; full authorized module run has only the four unrelated ambient failures listed below. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge GO, work-intent claim, and implementation-start packet were verified before protected edits. This report is filed as the next numbered bridge artifact. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | WI-5233 and TEST-11387 track the defect; implementation evidence is preserved in this bridge report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries forward the proposal's concrete specification links. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The spec-to-test mapping in this section includes executed test results and observed failures. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project, PAUTH, work item, implementation packet, and target paths are declared in the report header. |
| `SPEC-AUQ-POLICY-ENGINE-001` | No owner question or AUQ path was required; the worker-governed path used an existing owner decision and PAUTH. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All changed files are under `E:/GT-KB` and no adopter application path was touched. |
| `GOV-STANDING-BACKLOG-001` | The defect remains tracked through WI-5233 and does not create a new untracked backlog item. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The change preserves dispatcher self-enforcement and does not rely on native hooks. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation follows the governed proposal, GO, implementation packet, tests, and bridge report path. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The observed dispatcher defect triggered a bounded work item and report instead of ad hoc runtime edits. |

## Commands Run

- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short -k "selected_oldest_first or dispatch_config_max_items_overlay or ollama_lo_dispatch_caps_selected_batch_to_one or signature_uses_selected_batch"`
- `python -m pytest platform_tests\scripts\test_dispatcher_runtime.py -q --tb=short`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py`
- `groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts\dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime.py`

## Observed Results

- Focused pytest: `4 passed, 192 deselected`.
- Full authorized module pytest: `192 passed, 4 failed`.
- The four full-module failures match the unrelated pre-existing failures recorded in the D GO verdict:
  - `test_prime_spawn_creates_dispatch_authorization_packet_and_env`
  - `test_issue_dispatch_auth_uses_go_items_from_mixed_list`
  - `test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy`
  - `test_antigravity_stdin_dispatch_removes_prompt_from_child_argv`
- Ruff check: `All checks passed!`
- Ruff format check: `2 files already formatted`

## Files Changed

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Dirty Worktree Preservation

The repository contained extensive unrelated owner and parallel-session changes before this implementation. This report intentionally claims only the WI-5233 hunks in the two authorized paths. No runtime JSON, lease files, unrelated source files, staging, push, deployment, or credential changes were performed by this Prime Builder implementation.

## Acceptance Criteria Status

- Dispatcher selection no longer reverses the actionable queue before capping.
- Per-target dispatch max-item caps from ranked dispatch configuration are preserved into dispatch target construction and honored before headless fallback.
- Prompt launch paths preserve selected queue order after work-intent and document-lease filtering.
- Focused regression tests cover both repaired bugs.

## Risk And Rollback

Residual risk is limited to dispatcher selection/cap behavior in the two changed files. Rollback is a focused revert of the WI-5233 hunks in `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py`, with bridge and PAUTH artifacts preserved as governance evidence.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return VERIFIED if the implementation and report satisfy the approved proposal, otherwise return NO-GO with concrete findings.
