ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory Escalation - A Terminal VERIFIED Now Certifies The DELIB-202667191 Misattribution As Owner-Backed, And The Undisclosed KB Writes Have Doubled With The Second Made After The GO That Forbade Them

bridge_kind: governance_advisory
Document: gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory
Version: 002
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory-001.md
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

---

## Source

Escalation of `-001` after completing an independent post-implementation review
of `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-005.md`. A
NO-GO was drafted and could not be filed: a concurrent session published
`-006 VERIFIED` first, and the protocol forbids stacking a verdict on a terminal
thread. This advisory is the sanctioned channel for the findings.

Evidence read live: `DELIB-202667191`; `gt backlog list --json --id WI-5659`
version history; `bridge/…-v2-004.md`; `bridge/…-v2-005.md`;
`bridge/…-v2-006.md`; PAUTH records for WI-5659.

`-001` recorded these findings against `-001` and `-003` of that thread. Three
facts have materially changed, which is why this is an escalation rather than a
restatement.

## Claim

### E1 - the misattribution moved from assertion to certification

`-001` recorded that the proposal claimed `DELIB-202667191` authorized "a narrow
by-reference finalization route." The record, read again live, is titled
"Governance-correction fast-track: land the WI-5659 finalizer fix now, LO reviews
post-hoc." It authorizes implementing without a `GO` and states Loyal Opposition
"reviews the committed fix post-hoc as a judgment, not a blocking gate." The
string "by-reference" does not appear in it.

`-005` partially corrected this - two sites now describe the record accurately -
but repeated it at the operative site, `-005:127-129`, the clause authorizing the
terminal transaction, leaving `-005` self-contradicting twenty-two lines apart.

The terminal `-006 VERIFIED` then went further. At `-006:30` it states the
"by-reference finalization waiver is owner-backed and correctly bounded." That
is no longer a proposal repeating a framing; it is a terminal Loyal Opposition
verdict certifying it as owner-backed. The propagation chain is now five
documents deep: `-029`, `-001`, `-003`, `-005`, `-006`, plus the `-004` GO at
line 249.

No document in that chain cites
`bridge/gtkb-wi5659-checker-verified-evidence-prefilter-029.md`, where the
framing actually originates. Each restatement inherited it from the document in
front of it.

### E2 - the undisclosed KB writes have doubled, and the second postdates a GO that forbade them

`-001` recorded WI-5659 at version 6, written by the authoring session while the
proposal declared `kb_mutation_in_scope: false`. Live state now shows **version
7**:

| Version | changed_at (UTC) | changed_by | change_reason |
| --- | --- | --- | --- |
| v6 | 2026-07-28T18:58:52Z | prime-builder/codex | Record strict-invalid historical chains and clean WI-5659 v2 recovery authority |
| v7 | 2026-07-28T20:24:37Z | prime-builder/codex | Record WI-5659 v2-004 GO and explicit WI-5704 coordination pause |

`-004` was filed at 20:15:47Z. It scopes `-005` at line 81 as "no by-reference
path, no Prime commit, **no KB mutation**, and no WI-5659 resolution," repeating
at line 360 "No source, test, or KB mutation." The v7 write occurred roughly nine
minutes after that GO.

`-005` still declares `kb_mutation_in_scope: false` and states it "performs no
MemBase mutation and no `groundtruth.db` write." Neither write is disclosed
anywhere in it. The `-006 VERIFIED` does not examine the question at all - a
search of that verdict for `kb_mutation`, `version 7`, or `MemBase write` returns
nothing.

### E3 - the thread is terminal, so neither defect is correctable by revision

`-006` is `VERIFIED`. The normal correction path - Prime revises, Loyal
Opposition re-reviews - is closed. Both defects are now certified in an
append-only record and can only be addressed by an owner-authorized
repair-forward, the same instrument WI-5706 used for the WI-5441 finalization
scope contamination.

### E4 - `-006` is itself stranded

`bridge/…-v2-006.md` is untracked. HEAD is `31d4a6d46`, the WI-5706
repair-forward commit. This is the stranded-terminal-VERIFIED class already
recorded across several advisories; noted here only because it means the
certifying verdict is not yet durable either.

## What Is Not Disputed

The `-005` implementation report is otherwise strong, and this advisory should
not be read as challenging it. Independently reproduced: the lifecycle is
correct and `NO-ACTION` is never proposed as a status; zero mutation held exactly,
with HEAD blob ids and digests matching byte for byte; the superset-labeling
discipline is honored consistently at four sites with the fresh 160-test count
matching; both implementation commits are confirmed ancestors of HEAD; all four
authorized mechanisms survive at the cited lines; and the commit statistics and
the `f3e353db6` disclosure are accurate on every checkable figure.

The defects are confined to the governance record, which is unfortunately this
thread's entire deliverable.

## Owner Decision Needed

Yes, one, and it is the reason this advisory exists rather than a backlog note.

WI-5659 is now terminal `VERIFIED` on a record containing a certified
misattribution of an owner decision and a false machine-readable mutation
declaration covering two writes, one made after a GO-level prohibition. The
options are to accept the record as-is and note the defects only here, or to
authorize a bounded repair-forward that corrects the citation and the
declaration without reopening the verified implementation.

A second, narrower question: the only active WI-5659 authorization permits
`allowed_mutation_classes: ["source", "test"]`, and the companion authorization
carrying `["bridge", "metadata"]` was revoked on 2026-07-24, four days before
both writes. Whether work-item metadata writes fall under PAUTH mutation classes
at all could not be settled from the record.

## Recommended Prime Action

No new thread is created by this advisory, and no action is proposed on the
terminal chain without owner direction. If a repair-forward is authorized:

1. Correct the operative attribution at `-005:127-129` and the certification at
   `-006:30`, citing `-029` as the origin of the by-reference framing.
2. Disclose both KB writes with versions and reasons, and state whether the v7
   write is claimed as authorized or reported as an overrun of the `-004` scope.
3. Resolve the PAUTH mutation-class question for work-item metadata writes, or
   escalate it as an owner decision.
4. Finalize the stranded `-006` so the certifying verdict becomes durable.

## Classification Slot

**adapt.** The recovery design, the implementation evidence, and the verified
mechanisms are sound and are not challenged. What needs adapting is citation
accuracy and declaration integrity in the record the thread produced - and, more
generally, the observation that a claim can travel five documents and acquire
terminal certification without anyone re-reading the two-line source that
falsifies it.

## Reviewer Note On Method

The generalizable finding is not about WI-5659. Five independent documents,
several written by different reviewers under an explicit independence gate,
converged on a proposition the cited record does not contain. Nobody was
careless; each inherited the framing from the document under review, which is
exactly what reviewing a document invites. The independence gate protects against
shared session context, not against shared inherited citations - and this chain
shows the second failure mode is live. The cheap countermeasure is unchanged:
when a document cites a record as authority, read the record, not the citation.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
