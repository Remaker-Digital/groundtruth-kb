NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef217-7723-7290-a6e2-b70c08e6b471
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop app; approval_policy=never; filesystem=danger-full-access; role=prime-builder
author_metadata_source: explicit Codex runtime metadata plus bridge work-intent claim

# Implementation Proposal - WI-3202 Internal Event Bus Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3202-internal-event-bus-coverage
Version: 001 (NEW)
Date: 2026-06-23 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3202

target_paths: ["applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py"]

## Claim

WI-3202 should be implemented as a narrow test-only backfill for `SPEC-1778`.

Current Agent Red source already contains an internal integration event bus under `applications/Agent_Red/src/integrations/event_bus.py` and an existing general-purpose `test_event_bus.py`. The open work item exists because prior assertion-only coverage was rejected under `DELIB-0712` and `DELIB-0713`; this proposal adds deterministic, spec-mapped coverage with explicit `SPEC-1778` clause assertions without changing runtime code.

This proposal does not authorize source edits, existing-test rewrites, generated artifacts, deployment state, release tagging, formal GT-KB artifact mutation, project membership changes, credentials, or new work items. If the new test exposes a current source gap, including a need for concrete cross-replica pub/sub plumbing beyond the current compatibility surface, Prime Builder should stop and return through the bridge with a revised source-plus-test proposal rather than broadening target paths under this NEW proposal.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1778` directly states the target event-bus behavior: `IntegrationEventBus.on(event_type, handler)`, `emit(event_type, payload)`, fire-and-forget dispatch with error isolation, the required integration event taxonomy, representative handler categories, `_background_tasks` lifecycle, and compatibility with Redis pub/sub for cross-replica broadcasting.

The current source implements a local async event bus with string-valued event types, immutable event payloads, concurrent background task dispatch, per-handler error isolation, metrics, drain support, and sync-context scheduling. The Redis clause can be tested at the current compatibility boundary by verifying string event types and simple payload fields suitable for external publication. If Loyal Opposition concludes that `SPEC-1778` requires a concrete Redis publisher/subscriber adapter rather than compatibility primitives, this proposal should receive `NO-GO` and be revised with source scope.

## In-Root Placement Evidence

The implementation target is under the GT-KB root and Agent Red application subtree:

- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_event_bus_spec1778.py`

Read-only verification surfaces are also in-root:

- `E:\GT-KB\applications\Agent_Red\src\integrations\event_bus.py`
- `E:\GT-KB\applications\Agent_Red\tests\integrations\test_event_bus.py`

## Specification Links

- `SPEC-1778` - Direct historical requirement text and source spec for the internal integration event bus.
- `GOV-10` - Test artifacts must exercise exposed project artifacts; here the live event bus module is the exposed artifact under test.
- `SPEC-1649` - Master test plan/live-interface policy; repository-native pytest evidence must validate live code rather than rely on manual inspection or stale assertion rows.
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

No new owner decision is required. This proposal uses active project authorization `PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`, citing owner decision `DELIB-20265586`, and remains inside snapshot-bound project member `WI-3202`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red test coverage gap project; confirms project-level implementation authorization does not replace bridge proposal review, LO `GO`, implementation-start packets, specification-derived verification, or the ACID-invariant for new project items.
- `DELIB-0712` - POR Step 16.B methodology review classifying assertion-only and stale-evidence coverage gaps for remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected assertion-only verification for normal behavioral requirements, treating delta-prime specs as untested.
- `gt bridge threads --wi WI-3202 --json` returned `match_count: 0` before this proposal, so there is no prior WI-specific bridge chain to revise.
- `gt deliberations search "WI-3202 Integration Framework Internal Event Bus"` returned broad bridge/governance records (`DELIB-2192`, `DELIB-20261512`, `DELIB-2679`, `DELIB-20261604`, `DELIB-2411`) but no WI-3202-specific blocking prior decision.

## Current-State Evidence

- MemBase `SPEC-1778` title: "Integration Framework - Internal Event Bus".
- MemBase `SPEC-1778` description requires `IntegrationEventBus.on(event_type, handler)`, `emit(event_type, payload)`, fire-and-forget error isolation, event types `ticket.created`, `ticket.updated`, `article.created`, `article.updated`, `message.received`, `action.completed`, `integration.connected`, `integration.disconnected`, `sync.completed`, and `sync.failed`, representative handler categories, `_background_tasks` usage, and Redis pub/sub compatibility.
- `gt bridge threads --wi WI-3202 --json` currently returns `match_count: 0`.
- `applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py` does not currently exist.
- `applications/Agent_Red/src/integrations/event_bus.py` declares `IntegrationEventType`, immutable `IntegrationEvent`, `IntegrationEventBus.get_instance/reset`, `on`, `off`, async `emit`, sync-context `emit_sync`, `_run_handler` error isolation, `handler_count`, `total_handlers`, `emit_count`, `error_count`, `pending_tasks`, and `drain`.
- `applications/Agent_Red/tests/integrations/test_event_bus.py` already covers many behaviors, but it is not a WI-3202/SPEC-1778 named mapping file and does not explicitly bind every SPEC-1778 clause into one deterministic coverage artifact.
- A read-only source search found the event bus module documents Redis pub/sub compatibility but does not expose a concrete event-bus Redis adapter. This proposal therefore tests the compatibility primitives available in the current live surface and stops for proposal revision if concrete cross-replica transport is required.

## Pre-Filing Preflight Evidence

Applicability preflight command for this completed draft:

```text
python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3202-internal-event-bus-coverage-001.md --json
```

Observed before filing:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- draft packet hash intentionally omitted from this evidence because inserting the hash changes the content hashed by the preflight; Loyal Opposition should rerun preflight on the operative bridge file.

Clause preflight command for this completed draft:

```text
python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/agent-red-wi3202-internal-event-bus-coverage-001.md
```

Observed before filing:

- clauses evaluated: `5`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Proposed Scope

1. Add `applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py`.
2. In the new pytest, import live `IntegrationEventBus`, `IntegrationEvent`, and `IntegrationEventType` from the event bus module.
3. Assert the exact `SPEC-1778` event taxonomy values for ticket, article, message, action, integration lifecycle, and sync completion/failure events.
4. Assert `on(event_type, handler)` registration, `off(event_type, handler)` removal, event-type handler isolation, handler counts, and total-handler counts.
5. Assert `emit` dispatches matching handlers concurrently through background tasks, returns dispatched handler counts, increments emit count, and drains pending tasks.
6. Assert failing handlers do not block succeeding sibling handlers and increment error count.
7. Assert representative handler categories can be registered and dispatched for AI-pipeline, knowledge-ingestion, analytics, and notification use cases without hard-coded vendor coupling.
8. Assert immutable event payload fields preserve tenant id, integration id, payload, correlation id, timestamp, and string-valued event type data suitable for external pub/sub publication.
9. Assert `emit_sync` schedules emission when a running loop exists and fails closed with zero dispatch when no loop exists.
10. Keep implementation test-only unless the test exposes a current source gap; in that case, stop and revise the bridge proposal rather than expanding target paths.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1778` | New pytest imports live event bus surfaces and asserts API registration/emission behavior, fire-and-forget background task dispatch, error isolation, required event taxonomy, representative handler categories, metrics, drain behavior, sync-context scheduling, and compatibility primitives for external pub/sub publication. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Execute repository-native pytest against the new deterministic event-bus spec-mapping test file, using live in-repository source modules. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation will start only after LO `GO`, work-intent claim, and `scripts/implementation_authorization.py begin --bridge-id agent-red-wi3202-internal-event-bus-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | Run `ruff check` and `ruff format --check` on the new test file. |
| Bridge and artifact-governance specs | Preserve project authorization, project id, WI metadata, target paths, linked specs, implementation-start evidence, and post-implementation report for LO verification. |

Required commands after implementation:

```text
python -m pytest applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py -q --tb=short
python -m ruff check applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py
python -m ruff format --check applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py
```

## Acceptance Criteria

- PASS when the new pytest verifies the complete `SPEC-1778` event taxonomy.
- PASS when the new pytest verifies handler registration, unregistration, counting, and event-type isolation.
- PASS when the new pytest verifies fire-and-forget async emission through background tasks and drain cleanup.
- PASS when the new pytest verifies failing handlers do not block sibling handlers and errors are counted.
- PASS when the new pytest verifies representative handler categories can be registered and receive matching events.
- PASS when the new pytest verifies immutable event payload fields and string-valued event types suitable for external pub/sub publication.
- PASS when the new pytest verifies sync-context scheduling behavior.
- PASS when targeted pytest and ruff commands all pass.
- PASS when no source edits, existing-test rewrites, generated artifacts, deployment state, release tags, formal artifacts, project membership, credentials, or new WIs are changed.

## Risks / Rollback

Risk is moderate-low. The proposal adds one deterministic test module and does not alter runtime behavior. The main risk is the Redis pub/sub compatibility clause: if concrete cross-replica transport is required rather than the current compatibility primitives, this proposal should be revised before implementation.

Rollback is to delete `applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py`. Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/integrations/test_event_bus_spec1778.py`

## Recommended Commit Type

`test:`
