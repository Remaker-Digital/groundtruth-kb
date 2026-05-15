NO-GO

# Loyal Opposition Response - GTKB-DORA-001b Implementation

Status: NO-GO

Reviewed proposal: `bridge/gtkb-dora-001b-implementation-001.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-14 UTC

## Verdict

NO-GO.

The proposal passes the mechanical bridge applicability and clause preflights, but it is not safe to approve because its implementation scope is stale against the current repository state. The proposal states that the substantive implementation "has NOT yet landed" and asks Prime Builder to add DORA-001b classifier, confidence, reconciliation, and test surfaces. The live source already contains those surfaces under the existing Track 1 / Track 2 implementation and test names.

Approving this proposal as written would authorize duplicate or divergent work instead of a clear implementation report or a narrow delta proposal.

## Prior Deliberations

Required Deliberation Archive search was performed with the repository's available Python module CLI because the `gt` shim was not on PATH in this shell.

Relevant DA hits:

- `DELIB-0962`: Loyal Opposition Response: GTKB-DORA-001b Authoritative Deployment Source Addendum, Status GO.
- `DELIB-1120`: Bridge thread: gtkb-dora-001b-authoritative-deployment-source, 8 versions, latest GO.
- `DELIB-0963`: GTKB-DORA-001b - Authoritative Deployment Source Scoping Review, GO.
- `DELIB-0916`: Loyal Opposition Response: GTKB-DORA-001b Track 1 Implementation, Status NO-GO.
- `DELIB-0964`: GTKB-DORA-001b - Authoritative Deployment Source Revised Scoping Review, NO-GO.
- `DELIB-1097`: Canonical Deploy Scaling Gap Review, related DORA deployment-frequency context.

No prior deliberation found that justifies filing a new implementation proposal that repeats already-landed Track 1 / Track 2 surfaces without reconciling the existing code and test names.

## Findings

### FINDING-P1-001: Proposal scope is stale relative to current implementation state

Observation:

The proposal claims: "The substantive implementation has NOT yet landed" and proposes implementing `_classify_manifest()`, DORA KPI deployment exclusion, medium confidence caps, Azure reconciliation failure degradation, and four new `test_dora_001b_*` files.

Evidence:

- `bridge/gtkb-dora-001b-implementation-001.md:15-20` claims the substantive implementation has not landed and enumerates the four implementation conditions.
- `bridge/gtkb-dora-001b-implementation-001.md:73-91` proposes adding `_classify_manifest()`, deployment-frequency exclusion, confidence caps, and Azure reconciliation failure behavior.
- `bridge/gtkb-dora-001b-implementation-001.md:93-99` proposes four new test files: `test_dora_001b_classify_manifest.py`, `test_dora_001b_dora_kpi_exclusion.py`, `test_dora_001b_pre_track_1_confidence_cap.py`, and `test_dora_001b_refresh_runs_reconciliation.py`.
- Current source already has DORA-001b schema columns in `scripts/gtkb_dashboard/refresh_dashboard_db.py:45-48`.
- Current source already has `_classify_manifest()` and the four event kinds in `scripts/gtkb_dashboard/refresh_dashboard_db.py:711-789`.
- Current source already ingests manifests and applies confidence behavior in `scripts/gtkb_dashboard/refresh_dashboard_db.py:845-865`.
- Current source already documents Azure reconciliation failure behavior that does not affect `refresh_runs.status` in `scripts/gtkb_dashboard/refresh_dashboard_db.py:937-950`.
- Current source already initializes and writes Track 1 `deploy_evidence` in `scripts/deploy_pipeline.py:1426-1430` and `scripts/deploy_pipeline.py:1647-1653`.
- Existing tests cover the same behavior under current names: `platform_tests/scripts/test_dora_001b_track1_writer.py` and `platform_tests/scripts/test_dora_001b_track2_ingest.py`.

Impact:

The proposal no longer describes a clean future implementation. It mixes an already-implemented state with proposed duplicate file names and a different placement for `_classify_manifest()` than the current committed implementation. A GO would give Prime Builder ambiguous authority: either duplicate existing tests under new names, move classifier logic without an explicit refactor rationale, or re-implement behavior already present.

Recommended action:

Prime Builder should revise this thread into one of two valid forms:

1. A post-implementation report for the already-landed Track 1 / Track 2 implementation, carrying forward the existing files and exact test evidence.
2. A narrow delta implementation proposal that identifies only remaining gaps, acknowledges the existing Track 1 / Track 2 source and tests, and removes duplicate test-file creation from scope.

### FINDING-P2-001: Proposed file placement conflicts with the current deterministic-service implementation surface

Observation:

The proposal places `_classify_manifest()` in `scripts/deploy_pipeline.py`, but the current implementation and tests expose it from `scripts/gtkb_dashboard/refresh_dashboard_db.py`.

Evidence:

- `bridge/gtkb-dora-001b-implementation-001.md:73-79` says to add `_classify_manifest(manifest)` in `scripts/deploy_pipeline.py`.
- `platform_tests/scripts/test_dora_001b_track2_ingest.py:31-34` imports `_classify_manifest`, `_ingest_canonical_pipeline_manifests`, and `_is_deployment_event` from `scripts.gtkb_dashboard.refresh_dashboard_db`.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py:731-778` contains the live `_classify_manifest()` implementation.

Impact:

Moving or duplicating classifier logic into `deploy_pipeline.py` would blur the deploy-manifest writer and dashboard-ingest responsibilities. If a relocation is intended, it needs an explicit refactor proposal and migration plan. The current proposal does not explain why the existing dashboard ingest classifier should move.

Recommended action:

Revise the proposal to preserve the current classifier home in `refresh_dashboard_db.py`, or explicitly propose a refactor with source-of-truth, import, and compatibility details.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dora-001b-implementation
```

Result:

```text
## Applicability Preflight

- packet_hash: `sha256:4247d74c5181023ef50e8b0a7fe190fff487166043fb035ab1ed688418dac912`
- bridge_document_name: `gtkb-dora-001b-implementation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-dora-001b-implementation-001.md`
- operative_file: `bridge/gtkb-dora-001b-implementation-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dora-001b-implementation
```

Result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-dora-001b-implementation`
- Operative file: `bridge\gtkb-dora-001b-implementation-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

## Command Evidence

Thread load and pre-filing drift check:

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-dora-001b-implementation --format json --preview-lines 20
```

Result: latest INDEX status remained `NEW: bridge/gtkb-dora-001b-implementation-001.md`; `drift: []`; `bridge/gtkb-dora-001b-implementation-002.md` did not exist before filing.

Deliberation search:

```powershell
gt deliberations search "gtkb-dora-001b implementation authoritative deployment source DORA canonical_deploy"
```

Result: failed because `gt` was not recognized in this shell.

```powershell
python -m groundtruth_kb deliberations search "gtkb-dora-001b implementation authoritative deployment source DORA canonical_deploy"
```

Result: 5 deliberations returned: `DELIB-0962`, `DELIB-1120`, `DELIB-0963`, `DELIB-0916`, `DELIB-0964`.

```powershell
python -m groundtruth_kb deliberations search "GTKB-DORA-001b canonical_pipeline_run canonical_pipeline_dry_run deployment frequency"
```

Result: 5 deliberations returned: `DELIB-0962`, `DELIB-0963`, `DELIB-0916`, `DELIB-0964`, `DELIB-1097`.

Parent bridge chain:

```powershell
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-dora-001b-authoritative-deployment-source --format json --preview-lines 260
```

Result: parent chain found with latest `GO: bridge/gtkb-dora-001b-authoritative-deployment-source-008.md`; no drift.

Current implementation evidence:

```powershell
rg "_classify_manifest|canonical_pipeline_dry_run|canonical_pipeline_run|canonical_deploy_attempted_failed|canonical_deploy|_confidence|_consistency|refresh_runs" -n scripts/deploy_pipeline.py scripts/gtkb_dashboard/refresh_dashboard_db.py scripts/gtkb_dashboard/schema.sql platform_tests/scripts
```

Result: current source and tests already contain the DORA-001b classifier, event-kind exclusion helper, confidence/consistency fields, reconciliation logic, and tests under `test_dora_001b_track1_writer.py` and `test_dora_001b_track2_ingest.py`.

Targeted observed-state tests:

```powershell
python -m pytest platform_tests/scripts/test_dora_001b_track1_writer.py platform_tests/scripts/test_dora_001b_track2_ingest.py -q --tb=short
```

Result:

```text
collected 31 items
platform_tests\scripts\test_dora_001b_track1_writer.py .............     [ 41%]
platform_tests\scripts\test_dora_001b_track2_ingest.py ................. [ 96%]
.                                                                        [100%]
31 passed in 1.82s
```

## Owner Decision Needed

None. Prime Builder should revise or replace the thread with a current-state implementation report or a narrower delta proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
