NO-GO

Document: gtkb-fab-19-hygiene-detector-expansion
Version: 002
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-19-hygiene-detector-expansion-001.md

# Loyal Opposition Verdict - FAB-19 Hygiene Detector Expansion

## Verdict

NO-GO. The detector-expansion direction is coherent and the mandatory preflights pass, but the operative proposal claims a formal-artifact approval packet for the governed pattern-registry header revision while omitting the packet artifact from `target_paths`.

This is a target-scope defect, not a rejection of the implementation concept. Revise the proposal to include the concrete approval-packet path, or remove the packet-gated registry-header revision from this bridge scope.

## Same-Session Guard

Not a self-review. The operative proposal was authored by Prime Builder harness B in session `d2f32e6b-5441-45b3-b355-097a2507f5f7`. This verdict is authored by Loyal Opposition harness A.

## Dependency / Future-Work Check

FAB-20 is downstream of FAB-19 because it consumes the expanded hygiene detector as a layer-1 evidence source. That dependency supports reviewing FAB-19 first; it does not require approving an incomplete target envelope.

The skill-health work remains constrained to doctor WARN/advisory behavior. Promotion to a blocking gate remains deferred and is not approved by this verdict.

## Prior Deliberations

- `DELIB-FAB19-REMEDIATION-20260610` records the owner decision for full hygiene-pattern expansion and the determined fix to wire `check_skill_health.py` into doctor WARN.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` records the FABLE project chartering decisions, including Q5's layered repeatability architecture.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports converting recurring investigation classes into deterministic services.

## Applicability Preflight

- packet_hash: `sha256:bedd45b0b1d03ebc76683473cb72eceb238fc29ae6273f740f23f80d5f395836`
- bridge_document_name: `gtkb-fab-19-hygiene-detector-expansion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-19-hygiene-detector-expansion-001.md`
- operative_file: `bridge/gtkb-fab-19-hygiene-detector-expansion-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-fab-19-hygiene-detector-expansion`
- Operative file: `bridge\gtkb-fab-19-hygiene-detector-expansion-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | none | blocking | blocking |

## Findings

### P1 - Missing approval-packet target path for governed registry-header revision

Evidence:

- `bridge/gtkb-fab-19-hygiene-detector-expansion-001.md` declares `target_paths` as only `config/governance/hygiene-sweep-patterns.toml`, `scripts/check_skill_health.py`, `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, and `platform_tests/scripts/**`.
- The same proposal says the hygiene-sweep pattern registry is under a formal-artifact-approval packet for its governed header, that the registry-header revision uses the formal-artifact-approval packet, and that the acceptance evidence includes an approval packet.
- `DELIB-FAB19-REMEDIATION-20260610` says the registry-header revision uses the formal-artifact-approval packet.
- Active `PAUTH-FAB19-20260610` permits `governance_config_pattern_registry_with_packet`, confirming that the packet is part of the authorized mutation envelope.

Impact:

The bridge target envelope would authorize a governed header revision while excluding the artifact that proves that approval. Prime Builder would either need to create or edit a `.groundtruth/formal-artifact-approvals/*.json` packet outside the declared bridge scope, or implement without the packet promised by the proposal, deliberation, and project authorization.

Required revision:

Add the concrete approval-packet path to `target_paths`, for example `.groundtruth/formal-artifact-approvals/<fab-19-hygiene-pattern-registry-packet>.json`, or explicitly remove/defer the registry-header revision that requires the packet. The revision should keep the doctor skill-health check WARN-only and should keep external Agent Red repository mutation and push/deploy out of scope.

## Recommended Revised Scope

Retain:

- `config/governance/hygiene-sweep-patterns.toml`
- `scripts/check_skill_health.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/scripts/**`

Add or explicitly defer:

- `.groundtruth/formal-artifact-approvals/<concrete FAB-19 packet>.json`

## Review Notes

The spec-derived test plan is otherwise directionally sufficient: seeded hygiene-sweep fixtures should prove the formerly excluded directories are scanned for content patterns, and doctor tests should prove skill-health findings are surfaced at WARN rather than FAIL.

## Required Next Step

Prime Builder should file a `REVISED` FAB-19 proposal with the approval-packet target path included, or narrow the proposal so no formal approval packet is needed for the registry-header revision.
