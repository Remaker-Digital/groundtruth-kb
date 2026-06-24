NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3204 Multi-Replica Agent Routing Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3204-multi-replica-agent-routing-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3204

target_paths: ["applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py"]

## Claim

WI-3204 should be implemented as a narrow test-only backfill for the historical `SPEC-1800` Multi-Replica Agent Routing requirement.

Current Agent Red source already exposes deterministic live-interface routing surfaces that represent multi-replica compatibility without needing to spin up Azure Container Apps:

- `applications/Agent_Red/src/chat/pipeline/constants.py` builds per-agent HTTP URLs from the registry and the Azure Container Apps internal DNS convention `http://agent-red-{name}.internal.<CONTAINER_APP_ENV_FQDN>:8080`. That service-level address is the boundary where Azure's internal load balancer distributes requests across replicas of the same container app.
- `get_critic_urls()` parses comma-separated critic-supervisor URLs for multi-replica or multi-endpoint failover.
- `applications/Agent_Red/src/multi_tenant/agntcy_directory.py` provides Directory registration, static fallback listing, and `get_agent_topic()` topic resolution, allowing gateway routing to resolve an agent identity rather than hard-code a replica.
- `applications/Agent_Red/src/chat/pipeline/agent_dispatch.py` calls `get_agent_topic()` before creating the A2A client for transport dispatch.

This proposal adds one deterministic pytest file that binds those live surfaces to WI-3204 and the historical SPEC-1800 clauses. It does not authorize source edits. If Loyal Opposition concludes that `SPEC-1800` requires a live ACA multi-replica distribution test, production/staging infrastructure harness, or source-level per-request load-balancing algorithm beyond service-level routing compatibility, this proposal should receive `NO-GO` and be revised with the appropriate broader scope.

## Requirement Sufficiency

Existing requirements are sufficient for a test-only compatibility-boundary backfill.

`SPEC-1800` states the historical behavior: each agent container type supports 2+ replicas, and Azure Container Apps internal load balancer distributes requests across replicas. MemBase currently marks `SPEC-1800` as `retired` under FAB-11 app-scoped history because the old assertion evidence became stale after Agent Red moved under `applications/Agent_Red/`; the open WI remains the active project member asking for deterministic replacement evidence.

`SPEC-1802` and `SPEC-1852` provide the current active routing context: non-streaming agent dispatch uses the SLIM/NATS/HTTP cascade, and agent identity/routing derives from registry/Directory surfaces rather than hard-coded replica identities. No owner clarification is needed as long as this is treated as deterministic compatibility coverage and not a live infrastructure certification.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\agents\test_multi_replica_agent_routing_spec1800.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\chat\pipeline\constants.py`
- `E:\GT-KB\applications\Agent_Red\src\chat\pipeline\agent_dispatch.py`
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\agntcy_directory.py`
- `E:\GT-KB\applications\Agent_Red\tests\agents\plugins\test_agent_extensibility_phase0.py`

## Specification Links

- `SPEC-1800` - Direct historical requirement text and source spec for multi-replica agent routing.
- `SPEC-1802` - Current implemented per-interface transport policy for containerized non-streaming agent dispatch.
- `SPEC-1852` - Current implemented canonical agent identity/registry context used by routing and Directory fallback.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live routing constants, Directory, and dispatch topic-resolution surfaces are the exposed artifacts under test.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3204`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `bridge/por-step16c-stream-d-phantom-wi-creation-007.md` - Inventory table maps `WI-3204` to `SPEC-1800`, delta-prime, title "Multi-Replica Agent Routing".
- `gt deliberations search "SPEC-1800 Multi-Replica Agent Routing WI-3204"` returned no blocking owner decision specific to WI-3204 beyond broad governance/advisory records.
- `gt bridge threads --wi WI-3204 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3204 --json` shows open/backlogged `WI-3204`, source spec `SPEC-1800`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says assertion-only verification was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1800 --json` shows title "Multi-Replica Agent Routing", status `retired`, tags `fab11-app-scoped-history`, and the historical clause text that each agent container type supports 2+ replicas and ACA internal load balancer distributes requests across replicas.
- `applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py` does not currently exist.
- `applications/Agent_Red/src/chat/pipeline/constants.py` builds registry-derived `AGENT_URLS` with ACA internal service DNS when `CONTAINER_APP_ENV_FQDN` is set, and `get_critic_urls()` parses comma-separated URLs.
- `applications/Agent_Red/src/multi_tenant/agntcy_directory.py` resolves/list agents through Directory or static registry fallback and returns transport topics via `get_agent_topic()`.
- `applications/Agent_Red/src/chat/pipeline/agent_dispatch.py` resolves agent topics through `get_agent_topic()` before creating A2A transport clients.
- Existing tests verify generic topology consistency, but there is no named `SPEC-1800`/`WI-3204` deterministic coverage artifact tying service-level routing, multi-endpoint failover parsing, Directory topic resolution, and dispatch topic usage together.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3204-multi-replica-agent-routing-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3204-multi-replica-agent-routing-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py`.
2. In the new pytest, import live `src.chat.pipeline.constants`, `src.multi_tenant.agntcy_directory`, and `AgentDispatchMixin` surfaces.
3. Assert `_build_agent_urls()` derives one service-level ACA internal URL per registry core agent when `CONTAINER_APP_ENV_FQDN` is set, with no replica ordinal embedded in the route.
4. Assert `get_critic_urls()` parses comma-separated critic-supervisor endpoints into an ordered, trimmed failover list while preserving single-URL backward compatibility.
5. Assert Directory static fallback lists all registry core agents when Directory is unavailable.
6. Assert `get_agent_topic()` uses Directory/cache topic metadata when present and falls back to the stable agent id when Directory resolution is unavailable.
7. Assert `_call_via_transport()` resolves an agent topic through `get_agent_topic()` before constructing the A2A client, so dispatch is identity/topic based rather than replica-hard-coded.
8. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1800` | New pytest imports live routing constants, Directory, and dispatch code and asserts service-level ACA internal URLs, comma-separated multi-endpoint failover parsing, Directory/static fallback listing, topic resolution, and dispatch topic use. |
| `SPEC-1802`, `SPEC-1852` | New pytest verifies current active routing context: non-streaming dispatch uses transport topics resolved from canonical agent identity rather than hard-coded replica endpoints. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3204-multi-replica-agent-routing-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py
python -m ruff format --check applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py
```

## Acceptance Criteria

- PASS when the new pytest verifies registry-derived ACA internal service URLs for each core agent under `CONTAINER_APP_ENV_FQDN`.
- PASS when the new pytest verifies those URLs target service-level container-app names rather than replica-specific identities.
- PASS when the new pytest verifies comma-separated critic-supervisor URLs are parsed into a multi-endpoint failover list and single URL behavior remains backward-compatible.
- PASS when the new pytest verifies Directory/static fallback listing covers every registry core agent.
- PASS when the new pytest verifies `get_agent_topic()` honors resolved topic metadata and falls back to stable agent ids.
- PASS when the new pytest verifies dispatch uses Directory-resolved topics before A2A client creation.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is moderate. The proposal adds deterministic routing-compatibility evidence for a retired historical infrastructure spec; it does not prove live Azure Container Apps distribution across two real replicas. If Loyal Opposition requires live infrastructure proof or source changes, return `NO-GO` so Prime Builder can revise with harness or source scope.

Rollback is to delete `applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/agents/test_multi_replica_agent_routing_spec1800.py`

## Recommended Commit Type

`test:`
