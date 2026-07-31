NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; default Codex desktop execution
author_metadata_source: codex-explicit-runtime-envelope

# Implementation Proposal - DORA four-keys panels

bridge_kind: prime_proposal
Document: gtkb-dora-002-four-keys-panels
Version: 001
Date: 2026-07-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-DASHBOARD-OBSERVABILITY
Work Item: GTKB-DORA-002

target_paths: ["scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_dora_four_keys_panels.py", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement the DORA four-keys dashboard consumer now that `GTKB-DORA-001` is VERIFIED. The dashboard should expose deployment frequency, lead time for changes, change failure rate, and MTTR with null/annotation behavior when telemetry is insufficient.

## Requirement Sufficiency

Existing requirements are sufficient. The work item states the four panel outcomes and regression visibility, and active dashboard-observability PAUTH covers `GTKB-DORA-002`. `GTKB-DORA-001` is recorded as VERIFIED in the backlog dependency metadata.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded PAUTH-backed implementation.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms PAUTH does not bypass GO or implementation-start gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves bridge-governed implementation flow.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project linkage metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete spec links in the proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived test evidence before VERIFIED.
- `GOV-SESSION-SELF-INITIALIZATION-001` - dashboard/startup surfaces must remain truthful summaries, not fabricated telemetry.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - dashboard evidence and test outputs are governed artifacts.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - earlier dashboard observability batch approval.
- `DELIB-20265586` - snapshot-bound dashboard-observability implementation authorization.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DASHBOARD-OBSERVABILITY-DASHBOARD-OBSERVABILITY-BOUNDED-IMPLEMENTATION-2026-06-23` - active authorization covering `GTKB-DORA-002`.

## Proposed Scope

- Extend the dashboard refresh/query layer with four-keys metric rows derived from the verified telemetry foundation.
- Add Grafana/stat-panel generation for deployment frequency, lead time, change failure rate, and MTTR.
- Preserve nulls and annotations when fixture or live telemetry is insufficient.
- Add pinned Grafana/dashboard tests and seeded fixture-refresh tests for the expected query shape.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Confirm implementation report cites the active DORA PAUTH and target paths. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Confirm no protected mutation occurs before GO and implementation-start. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm live bridge lifecycle state before implementation and after report filing. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run live applicability preflight and confirm no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Include exact dashboard/Grafana test commands in the implementation report. |
| `GOV-SESSION-SELF-INITIALIZATION-001` | Tests confirm missing telemetry renders null/annotated values instead of fabricated metrics. |

## Acceptance Criteria

- Four stat panels exist for deployment frequency, lead time, change failure rate, and MTTR.
- Seeded dashboard refresh tests verify each query returns the expected shape.
- Grafana JSON tests pin the four panel titles and data sources.
- Insufficient telemetry displays null/annotated states, not fabricated values.

## Risks / Rollback

Risk is moderate because dashboard metrics can be mistaken for authoritative telemetry. Mitigation is null/annotation behavior plus pinned tests. Rollback is a revert of dashboard generator, refresh, tests, and generated dashboard JSON.

## Files Expected To Change

- `scripts/gtkb_dashboard/refresh_dashboard_db.py`
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py`
- `platform_tests/scripts/test_gtkb_dashboard_grafana.py`
- `platform_tests/scripts/test_dora_four_keys_panels.py`
- `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json`

## Recommended Commit Type

`feat`
