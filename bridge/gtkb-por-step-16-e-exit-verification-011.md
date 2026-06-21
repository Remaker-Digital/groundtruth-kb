REVISED
Responds-to: bridge/gtkb-por-step-16-e-exit-verification-010.md

# gtkb-por-step-16-e-exit-verification — POR Step 16.E Exit Verification Remediation Plan

bridge_kind: prime_proposal
Document: gtkb-por-step-16-e-exit-verification
Version: 011
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-21 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: cb447a9a-62e4-4fbe-8f6f-ef77dee8e1d3
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity IDE session

Project Authorization: PAUTH-PROJECT-POR-SPEC-HYGIENE-EXIT-VERIFICATION
Project: PROJECT-POR-SPEC-HYGIENE
Work Item: WORKLIST-POR-STEPS-16-D-16-E-SPEC-HYGIENE-REMEDIATION-16-A-B-C-COMPLETE

target_paths: ["scripts/remediate_por_step_16e.py", "platform_tests/scripts/test_remediate_por_step_16e.py", "scripts/por_step_16_exit_verification.py", "groundtruth.db", "bridge/gtkb-por-step-16-e-exit-verification-manifest-011.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This revised proposal details the remediation plan to satisfy the exit criteria of POR Step 16.E.
Currently, the exit verification gate fails due to 2,189 orphan test records in the database, and 84 implemented/verified specifications without test linkages.

We address the blockers in version 010 by:
1. Promoting the exact 69-adopt / 2,120-retire / 48-waiver / 36-covered-specs manifest to a tracked bridge appendix file at `bridge/gtkb-por-step-16-e-exit-verification-manifest-011.json`.
2. Tracking the approved manifest in `target_paths` and verifying its SHA-256 hash (`c12dff39354a3b4eb117bada2e3237b968b8c946b1879d94fbd7a0293aeffbda`) on execution to ensure auditability.
3. Updating the remediation script `scripts/remediate_por_step_16e.py` to read both the adoptions/retirements and the 36 covered specs test mappings from the tracked manifest file (rather than any local ignored scratch path) and fail closed if the manifest is missing or has a hash mismatch.
4. Updating the exit verifier `scripts/por_step_16_exit_verification.py` to read the waived specs list from the tracked manifest file and exclude them from the untested spec count, allowing the gate to pass.
5. Implementing regression tests in `platform_tests/scripts/test_remediate_por_step_16e.py` verifying dry-run safety, boundary checks, and post-remediation success.

## Approved Manifest — Exact Content Commitment

The exact list of adoptions (69 tests), retirements (2,120 tests), waivers (48 specs), and covered specification mappings (36 specs) is defined in `bridge/gtkb-por-step-16-e-exit-verification-manifest-011.json` with SHA-256 content hash:
```
c12dff39354a3b4eb117bada2e3237b968b8c946b1879d94fbd7a0293aeffbda
```

Approved counts: adopt=69, retire=2120, waived_specs=48, covered_specs=36.

The 48 waived spec IDs:
```json
[
  "ADR-008",
  "ADR-REGISTRY-DISCOVERY-001",
  "ADR-STANDING-BACKLOG-DB-AUTHORITY-001",
  "DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001",
  "DCL-STANDING-BACKLOG-DB-SCHEMA-001",
  "GOV-14",
  "GOV-16",
  "GOV-CD-PRESERVATION",
  "PB-DARK-MODE",
  "SPEC-1653",
  "SPEC-1707",
  "SPEC-1708",
  "SPEC-1709",
  "SPEC-1710",
  "SPEC-1711",
  "SPEC-1712",
  "SPEC-1775",
  "SPEC-1776",
  "SPEC-1777",
  "SPEC-1778",
  "SPEC-1816",
  "SPEC-1818",
  "SPEC-1819",
  "SPEC-1820",
  "SPEC-1821",
  "SPEC-1822",
  "SPEC-1823",
  "SPEC-1824",
  "SPEC-1825",
  "SPEC-1826",
  "SPEC-1827",
  "SPEC-1841",
  "SPEC-1861",
  "SPEC-1862",
  "SPEC-1863",
  "SPEC-1864",
  "SPEC-1865",
  "SPEC-1866",
  "SPEC-1867",
  "SPEC-1868",
  "SPEC-1872",
  "SPEC-1875",
  "SPEC-1878",
  "SPEC-1879",
  "SPEC-1880",
  "SPEC-1881",
  "SPEC-CD-HANDOFF-FORMAT-001",
  "SPEC-GTKB-SCOPE"
]
```

The 36 covered spec IDs that are mapped to existing platform tests in the manifest:
```json
[
  "ADR-0001",
  "ADR-004",
  "ADR-ARTIFACT-FORMALIZATION-GATE-001",
  "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
  "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
  "ADR-STANDING-BACKLOG-AS-WORK-AUTHORITY-001",
  "DCL-001",
  "DCL-003",
  "DCL-ARTIFACT-APPROVAL-HOOK-001",
  "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
  "DCL-SESSION-STARTUP-TOKEN-BUDGET-001",
  "DCL-SESSION-WRAP-UP-AUTOMATION-SAFETY-001",
  "DCL-STANDING-BACKLOG-SCHEMA-001",
  "GOV-15",
  "GOV-19",
  "GOV-20",
  "GOV-ACTING-PRIME-BUILDER-001",
  "GOV-AGENT-RED-GTKB-CONFORMANCE-001",
  "GOV-ARTIFACT-APPROVAL-001",
  "GOV-GTKB-ADOPTION-ENFORCEMENT-001",
  "GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001",
  "GOV-RELEASE-READINESS-GOVERNED-TESTING-001",
  "GOV-REQUIREMENTS-COLLECTION-HOOK-001",
  "GOV-SESSION-FORMALIZATION-AUDIT-001",
  "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001",
  "GOV-SESSION-SELF-INITIALIZATION-001",
  "PB-ARTIFACT-APPROVAL-001",
  "PB-SESSION-STARTUP-GOVERNANCE-DISCLOSURE-001",
  "PB-SESSION-WRAP-UP-PROACTIVE-001",
  "PB-STANDING-BACKLOG-CONTINUITY-001",
  "SPEC-1662",
  "SPEC-1882",
  "SPEC-2098",
  "SPEC-2099",
  "SPEC-2100",
  "SPEC-PROJECT-DASHBOARD-KPI-LINK-001"
]
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The bridge protocol and CLI command execution.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Specification linkage requirements.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Bounded metadata headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification requires tests.
- `GOV-STANDING-BACKLOG-001` — Backlog management.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — Release readiness; orphan tests block readiness.
- `GOV-ARTIFACT-APPROVAL-001` — Bulk-mutation governance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — The in-root application placement isolation boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — Modeling project memory as a durable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — Artifact lifecycle triggers, thresholds, and states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Artifact-oriented governance as the default project interpretation stance.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — State claims derive from fresh canonical reads.

## Prior Deliberations

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` — Batch-5 authorization including this WI.
- `DELIB-0822` — POR 16.D Phase 1 complete.
- `DELIB-0823` — POR 16.D Phase 2 complete.
- `DELIB-2313` — POR 16.D Phase 2 verification.
- `DELIB-20265448` — Version 002 NO-GO review.
- `DELIB-20265451` — Version 004 NO-GO review.
- `DELIB-20265456` — Owner waiver and bulk test deletion approval deliberation.
- `DELIB-20265455` — Version 008 NO-GO review.
- `DELIB-20265456` — Version 010 NO-GO review.

## Owner Decisions / Input

- `DELIB-20265456` — Owner approved: (1) waiving spec-derived test coverage requirements for the 48 specifications listed in the waived_specs section of the manifest; (2) bulk deletion of the 2,120 stale legacy test rows. The exact waived spec IDs and approved counts are now tracked inside `bridge/gtkb-por-step-16-e-exit-verification-manifest-011.json` so the decision content is fully auditable.

## Requirement Sufficiency

Existing requirements sufficient — The work item details specify the exit criteria for Step 16.E: untested-spec count <= 6 and orphan-test count <= 100.

## Spec-Derived Verification Plan

| Behavior | Test | Maps to |
|---|---|---|
| Dry-run mode performs no writes | `test_remediate_dry_run_does_not_mutate` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| Remediation script adopts 69, retires 2,120, and links 36 specs | `test_remediate_apply_lifecycle` | `GOV-ARTIFACT-APPROVAL-001` / `DELIB-20265456` |
| Boundary check fails closed on out-of-manifest orphan tests | `test_remediate_fails_on_unmapped_orphans` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` |
| Exit verification CLI exits 0 post-remediation | `groundtruth-kb/.venv/Scripts/python.exe scripts/por_step_16_exit_verification.py` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` |
| Exit verifier fails closed (exit 2) when waiver manifest absent | `test_exit_verifier_fails_closed_on_missing_manifest` | `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` |
| Exit verifier fails closed (exit 2) when manifest contains malformed JSON | `test_exit_verifier_fails_closed_on_malformed_manifest` | `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` |
| Exit verifier excludes waived specs from untested-spec count | `test_exit_verifier_waived_specs_excluded` | `DELIB-20265456` |
| Remediation script fails closed on manifest content-hash mismatch | `test_remediate_fails_on_hash_mismatch` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` |
| Committed manifest sha256 matches approved hash | Verify in implementation report via `sha256sum bridge/gtkb-por-step-16-e-exit-verification-manifest-011.json` | `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` |

## Pre-Filing Preflight Subsection

### Applicability Preflight

- packet_hash: `sha256:d6200f91b85fb36b66118d7026e538f518aee6b038a6086c4d6c8c7e8a901058`
- bridge_document_name: `gtkb-por-step-16-e-exit-verification`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-por-step-16-e-exit-verification-011.md`
- operative_file: `bridge/gtkb-por-step-16-e-exit-verification-011.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

### Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-por-step-16-e-exit-verification`
- Operative file: `bridge\gtkb-por-step-16-e-exit-verification-011.md`
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


## Risk / Rollback

Risk: Mutating database test records might dirty the test-audit history.
Rollback: A SQLite backup of `groundtruth.db` is captured as `groundtruth.db.pre-remediate.bak` before the mutation. The changes can be rolled back by restoring the database file from `groundtruth.db.pre-remediate.bak`.

## Recommended Commit Type

feat

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
