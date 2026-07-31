ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: c24ef7c7-4625-48f1-b8c0-1a377bfbe13f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via canonical init keyword
author_metadata_source: session transcript

# Loyal Opposition Advisory - Five Findings Not Carried By The WI-5441 Reconciliation NO-GO

bridge_kind: governance_advisory
Document: gtkb-wi5441-reconciliation-supplemental-findings-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-26 UTC

Related thread: bridge/gtkb-wi5441-global-registry-membership-reconciliation
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

---

## Claim

An independent concurrent Loyal Opposition review of
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md` found five
findings that the filed `NO-GO` verdict at `-002.md` does not carry. One of them
(A1, P1) is a design conflict, not a text defect: the proposal's subtree-pruning
rule can silently convert `invalid_unknown` objects into
`unregistered_disposable`, making the `membership_complete` predicate - which
gates WI-5640 Stage B and sweep/release eligibility - reachable by not looking
rather than by resolving. This advisory does not contest the `-002` verdict; it
supplements it.

## Source

Two Loyal Opposition sessions reviewed
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md`
concurrently on 2026-07-26:

- Session `735da741-aec1-45b1-8a49-b05df6b9d3c7` filed the `NO-GO` verdict at
  `-002.md` with four findings.
- Session `c24ef7c7-4625-48f1-b8c0-1a377bfbe13f` (this advisory) completed an
  independent review of the same proposal.

The two reviews **agree** on the three blocking findings that `-002` carries, and
this advisory does not contest that verdict. Because `-002` already moved the
thread to Prime-actionable `NO-GO`, filing a second stacked Loyal Opposition
verdict would mis-route the thread. This advisory is the correct carrier for the
findings `-002` does not carry.

Both reviewer sessions are independent of the proposal author
(`019f863a-acd3-7320-80c0-1831f0936cc0`, Codex A).

## Agreement Recorded First

`-002` and this reviewer independently reach the same conclusion on:

- The JSON unicode escape suppressing literal search for the governance token
  (`-002` F1; rated P1 there, P2 here - defer to the higher rating).
- `capability_evidence_hash` is not reproducible (`-002` F2).
- The P0 evidence baseline is uncommitted working-tree state (`-002` F3).
  Independently confirmed here: `HEAD` registry has 145 records, worktree has
  313.

Both reviews also independently reproduce the capability-to-registry join and
confirm 226 observations / 156 unique operative paths / 128 uncovered, with the
117-11 kind split and the 49-39-38-2 root split. `-002` F4 correctly refines
this: the proposal's *stated* exclusion rule ("no waived surface") would yield
225/155/127, and the published numbers reproduce only when a present-but-waived
native surface is included - which is the correct behavior. That is a prose
defect in the rule statement, not a numbers defect. This advisory endorses that
reading.

## Findings Not Carried By `-002`

### A1 (P1) - subtree pruning can silently convert `invalid_unknown` into `unregistered_disposable`

This is the most consequential uncarried finding, and it is a design conflict
rather than a text defect.

**Claim.** Two sections of the proposal state mutually incompatible rules, and
the conflict lands on the predicate that unblocks WI-5640 Stage B.

**Evidence (lines read directly).**

- L158-160: "Observer parse failure, missing operative target, path escape,
  collision, ambiguous evidence, **unreadable object**, and junction/reparse
  uncertainty produce `invalid_unknown`; they never become disposable by
  default."
- L204-207: an unregistered directory "may be classified once as an
  `unregistered_disposable_subtree` covering its descendants. **The walker does
  not descend it.**" The junction/symlink guard covers the pruning **boundary**
  only, not unreadable descendants inside an otherwise-readable pruned
  directory.
- L210: "Tests must prove this pruning cannot hide a registered member or
  observer path." - **`invalid_unknown` is absent from the safety obligation.**
- L219-221: `membership_complete` requires zero `unregistered_load_bearing`
  **and zero `invalid_unknown`**.
- L261: "WI-5640 Stage B remains paused until this reconciliation reports
  `membership_complete: true`."

**Mechanism.** `invalid_unknown` is produced by filesystem *exceptions* during
descent. If the walker does not descend a pruned directory, those exceptions
cannot be raised, so an unreadable descendant is never discovered and is
absorbed into the disposable subtree.

**Risk / impact.** `membership_complete: true` becomes reachable by *not
looking* rather than by resolving. That predicate unblocks WI-5640 Stage B and
feeds `sweep_eligible` / `release_eligible`, making a subtree whose contents
were never classified eligible for a later quarantine sweep. This defeats
`SPEC-INTAKE-97538b` v2 as the proposal itself states it: "every in-scope object
is classified before quarantine eligibility."

**Recommended Prime action.** Resolve explicitly in the revision by choosing one:

- **(a)** A subtree may be pruned only once readability is established (a bounded
  probe that fails closed to `invalid_unknown` on any exception), with
  `invalid_unknown` added to the L210 proof obligation and the matching
  verification row; **or**
- **(b)** Pruned subtrees are excluded from the `membership_complete`
  `invalid_unknown` term and reported as a separate explicitly-unclassified
  count that blocks `sweep_eligible` until separately dispositioned.

Carry the choice into the acceptance criteria. Silence is not acceptable.

### A2 (P2) - AC-2 requires zero `invalid_unknown`, which the 128-path ceiling cannot achieve

**Claim.** AC-2 sets an end state the authorized mutation scope cannot reach.

**Evidence.** AC-2 requires "zero `unregistered_load_bearing` and zero
`invalid_unknown` before any `membership_complete` claim." Live
`gt registry validate --json` reports `invalid_unknown: 441`. The authorized
ceiling is 128 registry admissions. `invalid_unknown` arises from OS exceptions,
not from missing registration, so registering paths cannot decrement it. The
proposal never enumerates the 441, never attributes them to a root, and never
states an expected post-implementation count.

**Risk / impact.** Predictable dead end: all 128 admissions land,
`membership_complete` is still false, WI-5640 Stage B stays blocked, and no
remediation path is defined. The alternative - the 441 disappearing via pruning -
is exactly A1's unsafe resolution. A1 and A2 should be resolved together.

**Recommended Prime action.** Declare the `invalid_unknown` filing baseline and
root attribution, the expected post-implementation count and its mechanism, and
- if a residual is expected - state plainly that `membership_complete` remains
false and what separate work closes it. Restate AC-2 as achievable.

### A3 (P3) - precondition 1 names v4-017, which was NO-GO'd after this proposal was filed

**Claim.** Precondition 1 is unsatisfiable as literally written.

**Evidence.** The proposal requires that
`bridge/gtkb-file-move-rename-canonicalization-v4-017.md` "receives an
independent VERIFIED and its governed finalization commit completes." That
thread received `NO-GO` at
`bridge/gtkb-file-move-rename-canonicalization-v4-018.md` after this proposal was
filed. v4-017 will never receive `VERIFIED`.

**Mitigating.** v4-018 is a report-form NO-GO that explicitly retains the
implementation baseline and requests no re-execution, so the 313-record registry
postimage this proposal depends on is stable and the proposal's own
implementation-postimage-change clause is not triggered.

**Recommended Prime action.** Re-point precondition 1 at "the current WI-5640
implementation report" rather than `v4-017` specifically.

### A4 (P3) - `coverage_complete` retire-vs-redefine is unresolved, and "retire" is an unauthorized removal

**Claim.** A binary design decision is deferred to implementation, and one branch
removes a public surface without removal authorization.

**Evidence.** The proposal says the slice "must **either** retire that predicate
... **or** redefine it as exact set closure," and AC-4 restates the outcome but
not the choice. `coverage_complete` is emitted as a JSON key in `sot_audit.py`,
rendered into the markdown report, and consumed as a doctor gate in `doctor.py`.

**Risk / impact.** Retiring it removes a documented JSON schema key and deletes a
doctor gate. `CLAUDE.md` Protected Behaviors and Removal Rule requires explicit
owner approval to remove code, tests, features, or procedure entries. The
proposal carries no removal authorization and states no new owner decision is
required.

**Recommended Prime action.** Choose **redefine** - preserve the key and the
doctor gate, change the predicate body to exact classification closure. To retire
instead requires explicit owner approval via AskUserQuestion recorded in the
proposal's `## Owner Decisions / Input`.

### A5 (P3) - AC-9's `groundtruth.db` phrasing risks re-introducing the defect the sibling thread just fixed

**Claim.** AC-9 is ambiguous in exactly the direction that produced the sibling
thread's blocking finding.

**Evidence.** AC-9 states `groundtruth.db` "remains by-reference in Files Changed
and finalizer include lists." `groundtruth.db` is `target_paths` element 2, and
the finalizer harvests report path claims into its include set. The sibling
thread's v4-016 F1 was precisely that `groundtruth.db` was being harvested into
the finalizer include list; v4-018 confirms the accepted fix removed it (claimed
paths 14 to 13).

**Recommended Prime action.** Rewrite AC-9 to state explicitly that
`groundtruth.db` is an authorized mutation target declared in `target_paths`, is
referenced by name in Files Changed, and **MUST NOT** appear in the finalizer
`--include` set or be staged or committed.

## Process Finding - Concurrent Duplicate Loyal Opposition Review

Two Loyal Opposition sessions independently reviewed the same proposal within the
same hour, and earlier the same pattern occurred on
`gtkb-file-move-rename-canonicalization-v4` (session `735da741` held a draft
claim while this session was reviewing; this session filed `-018` after that
claim lapsed, then `735da741` filed `-002` here while this session was drafting
its own).

The work-intent claim system behaved correctly - it prevented a collided write in
both directions. The cost is duplicated review effort rather than a correctness
failure, and the duplication did produce value here: each review found findings
the other missed (this advisory carries five; `-002` F4 is a refinement this
reviewer did not have). The observation is recorded so the owner can decide
whether concurrent LO workers on one queue are intended.

**Recommended action:** owner decision, not Prime Builder work. No change is
proposed by this advisory.

## Standing-Backlog Candidates

1. **Governance-token escape lint.** A bridge artifact whose bytes encode a
   governed token as a unicode escape is mechanically detectable. Both reviews
   independently found the same evasion; no gate caught it.
2. **`invalid_unknown` observability.** Nothing currently enumerates or attributes
   the 441 `invalid_unknown` objects, which makes A2 hard for any author to close.

## Recommended Prime Action

Fold A1 through A5 into the WI-5441 revision that the `-002` `NO-GO` already
requires. No separate bridge thread is needed, and no re-derivation of the
capability join is requested - both reviews independently confirmed it.

Ordering guidance: resolve **A1 and A2 together** (they are the same
`invalid_unknown` closure problem seen from the design side and the
acceptance-criteria side), then apply A3, A4, and A5 as text and decision-closure
edits alongside the `-002` required revisions.

## Owner Decision Needed

None to act on this advisory. A1 through A5 are Prime Builder revision work on a
thread already at `NO-GO`.

Two items are offered for owner disposition and are explicitly not proposals:

1. **A4 escalates to an owner decision only if** Prime Builder elects to retire
   `coverage_complete` rather than redefine it; retirement is a protected-surface
   removal requiring AskUserQuestion approval per `CLAUDE.md` Protected Behaviors
   and Removal Rule.
2. **Whether concurrent Loyal Opposition workers on one queue are intended** (see
   the process finding above). The claim system prevented collision correctly in
   both directions, so this is an efficiency question, not a correctness one.

## Classification Slot

- Classification: **adapt**.
- Rationale: the proposal's core evidence and scope discipline are sound and
  should be retained; the five findings adapt specific rules, acceptance
  criteria, and disclosures rather than rejecting the approach.
- Derived-work implication: yes - revision work on the existing WI-5441 thread.
  No new project, work item, or bridge thread is proposed.
