GO

# Loyal Opposition Review - implementation_start_gate Format-Spec Fix REVISED-1

Document: gtkb-impl-start-gate-format-spec-fix
Version: 004
Responds to: bridge/gtkb-impl-start-gate-format-spec-fix-003.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Work Item: WI-3317

## Verdict

GO.

The revised proposal resolves the blocking finding from
`bridge/gtkb-impl-start-gate-format-spec-fix-002.md`: the proposed redirect
regex no longer requires whitespace before `>`, so it preserves the real-file
redirect true positives for `>`, `>>`, `1>`, `2>`, `&>`, and no-space
`cmd>file`. The stale top-level test path is also removed. The mandatory
applicability and clause preflights both pass.

Approved implementation scope is limited to:

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `REVISED`, actionable for Loyal Opposition.
- Read the full bridge thread from `-001` through `-003`.
- Reviewed each NO-GO finding in `bridge/gtkb-impl-start-gate-format-spec-fix-002.md`.
- Ran mandatory applicability and ADR/DCL clause preflights against the operative `-003` file.
- Searched the Deliberation Archive and inspected the owner-decision record.
- Inspected the current `MUTATING_COMMAND_RE` and existing redirect tests.
- Evaluated the proposed regex behavior against the previously blocking true-positive redirect cases.

## Prior Deliberations

Commands run:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3317 MUTATING_COMMAND_RE Python format spec false positive implementation_start_gate Add as 6th WI" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT --json
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive and the AUQ answer: `MUTATING_COMMAND_RE format-spec false-positive -> Add as 6th WI`.

No prior deliberation was found that contradicts this defect fix.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:614b84481a51f9ba7201fa648c5b6c5221d72064134a54eb94239e5c33105340`
- bridge_document_name: `gtkb-impl-start-gate-format-spec-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-format-spec-fix-003.md`
- operative_file: `bridge/gtkb-impl-start-gate-format-spec-fix-003.md`
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
- Operative file: `bridge\gtkb-impl-start-gate-format-spec-fix-003.md`
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

### F1 - Redirect true positives are preserved

Severity: resolved

Evidence:

- Current `MUTATING_COMMAND_RE` is at `scripts/implementation_start_gate.py:62-68`.
- Existing platform tests assert real-file redirects are mutating at `platform_tests/scripts/test_implementation_start_gate.py:463-476`.
- `bridge/gtkb-impl-start-gate-format-spec-fix-003.md` changes the proposed redirect alternation to `(?<![:>-])>{1,2}(?![&])`.
- This design does not require whitespace or beginning-of-line before `>`, so it preserves the true-positive forms that blocked `-001`: `>`, `>>`, `1>`, `2>`, `&>`, and `cmd>file`.

Result: PASS.

### F2 - Stale test path is removed

Severity: resolved

Evidence:

- `bridge/gtkb-impl-start-gate-format-spec-fix-003.md` limits `target_paths` to `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`.
- The verification command now uses only the existing platform test file.

Result: PASS.

## Non-Blocking Implementation Note

The proposed regex excludes `:>`, `->`, and mid-`>` runs, but common Python
format specs with an explicit fill character before right alignment, such as
`:0>2` or `:*>10`, would still match because the character before `>` is not
`:`. This is not blocking for this GO because the original observed defect and
the revised acceptance table focus on `:>`, `:<`, `:^`, arrows, and redirect
preservation. Prime should consider adding fill-character alignment regression
cases while editing the same test file, or explicitly explain in the
implementation report why those are out of scope.

## Implementation Conditions

- Preserve all existing redirect true-positive tests.
- Add the new false-positive tests listed in `-003`.
- Run and report: `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -v`.
- Keep the change scoped to the two approved target paths.

## Decision

GO.
