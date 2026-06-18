GO
author_identity: loyal-opposition/antigravity
author_harness_id: C
author_session_context_id: 0b242940-62bf-4c2d-93b3-9023c8702f24
author_model: Gemini 3.5 Flash
author_model_version: 3.5 Flash (High)
author_model_configuration: Loyal Opposition review

# Verdict for gtkb-bridge-thread-read-cli

bridge_kind: loyal_opposition_verdict
Document: gtkb-bridge-thread-read-cli
Version: 002
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-06-18 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-bridge-thread-read-cli-001.md
parent_bridge_id: gtkb-bridge-thread-read-cli-001

## Applicability Preflight

- packet_hash: `sha256:24b9eb819fe7295b7de71233fcb5f4b2016ccc2b1b3ef5e28814b29666412a5a`
- bridge_document_name: `gtkb-bridge-thread-read-cli`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-bridge-thread-read-cli-001.md`
- operative_file: `bridge/gtkb-bridge-thread-read-cli-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-thread-read-cli`
- Operative file: `bridge\gtkb-bridge-thread-read-cli-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Prior Deliberations

- `bridge/gtkb-bridge-convenience-verbs-008.md` (VERIFIED).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (owner directive on offloading repetitive tasks).

## Review Findings

The proposal to add `gt bridge show` and `gt bridge threads` is sound. It implements the Deterministic Services Principle by replacing manual grep dup-checking with CLI commands. The design is read-only, glob-prefix optimized, and handles the legacy status-tokenless versions correctly.

No findings or risks identified.

## Positive Confirmations

- Confirmed that the design does not route scans through the status-gated routing parser, which prevents dropping legacy tokenless versions.
- Confirmed that the `--wi` parameter is validated and exits `2` on malformed values.

## Required Revisions

None.
