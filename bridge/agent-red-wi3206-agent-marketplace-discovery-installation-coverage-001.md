NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3206 Agent Marketplace Discovery and Installation Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3206-agent-marketplace-discovery-installation-coverage
Version: 001 (NEW)
Date: 2026-06-24 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3206

target_paths: ["applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py"]

## Claim

WI-3206 should be implemented as a narrow test-only backfill for `SPEC-1865` Agent Marketplace Discovery and Installation.

Current Agent Red source already exposes deterministic marketplace control-plane surfaces:

- `applications/Agent_Red/src/multi_tenant/admin_marketplace_api.py` lists marketplace agents through `PluginAgentRegistry.get_peer_agents()`, hides agents above the tenant tier, reports install state from tenant overlays, installs peer agents by creating an enabled overlay plus skill bindings, returns partial binding failure counts when at least one binding succeeds, invalidates caches after successful install/uninstall, and aborts uninstall before overlay deletion when binding cleanup fails.
- `applications/Agent_Red/src/agents/plugins/registry.py` provides canonical agent identity and skill metadata required by marketplace discovery.
- `applications/Agent_Red/src/agents/plugins/bindings.py` and `applications/Agent_Red/src/agents/plugins/overlay.py` provide the cache/resolution surfaces affected by marketplace install/uninstall.
- Existing `applications/Agent_Red/tests/unit/test_admin_marketplace_api.py` covers broad API behavior, but the project WI is still open because MemBase has no deterministic test evidence mapped to `SPEC-1865` / `WI-3206`.

This proposal adds one dedicated pytest file that binds those live surfaces to `WI-3206` and the historical `SPEC-1865` clauses. It does not authorize source edits. If the new tests expose a current source gap, Prime Builder must stop and return through the bridge with a revised proposal rather than expanding target paths.

## Requirement Sufficiency

Existing requirements are sufficient for a test-only coverage backfill.

`SPEC-1865` defines the marketplace behavior: tenant admins browse/evaluate/install curated agent skills without operator intervention; installation creates `AgentSkillBinding` records and provisions required credentials. Its dependency set is explicit: `SPEC-1852` canonical agent identity, `SPEC-1853` stable skill identity, `SPEC-1856` binding model, and `SPEC-1854` per-tenant overlay activation.

The relevant deliberation trail further constrains the test plan:

- `DELIB-0333` requires the marketplace catalog to be peer-only by default and installation to use best-effort cross-collection writes with compensating cleanup where appropriate.
- `DELIB-0337` accepts partial marketplace install success with warnings/counts, identifies cache invalidation after install/uninstall as a blocking runtime-consistency requirement, and records delete-on-uninstall as the simpler current contract.
- `DELIB-0344` verifies the S252 cache-fix closure and identifies explicit install/uninstall cache invalidation regressions as useful follow-up tests.

No owner clarification is needed because the proposal is a deterministic test addition against those accepted constraints.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\unit\test_agent_marketplace_spec1865.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\admin_marketplace_api.py`
- `E:\GT-KB\applications\Agent_Red\src\agents\plugins\registry.py`
- `E:\GT-KB\applications\Agent_Red\src\agents\plugins\bindings.py`
- `E:\GT-KB\applications\Agent_Red\src\agents\plugins\overlay.py`
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_admin_marketplace_api.py`

## Specification Links

- `SPEC-1865` - Direct requirement for self-service marketplace discovery and installation.
- `SPEC-1852` - Marketplace catalog entries depend on canonical agent identity and peer/core/internal agent kind.
- `SPEC-1853` - Marketplace installation binds stable skill IDs and skill modes, not transient tool names.
- `SPEC-1854` - Marketplace installation activates agents through tenant overlays.
- `SPEC-1856` - Marketplace installation creates AgentSkillBinding records and must preserve deny-by-default binding semantics.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live marketplace API, registry, overlay, binding, and cache-invalidation surfaces are the exposed artifacts under test.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3206`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements.
- `DELIB-0333` - S251 advisory review for SPEC-1864/1865/1866; requires peer-only marketplace catalog and best-effort install semantics.
- `DELIB-0337` - S252 advisory review; records partial-success install semantics, cache invalidation blocker, and delete-on-uninstall contract.
- `DELIB-0344` - S252 v3 review; verifies marketplace install/uninstall cache invalidation fixes and identifies explicit regression tests as useful follow-up.
- `gt bridge threads --wi WI-3206 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt backlog show WI-3206 --json` shows open/backlogged `WI-3206`, source spec `SPEC-1865`, project `AGENT-RED-TEST-COVERAGE-GAPS`, and the description says phantom-only evidence was rejected under `DELIB-0712`/`DELIB-0713`.
- `gt spec show SPEC-1865 --json` shows title "Agent Marketplace Discovery and Installation", status `implemented`, scope `agent_extensibility`, and dependencies on `SPEC-1852`, `SPEC-1853`, `SPEC-1856`, and `SPEC-1854`.
- `applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py` does not currently exist.
- `applications/Agent_Red/src/multi_tenant/admin_marketplace_api.py` contains the live marketplace list, install, uninstall, and cache invalidation surfaces.
- `applications/Agent_Red/tests/unit/test_admin_marketplace_api.py` has broad existing unit coverage, but no dedicated `WI-3206`/`SPEC-1865` replacement artifact.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3206-agent-marketplace-discovery-installation-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3206-agent-marketplace-discovery-installation-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py`.
2. In the new pytest, import the live `src.multi_tenant.admin_marketplace_api` functions and response models.
3. Assert marketplace listing uses peer-agent catalog semantics, hides agents above the tenant tier, and marks installed agents from tenant overlays.
4. Assert install creates an enabled tenant overlay plus one binding per registry-declared skill using stable skill IDs and modes.
5. Assert partial binding failure returns created/failed counts without deleting the overlay when at least one skill binding succeeds.
6. Assert successful install and uninstall invoke marketplace cache invalidation for the tenant.
7. Assert uninstall fails closed by preserving the overlay when any binding deletion fails.
8. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1865` | New pytest imports live marketplace API and asserts discovery, install, partial failure, cache invalidation, and uninstall behavior. |
| `SPEC-1852` | New pytest verifies marketplace discovery is peer-catalog based and does not treat core/internal agents as installable marketplace products. |
| `SPEC-1853` | New pytest verifies install writes bindings with stable `skill_id` values and registry-declared skill modes. |
| `SPEC-1854` | New pytest verifies install writes an enabled tenant overlay and uninstall removes it only after binding cleanup succeeds. |
| `SPEC-1856` | New pytest verifies AgentSkillBinding creation/removal behavior, partial failure accounting, and fail-closed uninstall semantics. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3206-agent-marketplace-discovery-installation-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py
python -m ruff format --check applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py
```

## Acceptance Criteria

- PASS when the new pytest verifies marketplace listing is peer-catalog based, tier-gated, and install-state aware.
- PASS when the new pytest verifies install creates an enabled overlay plus stable skill bindings with registry-declared modes.
- PASS when the new pytest verifies partial binding failure returns created/failed counts and preserves successful artifacts when at least one binding succeeds.
- PASS when the new pytest verifies successful install and uninstall invalidate tenant marketplace/routing caches.
- PASS when the new pytest verifies uninstall fails closed by preserving the overlay if any binding deletion fails.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low-to-moderate. The proposal adds deterministic function-level marketplace coverage using mocked repositories and the live marketplace API module; it does not exercise a real Cosmos DB or browser UI. If Loyal Opposition requires HTTP-router or UI-level evidence, return `NO-GO` so Prime Builder can revise with broader target paths.

Rollback is to delete `applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/unit/test_agent_marketplace_spec1865.py`

## Recommended Commit Type

`test:`
