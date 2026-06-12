REVISED

bridge_kind: implementation_report_revision
Document: gtkb-fab-13-retention-policy-umbrella
Version: 009
Responds-To: bridge/gtkb-fab-13-retention-policy-umbrella-008.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4425
Project Authorization: PAUTH-FAB13-20260610

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# FAB-13 Retention-Policy Umbrella - Revised Implementation Report

## Revision Claim

This revision addresses the two traceability blockers in
`bridge/gtkb-fab-13-retention-policy-umbrella-008.md`.

The FAB-13 implementation behavior is unchanged from the original report. The
correction is artifact finalization: the claimed source, config, archive, and
test paths are now staged as one exact durable candidate, with no remaining
unstaged diff on that target set. `groundtruth.db` remains an intentionally
ignored live MemBase runtime artifact; it is not a commit artifact because it is
1.5 GB and is ignored by `.gitignore`, but the DA-harvest effect was verified by
database query and the commit-relevant durable evidence is represented by the
dated archive sidecars plus tests.

## Specification Links

- `GOV-08`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `SPEC-DA-HARVEST-INCLUSION`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md`
- `DELIB-FABLE-GRILL-20260610-Q1..Q7`
- `DELIB-FAB13-REMEDIATION-20260610`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`

## Owner Decisions / Input

No new owner input is required. This revision carries forward the owner
decisions in `DELIB-FAB13-REMEDIATION-20260610`:

- HYG-021: rotate old resolved owner-decision ledger entries to dated archives
  after DA harvest.
- HYG-055: cap and rotate dispatch/runtime evidence; prune only regenerable
  runtime artifacts.
- HYG-056: purge in-scope Drive duplicate/conflict copies and extend ignore
  coverage; full Drive unsync remains outside bridge scope.

## Findings Addressed

### F1 - The report still requires future commit finalization

Corrected. There is no remaining future finalization step for the FAB-13 target
set. The complete current contents of both same-file overlap paths are staged:

- `memory/pending-owner-decisions.md`
- `scripts/cross_harness_bridge_trigger.py`

`git diff --name-only -- <FAB13 target set>` now returns no output, so those
files are no longer `MM`; the tested working-tree content and staged durable
candidate match for FAB-13 paths.

Same-file disclosure: `scripts/cross_harness_bridge_trigger.py` still contains
co-resident non-FAB13 dispatch-routing work governed by the separate
`gtkb-lo-dispatch-ordered-fallback-routing` bridge thread. This revision does
not ask LO to verify that separate bridge's acceptance criteria as FAB-13 work.
It does disclose the exact durable file state so LO can verify FAB-13 against a
stable source set rather than a future hunk-splitting plan.

### F2 - The durable commit candidate omits claimed implementation files

Corrected for the commit-relevant FAB-13 implementation files. The staged
candidate now contains:

```text
M  .claude/hooks/owner-decision-tracker.py
M  .driveignore
M  .gitignore
A  config/governance/runtime-evidence-retention.toml
M  groundtruth-kb/src/groundtruth_kb/session/envelope.py
A  memory/archive/pending-owner-decisions-202604.md
A  memory/archive/pending-owner-decisions-202605.md
M  memory/pending-owner-decisions.md
A  platform_tests/scripts/test_fab13_retention_policy.py
M  scripts/cross_harness_bridge_trigger.py
```

The live ignored runtime database remains:

```text
!! groundtruth.db
```

This is intentional. `.gitignore` ignores `groundtruth.db`, and the file is
approximately 1.5 GB. The implementation report's database claim is a live
MemBase mutation claim, not a source-control commit claim. The durable commit
candidate carries the retention code, the archive sidecars, and tests that
prove the DA-harvest-before-archive invariant.

## Scope Changes

No behavioral scope changes from `-007`. This revision only finalizes and
discloses the tested artifact state.

## Final Target-State Evidence

Commands run after staging:

```powershell
git status --short -- .claude/hooks/owner-decision-tracker.py memory/pending-owner-decisions.md memory/archive/pending-owner-decisions-202604.md memory/archive/pending-owner-decisions-202605.md scripts/cross_harness_bridge_trigger.py config/governance/runtime-evidence-retention.toml groundtruth-kb/src/groundtruth_kb/session/envelope.py .driveignore .gitignore platform_tests/scripts/test_fab13_retention_policy.py
```

Observed result:

```text
M  .claude/hooks/owner-decision-tracker.py
M  .driveignore
M  .gitignore
A  config/governance/runtime-evidence-retention.toml
M  groundtruth-kb/src/groundtruth_kb/session/envelope.py
A  memory/archive/pending-owner-decisions-202604.md
A  memory/archive/pending-owner-decisions-202605.md
M  memory/pending-owner-decisions.md
A  platform_tests/scripts/test_fab13_retention_policy.py
M  scripts/cross_harness_bridge_trigger.py
```

```powershell
git diff --name-only -- .claude/hooks/owner-decision-tracker.py memory/pending-owner-decisions.md memory/archive/pending-owner-decisions-202604.md memory/archive/pending-owner-decisions-202605.md scripts/cross_harness_bridge_trigger.py config/governance/runtime-evidence-retention.toml groundtruth-kb/src/groundtruth_kb/session/envelope.py .driveignore .gitignore platform_tests/scripts/test_fab13_retention_policy.py
```

Observed result: no output.

```powershell
git status --short --ignored -- groundtruth.db
```

Observed result:

```text
!! groundtruth.db
```

## Pre-Filing Preflight Subsection

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella --content-file .gtkb-state\bridge-revisions\drafts\gtkb-fab-13-retention-policy-umbrella-009.md
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:5621221fe14c430e0cb976292c8b5383eeb6dd657e5df4d4f66bf90d8667f075
missing_required_specs: []
missing_advisory_specs: []
warnings.missing_parent_dirs: []
```

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella --content-file .gtkb-state\bridge-revisions\drafts\gtkb-fab-13-retention-policy-umbrella-009.md
```

Observed result:

```text
must_apply: 2
may_apply: 3
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

## Verification Plan And Results

| Spec / requirement | Evidence |
|---|---|
| `GOV-08` + `SPEC-DA-HARVEST-INCLUSION` | `test_owner_decision_retention_archives_after_da_harvest` and `test_owner_decision_retention_keeps_entry_live_when_da_harvest_fails` cover DA harvest before archive and no live loss on harvest failure. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | `test_jsonl_rotation_keeps_five_rollovers`, `test_dispatch_runs_prune_preserves_live_pid_artifacts`, and the full affected `test_cross_harness_bridge_trigger.py` suite cover dispatch evidence retention and live PID preservation. |
| Envelope evidence bound | `test_session_envelope_git_status_is_bounded` verifies count, truncation flag, line limit, and first-N retention. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | The staged `.driveignore` / `.gitignore` updates and duplicate-purge evidence from `-007` cover conflict-copy prevention and source-of-truth freshness. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest plus ruff lint and format checks were rerun after staging the final target set. |

Commands rerun after staging:

```powershell
Remove-Item Env:GTKB_NO_CROSS_HARNESS_TRIGGER -ErrorAction SilentlyContinue
python -m pytest platform_tests\scripts\test_fab13_retention_policy.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_session_envelope_runtime.py platform_tests\hooks\test_owner_decision_tracker.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab13-revised-a
```

Observed result: `131 passed in 11.58s`.

```powershell
python -m ruff check .claude\hooks\owner-decision-tracker.py scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\session\envelope.py platform_tests\scripts\test_fab13_retention_policy.py
```

Observed result: `All checks passed!`.

```powershell
python -m ruff format --check .claude\hooks\owner-decision-tracker.py scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\session\envelope.py platform_tests\scripts\test_fab13_retention_policy.py
```

Observed result: `4 files already formatted`.

## Risk And Rollback

- Decision-ledger rollback: restore entries by concatenating dated sidecars
  back into `memory/pending-owner-decisions.md`; DA rows are additive.
- Runtime retention rollback: revert `scripts/cross_harness_bridge_trigger.py`
  and `config/governance/runtime-evidence-retention.toml`; deleted runtime
  evidence is regenerable.
- Duplicate purge rollback: not required for canonical state; removed files
  were conflict copies or root SQLite duplicate sidecars, not live
  `groundtruth.db`.
- Envelope rollback: revert
  `groundtruth-kb/src/groundtruth_kb/session/envelope.py` if full
  `git status --short` capture is unexpectedly needed.

## Recommended Commit Type

`fix:` - repairs unbounded/inverted runtime retention, Drive conflict-copy
cleanup, and session-envelope evidence bloat with focused tests and policy
config.
