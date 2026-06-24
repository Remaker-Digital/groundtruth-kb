NEW

# Implementation Proposal - Test coverage gap: Natural Language Escalation to Peer Agents

bridge_kind: prime_proposal
Document: agent-red-wi3205-natural-language-peer-escalation-coverage
Version: 001
Date: 2026-06-24 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3205
Owner Decision: DELIB-20265586

target_paths: ["applications/Agent_Red/src/chat/pipeline/intent_router.py", "applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py"]

## Claim

WI-3205 should add deterministic coverage for `SPEC-1864` and make the smallest required source correction if Loyal Opposition agrees with the confirmed behavior gap. `SPEC-1864` says a tenant admin or team member can use natural-language admin-chat phrases such as `transfer to sales` or `let the campaigns agent handle this` and receive a `PEER_AGENT` route with the target agent resolved from the phrase. Current source exposes the natural-language fallback in `IntentRouter.resolve()`, but runtime inspection shows that branch is unreachable for authenticated team members because the earlier `team_member_role -> CO_PILOT` branch returns first.

Observed pre-proposal behavior, read-only check on 2026-06-24:

- Bound customer/user-message path: `router.resolve(..., user_message="transfer to sales")` returns `RouteTarget.PEER_AGENT`, `agent_id="sales"`, `skill_id="sales:search-products"`.
- Bound team-member/admin path: `router.resolve(..., team_member_role="admin", user_message="transfer to sales")` returns `RouteTarget.CO_PILOT`, `agent_id=None`, `skill_id=None`.

The proposal is therefore source plus tests, not a pure test-only backfill.

## Requirement Sufficiency

Operative state: Existing requirements sufficient.

`SPEC-1864` is directly satisfied only when the natural-language phrase is evaluated in the admin/team-member route path and still goes through normal peer-agent verification. The required dependency chain is concrete in source:

- `SPEC-1861` defines `IntentRouter` and the `PEER_AGENT` execution-plan boundary.
- `SPEC-1862` defines team-member direct agent chat and the authenticated team-member route surface that currently short-circuits to `CO_PILOT`.
- `SPEC-1856` requires deny-by-default skill bindings before dispatch to a peer agent.
- `SPEC-1852` and `SPEC-1853` provide the peer-agent identity and stable `skill_id` surfaces that the router resolves.

Existing `applications/Agent_Red/tests/chat/test_agent_name_extractor.py` proves phrase extraction in isolation, but it does not prove that `IntentRouter.resolve()` routes authenticated admin/team-member phrases to `PEER_AGENT`. Existing `applications/Agent_Red/tests/chat/pipeline/test_intent_router.py` covers overlay, registry, explicit target, tier, domain, and fallback cases, but has no `SPEC-1864` natural-language router branch coverage. The proposed target adds that missing router-level evidence and guards the source fix.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`:

- `applications/Agent_Red/src/chat/pipeline/intent_router.py`
- `applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py`

## Specification Links

- `SPEC-1864` - Primary requirement: natural-language admin/team-member escalation phrases resolve to peer-agent routing.
- `SPEC-1861` - IntentRouter boundary and route targets; proposed tests assert `RouteTarget.PEER_AGENT` vs `RouteTarget.CO_PILOT`.
- `SPEC-1856` - Binding model; proposed tests create enabled bindings and verify missing binding remains deny-by-default.
- `SPEC-1862` - Team-member direct chat route surface; proposed source change affects only the authenticated team-member natural-language path after explicit target handling.
- `SPEC-1852` - Canonical peer-agent identity; proposed tests use registry peer agents and verify core agents are not routed by natural-language extraction.
- `SPEC-1853` - Stable skill identity; proposed tests assert resolved `skill_id` values such as `sales:search-products`.
- `GOV-10` - Tests must exercise exposed production behavior, not source-inspection-only claims; proposed tests instantiate production router/registry/binding services.
- `SPEC-1649` - Master test plan live-interface discipline; proposed tests avoid mocks for the routing behavior under test and use production service APIs.
- `GOV-12` - Work item-driven test addition; WI-3205 is the explicit coverage-gap work item.
- `GOV-13` - Backlog/project execution discipline; WI-3205 remains inside the authorized project membership.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - This source/test mutation is bounded by the cited project authorization and its snapshot member set.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Implementation must keep the router branch small, readable, and regression-tested.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Prime Builder must file NEW and wait for Loyal Opposition GO before mutating protected source/test paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal includes concrete specification links before implementation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification plan is derived from the `SPEC-1864` admin/team-member route requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Proposal includes Project Authorization, Project, Work Item, and target paths.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - All changed files stay inside the Agent Red application subtree under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Uses an existing project member WI; does not add new work items or expand snapshot scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex self-enforces bridge and preflight gates before protected mutation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The discovered behavior defect is preserved as bridge evidence rather than silent ad hoc mutation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Proposal/report flow keeps owner authorization and review evidence explicit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This concrete defect/plan crosses the artifact threshold and is routed through the bridge.

## Prior Deliberations

- `DELIB-0712` - POR Step 16.B methodology review established the implemented-untested classification stream that produced this class of coverage gaps.
- `DELIB-0713` - Owner accepted treating phantom/assertion-only evidence as untested for regular behavioral requirements, supporting creation/remediation of this WI class.
- `DELIB-20265586` - Owner authorized the bounded project implementation snapshot for the current 38 open project member WIs, including WI-3205.
- Search note: `gt deliberations search "WI-3205 Natural Language Escalation to Peer Agents SPEC"` and `gt deliberations search "SPEC-1864 phantom-only evidence"` found no owner decision specific to WI-3205 that changes the requirement.

## Owner Decisions / Input

- Owner authorization in force: `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, owner decision `DELIB-20265586`.
- No new owner input is requested. If Loyal Opposition determines that changing team-member `CO_PILOT` precedence requires a product decision rather than a direct `SPEC-1864` compliance fix, it should return `NO-GO` with that requirement-disambiguation finding.

## Proposed Scope

1. Update `applications/Agent_Red/src/chat/pipeline/intent_router.py` so natural-language peer-agent phrases from authenticated team members can resolve to `PEER_AGENT` after explicit `target_agent_id` handling and before the generic team-member `CO_PILOT` fallback.
2. Preserve existing explicit-target semantics: `team_member_role + target_agent_id` still returns `PEER_AGENT` on verified binding or `ERROR` on failed verification.
3. Preserve safe fallback semantics: if a team-member natural-language phrase resolves to a peer agent but verification/binding fails, route remains `CO_PILOT` rather than bypassing binding checks.
4. Preserve existing non-team-member natural-language fallback behavior unless tests expose a direct contradiction.
5. Add `applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py` with router-level tests for:
   - bound team-member/admin phrase `transfer to sales` routes to `PEER_AGENT` with `agent_id="sales"` and `skill_id="sales:search-products"`;
   - bound team-member phrase `let the campaigns agent handle this` resolves display-name/first-word language to `campaigns`;
   - unbound team-member natural-language peer phrase remains `CO_PILOT` and does not bypass `SPEC-1856` deny-by-default binding;
   - team-member phrase naming a core agent remains `CO_PILOT`;
   - existing customer/user-message natural-language fallback still routes a bound peer phrase to `PEER_AGENT`.
6. Keep the implementation scoped to the two listed target paths. Do not add new work items and do not mutate formal GOV/SPEC/ADR/DCL/PB/REQ artifacts.

## Specification-Derived Verification Plan

| Requirement | Test / Check |
|---|---|
| `SPEC-1864`: admin/team-member NL phrase routes to peer agent | New pytest case: `team_member_role="admin"`, `user_message="transfer to sales"`, enabled binding -> `RouteTarget.PEER_AGENT`, `agent_id="sales"` |
| `SPEC-1864`: display-name style phrase resolves target | New pytest case: `let the campaigns agent handle this` with campaigns binding -> `RouteTarget.PEER_AGENT`, `agent_id="campaigns"` |
| `SPEC-1856`: missing binding denies peer route | New pytest case: same phrase without binding -> `RouteTarget.CO_PILOT`, no peer agent id |
| `SPEC-1852`: only peer agents are natural-language routable | New pytest case: phrase names `intent classifier` core agent -> `RouteTarget.CO_PILOT` |
| Regression: existing customer fallback remains intact | New pytest case: no team role, bound `transfer to sales` -> `RouteTarget.PEER_AGENT` |
| Code quality | `python -m ruff check` and `python -m ruff format --check` on touched files |

Required implementation verification commands:

- `python -m pytest applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py -q --tb=short`
- `python -m pytest applications/Agent_Red/tests/chat/pipeline/test_intent_router.py applications/Agent_Red/tests/chat/test_agent_name_extractor.py -q --tb=short`
- `python -m ruff check applications/Agent_Red/src/chat/pipeline/intent_router.py applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py`
- `python -m ruff format --check applications/Agent_Red/src/chat/pipeline/intent_router.py applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py`

## Acceptance Criteria

- Natural-language admin/team-member peer-agent phrases no longer short-circuit to generic `CO_PILOT` when a verified peer binding exists.
- Binding and peer-agent verification remain mandatory; natural-language routing cannot bypass missing binding, disabled overlay, tier, or domain checks.
- Explicit `target_agent_id` behavior remains unchanged.
- Existing customer/user-message natural-language fallback remains covered and passing.
- The bridge post-implementation report includes the exact commands and outcomes listed above.

## Risks / Rollback

Risk is limited to routing precedence in `IntentRouter.resolve()`. The principal behavioral risk is accidentally diverting ordinary team-member admin assistance to peer agents too broadly. The proposed implementation mitigates that by only attempting peer routing when `user_message` contains an extractable peer-agent reference and the peer verification/binding checks pass. Rollback is straightforward: revert the small router branch/helper change and remove the new test file.

## Files Expected To Change

- `applications/Agent_Red/src/chat/pipeline/intent_router.py`
- `applications/Agent_Red/tests/chat/pipeline/test_natural_language_peer_escalation_spec1864.py`

## Recommended Commit Type

`fix`
