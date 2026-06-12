NEW

bridge_kind: implementation_report
Document: gtkb-fab-13-retention-policy-umbrella
Version: 007
Responds-To: bridge/gtkb-fab-13-retention-policy-umbrella-006.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4425
Project Authorization: PAUTH-FAB13-20260610

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

# FAB-13 Retention-Policy Umbrella - Implementation Report

## Implementation Authorization

Prime Builder started implementation from the live latest `GO` entry:

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-13-retention-policy-umbrella
```

Observed packet hash: `sha256:93970e9a91913a1783df499b5b5811bf4ca33a830d6f62cc337a8b934ee90d07`.

## Summary

Implemented FAB-13 across the three approved areas:

- HYG-021: the owner-decision tracker now uses the FAB13 retention config to archive old resolved/history entries to dated sidecars only after DA harvest succeeds. Temp projects without the config keep the legacy same-file `## History` behavior for backward-compatible tests.
- HYG-055: cross-harness runtime evidence now has a TOML-backed retention policy, five-rollover JSONL rotation, inactive dispatch-run pruning by age/size, and conservative `.gtkb-state` GC for stale pytest/uv-cache runtime directories. Session envelopes now bound `git status --short` to count + first 80 lines.
- HYG-056: `.driveignore` now covers hook-state JSON/err files and locks; `.gitignore` now includes generalized Drive conflict-copy patterns; a one-time duplicate purge removed only approved-perimeter conflict copies and root SQLite duplicate sidecars.

## Files Changed

FAB13 implementation files:

- `.claude/hooks/owner-decision-tracker.py`
- `memory/pending-owner-decisions.md`
- `memory/archive/pending-owner-decisions-202604.md`
- `memory/archive/pending-owner-decisions-202605.md`
- `groundtruth.db` (ignored working DB; DA harvest inserted owner-decision deliberation rows)
- `scripts/cross_harness_bridge_trigger.py`
- `config/governance/runtime-evidence-retention.toml`
- `groundtruth-kb/src/groundtruth_kb/session/envelope.py`
- `.driveignore`
- `.gitignore`
- `platform_tests/scripts/test_fab13_retention_policy.py`

One-time cleanup deleted 38 regenerable/duplicate files inside the approved deletion perimeter:

- root SQLite duplicate sidecars: `groundtruth (2).db-shm`, `groundtruth (2).db-wal`, `groundtruth (3).db-shm`, `groundtruth (3).db-wal`, `groundtruth (4).db-shm`, `groundtruth (5).db-shm`, `groundtruth (6).db-shm`, `groundtruth (7).db-shm`, `groundtruth (8).db-shm`, `groundtruth (9).db-shm`
- `.gtkb-state/bridge-poller/active-*-session (N).lock`
- `.gtkb-state/implementation-authorizations/current (2).json`
- `.codex/gtkb-hooks/last-session-start (N).json`
- `.claude/hooks/last-session-start (N).json`

## Same-File Scope Disclosure

The repository was already dirty before FAB13 implementation. Two FAB13-touched files had same-file staged/unstaged overlap:

- `scripts/cross_harness_bridge_trigger.py`: staged pre-existing hunks remained from earlier bridge work (`git diff --cached --stat` reported 55 insertions / 15 deletions). FAB13 added new unstaged retention-policy helpers, JSONL rotation, dispatch-run pruning, `.gtkb-state` GC, and trigger startup wiring. The unstaged file also still includes earlier non-FAB13 dispatch-routing work; commit finalization must separate or explicitly account for both scopes.
- `memory/pending-owner-decisions.md`: staged pre-existing 27-line owner-decision content remained. FAB13's unstaged live rotation removed 537 old history entries from the live ledger after DA harvest and sidecar archival.

No staged content was reverted or unstaged by this implementation.

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

## Spec-To-Test Mapping And Results

| Spec / requirement | Evidence |
|---|---|
| `GOV-08` + `SPEC-DA-HARVEST-INCLUSION` | `platform_tests/scripts/test_fab13_retention_policy.py::test_owner_decision_retention_archives_after_da_harvest` asserts DA harvest happens before sidecar write; `test_owner_decision_retention_keeps_entry_live_when_da_harvest_fails` asserts failed DA harvest keeps the entry live. Live backfill rotated 537 old history entries and verification found 537 archived IDs with 537 DA rows. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` | `test_jsonl_rotation_keeps_five_rollovers` covers 10 MB x 5 rollover semantics in reduced-size fixture form; `test_dispatch_runs_prune_preserves_live_pid_artifacts` covers age/size pruning while preserving live PID artifacts; the full existing `test_cross_harness_bridge_trigger.py` suite passed after wiring retention into trigger startup. Live retention pruned 6,017 bridge-poller dispatch-run artifacts (1,349,968,764 bytes) and 4 cross-harness-trigger dispatch-run artifacts (1,730 bytes), and GC removed 14 stale pytest/uv-cache directories (37,412,868 bytes). |
| envelope git-status bound | `test_session_envelope_git_status_is_bounded` verifies dirty count, truncation flag, line limit, and first-N-line retention. Existing `test_session_envelope_runtime.py` passed. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | One-time duplicate purge removed 38 conflict-copy files inside `.gtkb-state/**`, `.codex/gtkb-hooks/**`, `.claude/hooks/*.json`, and root SQLite duplicate sidecar perimeters. Post-purge scan reported `remaining_count: 0` for `name (N).ext` files outside `.git` / venv-style exclusions. `.driveignore` and `.gitignore` now include generalized conflict-copy coverage. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused FAB13 tests, affected trigger/envelope/owner-decision regressions, `ruff check`, and `ruff format --check` were executed and passed. |

## Commands Run

### Bridge Preflights

```powershell
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-fab-13-retention-policy-umbrella-007.md
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:415da2f9b7a8682d1a42ce77710efca71779c41d34110a519aced8431bef5911
missing_required_specs: []
missing_advisory_specs: []
```

```powershell
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-13-retention-policy-umbrella --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-fab-13-retention-policy-umbrella-007.md
```

Observed result:

```text
must_apply: 2
may_apply: 3
Evidence gaps in must_apply clauses: 0
Blocking gaps (gate-failing): 0
```

### Verification

```powershell
$env:GTKB_NO_CROSS_HARNESS_TRIGGER='0'; python -m pytest platform_tests\scripts\test_fab13_retention_policy.py platform_tests\scripts\test_cross_harness_bridge_trigger.py platform_tests\scripts\test_session_envelope_runtime.py platform_tests\hooks\test_owner_decision_tracker.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab13-final-a
```

Observed result: `131 passed in 9.01s`.

```powershell
python -m ruff check .claude\hooks\owner-decision-tracker.py scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\session\envelope.py platform_tests\scripts\test_fab13_retention_policy.py
```

Observed result: `All checks passed!` (ruff warning only: `Different package root in cache`, non-failing).

```powershell
python -m ruff format --check .claude\hooks\owner-decision-tracker.py scripts\cross_harness_bridge_trigger.py groundtruth-kb\src\groundtruth_kb\session\envelope.py platform_tests\scripts\test_fab13_retention_policy.py
```

Observed result: `4 files already formatted` (same non-failing ruff cache warning).

## Live Cleanup Evidence

Owner-decision backfill rotation:

```json
{
  "eligible_count": 537,
  "mutated": true,
  "pre_counts": {"pending": 1, "resolved": 582, "history": 581},
  "post_counts": {"pending": 1, "resolved": 582, "history": 44},
  "archive_files": [
    "memory/archive/pending-owner-decisions-202604.md",
    "memory/archive/pending-owner-decisions-202605.md"
  ]
}
```

DA verification:

```json
{
  "archived_ids": 537,
  "archived_ids_with_da_rows": 537,
  "all_decision_da_rows": 539
}
```

Runtime retention pass:

```json
{
  "dispatch_runs": {
    "E:\\GT-KB\\.gtkb-state\\bridge-poller": {"deleted_count": 6017, "deleted_bytes": 1349968764},
    "E:\\GT-KB\\.gtkb-state\\cross-harness-trigger": {"deleted_count": 4, "deleted_bytes": 1730}
  },
  "gtkb_state_gc": {"deleted_count": 14, "deleted_bytes": 37412868},
  "policy": {
    "dispatch_runs_retention_days": 14,
    "dispatch_runs_max_bytes": 209715200,
    "jsonl_max_bytes": 10485760,
    "jsonl_rollovers": 5,
    "gtkb_state_gc_age_days": 14
  }
}
```

Duplicate purge:

```json
{
  "removed_count": 38,
  "post_purge_remaining_count": 0
}
```

## Acceptance Criteria Status

- Area 1: PASS. Live ledger is now bounded to 1 pending, 582 resolved, and 44 recent/history entries; 537 old entries are archived in dated sidecars and have DA rows.
- Area 2: PASS. Policy config exists; trigger JSONLs rotate through five rollovers; dispatch-runs prune by 14d/200MB; stale pytest/uv-cache GC runs; session envelope git-status is bounded.
- Area 3: PASS. In-scope duplicate files were purged; post-purge scan found zero `name (N).ext` files outside excluded `.git`/venv-style directories; `.driveignore` and `.gitignore` gained coverage.
- Code quality: PASS. Focused tests, affected regressions, ruff lint, and ruff format-check passed.

## Risk And Rollback

- Decision-ledger rollback: restore entries by concatenating the dated sidecars back into `memory/pending-owner-decisions.md`; DA rows are additive and idempotent by source reference.
- Runtime retention rollback: revert `scripts/cross_harness_bridge_trigger.py` and `config/governance/runtime-evidence-retention.toml`; deleted runtime evidence is regenerable by future dispatch activity.
- Duplicate purge rollback: not needed for canonical state; removed files were conflict copies or root SQLite duplicate sidecars, not live `groundtruth.db`.
- Envelope rollback: revert `groundtruth-kb/src/groundtruth_kb/session/envelope.py` to restore full `git status --short` capture if unexpectedly needed.

## Recommended Commit Type

- Recommended commit type: `fix:`
- Diff-stat justification: repairs unbounded/inverted runtime retention, Drive conflict-copy cleanup, and session-envelope evidence bloat with focused tests and policy config.
