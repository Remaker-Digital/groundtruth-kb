GO

# Loyal Opposition Review - implementation_start_gate Format-Spec Fix REVISED-2

Document: gtkb-impl-start-gate-format-spec-fix
Version: 006
Responds to: bridge/gtkb-impl-start-gate-format-spec-fix-005.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Work Item: WI-3317

## Verdict

GO.

The REVISED-2 scope correction is approved. The added IP-3 is limited to the
already-authorized test file `platform_tests/scripts/test_implementation_start_gate.py`
and is necessary to make the GO-required verification command executable after
the now-live WI-3312 spec-linkage gate. The mandatory applicability and clause
preflights pass with no missing required specs and no blocking gaps.

Approved implementation scope remains limited to:

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `REVISED`,
  actionable for Loyal Opposition.
- Read the full bridge thread from `-001` through `-005`.
- Reviewed prior NO-GO `-002`, GO `-004`, and the REVISED-2 delta in `-005`.
- Ran mandatory applicability and ADR/DCL clause preflights against the
  operative `-005` file.
- Searched the Deliberation Archive and inspected the owner-decision record.
- Ran the current targeted verification command as review evidence:
  `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`.

## Prior Deliberations

Commands run:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3317 MUTATING_COMMAND_RE Python format spec false positive implementation_start_gate project authorization helper" --limit 10 --json
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  establishing this project and says `MUTATING_COMMAND_RE format-spec
  false-positive -> Add as 6th WI`.

No prior deliberation found in this pass contradicts the defect fix or the
single-helper test-scope correction.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:2cb24bed2fff2035dd72de00018ac2d177b2c98c1a06d15e599d0d6d07edb355`
- bridge_document_name: `gtkb-impl-start-gate-format-spec-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-format-spec-fix-005.md`
- operative_file: `bridge/gtkb-impl-start-gate-format-spec-fix-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The advisory omissions are non-blocking for GO because no required spec is
missing and the preflight reports `preflight_passed: true`.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-gate-format-spec-fix`
- Operative file: `bridge\gtkb-impl-start-gate-format-spec-fix-005.md`
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

Result: PASS.

## Review Findings

### F1 - REVISED-2 helper scope is justified

Severity: resolved

Evidence:

- `bridge/gtkb-impl-start-gate-format-spec-fix-005.md` adds only IP-3, a fix
  to `_seed_project_authorization()` in
  `platform_tests/scripts/test_implementation_start_gate.py`.
- The target file is already in the approved target scope.
- A fresh review run of
  `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short`
  produced exactly the four failures cited by REVISED-2. All four fail at
  `_seed_project_authorization()` because `db.insert_project_authorization()`
  now raises:
  `Project authorization status='active' requires at least one included_spec_id
  (GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001).`
- The same run reported `36 passed, 4 failed`, so the remaining blocker is the
  helper setup path, not the regex regression matrix.

Result: PASS.

### F2 - The regex repair remains bounded to the prior GO scope

Severity: resolved

Evidence:

- `bridge/gtkb-impl-start-gate-format-spec-fix-005.md` carries forward the
  previously approved redirect alternation and test matrix from `-003`/`-004`.
- Current source inspection shows `MUTATING_COMMAND_RE` uses
  `(?<![:>-])>{1,2}(?![&])`, preserving the redirect true positives approved at
  `-004`.
- Current test inspection shows the false-positive tests for `:>` and `->`,
  plus true-positive tests for `>>` and no-space `cmd>out.txt`, are present in
  `platform_tests/scripts/test_implementation_start_gate.py`.

Result: PASS.

## Implementation Conditions

- Make `_seed_project_authorization()` WI-3312-compliant by inserting an
  approved/verified spec fixture and passing that spec id through
  `included_spec_ids`.
- Do not change the assertion logic in the four project-authorization tests
  except as required by the fixture setup.
- Run and report:
  `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -v`.
- Keep changes scoped to the two approved target paths.

## Decision Needed From Owner

None.

File bridge scan: selected entry 1 of 2 processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
