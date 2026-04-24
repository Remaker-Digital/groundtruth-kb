GO

# GTKB-ISOLATION-008 Phase 8 Migration Rehearsal Plan Review

**Status:** GO
**Prepared by:** Loyal Opposition
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-isolation-008-migration-plan-review-003.md`

## Verdict

GO.

Revision 1 resolves the blocking factual mismatch from `bridge/gtkb-isolation-008-migration-plan-review-002.md` and keeps the plan inside the previously approved planning-only scope.

## Rationale

1. Surface 11 is now re-baselined against the live workspace instead of being treated as already retired. The revised plan records `.claude/hooks/workstream-focus.py` as a live B/C transitional wrapper paired with surface 10, gives it an explicit action, transformation recipe, rollback path, and verification matrix, and explicitly supersedes the earlier transient-absence note (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-008-PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:64-75`, `:388-424`).
2. The live repository evidence supports that re-baseline: `.claude/hooks/workstream-focus.py` exists and still loads the shared workstream module (`.claude/hooks/workstream-focus.py:1-39`), Codex parity still treats it as an active hook target (`scripts/check_codex_hook_parity.py:14-24`, `:195-216`, `:300-340`), the regression test still subprocesses that exact file (`tests/hooks/test_workstream_focus.py:14-46`), and the Phase 1 authority matrix still groups surfaces 10 and 11 together as one transitional wrapper surface (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-001-PHASE1-AUTHORITY-MATRIX-PLAN-2026-04-22.md:120-123`).
3. The required Phase 8 planning bindings remain intact after the revision. The plan still maps all seven required coverage areas to concrete rehearsal artifacts (`...PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:88-232`), still binds the four exit criteria to concrete checks and protected non-move artifacts (`:494-565`), and still preserves the planning-only / no-execution fence plus implementation-bridge owner decisions (`:567-608`). Those sections remain aligned with the inventory requirements (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:228-243`, `:648-663`).
4. The regression section no longer carries the stale "already absent" assumption. Instead it requires positive verification for the live wrapper pair and explicitly defers any negative-presence assertion to the later Phase 7-aligned retirement bridge, which is consistent with current repository state and avoids baking a false present-day invariant into Phase 8 rehearsal acceptance (`...PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:610-640`).

## Findings

### No blocking findings

The prior NO-GO item F1 is resolved, and I found no new scope-creep, authority, or verification gaps that block accepting this plan as the planning basis for the later Phase 8 implementation bridge.

## Evidence

- Read-only path check in the live Agent Red workspace on 2026-04-23 returned `True` for the path-backed mixed-state surfaces cited by this plan, including `groundtruth.toml`, `tools/knowledge-db/groundtruth.toml`, `groundtruth.db`, `.claude/hooks/workstream-focus.py`, `bridge/INDEX.md`, `memory/work_list.md`, `memory/release-readiness.md`, and `docs/gtkb-dashboard/`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\README.md:55-60,122-124` still documents the separate GT-KB product entrypoints (`gt project init`, `gt project doctor`, `gt project upgrade`) that this Phase 8 plan correctly treats as out-of-root product concerns rather than rehearsal-authorized rewrites.

## Required Action Items Or Conditions

None.

The later implementation bridge still has to surface the owner decisions already listed in the approved plan before execution starts (`...PHASE8-AGENT-RED-MIGRATION-REHEARSAL-PLAN-2026-04-23.md:584-608`), but that is execution governance, not a remaining planning-review blocker.

## Decision Needed From Owner

None.
