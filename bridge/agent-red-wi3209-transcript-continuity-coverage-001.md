NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3209 Transcript Continuity Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3209-transcript-continuity-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3209

target_paths: ["applications/Agent_Red/widget/tests/transcript-continuity-spec1868.test.tsx"]

## Claim

WI-3209 should be implemented as a narrow widget test-only backfill for `SPEC-1868` Transcript Continuity.

Current Agent Red source already exposes deterministic transcript-continuity surfaces:

- `applications/Agent_Red/widget/src/persistence/transcript.ts` stores, loads, expires, and clears conversation ids for `session` and `persistent` transcript continuity modes, using tenant-scoped widget-key storage names.
- `applications/Agent_Red/widget/src/transport/http.ts` exposes `fetchConversation()` for restore-time conversation fetches and classifies missing, inactive, and transient failures.
- `applications/Agent_Red/widget/src/state/store.ts` exposes `restoreMessages()` and normalizes backend conversation messages into widget messages while recording `restoredMessageCount`.
- `applications/Agent_Red/widget/src/components/Panel.tsx` persists new conversation ids, loads stored ids on mount, restores active conversations, clears storage on permanent restore failures, and preserves storage for transient restore failures.
- `applications/Agent_Red/widget/src/components/MessageList.tsx` renders the previous-conversation separator at the restored/live-message boundary.
- `applications/Agent_Red/src/chat/endpoints.py` exposes `GET /api/chat/conversations/{conversation_id}` for restore-time full conversation state.

Existing `applications/Agent_Red/widget/tests/transcript-restore.test.ts` covers storage helpers, store normalization, and Panel branch logic, while `applications/Agent_Red/tests/unit/test_chat_endpoints.py` covers the backend conversation-state endpoint success and not-found paths. The remaining deterministic coverage gap is a direct replacement artifact mapped to `WI-3209` / `SPEC-1868` that exercises live widget restore-classification behavior and renders the restored-message UI boundary instead of only proving the boundary formula. This proposal adds that dedicated Vitest file. It does not authorize source edits. If the new tests expose a source gap, Prime Builder must stop and return through the bridge with a revised proposal rather than expanding target paths.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1868` is the governing requirement for Transcript Continuity and is marked implemented. The live in-root implementation and existing SPEC-tagged tests identify the accepted behaviors clearly enough for a test-only coverage backfill: transcript continuity can be disabled, session-scoped, or persistent with TTL; conversation ids are persisted after conversation start; restore uses the existing conversation-state endpoint; active conversations restore message history into widget state; inactive, missing, or empty conversations clear stored state; transient restore failures preserve storage for retry; and restored transcripts show a boundary before new messages.

No owner clarification is needed because this proposal tests the accepted live behavior already reflected in the in-root implementation and does not alter product semantics.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\widget\tests\transcript-continuity-spec1868.test.tsx`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\widget\src\persistence\transcript.ts`
- `E:\GT-KB\applications\Agent_Red\widget\src\transport\http.ts`
- `E:\GT-KB\applications\Agent_Red\widget\src\state\store.ts`
- `E:\GT-KB\applications\Agent_Red\widget\src\components\Panel.tsx`
- `E:\GT-KB\applications\Agent_Red\widget\src\components\MessageList.tsx`
- `E:\GT-KB\applications\Agent_Red\widget\tests\transcript-restore.test.ts`
- `E:\GT-KB\applications\Agent_Red\widget\tests\restore-skeleton.test.tsx`
- `E:\GT-KB\applications\Agent_Red\src\chat\endpoints.py`
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_chat_endpoints.py`

## Specification Links

- `SPEC-1868` - Direct requirement for transcript continuity across reloads and restore-time message history.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live widget HTTP transport, store, persistence, and message-list components are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native Vitest evidence must validate live code rather than rely on stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native test mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline changed-file hygiene; TypeScript coverage will use Vitest, widget typecheck, and whitespace diff checks because no Python file is touched.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3209`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying phantom-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `gt deliberations list --spec-id SPEC-1868 --limit 10 --json` returned `[]`; no spec-linked deliberation entries exist for `SPEC-1868`.
- `gt deliberations list --work-item-id WI-3209 --limit 10 --json` returned `[]`; no WI-linked deliberation entries exist for `WI-3209`.
- `gt bridge threads --wi WI-3209 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3209 --json` shows open/backlogged `WI-3209`, source spec `SPEC-1868`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1868 --json` shows title "Transcript Continuity", version `2`, status `implemented`, and change reason "Track B Phase 3 implementation complete".
- `applications/Agent_Red/widget/tests/transcript-continuity-spec1868.test.tsx` does not currently exist.
- `applications/Agent_Red/widget/tests/transcript-restore.test.ts` already covers storage helpers, `restoreMessages()` normalization, Panel restore branch logic, and separator-boundary formulas, but it does not render `MessageList` to prove the separator UI appears in the live component.
- `applications/Agent_Red/widget/src/transport/http.ts` contains the live `fetchConversation()` restore classifier, but existing widget tests do not directly exercise its active, missing, inactive, and transient result mapping.
- `applications/Agent_Red/tests/unit/test_chat_endpoints.py` covers backend conversation-state endpoint success and not-found behavior, so this WI can remain widget-side without adding backend target paths.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3209-transcript-continuity-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.
- warning observed: `missing_parent_dirs` included a command-argument token for `tests/transcript-continuity-spec1868.test.tsx`; the declared implementation `target_paths` metadata remains the in-root Agent Red widget test path.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3209-transcript-continuity-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/widget/tests/transcript-continuity-spec1868.test.tsx`.
2. In the new Vitest file, import live `configureTransport()` and `fetchConversation()` from `widget/src/transport/http.ts`.
3. Mock `globalThis.fetch` and assert `fetchConversation()` requests `/api/chat/conversations/{conversationId}` with the configured widget key.
4. Assert `fetchConversation()` returns `ok: true` only for active conversation-state responses with messages.
5. Assert `fetchConversation()` maps 404 and 403 responses to `reason: "not_found"`, 5xx/network failures to `reason: "transient"`, and non-active 200 responses to `reason: "not_active"`.
6. Import live `createStore()` and `MessageList`.
7. Restore backend-shaped messages into the store and add a new live customer message.
8. Render live `MessageList` and assert the localized previous-conversation separator appears between restored and new messages.
9. Assert the separator is not rendered when all messages are restored or when no messages were restored.
10. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1868` | New Vitest imports live restore transport, store, and message-list components and verifies active restore success, permanent/transient failure classification, message restoration, and previous-conversation separator rendering. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native Vitest against the new deterministic spec-mapping test file, using live in-repository widget source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3209-transcript-continuity-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run widget `typecheck` and `git diff --check` on the touched TypeScript test file; no Python file is touched, so ruff has no applicable target. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
npm --prefix applications/Agent_Red/widget test -- transcript-continuity-spec1868.test.tsx
npm --prefix applications/Agent_Red/widget test -- transcript-restore.test.ts restore-skeleton.test.tsx transcript-continuity-spec1868.test.tsx
npm --prefix applications/Agent_Red/widget run typecheck
git diff --check -- applications/Agent_Red/widget/tests/transcript-continuity-spec1868.test.tsx
```

Ruff applicability after implementation:

- No Python file is in `target_paths`, so `ruff check` and `ruff format --check` have no applicable touched-file target for this WI. If implementation unexpectedly touches Python, Prime Builder must stop and revise this proposal before continuing.

## Acceptance Criteria

- PASS when the new Vitest verifies `fetchConversation()` requests the conversation-state endpoint with configured widget authentication.
- PASS when the new Vitest verifies active conversation-state responses return `ok: true` with message history.
- PASS when the new Vitest verifies 404/403 responses clear as permanent `not_found` failures, inactive conversation states return `not_active`, and 5xx/network failures return `transient`.
- PASS when the new Vitest renders live `MessageList` and observes the localized previous-conversation separator between restored and newly added messages.
- PASS when the new Vitest verifies the previous-conversation separator is absent when there is no restored/live boundary.
- PASS when targeted Vitest, adjacent restore widget tests, widget typecheck, and diff whitespace checks all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low-to-moderate. The proposal adds deterministic widget unit coverage with mocked fetch and rendered Preact components. It does not exercise a real browser tab lifecycle, real localStorage persistence across navigation, real EventSource streams, live model calls, or live backend services. Existing helper tests continue to cover storage TTL and Panel restore branch logic.

Rollback is to delete `applications/Agent_Red/widget/tests/transcript-continuity-spec1868.test.tsx`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/widget/tests/transcript-continuity-spec1868.test.tsx`

## Recommended Commit Type

`test:`
