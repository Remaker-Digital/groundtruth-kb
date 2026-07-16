NEW

# Advisory: Role-gated hooks (GTKB-LO-FILE-SAFETY et al.) trust a single static session-envelope file with no live cross-check or self-healing

bridge_kind: governance_review
Document: gtkb-role-gated-hook-envelope-fragility-advisory
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive session; session-stated Prime Builder role via literal ::init gtkb pb opening message; explanatory output style

Intended follow-on work item: WI-5336 (registration pending -- groundtruth.db is currently protected by a concurrent post-implementation-report review for bridge/gtkb-wi5211-df-governed-verdict-publication-parity-007.md; the DB-mutation implementation-start gate correctly refused a new work_items insert attempted during this filing. This document preserves the finding until that DB-mutation window reopens.)

implementation_scope: none (advisory / design-critique only; no code, test, or KB mutation proposed or performed by this document)
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Author Role-Provenance Disclosure (read before review)

Same live defect as the sibling proposals filed this session (`gtkb-wi5328-session-envelope-role-writeback`, `gtkb-wi5330-spec-link-heading-hyphen-false-positive`): this session''s envelope resolves `role_resolved: "loyal-opposition"` despite the literal `::init gtkb pb` opening message. The owner has explicitly confirmed the session-stated role is authoritative and directed proceeding with filing despite the inconsistency.

## Standing Directive This Advisory Satisfies

Owner directive, this session''s transcript, verbatim: "When you find an error, flaw or opportunity for enhancement, you must not allow that to be forgotten. The correct response is *always* to file an Advisory Proposal." This document is that filing, for the specific finding described below.

## Finding

Distinct from WI-5328 (which fixes the missing envelope role write-back call). This finding is architectural, and survives WI-5328 landing: `GTKB-LO-FILE-SAFETY`, and by extension any other role-gated `PreToolUse` hook that consults `.claude/session/envelope.json`, currently trusts that single static file unconditionally -- with no live cross-check against the actual session transcript/context, and no self-healing or fail-loud behavior when the file is stale or internally inconsistent.

### Live evidence (this session, 2026-07-16)

A freshly-opened session (`session_id: ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2`, literal opening message `::init gtkb pb`) produced an envelope containing an internally CONTRADICTORY record:

```
"role_resolution": { "interactive_role_source": "transcript_init_keyword" },   <- claims transcript-sourced
"worker_role_provenance": { "role_resolution_source": "session_resolver_fallback" }  <- but actually fell back
```

Both fields describe the SAME session_id at the SAME point in time, and directly contradict each other. `GTKB-LO-FILE-SAFETY` nonetheless accepted this record at face value and used it to block routine Prime Builder `Write`/`Bash` calls for over an hour across many retries this session, with no indication that the record it was trusting was self-contradictory.

## Why This Survives the WI-5328 Fix

WI-5328 closes the specific gap that produced THIS instance of a wrong/contradictory envelope (the missing `UserPromptSubmit` -> envelope write-back call). But the enforcement hook''s *design* -- read one file, trust it completely, no fallback -- remains a single point of failure. Any FUTURE code change, race condition, or partial-write scenario that produces a stale or contradictory envelope will again silently misroute enforcement, with no detection, because nothing in the hook''s design checks for that class of failure.

## Proposed Direction (advisory -- not a ready-to-implement design; requires its own follow-on proposal + review)

1. **Fail loud/safe on detected inconsistency.** When a role-gated hook reads an envelope where `role_resolution.interactive_role_source` and `worker_role_provenance.role_resolution_source` disagree about whether the role came from the transcript for the SAME `session_id`, treat that as a hook-level defect signal (log/surface it distinctly) rather than silently acting on either value.
2. **Prefer a live-derived signal over a purely file-cached one where practical.** Where the hook''s host process still has access to session/transcript context at PreToolUse time, cross-checking against that live context (rather than relying solely on a file written earlier in the session lifecycle) would make the enforcement point harder to desync from ground truth.
3. **Scope note:** this advisory does NOT prescribe the exact mechanism (full transcript re-derivation may be infeasible inside a PreToolUse hook''s execution context) -- that design work belongs in a dedicated follow-on proposal once WI-5328 lands and its fix''s actual failure modes are better understood.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` -- this advisory itself is filed under the artifact-oriented governance / strategic self-improvement directive rather than left as unrecorded chat context.

## Prior Deliberations

- `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md` (NEW, filed this session immediately prior to this advisory) -- the narrow bug-fix this advisory is explicitly distinct from and complementary to.
- No other prior deliberation found specifically on hook-level envelope-consistency verification; `gt deliberations search` was not re-run for this narrow advisory given its direct lineage from the WI-5328 filing just completed in the same session.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

Owner directive, verbatim, this session: "This is a flawed mechanism and it needs to be replaced with one that works for our purposes" (referring to the GTKB-LO-FILE-SAFETY enforcement design), followed immediately by the standing directive quoted above under "Standing Directive This Advisory Satisfies."

## Recommended Next Step for Prime Builder / Owner

1. Once `groundtruth.db` is unprotected (WI-5211''s review resolves), register this finding as WI-5336 in MemBase with a linked test, per the standard GOV-12 chain.
2. Treat this advisory as informational/design-input only; do not action any hook change from this document alone -- a dedicated implementation proposal with its own review is required before any hook code changes.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.