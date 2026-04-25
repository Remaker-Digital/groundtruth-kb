# Pending Owner Decisions

This file tracks owner-decision asks across sessions. The
`.claude/hooks/owner-decision-tracker.py` hook is the canonical writer:
it appends entries on Stop (when the assistant turn invoked
`AskUserQuestion` or matched a prose anti-pattern) and updates statuses
on `UserPromptSubmit` when the owner responds with a recognized shortcut.

The startup-disclosure renderer
(`scripts/session_self_initialization.py`) reads the `## Pending`
section and surfaces the entries in
`docs/gtkb-dashboard/session-startup-report.md`. The
`UserPromptSubmit` hook nudges if the owner's prompt arrives without
referencing pending decisions. The release-candidate gate's parity
verifier (`scripts/check_pending_owner_decisions_parity.py`) prints
the same content for harnesses that do not run the Claude hook.

Do NOT edit by hand under normal operation; the hook owns the
canonical state. Manual edits should add an `Edited-by-owner: <ISO timestamp>`
note in the affected entry's `notes` field for audit trail.

Per the GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 contract
(`bridge/gtkb-gov-owner-decision-surfacing-slice1-003.md` GO at `-004`),
this file is durable across sessions: SessionStart reads it; Stop
appends to it; UserPromptSubmit nudges off it.

---

## Pending

(none)

## Resolved

(none)

## History

(none)
