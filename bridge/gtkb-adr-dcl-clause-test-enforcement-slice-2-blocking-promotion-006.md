NO-GO

# Loyal Opposition Verification - ADR/DCL Clause-Test Enforcement Slice 2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed implementation report: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-005.md`
Verdict: NO-GO

## Claim

Most Slice 2 implementation evidence passes, but the mandatory clause-test
gate currently fails open when it cannot locate an operative bridge file. A
mandatory GO/VERIFIED gate must not return success for "not found" or
"cannot evaluate" states.

## Applicability Preflight

- packet_hash: `sha256:3c2dd7cf27f058f341ac4c1208d73dfc0813766339d347aedd156ddce79403ca`
- bridge_document_name: `gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-005.md`
- operative_file: `bridge/gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion
```

Observed result:

- exit code: `0`
- clauses evaluated: `5`
- must_apply: `4`
- may_apply: `1`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`

The operative implementation report itself passes the new gate. The defect
below is in the gate's error-path semantics.

## Evidence Checked

- `python -m pytest tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short` passed: 12 tests.
- `python -m ruff check scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py` passed.
- `python -m ruff format --check scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py` passed.
- `python -m ruff check scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py .claude/rules/file-bridge-protocol.md .claude/rules/codex-review-gate.md config/governance/adr-dcl-clauses.toml` passed.
- `python -m groundtruth_kb secrets scan --paths scripts/adr_dcl_clause_preflight.py tests/scripts/test_adr_dcl_clause_preflight.py config/governance/adr-dcl-clauses.toml .claude/rules/file-bridge-protocol.md .claude/rules/codex-review-gate.md --json --fail-on=` reported `finding_count: 0`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id definitely-not-a-real-bridge-id` printed `Operative file: (not found ...)` and `Mode: cannot evaluate without an operative file; gate neither passes nor fails.`, but exited `0`.

## Findings

### F1 - Required revision: mandatory gate fails open when no operative file is found

The Slice 2 CLI returns success when it cannot locate the bridge file to
evaluate. The implementation has `blocking_gaps_count = 0`, renders a "not
found" report, and reaches `return EXIT_BLOCKING_GAP if blocking_gaps_count > 0
else 0`. The observed command confirms the behavior: a nonexistent bridge id
prints "cannot evaluate" but returns `EXIT:0`.

Evidence:

- Missing-file branch emits "Operative file: (not found ...)" and "gate neither
  passes nor fails": `scripts/adr_dcl_clause_preflight.py:374` through
  `scripts/adr_dcl_clause_preflight.py:386`.
- Final return converts zero blocking gaps into exit 0:
  `scripts/adr_dcl_clause_preflight.py:423`.
- There is no focused regression test covering the missing-operative-file or
  missing-index path in `tests/scripts/test_adr_dcl_clause_preflight.py`.

Risk: a typo, stale index, or unindexed bridge id can make the mandatory
clause-test gate appear successful even though no bridge content was evaluated.
That is incompatible with the new rule text that makes this a mandatory
GO/VERIFIED gate.

Required action: make no-operative-file / cannot-evaluate states fail closed
with a nonzero exit code, and add a regression test proving the behavior. A
distinct exit code is acceptable, but exit 5 is also acceptable if the project
wants one blocking-gate failure code. The report text can still say "cannot
evaluate," but the process exit must not be 0.

## Non-Blocking Notes

- The implementation report's grep-style count evidence is not reproducible in
  this PowerShell harness because `grep` is not installed. The substantive TOML
  state is still clear from direct inspection: all five clause entries are
  `enforcement_mode = "blocking"` and no `advisory_only_in_slice_1` text remains.
- The focused Python tests, ruff checks, mandatory preflight on this bridge
  thread, report-only banner behavior, and secrets scan otherwise pass.

## Required Revision Summary

1. Fail closed when the CLI cannot locate an operative bridge file.
2. Add focused regression coverage for the missing-operative-file path.
3. Re-run the Slice 2 focused test suite, ruff checks, mandatory self-check,
   report-only check, applicability preflight, and secrets scan.

File bridge scan: 1 entry processed.

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
