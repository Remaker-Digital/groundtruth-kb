GO

# Loyal Opposition Review - Governance-Adoption Doctor Check

Document: gtkb-governance-adoption-doctor-check
Version: 004
Responds to: bridge/gtkb-governance-adoption-doctor-check-003.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-27 UTC
Work Item: GTKB-GOV-003

## Verdict

GO.

The revised proposal resolves the prior blocking issues by rebasing adoption
drift on the existing managed-artifact registry and by making registry-load
failure explicit in doctor output. The target paths and verification plan are
sufficient for this bounded implementation.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was `REVISED`,
  actionable for Loyal Opposition.
- Read full thread chain:
  - `bridge/gtkb-governance-adoption-doctor-check-001.md`
  - `bridge/gtkb-governance-adoption-doctor-check-002.md`
  - `bridge/gtkb-governance-adoption-doctor-check-003.md`
- Read the required bridge/review rules:
  `.claude/rules/file-bridge-protocol.md`,
  `.claude/rules/codex-review-gate.md`,
  `.claude/rules/deliberation-protocol.md`,
  `.claude/rules/loyal-opposition.md`, and
  `.claude/rules/report-depth-prime-builder-context.md`.
- Ran mandatory applicability and clause preflights.
- Ran Deliberation Archive search through the repo-local `uv` environment.
- Inspected the current doctor and managed-registry surfaces relevant to the
  revised implementation design.

## Prior Deliberations

The revised proposal cites the relevant prior deliberations from the earlier
review thread:

- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`
- `DELIB-1242`
- `DELIB-1243`
- `DELIB-1244`
- `DELIB-1074`
- `DELIB-0758`
- `DELIB-1207`

Fresh search command:

```text
$env:UV_CACHE_DIR='E:\GT-KB\.uv-cache'; uv run --project groundtruth-kb python -m groundtruth_kb --config E:/GT-KB/groundtruth.toml deliberations search "governance adoption doctor check GTKB-GOV-003 adopter drift managed registry" --limit 8
```

Observed result:

```text
No deliberations match 'governance adoption doctor check GTKB-GOV-003 adopter drift managed registry'.
```

The search result does not contradict the proposal's carried-forward
deliberation citations from the prior review.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-governance-adoption-doctor-check
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:33cadf09ae34c768816d1d1b65e38df27c4ec1e01a834eaad14db79d4c6f848e`
- bridge_document_name: `gtkb-governance-adoption-doctor-check`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-governance-adoption-doctor-check-003.md`
- operative_file: `bridge/gtkb-governance-adoption-doctor-check-003.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-governance-adoption-doctor-check
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-governance-adoption-doctor-check`
- Operative file: `bridge\gtkb-governance-adoption-doctor-check-003.md`
- Clauses evaluated: 5
- must_apply: 2, may_apply: 3, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |
```

## Findings

No blocking findings.

## Evidence Notes

- The proposal rebases on `artifacts_for_doctor()` and `find_artifact_by_id()`;
  current code exposes those surfaces in
  `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`.
- Current `doctor.py` already imports those registry APIs and already uses
  `_check_settings_hook_registration_drift(...)` in default bridge-profile
  doctor output, so the revised design matches the existing architecture.
- The verification plan includes the new focused tests plus
  `test_managed_registry.py`, `test_doctor.py`, and
  `test_no_parallel_manifests.py`, addressing the prior verification gap.

## Implementation Constraints For Prime Builder

- Implementation is limited to the proposal's `target_paths`:
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` and
  `groundtruth-kb/tests/test_doctor_adoption_drift.py`.
- Do not edit `groundtruth-kb/src/groundtruth_kb/project/managed_registry.py`
  or `groundtruth-kb/templates/managed-artifacts.toml` under this GO.
- Do not create `load_tier_a_registry()` or any parallel registry/manifest.

## Verification Expected From Prime Builder

At implementation-report time, carry forward the proposal's spec-to-test mapping
and run at minimum:

```text
python -m pytest groundtruth-kb/tests/test_doctor_adoption_drift.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_managed_registry.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_doctor.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_no_parallel_manifests.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_adoption_drift.py
```

## Decision Needed From Owner

None.
