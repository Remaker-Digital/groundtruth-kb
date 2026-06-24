NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Report - WI-3208 Structured Answer Blocks Coverage

bridge_kind: implementation_report
Document: agent-red-wi3208-structured-answer-blocks-coverage
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/agent-red-wi3208-structured-answer-blocks-coverage-002.md
Approved proposal: bridge/agent-red-wi3208-structured-answer-blocks-coverage-001.md
Recommended commit type: test:

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3208

Implementation-start packet: sha256:0cbe0264d6a97d4bc3bd1d68693a3fe111140b570bd48614ce28a4da057db0bb
target_paths: ["applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py", "applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx"]

## Implementation Claim

Implemented the Loyal Opposition-approved test-only backfill for `WI-3208` / `SPEC-1867`.

`applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py` now provides deterministic backend coverage for:

- accepted v1 block extraction (`steps`, `faq`, `action`) and non-creation of unsupported product/product-card blocks from product-shaped prose;
- `validated_event()` carrying non-empty optional `blocks` metadata while preserving normal `validated` fields and structured `sources`;
- omission of empty or absent `blocks`;
- professional-plus gating for `structured_blocks_enabled` through live field registry and validation surfaces.

`applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx` now provides deterministic widget coverage for:

- `Store.updateLastAgentMessage()` finalizing a streaming agent message while preserving fallback text and `blocks`;
- `AnswerBlocks` rendering steps, FAQ interaction, and action links through live widget components;
- `MessageBubble` rendering fallback text plus blocks for completed agent messages;
- `MessageBubble` suppressing blocks for customer messages and still-streaming agent messages.

No source files were changed for `WI-3208`. No existing tests were rewritten. No generated artifacts, deployment state, release tags, formal GOV/SPEC/ADR/DCL/PB/REQ artifacts, project membership, credentials, or new work items were changed.

## Specification Links

- `SPEC-1867` - Primary requirement for structured answer blocks, accepted v1 block types, tenant opt-in, professional-plus tier gating, widget rendering, and fallback text preservation.
- `SPEC-1870` - Related validated-event optional metadata pattern for structured source attribution; structured blocks reuse this backward-compatible SSE/event shape.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live extractor, SSE model, tenant field registry, widget store, and widget rendering components are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest and Vitest evidence validates live code rather than stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native test mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline Python lint and formatting checks to the new Python test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires proposal/report spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, work item, and target-path metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Uses an existing project member WI; does not add new work items or expand snapshot scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforced bridge and implementation-start gates before protected mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Durable bridge/test evidence is preserved for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Implementation intent, authorization, review evidence, and verification evidence are preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This implementation report is a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision was required. This implementation uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3208`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0279` - S249 Track B Phase 3 advisory review; recommends optional `blocks[]` on `validated`, tenant/config persistence, and deferring product cards until a structured product payload contract exists.
- `DELIB-0280` - S249 Track B Phase 3 v2 GO review; records that product cards were deferred and v1 is limited to text-derived `steps`, `faq`, and `action` blocks.
- `DELIB-0281` - S249 workspace re-review; records that then-current source did not yet contain the claimed `blocks[]` transport or config seams, which the current implementation now exposes.
- `bridge/agent-red-wi3208-structured-answer-blocks-coverage-001.md` - Approved implementation proposal carried forward.
- `bridge/agent-red-wi3208-structured-answer-blocks-coverage-002.md` - Loyal Opposition GO verdict authorizing the test-only implementation.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-1867` | Python tests verify accepted v1 extraction, product-card deferral, optional blocks payload, and professional-plus field gate; widget tests verify store preservation, step/FAQ/action rendering, fallback text preservation, and completed-agent-only rendering. |
| `SPEC-1870` | `test_validated_event_includes_non_empty_blocks_and_preserves_sources` verifies `blocks` coexist with structured `sources` and are omitted when empty or absent. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Repository-native pytest and Vitest commands executed against deterministic WI-3208 spec-mapping test files plus adjacent backend regression tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Latest bridge status was `GO`; work-intent claim was active; implementation-start packet `sha256:0cbe0264d6a97d4bc3bd1d68693a3fe111140b570bd48614ce28a4da057db0bb` was acquired before adding the test files. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `ruff check`, `ruff format --check`, widget Vitest, and widget typecheck pass for the touched surfaces. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, artifact-governance specs | This report carries forward linked specs, target paths, command evidence, observed results, and spec-to-test mapping for LO verification. |

## Commands Run

```text
python -m pytest applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py -q --tb=short
npm --prefix applications/Agent_Red/widget test -- structured-answer-blocks.test.tsx
python -m ruff check applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py
python -m ruff format --check applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py
npm --prefix applications/Agent_Red/widget run typecheck
python -m pytest applications/Agent_Red/tests/chat/test_blocks.py applications/Agent_Red/tests/multi_tenant/test_schema_alias_regression.py applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py -q --tb=short
git diff --check -- applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx
```

## Observed Results

- `python -m pytest applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py -q --tb=short` - PASS: `3 passed in 0.43s`.
- `npm --prefix applications/Agent_Red/widget test -- structured-answer-blocks.test.tsx` - PASS: `Test Files 1 passed (1)`, `Tests 4 passed (4)`, duration `3.11s`.
- `python -m ruff check applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py` - PASS: `All checks passed!`.
- `python -m ruff format --check applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py` - PASS: `1 file already formatted`.
- `npm --prefix applications/Agent_Red/widget run typecheck` - PASS: `tsc --noEmit` exited 0.
- `python -m pytest applications/Agent_Red/tests/chat/test_blocks.py applications/Agent_Red/tests/multi_tenant/test_schema_alias_regression.py applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py -q --tb=short` - PASS: `30 passed in 1.84s`.
- `git diff --check -- applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx` - PASS: no output, exit code 0.

## Files Changed

- `applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py`
- `applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx`

## Acceptance Criteria Status

- PASS: New Python pytest verifies only accepted v1 block types are extracted and product-card-shaped prose does not create unsupported product blocks.
- PASS: New Python pytest verifies `validated_event()` includes optional `blocks`, omits empty blocks, preserves core validated fields, and remains compatible with `sources`.
- PASS: New Python pytest verifies `structured_blocks_enabled` is professional-plus tier-gated through live registry and validation surfaces.
- PASS: New widget Vitest verifies finalized store messages preserve both text fallback and `blocks`.
- PASS: New widget Vitest verifies step, FAQ, and action blocks render through live widget components.
- PASS: New widget Vitest verifies blocks render only for completed agent messages, not customer or streaming messages.
- PASS: Targeted pytest, ruff, Vitest, and widget typecheck commands all pass.
- PASS: No source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs were changed for this implementation payload.

## Risk And Rollback

Residual risk is low-to-moderate and limited to deterministic backend/widget unit coverage. The implementation does not exercise real EventSource transport, model calls, browser visual layout, or live tenant persistence, matching the approved test-only proposal.

Rollback is to delete `applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py` and `applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx`. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Return `VERIFIED` if the report and implementation satisfy the approved proposal, otherwise return `NO-GO` with findings.
