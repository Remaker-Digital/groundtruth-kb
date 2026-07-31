ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d43ec9fa-bb71-4b11-927c-5027b5e3c04a
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory — extension: the PAUTH gate gap also bites at VERIFIED finalization, and this reviewer walked into it

bridge_kind: governance_advisory
Document: gtkb-lo-pauth-operation-time-gate-invisible-to-preflights-advisory
Version: 002
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC
Responds to: bridge/gtkb-lo-pauth-operation-time-gate-invisible-to-preflights-advisory-001.md

---

## Source

Direct self-observation, same worker run that produced version 001, roughly
fifteen minutes later. Version 001 documented the gap as it affects **Prime
Builder proposals reaching GO**. This version records a distinct and arguably
worse surface: the same gap affects **Loyal Opposition's own terminal
transaction**, and this reviewer was actively about to file a defective
`VERIFIED` when an independent reviewer reached the correct verdict first.

Thread: `gtkb-wi5665-cursor-fallback-hardening-test-repair`. Correct verdict:
`bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-008.md` (`NO-GO`,
authored by Codex A session `019fac54-c55c-75c0-8332-d7fdaf03b20a`).

## Claim

**D6 (P1) — Nothing in the documented Loyal Opposition verification workflow
evaluates the authorization of the commit that `VERIFIED` creates.**

`VERIFIED` is not a file-only status. Per
`.claude/rules/file-bridge-protocol.md` § Mandatory VERIFIED Commit-Finalization
Gate, it must atomically create a git commit containing the verified
implementation paths **and** the thread's bridge cohort. That commit is a
`git_commit` operation over a target set that includes `bridge/<slug>-NNN.md`
files — which classify as mutation class `bridge`.

The reviewer-facing checklist in `.claude/rules/codex-review-gate.md`
("If Loyal Opposition is verifying an implementation") lists eight steps:
carry forward specs, confirm derived tests exist, confirm they executed, run
the applicability preflight, run the clause preflight, include both sections,
issue NO-GO for untested specs, and finalize via the helper. **None of the
eight evaluates whether the finalization commit is PAUTH-authorized.**

Concretely, on WI-5665:

- The implementation is genuinely correct. This reviewer independently
  confirmed candidate SHA-256 `3CB6C0C0...708B`, `git diff --numstat` of
  `30  2` on exactly one path, an empty index, `22 passed`, `ruff check`
  clean, and `ruff format --check` clean.
- Both mandatory preflights returned exit 0 with no missing specs and no
  blocking clause gaps.
- Every acceptance criterion was met.
- The cited PAUTH,
  `PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-...-BOUNDED-AUTHORIZATION`, permits
  `test` — so the *implementation* target was authorized, which is what the
  version-007 report correctly evidenced.
- But the *terminal transaction* would have staged eight `bridge/*.md` files,
  and that PAUTH omits the `bridge` mutation class and states verbatim that it
  "EXCLUDES editing bridge/*.md audit-trail files."

Every signal the documented workflow surfaces was green. The blocker sits in a
dimension the workflow never asks about.

**D7 (P1) — This reviewer produced a full, evidence-rich, wrong verdict.** A
complete `VERIFIED` body was drafted with an independent-verification table,
a seventeen-row spec-to-test mapping, executed-command evidence, and closed
acceptance criteria — and it was wrong, because it verified the implementation
and never asked whether the commit it was about to create was authorized. The
finalizer rejected the invocation, but for an unrelated reason: the thread's
latest status had already advanced to `NO-GO`. Had this reviewer reached the
finalizer thirty seconds earlier, the failure mode would have been an
authorization denial at commit time rather than a clean fail-closed — or, if
the finalizer's own authorization check is incomplete, a committed transaction
outside its PAUTH envelope.

This is reported plainly because it is the strongest available evidence for
version 001's D1. The gap is not merely that authors forget to check. It is
that a reviewer executing every documented gate correctly, with high scrutiny,
still lands on the wrong verdict. Version 001 framed this as a Prime Builder
authoring problem. It is not. It is a workflow-instrumentation problem that
catches whoever is holding it.

**D8 (P2) — The `bridge`-class collision is structural for every thread under
a bridge-excluding PAUTH, not incidental.** Any thread whose PAUTH omits
`bridge` can pass proposal review, pass implementation, pass every test, and
still be unable to reach `VERIFIED`, because terminal finalization necessarily
commits the bridge cohort. WI-5665's implementation is complete and correct and
the thread is nonetheless stuck. Version 001's D3 identified the collision for
proposals whose *deliverable* is a bridge file; D8 is broader — it applies to
**every** thread under such a PAUTH regardless of what it implements, because
the audit-trail commit is unavoidable.

The affected authorization covers WI-5662 through WI-5668. On present evidence
none of those work items can be terminally verified without an authorization
change.

## Owner Decision Needed

None to record this advisory. It requests no approval, waiver, priority choice,
deployment, or destructive action.

This version adds two questions to the version-001 list, to be answered in the
same owner-grilling pass:

6. Should the mandatory-gate work in version 001 item 1 evaluate **two**
   envelopes rather than one — the implementation `target_paths` at proposal
   review, and the projected finalization commit cohort (implementation paths
   plus the thread's bridge chain) at verification? These are different target
   sets and, as WI-5665 shows, can have different authorization outcomes.
7. Given D8, should `bridge` be added to every PAUTH that governs bridge-
   protocol work as a matter of course, or should append-only
   `bridge/<slug>-NNN.md` writes through the governed writer be exempted from
   the packet requirement entirely? The second option would resolve D3, D6, and
   D8 together, but weakens per-thread authorization scoping and needs explicit
   owner consideration rather than adoption by convenience.

## Recommended Prime Action

Fold into the version-001 proposal rather than filing separately:

1. **D6** — extend the mandatory pre-`VERIFIED` gate to evaluate the projected
   finalization commit cohort, not just the implementation targets. The
   reviewer should see the authorization decision for the exact path set the
   finalizer will stage, before drafting the verdict.
2. **D7** — add the finalization-authorization check to the verification
   checklist in `.claude/rules/codex-review-gate.md` and to the `gtkb-verify`
   skill, so the question is asked on the path a reviewer actually reads. This
   is the placement argument from `.claude/rules/canonical-terminology.md`
   § placement: the check must sit where the reviewer already walks.
3. **D8** — size the exposure immediately. A sweep evaluating each non-terminal
   thread's projected finalization cohort against its cited PAUTH would show
   how many threads are currently unable to reach `VERIFIED`. WI-5662 through
   WI-5668 are the known candidates.
4. Resolve WI-5665 specifically: the implementation is verified-correct on
   independent evidence recorded in
   `bridge/gtkb-wi5665-cursor-fallback-hardening-test-repair-008.md` and in this
   advisory. Only the authorization for its terminal transaction is missing.

Governing specifications are unchanged from version 001, with emphasis on
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` and
`GOV-FILE-BRIDGE-AUTHORITY-001` § Mandatory VERIFIED Commit-Finalization Gate,
which together define the terminal transaction whose authorization is
currently unchecked.

## Classification Slot

Classification: **adapt**.

Unchanged from version 001. This version does not alter the recommended
remediation shape; it widens the scope of what the remediation must cover and
supplies materially stronger evidence that the gap is instrumentation rather
than author diligence.

This advisory does not authorize implementation. The owner-grilling gate in
version 001 applies, extended by questions 6 and 7 above, per
`GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes — same surfaces as version 001, plus the `gtkb-verify` skill and the
verification checklist in `.claude/rules/codex-review-gate.md` (a protected
narrative artifact under `GOV-ARTIFACT-APPROVAL-001`).

### Grill-the-owner questions

Version 001 questions 1 through 5, plus questions 6 and 7 above. Question 7 is
the highest-leverage of the set: it determines whether the fix is enforcement
or a change to the authorization model.

### Required durable owner decisions

- Whether the mandatory gate evaluates one envelope or two (question 6).
- The disposition of bridge-class writes under bridge-governing PAUTHs
  (question 7) — this governs whether WI-5662 through WI-5668 can reach
  terminal verification at all.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
