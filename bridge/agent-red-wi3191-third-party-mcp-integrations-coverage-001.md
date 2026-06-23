NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5 Codex
author_model_version: 2026-06-23
author_model_configuration: Codex Desktop interactive Prime Builder session override; application mode heartbeat continuation

# Implementation Proposal - WI-3191 Third-Party MCP Integrations Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3191-third-party-mcp-integrations-coverage
Version: 001
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3191

target_paths: ["applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py"]

## Claim

Add deterministic repository-native pytest evidence for `SPEC-1712` by exercising the current Agent Red plug-in registry and dispatch surfaces for the five configured third-party MCP server integrations: Stripe, Shopify, Square, PayPal, and Coinbase. Existing tests already cover the in-process `ExternalMcpConnector` circuit breaker, rate limiter, cache, tool discovery, invocation, status, and audit behavior with synthetic registry data; this proposal closes the remaining production-registry gap by proving the external MCP server definitions in `agents.yaml` are discoverable, tagged to `SPEC-1712`, expose the expected capabilities and stable skill identities, carry credential/auth/tier/read-only metadata, participate in default routing rules where configured, resolve tools to the external server entries, and dispatch through the production `PluginDispatcher` external route without touching live third-party networks.

This proposal is intentionally test-only. It does not implement or claim real Stripe, Shopify, Square, PayPal, Coinbase, tenant credential storage, Azure Key Vault, PCI compliance, consent flows, rate-limit infrastructure, circuit-breaker persistence, or hosted MCP-container behavior. `SPEC-1712` includes those production-security and integration expectations; this proposal documents the boundary explicitly and focuses on the implemented Agent Red registry, skill, discovery, and dispatcher surfaces plus existing connector method coverage.

## Requirement Sufficiency

Existing requirements sufficient. Existing requirements are sufficient for this test-only coverage proposal. `SPEC-1712` defines the third-party MCP server capability surface and cites `SPEC-1706` for configuration-driven MCP plug-in discovery and dispatch. `SPEC-1853` defines stable skill ids and MCP tool mappings, while `SPEC-1857` provides the binding/credential boundary context that prevents base dispatcher evidence from implying tenant exposure. Existing `test_external_mcp.py` tests cover connector behavior with synthetic external servers; this proposal adds missing evidence against the production YAML registry and dispatcher route without broadening production behavior.

## In-Root Placement Evidence

The target path is inside `E:\GT-KB`: `applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py`.

## Bridge File Chain Evidence

This is a first `NEW` proposal for document `agent-red-wi3191-third-party-mcp-integrations-coverage`. If approved by the preflight gates, it will be filed append-only as `bridge/agent-red-wi3191-third-party-mcp-integrations-coverage-001.md` through the governed helper-mediated bridge path. No prior version exists and no prior bridge version will be rewritten or deleted.

## Specification Links

- `SPEC-1712` - Direct target requirement: third-party MCP server integrations for Stripe, Shopify, Square, PayPal, Coinbase, and any MCP-compliant server, including authenticated transport, tenant-scoped credentials, tool discovery, request caching, rate limiting, circuit breaking, audit logging, and consent/security context.
- `SPEC-1706` - Parent architecture requirement for modular MCP plug-in agents: configuration-driven discovery, separate agent/server definitions, capability/tool exposure, and dispatch through the MCP tool-use pattern.
- `SPEC-1853` - Stable skill/tool identity requirement: external MCP servers must expose stable `<server>:<skill>` identities mapped to underlying MCP tool names and modes.
- `SPEC-1857` - Binding and credential boundary context: base registry/dispatch tests must not imply tenant access unless skills are bound and credentials are resolved through the binding path.
- `SPEC-1861` - Default routing context: payment and subscription intents map to Stripe MCP skills in `agents.yaml`; test coverage should keep those production routing entries durable without asserting tenant overlay enablement.
- `GOV-10` - Test artifacts must exercise exposed production interfaces; this proposal uses registry and dispatcher APIs rather than source-text inspection.
- `SPEC-1649` - Master test plan/live interface policy; repository-native pytest evidence is limited to live production interfaces and avoids source inspection.
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

- `DELIB-0712` - 16.B methodology review classifying coverage gaps, including `SPEC-1712`, by evidence quality.
- `DELIB-0713` - Owner decision rejecting assertion-only/phantom-only evidence as sufficient for behavioral requirements.
- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-20265105` - POR Step 16.C phantom WI creation review; relevant to avoiding false closure from phantom evidence.
- `DELIB-20265110` - POR Step 16.D phantom spec-link cleanup review; relevant to avoiding false coverage from stale or phantom evidence.
- `DELIB-20263468` - WI-4455 Loyal Opposition advisory recognizing repository-native pytest evidence as the live verification surface.
- `DELIB-0026` - Broader containerized agent transport review noting owner MCP policy context; relevant only as background for avoiding false MCP runtime claims.
- Semantic deliberation search for `SPEC-1712 3rd-Party MCP Server Integrations External Service Connectors phantom-only evidence DELIB-0712 DELIB-0713` returned broad MCP transport, bridge-dispatch, and scaffold history records but no more specific third-party MCP integration owner decision beyond the methodology/project authorization records above.

## Owner Decisions / Input

- `DELIB-20265586` and `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23` authorize bounded implementation for the snapshot-bound 38-WI project membership, including `WI-3191`.
- Mutation class: `test_addition`.
- No new owner input is required. This proposal does not add a work item, broaden project membership, deploy, mutate credentials, perform destructive cleanup, or change formal GOV/SPEC/ADR/DCL/PB/REQ artifacts.

## Proposed Scope

1. Add `applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py` with `SPEC-1712`-specific tests that load the production `agents.yaml` through `PluginAgentRegistry.load_from_yaml()` and assert:
   - The five external MCP server ids are present: `stripe_mcp`, `shopify_mcp`, `square_mcp`, `paypal_mcp`, and `coinbase_mcp`.
   - Each server has `spec_id == "SPEC-1712"`, `category == "external"`, `agent_kind == "peer"`, `is_external is True`, non-empty endpoint, expected auth type, tier gate, read-only flag, lifecycle status, and expected credential-env metadata where configured.
   - Capabilities for Stripe, Shopify, Square, PayPal, and Coinbase match the production YAML contract.
   - Stable skill ids map to the corresponding MCP tool names, modes, and credential types.
   - `get_external_servers()`, `find_by_capability()`, `resolve_tool_agent()`, and `get_tool_catalog()` expose the external MCP entries without source inspection.
2. Add focused default-routing assertions proving `payment_issue` and `subscription_question` route to the configured Stripe MCP skills, while documenting that tenant overlays and bindings remain outside this proposal.
3. Add a fake external-dispatch test in the same file that invokes one external MCP tool through `PluginDispatcher` using the production YAML registry, monkeypatches the external dispatch boundary to avoid live network/credential access, and asserts the selected external server, endpoint metadata, `is_external` metadata, tenant context, and successful result shape.
4. Identify existing connector tests in `applications/Agent_Red/tests/agents/plugins/test_external_mcp.py` as carried-forward evidence for circuit breaker, rate limiting, caching, tool discovery, invocation flow, server status, and audit logging behavior.
5. Treat real third-party provider calls, Azure Key Vault, tenant credential storage, PCI compliance, consent activation, AGNTCY SDK live client behavior, and hosted MCP-container behavior as outside this test-addition proposal unless Loyal Opposition requires a revised target path and scope.
6. Do not change production code unless the approved test exposes an implementation defect; if a production defect is discovered, stop and file a revised proposal or follow the bridge finding path before widening scope.

## Specification-Derived Verification Plan

| Spec / Requirement | Test Evidence To Add Or Carry Forward | Expected Result |
|---|---|---|
| `SPEC-1712` external MCP provider set | New pytest assertions for the five production external server entries, provider capabilities, auth/credential/tier/read-only metadata, skills, and default routing rules | Third-party MCP integrations have deterministic live test evidence against `agents.yaml` |
| `SPEC-1712` connector behavior | Existing `test_external_mcp.py` carried forward for circuit breaker, rate limit, cache, discovery, invocation, status, and audit logging | Existing synthetic connector behavior remains covered |
| `SPEC-1706` configuration-driven discovery and MCP tool-use pattern | `PluginAgentRegistry.load_from_yaml()`, `resolve_tool_agent()`, `get_tool_catalog()`, and `PluginDispatcher.dispatch()` exercised directly | Production registry and dispatcher APIs expose and route external MCP servers without source inspection |
| `SPEC-1853` stable skill/tool identity | New tests assert `<server>:<skill>` ids, modes, credential types, and MCP tool mappings | Skill identities remain stable and mapped to external MCP tools |
| `SPEC-1857` binding/credential boundary | Proposal and tests avoid tenant exposure claims; fake dispatch avoids real credential use and does not exercise bound catalog behavior | Registry/dispatch evidence does not overclaim tenant authorization |
| `SPEC-1861` default routing context | New tests assert configured Stripe MCP routing rules for payment/subscription intents | Default route entries stay durable while tenant overlay behavior remains out of scope |
| `GOV-10` / `SPEC-1649` live-interface test policy | Tests call production Python APIs and parse YAML through the registry, not text-grep source | Evidence is behavioral/interface-based |

Verification commands after implementation:

```powershell
python -m pytest applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py applications/Agent_Red/tests/agents/plugins/test_external_mcp.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py
python -m ruff format --check applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py
```

## Acceptance Criteria

- Added tests fail closed if any configured `SPEC-1712` external MCP server is missing, misidentified, disabled, assigned the wrong spec id, missing expected capabilities, missing stable skill ids, or missing expected auth/credential/tier/read-only metadata.
- Added tests prove Stripe payment and subscription default routing still points to the configured Stripe MCP skill ids.
- Added dispatch evidence verifies an external MCP tool invocation through `PluginDispatcher` selects the external server route and reports external metadata without making live network calls or reading credentials.
- Carried-forward existing tests continue to cover connector circuit breaker, rate-limit, cache, tool-discovery, invocation, status, and audit logging behavior.
- Tests do not call Stripe, Shopify, Square, PayPal, Coinbase, Azure Key Vault, AGNTCY live clients, or a hosted MCP server.
- No production source, runtime config, credentials, formal artifacts, or project membership are mutated under this proposal.
- Post-implementation report includes exact command output and maps each linked spec to observed test evidence.

## Code Quality Baseline

| Rule | Applicability | Proposal Position |
|---|---|---|
| `CQ-SECRETS-001` | Applies | Test data must use synthetic tenant/provider values and must not read or embed credentials. |
| `CQ-PATHS-001` | Applies | No absolute runtime paths are added to tests. |
| `CQ-CONSTANTS-001` | Applies | Expected provider ids, capabilities, and skill names are domain-stable contract literals. |
| `CQ-DOCS-001` | Applies | Test names and focused assertions should carry the intent; no noisy comments. |
| `CQ-COMPLEXITY-001` | Applies | Test additions are small focused functions/classes in one focused file. |
| `CQ-TESTS-001` | Applies | This proposal is test-only and adds direct regression coverage. |
| `CQ-LOGGING-001` | N/A | No logging behavior changes. |
| `CQ-SECURITY-001` | Applies | Security review is limited to synthetic data, no credential reads, no external network calls, and fake external dispatch. |
| `CQ-VERIFICATION-001` | Applies | Automated pytest plus ruff check/format evidence required. |
| `CQ-PERF-001` | N/A | No hot-path production code or unbounded loops added. |
| `CQ-DEPS-001` | N/A | No dependency changes. |

## Risks / Rollback

- Risk: Existing `test_external_mcp.py` already covers connector internals, so duplicating those assertions would not close the WI's production-registry gap. Mitigation: scope this work to `agents.yaml`, skill identity, tool catalog, routing-rule, and dispatcher evidence while carrying existing connector tests forward.
- Risk: `SPEC-1712` security and integration wording could make registry/dispatch-only coverage insufficient. Mitigation: the proposal explicitly states that live provider calls, Key Vault, PCI, consent, tenant credential storage, and hosted MCP behavior are not newly added; Loyal Opposition can require a revision if that coverage is needed for GO.
- Risk: External MCP dispatcher code may try to import AGNTCY or read credential env vars. Mitigation: the new test will monkeypatch the external dispatch boundary and assert route selection/metadata rather than exercising live client creation.
- Rollback: delete the new test file. No data migration or production rollback is required.

## Files Expected To Change

- `applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py`

## Recommended Commit Type

`test`
