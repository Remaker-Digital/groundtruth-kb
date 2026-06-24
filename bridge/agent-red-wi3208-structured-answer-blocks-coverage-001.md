NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3208 Structured Answer Blocks Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3208-structured-answer-blocks-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3208

target_paths: ["applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py", "applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx"]

## Claim

WI-3208 should be implemented as a narrow test-only backfill for `SPEC-1867` Structured Answer Blocks.

Current Agent Red source already exposes deterministic structured-answer-block surfaces:

- `applications/Agent_Red/src/chat/blocks.py` extracts v1 block types from response text: `steps`, `faq`, and `action`; product-card blocks are explicitly deferred.
- `applications/Agent_Red/src/chat/models.py` allows `validated_event()` to carry optional `blocks` metadata, using the same backward-compatible optional payload pattern as structured sources.
- `applications/Agent_Red/src/chat/pipeline/orchestrator.py` emits blocks only when `structured_blocks_enabled` is true and the tenant tier is `professional` or `enterprise`; extraction failure is non-fatal and text remains the fallback.
- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` and `applications/Agent_Red/src/multi_tenant/config/field_mapping.py` expose the tenant-level `structured_blocks_enabled` setting.
- `applications/Agent_Red/widget/src/transport/sse.ts`, `applications/Agent_Red/widget/src/state/store.ts`, `applications/Agent_Red/widget/src/components/MessageBubble.tsx`, and `applications/Agent_Red/widget/src/components/AnswerBlocks.tsx` parse, preserve, and render structured blocks for completed agent messages.

Existing `applications/Agent_Red/tests/chat/test_blocks.py` covers extractor heuristics and `applications/Agent_Red/tests/multi_tenant/test_schema_alias_regression.py` covers a related professional-tier field-registry regression, but the project WI remains open because MemBase has no deterministic test evidence mapped to `SPEC-1867` / `WI-3208`. This proposal adds dedicated spec-mapping backend and widget tests. It does not authorize source edits. If the new tests expose a current source gap, Prime Builder must stop and return through the bridge with a revised proposal rather than expanding target paths.

## Requirement Sufficiency

Existing requirements are sufficient for a test-only coverage backfill.

`SPEC-1867` v1 describes structured answer rendering in the widget with step lists, product cards, FAQ accordions, and action buttons; it also names RG JSON blocks, dedicated widget components, tenant opt-in, and a professional-plus tier gate. `SPEC-1867` v2 marks the feature implemented by S249. The S249 review trail narrows the operative v1 scope: `DELIB-0279` rejects product cards without a structured product payload contract and recommends using optional `blocks[]` on the validated SSE event; `DELIB-0280` records GO once product cards were explicitly deferred and v1 was limited to text-derived `steps`, `faq`, and `action` blocks.

No owner clarification is needed because this proposal tests the accepted non-product v1 scope already reflected in the live source. Product-card implementation remains outside this WI unless separately specified and authorized.

## In-Root Placement Evidence

The implementation targets are under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\chat\test_structured_answer_blocks_spec1867.py`
- `E:\GT-KB\applications\Agent_Red\widget\tests\structured-answer-blocks.test.tsx`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\chat\blocks.py`
- `E:\GT-KB\applications\Agent_Red\src\chat\models.py`
- `E:\GT-KB\applications\Agent_Red\src\chat\pipeline\orchestrator.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\cosmos_schema.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\config\field_mapping.py`
- `E:\GT-KB\applications\Agent_Red\widget\src\transport\sse.ts`
- `E:\GT-KB\applications\Agent_Red\widget\src\state\store.ts`
- `E:\GT-KB\applications\Agent_Red\widget\src\components\MessageBubble.tsx`
- `E:\GT-KB\applications\Agent_Red\widget\src\components\AnswerBlocks.tsx`
- `E:\GT-KB\applications\Agent_Red\tests\chat\test_blocks.py`
- `E:\GT-KB\applications\Agent_Red\tests\chat\test_source_attribution.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_schema_alias_regression.py`

## Specification Links

- `SPEC-1867` - Direct requirement for structured answer blocks, accepted v1 block types, tenant opt-in, professional-plus tier gating, widget rendering, and fallback text preservation.
- `SPEC-1870` - Related validated-event optional metadata pattern for structured source attribution; structured blocks intentionally reuse this backward-compatible SSE shape.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live extractor, SSE model, tenant field registry, widget store, and widget rendering components are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest and Vitest evidence must validate live code rather than rely on stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native test mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline Python lint and formatting checks to the new Python test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use governed bridge helper paths and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3208`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0279` - S249 Track B Phase 3 advisory review; recommends optional `blocks[]` on `validated`, tenant/config persistence, and deferring product cards until a structured product payload contract exists.
- `DELIB-0280` - S249 Track B Phase 3 v2 GO review; records that product cards were deferred and v1 is limited to text-derived `steps`, `faq`, and `action` blocks.
- `DELIB-0281` - S249 workspace re-review; records that then-current source did not yet contain the claimed `blocks[]` transport or config seams, which are now visible in the read-only current-state evidence below.
- `gt bridge threads --wi WI-3208 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3208 --json` shows open/backlogged `WI-3208`, source spec `SPEC-1867`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1867 --json` shows title "Structured Answer Blocks", version `2`, status `implemented`, and change reason "Track B Phase 3 implementation complete".
- In-root `specifications-export.csv` preserves `SPEC-1867` v1 text requiring structured answer rendering, tenant opt-in, professional-plus tier gate, and widget components.
- `applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py` does not currently exist.
- `applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx` does not currently exist.
- `applications/Agent_Red/src/chat/blocks.py` currently implements `extract_blocks()` for `steps`, `faq`, and `action`, with product cards deferred.
- `applications/Agent_Red/src/chat/models.py` currently includes optional `blocks` in `validated_event()`.
- `applications/Agent_Red/src/chat/pipeline/orchestrator.py` currently gates block extraction on `structured_blocks_enabled` and professional/enterprise tier.
- `applications/Agent_Red/widget/src/transport/sse.ts` currently parses `payload.blocks` from `validated`.
- `applications/Agent_Red/widget/src/state/store.ts` currently preserves `blocks` on the finalized streaming agent message.
- `applications/Agent_Red/widget/src/components/MessageBubble.tsx` currently renders `AnswerBlocks` only for completed non-customer messages with non-empty `message.blocks`.
- Existing tests cover related extractor and tier-registry behavior but do not provide a dedicated `WI-3208`/`SPEC-1867` replacement artifact spanning backend payload and widget rendering.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3208-structured-answer-blocks-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3208-structured-answer-blocks-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py`.
2. In the new Python pytest, import live `src.chat.blocks.extract_blocks`, `src.chat.models.validated_event`, and live tenant-field registry/validation surfaces.
3. Assert `extract_blocks()` produces only accepted v1 block types (`steps`, `faq`, `action`) and does not fabricate product-card blocks from prose containing product-like details.
4. Assert `validated_event()` includes `blocks` when provided, omits `blocks` when absent or empty, preserves standard validated-event fields, and remains backward-compatible with `sources`.
5. Assert `structured_blocks_enabled` is excluded/rejected for `starter` tenants and included/accepted for `professional` and `enterprise` tenants through the live registry/validation surfaces.
6. Add `applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx`.
7. In the new Vitest file, import live widget store and rendering components.
8. Assert `updateLastAgentMessage()` finalizes the streaming agent message while preserving text fallback plus `blocks`.
9. Assert `AnswerBlocks` renders step lists, FAQ accordions, and action links with the expected visible content and interaction.
10. Assert `MessageBubble` renders both ordinary text and blocks for completed agent messages, and suppresses blocks for customer or still-streaming messages.
11. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1867` | New Python and widget tests verify accepted v1 block extraction, optional `blocks` payload, professional-plus gate, fallback text preservation, and widget rendering for completed agent messages. |
| `SPEC-1870` | New Python test verifies structured blocks reuse the same backward-compatible optional `validated_event` metadata pattern as structured sources. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest and Vitest commands against deterministic spec-mapping test files using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3208-structured-answer-blocks-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new Python test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py
python -m ruff format --check applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py
npm --prefix applications/Agent_Red/widget test -- structured-answer-blocks.test.tsx
npm --prefix applications/Agent_Red/widget run typecheck
```

## Acceptance Criteria

- PASS when the new Python pytest verifies only accepted v1 block types are extracted and product-card-shaped prose does not create unsupported product blocks.
- PASS when the new Python pytest verifies `validated_event()` includes optional `blocks`, omits empty blocks, preserves core validated fields, and remains compatible with `sources`.
- PASS when the new Python pytest verifies `structured_blocks_enabled` is professionally tier-gated through live registry and validation surfaces.
- PASS when the new widget Vitest verifies finalized store messages preserve both text fallback and `blocks`.
- PASS when the new widget Vitest verifies step, FAQ, and action blocks render through live widget components.
- PASS when the new widget Vitest verifies blocks render only for completed agent messages, not customer or streaming messages.
- PASS when targeted pytest, ruff, Vitest, and widget typecheck commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is moderate because this coverage spans both Python backend and TypeScript widget tests, and widget typecheck can surface unrelated existing type drift. The behavioral scope remains narrow and deterministic; it does not exercise live model calls, real EventSource transport, browser visual layout, or real tenant persistence.

Rollback is to delete `applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py` and `applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/chat/test_structured_answer_blocks_spec1867.py`
- `applications/Agent_Red/widget/tests/structured-answer-blocks.test.tsx`

## Recommended Commit Type

`test:`
