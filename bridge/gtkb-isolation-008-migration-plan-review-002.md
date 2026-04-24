NO-GO

# GTKB-ISOLATION-008 Phase 8 Migration Rehearsal Plan Review

**Status:** NO-GO
**Prepared by:** Loyal Opposition
**Date:** 2026-04-23

## Verdict

NO-GO. The plan is otherwise well-scoped and mostly satisfies the requested
coverage, exit-criterion, and planning-only checks, but approval is blocked by
one high-severity factual mismatch in mixed-state surface 11.

## Finding F1 (High)

### Surface 11 is not retired/absent in the live workspace

The plan states that `.claude/hooks/workstream-focus.py` is already absent in
the live Agent Red workspace and should therefore be treated only as a retired
surface with no rewrite rule or test references
(`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:381-395`).
The upstream GO note repeats that same claim
(`bridge/gtkb-isolation-phases-8-9-planning-scope-004.md:41-46`).

The current workspace contradicts that premise:

- `.claude/hooks/workstream-focus.py` exists in the live Agent Red root and is
  an executable hook adapter
  (`.claude/hooks/workstream-focus.py:1-18`).
- The workstream-focus hook path is still treated as an active parity target in
  `scripts/check_codex_hook_parity.py`
  (`scripts/check_codex_hook_parity.py:15-17`, `:195-216`, `:300-340`).
- The hook test module still points directly at that file and subprocesses it
  as `HOOK_PATH`
  (`tests/hooks/test_workstream_focus.py:14-17`, `:28-46`).
- Phase 1's authority matrix still treats `scripts/workstream_focus.py` and
  `.claude/hooks/workstream-focus.py` together as the current transitional
  wrapper surface rather than as an already-absent artifact
  (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:122`).

## Risk / Impact

If approved as written, the implementation bridge would plan against an
incorrect current-state inventory, omit a live mixed-state surface from the
real rehearsal treatment, and carry forward a false regression expectation
("absent already") into path-rewrite, hook-parity, and verification work.

That directly weakens the review's requested confirmation that each mixed-state
surface has a correct named action, transformation recipe, rollback behavior,
and post-migration verification, especially for surface 11.

## Required Revisions

1. Revise surface 11 to match the current repository state.
2. Choose and document one explicit handling path:
   - treat `.claude/hooks/workstream-focus.py` as a live transitional wrapper
     surface that must be migrated/rewritten/verified alongside surface 10; or
   - keep the retirement goal, but state that the file is currently present and
     make removal/retirement of the live file plus its remaining references a
     prerequisite dependency rather than a completed fact.
3. Remove or correct the stale "already absent" claim in this plan revision and
   in any dependent acceptance text that assumes present-day absence.
4. Re-baseline the regression/verification text so it matches the chosen
   transition state and explicitly covers the remaining parity/test references.

## Non-Blocking Notes

Aside from F1, the plan does bind the required coverage areas to concrete
rehearsal artifacts (`...PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:81-225`),
binds exit criteria to concrete acceptance checks (`:465-517`), stays within
planning-only scope (`:538-553`), and lists the required "must not move"
artifacts including `groundtruth.db`, production Azure assets, live secrets,
GT-KB product source, and git history (`:521-536`).

## Decision Needed From Prime Builder

Submit a revised plan that resolves F1 and re-enters bridge review.
