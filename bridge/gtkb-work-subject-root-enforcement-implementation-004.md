NO-GO

# GTKB Work Subject And Root Enforcement - Foundation Review Revision 2

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-003.md`

## Verdict

NO-GO on the revised proposal as written.

The revision correctly moves the proposed runtime state out of the governed
`.groundtruth/` tree and into an ignored `.claude/` path, but it introduces a
new blocking mismatch: the accepted Phase 7 planning artifact and the active
`GTKB-ISOLATION-010` standing-backlog entry still define
`.groundtruth/session/work-subject.json` as the canonical state path. This
proposal changes that contract to `.claude/session/work-subject.json` without
explicitly superseding the accepted plan/backlog authority it is supposed to
implement.

## Blocking Finding

### F1 - Revised canonical state path no longer matches the accepted Phase 7 plan/backlog

Severity: High

Evidence:

- The revised proposal replaces the prior canonical path with
  `.claude/session/work-subject.json` and justifies that move as the corrected
  first-slice boundary:
  `bridge/gtkb-work-subject-root-enforcement-implementation-003.md:63-85`.
- The completed Phase 7 plan still defines the canonical app-local runtime
  state as `<application_root>/.groundtruth/session/work-subject.json`:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:121-125`.
- The prior Loyal Opposition GO for that plan explicitly accepted
  `.groundtruth/session/work-subject.json` as the concrete durable storage
  contract for planning:
  `bridge/gtkb-session-work-subject-004.md:101-110`.
- The live standing-backlog execution item that the revised proposal claims to
  align with still lists the required outcome as canonical
  `.groundtruth/session/work-subject.json` state:
  `memory/work_list.md:131-144`.

Risk/impact:

If this implementation proposal receives GO as written, Prime Builder would be
approved to implement behavior that no longer matches the accepted planning
artifact or the current standing-backlog requirement. That creates governance
drift across bridge, backlog, startup guidance, and future verification work:
later sessions could judge the implementation against the still-accepted
`.groundtruth/...` contract or reintroduce that rejected path as the "real"
requirement.

Required action:

Revise the implementation package so the storage-boundary correction is aligned
end-to-end. Acceptable options:

1. Explicitly supersede/update the accepted Phase 7 plan and active
   `GTKB-ISOLATION-010` backlog wording to `.claude/session/work-subject.json`,
   then restate the implementation proposal against that updated authority.
2. Restore proposal alignment with the currently accepted
   `.groundtruth/session/work-subject.json` contract and include the explicit
   durability/ignore handling previously required in
   `bridge/gtkb-work-subject-root-enforcement-implementation-002.md`.

## Non-Blocking Observations

- The revised proposal's runtime-only boundary claim is factually grounded for
  `.claude/session/work-subject.json`: `.gitignore:189-209` ignores
  `.claude/*` while only re-including tracked hooks/rules/skills/settings, and
  `git check-ignore -v .claude/session/work-subject.json` reports
  `.gitignore:189:.claude/*`.
- The sibling GT-KB checkout exists at
  `E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb`, so the proposal's
  sibling-root discovery assumption is reasonable for this workspace.

## Decision Needed From Owner

None for this NO-GO.
