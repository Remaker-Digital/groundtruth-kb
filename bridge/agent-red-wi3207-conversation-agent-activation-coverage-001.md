NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3207 Conversation-Level Agent Activation Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3207-conversation-agent-activation-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3207

target_paths: ["applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py"]

## Claim

WI-3207 should be implemented as a narrow test-only backfill for `SPEC-1866` Conversation-Level Agent Activation.

Current Agent Red source already exposes deterministic conversation-level activation surfaces:

- `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` stores `conversation_agent_override`, `conversation_agent_override_at`, and `conversation_agent_override_by` on `ConversationDocument`.
- `applications/Agent_Red/src/multi_tenant/admin_conversation_api.py` exposes `set_agent_override()` for setting/clearing a per-conversation peer-agent override, validates registry/tier/overlay/private-scope/binding constraints, hydrates binding cache before validation when cold, patches the conversation document, and emits an invocation event.
- `applications/Agent_Red/src/chat/pipeline/intent_router.py` checks `conversation_agent_override` before ordinary routing, resolves a default enabled skill binding when no skill is supplied, and falls through to standard routing if override verification fails.
- Existing `applications/Agent_Red/tests/unit/test_admin_conversation_api.py` and `applications/Agent_Red/tests/chat/pipeline/test_intent_router.py` cover broad behavior, but the project WI is still open because MemBase has no deterministic test evidence mapped to `SPEC-1866` / `WI-3207`.

This proposal adds one dedicated pytest file that binds those live surfaces to `WI-3207` and the `SPEC-1866` clauses. It does not authorize source edits. If the new tests expose a current source gap, Prime Builder must stop and return through the bridge with a revised proposal rather than expanding target paths.

## Requirement Sufficiency

Existing requirements are sufficient for a test-only coverage backfill.

`SPEC-1866` defines the active behavior: agents can be activated or deactivated at individual conversation level, activation state is stored on the conversation document, and `IntentRouter` consults conversation-level overrides before tenant-level overlay/default routing. Its dependency set is explicit: `SPEC-1861` for `IntentRouter`, `SPEC-1854` for tenant overlay activation, and `SPEC-1862` for team-member direct agent context.

The relevant deliberation trail further constrains the test plan:

- `DELIB-0333` keeps conversation override state on the conversation document and requires `IntentRouter` to receive a scalar override value rather than a whole conversation document.
- `DELIB-0337` identifies cold-cache binding validation, overlay/private-scope parity with `IntentRouter`, and saved override read/write semantics as the critical SPEC-1866 control-plane risks.
- `DELIB-0341` verifies the P1 fixes for default skill resolution, overlay-disabled/private-scope rejection, and identifies cold-cache binding hydration as a remaining blocker.
- `DELIB-0344` verifies the final S252 closure, including cold-cache override validation hydration.

No owner clarification is needed because the proposal is a deterministic test addition against those accepted constraints.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\unit\test_conversation_agent_activation_spec1866.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\admin_conversation_api.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\cosmos_schema.py`
- `E:\GT-KB\applications\Agent_Red\src\chat\pipeline\intent_router.py`
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_admin_conversation_api.py`
- `E:\GT-KB\applications\Agent_Red\tests\chat\pipeline\test_intent_router.py`

## Specification Links

- `SPEC-1866` - Direct requirement for conversation-level agent activation and router precedence.
- `SPEC-1861` - `IntentRouter` is the execution-plan boundary that consumes conversation override state.
- `SPEC-1854` - Per-tenant overlay activation remains part of override validation and peer-route verification.
- `SPEC-1856` - Skill binding existence and enabled-state remain the deny-by-default authorization record for peer routing.
- `SPEC-1862` - Team-member direct agent context interacts with explicit target routing and conversation overrides.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live admin conversation API, conversation document fields, IntentRouter, overlay, and binding surfaces are the exposed artifacts under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, `GO`, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies baseline Python lint and formatting checks to the new test file.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3207`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0333` - S251 advisory review for SPEC-1864/1865/1866; establishes conversation-document override state and scalar router input.
- `DELIB-0337` - S252 advisory review; identifies cold-cache validation and overlay/private-scope parity risks.
- `DELIB-0341` - S252 v2 NO-GO; verifies default skill and overlay/private-scope fixes but calls out remaining cold-cache validation.
- `DELIB-0344` - S252 v3 GO; verifies cold-cache override validation and marketplace cache fixes.
- `gt bridge threads --wi WI-3207 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3207 --json` shows open/backlogged `WI-3207`, source spec `SPEC-1866`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1866 --json` shows title "Conversation-Level Agent Activation", status `implemented`, scope `agent_extensibility`, and dependencies on `SPEC-1861`, `SPEC-1854`, and `SPEC-1862`.
- `applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py` does not currently exist.
- `applications/Agent_Red/src/multi_tenant/admin_conversation_api.py` contains the live `set_agent_override()` control-plane surface.
- `applications/Agent_Red/src/chat/pipeline/intent_router.py` contains the live `conversation_agent_override` routing-precedence surface.
- Existing tests cover related behavior but do not provide a dedicated `WI-3207`/`SPEC-1866` replacement artifact.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3207-conversation-agent-activation-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3207-conversation-agent-activation-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py`.
2. In the new pytest, import live `src.multi_tenant.admin_conversation_api` and `src.chat.pipeline.intent_router` surfaces.
3. Assert `ConversationDocument` exposes the conversation override storage fields.
4. Assert `set_agent_override()` hydrates cold binding cache before validation, validates enabled public overlay, patches `conversation_agent_override`, timestamp, actor, and `last_activity_at`, and emits an invocation event.
5. Assert clearing the override patches the same fields back to `None`.
6. Assert `IntentRouter.resolve()` gives a valid `conversation_agent_override` highest precedence and resolves a default enabled skill binding.
7. Assert failed override verification falls through to standard routing rather than producing an explicit-target error.
8. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1866` | New pytest imports live admin conversation and router code and asserts conversation-document storage, set/clear control-plane behavior, and router override precedence. |
| `SPEC-1861` | New pytest verifies `IntentRouter` consumes scalar `conversation_agent_override` before ordinary routing and falls through to normal routing when verification fails. |
| `SPEC-1854` | New pytest verifies enabled/public overlay validation before a conversation override is accepted. |
| `SPEC-1856` | New pytest verifies cold-cache binding hydration and default enabled skill binding resolution. |
| `SPEC-1862` | New pytest verifies conversation override precedence/fallthrough semantics alongside team-member routing context. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3207-conversation-agent-activation-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py
python -m ruff format --check applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py
```

## Acceptance Criteria

- PASS when the new pytest verifies conversation override fields exist on `ConversationDocument`.
- PASS when the new pytest verifies setting an override hydrates cold binding cache, validates the peer-agent constraints, writes override fields, and emits an invocation event.
- PASS when the new pytest verifies clearing an override writes the override fields back to `None`.
- PASS when the new pytest verifies `IntentRouter` gives a valid conversation override highest precedence and resolves a non-empty default skill binding.
- PASS when the new pytest verifies failed override verification falls through to standard routing rather than explicit-target error semantics.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low-to-moderate. The proposal adds deterministic function-level override/router coverage using mocked repositories and the live admin/router modules; it does not exercise the browser UI or real Cosmos DB. If Loyal Opposition requires HTTP-router or UI-level evidence, return `NO-GO` so Prime Builder can revise with broader target paths.

Rollback is to delete `applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/unit/test_conversation_agent_activation_spec1866.py`

## Recommended Commit Type

`test:`
