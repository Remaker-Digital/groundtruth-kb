NO-GO

bridge_kind: loyal_opposition_verification
Document: gtkb-fab-13-retention-policy-umbrella
Version: 008
Author: loyal-opposition (Codex, harness A)
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-13-retention-policy-umbrella-007.md

# Loyal Opposition Verification - FAB-13 Retention Policy Umbrella

## Verification Scope

Reviewed the implementation report at
`bridge/gtkb-fab-13-retention-policy-umbrella-007.md` for WI-4425 /
PROJECT-FABLE-INVESTIGATION.

This session did not author the implementation report. The report records
`author_session_context_id:
019ebc0a-181f-7791-a64b-482f97486014`, which is not this Loyal Opposition
session context.

## Dependency And Precedence Check

FAB-13 precedes FAB-14 in PROJECT-FABLE-INVESTIGATION ordering. I reviewed
FAB-13 before the currently actionable FAB-14 report because the Fable backlog
order records WI-4425 as FAB-13 and WI-4426 as FAB-14. No future dependency
justified taking FAB-14 first.

## Authority Check

- `gt deliberations get DELIB-FAB13-REMEDIATION-20260610` confirmed the owner
  decisions for HYG-021, HYG-055, and HYG-056.
- `gt projects authorizations PROJECT-FABLE-INVESTIGATION --json` confirmed
  `PAUTH-FAB13-20260610` is active.
- The authorization covers hook/source edits, additive governance config,
  owner-approved runtime evidence pruning, DA harvest for resolved decisions,
  Drive ignore coverage extension, and test additions. It forbids push/deploy,
  owner Drive sync infrastructure changes, canonical spec/DA hard deletes, and
  external Agent Red repository changes.

## Mandatory Preflights

- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella`
  passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella`
  passed with 2 must-apply clauses, 0 must-apply evidence gaps, and 0 blocking
  gaps.

## Functional Verification Evidence

The current combined working tree passes the focused implementation checks:

- With `GTKB_NO_CROSS_HARNESS_TRIGGER` removed from the child process:
  `python -m pytest platform_tests\scripts\test_fab13_retention_policy.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_session_envelope_runtime.py platform_tests\hooks\test_owner_decision_tracker.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab13-lo-b`
  passed: 131 tests.
- `python -m ruff check .claude\hooks\owner-decision-tracker.py scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\session\envelope.py platform_tests\scripts\test_fab13_retention_policy.py`
  passed.
- `python -m ruff format --check .claude\hooks\owner-decision-tracker.py scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\session\envelope.py platform_tests\scripts\test_fab13_retention_policy.py`
  passed: 4 files already formatted.

A first run without clearing the automation harness environment failed because
`GTKB_NO_CROSS_HARNESS_TRIGGER` was present and the trigger suite returned
loop-prevention summaries instead of normal dispatch summaries. The rerun above
matches the implementation report's intended trigger-enabled verification
state.

The NO-GO below is not based on failing retention behavior.

## Blocking Findings

### F1 - The report still requires future commit finalization

The implementation report explicitly discloses same-file staged/unstaged
overlap in two FAB13-touched files:

- `scripts/cross_harness_bridge_trigger.py`
- `memory/pending-owner-decisions.md`

For `scripts/cross_harness_bridge_trigger.py`, the report says staged
pre-existing hunks remain from earlier bridge work, FAB13 added new unstaged
retention helpers and cleanup behavior, and the unstaged file still includes
earlier non-FAB13 dispatch-routing work. It then says commit finalization must
separate or explicitly account for both scopes.

That is still a future finalization plan, not a verifiable artifact state. The
current file remains `MM`, so a normal commit of the file would still combine
claimed FAB13 behavior with unclaimed same-file dispatch work. A verifier
cannot mark the implementation VERIFIED until the passing test evidence is tied
to an exact durable source set.

### F2 - The durable commit candidate omits claimed implementation files

The report claims implementation changes across:

- `.claude/hooks/owner-decision-tracker.py`
- `memory/pending-owner-decisions.md`
- `memory/archive/pending-owner-decisions-202604.md`
- `memory/archive/pending-owner-decisions-202605.md`
- `groundtruth.db`
- `scripts/cross_harness_bridge_trigger.py`
- `config/governance/runtime-evidence-retention.toml`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `.driveignore`
- `.gitignore`
- `platform_tests/scripts/test_fab13_retention_policy.py`

Current index state for that implementation set contains only:

- `M memory/pending-owner-decisions.md`
- `M scripts/cross_harness_bridge_trigger.py`

The live working tree additionally shows unstaged changes to
`.claude/hooks/owner-decision-tracker.py`, `.driveignore`, `.gitignore`,
`groundtruth-kb/src/groundtruth_kb/session/envelope.py`,
`memory/pending-owner-decisions.md`, and
`scripts/cross_harness_bridge_trigger.py`. It also shows untracked files for
the new retention policy config, the two archive sidecars, and the focused
FAB13 test file.

This means the passing verification evidence describes the live working tree,
not a complete durable commit candidate. The report needs to either present a
clean staged candidate or explicitly state a final target-path/hunk set whose
durable state matches the tested tree.

## Required Revision

Prime Builder should refile after resolving the artifact traceability boundary:

1. Separate the pre-existing dispatch-routing / owner-decision staged layer
   from FAB13, or revise the FAB13 scope so every required same-file hunk is
   explicitly claimed under active authority.
2. Stage or otherwise make durable every claimed FAB13 file, including the new
   retention policy config, sidecar archives, and regression test file.
3. Re-run the focused pytest, ruff check, and ruff format check against that
   final source set.
4. Include the final git status or staged file list in the revised report so
   Loyal Opposition can verify the exact artifact that Prime Builder intends to
   commit.

## Verdict

NO-GO. FAB13's behavior appears coherent in the live working tree, but the
implementation report has not yet resolved the same-file overlap and untracked
artifact state into a complete durable commit candidate.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
