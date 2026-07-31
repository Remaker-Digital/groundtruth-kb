ADVISORY

# Advisory: Role-gated hooks (GTKB-LO-FILE-SAFETY et al.) trust a single static session-envelope file with no live cross-check or self-healing

bridge_kind: governance_advisory
Document: gtkb-role-gated-hook-envelope-fragility-advisory
Version: 002
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-16 UTC

Responds to: bridge/gtkb-role-gated-hook-envelope-fragility-advisory-001.md

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive session; session-stated Prime Builder role via literal ::init gtkb pb opening message; explanatory output style

implementation_scope: none (advisory / design-critique only; no code, test, or KB mutation proposed or performed by this document)
requires_review: true
requires_verification: false
kb_mutation_in_scope: false

---

## Classification Correction (this version)

Version 001 of this thread was filed with `bridge_kind: governance_review` and first-line status `NEW`, and did not follow the required ADVISORY template (missing `## Source` / `## Claim` / `## Owner Decision Needed` / `## Recommended Prime Action` / `## Classification Slot`). Also, `bridge_kind: loyal_opposition_advisory` (used in an earlier attempt to correct this) is itself not a valid value -- the enforced enum (`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`) is `{governance_advisory, implementation_report, index_reconciliation, lo_verdict, operational_state_change, prime_proposal}`. Both the `findings-always-become-advisory-proposals.md` auto-memory and the `canonical-terminology.md` glossary entry for "Loyal Opposition advisory" reference the stale `loyal_opposition_advisory` value; that drift is itself noted under Recommended Prime Action below. This version 002 corrects the classification and template to what the live `bridge-compliance-gate` actually enforces. It does not change the substantive finding from -001.

## Author Role-Provenance Disclosure (read before review)

Same live defect as the sibling proposals filed this session (`gtkb-wi5328-session-envelope-role-writeback`, `gtkb-wi5330-spec-link-heading-hyphen-false-positive`): this session's envelope resolves `role_resolved: "loyal-opposition"` despite the literal `::init gtkb pb` opening message. The owner has explicitly confirmed the session-stated role is authoritative and directed proceeding with filing despite the inconsistency.

## Source

This session's own live investigation (2026-07-16), while diagnosing why routine Prime Builder `Write`/`Bash` calls were being blocked. Not an external/peer-harness source -- a first-hand defect discovery made while working WI-5328.

## Claim

`GTKB-LO-FILE-SAFETY`, and by extension any other role-gated `PreToolUse` hook that consults `.claude/session/envelope.json`, currently trusts that single static file unconditionally -- with no live cross-check against the actual session transcript/context, and no self-healing or fail-loud behavior when the file is stale or internally inconsistent. This is distinct from WI-5328 (the narrower missing envelope-role-write-back bug) and survives WI-5328 landing: the enforcement hook's *design* -- read one file, trust it completely, no fallback -- remains a single point of failure for any FUTURE stale/contradictory envelope, regardless of what causes it.

### Evidence

A freshly-opened session (`session_id: ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2`, literal opening message `::init gtkb pb`) produced an envelope containing an internally CONTRADICTORY record:

```
"role_resolution": { "interactive_role_source": "transcript_init_keyword" },   <- claims transcript-sourced
"worker_role_provenance": { "role_resolution_source": "session_resolver_fallback" }  <- but actually fell back
```

Both fields describe the SAME session_id at the SAME point in time, and directly contradict each other. `GTKB-LO-FILE-SAFETY` nonetheless accepted this record at face value and used it to block routine Prime Builder writes for over an hour across many retries this session, with no indication that the record it was trusting was self-contradictory.

## Owner Decision Needed

1. Is "fail loud/safe on detected internal inconsistency" (log/surface the contradiction, do not silently trust either value) sufficient by itself, or is a live-recheck mechanism (re-derive role from current context at PreToolUse time) also wanted, given that is a heavier design with its own feasibility questions inside a hook's execution context?
2. How urgently should this be prioritized relative to the WI-5320 (dispatcher starvation), WI-5328 (envelope write-back), and WI-5330 (spec-link regex) items already in flight this session -- fast-follow after WI-5328 VERIFIES, or lower priority as a hardening/defense-in-depth improvement rather than an active-harm bug?
3. Should this become its own registered work item (WI-5336, number reserved in this session's draft investigation) once `groundtruth.db` unblocks from the concurrent WI-5211 report review, or should it fold into WI-5328's scope as an additional acceptance criterion instead of being tracked separately?

These questions remain OPEN and unresolved pending a dedicated AskUserQuestion pass; per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` they must be resolved before any implementation proposal derived from this advisory is drafted.

## Recommended Prime Action

1. Run the three Owner Decision Needed questions above via AskUserQuestion (one at a time) before drafting any implementation proposal for this advisory.
2. Once `groundtruth.db` is unprotected (WI-5211's review resolves), register this finding as WI-5336 in MemBase with a linked test, per the standard GOV-12 chain -- pending the tracking-decision question above.
3. Separately: `findings-always-become-advisory-proposals.md` (Claude auto-memory) and the `canonical-terminology.md` "Loyal Opposition advisory" glossary entry both cite the non-existent `bridge_kind: loyal_opposition_advisory` value; Prime Builder should correct both references to `governance_advisory` (or whichever kind is judged correct) in a future hygiene pass, since this drift caused two failed filing attempts on this very thread.

## Classification Slot

**adapt.** The finding is real and confirmed live this session, not speculative -- not a `reject`. It is not blocked on any milestone, so not a pure `defer`. The failure mode has already manifested and cost real session time, so `monitor` alone is insufficient. It is not yet implementation-ready (the exact mechanism needs owner input per the Owner Decision Needed section), so full `adopt` is premature -- `adapt` is the correct slot: the core direction (fail-loud-on-inconsistency, possibly a harder-to-desync live signal) should be carried forward, but the exact design awaits the owner-grilling answers above.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`

## Prior Deliberations

- `bridge/gtkb-role-gated-hook-envelope-fragility-advisory-001.md` (this same thread, this session) -- the miscategorized first filing this version corrects.
- `bridge/gtkb-wi5328-session-envelope-role-writeback-001.md` (NEW, filed this session immediately prior) -- the narrow bug-fix this advisory is explicitly distinct from and complementary to.

## Owner Decisions / Input

Owner directive, verbatim, this session: "This is a flawed mechanism and it needs to be replaced with one that works for our purposes" (referring to the GTKB-LO-FILE-SAFETY enforcement design), followed immediately by: "When you find an error, flaw or opportunity for enhancement, you must not allow that to be forgotten. The correct response is *always* to file an Advisory Proposal." The Owner Decision Needed questions above remain open pending a dedicated AskUserQuestion pass.

## Non-Approval Statement

This ADVISORY entry is not implementation approval. It does not authorize any hook code change, does not bypass the bridge, project-authorization, owner-decision, root-boundary, credential-safety, formal-artifact, or verification gates, and does not itself constitute a work item until formally registered in MemBase.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.