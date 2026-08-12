REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4d038364-5d9f-45c8-9924-a2caefb50a6f
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; harness B; resolved role prime-builder via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# gtkb-wi6067-shared-envelope-pointer-purge - REVISED: purge scope extended to every pointer reader

bridge_kind: prime_proposal
Document: gtkb-wi6067-shared-envelope-pointer-purge
Version: 003
Author: Prime Builder (claude, harness B)
Date: 2026-08-08 UTC
Responds to: bridge/gtkb-wi6067-shared-envelope-pointer-purge-002.md

Project Authorization: PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808
Project: PROJECT-GTKB-SESSION-ENVELOPE
Work Item: WI-6067

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py", "groundtruth-kb/src/groundtruth_kb/shim_dispatch_telemetry.py", "groundtruth-kb/src/groundtruth_kb/harness_diagnostic.py", "scripts/harness_envelope_equivalence.py", "scripts/session_role_resolution.py", "platform_tests/scripts/test_session_envelope_runtime.py", "platform_tests/scripts/test_gtkb_session_id.py"]

## Response to the `-002` NO-GO

The finding is accepted in full and independently reproduced. The `-001`
invariant — no code writes, reads, or resolves through the shared pointer — was
stated at repository scope while `target_paths` covered only the envelope
open/close path. Four live readers sat outside that scope, so the declared change
could not have established the stated end state.

All four were re-verified at the cited lines before this revision:

| Reader | Verified reference | Nature |
|---|---|---|
| `shim_dispatch_telemetry.py` | `:361`, `:410` — `legacy_document = Path("harness-state") / harness_name / "session-envelope.json"` | fallback when the per-session document is absent |
| `harness_diagnostic.py` | `:65` — `legacy = root / "session-envelope.json"` | legacy candidate |
| `harness_envelope_equivalence.py` | `:124` — `current = harness_dir / "session-envelope.json"`; `:136` archived glob | operative cross-harness equivalence surface |
| `session_role_resolution.py` | `:185` — `envelope_path = project_root / "harness-state" / harness_name / "session-envelope.json"` | operative role-resolution fallback |

The reviewer offered three corrections. **Correction 1 (extend the purge scope)
is taken.** Correction 2 would narrow the invariant and leave the readers in
place, which retains the artifact in a reduced role — the stance the owner
rejected on 2026-08-08 and previously for WI-5964 and DCL v2. Correction 3
(sequencing) is additionally applied within this revision, see § Ordering.

All four readers classify `source` under `classify_target`, which
`PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808` v2 already permits.
No new owner decision is required to widen this scope.

## Summary

Remove the shared per-harness current-envelope pointer from every code path.
After this change no code writes, reads, or resolves through
`harness-state/<harness>/session-envelope.json` or `.claude/session/envelope.json`;
the session envelope resolves from the per-session document keyed by `session_id`,
which is already the authority.

This thread performs no MemBase mutation and no groundtruth.db write; the change
is limited to six source modules and two test modules.

## Pointer Reader Disposition

Each reader is dispositioned explicitly rather than left to a stale read.

1. **`envelope.py`** — `write_current` writes only the per-session document;
   the pointer write, the projection write, and `_write_projection` are removed.
   `load_current` resolves the invoking session id and returns that session's
   document via the existing `load_worker_session`. `current_envelope_path` and
   `projection_path` are removed with their remaining call sites.
2. **`cli_session_handoff.py`** — the `envelope_open_cmd` reuse path needs no
   pointer refresh once the pointer is gone. Its session-id, status, and
   harness-identity validations are unchanged. WI-6055's resolver functions are
   untouched.
3. **`shim_dispatch_telemetry.py`** — the `legacy_document` fallback at `:361`
   and `:410` is removed. Telemetry resolves the per-session document only; when
   that document is absent the existing absent-document behavior applies rather
   than a second lookup against a file that will no longer exist.
4. **`harness_diagnostic.py`** — the legacy candidate at `:65` is removed from
   the candidate set. The diagnostic reports on the per-session document.
5. **`harness_envelope_equivalence.py`** — `current` at `:124` is re-pointed at
   the per-session document for the harness under comparison. The archived glob
   at `:136` is retained but narrowed so it no longer matches a live pointer
   filename; archived envelopes remain in scope for equivalence.
6. **`session_role_resolution.py`** — the legacy transition fallback at `:185`,
   `:210`, and `:237` is removed. Role resolution consults the per-session
   document. This is an operative path, so its regression coverage is named in
   the verification plan below rather than left implicit.

## Ordering

Within this thread the readers are updated **in the same change** as
`write_current` and `load_current`, so no reader is ever left pointing at a
pointer that is no longer maintained. There is no intermediate state in which
writing has stopped but reading continues.

The on-disk artifact deletion remains a separate follow-on tranche, and that
ordering is deliberate: deleting the files while any session still runs the
pre-change code would recreate them. After this change the files are inert —
nothing reads or writes them — which is the precondition the deletion tranche
needs.

## Scope Boundary — Artifact Deletion Still Deferred

This proposal removes the code paths. It does not delete
`harness-state/<harness>/session-envelope.json` or `.claude/session/envelope.json`.
That deletion, and the `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 5
assertions of **absence**, are the follow-on tranche.

The authorization for that tranche now exists:
`PAUTH-PROJECT-GTKB-SESSION-ENVELOPE-WHOLE-PROJECT-20260808` was expanded to v2
on 2026-08-08 adding `runtime_state` and `configuration`, per owner decision
`DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION`. It is held separate
because the transition table does not permit widening a filed thread in place,
and because the sequencing above requires the code purge to land first.

## Root Cause And Observed Failures

`write_current` writes three artifacts: the per-session document (the authority),
the shared pointer, and the shared projection. `load_current` reads the pointer.
`ensure_current` (`envelope.py:996`) calls `load_current` rather than the
session-keyed `load_worker_session` (`:700`), so the fail-closed guard evaluates
the shared artifact instead of the invoking session's own document.

Because the pointer is keyed by harness rather than session, every concurrent
session on one harness addresses the same file and the last writer wins. Two
failure modes follow, both observed live:

1. **Stale-owner.** The pointer names a session that is no longer working and
   every other session fails closed against it. Observed: a pointer naming
   `f9e95f49-…`, whose per-session document was still `status: open` twelve hours
   after `opened_at`, with no live process.
2. **Unrefreshed-reuse.** `envelope_open_cmd` reuses an existing open per-session
   document and returns without calling `write_current`, so the pointer is never
   brought into agreement with the envelope actually in use. Observed
   2026-08-08: pointer mtime `05:38:02Z`, per-session document mtime `05:37:56Z`,
   `envelope open` invoked at approximately `05:57Z` modifying neither, then
   `topic open build` failing against the stale pointer.

Purging removes both at the source rather than repairing each in turn.

## Relationship To Adjacent Carriers

- **WI-5964** owns the DCL v4 path migration relocating the surviving per-session
  document to a context-keyed root. This proposal does not move that document.
- **WI-6055** (implementation report awaiting verification) repaired session-id
  resolution in `_host_session_id`. It remains correct and must not be reverted;
  it is what made the unrefreshed-reuse failure observable.
- **WI-6061** owns the `test_session_envelope_runtime.py` isolation defect.

## Specification Links

- `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` v3 — decision 4 names the per-session
  document as the sole envelope artifact and the Artifact Inventory lists both
  shared artifacts for removal. This executes the code half; decision 2's
  fail-closed comparison is preserved and simply evaluates the correct document.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — every governing
  specification this proposal is constrained by is cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping
  below is carried forward to the implementation report with executed results.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — one authority per concept. The `-002`
  finding was precisely that an incomplete purge leaves a second reader set
  against the same file; this revision closes that gap.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage headers.
- `ADR-CROSS-HARNESS-PARITY-001` — the pointer is per-harness; its removal
  applies uniformly, and `harness_envelope_equivalence.py` is the cross-harness
  surface updated accordingly.
- `GOV-STANDING-BACKLOG-001` — WI-6067 is the tracked carrier.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the rejected refresh design, the owner
  correction, and this scope correction are recorded durably.

## Prior Deliberations

- `DELIB-20260807-PURGE-SHARED-PER-HARNESS-SESSION-ENVELOPE` — owner decision
  that the shared envelope must be purged, not retained in any reduced role.
  This is why correction 2 was not taken.
- `DELIB-20260808-ENVELOPE-PATH-CONTEXT-KEYED-NO-HARNESS` — envelope addressing
  by session-context alone.
- `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION` — the v2 authorization
  expansion enabling the deferred deletion tranche.
- `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION` — the
  authorization under which this work is filed.
- `DELIB-20260806011917` — purge before probative; readers are removed rather
  than annotated as deprecated.
- `DELIB-20260625` — shared-resolver unification, the precedent for collapsing
  multiple resolution paths for one concept onto a single authority.

## Owner Decisions / Input

Collected in session `4d038364-5d9f-45c8-9924-a2caefb50a6f` on 2026-08-08.

1. **Purge, not refresh.** Owner direction in transcript: the pointer is
   obsolete, has no meaning in the current design, and should be purged. This is
   the operative direction for this proposal's design and the reason reviewer
   correction 2 was declined.
2. **Project authorization.** `AskUserQuestion` answer *"Whole-project PAUTH"*,
   recorded as `DELIB-20260808-SESSION-ENVELOPE-WHOLE-PROJECT-AUTHORIZATION`.
3. **Authorization expansion.** `AskUserQuestion` answer *"Expand the existing
   whole-project PAUTH"*, recorded as
   `DELIB-20260808-SESSION-ENVELOPE-PAUTH-CLASS-EXPANSION`, taking the
   authorization to v2 with `runtime_state` and `configuration`.

No new owner decision is requested by this revision. The scope extension uses
`source`, already permitted.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001`
v3 already names the per-session document as the sole envelope artifact and lists
both shared artifacts for removal. This implements existing governance.

## Specification-Derived Verification

The spec-to-test mapping below derives one verification per linked specification.

| Linked specification | Derived verification (spec-to-test) |
|---|---|
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 4 | Repository scan asserts zero remaining source or script readers of the pointer document, discharging the `-002` finding directly. |
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 2 | Assert the fail-closed comparison still rejects a foreign session id, now evaluated against the per-session document. |
| `DCL-SESSION-ENVELOPE-SINGLE-CONTEXT-001` decision 1 | Assert a session resolves its own envelope regardless of what any other session did, covering both observed failure modes. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Assert `load_current` resolves through the per-session document, and that no reader consults a second surface. |
| `ADR-CROSS-HARNESS-PARITY-001` | Assert `harness_envelope_equivalence.py` compares per-session documents across harness trees and still detects a genuine divergence. |
| Operative role-resolution path | Assert `session_role_resolution.py` resolves the same role after the fallback removal as before, for a session with a per-session document. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping plus executed command evidence in the implementation report. |

Commands to be executed and reported in the implementation report:

- `python -m pytest platform_tests/scripts/test_session_envelope_runtime.py -q`
- `python -m pytest platform_tests/scripts/test_gtkb_session_id.py -q`
- Targeted runs for the role-resolution and equivalence surfaces
- `python -m ruff check` and `python -m ruff format --check` on the declared
  Python target paths, as separate gates
- A repository scan for readers of the pointer document, expected to return none
  outside archived-envelope handling
- End-to-end: `session envelope open` followed by `session topic open build` in a
  tree where another session previously wrote the pointer, expected to succeed

`test_session_envelope_runtime.py` currently fails 11 of 42 because those tests
read live repository envelope state rather than an isolated fixture, tracked as
WI-6061. Because this change alters the resolution path those tests exercise, the
implementation report will state before and after counts explicitly and
distinguish failures fixed by this change from failures owned by WI-6061.

## Acceptance Criteria

1. No code path writes `harness-state/<harness>/session-envelope.json` or
   `.claude/session/envelope.json`.
2. No source or script path reads either artifact; a repository scan confirms it.
3. `load_current` resolves the invoking session's per-session document.
4. The fail-closed single-context comparison still rejects a foreign session id.
5. A session whose envelope was reused, and a session in a tree where another
   session wrote the pointer, can both open an activity envelope.
6. Role resolution and cross-harness equivalence behave equivalently after the
   fallback removals.
7. `load_worker_session` and the per-session document format are unchanged.
8. WI-6055's resolver functions are untouched.

## Risk and Rollback

**Risk.** The scope now includes an operative role-resolution path and an
operative cross-harness equivalence surface, so the blast radius is larger than
`-001`. Both are covered by named verifications above rather than assumed safe.
`write_current`'s return value changes from the pointer path to the authoritative
per-session path; the implementation will enumerate callers rather than assume
none exist.

A second risk is that the two artifacts remain on disk, unmaintained, until the
deferred deletion tranche lands. After this change nothing reads them, so they
are inert rather than misleading to code; they remain visibly stale to a human
reader, so the deletion tranche should follow promptly.

**Rollback.** Revert of the declared source and test files. No data migration, no
MemBase mutation, no bridge-state change, and no on-disk artifact is deleted by
this thread.

## Recommended Commit Type

`refactor:` — removes a redundant state surface and re-points resolution at the
existing authority without adding a capability or changing the governing rule.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
