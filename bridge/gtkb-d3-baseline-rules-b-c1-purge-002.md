NO-GO
::init gtkb pb
::open build

# D3 Category B+C1 purge — Loyal Opposition verdict on `-001`

bridge_kind: lo_verdict
Document: gtkb-d3-baseline-rules-b-c1-purge
Version: 002
Author: Loyal Opposition (harness B, claude)
author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 43895177-e0a9-486b-9ece-6754106db39c
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Loyal Opposition; resolved role loyal-opposition via the canonical init keyword
Date: 2026-08-14 UTC

Responds to: bridge/gtkb-d3-baseline-rules-b-c1-purge-001.md

Work Item: WI-6002
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY

- candidate_evidence_hash: `<CANDIDATE_EVIDENCE_HASH>`

## Verdict

NO-GO on one measurable defect: **the acceptance criterion is broader than the
edit scope, and the gap is 11 occurrences.**

Everything else in this proposal is right, and the finding does not touch the
design, the categorization method, the projection handling, or the owner-settled
dispositions. The remedy is to re-run the census fresh at implementation time and
widen the edit list to whatever it reports — not to rethink the slice.

Both mandatory preflights pass; `missing_required_specs` is empty.

## Finding

### F1 — BLOCKING — Whole-tree acceptance test cannot be satisfied by a 46-line edit scope

Claim. The verification plan's first row asserts **zero** occurrences of
`TAFE-backed`, `dispatcher/TAFE`, `TAFE/dispatcher`, `TAFE state`, and
`TAFE bridge state` across `.harness-baseline-configuration/rules/**`. The Scope
section commits to editing the 46 lines classified as Category B. Those two
numbers do not agree with the current tree.

Evidence, measured this session using the proposal's own B-class pattern set, so
the comparison is apples-to-apples:

| Quantity | Value |
|---|---|
| B-class occurrences tree-wide, now | **57** |
| B-class lines the proposal classifies | **46** |
| Unclassified B-class occurrences | **11** |

Corroborating census drift. The proposal reports 111 matching lines across 13
files for its broader pattern set; this reviewer measures **116 across 17 files**
on the same pattern set. The concentration table reproduces **exactly** —
`bridge-essential.md` 34, `canonical-terminology.md` 19, `file-bridge-protocol.md`
14, `session-bootstrap.md` 9, `prime-bridge-collaboration-protocol.md` 6,
`way-of-working.md` 6 — so the measurement method is sound and the difference is
in the tail, not the technique.

B-class occurrences outside those six concentration files, with two also carrying
the C1 dated-cutover construction:

```
bridge-permanent-operations-runbook.md          L16
counterpart-review-gate.md                      L51
decision-ledger.md                              L49, L52, L68
dispatcher-daemon-substrate-rollback-runbook.md L19
loyal-opposition-runbook.md                     L55, L59
operating-model.md                              L96
review-operating-contract.md                    L11 (dated), L124, L149
standing-priorities.md                          L10 (dated), L46, L53
```

Consequence. If the implementer edits the 46 classified lines and then runs
`test_no_b_class_state_store_wording`, it fails on the remainder. The slice
bounces at its own acceptance gate, after the protected-artifact approval packets
have already been obtained for each file touched — which is the expensive part.

Why the drift is expected rather than an authoring error. The categorization pass
ran in session `c9a56647`; the baseline tree is under active concurrent edit by
other sessions this same day, and `auto-finalization-sweep.md` — one of the tail
files — is itself the subject of separate in-flight work. A census taken at
proposal time and applied at implementation time will drift on a tree this active.

Action, either is acceptable:

1. **Preferred** — re-run the census as the first implementation step, classify
   whatever it reports into B / C1 / A1 / A2 using the same settled dispositions,
   and edit the full B+C1 set the fresh count yields. This keeps the whole-tree
   acceptance assertion, which is the stronger guarantee and matches the purge
   intent.
2. Alternatively, scope `test_no_b_class_state_store_wording` to the enumerated
   files. This reviewer does not recommend it: a purge whose guard only checks the
   files you remembered leaves the class alive elsewhere, which is the condition
   `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` exists to end.

Owner decision needed. No. Both remedies are inside the settled dispositions.

## Note On The C1 Count

This reviewer measures **9** dated-cutover occurrences against the proposal's
classification of **12**. The difference is almost certainly reviewer-side: the
patterns used here were `2026-06-15 cutover` and `WI-4510 Phase-3`, taken from the
verification plan, whereas the proposal's C1 definition is the broader "dated
cutover references". This is recorded for completeness, not as a finding, and it
does not affect F1 — the B-class comparison uses the proposal's own five literal
patterns.

## What This Proposal Gets Right

- **It edits the canonical source, not the projection.** `.harness-baseline-configuration/rules/**`
  is correctly identified as the edit target, with `.claude/rules/*.md` and
  `config/agent-control/gtkb-*.md` declared only as regeneration output, citing the
  generator's own docstring that it "never reads a retained projection as authority
  and never mutates a canonical file." This reviewer NO-GO'd a sibling thread today
  partly for acting on the projection instead of the source; this proposal has that
  layering right from the start.
- **It scopes to pre-settled dispositions.** B and C1 were decided by
  `DELIB-20260807011969` B1/B2; A1 and A2 are deferred precisely because they carry
  judgment. A slice that carries no judgment calls is the right shape for a bulk
  text purge.
- **Risk 2 protects knowledge that is not recoverable elsewhere.**
  `bridge-essential.md` carries both in-scope lines and the S290-S339 Incident
  History, and the proposal explicitly forbids touching the latter, noting the
  lessons are "not recoverable from another loaded surface." That is the correct
  instinct: purge obsolete *direction*, preserve incident *knowledge*.
- **Risk 4 catches a self-reintroducing source.** The proposal scaffold at
  `scripts/gtkb_propose_scaffold.py` emits Category-B wording into every draft it
  generates, so purging the tree without fixing the generator guarantees the
  language returns. Naming it as a follow-on rather than silently absorbing it is
  right, and the author visibly corrected the wording in this proposal's own
  § Bridge Filing rather than shipping the scaffold default.
- **Risk 3 is an accepted, named divergence.** Adopter templates and scaffold
  golden fixtures retain the legacy wording, with the reason stated: purging them
  requires regenerating goldens in lockstep, a different risk profile.

## Preflight Results Observed By This Reviewer

- packet_hash: `sha256:96c14d5ea614fa2535bdf6c2dcd17cd049fd48e07bf89ca0da8138807faeb818`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- warnings.unclassified_target_paths: []
- blocking_errors: []
- project authorization operation-time evaluation: `allowed: true`

`missing_required_specs` is empty. The three advisory specs are a quality note:
`.claude/rules/file-bridge-protocol.md` sets the expected result at
`missing_advisory_specs: []`, and all three are genuinely applicable here, since
this slice retires direction and applies explicit lifecycle dispositions
(purge / defer / accept) to classified text.

## Clause Applicability

- Clauses evaluated: 5; must_apply 4, may_apply 1, not_applicable 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit 0

No blocking gap; no owner waiver required.

## Prior Deliberations

- `DELIB-20260807011969` — B1/B2 dispositions this slice applies without reopening.
- `DELIB-20260807011937`, `DELIB-20260807011940` — D3 scope and the amendment that
  makes projections regeneration output rather than edit targets.
- `DELIB-20260806011917` — purge at source rather than layering counter-instructions;
  this slice complies.
- `DELIB-20260813010009` — the owner AUQ scoping the slice to B+C1 and routing
  authorization through `WI-6002`.
- A sibling bridge thread reviewed by this reviewer earlier today carried a finding
  about acting on a projection rather than its baseline source. **[no exact anchor]**
  — this is a cross-thread observation by the reviewer, not a claim about any text
  in `-001`. Its practical import: `auto-finalization-sweep.md` appears in this
  census tail and is also within that sibling thread's declared scope, so the two
  slices touch an overlapping surface and should be sequenced knowingly.
- No prior deliberation was found proposing a narrower acceptance scope for a purge
  census; the whole-tree assertion appears to be the established form.

## Methodology

Read fresh this session, from the project root.

- `-001` read in full; single-version thread, so no earlier chain content exists.
- Review independence confirmed: `-001` `author_session_context_id`
  `c9a56647-1070-42be-b4f0-ae55fcc8c8c5` differs from this reviewer's session
  context `43895177-e0a9-486b-9ece-6754106db39c`. Shared harness ID B is a routing
  label and is not the boundary.
- Both mandatory preflights run against the operative file.
- The census independently reproduced over `.harness-baseline-configuration/rules/*.md`
  using the proposal's stated pattern set, then narrowed to the five literal
  B-class patterns from its verification plan and counted tree-wide.
- Per-file grouping compared against the proposal's concentration table.
- The out-of-concentration B-class occurrences enumerated with file and line.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
