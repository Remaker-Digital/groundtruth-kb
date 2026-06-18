GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 0b242940-62bf-4c2d-93b3-9023c8702f24
author_model: Gemini 3.5 Flash
author_model_version: 3.5 Flash (High)
author_model_configuration: Loyal Opposition review

# Verdict for gtkb-doctor-legacy-root-pattern-catalog-false-positive

bridge_kind: loyal_opposition_verdict
Document: gtkb-doctor-legacy-root-pattern-catalog-false-positive
Version: 002
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-001.md
parent_bridge_id: gtkb-doctor-legacy-root-pattern-catalog-false-positive-001

## Applicability Preflight

- packet_hash: `sha256:b10d9c213c523d5daa13b07e67c81274d53f431e521bf35a9c890d7597dd68ef`
- bridge_document_name: `gtkb-doctor-legacy-root-pattern-catalog-false-positive`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-001.md`
- operative_file: `bridge/gtkb-doctor-legacy-root-pattern-catalog-false-positive-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:* |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-doctor-legacy-root-pattern-catalog-false-positive`
- Operative file: `bridge\gtkb-doctor-legacy-root-pattern-catalog-false-positive-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `DELIB-20260602-GLOSSARY-CLI-SCAN-LEGACY-ROOT-HARD-FAIL` - Owner selected HARD-FAIL doctor behavior for active artifacts treating the legacy root as live.
- `DELIB-20263459` - Hygiene Sweep Scope Regression 2026-06-12.
- `DELIB-20263489` - Loyal Opposition Hygiene Assessment - Advisory Report (2026-06-15).

## Review Findings

The proposal to exempt the hygiene-sweep-patterns.toml detection catalog from the doctor's legacy-root checks is sound. It resolves a false positive where the detection definitions are double-counted as live dependencies, while preserving the hard-fail for genuine live references as defined in `DELIB-20260602`.

No findings or risks identified.

## Positive Confirmations

- Confirmed that the proposed fix whitelists only the patterns config file name `hygiene-sweep-patterns.toml`, keeping other files governed by the hard-fail checks.
- Confirmed that test coverage is included to assert both the whitelist behavior for the catalog and the fail behavior for genuine out-of-root references.

## Required Revisions

None.
