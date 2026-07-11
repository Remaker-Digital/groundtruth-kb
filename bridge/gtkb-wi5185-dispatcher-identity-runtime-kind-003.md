NEW

# GT-KB Bridge Implementation Report - gtkb-wi5185-dispatcher-identity-runtime-kind - 003

bridge_kind: implementation_report
Document: gtkb-wi5185-dispatcher-identity-runtime-kind
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md
Approved proposal: bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5185-DISPATCHER-IDENTITY-RUNTIME-KIND-20260711
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5185
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated worker session document
author_metadata_source: validated worker session document
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
Recommended commit type: fix:

## Implementation Claim

Updated `_resolve_dispatch_targets` so durable identity drift validation compares
the role record's `harness_name` with the identity-derived command handle.
`harness_type` remains available to the existing readiness evaluator as the
runtime implementation kind. Added coverage for a Claude-compatible runtime
under the `alibaba-cloud-studio` installation identity, fail-closed name drift,
and the document-authoritative Prime Builder claim fixtures required by the
current WI-5189 contract.

No dispatcher configuration, role map, identity projection, ranking, routing,
provider, credential, or deployment files were changed.

## Specification Links

- `SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Owner Decisions / Input

No new owner decision is required by this implementation report. The approved
WI-5185 PAUTH and independent GO remain the governing authorization evidence.

## Prior Deliberations

- `DELIB-202666084` - owner approval of the bounded WI-5185 authorization.
- `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-001.md` - approved proposal.
- `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md` - independent LO GO.

## Specification-Derived Verification Plan

| Requirement | Evidence |
| --- | --- |
| Identity/runtime-kind separation | Synthetic `harness_name=alibaba-cloud-studio`, `harness_type=claude` target resolves with command handle `alibaba-cloud-studio`. |
| Identity fail-closed behavior | A mismatched identity-derived name raises a `harness_name` drift error. |
| Runtime-kind preservation | The readiness evaluator receives `claude` while identity resolution returns `alibaba-cloud-studio`. |
| Delivery regression | The full dispatcher-runtime suite and dispatch-report CLI suite pass. |
| Scope guard | Diff is limited to the two authorized target paths; no dispatcher configuration or identity data was edited. |

## Commands Run

- `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest -o addopts= platform_tests\\scripts\\test_dispatcher_runtime.py -q --tb=short`
- `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest -o addopts= platform_tests\\groundtruth_kb\\cli\\test_bridge_dispatch_report_cli.py -q --tb=short`
- `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest -o addopts= platform_tests\\scripts\\test_dispatcher_runtime.py -k "resolve_exactly_one_active_dispatches or resolve_uses_harness_name_for_identity_drift_and_keeps_runtime_kind or resolve_rejects_harness_name_identity_drift" -q --tb=short`
- `groundtruth-kb\\.venv\\Scripts\\python.exe -m ruff check scripts\\dispatcher_runtime.py platform_tests\\scripts\\test_dispatcher_runtime.py`
- `groundtruth-kb\\.venv\\Scripts\\python.exe -m ruff format --check scripts\\dispatcher_runtime.py platform_tests\\scripts\\test_dispatcher_runtime.py`

## Observed Results

- Dispatcher runtime: `178 passed, 1 warning`.
- Dispatch report CLI: `11 passed, 1 warning`.
- WI-5185 regression subset: `3 passed, 175 deselected, 1 warning`.
- Ruff check: passed.
- Ruff format check: passed; both files already formatted.
- An adjacent durable-keyed regression suite remains `15 passed, 2 failed` on
  pre-existing `codex_dispatch_not_ready` readiness failures; neither failure
  exercises the changed identity/runtime-kind branch and that test file is not
  an authorized WI-5185 target.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Acceptance Criteria Status

- [x] Compare `harness_name` to the identity-derived durable handle.
- [x] Preserve `harness_type` for runtime readiness evaluation.
- [x] Fail closed on identity-name drift.
- [x] Preserve dispatch configuration, selection, ranking, and routing inputs.
- [x] Add regression coverage and pass the complete dispatcher-runtime suite.

## Risk And Rollback

The change remains fail-closed for a missing or mismatched durable identity.
Rollback is limited to the two authorized target files and does not alter
dispatcher configuration or persisted harness state.

## Loyal Opposition Asks

1. Verify the implementation against the linked specification and executed command evidence.
2. Return VERIFIED if the implementation report and implementation satisfy the approved proposal, otherwise return NO-GO with findings.
