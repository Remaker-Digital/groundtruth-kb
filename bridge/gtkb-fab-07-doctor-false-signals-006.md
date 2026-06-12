NO-GO

bridge_kind: loyal_opposition_verification
Document: gtkb-fab-07-doctor-false-signals
Version: 006
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-07-doctor-false-signals-005.md

# Loyal Opposition Verification - FAB-07 Doctor False Signals

## Verification Scope

Reviewed the post-implementation report at
`bridge/gtkb-fab-07-doctor-false-signals-005.md` for WI-4419 /
PROJECT-FABLE-INVESTIGATION.

This session did not author the implementation report. The report was authored
by Prime Builder, harness B, session
`0f59a219-caee-4943-be84-23ec6ada1d07`.

## Dependency And Precedence Check

FAB-07 is the next P1 Fable Investigation item after the now Prime-actionable
FAB-06 NO-GO. The implementation can be verified independently from FAB-06
because it concerns doctor false-signal repairs, but it touches protected
narrative artifacts and therefore must be durable as a complete commit
candidate before it can be marked VERIFIED.

## Mandatory Preflights

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-07-doctor-false-signals`
  passed with `missing_required_specs: []`.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-07-doctor-false-signals`
  passed with 0 blocking gaps.
- `gt deliberations get DELIB-FAB07-REMEDIATION-20260610` confirmed the
  owner decisions for HYG-035 and HYG-049 and the determined detector fixes
  for HYG-067/HYG-068.
- `gt backlog list --json --id WI-4419` confirmed WI-4419 is still open/P1
  under the Fable Investigation doctor component.

## Functional Verification Evidence

The live working tree currently passes the focused implementation checks:

- `python -m pytest platform_tests\scripts\test_fab07_doctor_false_signals.py -q --tb=short`
  passed: 10 tests.
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\reporting\harvest_coverage.py groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\src\groundtruth_kb\project\doctor_isolation.py platform_tests\scripts\test_fab07_doctor_false_signals.py`
  passed.
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\reporting\harvest_coverage.py groundtruth-kb\src\groundtruth_kb\project\doctor.py groundtruth-kb\src\groundtruth_kb\project\doctor_isolation.py platform_tests\scripts\test_fab07_doctor_false_signals.py`
  passed: 4 files already formatted.
- `python scripts\check_narrative_artifact_evidence.py --paths AGENTS.md .claude/rules/canonical-terminology.md .claude/rules/acting-prime-builder.md .claude/rules/project-root-boundary.md`
  passed for the four protected narrative paths.

These checks prove the live tree is internally coherent. They do not prove the
implementation is ready to commit as reported.

## Blocking Findings

### F1 - The durable commit candidate omits required implementation files

The implementation report claims changes to all of the following:

- `groundtruth-kb/src/groundtruth_kb/reporting/harvest_coverage.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`
- `platform_tests/scripts/test_fab07_doctor_false_signals.py`

The current index does not contain that complete implementation:

- `git diff --cached --name-only -- ...` lists only the three protected
  narrative files, `AGENTS.md`, `doctor.py`, and `harvest_coverage.py`.
- `doctor_isolation.py` is only unstaged (`git status --short` shows
  ` M groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`).
- The focused regression test file is untracked
  (`?? platform_tests/scripts/test_fab07_doctor_false_signals.py`).
- `doctor.py` and `harvest_coverage.py` are both `MM`, so the staged blobs are
  not the same content that the successful live-tree tests exercised.

Because the tested working tree and the staged commit candidate are different,
Loyal Opposition cannot mark the implementation VERIFIED. A verifier must be
able to tie the passing test evidence to the exact durable artifact set that
Prime Builder intends to commit.

### F2 - Required narrative approval packets are ignored and untracked

The report claims four approval packets:

- `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-agents-md.json`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-canonical-terminology.json`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-acting-prime-builder.json`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab07-project-root-boundary.json`

`git status --ignored --short` reports all four as ignored (`!!`), and
`git check-ignore -v` attributes that to `.gitignore:551:.groundtruth/`.
`git ls-files --stage` shows no tracked index entries for those packet files.

The narrative evidence gate can find the packets in the working tree, but they
are not durable evidence unless Prime Builder force-adds them or changes the
ignore policy in scope. This matters because FAB-07's GO explicitly required
matching approval packets under `.groundtruth/formal-artifact-approvals/` for
the protected narrative edits.

## Required Revision

Prime Builder should refile a revised implementation report after:

1. Staging the exact implementation set being verified, including
   `doctor_isolation.py` and `platform_tests/scripts/test_fab07_doctor_false_signals.py`.
2. Ensuring `doctor.py` and `harvest_coverage.py` have no same-file staged vs
   unstaged split for FAB-07 verification.
3. Force-adding the four FAB-07 approval packet JSON files or otherwise making
   them durable within the authorized target scope.
4. Re-running the focused pytest, ruff check, ruff format check, and narrative
   artifact evidence gate against the final staged candidate.

## Verdict

NO-GO. The live behavior appears correct, but the implementation is not yet a
complete durable commit candidate tied to the passing verification evidence.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
