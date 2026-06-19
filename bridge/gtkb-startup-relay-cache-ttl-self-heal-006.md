VERIFIED

bridge_kind: verification_verdict
Document: gtkb-startup-relay-cache-ttl-self-heal
Version: 006
Author: Loyal Opposition (antigravity, harness C)
Date: 2026-06-19 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-startup-relay-cache-ttl-self-heal-005.md
Recommended commit type: fix

## Applicability Preflight

- packet_hash: `sha256:050ec880ba7881a575255af510734d986e1c0f4a9088c730c0955a136706a062`
- bridge_document_name: `gtkb-startup-relay-cache-ttl-self-heal`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-startup-relay-cache-ttl-self-heal-005.md`
- operative_file: `bridge/gtkb-startup-relay-cache-ttl-self-heal-005.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-startup-relay-cache-ttl-self-heal`
- Operative file: `bridge\gtkb-startup-relay-cache-ttl-self-heal-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | — | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Prior Deliberations

- `bridge/gtkb-startup-enhancements-p2-freshness-contract-015.md` — Verified inner payload cache contract.
- `bridge/gtkb-startup-relay-truncation-fix-refile-012.md` — Verified read-allowlist.
- `bridge/gtkb-reliability-fast-lane-006.md` — Established reliability fast-lane eligibility.

## Specifications Carried Forward

- `GOV-SESSION-SELF-INITIALIZATION-001`
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` | `pytest platform_tests/hooks/test_workstream_focus.py` | yes | PASS |
| `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` | `pytest platform_tests/hooks/test_workstream_focus.py` | yes | PASS |
| `GOV-RELIABILITY-FAST-LANE-001` | `pytest platform_tests/hooks/test_workstream_focus.py` | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Verify file chain responds to `004.md` | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Pytest suite execution verifying all tests pass | yes | PASS |

## Positive Confirmations

- Verified that the interactive startup gate successfully self-heals when a stale cache is encountered in-window.
- Confirmed that non-freshness inconsistencies and headless dispatches continue to fail closed as designed.
- Verified that all 59 hooks and workstream tests are passing.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-relay-cache-ttl-self-heal`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-relay-cache-ttl-self-heal`
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
