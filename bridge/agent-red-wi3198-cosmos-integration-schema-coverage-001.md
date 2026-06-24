NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3198 Cosmos Integration Schema Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3198-cosmos-integration-schema-coverage
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3198

target_paths: ["applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py"]

## Claim

WI-3198 can be implemented as a narrow test-only backfill for `SPEC-1773`.

Current `applications/Agent_Red/src/multi_tenant/cosmos_schema.py` already defines the five integration-framework containers required by `SPEC-1773`, includes them in `ALL_COLLECTIONS`, and returns them from `get_collection_configs()` with tenant partition keys. `integration_events` also has the required 30-day TTL. The missing piece is deterministic test evidence that maps those live schema values to the retired historical requirement text and the open coverage-gap work item.

This proposal authorizes only:

- add `applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py`;
- import the live schema module and verify the SPEC-1773 collection constants/configs; and
- assert existing leveraged containers remain present.

This proposal does not authorize schema/source edits, repository rewrites, generated artifacts, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items. If the new test exposes a schema gap, Prime Builder should stop and return through the bridge with a revised proposal rather than silently broadening target paths.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1773` and `WI-3198` together state the testable target: Cosmos DB schema support for the integration framework must include `integration_credentials`, `integration_sync_state`, `integration_events`, `normalized_tickets`, and `normalized_contacts`, with tenant partitioning and 30-day TTL on integration events, while leveraging existing `knowledge_bases`, `conversations`, and `tenants` containers. `WI-3198` exists because previous assertion-only evidence was insufficient per `DELIB-0712` and `DELIB-0713`. No owner clarification is needed to add deterministic tests over the live schema module.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\multi_tenant\test_cosmos_integration_schema_spec1773.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\cosmos_schema.py`

## Specification Links

- `SPEC-1773` - Direct historical requirement text and source spec for Integration Framework Cosmos DB schema extensions.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live `cosmos_schema.py` module is the exposed artifact under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate the schema module rather than rely on manual inspection or stale assertion rows.
- `GOV-12` - Work-item remediation must create test evidence.
- `GOV-13` - Test visibility/phase governance; repository-native pytest mappings are live spec-to-test evidence under the current FAB-11 amendment.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner authorization is required but does not replace bridge review, GO, target paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies the baseline Python lint and formatting checks to the new test file.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority, role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires implementation verification to map linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms Agent Red application artifacts live under `applications/Agent_Red/`.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal uses the existing authorized WI and does not add project scope.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex must use the governed bridge helper path and explicit preflight evidence rather than assuming hook parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence for implementation work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this implementation proposal as a lifecycle artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3198`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3198 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.
- `gt deliberations search "WI-3198 Integration Framework Cosmos DB Schema Extensions"` returned broad Cosmos/project results but no WI-3198-specific blocking prior decision.

## Current-State Evidence

- MemBase `SPEC-1773` title: "Integration Framework - Cosmos DB Schema Extensions".
- MemBase `SPEC-1773` description requires the new containers `integration_credentials`, `integration_sync_state`, `integration_events`, `normalized_tickets`, and `normalized_contacts`, plus existing leveraged containers `knowledge_base`/`knowledge_bases`, `conversations`, and `tenants`.
- `gt bridge threads --wi WI-3198 --json` currently returns `match_count: 0`.
- `applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py` does not currently exist.
- Live schema inspection shows `get_collection_configs()` returns:
  - `integration_credentials`: partition key `/tenant_id`, no TTL, unique key over tenant/integration/secret fields.
  - `integration_sync_state`: partition key `/tenant_id`, no TTL, unique key over tenant/integration fields.
  - `integration_events`: partition key `/tenant_id`, default TTL `2592000` seconds, matching 30 days.
  - `normalized_tickets`: partition key `/tenant_id`, no TTL, unique key over tenant/external/source fields.
  - `normalized_contacts`: partition key `/tenant_id`, no TTL, unique key over tenant/external/source fields.
  - existing leveraged `knowledge_bases`, `conversations`, and `tenants` collections are present.

## Pre-Filing Preflight Evidence

Applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3198-cosmos-integration-schema-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3198-cosmos-integration-schema-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py`.
2. In the new pytest, import `src.multi_tenant.cosmos_schema` and build a lookup from `get_collection_configs()`.
3. Assert the five SPEC-1773 integration collections have exact names, are included in `ALL_COLLECTIONS`, and are returned by `get_collection_configs()`.
4. Assert all five new integration collections use partition key `/tenant_id`.
5. Assert `integration_events` has default TTL equal to `TTL_INTEGRATION_EVENTS` and exactly 30 days in seconds.
6. Assert unique-key coverage for credentials, sync state, normalized tickets, and normalized contacts matches the source requirement's tenant-scoped data model.
7. Assert existing leveraged containers `knowledge_bases`, `conversations`, and `tenants` remain defined in `ALL_COLLECTIONS` and collection configs.
8. Keep implementation test-only unless the test exposes a current schema gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1773` | New pytest imports `cosmos_schema.py` and asserts the required integration containers, tenant partition keys, integration-events 30-day TTL, unique-key constraints, and leveraged existing containers. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic schema test file. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3198-cosmos-integration-schema-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py
python -m ruff format --check applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py
```

## Acceptance Criteria

- PASS when the new pytest verifies all five SPEC-1773 integration containers are defined and included in collection configs.
- PASS when each new integration collection uses partition key `/tenant_id`.
- PASS when `integration_events` is configured with a 30-day TTL.
- PASS when tenant-scoped unique keys are asserted for credentials, sync state, normalized tickets, and normalized contacts.
- PASS when existing leveraged containers `knowledge_bases`, `conversations`, and `tenants` are asserted present.
- PASS when the targeted pytest and ruff commands all pass.
- PASS when no schema/source edits, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is low. The proposal adds one deterministic test module and does not alter runtime behavior or schema provisioning. The main risk is over-constraining schema internals; assertions are limited to the collection names, partitioning, TTL, and unique-key details named by `SPEC-1773`.

Rollback is to delete `applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/multi_tenant/test_cosmos_integration_schema_spec1773.py`

## Recommended Commit Type

`test:`
