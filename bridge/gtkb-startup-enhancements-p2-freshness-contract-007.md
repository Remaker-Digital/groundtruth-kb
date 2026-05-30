NEW

# GT-KB Bridge Prime Builder Blocker Note - Startup Enhancements P2 Freshness Contract

bridge_kind: prime_builder_deferral_note
Document: gtkb-startup-enhancements-p2-freshness-contract
Version: 007 (NEW; Prime Builder blocker deferral note)
Responds to NO-GO: bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md
Approved proposal: bridge/gtkb-startup-enhancements-p2-freshness-contract-003.md
Approved GO: bridge/gtkb-startup-enhancements-p2-freshness-contract-004.md
Project Authorization: PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH
Project: PROJECT-GTKB-SESSION-LIFECYCLE-UX
Work Item: GTKB-STARTUP-ENHANCEMENTS
target_paths: []
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 2026-05-27T08-36-48Z-prime-builder-bb3b65
author_model: Claude Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: explanatory output style; cross-harness dispatch worker context
author_metadata_source: auto-dispatch session

## Status Summary

This is a Prime Builder deferral note. No source code is modified by this
bridge version. The post-impl revision required by `-006` NO-GO F1 (cached
startup-service payload reuse violates the dispatcher freshness contract)
could not be authored in this auto-dispatch cycle because a parallel bridge
thread holds an unverified post-implementation report on the same source file.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - startup self-initialization payload freshness; the deferred revision targets this spec.
- `GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001` - proactive startup recovery; degraded fallback observed in `-006` violates this.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` and bridge versioning remain canonical workflow state; this note preserves the audit trail.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic startup-policy surface; no AUQ asked because worker context cannot interact with the owner.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all referenced files are in-root under `E:\GT-KB`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this note carries forward the prior thread's spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - retained for continuity with the deferred revision.
- `GOV-STANDING-BACKLOG-001` - the work remains tied to work item `GTKB-STARTUP-ENHANCEMENTS`.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - bridge note preserves artifact linkage.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - blocker condition documented as a lifecycle trigger for the next dispatch cycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - governed audit trail preserved.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - owner-decision evidence for the active project authorization covering this work item.

## Prior Deliberations

- `bridge/gtkb-startup-enhancements-p2-freshness-contract-006.md` - Loyal Opposition NO-GO on the prior post-implementation report; defined F1 and the required revisions.
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-005.md` - Prior Prime Builder post-implementation report (Codex authorship under previous role assignment).
- `bridge/gtkb-startup-enhancements-p2-freshness-contract-004.md` - Loyal Opposition GO authorizing implementation per the approved proposal at `-003`.
- `bridge/gtkb-startup-refractor-glossary-load-surface-005.md` - Parallel Prime Builder post-implementation report (status NEW) on the same target file `scripts/session_self_initialization.py`; awaiting Loyal Opposition VERIFIED.

## Blocker

Concurrent bridge thread `gtkb-startup-refractor-glossary-load-surface` is in
post-implementation review at version `-005` with status `NEW`. Its declared
`target_paths` include `scripts/session_self_initialization.py` and
`platform_tests/scripts/test_session_self_initialization.py` - the same files
required by the F1 revision on this thread.

The mechanical bridge compliance gate
(`.claude/hooks/bridge-compliance-gate.py` `_pending_proposal_ask_reason`,
lines 788-810) treats any `NEW`, `REVISED`, or `NO-GO` thread declaring a
file in its `target_paths` as a hold against any Edit/Write of that file,
regardless of which thread the active implementation-authorization packet
covers. The cross-harness event-driven trigger that auto-dispatched this
Prime Builder session for the freshness-contract NO-GO has no visibility
into that overlap.

Reproduction in this auto-dispatch session:

1. `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-enhancements-p2-freshness-contract` succeeded; packet is active for the freshness-contract thread (`bridge_id` recorded, `go_file = bridge/gtkb-startup-enhancements-p2-freshness-contract-004.md`).
2. Attempted Edit on `scripts/session_self_initialization.py` (within the GO'd thread's `target_paths`).
3. PreToolUse:Edit hook returned: `[Governance] Bridge proposal for gtkb-startup-refractor-glossary-load-surface is pending Codex review (NEW). Wait for GO verdict before implementing.`

The cited thread (`gtkb-startup-refractor-glossary-load-surface`) is awaiting
VERIFIED, not GO; its source implementation is already on disk. The hook
message is a generic template that conflates "pending review of a NEW
proposal" with "pending VERIFIED on a NEW post-implementation report".

## Deferral Disposition

This thread is deferred until `gtkb-startup-refractor-glossary-load-surface`
reaches a terminal Loyal Opposition verdict (VERIFIED or NO-GO). When that
parallel thread closes, the freshness-contract revision can resume against
a single in-flight set of `target_paths`.

The next dispatch cycle will surface this thread again because the latest
status remains `NO-GO` after this Prime-side note (actionable for Prime
Builder). The next Prime Builder session inheriting this thread should:

1. Confirm `gtkb-startup-refractor-glossary-load-surface` is at VERIFIED (or has been terminated).
2. Re-open the authorization packet: `python scripts/implementation_authorization.py begin --bridge-id gtkb-startup-enhancements-p2-freshness-contract`.
3. Apply the F1 revision per the implementation context in `-006`:
   - Thread `request_started_at`, `harness_name`, and `role_profile` parameters through `_payload_staleness_reasons(...)` and `_is_payload_fresh(...)` in `scripts/session_self_initialization.py`.
   - Add cached-payload metadata fields `harness_name` and `role_profile` in `_startup_freshness_metadata(...)` and `_emit_startup_service_payload(...)`.
   - Pass these from `main(...)` so the cache check rejects payloads whose `request_started_at`, harness, or role profile does not match the current request.
   - Add regression tests covering all three new staleness reasons in `platform_tests/scripts/test_session_self_initialization.py`.
4. Run targeted pytest, `ruff check`/`ruff format --check`, both bridge preflights, and `python .codex/gtkb-hooks/session_start_dispatch.py`; the dispatcher run must no longer emit `Startup Service Degraded`.
5. File the revision as `bridge/gtkb-startup-enhancements-p2-freshness-contract-008.md` (NEW post-implementation report).

## Owner Decisions / Input

None for this deferral note. The owner has already approved the project
authorization (`PAUTH-PROJECT-GTKB-SESSION-LIFECYCLE-UX-SESSION-LIFECYCLE-UX-BATCH`,
`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`) covering the work item
`GTKB-STARTUP-ENHANCEMENTS`. The parallel thread is also within the same
project authorization; coordination is mechanical (which thread's
`target_paths` lock the file first), not authorization-related.

## Process Improvement Opportunity (Backlog Candidate)

The hook conflation surfaced above is a candidate for a separate hygiene
fix. Possible improvements:

- Distinguish `bridge_kind: implementation_report` (post-impl reports awaiting VERIFIED) from `NEW` proposals awaiting GO in `_pending_proposal_ask_reason`. The former should not block edits to other GO'd threads on the same file; the latter should.
- Or: treat the active `current.json` packet's bridge_id as the authoritative writer for the file, with other-thread `target_paths` becoming advisory rather than blocking when the active packet covers the file.
- Or: enforce thread serialization at proposal-filing time by detecting `target_paths` collisions with already-GO'd threads, so two threads on the same file cannot both reach implementation simultaneously.

This is not in scope for this thread. It is logged here for the next session
to consider filing as a separate bridge proposal under the appropriate
project authorization.

## Bridge INDEX Maintenance

A new `NEW: bridge/gtkb-startup-enhancements-p2-freshness-contract-007.md`
row will be inserted at the top of the existing `Document:
gtkb-startup-enhancements-p2-freshness-contract` entry, above the prior
`NO-GO` row at `-006`. Prior versions remain preserved.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
