NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8f2455b1-c515-479c-b544-720ce8ef2471
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4667 retire the auto-confirmed spec when an intake is rejected

Document: gtkb-wi4667-intake-reject-retire-confirmed-spec
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-4667
Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4667-REJECT-RETIRE-SPEC

target_paths: ["groundtruth-kb/src/groundtruth_kb/intake.py", "groundtruth-kb/tests/test_intake.py"]

## Summary

`reject_intake` (groundtruth-kb/src/groundtruth_kb/intake.py, ~line 485) marks the
intake deliberation `rejected` but never inspects `content["confirmed_spec_id"]`.
When an intake was previously auto-confirmed (the spec-classifier hook path),
`confirm_intake` created a `SPEC-INTAKE-*` row at status `specified` and recorded
its id in `content["confirmed_spec_id"]` (intake.py line 460). A subsequent reject
leaves that spec at `specified` — an orphan "active" specification for a candidate
the owner rejected. The fix: when `reject_intake` runs and a `confirmed_spec_id`
is present, move that spec to `retired` status via `db.update_spec(...)`, so the
KB state reflects the rejection.

## Specification Links

- GOV-SPEC-CAPTURE-TRANSPARENCY-001 — capture lifecycle integrity ("surface every
  capture event ... on approve/reject"). A reject that leaves the auto-confirmed
  spec `specified` makes the KB disagree with the rejection decision; retiring the
  spec on reject keeps the capture lifecycle truthful. (governing)
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; append-only
  numbered-file chain and GO/NO-GO discipline apply.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps the
  behavioral clause (rejected intake's confirmed spec ends at `retired`) to an
  executed test.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  package source/tests in-root; no out-of-root dependency.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the fix is enforced
  by a spec-derived regression test.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + test, advances
  WI-4667 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop over the whole
  backlog (PB picks); basis for the covering PAUTH.
- Deliberation search "intake reject confirmed spec retire orphan stub" (5 hits;
  none reject retiring the confirmed spec on intake rejection).
- Sibling thread `gtkb-wi4665-intake-confirm-description-from-raw-text` (WI-4665,
  NEW) fixes the confirm-path description gap in the same module; this thread
  fixes the reject-path orphan. The two are independent and touch different
  functions.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SPEC-CAPTURE-TRANSPARENCY-001 already
requires the capture lifecycle to reflect approve/reject decisions; this proposal
makes the `reject_intake` path conform. No new or revised requirement is needed;
no formal spec/governance mutation is in scope.

## Design

Single-site source change plus regression tests, confined to the two authorized
files:

1. `reject_intake` (intake.py, after the rejected-deliberation re-insert ~line
   526): read `confirmed_spec_id = content.get("confirmed_spec_id")`. When it is
   set, the spec exists, and its status is not already `retired`, call
   `db.update_spec(confirmed_spec_id, changed_by=changed_by, change_reason=...,
   status="retired")`. `update_spec` is a partial update that carries forward
   unchanged fields, so only the status changes (append-only new version). The
   guard (`get_spec` present and not already retired) makes the path idempotent
   and safe when the spec is missing.
2. The common case — rejecting a still-`pending` intake (no `confirmed_spec_id`) —
   is unchanged: the `.get` yields `None`, the retirement branch is skipped, and
   reject behaves exactly as today.

Scope note for the reviewer (deliberately out of scope, surfaced for an informed
verdict): when `confirm_intake` ran, `ensure_backlog_for_confirmed_spec` may have
created an auto-backlog work item linked to the now-retired spec (only for
implementation-bearing specs). Retiring that conditional work item is a distinct,
generically-trackable concern (orphaned work item whose source spec is retired)
rather than part of WI-4667's literal "spec stub" scope. This proposal fixes the
spec orphan named in WI-4667 and recommends the work-item residue be tracked as a
sibling follow-on if the reviewer wants the cascade. If the reviewer prefers the
cascade in-scope here, that is a NO-GO with a scope-expansion request.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-SPEC-CAPTURE-TRANSPARENCY-001 (rejecting an auto-confirmed intake retires its SPEC-INTAKE row) | test_reject_intake_retires_confirmed_spec | groundtruth-kb/tests/test_intake.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (rejecting a pending intake with no confirmed spec is a safe no-op) | test_reject_intake_pending_has_no_spec_to_retire | groundtruth-kb/tests/test_intake.py |

Commands run against the changed files before the post-implementation report:

- `python -m pytest groundtruth-kb/tests/test_intake.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py`

## Risk / Rollback

- Risk: retiring a spec that something else still references. Mitigation: the spec
  is a `SPEC-INTAKE-*` stub created by the same intake now being rejected; the
  retirement is the correct lifecycle outcome and uses append-only versioning
  (history preserved). The idempotent guard avoids double-retiring.
- Risk: an intake confirmed then rejected then re-examined. Mitigation: retirement
  is append-only; the deliberation already records `rejected` + `rejection_reason`,
  so the audit trail is complete.
- Rollback: the change is a localized branch in `reject_intake` plus two tests;
  reverting the two files restores prior behavior. No schema or narrative change.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks). WI-4667 is in the active
  PROJECT-BACKLOG-TRIAGE-AND-HYGIENE under
  PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4667-REJECT-RETIRE-SPEC (allowed
  mutation classes source + test_addition; linked spec
  GOV-SPEC-CAPTURE-TRANSPARENCY-001). The proposed target_paths (intake.py + test)
  are within that PAUTH scope. No further owner decision is required to review this
  proposal; the work-item-cascade scope question is a reviewer (LO) call, not an
  owner decision.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
