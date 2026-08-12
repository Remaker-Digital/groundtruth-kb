NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4d038364-5d9f-45c8-9924-a2caefb50a6f
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; harness B; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# gtkb-wi6067-shared-envelope-pointer-purge - stop writing and reading the shared current-envelope pointer

bridge_kind: prime_proposal
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 001
Author: Prime Builder (claude, harness B)
Date: 2026-08-08 UTC

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6067

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_gtkb_session_id.py"]

## Summary

Remove the shared per-harness current-envelope pointer from the code path. After
this change no code writes, reads, or resolves through
`harness-state/<harness>/session-envelope.json` or `.claude/session/envelope.json`;
the session envelope is resolved from the per-session document keyed by
`session_id`, which is already the authority.

This thread performs no MemBase mutation and no groundtruth.db write; the change
is limited to two source modules and two test modules.

## Scope Boundary — Code Purge Only, Stated Up Front

This proposal removes the **code paths**. It does **not** delete the on-disk
artifacts, because they classify outside the controlling authorization:

| Path | `classify_target` mutation class | In PAUTH `allowed_mutation_classes`? |
|---|---|---|
| `harness-state/<harness>/session-envelope.json` | `runtime_state` | no |
| `.claude/session/envelope.json` | `configuration` | no |

`PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808` carries `source`,
`test`, `documentation`, `governance_evidence`, `metadata`, `bridge`. Adding
`runtime_state` and `configuration` widens the classes the owner approved, which
is an expansion rather than the correction of an authoring defect, and therefore
belongs to the owner. The artifact deletion and the `absence` assertions that
`DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 5 requires are consequently
**deferred to a follow-on tranche** gated on that expansion.

Sequencing also favors this split on its own merits: deleting the files while any
session still runs the current code would simply recreate them. The code purge
must land first regardless.

## Why This And Not A Pointer Refresh

The originally drafted remedy for WI-6067 was to refresh the pointer on the
`envelope_open_cmd` reuse path. The owner rejected that on 2026-08-08 with the
direction that the pointer is obsolete, has no meaning in the current design, and
should be purged. Refreshing retains the artifact in a reduced role, which is the
stance already rejected for WI-5964 and for DCL v2 under
`DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE`. That draft was
discarded before filing.

## Root Cause And Current Behavior

`write_current` writes three artifacts: the per-session document (the authority),
the shared pointer, and the shared projection. `load_current` reads the shared
pointer. `ensure_current` calls `load_current` and hands the result to
`_assert_fail_closed_single_context`, so the guard evaluates the pointer rather
than the invoking session's own document.

Because the pointer is keyed by harness rather than by session, every concurrent
session on one harness addresses the same file and the last writer wins. Two
distinct failure modes follow from that single fact, both observed live:

1. **Stale-owner failure.** The pointer names a session that is no longer
   working, and every other session fails closed against it. Observed: a pointer
   naming `f9e95f49-…`, whose per-session document was still `status: open`
   twelve hours after `opened_at` with no live process.
2. **Unrefreshed-reuse failure.** `envelope_open_cmd` reuses an existing open
   per-session document and returns without calling `write_current`, so the
   pointer is never brought into agreement with the envelope actually in use.
   Observed 2026-08-08: pointer mtime `05:38:02Z`, per-session document mtime
   `05:37:56Z`, `envelope open` invoked at approximately `05:57Z` and modified
   neither, then `topic open build` failed against the stale pointer.

Purging the pointer removes both failure modes at the source rather than
repairing each in turn.

## Proposed Change

1. **`write_current`** — write only the per-session document. Remove the pointer
   write and the projection write. Return the authoritative per-session path.
   Callers depending on the previous return value are updated.
2. **`_write_projection`** — removed, with its call sites.
3. **`load_current`** — resolve the invoking session id through the canonical
   resolver and return that session's per-session document via the existing
   `load_worker_session`, which already reads the authority directly.
4. **Residual call sites** — the remaining `current_envelope_path` /
   `projection_path` references in `envelope.py` are removed with their helpers.
5. **`cli_session_handoff.py`** — the `envelope_open_cmd` reuse path no longer
   needs a pointer refresh once the pointer is gone; its existing session-id,
   status, and harness-identity validations are unchanged.

`load_worker_session`, `worker_session_envelope_path`, and the per-session
document format are unchanged. The fail-closed single-context comparison in
decision 2 is unchanged in force; it simply evaluates the correct document.

## Relationship To Adjacent Carriers

- **WI-5964** owns the DCL v4 path migration relocating the surviving per-session
  document to a context-keyed root. This proposal does not move that document;
  the two carriers do not overlap.
- **WI-6055** (implementation report awaiting verification) repaired session-id
  resolution in `_host_session_id`. This proposal does not modify
  `_host_session_id`, `_canonical_session_id`, `_valid_turn_metadata`, or
  `_required_turn_metadata`. WI-6055 remains correct and must not be reverted;
  it is what made the unrefreshed-reuse failure observable.
- The deferred artifact deletion plus decision-5 absence assertions are the
  follow-on tranche described under § Scope Boundary.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v3 — decision 4 names the per-session
  document as the sole envelope artifact, and the Artifact Inventory already
  lists both shared artifacts for removal. This proposal executes the code half
  of that inventory; decision 2's fail-closed comparison is preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  every governing specification it is constrained by.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the
  Specification-Derived Verification section maps each linked specification to a
  derived verification, carried forward to the implementation report.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — one authority per concept; a shared
  pointer that can disagree with the document it names is the drift class removed
  here.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage headers.
- `ADR-CROSS-HARNESS-PARITY-001` — the pointer is per-harness; its removal
  applies uniformly to every harness tree.
- `GOV-STANDING-BACKLOG-001` — WI-6067 is the tracked carrier.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the rejected refresh design and the
  owner correction are recorded durably rather than silently replaced.

## Prior Deliberations

- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE` — owner decision
  that the shared per-harness envelope must be purged and not retained in any
  reduced role. This proposal is the code half of that purge.
- `DELIB-20260808-ENVELOPE-PATH-CONTEXT-KEYED-NO-HARNESS` — owner decision that
  envelope addressing is by session-context alone.
- `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION` — the
  authorization under which this work is filed.
- `DELIB-20260806011917` — purge before probative; the pointer is deleted rather
  than annotated as deprecated.
- `DELIB-20260625` — shared-resolver unification, the precedent for collapsing
  two resolution paths for one concept onto a single authority.


### Helper-suggested candidates

<!-- Pre-populated by helper; review and prune. -->
- DA: `DELIB-202667166` — seed=search; bridge_thread; NO-GO — WI-5445 Active/Template Hook Fail-Closed Parity
- DA: `DELIB-20260808-CURRENT-ENVELOPE-OBSOLETE-DESIGN` — seed=search; owner_conversation; Owner ruling: the shared current session-envelope concept is meaningless and is 
- DA: `DELIB-20262117` — seed=search; bridge_thread; Bridge thread: gtkb-dispatch-envelope-adr-specs (1 versions, ORPHAN)
- DA: `DELIB-20260621-EXPLICIT-HINT-CONTEXT-LOAD-REFRAME` — seed=search; owner_conversation; Explicit-Hint ::open Activity Layer as a Context-Management Mechanism (4-class c
- DA: `DELIB-20265650` — seed=search; bridge_thread; Verdict

## Owner Decisions / Input

Collected in session `4d038364-5d9f-45c8-9924-a2caefb50a6f` on 2026-08-08.

1. **Purge, not refresh.** Owner direction in the transcript: the pointer is
   obsolete, has no meaning in the current design, and should be purged. This
   superseded the drafted refresh remedy before it was filed, and is the
   operative direction for this proposal's design.
2. **Project authorization.** `AskUserQuestion` answer *"Whole-project PAUTH"*,
   recorded as `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION` and
   issued as the authorization cited in this header, which covers WI-6067 as an
   active project member.
3. **Unblock route.** `AskUserQuestion` answer *"Fix WI-6055 first, no
   exception"*, directing repair of the envelope machinery over a
   governance-emergency-bootstrap exception. This proposal continues that route.

No new owner decision is requested by this proposal. The mutation-class
expansion required for the deferred artifact deletion is raised separately and
does not gate this filing.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001`
v3 already names the per-session document as the sole envelope artifact and lists
both shared artifacts for removal. This proposal implements existing governance;
it introduces no new requirement.

## Specification-Derived Verification

The spec-to-test mapping below derives one verification per linked specification.

| Linked specification | Derived verification (spec-to-test) |
|---|---|
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 4 | Assert `write_current` writes the per-session document and no other envelope artifact; assert no code path references the removed helpers. |
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 2 | Assert the fail-closed comparison still rejects a foreign session id, now evaluated against the per-session document. |
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 1 | Assert a session resolves its own envelope regardless of what any other session did, covering both observed failure modes. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Assert `load_current` resolves through the per-session document rather than a shared file. |
| `ADR-CROSS-HARNESS-PARITY-001` | Assert the behavior holds for a mapped harness and an unmapped one. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus executed command evidence in the implementation report. |

Commands to be executed and reported in the implementation report:

- `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py -q`
- `python -m pytest platform_tests/scripts/test_gtkb_session_id.py -q`
- `python -m ruff check` and `python -m ruff format --check` on the declared
  Python target paths, as separate gates
- End-to-end: `session envelope open` followed by `session topic open build` in a
  tree where another session previously wrote the pointer, expected to succeed.

`test_session_envelope_runtime.py` currently fails 11 of 42 for reasons unrelated
to this change: those tests read live repository envelope state rather than an
isolated fixture, which is tracked as WI-6061. Because this proposal changes the
resolution path those tests exercise, the implementation report will state the
before and after counts explicitly rather than reporting a bare pass, and will
distinguish failures fixed by this change from failures owned by WI-6061.

## Acceptance Criteria

1. No code path writes `harness-state/<harness>/session-envelope.json` or
   `.claude/session/envelope.json`.
2. `load_current` resolves the invoking session's per-session document.
3. The fail-closed single-context comparison still rejects a foreign session id.
4. A session whose envelope was reused, and a session in a tree where another
   session wrote the pointer, can both open an activity envelope.
5. `load_worker_session` and the per-session document format are unchanged.
6. WI-6055's resolver functions are untouched.

## Risk and Rollback

**Risk.** `write_current`'s return value changes from the pointer path to the
authoritative per-session path; any caller reading that return value must be
updated, and the implementation will enumerate them rather than assume none
exist. A second risk is that the two on-disk artifacts remain present but
unmaintained until the deferred deletion tranche lands; they are inert after this
change because nothing reads them, but they are visibly stale on disk, so the
deferred tranche should follow promptly.

**Rollback.** Revert of the declared source and test files. No data migration, no
MemBase mutation, no bridge-state change, and no on-disk artifact is deleted by
this thread.

## Recommended Commit Type

`refactor:` — removes a redundant state surface and re-points resolution at the
existing authority without adding a capability or changing the governing rule.

---

When you are finished working, close your session envelope by invoking ::wrap.
