NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8f2455b1-c515-479c-b544-720ce8ef2471
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal: WI-4665 propagate intake raw_text into the confirmed spec description

Document: gtkb-wi4665-intake-confirm-description-from-raw-text
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-4665
Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4665-INTAKE-DESCRIPTION

target_paths: ["groundtruth-kb/src/groundtruth_kb/intake.py", "groundtruth-kb/tests/test_intake.py"]

## Summary

`confirm_intake` (groundtruth-kb/src/groundtruth_kb/intake.py, ~line 378) creates a
`SPEC-INTAKE-*` specification row from a captured requirement candidate but does
not pass a `description` to `insert_spec` (the call at ~line 418 passes id, title,
status, section, scope, type, authority, provisional_until — no description). So
the confirmed spec's description is left NULL. The captured requirement body is
already available: `capture_requirement` stores the full text in the linked
`INTAKE-*` deliberation's content JSON as `raw_text` (intake.py line 346). The fix
threads `content.get("raw_text")` into the `insert_spec` call so the confirmed spec
carries the captured body. This restores the GOV-SPEC-CAPTURE-TRANSPARENCY-001
contract that the captured spec present the full owner text, not just the heading.

## Specification Links

- GOV-SPEC-CAPTURE-TRANSPARENCY-001 — "surface every capture event + present full
  text on approve/reject." The NULL description violates this: the confirmed spec
  carries the title but not the substance. This proposal restores the full-text
  contract at confirm time. (governing)
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; append-only
  numbered-file chain and GO/NO-GO discipline apply.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — this proposal cites
  every relevant governing specification.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps the
  behavioral clause (non-null description equal to the captured raw_text) to an
  executed test.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  package source/tests in-root; no out-of-root dependency.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the fix is enforced
  by a spec-derived regression test.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + test, advances
  WI-4665 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop over the whole
  backlog (PB picks); basis for the covering PAUTH.
- WI-4665 description cites the S447 concrete repro (INTAKE-702b8ea6 captured
  ~800 chars; the resulting SPEC-INTAKE-a3cdef row has description=NULL).
- No prior deliberation rejects propagating the captured text into the spec body;
  the sibling `core_spec_intake.py` path already sets `description` at insert time
  (intake-side parity), so this aligns the `confirm_intake` path with established
  behavior.

## Requirement Sufficiency

Existing requirements sufficient. GOV-SPEC-CAPTURE-TRANSPARENCY-001 already
mandates presenting the full captured text; this proposal makes the
`confirm_intake` path conform. No new or revised requirement is needed; no formal
spec/governance mutation is in scope.

## Design

Single-site source change plus a regression test, confined to the two authorized
files:

1. `confirm_intake` (intake.py, the `insert_spec` call ~line 418): add
   `description=content.get("raw_text")` to the keyword arguments. `raw_text` is
   the full captured requirement body stored by `capture_requirement` (line 346).
   When `raw_text` is absent (legacy/hand-built deliberations), `.get` yields
   `None`, preserving today's behavior for those rows (no regression).
   `insert_spec` already accepts a `description` keyword (the sibling
   `core_spec_intake.py` path uses it), so no signature change is required.
2. No change to `capture_requirement`, the content schema, the rejection path, or
   any other call site. The fix is localized to the confirm-time insert.

Out of scope (noted for the reviewer): retiring the pre-existing S447 orphan stub
`SPEC-INTAKE-a3cdef` is historical-evidence cleanup, not part of this forward fix
(the WI acceptance leaves it as evidence). Sibling intake defects WI-4666
(`gt intake list` status mismatch) and WI-4667 (reject does not retire the stub)
are separate threads.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| GOV-SPEC-CAPTURE-TRANSPARENCY-001 (confirmed spec description is non-null and equals the captured raw_text) | test_confirm_intake_populates_description_from_raw_text | groundtruth-kb/tests/test_intake.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (regression guards the raw_text to description propagation) | test_confirm_intake_populates_description_from_raw_text | groundtruth-kb/tests/test_intake.py |

Commands run against the changed files before the post-implementation report:

- `python -m pytest groundtruth-kb/tests/test_intake.py -q --tb=short`
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py`
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/intake.py groundtruth-kb/tests/test_intake.py`

## Risk / Rollback

- Risk: a deliberation row without `raw_text` (legacy/hand-built) — `.get` yields
  `None`, so the confirmed spec description stays NULL exactly as today (no new
  failure mode). Mitigation: the test covers the populated path; the `.get`
  default preserves the legacy path.
- Risk: the confirm path feeds `score_spec_quality`. Mitigation: the change only
  adds a description value; a richer description can only improve, not break,
  quality scoring (which reads the created spec after insert).
- Rollback: the change is a single added keyword argument plus one test; reverting
  the two files restores prior behavior. No schema, governed-record, or narrative
  change is involved.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop over the whole backlog (PB picks). WI-4665 is in the active
  PROJECT-BACKLOG-TRIAGE-AND-HYGIENE under
  PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-4665-INTAKE-DESCRIPTION (allowed
  mutation classes source + test_addition; linked spec
  GOV-SPEC-CAPTURE-TRANSPARENCY-001). The proposed target_paths (intake.py + test)
  are within that PAUTH scope. No further owner decision is required to review this
  proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
