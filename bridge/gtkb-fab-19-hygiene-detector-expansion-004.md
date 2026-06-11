GO

Document: gtkb-fab-19-hygiene-detector-expansion
Version: 004
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-19-hygiene-detector-expansion-003.md

# Loyal Opposition Verdict - FAB-19 Hygiene Detector Expansion

## Verdict

GO. The `-003` revision fixes the prior target-envelope defect by adding the concrete formal-artifact approval packet path for the governed hygiene-sweep registry header:

- `.groundtruth/formal-artifact-approvals/fab-19-hygiene-sweep-patterns-registry-header.json`

The revised scope remains bounded to the deterministic detector expansion, the skill-health doctor WARN, the approval evidence artifact, and tests. It does not approve a blocking skill-health gate, Agent Red repository mutation, deploy, or push.

## Same-Session Guard

Not a self-review. The operative `REVISED` proposal was authored by Prime Builder harness B in session `e45ccf07-99f6-4ad6-b572-570a76a264a2`. This verdict is authored by Loyal Opposition harness A.

## Dependency / Future-Work Check

FAB-19 is the predecessor for FAB-20's hygiene-investigation skill and future delta-mode evidence-pack path. Reviewing FAB-19 first is the correct precedence. FAB-20 should still avoid depending on an implemented evidence-pack contract until FAB-19 implementation reports a concrete output contract and path.

## Prior Deliberations

- `DELIB-FAB19-REMEDIATION-20260610` records the owner decision for full hygiene-pattern expansion and the determined fix to wire `check_skill_health.py` into doctor WARN.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` records the FABLE project chartering decisions, including Q5's layered repeatability architecture.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports converting recurring investigation classes into deterministic services.

## Applicability Preflight

- packet_hash: `sha256:98dfe650536cb1499b8066c58fc55e133435abc332d52bc9bdbe36046abdcb18`
- bridge_document_name: `gtkb-fab-19-hygiene-detector-expansion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-fab-19-hygiene-detector-expansion-003.md`
- operative_file: `bridge/gtkb-fab-19-hygiene-detector-expansion-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-fab-19-hygiene-detector-expansion`
- Operative file: `bridge\gtkb-fab-19-hygiene-detector-expansion-003.md`
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

No blocking findings.

Implementation constraints:

- Keep `check_skill_health.py` surfaced as doctor WARN/advisory only.
- Keep the registry-header formal-artifact approval packet at the targeted path and include it in the implementation report evidence.
- Keep FAB-20 delta-mode and evidence-pack consumer contracts out of this implementation unless separately approved.

## Opportunity Radar

- Token-savings cue: this work converts recurring hygiene-investigation classes into reusable deterministic detector output.
- Deterministic-service cue: the strongest implementation shape is a stable, testable hygiene-sweep evidence surface that later FAB-20 code can consume.
- Recommended surface: expose the detector output through the existing hygiene sweep/doctor surfaces before teaching a skill to consume it.
- Residual human judgment: Loyal Opposition still needs to review whether newly detected drift classes are correctly routed and not overbroad false positives.

## Required Next Step

Prime Builder may implement FAB-19 within the `-003` target envelope and the constraints above, then file a post-implementation report with spec-derived test evidence.
