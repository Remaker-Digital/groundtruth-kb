REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e150e9ce-4657-4130-9e10-af48d3e79a44
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude interactive Prime Builder auto-process

# Implementation Proposal (REVISED): WI-4854 extract_target_paths cross-gate consistency (re-homed)

Document: gtkb-wi4854-extract-target-paths-cross-gate-consistency
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds to: bridge/gtkb-wi4854-extract-target-paths-cross-gate-consistency-002.md
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4854
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4854-EXTRACT-TARGET-PATHS-CONSISTENCY

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

## Revision Note

REVISED only to re-home the work item and re-cite its authorization; the scope,
design, and test plan are unchanged from the GO'd `-001`/`-002`. WI-4854 was
originally filed under PROJECT-GTKB-IMPLEMENTATION-START-GATE-HARDENING-001, which
auto-retired (its sibling work items resolved via the concurrent swarm) after
WI-4854 was added and its PAUTH minted — leaving WI-4854 stranded open in a
retired project, so `implementation_authorization.py begin` rejected the original
PAUTH as "not attached to an active project." Per owner AUQ 2026-06-26
(DELIB-20266194), WI-4854 is re-homed to the active PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
with a fresh PAUTH; this REVISED version re-cites the new Project and Project
Authorization so the GO → begin path succeeds.

## Summary

`extract_target_paths()` in `scripts/implementation_authorization.py` is the
reader `implementation_authorization.py begin` uses to derive the authorized-file
set from an approved proposal. It has three accepted forms: an inline
single-line list on the label line (`TARGET_PATHS_RE`), a markdown-heading form
with a fenced JSON list, and a `## Files Expected To Change` bullet section. The
function tries the inline regex first via `search()` and, when that regex matches
but its captured text is not valid JSON, it raises `AuthorizationError`
immediately without falling through to the heading or bullet branches.

This produced two live failures on thread `gtkb-wi4852-watchdog-dormancy-auto-restart`:
a GO'd proposal whose authorized-file list used a non-inline form was rejected by
`begin` ("missing concrete target_paths") even though every pre-GO gate accepted
it; and a later revision whose narrative quoted the label-and-bracket pattern as
prose was matched first and rejected as invalid JSON. The defect class: the
pre-GO gate chain and `begin` disagree on accepted forms, and the reader fails
closed on a leftmost partial match instead of trying all forms — so a proposal
can clear every gate and receive GO, then be un-implementable.

## Specification Links

- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — governs the concrete
  authorized-file linkage that `extract_target_paths` reads; this WI makes the
  reader robust so a compliant proposal is not rejected post-GO.
- GOV-FILE-BRIDGE-AUTHORITY-001 — bridge artifact under `bridge/`; bridge
  authority and GO/NO-GO discipline apply.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — the verification plan maps
  each behavioral clause to an executed test before VERIFIED.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — both touched paths are GT-KB platform
  source/tests in-root under `E:\GT-KB`; no out-of-root dependency.
- GOV-STANDING-BACKLOG-001 — WI-4854 is the canonical backlog record for this
  work; no bulk backlog operation is performed.
- GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 — the fix is enforced
  by spec-derived unit tests over the pure reader function.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — advisory; durable code + test artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — advisory; adds code + tests and advances
  WI-4854 toward verified.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — advisory; work item + owner decision +
  spec linkage preserved as durable artifacts.

## Prior Deliberations

- DELIB-20266194 (owner_conversation / owner_decision) — owner AUQ 2026-06-26
  authorizing the NEW-implementation-proposal generation loop and (in follow-up)
  the re-home of WI-4854 to an active project; basis for the re-homed PAUTH.
- bridge/gtkb-wi4852-watchdog-dormancy-auto-restart-001.md / -003.md / -005.md /
  -006.md — the live evidence of the two failure modes this WI fixes.
- WI-4833 (resolved) — earlier `extract_target_paths` fenced-heading parse fix;
  this WI hardens the same reader against the fail-closed-on-first-match class.
- WI-3268 — pre-filing mechanical lints; a pre-filing `extract_target_paths`
  check is a candidate surface there.
- No prior deliberation rejects making the reader try all forms before failing.

## Requirement Sufficiency

Existing requirements sufficient. DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
already requires concrete authorized-file linkage; this WI corrects the reader so
a compliant proposal is parsed rather than rejected. No new or revised
requirement is needed; no formal spec/governance mutation is in scope.

## Design

Single behavioral change plus tests, confined to the two authorized files:

1. `extract_target_paths()` (in `scripts/implementation_authorization.py`):
   restructure so it collects candidate results from ALL three forms (inline
   regex, markdown-heading fenced JSON, `Files Expected To Change` bullets) and
   returns the first form that yields a non-empty list of valid path strings. A
   form that matches structurally but fails its content validation (e.g., an
   inline regex hit whose capture is not valid JSON, such as a prose placeholder)
   is treated as "no result from this form" and the function continues to the
   next form. `AuthorizationError` is raised only when NO form yields a valid
   non-empty list. Path normalization (`strip()` + backslash-to-forward-slash)
   is unchanged.

2. Preserve current success behavior exactly: a valid inline list, a valid
   heading-fenced list, and a valid bullet section all still return the same
   normalized paths as today. Only the failure path changes (fall-through instead
   of immediate raise on a leftmost partial match).

Out of scope (noted for the reviewer): aligning the pre-GO preflight/compliance
gates to validate authorized-file form with this same reader is a follow-on
hardening (a pre-filing lint, candidate under WI-3268); this WI fixes the reader
itself so the post-GO dead-end cannot occur.

## Test Plan (spec-to-test mapping)

| Specification clause | Test | File |
|---|---|---|
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (valid inline list parses) | test_extract_target_paths_inline_single_line | platform_tests/scripts/test_implementation_authorization.py |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (valid heading-fenced list parses) | test_extract_target_paths_heading_fenced | platform_tests/scripts/test_implementation_authorization.py |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (leftmost invalid inline falls through to a valid heading form) | test_extract_target_paths_falls_through_invalid_inline_to_heading | platform_tests/scripts/test_implementation_authorization.py |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (Files Expected To Change bullet section parses) | test_extract_target_paths_files_expected_section | platform_tests/scripts/test_implementation_authorization.py |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (raise only when no form yields a valid list) | test_extract_target_paths_raises_when_no_valid_form | platform_tests/scripts/test_implementation_authorization.py |

Commands (run against changed files before the post-implementation report):

```text
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
python -m ruff format --check scripts/implementation_authorization.py platform_tests/scripts/test_implementation_authorization.py
```

## Risk / Rollback

- Risk: the restructure changes a success path. Mitigation: the test plan pins
  all three success forms plus the fall-through and the no-valid-form raise; the
  change is to the failure branch only.
- Risk: a genuinely malformed authorized-file list now raises a less specific
  error. Mitigation: keep a clear `AuthorizationError` message enumerating the
  forms tried when none succeed.
- Rollback: the change is confined to one function and its tests; reverting the
  two files restores prior behavior. No schema, governed-record, or narrative
  change is involved.

## Bridge Filing Discipline

This revision is filed as the next numbered bridge file
(`bridge/gtkb-wi4854-extract-target-paths-cross-gate-consistency-003.md`) under
the canonical append-only numbered-file chain. Prior versioned bridge files
(`-001` NEW, `-002` GO) are never rewritten or deleted; this REVISED version is
added as a new numbered file so the numbered file chain remains the canonical
audit trail per GOV-FILE-BRIDGE-AUTHORITY-001.

## Owner Decisions / Input

- DELIB-20266194 — owner AUQ (2026-06-26) authorized the NEW-implementation-proposal
  generation loop and, in follow-up, directed re-homing WI-4854 to an active
  project (the original project auto-retired). This REVISED version re-cites the
  active PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY and its PAUTH
  (PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4854-EXTRACT-TARGET-PATHS-CONSISTENCY;
  allowed mutation classes source + test_addition; linked spec
  DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001). No further owner
  decision is required to re-review this REVISED proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
