---
name: gtkb-spec-intake
description: Capture an owner requirement as a temporary candidate, then confirm it into one canonical specification through the native authority or discard it with a reason. Use when the owner states a requirement that should become (or might become) a tracked specification.
---
This skill implements direct requirement intake for ``groundtruth_kb.spec_intake``:
a temporary candidate, one explicit confirmation into a canonical specification,
or a discard with a reason. It pairs confirm-before-mutate ergonomics with
audit attribution (``changed_by = "prime-builder/spec-intake-skill"``) on the
one record it writes. The persisted deliberation queue is retired (O-7 R24).

# /gtkb-spec-intake

## What this skill does

Wraps ``groundtruth_kb.spec_intake`` with three helper functions:

- ``capture_candidate(text, *, proposed_title, proposed_section, ...)`` —
  classify intent and return a temporary candidate (optionally saved as JSON
  under the application's runtime directory). Nothing canonical is written.
- ``confirm_candidate(client, candidate)`` — write exactly one specification
  through the native authority (``expected_version`` 0) and read it back.
- ``reject_candidate(candidate, reason)`` — discard the candidate with the
  owner's reason. Nothing canonical is written.

## Confirm-before-mutate contract

1. **Capture** — ``capture_candidate()`` returns the candidate. No spec, work
   item, ADR, DCL or document is created; the candidate is not a record and
   grants no authorization.
2. **Confirm** *or* **Reject** — at most one of:
   - ``confirm_candidate()`` creates the specification, or
   - ``reject_candidate()`` discards the candidate without any artifact.

A confirmed specification is a current canonical record. Retiring or changing
it later is an explicit canonical amendment, never a rejection side effect.
Confirmation does not create implementation work: native work requires the
specification and an executable test in an active plan phase, recorded with
``gt backlog record`` when the test exists. The confirmation result reports
whether the specification is implementation-bearing.

## When to invoke

Use this skill when the owner states a requirement that should become (or
might become) a tracked specification and has not yet said "yes, add that
spec"; the candidate preserves it for the explicit confirm/reject gate.

Do NOT use for:

- Direct specification creation with owner pre-approval (use ``gt spec record``).
- Owner choices already clear enough to apply: update the affected canonical
  source or perform the requested action. Conversation history stays in session logs.
- Bulk backfill of existing specifications.

## Errors

- ``SpecIntakeCaptureFailed`` — empty text, title or section, or an unknown authority level.
- ``SpecIntakeConfirmFailed`` — not a candidate, the identity already exists (the
  authority refuses without changing data), or the readback differs.
- ``SpecIntakeRejectFailed`` — empty reason, or the object is not a candidate.

## Attribution

| Effect | Record | ``changed_by`` |
|---|---|---|
| Capture | none (temporary candidate) | n/a |
| Confirmation | one specification, version 1 | ``prime-builder/spec-intake-skill`` |
| Rejection | none | n/a |

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
