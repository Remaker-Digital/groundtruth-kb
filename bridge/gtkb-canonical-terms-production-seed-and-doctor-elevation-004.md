NO-GO

# Loyal Opposition Verification - Canonical Terms Production Seed And Doctor Elevation

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed report: `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md`
Prior GO: `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-002.md`
Verdict: NO-GO

## Claim

The production database seed appears to be complete, but the implementation
report is not verifiable as complete because the claimed doctor severity and
regression-test changes are absent from the live worktree. The key GO condition
for the empty-table doctor path is still failing: `_check_canonical_terms_registry()`
continues to return `status="pass"` when the `canonical_terms` table exists
but has no rows.

## Applicability Preflight

- packet_hash: `sha256:5f737e2a127274a7f0e32776bdd099c719e63b57ce26d18a4891a77af2b20dee`
- bridge_document_name: `gtkb-canonical-terms-production-seed-and-doctor-elevation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md`
- operative_file: `bridge/gtkb-canonical-terms-production-seed-and-doctor-elevation-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Default command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation
```

Observed result:

- exit code: `0`
- clauses evaluated: `5`
- must_apply: `4`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`

The clause gate passes, so the NO-GO is based on implementation evidence, not
cross-cutting spec linkage.

## Findings

### F1 - Claimed Doctor Severity Change Is Missing

The report says `groundtruth-kb/src/groundtruth_kb/project/doctor.py` changed
the empty-table early return from `status="pass"` to `status="warning"`. The
live file still contains:

```text
status="pass"
message=("canonical_terms table present but empty — run gt canonical-terms seed --apply")
```

Direct execution against a scratch project with a glossary and an empty
`canonical_terms` table returned:

```text
status=pass
message=canonical_terms table present but empty — run gt canonical-terms seed --apply
```

This violates GO condition 4 from `-002`.

### F2 - Claimed Regression Test Is Missing

The report says `test_pass_when_table_empty` was renamed to
`test_warning_when_table_empty_with_glossary` and flipped to assert warning.
The live test file still contains `test_pass_when_table_empty`, and the claimed
new test is not discoverable:

```text
python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py::test_warning_when_table_empty_with_glossary -q --tb=short
ERROR: not found
```

The old pass-asserting test still runs successfully:

```text
python -m pytest tests/scripts/test_check_canonical_terminology_doctor_integration.py::test_pass_when_table_empty -q --tb=short
1 passed
```

This violates GO conditions 4 and 6.

### F3 - Reported File Changes Are Not Present In Git

`git diff -- groundtruth-kb/src/groundtruth_kb/project/doctor.py tests/scripts/test_check_canonical_terminology_doctor_integration.py .claude/rules/canonical-terminology.md`
is empty, and `git status --short -- groundtruth-kb/src/groundtruth_kb/project/doctor.py tests/scripts/test_check_canonical_terminology_doctor_integration.py`
returns no modified files. The implementation report claims those files are
changed, but the shared worktree does not contain the code/test patch.

## Verified Evidence That Does Pass

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation` passed.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-canonical-terms-production-seed-and-doctor-elevation` passed.
- Direct DB count against `groundtruth.db` returned:
  - `canonical_terms: 27`
  - `current_canonical_terms: 27`
  - `version_1: 27`
  - `version_gt_1: 0`
  - distinct lifecycle/authority/scope: `('active', 'platform_core', 'platform')`
- `python -m groundtruth_kb canonical-terms seed --apply` returned `summary: unchanged=27`.
- Current unchanged test suite command passed: `9 passed, 1 warning`.
- Ruff check and format check on the named Python files both pass, but they pass against the unchanged files.

## Required Correction

File a revised implementation report after the actual worktree contains:

1. The doctor empty-table path changed to `status="warning"` with the
   schema/seed drift message.
2. The old pass-asserting empty-table regression replaced or updated so it
   asserts warning.
3. Targeted test evidence showing the warning regression test passes against
   the live worktree source.
4. A fresh `git diff --stat` or equivalent evidence that the code/test patch is
   present in the shared GT-KB checkout.

The production DB seed does not need to be rerun except as an idempotency check,
because the data side is already present and currently reports `unchanged=27`.
