VERIFIED

# GTKB Telemetry Churn Policy - Codex Verification

**Status:** VERIFIED
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gtkb-telemetry-churn-policy-2026-04-28-003.md`

bridge_kind: lo_verdict
work_item_ids: []
spec_ids: []
target_project: gtkb
implementation_scope: repository-hygiene
requires_review: false
requires_verification: false

---

## Verdict

VERIFIED.

Commit `6c3819e6` implements the approved hybrid telemetry policy: the two
large dashboard JSON telemetry files are ignored and removed from git tracking,
while the small markdown reports and durable owner-decision file remain
tracked.

## Verification Evidence

Commit stat:

```text
6c3819e6 gitignore: Move auto-regen dashboard telemetry out of git tracking
 .gitignore                                         |   10 +
 docs/gtkb-dashboard/dashboard-data.json            | 7791 --------------------
 memory/gtkb-dashboard-history.json                 | 3600 ---------
 tests/scripts/test_groundtruth_governance_adoption.py | 14 +-
```

Tracking and ignore checks:

```text
git ls-files docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
# empty

git ls-files docs/gtkb-dashboard/session-startup-report.md docs/gtkb-dashboard/session-wrapup-report.md memory/pending-owner-decisions.md
docs/gtkb-dashboard/session-startup-report.md
docs/gtkb-dashboard/session-wrapup-report.md
memory/pending-owner-decisions.md

git check-ignore -v docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
.gitignore:374:docs/gtkb-dashboard/dashboard-data.json
.gitignore:375:memory/gtkb-dashboard-history.json
```

On-disk presence:

```text
Test-Path docs/gtkb-dashboard/dashboard-data.json  -> True
Test-Path memory/gtkb-dashboard-history.json       -> True
```

SessionStart regeneration/status check:

```powershell
python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
git status --short -- docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
```

Result: no status output for the two ignored JSON files; both still exist.

Tracked small-state files still update as expected:

```text
 M docs/gtkb-dashboard/session-startup-report.md
 M docs/gtkb-dashboard/session-wrapup-report.md
 M memory/pending-owner-decisions.md
```

## Non-Blocking Observation

`python -m pytest tests/scripts/test_groundtruth_governance_adoption.py -q`
still errors during collection because `groundtruth_kb.db` is not importable.
This is the pre-existing import surface reported in `-003`; collection fails
before the updated assertions can run. It is not introduced by the telemetry
policy commit.

## Summary

The repository no longer tracks the high-churn dashboard JSON telemetry files,
runtime generation remains functional, and the durable small session-state
files remain tracked.

