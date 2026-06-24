NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3203 Container Failure Resilience Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3203-container-failure-resilience-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3203

target_paths: ["applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py"]

## Claim

WI-3203 should be implemented as a narrow test-only backfill for the historical `SPEC-1799` Container Failure Resilience requirement.

Current Agent Red source already exposes the relevant live interfaces:

- `applications/Agent_Red/src/agents/containers/agent_app.py` provides per-agent container `/health` and `/ready` probes. `/ready` returns HTTP 503 before the agent is configured and returns HTTP 200 once the agent is configured again, giving a deterministic local proxy for degraded readiness and automatic recovery after restart/setup.
- `applications/Agent_Red/src/chat/pipeline/agent_dispatch.py` enforces the current all-tiers-exhausted path with HTTP 503 and a tier-diagnostic message when transport plus HTTP container dispatch cannot serve a non-streaming agent request.
- `applications/Agent_Red/src/app/health.py` enforces gateway `/ready` HTTP 503 when AGNTCY transport is inactive under the current transport-readiness policy.

This proposal adds one deterministic pytest file that binds those live interfaces to WI-3203 and the historical SPEC-1799 clauses. It does not authorize source edits. If Loyal Opposition concludes that `SPEC-1799` requires direct container `process()` exceptions to be converted from the current 500 error wrapper into 503, or requires a concrete multi-replica kill/restart harness, this proposal should receive `NO-GO` and be revised with source/test or harness scope instead of broadening under this NEW proposal.

## Requirement Sufficiency

Existing requirements are sufficient for a test-only compatibility-boundary backfill.

`SPEC-1799` states the historical behavior: when an agent container fails or restarts, in-flight requests receive 503, gateway `/ready` reflects degraded status, and recovery is automatic. MemBase currently marks `SPEC-1799` as `retired` under FAB-11 app-scoped history because the old assertion evidence became stale after Agent Red moved under `applications/Agent_Red/`; the open WI remains the active project member asking for deterministic replacement evidence.

The active/implemented `SPEC-1802` and current retired-history `SPEC-1780`/`DCL-002` explain the current dispatch and readiness semantics: non-streaming agent dispatch follows SLIM/NATS/HTTP and fails with 503 when all tiers are exhausted, and `/ready` must fail loud when transport is unavailable. That is the live-interface interpretation used by this proposal.

No new owner decision is needed because implementation is limited to test additions against existing source. The only interpretation risk is whether Loyal Opposition requires a stronger direct-container-failure semantic than the current dispatch/readiness surfaces expose.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\agents\test_container_failure_resilience_spec1799.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\agents\containers\agent_app.py`
- `E:\GT-KB\applications\Agent_Red\src\agents\base.py`
- `E:\GT-KB\applications\Agent_Red\src\chat\pipeline\agent_dispatch.py`
- `E:\GT-KB\applications\Agent_Red\src\app\health.py`
- `E:\GT-KB\applications\Agent_Red\tests\agents\test_agent_app.py`
- `E:\GT-KB\applications\Agent_Red\tests\test_health.py`

## Specification Links

- `SPEC-1799` - Direct historical requirement text and source spec for container failure resilience.
- `SPEC-1802` - Current implemented per-interface transport policy; non-streaming dispatch fails with HTTP 503 when SLIM/NATS/HTTP tiers are exhausted.
- `SPEC-1780` - Historical fail-loud transport/readiness requirement; `/ready` returns HTTP 503 when transport is inactive.
- `DCL-002` - Historical design constraint that non-streaming canonical dispatch must not silently fall back to in-process execution.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live agent-container readiness and dispatch failure surfaces are the exposed artifacts under test.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3203`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `bridge/por-step16c-stream-d-phantom-wi-creation-007.md` - Inventory table maps `WI-3203` to `SPEC-1799`, delta-prime, title "Container Failure Resilience".
- `gt deliberations search "SPEC-1799 Container Failure Resilience WI-3203"` returned no blocking owner decision specific to WI-3203 beyond broad governance/advisory records.
- `gt bridge threads --wi WI-3203 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3203 --json` shows open/backlogged `WI-3203`, source spec `SPEC-1799`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says assertion-only verification was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1799 --json` shows title "Container Failure Resilience", status `retired`, tags `fab11-app-scoped-history`, and the historical clause text: in-flight requests receive 503, gateway `/ready` reflects degraded status, and recovery is automatic.
- `applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py` does not currently exist.
- `applications/Agent_Red/src/agents/containers/agent_app.py` declares `/ready` as 503 until `agent._configured` and 200 after configuration.
- `applications/Agent_Red/src/agents/base.py` declares `AgentRedBaseAgent.setup()` sets `_configured = True` and `health()` reports `healthy` only when configured.
- `applications/Agent_Red/src/chat/pipeline/agent_dispatch.py` declares `_require_transport_or_fail()` and raises HTTP 503 with a tier-diagnostic message when all non-streaming dispatch tiers are exhausted.
- `applications/Agent_Red/src/app/health.py` returns gateway `/ready` HTTP 503 when `agntcy_sdk.transport_active` is false.
- Existing tests cover generic agent app and health behavior, but there is no named `SPEC-1799`/`WI-3203` deterministic coverage artifact tying degraded readiness, 503 dispatch, and recovery together.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3203-container-failure-resilience-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3203-container-failure-resilience-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py`.
2. In the new pytest, import live `create_agent_app`, `AgentRedBaseAgent`, and `AgentDispatchMixin` surfaces.
3. Define local test agents for configured/unconfigured readiness and request handling.
4. Assert agent container `/ready` returns HTTP 503 with `ready: false` before setup/configuration.
5. Assert agent container recovery is automatic at the live readiness boundary by invoking `agent.setup()` or setting equivalent configured state, then asserting `/ready` returns HTTP 200 with `ready: true`.
6. Assert `/health` reports 503/not_configured before setup and 200/healthy after setup.
7. Assert `AgentDispatchMixin._require_transport_or_fail("intent-classifier")` raises `fastapi.HTTPException` with status 503 and an all-tiers-exhausted diagnostic.
8. Assert a non-streaming dispatch path with no transport, HTTP container enabled, and a failing HTTP tier ends in the same 503 failure rather than silently calling the direct in-process method.
9. Keep implementation test-only unless a source gap is exposed; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1799` | New pytest imports live agent-container and dispatch surfaces and asserts degraded readiness, readiness recovery after setup, fail-loud 503 dispatch when tiers are exhausted, and no silent in-process fallback for non-streaming agent dispatch. |
| `SPEC-1802`, `SPEC-1780`, `DCL-002` | New pytest verifies current dispatch/readiness semantics that refine the historical resilience requirement: transport cascade failure ends in 503, and degraded readiness is exposed to traffic routing. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3203-container-failure-resilience-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py
python -m ruff format --check applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py
```

## Acceptance Criteria

- PASS when the new pytest verifies agent-container `/ready` returns HTTP 503 while the agent is not configured.
- PASS when the new pytest verifies agent-container `/ready` returns HTTP 200 after setup/configuration recovery.
- PASS when the new pytest verifies `/health` transitions from 503/not_configured to 200/healthy across setup.
- PASS when the new pytest verifies all-tiers-exhausted non-streaming dispatch raises HTTP 503 with a tier-diagnostic message.
- PASS when the new pytest verifies a failing HTTP container tier does not silently fall back to a direct in-process non-streaming agent method.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is moderate. The proposal intentionally tests the current live compatibility boundary for a retired historical resilience spec. It does not simulate a real Azure Container Apps kill/restart, and it does not change direct agent `process()` exception wrapping from 500 to 503. If Loyal Opposition requires either stronger behavior, return `NO-GO` so Prime Builder can revise with source/test or harness scope.

Rollback is to delete `applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/agents/test_container_failure_resilience_spec1799.py`

## Recommended Commit Type

`test:`
