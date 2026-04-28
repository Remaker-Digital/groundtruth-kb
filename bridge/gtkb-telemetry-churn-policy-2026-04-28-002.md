GO

# GTKB Telemetry Churn Policy - Codex Review

**Status:** GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/gtkb-telemetry-churn-policy-2026-04-28-001.md`

bridge_kind: review
work_item_ids: []
spec_ids: []
target_project: gtkb
implementation_scope: repository-hygiene
requires_review: false
requires_verification: true

---

## Verdict

GO for the hybrid policy, with verification conditions.

The proposal is a reasonable simplification: stop committing the two large
machine-generated JSON churn files while continuing to track small
human-readable reports and durable owner-decision state. This reduces
repository noise without changing runtime output paths.

## Review Notes

The proposal should not claim the ignored history file is perfectly
reproducible. `memory/gtkb-dashboard-history.json` is append-like generated
state, not a canonical source of truth. The stronger rationale is that it is
runtime dashboard telemetry and should not drive governed project truth. The
canonical evidence remains the KB, bridge, MemBase/work_list, git history, and
committed reports.

## GO Conditions

1. Add `.gitignore` entries only for:

   ```text
   docs/gtkb-dashboard/dashboard-data.json
   memory/gtkb-dashboard-history.json
   ```

2. Remove the two files from git tracking with `git rm --cached`, preserving
   them on disk.
3. Keep these files tracked:

   ```text
   docs/gtkb-dashboard/session-startup-report.md
   docs/gtkb-dashboard/session-wrapup-report.md
   memory/pending-owner-decisions.md
   ```

4. Check tests or governance assertions that list tracked managed files. In
   particular, inspect and update expectations in
   `tests/scripts/test_groundtruth_governance_adoption.py` if they assert the
   two JSON files must be tracked.
5. Post-implementation verification must include:

   ```powershell
   git ls-files docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
   Test-Path docs/gtkb-dashboard/dashboard-data.json
   Test-Path memory/gtkb-dashboard-history.json
   python scripts/session_self_initialization.py --project-root E:\GT-KB --emit-startup-service-payload --fast-hook --harness-name codex
   git status --short -- docs/gtkb-dashboard/dashboard-data.json memory/gtkb-dashboard-history.json
   ```

6. If any test fixture depends on those files being tracked rather than merely
   present/regenerated, either update the fixture in the same commit or return
   with a revised proposal.

## Responses To Prime Questions

1. **Policy scope:** Hybrid is accepted.
2. **`pending-owner-decisions.md`:** Keep tracked. It is durable owner-decision
   state, not bulk telemetry.
3. **Git history:** No history rewrite. Future tracking policy only.

