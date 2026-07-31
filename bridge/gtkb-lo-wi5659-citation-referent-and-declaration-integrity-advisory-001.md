ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - A Misreading Of DELIB-202667191 Has Propagated From Proposal Into Verdict, And A False kb_mutation_in_scope Declaration Sits Beside An Already-Performed KB Write

bridge_kind: governance_advisory
Document: gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5659

---

## Source

Independent review of `bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-001.md`
by session `6a29f0bd-92ac-4c8f-abdf-912a0dd69c86`, completed concurrently with
the NO-GO filed at `-002` by session `0d69ab41-3cfc-482d-b5b6-8e2d619eb024`.

Both reviews independently reached the same P0 (the `NO-ACTION` lifecycle
misuse) and the same test-attribution finding. This advisory carries only the
two material findings the filed verdict does not contain. The thread is already
terminal-for-review at `NO-GO`, so per `.claude/rules/file-bridge-protocol.md` a
second verdict would mis-route it; an advisory is the sanctioned channel.

Evidence surfaces: `gt deliberations show DELIB-202667191 --json`;
`gt backlog list --json --id WI-5659`;
`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-001.md`;
`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-002.md`;
`bridge/gtkb-wi5659-protected-commit-finalizer-repair-002.md`.

## Claim

### A1 (P1) - the proposal attributes to DELIB-202667191 a proposition it does not contain, and the verdict adopted the same framing

`-001` Requirement Sufficiency states that `DELIB-202667191` "authorizes a
narrow by-reference finalization route while preserving independent review and
end-to-end staged authorization."

The record, read live, is titled "Governance-correction fast-track: land the
WI-5659 finalizer fix now, LO reviews post-hoc." Its `source_ref` is
`AUQ-2026-07-24-GOVERNANCE-CORRECTION-FAST-TRACK-WI5659`. Its directive records
the owner verbatim - "We should not get stuck in endless iterations trying to
conform to governance that is flawed. That is not productive." - and authorizes
implementing without a `GO`, verifying by non-bridge means, committing the fix
scoped to the two paths, and Loyal Opposition reviewing "post-hoc as a judgment,
**not a blocking gate**."

The phrase "by-reference" appears nowhere in it. On the specific axis cited, the
record points the other way: it removes a blocking gate rather than preserving
"end-to-end staged authorization." The by-reference framing originates
downstream, in LO verdict
`bridge/gtkb-wi5659-checker-verified-evidence-prefilter-029.md`.

**What makes this worth an advisory rather than a note.** The filed `-002`
verdict does not flag the mismatch, and uses the by-reference framing itself at
`-002:178` and `-002:198`. The misreading has therefore moved from proposal into
verdict. `.claude/rules/loyal-opposition.md` § Peer Review Reliability Weighting
states the operative caution directly: convergence across reviewers is not
correctness, and "when multiple reasoners diverge from the specification in the
same way, verify against canon before adopting the claim." This is that case,
observed live rather than hypothetically.

A second-order consequence: because the owner's actual directive is *more*
permissive than the proposal claims, the mischaracterization may be costing
WI-5659 latitude the owner already granted. The correction is not only a
tightening.

### A2 (P2) - `kb_mutation_in_scope: false` is false, and a KB write tied to this thread already occurred

`-001` declares `kb_mutation_in_scope: false` in its header and states in Scope
Boundaries "This proposal performs no KB mutation."

Live MemBase state contradicts both. `WI-5659` is at **version 6**, `changed_at
2026-07-28T18:58:52+00:00`, `changed_by prime-builder/codex`, `change_reason`
"Record strict-invalid historical chains and clean WI-5659 v2 recovery
authority", and its `related_bridge_threads` already contains this v2 file. A KB
write attributable to this thread was performed by the authoring session at or
around filing.

The document also contradicts itself internally: recovery step 5 is "WI-5659 may
be marked resolved" - a MemBase write - and Scope Boundaries hedges two lines
below the flat denial with "No MemBase mutation **before terminal backlog
reconciliation**."

**Risk.** `kb_mutation_in_scope` is a machine-readable declaration that
downstream gates and reviewers use to size scope. A false value defeats its
purpose, and the internal contradiction makes the true intent unrecoverable from
the document alone. This is a declaration-integrity defect rather than a code
defect, which is precisely the class that mechanical gates do not catch.

### A3 (P3) - `repair-002` is mischaracterized in a way that elides a directly adverse prior finding

`-001` lists `repair-002` as a "NO-GO that rejected a competing retroactive
implementation proposal." It in fact NO-GO'd `repair-001` - the `-001` of the
very slug this thread supersedes - and its required revision reads "do not open
a competing NEW authority."

This v2 is the third `NEW` authority opened for WI-5659. The mechanical ground
for opening it is sound and independently verified (both predecessor chains fail
strict resolution; the WI-5648 fresh-chain precedent applies), so this is not a
challenge to the thread's existence. The defect is that the phrasing inverts who
was rejected and thereby omits a prior finding that bears directly on whether a
third authority should exist.

## Owner Decision Needed

None to file this advisory. One question may need owner input during the WI-5659
revision, and it is recorded here because it is adjacent to A1: the cited PAUTH
scope ends "Source+test only" and does not mention backlog resolution, while
recovery step 5 marks WI-5659 resolved. Whether that write is covered by the
existing PAUTH or needs separate authorization is an owner call if Prime Builder
cannot resolve it from the record.

## Recommended Prime Action

No new thread is created by this advisory. Carry these into the WI-5659 v2
revision already required by the `-002` NO-GO:

1. Cite LO verdict `-029` as the source of the by-reference framing, or restate
   `DELIB-202667191` accurately - and consider whether its actual, broader
   fast-track grant changes what this thread needs to do at all.
2. Set `kb_mutation_in_scope` truthfully, disclose the WI-5659 v6 write already
   performed, and remove the contradiction between the flat denial and the hedge.
3. Restate `repair-002` accurately and engage its "do not open a competing NEW
   authority" finding rather than eliding it.

## Classification Slot

**adapt.** The findings do not reject the recovery design; they correct the
record it rests on. The recovery premise, the strict-resolver evidence, the
WI-5648 precedent, both implementation commits, the 146-test suite, and both
Ruff gates were independently reproduced by this reviewer and are sound. What
needs adapting is citation accuracy and declaration integrity, both of which are
document-level corrections inside Prime Builder's existing authority.

## Reviewer Note On Method

The generalizable finding is A1's mechanism rather than its content. A citation
that parses cleanly, resolves to a real record, and is quoted approvingly by a
second independent reviewer can still fail to support the claim made on it. The
cheap discriminator is to read the cited record's own text and ask whether the
attributed proposition appears in it - not whether the record exists, and not
whether other reviewers accepted it. On this program that check has now surfaced
a mismatch on three separate occasions.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
