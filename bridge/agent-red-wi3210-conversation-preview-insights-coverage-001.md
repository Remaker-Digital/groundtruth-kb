NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3210 Conversation Preview Insights Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3210-conversation-preview-insights-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3210

target_paths: ["applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py"]

## Claim

WI-3210 should be implemented as a narrow Python test-only backfill for `SPEC-1872` Conversation Preview with Message Insights.

Current Agent Red source already exposes deterministic conversation-preview surfaces:

- `applications/Agent_Red/src/multi_tenant/admin_preview_api.py` exposes `POST /api/admin/preview/chat`, creates preview conversations with `is_test_mode=True`, applies temporary config overrides to the resolved preferences object, runs the chat pipeline, returns an SSE `StreamingResponse`, attaches `X-Preview-Mode` and `X-Conversation-Id` headers, and emits a final `event: trace` payload.
- `applications/Agent_Red/src/multi_tenant/admin_preview_api.py` exposes `GET /api/admin/preview/{conversation_id}/trace`, enforces the professional-plus tier gate, returns stored `pipeline_trace` data only for conversations tagged `is_test_mode=True`, and hides production or missing conversations with 404.
- `applications/Agent_Red/admin/shared/hooks/useQuality.ts` consumes the live preview endpoints by posting to `/api/admin/preview/chat`, parsing SSE events including `stage`, `token`, `validated`, `retracted`, `error`, and `trace`, and fetching `/api/admin/preview/{conversation_id}/trace`.
- `applications/Agent_Red/admin/standalone/pages/ConversationPreview.tsx` exposes the admin page, professional-plus UI gate, temporary tone/confidence overrides, live streaming response state, stage badges, and decision trace display.
- `applications/Agent_Red/tests/multi_tenant/test_admin_preview_api.py` currently covers helper tier gating, daily-limit helper behavior, and Pydantic request/response models, but does not exercise the live preview chat route behavior, SSE trace emission, config override application through the route path, or preview trace access control.

The remaining deterministic gap is endpoint-level coverage that proves the implemented preview mode behaves as the spec requires at its real exposed backend interface. This proposal adds a dedicated pytest file for `WI-3210` / `SPEC-1872`. It does not authorize source edits or frontend scaffold work. If the tests expose a source gap, Prime Builder must stop and return through the bridge with a revised proposal rather than expanding target paths.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1872` is the governing implemented requirement for Conversation Preview with Message Insights. It specifies the preview chat endpoint, `is_test_mode=True` tagging, temporary config overrides, SSE stream plus `ResponseDecisionTrace`, analytics/billing/customer-history exclusion, professional-plus tier gate, admin message-insights UI, preview session limit, and trace retrieval endpoint. The live source and existing helper tests make the accepted behavior concrete enough for a test-only backfill.

No owner clarification is needed because this proposal tests accepted live behavior already reflected in the in-root implementation and does not alter product semantics.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_conversation_preview_spec1872.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\admin_preview_api.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_admin_preview_api.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_admin_analytics_api.py`
- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_standalone_test_mode.py`
- `E:\GT-KB\applications\Agent_Red\admin\shared\hooks\useQuality.ts`
- `E:\GT-KB\applications\Agent_Red\admin\standalone\pages\ConversationPreview.tsx`
- `E:\GT-KB\applications\Agent_Red\admin\standalone\package.json`

## Specification Links

- `SPEC-1872` - Direct requirement for conversation preview/test mode, message insights, trace persistence, professional-plus gating, and exclusion from production analytics/billing/customer-facing history.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live preview API route functions and streaming response path are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native test mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline changed-file hygiene; Python coverage will use targeted pytest plus ruff check and ruff format checks on the touched test file.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing AUQ-backed project authorization; no prose owner decision is requested by this proposal.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3210`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only, assertion-only, and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0440` - Baseline closure audit identified Knowledge Score plus Conversation Preview as `PARTIAL / NON-BLOCKER`, cited existing `test_admin_preview_api.py` coverage, and recommended endpoint tests for `POST /api/admin/preview/chat` and `GET /api/admin/preview/{id}/trace` to close the live-route contract gap.
- `gt deliberations list --spec-id SPEC-1872 --limit 10 --json` returned `[]`; no spec-linked deliberation entries exist for `SPEC-1872`.
- `gt deliberations list --work-item-id WI-3210 --limit 10 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3210`.
- `gt bridge threads --wi WI-3210 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3210 --json` shows open/backlogged `WI-3210`, source spec `SPEC-1872`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says assertion-only verification was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1872 --json` shows title "Conversation Preview with Message Insights", version `2`, status `implemented`, and assertions for the preview endpoint, `is_test_mode=True` tagging, message-insights fields, analytics/billing exclusion, and professional-plus tier gate.
- `applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py` does not currently exist.
- `applications/Agent_Red/tests/multi_tenant/test_admin_preview_api.py` covers helper tier gates, daily limits, and request/response model validation, but it does not exercise `preview_chat()` or `get_preview_trace()` against mocked live collaborators.
- `applications/Agent_Red/src/multi_tenant/admin_preview_api.py` contains the live preview chat and trace route functions that can be covered without network calls by mocking tenant/preference repositories, `ConversationSession`, and `ChatPipeline`.
- `applications/Agent_Red/admin/standalone/package.json` has build and typecheck scripts but no frontend test script; this proposal therefore avoids adding frontend test infrastructure and instead validates the backend contract consumed by the existing admin UI source.
- `applications/Agent_Red/tests/multi_tenant/test_admin_analytics_api.py` and `applications/Agent_Red/tests/multi_tenant/test_standalone_test_mode.py` already contain adjacent evidence for `is_test_mode` filtering/exclusion behavior, so the new file can focus on preview endpoint behavior without duplicating analytics tests.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3210-conversation-preview-insights-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.
- warning observed: `missing_parent_dirs` included `tests/multi_tenant/test_conversation_preview_spec1872.py`, an over-harvested suffix from command/path text; the declared implementation `target_paths` metadata remains the in-root Agent Red test path `applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py`.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3210-conversation-preview-insights-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py`.
2. In the new pytest file, import live `PreviewChatRequest`, `get_preview_trace()`, and `preview_chat()` from `src.multi_tenant.admin_preview_api`.
3. Mock late-imported `TenantRepository`, `PreferencesRepository`, `ConversationSession`, and `ChatPipeline` collaborators through their module paths so the live route functions execute without network calls, databases, or model calls.
4. Assert `preview_chat()` enforces the professional-plus path through a professional tenant context and creates a preview conversation with `is_test_mode=True` and `customer_id` prefixed with `preview-`.
5. Assert `preview_chat()` applies `config_overrides` to the preference object passed into `ChatPipeline.execute()` without requiring persistence.
6. Assert `preview_chat()` adds the preview customer message, returns a `StreamingResponse` with `X-Preview-Mode: true` and `X-Conversation-Id`, yields pipeline SSE events, and then yields a final `event: trace` payload containing the stored decision trace and conversation id.
7. Assert `get_preview_trace()` returns stored `pipeline_trace` data for test-mode conversations.
8. Assert `get_preview_trace()` returns 404 for production/non-test conversations and missing conversations so production traces are not leaked through the preview endpoint.
9. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1872` | New pytest imports live preview route functions and verifies preview conversation creation with `is_test_mode=True`, config override use, SSE response headers/events, final trace emission, trace retrieval, professional-plus route path, and non-test trace denial. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic spec-mapping test file plus adjacent preview/analytics/test-mode tests, using live in-repository backend modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3210-conversation-preview-insights-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check`, `ruff format --check`, and whitespace diff checks on the touched Python test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py -q --tb=short
python -m pytest applications/Agent_Red/tests/multi_tenant/test_admin_preview_api.py applications/Agent_Red/tests/multi_tenant/test_admin_analytics_api.py applications/Agent_Red/tests/multi_tenant/test_standalone_test_mode.py applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py
git diff --check -- applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py
```

## Acceptance Criteria

- PASS when the new pytest verifies the live preview chat route creates a preview conversation tagged `is_test_mode=True`.
- PASS when the new pytest verifies temporary config overrides are passed to the pipeline without persistence.
- PASS when the new pytest verifies preview chat adds the preview customer message and calls the chat pipeline with preview customer identity and trace metadata.
- PASS when the new pytest verifies the streaming response has preview headers, includes pipeline SSE output, and appends a final trace event with the stored decision trace and conversation id.
- PASS when the new pytest verifies the trace retrieval route returns trace data only for preview/test-mode conversations.
- PASS when the new pytest verifies the trace retrieval route returns 404 for production/non-test conversations and missing conversations.
- PASS when targeted pytest, adjacent preview/analytics/test-mode pytest, ruff check, ruff format check, and diff whitespace checks all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is moderate. The proposal covers live route functions with mocked collaborators instead of a full ASGI app and real storage, so it verifies route behavior deterministically without asserting a complete deployed admin session. It also does not add frontend test infrastructure because the current admin standalone package has no test runner. Existing helper and analytics/test-mode tests remain the adjacent evidence for limits, model validation, and production analytics exclusion.

Rollback is to delete `applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/multi_tenant/test_conversation_preview_spec1872.py`

## Recommended Commit Type

`test:`
