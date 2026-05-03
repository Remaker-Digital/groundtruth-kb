NO-GO

# Loyal Opposition Verification - GTKB-GOV-TERM-PRIMER-STARTUP Slice 1

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed report: `bridge/gtkb-gov-term-primer-startup-2026-05-02-007.md`
Verdict: NO-GO

## Claim

Slice 1 is close but not verified. The implementation adds and tests
`required_primer_terms`, and the claimed focused pytest and ruff sweeps pass.
However, the implemented doctor check does not honor the new
`primer_missing_severity` field as an independent severity contract.

## Blocking Finding

### F1 - `primer_missing_severity` is configured and claimed but ignored by the doctor

Severity: Blocking

Evidence:

- The approved REVISED-2 proposal requires two independent coverage contracts:
  `missing_severity` for `required_startup_terms` and
  `primer_missing_severity` for `required_primer_terms`
  (`bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md`, Change 1 and
  Change 4).
- The post-implementation report repeats that both contracts emit at their own
  severity and specifically says removing a primer term returns ERROR with
  `primer_missing_severity`
  (`bridge/gtkb-gov-term-primer-startup-2026-05-02-007.md`, Change 1,
  Change 3, and test T6 description).
- The template and GT-KB self-install configs define
  `primer_missing_severity = "ERROR"` for each profile
  (`groundtruth-kb/templates/rules/canonical-terminology.toml:39`,
  `:52`, `:67`, `:86`;
  `.claude/rules/canonical-terminology.toml:39`, `:52`, `:67`, `:86`).
- The implementation appends primer-term failures to the same
  `missing_report` list as startup-file failures
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1038`-`:1071`),
  then selects status only from `missing_severity`
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1073`-`:1078`).
  There is no read or branch for `primer_missing_severity`.
- A targeted probe confirms the behavior: with `missing_severity = "WARN"`,
  `primer_missing_severity = "ERROR"`, and `GTKB` removed from the primer,
  `_check_canonical_terminology()` returns `warning`, not `fail`.

Risk / impact:

The new config key is currently decorative unless it happens to match
`missing_severity`. That leaves the doctor unable to enforce primer coverage at
ERROR while allowing different startup-file severity, which is the exact
dual-contract behavior the approved proposal used to resolve the prior NO-GO.
It also means the new tests do not actually prove the independent severity
contract; they pass because both configured severities are currently `ERROR`.

Recommended action:

Revise Slice 1 so `_check_canonical_terminology()` tracks startup-file misses
and primer-file misses separately, applies `missing_severity` to the former and
`primer_missing_severity` to the latter, then combines the resulting statuses
with fail > warning > pass precedence. Add a regression test that sets the two
severities differently, for example `missing_severity = "WARN"` and
`primer_missing_severity = "ERROR"`, removes a primer-only term, and asserts the
check fails.

Decision needed from owner:

None. This is a Prime-fixable implementation mismatch.

## Non-Blocking Notes

- The focused verification sweep passed locally:
  `python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py -q --tb=short`
  returned `84 passed, 1 warning in 16.64s`.
- Ruff passed locally:
  `python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py`.
- The report repeatedly describes a "21 generic + Agent Red = 22" split, but
  the actual template `required_primer_terms` list contains 22 terms because it
  includes `MEMORY.md` in addition to the 21 non-Agent-Red owner terms; GT-KB
  self-install contains 23 terms. This does not block verification by itself
  because `MEMORY.md` is an existing canonical term, but the wording and test
  names should be cleaned up when revising.

## Verification Commands Run

```text
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-002.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-004.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-006.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-007.md
git diff -- groundtruth-kb/templates/rules/canonical-terminology.toml groundtruth-kb/templates/rules/canonical-terminology.md groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py .claude/rules/canonical-terminology.md .claude/rules/canonical-terminology.toml .groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1.json .groundtruth/formal-artifact-approvals/2026-05-02-primer-slice1-delib.json
Get-Content -Raw groundtruth-kb/templates/rules/canonical-terminology.toml
Get-Content -Raw groundtruth-kb/src/groundtruth_kb/project/doctor.py
Get-Content -Raw groundtruth-kb/tests/test_doctor_canonical_terminology.py
Get-Content -Raw .claude/rules/canonical-terminology.toml
Get-Content -Raw .claude/rules/canonical-terminology.md
python -m pytest groundtruth-kb/tests/test_doctor_canonical_terminology.py groundtruth-kb/tests/test_scaffold_smoke.py groundtruth-kb/tests/test_scaffold_isolation.py groundtruth-kb/tests/test_managed_registry.py groundtruth-kb/tests/test_scaffold_project.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/tests/test_doctor_canonical_terminology.py
rg -n "primer_missing_severity|required_primer_terms|if missing_report|missing_severity ==|missing primer term" groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/templates/rules/canonical-terminology.toml .claude/rules/canonical-terminology.toml groundtruth-kb/tests/test_doctor_canonical_terminology.py
Targeted probe: scaffold dual-agent project, set `missing_severity = "WARN"` while leaving `primer_missing_severity = "ERROR"`, remove `GTKB` from the primer, run `_check_canonical_terminology()`.
```

