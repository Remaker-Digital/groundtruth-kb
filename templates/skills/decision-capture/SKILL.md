---
name: gtkb-decision-capture
description: Capture an owner decision as a governed Deliberation Archive record. Use when the owner makes a yes/no/tradeoff decision worth preserving for future sessions — policy choices, scope calls, design selections, rejected alternatives.
---

# /gtkb-decision-capture

## What this skill does

Records an owner decision as an append-only entry in the Deliberation
Archive via `KnowledgeDB.insert_deliberation()`. Fixed metadata:
`source_type="owner_conversation"`, `outcome="owner_decision"`. Never
mutates specs, work items, or other artifacts. Enforces DELIB-ID
collision checks so repeated IDs raise explicitly rather than
silently version-bumping an unrelated record.

## When to invoke

Use this skill when:

- Owner makes a scope/policy/design decision during a session
- Owner selects one option over considered alternatives
- Owner grants explicit approval that should be durable across sessions

Do NOT use for:

- Routine protocol acknowledgments (bridge GO/NO-GO acks)
- Code review feedback (use Loyal Opposition reports instead)
- Session-scoped reminders (use `MEMORY.md`)

## How it works

Invokes `helpers/record_decision.py` with the owner-supplied:

- DELIB-ID (fresh, caller-generated; collision raises
  `DeliberationIDCollisionError`)
- `title` and `summary` strings for list / detail views
- `content` capturing the decision, options considered, and rationale
- Optional `spec_id`, `work_item_id`, `participants`, `session_id`
  links for traceability

The helper calls `KnowledgeDB.insert_deliberation()` with the fixed
metadata and returns the persisted row as a `dict[str, Any]`. Raises
`DeliberationInsertFailed` if the underlying insert unexpectedly
returns `None`.

Redaction of credential patterns in the `content` body is performed
inside `insert_deliberation()`; the helper does not duplicate that
pass.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
