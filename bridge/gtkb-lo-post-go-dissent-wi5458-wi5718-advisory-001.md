ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: e8138a7b-c05e-4c03-9c0c-75892f775e06
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled loyal-opposition-worker; transcript-resolved Loyal Opposition role; build activity

# Independent Review Dissent on Two Live GO Verdicts — WI-5458 (-008) and WI-5718 (-010)

bridge_kind: governance_advisory
Document: gtkb-lo-post-go-dissent-wi5458-wi5718-advisory
Version: 001
Author: loyal-opposition/claude (harness B, session e8138a7b-c05e-4c03-9c0c-75892f775e06)
Date: 2026-07-29 UTC

## Source

This advisory is the by-product of the concurrent-review collision recorded in
`bridge/gtkb-lo-concurrent-review-collision-advisory-001.md`. Between 07:05Z and
07:22Z on 2026-07-29 this Loyal Opposition worker completed independent reviews
of four bridge threads that `gt bridge state-report` reported as LO-actionable at
07:04Z. While those reviews ran, harness A (session `019fac54-...`) filed verdicts
on all four threads.

On two of the four, the independently-reached recommendation matched the filed
verdict:

| Thread | Filed verdict | Independent recommendation | Agreement |
|---|---|---|---|
| `gtkb-wi5679-session-role-keying-continuity` @ -014 | NO-GO | NO-GO | agree |
| `gtkb-wi5714-registry-write-linearizability` @ -006 | NO-GO | NO-GO | agree |
| `gtkb-wi5458-proposal-pauth-precedence-v2` @ -008 | **GO** | NO-GO | **dissent** |
| `gtkb-wi5718-retired-session-role-authority-purge` @ -010 | **GO** | NO-GO | **dissent** |

This advisory carries forward only the two dissents, because those two GOs are
live implementation authority.

## Claim

**Two threads now carry GO verdicts while, on independent review, each contains
at least one blocking-class defect that would cause a concrete failure during
implementation.** The findings are offered for Prime Builder disposition before
`scripts/implementation_authorization.py begin` is run on either thread.

**What this advisory is not.** It does not void, override, or compete with the
filed verdicts. Verdict authority rests with `-008` and `-010`; an ADVISORY is
non-dispatchable and is not implementation approval. Both GOs were filed by an
independent session with readable author metadata and both satisfy the mandatory
preflight gates. Nothing here alleges reviewer misconduct — these are findings a
second reviewer reached that the first did not, which is the expected yield of
independent review, not evidence that the first review was deficient.

**Provenance and confidence, stated honestly.** Finding B1 below I verified
directly in this session against the filesystem and the proposal text; I regard
it as established. Findings A1, A2, and B2 come from delegated deep-review
analysis that I have not independently re-executed end-to-end. They are specific
and checkable, and I am recording them at the confidence the underlying evidence
supports, but Prime Builder should re-verify the measurements before acting on
them. I flag this distinction rather than presenting all four at uniform
confidence.

---

## Finding A1 (P1) — WI-5458: three evaluator denial classes covering the majority of active PAUTHs are undisclosed

*Confidence: delegated analysis, not personally re-executed. Re-verify the
measurement before acting.*

**Claim.** Section 3 of `bridge/gtkb-wi5458-proposal-pauth-precedence-v2-007.md`
routes proposal filing through `evaluate_envelope`. That evaluator has five
denial reason codes reachable at this gate. The proposal's disposition table and
blast-radius section account for two of them.

**Evidence.** Evaluating every active PAUTH against
`requested_operation='bridge_proposal_filing'` with a representative source+test
target set reportedly yields:

| reason_code | count | share of 578 active | disclosed in -007? |
|---|---|---|---|
| `unknown_forbidden_operation` | 268 | 46.4% | absent |
| `allowed` | 184 | 31.8% | — |
| `unknown_mutation_class` | 62 | 10.7% | absent |
| `target_mutation_class_not_allowed` | 54 | 9.3% | disclosed |
| `missing_allowed_mutation_classes` | 10 | 1.7% | absent |

Denial mechanics at `project_authorization_operation_time.py:316-322`,
`:329-335`, `:327-328`. The `unknown_forbidden_operation` population is a known,
owner-escalated, unremediated defect tracked by **WI-5311** and **WI-5339**, both
live at stage `backlogged`, priority `P0`. The proposal's blast-radius section
quantifies 21 expiry-bearing rows against a reported 340-row denial reality, and
its Non-Impairment Disposition asserts "ordinary content and owner hand edits are
unaffected."

**Impact.** Three denial paths that fire on the majority of real PAUTHs would
ship with no fixtures, alongside a non-impairment claim that live data
contradicts, and an undeclared dependency on two unresolved P0 work items.

**Calibration.** Bounded to the `gt bridge file-implementation-proposal` CLI
surface; `.claude/skills/gtkb-bridge-propose/helpers/write_bridge.py` does not
route through `proposal_filing.py`. Not a whole-bridge outage. The denials are
also *correct* under `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
— the defect is disclosure, sequencing, and test coverage, not enforcement
direction.

**Recommended action.** Add the three reason codes to the disposition table with
recovery routes; replace the 21-row blast-radius figure with the measured
distribution; add WI-5311 and WI-5339 to Cross-Thread Coordination with an
explicit sequencing statement; add fixtures for each undisclosed code; correct
the Non-Impairment Disposition.

## Finding A2 (P2) — WI-5458: `--create-missing-state` membership creation remains an authority-broadening vector

*Confidence: delegated analysis, not personally re-executed.*

**Claim.** Section 1a makes active membership load-bearing for empty-include-list
coverage, but the standalone membership-creation branch is not retired, so a
filer can mint the coverage predicate for a pre-existing blanket PAUTH.

**Evidence.** `proposal_filing.py:247-261` creates membership in a branch
independent of PAUTH creation at `:269-293`. Section 4 of `-007` addresses only
the PAUTH-creation branch. `_require_owner_decision` at `proposal_filing.py:207-211`
validates existence only (`db.get_deliberation(delib_id) is None`) with no scope
check. Collides with
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` Deterministic
Precedence rule 6: "Backlog or project membership never substitutes for explicit
current authorization coverage."

**Recommended action.** State whether standalone membership creation is retired,
gated, or retained; if retained, bar a newly created membership from satisfying
empty-list fallback in the same invocation, and add the corresponding fixture.

---

## Finding B1 (P1) — WI-5718: an undeclared write target would overwrite existing immutable approval evidence

*Confidence: verified directly in this session. Established.*

**Claim.** `bridge/gtkb-wi5718-retired-session-role-authority-purge-009.md`
instructs implementation to regenerate an approval packet at a path that is not
in `target_paths`, that already exists on disk holding a different amendment's
evidence, and whose filename violates the proposal's own naming rule.

**Evidence — all three legs checked in this session:**

1. **The instruction exists.** `Select-String` over `-009.md` for
   `PAUTH-WI5679-REMOVE-RETIRED-GOV` returns exactly one hit, at **L630**, in
   prose: the packet "must be regenerated and owner-approved against the current
   row before mutation."
2. **It is not in `target_paths`.** L630 is the *only* occurrence in the file.
   The `target_paths` declaration at L24 does not contain it. The declaration
   instead carries the complete-identifier form
   `.groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI5679-SESSION-ROLE-KEYING-20260724.json`,
   which does not yet exist.
3. **The named file already exists and holds other evidence.**
   `.groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5679-REMOVE-RETIRED-GOV.json`
   is present: 1359 bytes, last written 2026-07-28 14:26 local. Its content is
   the v1→v2 approval (`action=amend`) for that PAUTH — an amendment that has
   already executed.

Additionally, `-009` classifies `.groundtruth/formal-artifact-approvals/**` as
"Immutable approval evidence; preserve" (L189), and states at L501 that "each
packet filename embeds the complete PAUTH identifier from this list; no ordinal
mapping is used" — the remedy adopted to close the earlier `-004` FINDING-P2-005.
`PAUTH-WI5679-REMOVE-RETIRED-GOV` does not embed the complete identifier.

**Impact.** Compounding, and it fails either way. If the implementation obeys
L630, `scripts/implementation_start_gate.py` blocks the write as outside the
GO'd `target_paths` — mid-transaction, after postimage drafting, during owner
packet solicitation. If the write somehow proceeds, it overwrites the v2
approval evidence with a v3 postimage under the same filename and a different
SHA-256, so any later audit of the v2 amendment retrieves a packet describing v3.
That is destruction of exactly the audit trail this work item exists to protect.

**Recommended action.** One-line correction: name the declared `target_paths`
entry as the WI-5679 postimage packet, state that it is newly created rather
than regenerated, and record
`2026-07-28-PAUTH-WI5679-REMOVE-RETIRED-GOV.json` as immutable v1→v2 evidence
that this implementation does not write.

## Finding B2 (P1) — WI-5718: the owner-approved scope sentence does not name the project-authorization, test-record, or project-record classes

*Confidence: delegated analysis; the packet quotation should be re-read before
acting.*

**Claim.** The scope text the owner saw and approved stops short of the largest
and most authority-consequential mutation class in the proposal.

**Evidence.**
`.groundtruth/formal-artifact-approvals/2026-07-28-PAUTH-WI5718-RETIRED-ROLE-AUTHORITY-PURGE.json`
`full_content` reads: "...removing the retired identifier and harness-scoped
worker-role authority from every active registered rule, manifest, interface map,
document, test, generated projection, **current specification, and current
work-item projection**." The enumeration names no project-authorization class, no
project record, and "test" is ambiguous between test files and test artifacts.
`DELIB-202667220` similarly enumerates file surfaces. Meanwhile `-009` amends 37
active PAUTH rows spanning roughly 15 other projects, plus 10 test records and 1
project record, resting the authority on the `metadata` and `governance_evidence`
mutation classes rather than on the scope sentence.

Mutation classes describe *how* a change is classified; `scope_summary` is the
owner-facing statement of *what* is in scope. The proposal's inline PAUTH
envelope JSON at `-009.md:42-85` omits `scope_summary`, so prior field-for-field
envelope comparisons would not have surfaced the narrowing sentence.

**Impact.** A GO authorizes appending new versions to 37 active authorization
envelopes that gate implementation for other projects, plus 52 owner packet
presentations in one session. The proposal's controls are strong — exact
postimages, a no-widening rule, before/after envelope comparison, per-row owner
packets — but the authority to touch the class at all is inferential.

**Anti-recycling disclosure.** The adjacent concern was raised and rated
non-blocking three times (`-004` FINDING-P2-004, `-006` FINDING-P2-3, `-008` N4).
This escalation rests on evidence none of those examined — the approval packet's
own scope sentence. If the owner reads that sentence as covering all MemBase
record classes, this collapses to P3.

**Recommended action.** Any one of: a single `AskUserQuestion` confirming the
project-authorization, test-record, and project-record classes are in scope; an
exact-content amendment to the WI-5718 PAUTH `scope_summary` naming those
classes; or deferral of the 37-PAUTH and 1-project class to a follow-on work
item.

---

## Owner Decision Needed

None blocking at advisory stage. Finding B2's remedy path (a) would be an owner
`AskUserQuestion` if Prime Builder selects that route, and Finding A1's rollout
question (ship fail-closed now / sequence behind WI-5311 and WI-5339 / stage
warn-then-enforce) is an owner decision if Prime Builder converts A1. Neither is
raised here; both belong to the owner-grilling gate that applies when Prime
Builder dispositions this advisory per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Recommended Prime Action

1. **Before running `scripts/implementation_authorization.py begin` on WI-5718**,
   resolve Finding B1. It is verified, cheap to fix, and will otherwise halt the
   implementation mid-transaction regardless of the GO. This is the single
   highest-value item in this advisory.
2. **Disposition Finding B2** by one of its three remedy routes before the
   37-PAUTH class is touched.
3. **Re-verify Findings A1 and A2** against live data, then disposition. If A1's
   measurement holds, WI-5458 should not begin implementation without the
   disclosure and fixture work.
4. Where a finding survives re-verification, the governed route is a fresh
   `REVISED` on the affected thread rather than an implementation-time patch, so
   the corrected scope receives its own review.

## Classification Slot

`adapt` — the underlying proposals are sound in design and the GO verdicts are
well-formed; these are bounded corrections to scope disclosure and one
declaration defect, not a rejection of either thread's approach.

## Prior Deliberations

_No prior deliberations: this advisory records findings generated in this session
against two bridge threads whose own version chains already carry the relevant
deliberation citations (`-007` and `-009` respectively). The findings are new to
those chains; a deliberation search for prior treatment of the WI-5311 /
WI-5339 PAUTH-taxonomy remediation sequencing is a reasonable step for Prime
Builder during disposition of Finding A1._

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
