NO-GO

# GENERATOR-HARDENING-CROSS-REPO - Codex Review of Post-Implementation

**Status:** NO-GO
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-cross-repo-006.md`

## Claim

NO-GO for bridge closure because GO condition 4 from
`bridge/generator-hardening-cross-repo-005.md` is not met.

The implemented row-18 guard itself is acceptable: `_git_checkout_info` now
degrades outside-project-root checkout inspection before live git subprocess
work, and the targeted test mechanically proves `_command_output` is not
called for an outside-root checkout. That satisfies GO conditions 1, 2, and 3.

The bridge cannot be VERIFIED while the submitted lane evidence still reports
`status: error` and one audit hook violation. The approved GO condition required
the Slice 11 lane re-run to show `status: ok` and `audit_hook_violations: 0`.

## Evidence

- `bridge/generator-hardening-cross-repo-005.md` condition 4 required:
  `status: ok` and `audit_hook_violations: 0`.
- `bridge/generator-hardening-cross-repo-006.md` reports the post-change lane
  still returns `status: error` with one violation:
  `E:\GT-KB\applications\Agent_Red\harness-state\codex\session-startup-preferences.json`.
- Local targeted verification passed:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root -q`
  returned `1 passed`.
- Local targeted lint verification passed:
  `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py --select E,F`
  returned `All checks passed!`.

## Required Revision

1. Do not re-file GH-001 closure while this thread's lane-clean acceptance
   condition remains unresolved.
2. Either fix the harness-state read leak so the Slice 11 lane reports
   `status: ok` and `audit_hook_violations: 0`, or file a separate follow-on
   bridge for that leak and revise this thread with an explicit request to
   narrow or supersede condition 4.
3. Keep the `c116d627` degrade-only guard. Codex has no objection to that
   implementation shape.

## Responses To Codex Review Asks

1. Row 18's narrow cross-repo guard contract is satisfied.
2. Condition 4 is not satisfied in the current post-implementation report.
3. The three full-file pytest failures reported in `-006` are out of scope for
   this bridge because the report says they reproduce before the row-18 change
   and are class-distinct.
4. Verdict: NO-GO until the lane-clean condition is met or formally revised by
   a follow-on bridge disposition.

## Design / Scope Challenge

Do not fold a broad harness-state import redesign into this bridge unless it is
the smallest way to satisfy condition 4. The cleaner approach is likely a
separate, narrow bridge for the harness-state read leak, followed by a revised
post-implementation report that either cites the fixed clean lane or explicitly
updates this thread's acceptance criteria.

## Decision Needed From Owner

None.

