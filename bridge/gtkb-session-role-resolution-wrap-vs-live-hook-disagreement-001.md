ADVISORY

# Advisory: Session-Envelope role_resolved Disagrees With Live Hook/Claim-CLI Role Resolution For the Same Session, Including After ::wrap

bridge_kind: governance_advisory
Document: gtkb-session-role-resolution-wrap-vs-live-hook-disagreement
Version: 001
Author: Loyal Opposition (Claude Code, harness B)
Date: 2026-07-18 UTC

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: b7c2c4c5-cdc9-4509-9689-cbcef8014f8f
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: interactive session; resolved role loyal-opposition via dispatcher/default registry per this session's own live tool behavior throughout; the session-envelope wrap snapshot separately reports prime-builder -- see Claim section for the discrepancy this document documents

implementation_scope: none (advisory / defect-diagnosis only; no code, test, or KB mutation proposed or performed by this document)
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Source

Discovered at the end of this same session, at the owner's `::wrap` trigger, when `gt session wrap --harness-name claude --harness-id B --json` reported this session's envelope `role_resolved` as `prime-builder` -- a result that contradicts how every live role-gated mechanism in this session actually behaved for the session's entire duration. Filed at the owner's explicit direction, given in this session in response to a direct question offering this as one of three options once the contradiction was reported in chat.

## Claim

For one continuous interactive session (`session_id: c57a453e-dccb-4ca1-afb7-1d23dfa8444a`), the end-of-session envelope snapshot and the live, in-session role-gated enforcement mechanisms disagree about which role that session held, and the disagreement was still reproducible after the formal `::wrap` close, not merely a transient startup race.

### Evidence

- `gt session wrap --harness-name claude --harness-id B --json`, run at the owner's `::wrap` trigger, reported: `init_keyword: "::init gtkb pb"`, `role_resolution.interactive_role_source: "transcript_init_keyword"`, `role_resolution.interactive_resolved_role: "prime-builder"`, `role_resolved: "prime-builder"`, and explicitly `role_resolution.durable_registry_authority: "headless dispatch routing and interactive fallback only; non-overriding when a transcript-defined interactive role is present"`. By the project's own stated precedence rule, this should mean the session was prime-builder throughout for all in-session surfaces.
- `python scripts/bridge_claim_cli.py claim <slug>`, run three separate times across this session -- twice before `::wrap` (at approximately 16:35 and 16:52 UTC) and once again after `::wrap` had already closed and archived the envelope (17:45:47 UTC, three minutes after the envelope archive timestamp 17:42:24Z) -- returned `"acting_role": "loyal-opposition"` all three times, for the same `session_id` the wrap output later attributed to prime-builder.
- `.claude/hooks/lo-file-safety-gate.py`'s `_is_lo_enforced()` actively blocked a `Write` to a non-allowlisted path during this session with `BLOCKED (GTKB-LO-FILE-SAFETY)`. That function's own docstring states it is "driven only by explicit interactive session authority" and explicitly returns `False` (not enforced) whenever its underlying `resolve_interactive_session_role()` call reports a durable-fallback outcome (`if str(_outcome).startswith("durable_"): return False`, `lo-file-safety-gate.py:299-301`) rather than a genuine session-specific marker resolution. For this hook to have blocked the write at all, its call to `resolve_interactive_session_role()` must have resolved something other than a fresh, genuine "prime-builder" marker for this session at that moment -- directly at odds with the wrap-time report of `interactive_role_source: transcript_init_keyword` / role `prime-builder` for the same session.
- No direct Read/Grep/Glob evidence of an `::init gtkb pb` (or any `::init`) message appearing anywhere in this session's visible conversation history was available to this reviewing context; the wrap output is the first and only place in this session where that init keyword surfaced. Whether the keyword was genuinely sent earlier and fell out of visible context through compaction, or the wrap-time envelope record itself is inaccurate, was not determined in this review.

### Why this matters

This session operated under the loyal-opposition governance contract for its entire duration -- default wrap-up behavior, file-safety restrictions, advisory-only disposition of findings, deference to Prime Builder for implementation -- based on the durable registry default, because that was the only role signal genuinely visible to the reviewing context and because every live mechanism touched during the session agreed with it. If the wrap-time report is correct that the session was actually prime-builder throughout, then the session was governed under the wrong behavioral contract for its full duration without any live signal available to catch the mismatch -- a defect in the role-resolution surface itself, not a mistake correctable by more careful reading within the session, since the correct signal was not consistently exposed to begin with. If instead the wrap-time report is the inaccurate one, then the deterministic wrap service that generates the canonical handoff prompt and closes the session envelope is recording an incorrect resolved role into the persisted, archived record that future sessions and audits will treat as authoritative. Either direction is a governance-integrity concern: `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` exist specifically to make this resolution deterministic and unambiguous, and this session produced two internally-inconsistent authoritative-looking answers to "what role was this session" from two different canonical surfaces.

## Owner Decision Needed

1. Should Prime Builder's investigation start from the live-hook side (why did `resolve_interactive_session_role()`, as called from `lo-file-safety-gate.py` and from `bridge_claim_cli.py`'s acting_role resolution, apparently reach a durable-fallback-shaped outcome across this entire session and even after `::wrap`, if a genuine prime-builder session marker existed) or from the wrap-service side (why does `gt session wrap` report `interactive_role_source: transcript_init_keyword` if no such marker was actually available to the live resolvers)? These point at different code paths and probably need to be reconciled rather than picked exclusively, but the starting point affects sequencing.
2. Is this the same underlying defect class as `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` / `-003.md` (tracked as its own future work item per that thread's Prime Builder disposition), meriting folding into that same work item, or is the live-vs-wrap-snapshot disagreement documented here different enough (a different pair of surfaces disagreeing, not one document self-contradicting) to warrant its own work item alongside it?
3. Given this session's actual governed conduct was loyal-opposition-shaped throughout (investigation, evidence-based advisories, no direct implementation or work-item authoring, deference to owner-grilling before any implementation proposal), do you want that work re-validated or re-framed now that the wrap output claims prime-builder was the intended role for this session, or does the loyal-opposition framing stand as-delivered regardless of which role label was technically correct?
4. Should a lightweight, cheap fail-loud check be added at session end (or continuously) that compares `role_resolved` from the envelope against a fresh live call to `resolve_interactive_session_role()` for the same session, and surfaces a hard, visible warning on any mismatch, rather than requiring an owner or reviewer to notice the discrepancy by hand as happened in this session?

These questions remain open pending a dedicated `AskUserQuestion` pass; per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` they must be resolved before any implementation proposal derived from this advisory is drafted.

## Recommended Prime Action

1. Run the four Owner Decision Needed questions above via `AskUserQuestion` (one at a time) before drafting any implementation proposal.
2. Before scoping new work, read the full `-002` and `-003` versions of `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-*.md` (this document only read `-002` in full and the first lines of `-003`) to determine precisely how much this finding overlaps with the work item that thread's disposition already committed to tracking separately, per Owner Decision Needed item 2.
3. If treated as its own work item, the highest-value first regression test is narrow and cheap: for a session with a written, valid, non-stale prime-builder session marker, assert that `resolve_interactive_session_role()` (as called from both `lo-file-safety-gate.py` and `bridge_claim_cli.py`) returns a non-durable-fallback outcome resolving to prime-builder, and that `gt session wrap` for the same session/harness reports a consistent `role_resolved`. This tests the reconciliation directly rather than requiring a full live two-session repro.
4. This document's own header intentionally does not claim a definitively "correct" role for this session (see `author_model_configuration` above) because that is exactly the open question; Prime Builder should not treat either this document's `loyal-opposition` framing or the wrap output's `prime-builder` framing as settled without further investigation.

## Classification Slot

adapt. The disagreement between two canonical-looking role signals for one session is directly evidenced, not speculative -- not a reject. It is not waiting on any external milestone, so not a pure defer. It reflects a governance-integrity gap in the core role-resolution surface that already caused this session to operate under a contract that may not match its intended role, so monitor alone is insufficient. It is not implementation-ready -- the root cause is not yet isolated to one code path, and Owner Decision Needed item 2 (fold into the existing tracked work item versus separate) is a real, undecided fork -- so full adopt is premature. Adapt is the correct slot: the direction (role resolution must be made a single, live-checked, unambiguous signal, and its consumers must agree) is clear, but the exact fix and its relationship to the already-tracked sibling work await the owner-grilling answers above.

## Specification Links

- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` (governs this document's Owner Decision Needed / Recommended Prime Action structure).
- `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` (the specifications this defect report concerns directly -- the deterministic role-resolution contract this session's own evidence shows was not honored consistently).
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` (the persistence-across-compaction rule directly relevant to the "did an earlier ::init fall out of visible context" open question in the Evidence section).

## Prior Deliberations

`gt deliberations search` run for this topic (query: session envelope role resolved wrap live hook contradiction prime-builder loyal-opposition) returned only weakly-related verdict records (durable role assignment review, harness role portability review, an unrelated claim record) with no exact match on this specific wrap-versus-live-hook disagreement.

Closely related, and read in this review before drafting, not a duplicate: `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` (VERIFIED status not confirmed by this review; a same-session envelope read there showed two fields of the SAME snapshot self-contradicting -- `interactive_role_source: transcript_init_keyword` claiming a transcript source while `worker_role_provenance.role_resolution_source: session_resolver_fallback` claimed a fallback, both describing the same session at the same instant) and its `-003` Prime Builder disposition (Codex, harness A, 2026-07-16), which committed to tracking that finding as its own future work item, separate from WI-5328, without yet creating that work item as of the disposition's filing. This document's finding is a different failure signature on the same general subsystem: not one snapshot self-contradicting, but the wrap-time snapshot disagreeing with independently-observed live hook and CLI behavior across the whole session, including after the session had already been formally closed by `::wrap`. Prime Builder should determine, per Owner Decision Needed item 2, whether these belong in the same work item.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

This advisory does not itself depend on new owner approval to be filed -- advisory capture is not implementation approval. The owner explicitly directed, in this same session, that this specific contradiction be filed as its own advisory (selected from three offered options after the discrepancy was first reported in chat at the `::wrap` trigger). The Owner Decision Needed questions above remain open pending a dedicated `AskUserQuestion` pass before any implementation proposal is drafted.

## Non-Approval Statement

This ADVISORY entry is not implementation approval. It does not authorize any code change, does not bypass the bridge, project-authorization, owner-decision, root-boundary, credential-safety, formal-artifact, or verification gates, and does not itself constitute a work item until formally registered in MemBase.

## Methodology Trail

- The triggering evidence (`role_resolved: prime-builder`) came directly from this session's own `gt session wrap --harness-name claude --harness-id B --json` invocation at the owner's literal `::wrap` message, not from inference or a cached report.
- Cross-checked against three independent live data points from earlier in the same session: two `bridge_claim_cli.py claim` responses (16:35 and 16:52 UTC) and one additional claim response run deliberately after `::wrap` had already closed the envelope (17:45:47 UTC) to test whether the disagreement was merely a pre-wrap race condition; all three returned `acting_role: loyal-opposition`.
- Read `.claude/hooks/lo-file-safety-gate.py`'s `_is_lo_enforced()` and `_is_durable_lo_enforced()` in full to confirm that hook's own design intent (durable-fallback outcomes should NOT enforce Loyal Opposition restrictions) and that its observed live behavior (it DID enforce them) is therefore inconsistent with a genuine prime-builder marker having been resolved for this session at hook-run time.
- Read `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-002.md` in full and the opening of `-003` to confirm this is a related-but-distinct finding rather than a duplicate, and to correctly cite that thread's own disposition state.
- Ran `gt deliberations search` once for this topic before drafting -- see Prior Deliberations.

Skills applied: bridge, codex-report, advisory-proposal

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
