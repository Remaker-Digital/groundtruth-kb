VERIFIED

# Loyal Opposition Verification - implementation_start_gate Format-Spec Fix

Document: gtkb-impl-start-gate-format-spec-fix
Version: 008
Responds to: bridge/gtkb-impl-start-gate-format-spec-fix-007.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Work Item: WI-3317

## Verdict

VERIFIED.

The WI-3317 implementation report is accepted. The implementation stays within
the `-006` GO scope, carries forward the required specification links, maps the
linked behavior to tests, and the reported verification command passes in the
current worktree. No blocking applicability or ADR/DCL clause gaps remain.

Verified implementation scope:

- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`,
  actionable for Loyal Opposition verification.
- Read the full bridge thread from `-001` through `-007`.
- Reviewed the `-006` GO conditions and the post-implementation report at
  `bridge/gtkb-impl-start-gate-format-spec-fix-007.md`.
- Inspected the current diff for both approved target paths.
- Ran mandatory applicability and ADR/DCL clause preflights against the
  operative `-007` implementation report.
- Searched the Deliberation Archive and inspected the owner-decision record.
- Ran the reported pytest verification command and a targeted Ruff check.

## Prior Deliberations

Commands run:

```text
python -m groundtruth_kb deliberations search "WI-3317 MUTATING_COMMAND_RE Python format spec false positive implementation_start_gate post implementation report" --limit 10
python -m groundtruth_kb deliberations get DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT
```

Relevant result:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` records the owner directive
  establishing the spec -> project -> work item -> bridge enforcement project
  and says `MUTATING_COMMAND_RE format-spec false-positive -> Add as 6th WI`.

No prior deliberation found in this review pass contradicts verifying this
defect fix.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:78379aa1f61ec189b81d14874db50ecae30e3b60393295cf29c69285450c7e8f`
- bridge_document_name: `gtkb-impl-start-gate-format-spec-fix`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-impl-start-gate-format-spec-fix-007.md`
- operative_file: `bridge/gtkb-impl-start-gate-format-spec-fix-007.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The advisory omissions are non-blocking because the preflight passed and no
required specification is missing.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-impl-start-gate-format-spec-fix
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-impl-start-gate-format-spec-fix`
- Operative file: `bridge\gtkb-impl-start-gate-format-spec-fix-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | - | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Result: PASS.

## Implementation Evidence

Observed source/test diff:

- `scripts/implementation_start_gate.py`: `MUTATING_COMMAND_RE` redirect
  alternation changed from `(^|[^>])>{1,2}($|[^&])` to
  `(?<![:>-])>{1,2}(?![&])`.
- `platform_tests/scripts/test_implementation_start_gate.py`: the
  project-authorization fixture now seeds an approved spec and passes
  `included_spec_ids`; the spec-exclusion amendment test writes a
  formal-artifact approval packet for the amendment fixture; new regression
  tests cover Python format-spec right alignment, Python arrow tokens, append
  redirects, and no-space redirects.

Scope check: only the two approved target files changed for this implementation.

## Specification-Derived Verification

Report mapping was present and executable. Relevant coverage:

- Format-spec `:>` not mutating:
  `test_gate_allows_python_format_spec_right_align`
- Arrow `->` not mutating:
  `test_gate_allows_python_arrow_token`
- Redirect true positives preserved:
  `test_gate_blocks_unnumbered_redirect_to_file`,
  `test_gate_blocks_append_redirect_to_file`,
  `test_gate_blocks_stdout_numbered_redirect_to_file`,
  `test_gate_blocks_stderr_numbered_redirect_to_real_file`,
  `test_gate_blocks_combined_redirect_to_file`,
  `test_gate_blocks_no_space_redirect_to_file`
- WI-3312/WI-3313 fixture compliance:
  the four `test_project_authorization_*` tests in
  `platform_tests/scripts/test_implementation_start_gate.py`.

Commands run:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
```

Observed results:

- `40 passed, 1 warning in 4.22s`
- `All checks passed!`

## Findings

No blocking findings.

The implementation report discloses that IP-3 also needed a WI-3313 amendment
fixture fix after the GO-required full-file verification surfaced that gate.
That remains within the already-approved test file, is fixture setup only, and
does not alter the assertions of the project-authorization tests. The `-006`
GO condition allowed fixture setup changes needed to make the full verification
file executable.

## Decision Needed From Owner

None.

File bridge scan: selected WI-3317 entry processed.
