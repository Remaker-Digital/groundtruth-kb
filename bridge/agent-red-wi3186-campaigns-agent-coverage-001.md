NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex Desktop interactive Prime Builder session override; application mode heartbeat continuation

# Implementation Proposal - WI-3186 Campaigns Agent Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3186-campaigns-agent-coverage
Version: 001
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3186

target_paths: ["applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py", "applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py"]

## Claim

Add deterministic repository-native pytest evidence for `SPEC-1707` by exercising the current Agent Red plug-in registry and dispatch interfaces for the Campaigns Agent. Existing tests already cover the in-process `CampaignsAgentTools` methods; this proposal closes the remaining live-interface gap by proving the Campaigns Agent is discoverable from `agents.yaml`, exposes the expected MCP tool identities and stable skill identities, has the intended peer/tier/mode metadata, resolves the four campaign capabilities to the Campaigns Agent, and dispatches a campaign tool through the production `PluginDispatcher` route.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-1707` defines the Campaigns Agent capability surface and cites `SPEC-1706` for the independent MCP server/container, configuration-driven discovery, and MCP tool-use interaction model. `SPEC-1852` and `SPEC-1853` define the current registry fields needed to make that surface durable (`agent_kind`, stable `skill_id`, skill mode, and MCP tool mappings). No owner clarification is needed because the implementation is limited to test additions against existing production interfaces.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py` and `applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py`.

## Bridge File Chain Evidence

This is a first `NEW` proposal for document `agent-red-wi3186-campaigns-agent-coverage`. If approved by the preflight gates, it will be filed append-only as `bridge/agent-red-wi3186-campaigns-agent-coverage-001.md` through the governed helper-mediated bridge path. No prior version exists and no prior bridge version will be rewritten or deleted.

## Specification Links

- `SPEC-1707` - Direct target requirement: Campaigns Agent marketing campaign information MCP server, including active/scheduled campaign queries, discount codes/offers, campaign talking points, conversation metrics, routing support, `agents.yaml` discovery, and MCP tool-use protocol.
- `SPEC-1706` - Parent architecture requirement for modular plug-in MCP agents: configuration-driven discovery, separate agent endpoints, capability/tool exposure, and dispatch through the MCP tool-use pattern.
- `SPEC-1852` - Agent identity requirement: the Campaigns Agent must be represented with canonical `agent_kind` semantics rather than legacy ambiguous classification.
- `SPEC-1853` - Stable skill/tool identity requirement: the Campaigns Agent skills must expose stable `campaigns:<skill>` identifiers mapped to underlying MCP tool names and declare read/mutate modes.
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

- `DELIB-0712` - 16.B methodology review classifying coverage gaps, including SPEC-1707, by evidence quality.
- `DELIB-0713` - Owner decision rejecting assertion-only/phantom-only evidence as sufficient for behavioral requirements.
- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-20265110` - POR Step 16.D phantom spec-link cleanup review; relevant to avoiding false coverage from stale or phantom evidence.
- `DELIB-20263468` - WI-4455 Loyal Opposition advisory recognizing repository-native pytest evidence as the live verification surface.
- Semantic deliberation search for `SPEC-1707 Campaigns Agent Marketing Campaign Information MCP Server phantom-only evidence` returned no more specific Campaigns Agent owner decision beyond the methodology/project authorization records above.

## Owner Decisions / Input

- `DELIB-20265586` and `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23` authorize bounded implementation for the snapshot-bound 38-WI project membership, including `WI-3186`.
- Mutation class: `test_addition`.
- No new owner input is required. This proposal does not add a work item, broaden project membership, deploy, mutate credentials, perform destructive cleanup, or change formal GOV/SPEC/ADR/DCL/PB/REQ artifacts.

## Proposed Scope

1. Add `SPEC-1707`-specific tests to `applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py` that load the production `agents.yaml` through `PluginAgentRegistry.load_from_yaml()` and assert:
   - `campaigns` is present with `spec_id == "SPEC-1707"`, `agent_kind == "peer"`, category `marketing`, professional tier gate, internal auth, health check, and the expected endpoint template.
   - The four campaign MCP capabilities are present: `campaigns.list_active`, `campaigns.get_discount_codes`, `campaigns.get_talking_points`, and `campaigns.track_metrics`.
   - Stable skill ids map to the corresponding MCP tool names, with the expected `read`/`mutate` modes.
   - The generated tool catalog and `resolve_tool_agent()` route campaign capabilities to the `campaigns` agent.
2. Add `SPEC-1707`-specific tests to `applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py` that dispatch at least one Campaigns Agent tool through `PluginDispatcher` using the production YAML registry and a fake HTTP client, then assert the constructed URL, payload, tenant/conversation headers, success metadata, and `agent_id == "campaigns"`.
3. Do not change production code unless the approved test exposes an implementation defect; if a production defect is discovered, stop and file a revised proposal or follow the bridge finding path before widening scope.

## Specification-Derived Verification Plan

| Spec / Requirement | Test Evidence To Add | Expected Result |
|---|---|---|
| `SPEC-1707` Campaigns Agent capability surface | Pytest assertions in registry/dispatch tests for four Campaigns Agent capabilities and dispatch behavior | Campaigns Agent has deterministic live test evidence for discovery, tool identity, and dispatch |
| `SPEC-1706` configuration-driven discovery and MCP tool-use pattern | `PluginAgentRegistry.load_from_yaml()` and `PluginDispatcher.dispatch()` exercised directly | Production registry and dispatcher APIs expose and route the Campaigns Agent without source inspection |
| `SPEC-1852` canonical agent identity | Registry test asserts `agent_kind == "peer"` for campaigns | Campaigns Agent identity uses the canonical field |
| `SPEC-1853` stable skill/tool identity | Registry test asserts `campaigns:<skill>` ids, modes, and MCP mappings | Skill identities remain stable and mapped to campaign MCP tools |
| `GOV-10` / `SPEC-1649` live-interface test policy | Tests call production Python APIs and parse YAML through the registry, not text-grep source | Evidence is behavioral/interface-based |

Verification commands after implementation:

```powershell
python -m pytest applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py
python -m ruff format --check applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py
```

## Acceptance Criteria

- Added tests fail closed if the `campaigns` registry entry is missing, misidentified, disabled, assigned the wrong spec id, missing any Campaigns Agent MCP capability, missing stable skill ids, or mapping a campaign tool to a non-campaigns agent.
- Added dispatch evidence verifies a campaign tool invocation through `PluginDispatcher` reaches the Campaigns Agent endpoint with tenant and conversation context.
- No production source, runtime config, credentials, formal artifacts, or project membership are mutated under this proposal.
- Post-implementation report includes exact command output and maps each linked spec to observed test evidence.

## Code Quality Baseline

| Rule | Applicability | Proposal Position |
|---|---|---|
| `CQ-SECRETS-001` | Applies | Test data must use synthetic tenant/conversation ids and no credentials. |
| `CQ-PATHS-001` | Applies | No absolute runtime paths are added to tests. |
| `CQ-CONSTANTS-001` | Applies | Expected campaign capability and skill names are domain-stable contract literals; no non-obvious tuned values are introduced. |
| `CQ-DOCS-001` | Applies | Test names and focused assertions should carry the intent; no noisy comments. |
| `CQ-COMPLEXITY-001` | Applies | Test additions are small focused functions/classes under existing files. |
| `CQ-TESTS-001` | Applies | This proposal is test-only and adds direct regression coverage. |
| `CQ-LOGGING-001` | N/A | No logging behavior changes. |
| `CQ-SECURITY-001` | Applies lightly | Dispatcher test uses synthetic inputs and does not expose credentials or external network calls. |
| `CQ-VERIFICATION-001` | Applies | Automated pytest plus ruff check/format evidence required. |
| `CQ-PERF-001` | N/A | No hot-path production code or unbounded loops added. |
| `CQ-DEPS-001` | N/A | No dependency changes. |

## Risks / Rollback

- Risk: Existing registry tests already cover generic discovery, so overly broad assertions could duplicate coverage. Mitigation: keep the additions narrowly tied to `SPEC-1707` Campaigns Agent metadata, skill mappings, and dispatch route.
- Risk: Dispatch tests must not perform real network calls. Mitigation: use a fake HTTP client and assert the constructed request.
- Rollback: remove the added test functions from the two targeted files. No data migration or production rollback is required.

## Files Expected To Change

- `applications/Agent_Red/tests/agents/plugins/test_plugin_registry.py`
- `applications/Agent_Red/tests/agents/plugins/test_plugin_dispatch.py`

## Recommended Commit Type

`test`
