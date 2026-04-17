---
name: gtkb-spec-intake
description: Capture an owner requirement as a requirement-candidate deliberation at outcome='deferred', then confirm it into a KB spec or reject it with a reason. Use when the owner states a requirement that should become (or might become) a tracked specification.
---

This skill implements the governed requirement-intake path for
``groundtruth_kb.intake``. It is the skill-level wrapper that pairs
confirm-before-mutate ergonomics with audit-trail differentiation
(``changed_by = "prime-builder/spec-intake-skill"``) so the persisted
governance rows distinguish skill-driven captures from legacy
CLI-driven or hook-driven captures.

# /gtkb-spec-intake

## What this skill does

Wraps ``groundtruth_kb.intake.capture_requirement``,
``confirm_intake``, and ``reject_intake`` with three helper functions:

- ``capture_candidate(db, text, *, proposed_title, proposed_section,
  ...)`` — classify intent, persist a requirement-candidate
  deliberation at ``outcome="deferred"``.
- ``confirm_candidate(db, deliberation_id)`` — promote a captured
  candidate into a KB spec (``status="specified"``) and record a
  confirmation-version deliberation at ``outcome="owner_decision"``.
- ``reject_candidate(db, deliberation_id, reason)`` — record a
  rejection-version deliberation at ``outcome="no_go"`` with the
  owner-supplied reason.

All three calls pass
``changed_by="prime-builder/spec-intake-skill"`` so every row written
through the skill is distinguishable from rows written by the legacy
CLI / hook callers of ``intake.py``.

## Confirm-before-mutate contract

The skill enforces a **three-step flow**:

1. **Capture** — ``capture_candidate()`` writes exactly one
   deliberation at ``outcome="deferred"``. No spec, work item, ADR,
   DCL, or document is created. The return value contains the
   ``deliberation_id`` that the next step needs.
2. **Confirm** *or* **Reject** — at most one of:
   - ``confirm_candidate()`` creates the spec and records a
     confirmation-version deliberation, **or**
   - ``reject_candidate()`` records a rejection-version deliberation
     without creating any artifact.

Under no circumstances does ``capture_candidate()`` silently mutate
specs, work items, ADRs, DCLs, or documents. The ``"deferred"``
outcome is the state that forces the explicit confirm/reject gate.

## When to invoke

Use this skill when:

- Owner states a requirement during a session and you want to
  preserve it for later confirmation (before owner has explicitly
  said "yes, add that spec").
- You want the audit trail to attribute the capture to the skill
  rather than to the generic intake pipeline.
- You need the confirm-before-mutate ergonomics so the spec is not
  created until the owner has explicitly approved it.

Do NOT use for:

- Direct spec creation with owner pre-approval (use
  ``KnowledgeDB.insert_spec()`` or ``/kb-spec`` instead).
- Decision capture of yes/no/tradeoff choices (use
  ``/gtkb-decision-capture``).
- Bulk backfill of existing specs (out of scope for this skill).

## How it works

Invokes ``helpers/spec_intake.py``'s three functions.

### Phase 1 — Capture

``capture_candidate(db, text, *, proposed_title, proposed_section,
proposed_scope=None, proposed_type="requirement",
proposed_authority="stated")`` calls
``intake.capture_requirement(...)`` with
``changed_by="prime-builder/spec-intake-skill"`` and a skill-specific
capture reason.

The persisted deliberation has:

- ``source_type="owner_conversation"`` (fixed)
- ``outcome="deferred"`` (fixed — **never** promoted to other values
  by the skill)
- ``changed_by="prime-builder/spec-intake-skill"`` (fixed)

If ``intake.capture_requirement`` returns a malformed result
(missing ``deliberation_id`` key, or not a dict),
``SpecIntakeCaptureFailed`` is raised. This is a defensive guard
against library regressions — not a recoverable user state.

### Phase 2 — Confirm (owner said yes)

``confirm_candidate(db, deliberation_id)`` calls
``intake.confirm_intake(...)`` with
``changed_by="prime-builder/spec-intake-skill"``. The call creates a
KB spec (``status="specified"``) and records a confirmation-version
deliberation (``outcome="owner_decision"``). Both rows record the
skill actor.

If ``intake.confirm_intake`` returns an error dict (unknown ID,
non-intake deliberation, ``insert_spec`` returned None),
``SpecIntakeConfirmFailed`` is raised.

### Phase 2' — Reject (owner said no, or candidate is out of scope)

``reject_candidate(db, deliberation_id, reason)`` fails fast on an
empty or whitespace-only ``reason`` at the helper boundary
(``SpecIntakeRejectFailed`` before any library call). Otherwise it
calls ``intake.reject_intake(...)`` with
``changed_by="prime-builder/spec-intake-skill"``. The call records a
rejection-version deliberation (``outcome="no_go"``). No spec is
created.

If ``intake.reject_intake`` returns an error dict,
``SpecIntakeRejectFailed`` is raised.

## Errors

- ``SpecIntakeCaptureFailed`` — capture returned a malformed result.
- ``SpecIntakeConfirmFailed`` — confirm returned an error dict
  (unknown deliberation ID, non-intake deliberation, spec-insert
  failure).
- ``SpecIntakeRejectFailed`` — empty/whitespace reason at the
  helper boundary, or reject returned an error dict.

## Governance metadata summary

| Row | ``source_type`` | ``outcome`` | ``changed_by`` |
|---|---|---|---|
| Capture deliberation | ``owner_conversation`` | ``deferred`` | ``prime-builder/spec-intake-skill`` |
| Confirmation spec | n/a | n/a | ``prime-builder/spec-intake-skill`` |
| Confirmation deliberation | ``owner_conversation`` | ``owner_decision`` | ``prime-builder/spec-intake-skill`` |
| Rejection deliberation | ``owner_conversation`` | ``no_go`` | ``prime-builder/spec-intake-skill`` |

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
