GO

bridge_kind: lo_verdict
Document: gtkb-wi5095-adapter-registry-sha-refresh-in-flow
Version: 004
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-07-09 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-003.md

author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 6147bb18-d9cc-41a7-8702-1ca4a8b977cf
author_model: Gemini 3.5 Flash (High)
author_model_version: 3.5
author_model_configuration: Antigravity harness, Loyal Opposition role

## Verdict: GO

Loyal Opposition grants GO for the REVISED proposal of WI-5095: Make registry `source_sha256` refresh part of the default adapter-regen flow. The revised approach safely restricts the registry update to existing `status = "adapter"` blocks, preventing clobbering of intentional `unsupported` parity dispositions. The proposed verification test is clean and the scope is appropriate.

## Applicability Preflight

- packet_hash: `sha256:fc2d2f95cf4d29ad4181c9cc9d5891e8cbda16b163cdd997806259f0151aa02e`
- bridge_document_name: `gtkb-wi5095-adapter-registry-sha-refresh-in-flow`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-003.md`
- operative_file: `bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-wi5095-adapter-registry-sha-refresh-in-flow`
- Operative file: `bridge\gtkb-wi5095-adapter-registry-sha-refresh-in-flow-003.md`
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

- `DELIB-20260709-WI5095-SYSTEMIC-REFRESH-IN-FLOW` (owner_decision) — selected "Systemic: refresh in the flow" to make registry `source_sha256` refresh part of the default adapter-regen flow.
- `DELIB-20260709-WI5095-REVISED-DESIGN` (owner_decision) — selected "Revise with corrected design" after the `unsupported`-clobber defect was caught in implementation-time review.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — parity contract governing the registry's source_sha256.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Conditions / Required Actions

1. **Scoped Commit discipline:** Because the active worktree remains dirty with other changes, the Prime Builder must use a scoped, hunk-limited commit that includes only the generators, tests, and the genuinely-drifted adapter/registry blocks, without sweeping the entire worktree.

## Owner Action Required

None.

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
