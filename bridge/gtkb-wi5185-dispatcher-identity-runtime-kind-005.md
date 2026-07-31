REVISED

# WI-5185 Dispatcher Identity / Runtime-Kind Separation - Sequencing-Resolved Report

bridge_kind: implementation_report
Document: gtkb-wi5185-dispatcher-identity-runtime-kind
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-07-11 UTC
Responds to: bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-004.md
Approved GO: bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f387f-0fc7-7200-abaa-03068ca8eee0
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; role=prime-builder resolved from validated worker session document
author_metadata_source: harness-state/codex/session-envelopes/019f387f-0fc7-7200-abaa-03068ca8eee0.json

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5185-DISPATCHER-IDENTITY-RUNTIME-KIND-20260711
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5185
target_paths: ["scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]
implementation_scope: source | test_addition
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix

---

## Revision Claim

This revision changes no WI-5185 implementation bytes. It resolves the sole
sequencing blocker in NO-GO-004: WI-5189 is now independently VERIFIED and
committed at `cd877ac477192181fd781df61b7513f20bca0380`, including the
document-authoritative `scripts/bridge_work_intent_registry.py` behavior on
which two dispatcher fixtures depend.

The exact WI-5185 source and test changes previously found substantively
correct now pass against committed HEAD. They are independently finalizable as
the two PAUTH target paths without carrying any WI-5189 source or unrelated
working-tree change.

## Implementation Claim

`_resolve_dispatch_targets` compares the role record's durable `harness_name`
with the identity-derived command handle for fail-closed drift detection.
`harness_type` remains the runtime implementation kind passed to readiness
evaluation. A Claude-compatible runtime can therefore operate under the
distinct `alibaba-cloud-studio` installation identity without weakening
identity drift detection.

The test file covers the split identity/runtime-kind case, rejects a mismatched
durable identity name, and creates validated Prime Builder worker session
documents for the same-role project-holder fixtures. Those document fixtures
now execute against committed WI-5189 source.

No dispatcher configuration, durable role or identity map, selection ranking,
routing rule, provider behavior, credential, deployment surface, or unrelated
path is changed.

## Specification Links

- `SPEC-DISPATCHER-IDENTITY-RUNTIME-KIND-SEPARATION-001`
- `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-202666084` - owner approval of the bounded WI-5185 PAUTH.
- `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md` - independent LO GO.
- `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-004.md` - sequencing-only NO-GO; source and self-contained tests found correct.
- `bridge/gtkb-wi5189-document-claim-authority-011.md` - independent VERIFIED verdict satisfying the required predecessor sequence.

## Owner Decisions / Input

No new owner decision is required. WI-5185 remains within its exact approved
PAUTH and GO. NO-GO-004 prescribed landing WI-5189 first and then refiling this
report; that sequence is complete.

## Authorization Evidence

- Active PAUTH: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5185-DISPATCHER-IDENTITY-RUNTIME-KIND-20260711`.
- Independent GO: `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-002.md`.
- Implementation report: `bridge/gtkb-wi5185-dispatcher-identity-runtime-kind-003.md`.
- Required committed predecessor: WI-5189/WI-5195 commit `cd877ac477192181fd781df61b7513f20bca0380` and `VERIFIED-011`.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Spec-Derived Verification

| Requirement | Executed evidence | Observed result |
| --- | --- | --- |
| Durable identity drift compares `harness_name`, not runtime kind | Focused `alibaba-cloud-studio` / `claude` resolver regression | Passed. |
| Runtime kind remains available to readiness evaluation | Same focused resolver regression | Passed. |
| Mismatched projected durable name fails closed | Focused identity-drift rejection regression | Passed. |
| Existing dispatcher runtime behavior, including committed document-authority fixtures, remains intact | Full `test_dispatcher_runtime.py` suite | `178 passed, 1 warning`. |
| Existing compact/full workflow report behavior remains intact | Full `test_bridge_dispatch_report_cli.py` suite | `15 passed, 1 warning`. |
| Code quality | Ruff check and format check on both target paths | Passed; `2 files already formatted`. |

## Commands Executed

1. `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/scripts/test_dispatcher_runtime.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short`
   - Result: `193 passed, 1 warning in 31.15s`.
2. `groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short`
   - Result: `15 passed, 1 warning`.
3. Focused dispatcher resolver command selecting `resolve_exactly_one_active_dispatches`, `resolve_uses_harness_name_for_identity_drift_and_keeps_runtime_kind`, and `resolve_rejects_harness_name_identity_drift`.
   - Result: `3 passed, 175 deselected, 1 warning`.
4. `groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
   - Result: `All checks passed!`.
5. `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py`
   - Result: `2 files already formatted`.

## Findings Addressed

### WI-5185 test file depended on uncommitted WI-5189 source

Resolved by sequencing exactly as NO-GO-004 required. WI-5189 source is now in
HEAD at `cd877ac4`, independently VERIFIED, and the full dispatcher suite passes
against that committed source. No WI-5185 implementation rewrite was needed.

## Acceptance Status

All WI-5185 acceptance criteria pass. The two target paths are ready for
independent Loyal Opposition VERIFIED and same-transaction scoped commit.

## Risk / Rollback

The resolver remains fail closed for missing or mismatched durable identity
data. Rollback is a scoped revert of only the two WI-5185 target paths and must
preserve the already-terminal WI-5189 commit and all unrelated working-tree
content.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
