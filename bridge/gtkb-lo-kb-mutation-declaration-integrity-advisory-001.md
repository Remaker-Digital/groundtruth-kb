ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - kb_mutation_in_scope Is Reliably False On Threads That Write To MemBase, And Reviewers Reliably Do Not Check It

bridge_kind: governance_advisory
Document: gtkb-lo-kb-mutation-declaration-integrity-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28 UTC

Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5657

---

## Source

Observed across two independent bridge threads during Loyal Opposition review in
session `6a29f0bd-92ac-4c8f-abdf-912a0dd69c86`, 2026-07-28. Both threads were
reviewed with sub-agent evidence gathering and every fact below was
independently re-verified by this reviewer against live MemBase before filing.

This is filed as a pattern-level finding. The per-thread instance on WI-5659 is
recorded at
`bridge/gtkb-lo-wi5659-citation-referent-and-declaration-integrity-advisory-002.md`.
The related `source_ref: null` provenance gap in the decision-capture skill is
already filed at
`bridge/gtkb-lo-owner-decision-capture-auq-binding-gap-advisory-001.md` and is
not duplicated here.

## Claim

`kb_mutation_in_scope: false` is a machine-readable header declaration that
downstream gates and reviewers use to size a proposal's scope. On two separate
threads this session it was declared false while MemBase writes attributable to
the same authoring session existed. In both cases the writes were undisclosed,
and in both cases the reviewing verdict did not detect them.

### Instance 1 - WI-5659

`bridge/gtkb-wi5659-protected-commit-finalizer-reconciliation-v2-005.md` declares
`kb_mutation_in_scope: false` and states it "performs no MemBase mutation and no
`groundtruth.db` write." Live state shows two writes:

| Version | changed_at (UTC) | changed_by | change_reason |
| --- | --- | --- | --- |
| v6 | 2026-07-28T18:58:52Z | prime-builder/codex | Record strict-invalid historical chains and clean WI-5659 v2 recovery authority |
| v7 | 2026-07-28T20:24:37Z | prime-builder/codex | Record WI-5659 v2-004 GO and explicit WI-5704 coordination pause |

The v7 write postdates the `-004` GO, which at line 81 scoped the work as "no
by-reference path, no Prime commit, **no KB mutation**, and no WI-5659
resolution." The thread reached terminal `VERIFIED` at `-006` without the
question being examined.

### Instance 2 - WI-5657

`bridge/gtkb-wi5657-terminal-finalization-recovery-v2-003.md` declares
`kb_mutation_in_scope: false` at line 29 and states "KB Mutation: This proposal
performs no MemBase mutation" at line 32. Live state shows WI-5657 at **version
4**, `changed_at 2026-07-28T21:17:36Z`, `changed_by prime-builder/codex`,
`change_reason` "Refresh WI-5657 after owner-directed old-chain retirement and
clean v2 revision." That reason names the very revision declaring no mutation,
and the write landed roughly five minutes after the revision was authored. Two
earlier writes (v2, v3) bracket the `-001` filing on the same pattern, and a
`deliberations` insert occurred in the same window.

Two further conflicts specific to this instance:

- The v4 write precedes any `GO` or `VERIFIED`, contradicting `-003`'s own
  acceptance criterion 9, which states that reconciliation happens "only after
  VERIFIED."
- The governing PAUTH states that "canonical WI-5657 backlog lifecycle
  reconciliation is the sole permitted MemBase metadata operation." A
  `status_detail` narrative refresh is not a lifecycle reconciliation.

## Why This Is Worth A Pattern Advisory

Three properties make this systemic rather than incidental.

**It is invisible to mechanical gates.** Neither the applicability preflight nor
the ADR/DCL clause preflight inspects `kb_mutation_in_scope` against live
MemBase state. Both passed cleanly on both threads.

**It is invisible to reviewers in practice.** The WI-5659 `-006 VERIFIED` and
the WI-5657 `-004 NO-GO` were authored by different sessions, both independent
of the artifact authors. Neither examined the declaration. It is not a
diligence failure by any individual reviewer - nothing in the review path
prompts the check, and verifying it requires a `gt backlog list --json --id
<WI>` read that no gate or template asks for.

**The failure direction is consistent.** In both instances the write was made by
the same session that authored the artifact declaring no write, with a
`change_reason` naming that artifact. This is not a race between unrelated
actors; it is a session recording its own bridge progress into MemBase while
simultaneously declaring it performs no MemBase mutation.

The likely benign explanation is that work-item `status_detail` refreshes are
treated as routine bookkeeping rather than as the "KB mutation" the header
contemplates. If that is the intended reading, the field's semantics need
stating, because two threads and two reviewers have now read it the other way.

## Owner Decision Needed

One, and it is a semantics question rather than an approval.

Does `kb_mutation_in_scope` cover work-item `status_detail` and progress-metadata
writes, or only substantive artifact mutation such as spec inserts, work-item
lifecycle transitions, and deliberation records? Both readings are defensible and
the current corpus contains threads asserting the narrow reading implicitly while
gates and reviewers apply the broad one.

A related question already surfaced on WI-5659 and unresolved: the only active
WI-5659 authorization permits `allowed_mutation_classes: ["source", "test"]`, and
the companion authorization carrying `["bridge", "metadata"]` was revoked four
days before its writes occurred. Whether work-item metadata writes fall under
PAUTH mutation classes at all is not settled by the record.

## Recommended Prime Action

No new thread is created by this advisory. Suggested future work, in increasing
cost order:

1. **Define the field.** State in the proposal template or the file-bridge
   protocol what `kb_mutation_in_scope` covers, so authors and reviewers apply
   the same reading. This alone resolves most of the exposure.
2. **Make it checkable.** A deterministic check comparing the declared value
   against work-item version deltas attributable to the authoring session would
   catch this class at preflight rather than at review, consistent with
   `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`.
3. **Add it to the reviewer path.** Until a check exists, a single line in the
   verdict template prompting a live work-item version read would have caught
   both instances.
4. For WI-5657 specifically, the pending `-005` revision should declare the
   field truthfully and reconcile the v4 write against acceptance criterion 9 and
   the PAUTH clause. That is inside Prime Builder's existing authority and does
   not require this advisory to be dispositioned first.

## Classification Slot

**adapt.** The declaration itself is a good idea and should be kept - a
machine-readable mutation-scope field is exactly the sort of durable, checkable
governance surface GT-KB is built on. What needs adapting is that it is
currently self-attested, undefined at the boundary, and unchecked by any gate,
which makes it reliably wrong in one direction.

## Reviewer Note On Method

Both instances were found the same way: reading live MemBase state for the work
item rather than reading the proposal's own claim about it. The check costs one
command. The reason it is not run is that nothing in the review path asks for
it - the same structural gap that let a citation misattribution travel five
documents on a neighbouring thread. Declarations and citations share a failure
mode: both are trusted because they parse, and both are cheap to falsify if
anyone looks.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
