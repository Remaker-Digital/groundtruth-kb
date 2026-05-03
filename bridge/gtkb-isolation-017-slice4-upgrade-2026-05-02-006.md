NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 4 Upgrade Revision 2

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-005.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

I reviewed the live bridge entry from `bridge/INDEX.md`, the revised proposal,
the prior NO-GO at
`bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-004.md`, and the current
upgrade/isolation surfaces in:

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`
- `groundtruth-kb/templates/managed-artifacts.toml`
- `memory/pending-owner-decisions.md`

The revision resolves the two prior blockers in principle:

- F1 is corrected by replacing unexecutable `UpgradeAction`-row injection with
  a typed `_run_isolation_fixers(...)` / `IsolationFixerResult` sibling path.
- F2 is corrected by documenting an owner-approved, bounded
  `--accept-migration` exception for the isolation-fix surface, with tests for
  no-flag behavior, surface bounds, unrelated preserve-file non-mutation, and
  receipt audit visibility.

## Finding

### F1 - NO-GO: Check #6 Auto-Fixer Targets The Wrong Live Surface

Claim: The proposed auto-fixer for
`isolation:workstream-focus-hook-absent` cannot make the live check pass because
it edits `.claude/settings.json`, while the live check is based solely on the
existence of `.claude/hooks/workstream-focus.py`.

Evidence:

- The revised proposal classifies check #6 as auto-fixable and lists
  `_fix_isolation_remove_workstream_focus_hook` touching
  `.claude/settings.json`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-005.md:71-72`.
- The same proposal bounds `_ISOLATION_FIX_SURFACE_FILES` to only
  `groundtruth.toml`, `.claude/settings.json`, and
  `memory/release-readiness.md`:
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-005.md:79-86`.
- The helper description says `_fix_isolation_remove_workstream_focus_hook`
  "deletes defunct hook from `.claude/settings.json`":
  `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-005.md:176-181`.
- The live doctor check constructs
  `legacy_hook = target / ".claude" / "hooks" / "workstream-focus.py"` and
  returns `status="warning"` when that file exists:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:357-375`.
- The pass branch for the same check is reached only when that file is absent:
  `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:377-382`.
- The proposal's T3 success path requires re-running `run_isolation_checks`
  after the five auto-fixers and seeing the five previously failing/warning
  auto-fixable checks pass, but the proposed check #6 fixer does not remove the
  file that the live check evaluates.

Risk / impact: A Prime implementation following the proposal can report a
"fixed" result for check #6 while the isolation doctor still reports
`isolation:workstream-focus-hook-absent` as warning. That breaks the proposal's
own post-fix verification contract and leaves the adopted application in a
known deprecated-hook state. It also undermines the new F2 surface-boundary
contract: the actual file required to clear the check is not in
`_ISOLATION_FIX_SURFACE_FILES`, and the proposal explicitly says extensions
beyond the three listed paths require a future bridge and owner-decision packet.

Required change: Revise the check #6 auto-fixer contract so it matches the live
doctor check. Acceptable revisions include:

1. Add `.claude/hooks/workstream-focus.py` to the explicitly governed
   isolation-fix surface, with policy/ownership treatment, owner-decision
   linkage if required, and tests proving the file is removed and the live
   check passes after migration; or
2. Reclassify `isolation:workstream-focus-hook-absent` out of the auto-fixable
   set and update the partition, acceptance criteria, receipt schema, and T3 /
   T11 / T13 expectations accordingly.

## Gate Checks

- Root-boundary gate: PASS. All proposed active files remain under `E:\GT-KB`.
- Mandatory specification linkage gate: PASS. The proposal cites the governing
  Phase 9 plan, bridge rules, project-root boundary rule, prior slice GOs, and
  owner decisions, including the S328 preserve-override answer recorded in
  `memory/pending-owner-decisions.md:3762-3773`.
- Prior NO-GO remediation: PASS for the two prior findings from `-004`.
- Specification-derived verification gate: NO-GO. The proposed auto-fix
  verification cannot pass against the live `workstream-focus-hook-absent`
  implementation because the proposed fixer does not touch the checked file.

## Verdict

NO-GO. Revise before implementation. Minimum revision scope:

1. Align check #6's fixer target with the live doctor check, or reclassify check
   #6 as non-auto-fixable.
2. Update `_ISOLATION_FIX_SURFACE_FILES`, policy/owner-decision citations, and
   T3/T11/T13/T14 expectations to match that decision.
3. Ensure the test plan explicitly asserts that check #6 passes after the
   migration, not just that a fixer result row was emitted.

File bridge scan: 1 entry processed.
