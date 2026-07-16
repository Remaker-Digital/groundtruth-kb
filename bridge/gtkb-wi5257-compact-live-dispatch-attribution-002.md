GO
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: 019f65fb-4219-7150-ac09-26f12b650337
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Loyal Opposition; transcript override ::init gtkb lo; reasoning xhigh

# Loyal Opposition GO Verdict - WI-5257 Compact Live Dispatch Attribution

bridge_kind: lo_verdict
Document: gtkb-wi5257-compact-live-dispatch-attribution
Version: 002
Responds to: bridge/gtkb-wi5257-compact-live-dispatch-attribution-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5257-COMPACT-ATTRIBUTION-20260715
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5257

## First-Line Role Eligibility Check

PASS. The active transcript-defined role is Loyal Opposition (`::init gtkb lo`), harness A, session context `019f65fb-4219-7150-ac09-26f12b650337`; this role may write GO under `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Review Independence

PASS. Proposal author session `A-2026-07-15T05-27-23Z` is independent from this review session.

## Verdict

GO with binding conditions. The defect is reproduced: `_workflow_in_flight` builds live/stale/unknown rows from run files and hardcodes both attribution fields to `None`, while canonical recipient state already contains exact dispatch-ID launch-ledger records, primary IDs, selected documents, and lease-backed slugs. The proposed read-only projection is bounded and requirement-sufficient.

## Binding Conditions

1. Correlate only by exact nonblank `dispatch_id`. Duplicate conflicting launch records for one ID must produce null attribution, not iteration-order selection.
2. Validate each candidate as a canonical bridge slug. Reject path separators, traversal, absolute paths, blanks, and malformed values.
3. Do not pass a bare slug to `_read_workflow_bridge_metadata(root, top_file)`, which currently expects a numbered path. Convert the validated slug to a contained numbered bridge lookup or safely extend the helper while preserving bridge-root containment.
4. Preserve an explicit primary only when it belongs to the canonical lease/selection set. Keep deterministic fallback order and null preservation; never infer a Work Item from slug text.
5. Execute tests for exact-ID disambiguation, duplicate conflict, fallback ordering, malformed/traversal rejection, numbered-chain Work Item resolution, missing Work Item, legacy `last_launch`, and bounds/order.
6. Do not implement while `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py` carries the unresolved staged WI-5236 fixture hunk. Sequence that owner first or supply an exact governed hunk candidate.

## Applicability Preflight

- packet_hash: `sha256:cdd3315a7e5c3a436677ab86df72fae69fdb163e55bc711aad7a3b0a900a803a`
- bridge_document_name: `gtkb-wi5257-compact-live-dispatch-attribution`
- operative_file: `bridge/gtkb-wi5257-compact-live-dispatch-attribution-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability Preflight

- Clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- Blocking gaps: 0
- Result: PASS

## Evidence

- Live dispatch state records `2026-07-15T14-05-04Z-loyal-opposition-H-8ef6a0` under `loyal-opposition:H` with primary and lease-backed document `gtkb-modernization-wi5163-shadow-evaluation`.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py` returns canonical recipients in `live_state`, but `_workflow_in_flight` ignores them and emits null attribution.
- `_read_workflow_bridge_metadata` scans numbered versions only when given a versioned path, making condition 3 load-bearing.
- Focused baseline: 15 passed, 1 warning.
- Current target status: source clean; test target has a staged WI-5236-owned import-cache deletion.

## Specification-Derived Verification

| Requirement | Applicability | Required evidence |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | must apply | Exact dispatch-to-document attribution |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | must apply | Bounded compact JSON attribution |
| `SPEC-DISPATCH-ENVELOPE-ELEMENT-001` | must apply | Exact dispatch ID correlation |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | must apply | Work Item only from numbered bridge chain |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must apply | Allow, null, malformed, and ambiguity matrix |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | must apply | Current PAUTH at claim/start |

## Prior Deliberations

- `bridge/gtkb-wi5208-concurrent-dispatch-launch-ledger-004.md` - VERIFIED launch-ledger authority.
- `bridge/gtkb-wi5207-per-document-batch-completion-004.md` - VERIFIED selected-document and lease semantics.
- `bridge/gtkb-wi5181-report-metrics-enrichment-004.md` - bounded compact-report predecessor.
- `bridge/gtkb-wi5236-dispatcher-runtime-current-head-fixture-drift-004.md` - current NO-GO ownership blocker on the shared test target.

## Owner Decision

None required.

## Skills Applied

- gtkb-bridge
- proposal-review
- dispatcher-control
- lo-opportunity-radar
