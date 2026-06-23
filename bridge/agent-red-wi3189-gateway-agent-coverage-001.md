NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex Desktop interactive Prime Builder session override; application mode heartbeat continuation

# Implementation Proposal - WI-3189 Gateway Agent Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3189-gateway-agent-coverage
Version: 001
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3189

target_paths: ["applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py"]

## Claim

Add deterministic repository-native pytest evidence for `SPEC-1710` by exercising the current Agent Red plug-in registry and dispatch interfaces for the Gateway Agent. Existing tests already cover the in-process `GatewayAgentTools` availability, queueing, context transfer, and queue monitoring methods; this proposal closes the remaining live-interface gap by proving the Gateway Agent is discoverable from `agents.yaml`, exposes the expected MCP tool identities and stable skill identities, has the intended peer/tier/mode metadata, resolves Gateway capabilities to the Gateway Agent, and dispatches a Gateway tool through the production `PluginDispatcher` route.

This proposal is intentionally test-only. It does not implement new WebSocket, SSE, agent desktop, workforce-management, CRM, or supervisor-dashboard behavior. `SPEC-1710` includes real-time transport language; this proposal documents that boundary explicitly and focuses on the implemented Gateway Agent MCP registry/dispatch surface plus existing in-process Gateway method coverage.

## Requirement Sufficiency

Existing requirements sufficient. Existing requirements are sufficient for this test-only coverage proposal. `SPEC-1710` defines the Gateway Agent capability surface and cites `SPEC-1706` for the independent MCP server/container, configuration-driven discovery, and MCP tool-use interaction model. `SPEC-1852` and `SPEC-1853` define the current registry fields needed to make that surface durable (`agent_kind`, stable `skill_id`, skill mode, and MCP tool mappings). Existing chat transport specifications and tests cover general SSE/WebSocket infrastructure separately; this WI proposal adds missing Gateway-specific registry and dispatch evidence without broadening production behavior.

## In-Root Placement Evidence

The target path is inside `E:\GT-KB`: `applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py`.

## Bridge File Chain Evidence

This is a first `NEW` proposal for document `agent-red-wi3189-gateway-agent-coverage`. If approved by the preflight gates, it will be filed append-only as `bridge/agent-red-wi3189-gateway-agent-coverage-001.md` through the governed helper-mediated bridge path. No prior version exists and no prior bridge version will be rewritten or deleted.

## Specification Links

- `SPEC-1710` - Direct target requirement: Gateway Agent human escalation connection MCP server, including live-agent availability, queue management, conversation context handoff, skill-based routing, real-time messaging context, agent takeover/return-to-AI transition context, and supervisor monitoring context.
- `SPEC-1706` - Parent architecture requirement for modular plug-in MCP agents: configuration-driven discovery, separate agent endpoints, capability/tool exposure, and dispatch through the MCP tool-use pattern.
- `SPEC-1852` - Agent identity requirement: the Gateway Agent must be represented with canonical `agent_kind` semantics rather than legacy ambiguous classification.
- `SPEC-1853` - Stable skill/tool identity requirement: the Gateway Agent skills must expose stable `gateway:<skill>` identifiers mapped to underlying MCP tool names and declare read/mutate modes.
- `SPEC-1857` - Dispatcher/catalog guardrail context: bound dispatch is deny-by-default, so test evidence for the base dispatcher path must not imply tenant exposure without bindings.
- `SPEC-1861` - Intent-router boundary context: peer-agent routing remains deterministic and tenant-overlay/binding-aware; coverage here is limited to registry and dispatcher surfaces, not new routing behavior.
- `GOV-10` - Test artifacts must exercise exposed production interfaces; this proposal uses registry and dispatcher APIs rather than source-text inspection.
- `SPEC-1649` - Master test plan/live interface policy; repository-native pytest evidence is limited to live production interfaces and not source inspection.
- `GOV-12` - Work item creation triggers test creation; this proposal adds current pytest evidence for this WI's source spec.
- `GOV-13` - Test visibility/phase governance; FAB-11 recognizes repository-native pytest mappings as live spec-to-test evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped authorization is the bounded owner approval source for this WI but does not bypass bridge review, GO, implementation-start, report, or verification gates.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Requires the proposal to account for the baseline code-quality rules.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge file chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires concrete proposal specification links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification to map linked specs to executed test evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines in implementation-targeting proposals.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the helper-mediated bridge write path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - The bridge proposal is the durable artifact for implementation intent.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Implementation intent and review evidence are preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - The owner-authorized WI implementation crosses the threshold for bridge proposal capture.

## Prior Deliberations

- `DELIB-0712` - 16.B methodology review classifying coverage gaps, including `SPEC-1710`, by evidence quality.
- `DELIB-0713` - Owner decision rejecting assertion-only/phantom-only evidence as sufficient for behavioral requirements.
- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0162` - Loyal Opposition architecture memo on pluggable agents, escalation taxonomy, and tenant RBAC; relevant to not treating Gateway escalation as a local-only test concern.
- `DELIB-0096` - Agent extensibility advisory review covering direct peer-agent chat, session semantics, RBAC, observability, and direct agent-chat boundaries; relevant to the scope boundary around real-time/direct-chat Gateway behavior.
- `DELIB-20265105` - POR Step 16.C phantom WI creation review; relevant to avoiding false closure from phantom evidence.
- `DELIB-20265110` - POR Step 16.D phantom spec-link cleanup review; relevant to avoiding false coverage from stale or phantom evidence.
- `DELIB-20263468` - WI-4455 Loyal Opposition advisory recognizing repository-native pytest evidence as the live verification surface.
- Semantic deliberation search for `SPEC-1710 Gateway Agent Human Escalation Connection MCP Server phantom-only evidence DELIB-0712 DELIB-0713` returned broader MCP/agent-disposition records but no more specific Gateway Agent owner decision beyond the methodology, extensibility, and project authorization records above.

## Owner Decisions / Input

- `DELIB-20265586` and `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23` authorize bounded implementation for the snapshot-bound 38-WI project membership, including `WI-3189`.
- Mutation class: `test_addition`.
- No new owner input is required. This proposal does not add a work item, broaden project membership, deploy, mutate credentials, perform destructive cleanup, or change formal GOV/SPEC/ADR/DCL/PB/REQ artifacts.

## Proposed Scope

1. Add `applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py` with `SPEC-1710`-specific tests that load the production `agents.yaml` through `PluginAgentRegistry.load_from_yaml()` and assert:
   - `gateway` is present with `spec_id == "SPEC-1710"`, `agent_kind == "peer"`, category `escalation`, starter tier gate, internal auth, health check, and the expected endpoint template.
   - The four Gateway MCP capabilities are present: `gateway.check_availability`, `gateway.queue_customer`, `gateway.transfer_context`, and `gateway.monitor_queue`.
   - Stable skill ids map to the corresponding MCP tool names, with expected `read`/`mutate` modes.
   - The generated tool catalog and `resolve_tool_agent()` route Gateway capabilities to the `gateway` agent.
2. Add a fake HTTP-client dispatch test in the same file that invokes one Gateway Agent tool through `PluginDispatcher` using the production YAML registry, then asserts the constructed URL, payload, tenant/conversation headers, success metadata, and `agent_id == "gateway"`.
3. Identify existing in-process tests for Gateway behavior in `applications/Agent_Red/tests/agents/plugins/test_domain_agents.py::TestGatewayAgent` as carried-forward evidence for availability, queueing, context transfer, and queue monitoring method behavior.
4. Treat WebSocket/SSE transport tests as existing adjacent transport evidence only, not as newly added Gateway-specific coverage under this proposal. If Loyal Opposition determines `SPEC-1710` requires new Gateway-specific transport tests before GO, it should issue `NO-GO` with the required target-path revision.
5. Do not change production code unless the approved test exposes an implementation defect; if a production defect is discovered, stop and file a revised proposal or follow the bridge finding path before widening scope.

## Specification-Derived Verification Plan

| Spec / Requirement | Test Evidence To Add Or Carry Forward | Expected Result |
|---|---|---|
| `SPEC-1710` Gateway Agent capability surface | New pytest assertions for four Gateway capabilities, stable skills, registry metadata, and dispatch behavior; existing `TestGatewayAgent` method tests carried forward | Gateway Agent has deterministic live test evidence for discovery, tool identity, dispatch, and implemented method behavior |
| `SPEC-1706` configuration-driven discovery and MCP tool-use pattern | `PluginAgentRegistry.load_from_yaml()` and `PluginDispatcher.dispatch()` exercised directly | Production registry and dispatcher APIs expose and route the Gateway Agent without source inspection |
| `SPEC-1852` canonical agent identity | Registry test asserts `agent_kind == "peer"` for `gateway` | Gateway Agent identity uses the canonical field |
| `SPEC-1853` stable skill/tool identity | Registry test asserts `gateway:<skill>` ids, modes, and MCP mappings | Skill identities remain stable and mapped to Gateway MCP tools |
| `SPEC-1710` real-time transport context | Proposal identifies existing WebSocket/SSE implementation and treats new transport-specific tests as out of scope unless LO requires revision | The bridge record avoids false coverage claims for transport behavior |
| `GOV-10` / `SPEC-1649` live-interface test policy | Tests call production Python APIs and parse YAML through the registry, not text-grep source | Evidence is behavioral/interface-based |

Verification commands after implementation:

```powershell
python -m pytest applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py applications/Agent_Red/tests/agents/plugins/test_domain_agents.py::TestGatewayAgent -q --tb=short
python -m ruff check applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py
python -m ruff format --check applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py
```

## Acceptance Criteria

- Added tests fail closed if the `gateway` registry entry is missing, misidentified, disabled, assigned the wrong spec id, missing any Gateway Agent MCP capability, missing stable skill ids, or mapping a Gateway tool to a non-Gateway agent.
- Added dispatch evidence verifies a Gateway tool invocation through `PluginDispatcher` reaches the Gateway Agent endpoint with tenant and conversation context.
- Carried-forward existing tests continue to cover Gateway availability, queueing, context transfer, and queue monitoring behavior.
- Tests do not open real WebSocket/SSE connections, call workforce-management/CRM systems, or depend on a hosted Gateway container.
- No production source, runtime config, credentials, formal artifacts, or project membership are mutated under this proposal.
- Post-implementation report includes exact command output and maps each linked spec to observed test evidence.

## Code Quality Baseline

| Rule | Applicability | Proposal Position |
|---|---|---|
| `CQ-SECRETS-001` | Applies | Test data must use synthetic tenant/conversation/customer ids and no credentials. |
| `CQ-PATHS-001` | Applies | No absolute runtime paths are added to tests. |
| `CQ-CONSTANTS-001` | Applies | Expected Gateway capability and skill names are domain-stable contract literals; no non-obvious tuned values are introduced. |
| `CQ-DOCS-001` | Applies | Test names and focused assertions should carry the intent; no noisy comments. |
| `CQ-COMPLEXITY-001` | Applies | Test additions are small focused functions/classes in one focused file. |
| `CQ-TESTS-001` | Applies | This proposal is test-only and adds direct regression coverage. |
| `CQ-LOGGING-001` | N/A | No logging behavior changes. |
| `CQ-SECURITY-001` | Applies | Security review is limited to synthetic data, no external escalation systems, and fake HTTP dispatch with no external network calls. |
| `CQ-VERIFICATION-001` | Applies | Automated pytest plus ruff check/format evidence required. |
| `CQ-PERF-001` | N/A | No hot-path production code or unbounded loops added. |
| `CQ-DEPS-001` | N/A | No dependency changes. |

## Risks / Rollback

- Risk: Existing `test_domain_agents.py` already covers the in-process Gateway Agent methods, so duplicating those assertions would not close the WI's current interface gap. Mitigation: scope this work to registry, skill identity, tool catalog, and dispatch evidence while carrying existing method tests forward.
- Risk: `SPEC-1710` transport wording could make registry/dispatch-only coverage insufficient. Mitigation: the proposal explicitly states that WebSocket/SSE transport tests are not newly added; Loyal Opposition can require a revision if Gateway-specific transport coverage is needed for GO.
- Risk: Escalation/live-agent wording could imply external workforce, CRM, or agent desktop integration coverage. Mitigation: tests use synthetic payloads and fake dispatch only.
- Rollback: delete the new test file. No data migration or production rollback is required.

## Files Expected To Change

- `applications/Agent_Red/tests/agents/plugins/test_gateway_agent_registry_dispatch.py`

## Recommended Commit Type

`test`
