NEW
author_identity: prime-builder/codex-automation
author_harness_id: A
author_session_context_id: 019ef424-e515-7073-81cd-3ea59a85ce54
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation Auto-builder; approval_policy=never; workspace E:\GT-KB

# WI-3191 Third-Party MCP Integrations Coverage Implementation Report

bridge_kind: implementation_report
Document: agent-red-wi3191-third-party-mcp-integrations-coverage
Version: 003
Status: NEW
Date: 2026-06-23 UTC
Responds to GO: bridge/agent-red-wi3191-third-party-mcp-integrations-coverage-002.md
Approved proposal: bridge/agent-red-wi3191-third-party-mcp-integrations-coverage-001.md
Implementation commit: ceabab819e65c0e350c9428ff1a72cbfb1b23a1a

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3191

target_paths: ["applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py"]

## Implementation Claim

Implemented the approved test-only WI-3191 slice by adding repository-native pytest coverage for the SPEC-1712 external MCP registry and dispatch surfaces at the single GO-authorized target path:

- applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py

The new tests load the production Agent Red plug-in registry from agents.yaml, assert external MCP server metadata for Stripe, Shopify, Square, PayPal, and Coinbase, verify stable external MCP skill ids, read/mutate modes, credential types, tool catalog exposure, capability lookup, and tool-to-agent resolution, verify default Stripe routing rules, and dispatch stripe.list_charges through PluginDispatcher using a monkeypatched external-dispatch path so no live provider call occurs. The verification lane also carries forward the existing external MCP unit tests in applications/Agent_Red/tests/agents/plugins/test_external_mcp.py.

The implementation does not call real third-party MCP providers, use credentials, change production source, mutate runtime config, alter formal artifacts, change project membership, or mutate MemBase records.

## Specification Links

- SPEC-1712 - Third-party MCP server integration requirement for Stripe, Shopify, Square, PayPal, and Coinbase.
- SPEC-1706 - Parent plug-in MCP-agent architecture requiring configuration-driven discovery, separate agent endpoints, capability/tool exposure, and dispatch through the MCP tool-use pattern.
- SPEC-1852 - Canonical agent identity via agent_kind.
- SPEC-1853 - Stable skill and MCP tool identity via external_mcp:<skill> ids, tool mappings, read/mutate modes, and credential requirements.
- SPEC-1857 - Dispatcher/catalog guardrail context; this base dispatcher coverage must not imply tenant binding exposure.
- SPEC-1861 - Intent-router boundary context; this coverage stays limited to registry and dispatcher surfaces.
- GOV-10 - Test artifacts must exercise exposed production interfaces.
- SPEC-1649 - Master live-interface test policy; evidence is repository-native pytest over production APIs, not source inspection.
- GOV-12 - Work item creation triggers test creation.
- GOV-13 - Test visibility and phase governance.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - Project-scoped authorization bounds owner approval and does not bypass bridge review or verification.
- SPEC-CODE-QUALITY-CHECKLIST-001 - Baseline code-quality checklist.
- GOV-FILE-BRIDGE-AUTHORITY-001 - Status-bearing numbered bridge files govern bridge authority.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - Proposal and report must cite applicable specifications.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - Verification must map linked specs to executed test evidence.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - Project authorization, project id, work item, and target paths must be explicit.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - Agent Red application artifacts live under applications/Agent_Red/.
- GOV-STANDING-BACKLOG-001 - WI-3191 is governed backlog work.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 - Codex uses helper-mediated bridge write paths and explicit preflight evidence.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - Implementation intent and evidence are durable artifacts.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - Implementation and review evidence are preserved as governed artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - The owner-authorized WI implementation crosses the threshold for bridge capture.

## Prior Deliberations

- DELIB-0712 - 16.B methodology review classifying coverage gaps, including SPEC-1712, by evidence quality.
- DELIB-0713 - Owner decision rejecting assertion-only or phantom-only evidence as sufficient for behavioral requirements.
- DELIB-20265586 - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- DELIB-20265105 - POR Step 16.C phantom WI creation review.
- DELIB-20265110 - POR Step 16.D phantom spec-link cleanup review.
- DELIB-20263468 - WI-4455 Loyal Opposition advisory recognizing repository-native pytest evidence as the live verification surface.
- bridge/agent-red-wi3191-third-party-mcp-integrations-coverage-001.md - Approved implementation proposal.
- bridge/agent-red-wi3191-third-party-mcp-integrations-coverage-002.md - Loyal Opposition GO verdict.

## Owner Decisions / Input

No new owner decision was required for this implementation. The work stayed within:

- DELIB-20265586
- PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
- bridge/agent-red-wi3191-third-party-mcp-integrations-coverage-002.md

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| SPEC-1712 | The new pytest file asserts external MCP metadata for Stripe, Shopify, Square, PayPal, and Coinbase; their capabilities, endpoints, auth types, credential env vars, read-only flags, status, and tier gates; stable external MCP skill ids; credential types; read/mutate modes; tool catalog exposure; capability lookup; tool-to-agent resolution; default Stripe routing rules; and PluginDispatcher dispatch to stripe.list_charges without a live provider call. |
| SPEC-1706 | Tests call PluginAgentRegistry.load_from_yaml() and PluginDispatcher.dispatch() against production Agent Red APIs. |
| SPEC-1852 | Tests assert every covered external MCP server has agent_kind == "peer". |
| SPEC-1853 | Tests assert stable <server>:<skill> ids, read/mutate modes, credential types, and MCP tool mappings. |
| SPEC-1857 and SPEC-1861 | Tests use the base production dispatcher/catalog route without asserting tenant binding or intent-router exposure. |
| SPEC-1712 live-provider context | This slice intentionally avoids live third-party calls and credentials; it verifies repository-native registry, catalog, routing, and dispatcher integration surfaces only. |
| GOV-10 and SPEC-1649 | Evidence comes from repository-native pytest over live interfaces, not source-text inspection. |
| GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 | Bridge report carries project metadata, target paths, linked specs, spec-to-test mapping, exact commands, and observed results. Applicability and clause preflights passed. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | All implementation and verification paths are under E:\GT-KB\applications\Agent_Red or E:\GT-KB\bridge. |
| GOV-STANDING-BACKLOG-001 and WI-3191 | Work was selected from live governed backlog and bridge GO state; this report does not claim unrelated WI closure. |

## Commands Run

```text
python -m pytest applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py applications/Agent_Red/tests/agents/plugins/test_external_mcp.py -q --tb=short --basetemp .gtkb-state\pytest-wi3191-rerun
python -m ruff check applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py
python -m ruff format --check applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py
python scripts/implementation_authorization.py validate --target applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py
python scripts/bridge_applicability_preflight.py --bridge-id agent-red-wi3191-third-party-mcp-integrations-coverage
python scripts/adr_dcl_clause_preflight.py --bridge-id agent-red-wi3191-third-party-mcp-integrations-coverage
Test-Path -LiteralPath bridge\INDEX.md
git commit -m "test: cover external mcp registry dispatch" --only -- applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py
```

## Observed Results

- Pytest: 24 passed in 1.76s.
- Ruff check: All checks passed.
- Ruff format check: 1 file already formatted.
- Implementation authorization validation: authorized true; targets ["applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py"].
- Applicability preflight: preflight_passed true; missing_required_specs []; missing_advisory_specs []; packet_hash sha256:508a809882f10bc7f3935585c82b6e3d241d4c891194286952743c3345b538e2.
- Clause preflight: clauses evaluated 5; must_apply 2; evidence gaps in must_apply clauses 0; blocking gaps 0; exit 0.
- Retired bridge index check: False.
- Commit: ceabab819e65c0e350c9428ff1a72cbfb1b23a1a test: cover external mcp registry dispatch.

## Files Changed

- applications/Agent_Red/tests/agents/plugins/test_external_mcp_registry_dispatch.py - new SPEC-1712 live-interface registry and dispatch coverage.

## Recommended Commit Type

Recommended commit type: test:

Justification: the committed payload is test-only coverage for an existing Agent Red external MCP integration contract.

## Acceptance Criteria Status

- [x] Tests fail closed if the Stripe, Shopify, Square, PayPal, or Coinbase external MCP registry entries are missing, misidentified, assigned the wrong spec id, missing declared capabilities, assigned wrong endpoints/auth types/credential env vars/status/tier gates/read-only flags, or mapped to a non-peer agent kind.
- [x] Tests verify stable skill ids, read/mutate modes, credential types, and MCP tool mappings for the covered external MCP providers.
- [x] Tests verify tool catalog entries, capability lookup, tool-to-agent resolution, and default Stripe routing rules.
- [x] Dispatch evidence verifies an external MCP tool invocation through PluginDispatcher reaches the expected external agent metadata path without a live provider call.
- [x] The carried-forward external MCP test lane remains green.
- [x] Tests do not call real third-party MCP providers, use credentials, mutate runtime config, or depend on hosted external services.
- [x] No production source, runtime config, credentials, formal artifacts, project membership, or MemBase records were mutated.
- [x] Exact command output and spec-to-test mapping are included above.

## Risk And Rollback

Residual risk is limited to test maintenance if the external MCP registry contract intentionally changes. Rollback is to revert commit ceabab819e65c0e350c9428ff1a72cbfb1b23a1a, removing the single new test file. Bridge audit files remain append-only.

## Loyal Opposition Asks

1. Verify that the new test file and carried-forward external MCP lane satisfy SPEC-1712 live-interface coverage for WI-3191.
2. Confirm the test-only commit stayed within the approved target path.
3. Return VERIFIED if satisfied, or NO-GO with concrete findings.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
