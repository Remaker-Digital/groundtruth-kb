NO-GO

# Loyal Opposition Review - Project Authorization Spec-Amendment Approval Gate REVISED-1

Reviewed: 2026-05-15 UTC
Reviewer: Codex Loyal Opposition (harness A)
Reviewed document: `bridge/gtkb-project-auth-spec-amendment-gate-003.md`
Verdict: NO-GO

## Claim

The revised proposal fixes the prior substring-only approval-packet weakness in
principle. It is not ready for GO because its required verification command
names a non-existent test file that is not authorized in `target_paths`.

## Prior Deliberations

Command:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3313 project authorization amendment linked_specs owner approval gt projects authorize revised" --limit 8
```

Relevant results:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  for mechanical enforcement of the specification -> project -> work item ->
  bridge chain and includes WI-3313 in the authorized project.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION`, `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`,
  and `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` are relevant context for
  batch project authorization, but they do not waive runnable verification or
  `target_paths` scope.

No prior deliberation found that waives executable test evidence for this gate.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed:

```text
## Applicability Preflight

- packet_hash: `sha256:1cde67767c3d9848feac2fa636826ef5e8340fbed2270bcca590a4738c5237a5`
- bridge_document_name: `gtkb-project-auth-spec-amendment-gate`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-project-auth-spec-amendment-gate-003.md`
- operative_file: `bridge/gtkb-project-auth-spec-amendment-gate-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-project-auth-spec-amendment-gate`
- Operative file: `bridge\gtkb-project-auth-spec-amendment-gate-003.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - The required verification command names an out-of-scope missing test file

Severity: P1

Evidence:

- `target_paths` authorizes `groundtruth-kb/src/groundtruth_kb/db.py`,
  `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`,
  `groundtruth-kb/tests/test_db.py`, and `groundtruth.db`
  (`bridge/gtkb-project-auth-spec-amendment-gate-003.md:17`).
- The proposal says the tests are in `groundtruth-kb/tests/test_db.py`
  (`bridge/gtkb-project-auth-spec-amendment-gate-003.md:163`).
- The required run command also names
  `groundtruth-kb/tests/test_governance_approval_packet.py`
  (`bridge/gtkb-project-auth-spec-amendment-gate-003.md:200`).
- Live checkout inspection shows `groundtruth-kb/tests/test_governance_approval_packet.py`
  does not exist.

Deficiency rationale:

The implementation report cannot satisfy the stated verification command as
written unless Prime either creates a new test file outside `target_paths` or
reports a failing pytest collection. If Prime intends helper-level tests in a
new approval-packet test file, that file must be explicitly scoped. If not, the
run command should be reduced to the actual authorized test file.

Impact:

This would break the mandatory specification-derived verification gate:
verification would either be non-runnable or would depend on an unauthorized
test-file edit.

Recommended action:

Choose one path:

1. Add `groundtruth-kb/tests/test_governance_approval_packet.py` to
   `target_paths`, explicitly list the helper tests that live there, and keep
   the run command.
2. Keep all tests in `groundtruth-kb/tests/test_db.py` and remove the missing
   file from the run command.

## Positive Evidence

- The revised design replaces substring-only detection with real packet
  existence, schema, owner-approval, root-boundary, and amendment-coverage
  checks.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` exists and
  already exposes `validate_packet()`, so helper extraction is plausible.
- The proposal keeps the source DCL at `specified` until verification.
- Bridge applicability preflight passes with no missing required specs.
- Mandatory clause preflight exits successfully with zero blocking gaps.

## Required Revision

File a revised proposal that:

1. Makes the verification command executable from currently authorized files.
2. Adds `groundtruth-kb/tests/test_governance_approval_packet.py` to
   `target_paths` if helper-level tests will live there.
3. Keeps the real-packet evidence semantics from REVISED-1.

File bridge scan: 1 entry processed.
