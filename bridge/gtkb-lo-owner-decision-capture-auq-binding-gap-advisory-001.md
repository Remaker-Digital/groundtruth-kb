ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 8acb741f-f238-438e-940c-49bdf36ca8fd
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session-envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# LO Advisory - Owner-Decision Records Written By The Decision-Capture Skill Carry No AUQ Binding, So A Governance Posture Change Cannot Be Distinguished From Agent Self-Authorization

bridge_kind: governance_advisory
Document: gtkb-lo-owner-decision-capture-auq-binding-gap-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-28

---

## Source

Discovered while verifying
`bridge/gtkb-wi5441-global-registry-membership-reconciliation-017.md` and filing
the NO-GO at `-018` in this session. The WI-5441 thread's remaining blocker (F1)
is an instance of this platform-level gap; the gap itself is out of that thread's
scope, so it is filed separately here.

Evidence sources, all read directly this session:

- `.claude/skills/gtkb-decision-capture/helpers/record_decision.py` - fixed
  `source_type` / `outcome` constants and `changed_by` attribution.
- `gt deliberations record --help` - `--source-ref`, `--auq-id`, `--auq-answer`
  marked `[required]`; `--owner-presented` available.
- `gt deliberations show DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` -
  `source: owner_conversation: -`, no AUQ binding, no owner utterance.
- `gt deliberations show DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` -
  same skill, same empty `source_ref`, owner utterance present.
- `gt deliberations show DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` -
  points 8 and 9 establish a quarantine-then-automatic-deletion path.

## Claim

GT-KB has two write paths that both produce Deliberation Archive rows with
`outcome='owner_decision'`. One requires machine-checkable owner evidence; the
other requires none and hardcodes the fields that would otherwise signal
provenance. Nothing at read time distinguishes their output.

**Path A - governed, evidence-bearing.** `gt deliberations record` is documented
as "Record an AUQ-backed deliberation through the governed service path." Its
`--help` marks `--source-ref`, `--auq-id`, and `--auq-answer` as `[required]`.

**Path B - skill, evidence-free.** `record_decision.py` sets
`source_type='owner_conversation'` and `outcome='owner_decision'` as fixed
constants not exposed to the caller, with
`changed_by = "prime-builder/decision-capture-skill"`. It requires no
`source_ref`, no AUQ identifier, no owner answer text, and no assertion that
anything was presented to the owner.

**Why this matters, concretely.**
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` records an owner posture
selection determining whether approximately 278 uninspectable filesystem objects
are classified `unregistered_disposable`. Under `DELIB-20260722` points 8 and 9,
`unregistered_disposable` in-scope artifacts are quarantined and then
**permanently deleted automatically** after 30 days. That record contains no AUQ
id, no question as presented, no options as presented, and no quoted owner
response - only third-person assertion that the owner selected posture A.

**Four deficiency rationales.**

1. The governance stack assumes owner-decision records are owner-attributable.
   `GOV-ARTIFACT-APPROVAL-001` and the AUQ-only enforcement stack exist to make
   owner authority auditable. A record class asserting owner authority without
   owner evidence silently defeats that.
2. The read-time check a reviewer would naturally perform does not work.
   Checking `source_type == 'owner_conversation'` and
   `outcome == 'owner_decision'` looks like verification but is tautological on
   Path B - those values are writer constants, not observations.
3. It is not a harness-capability limitation. `AskUserQuestion` is Claude-native,
   so a Codex-as-Prime session cannot emit AUQ tool evidence - but
   `gt deliberations record` is a harness-agnostic `gt` CLI with the
   required-evidence contract already implemented. The gap is that nothing routes
   owner-decision capture to it or requires equivalent evidence on the skill path.
4. The failure is silent and permanent. Deliberations are append-only; a record
   filed without owner evidence cannot later be shown to have had it.

**The capability exists and is sometimes used.** `DELIB-20260727`, written by the
**same skill** one day earlier on the **same work item**, preserves the owner's
actual words ("the owner replied **Approved as stated** ..."). Owner-utterance
capture is achievable on Path B today - it is discretionary prose, not a contract.

**Explicit non-claim.** This advisory makes **no allegation that any owner
decision was fabricated.** Loyal Opposition cannot read another harness's
transcript. The claim is narrower and verifiable: the records do not carry the
evidence, and the read surfaces cannot distinguish bound from unbound.

## Owner Decision Needed

Per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`, this advisory is classified
`adapt`, so Prime Builder must obtain durable, recorded answers to the following
before filing any derived implementation proposal:

1. **Fail-closed or downgrade?** When an owner-decision capture has no AUQ
   binding, should the write be refused outright, or written with
   `outcome='informational'` plus a visible unbound marker?
2. **What counts as sufficient owner evidence** for a harness that cannot emit
   native AUQ tool evidence - an owner-response quotation, a transcript
   reference, an operator-supplied source ref, or all three?
3. **What disposition for the existing unbound corpus?** Leave as-is with a
   read-time marker, triage only those cited by live bridge threads, or require
   re-capture for a named subset?
4. **Does this apply retroactively to threads currently in flight**, specifically
   the WI-5441 posture record that occasioned this advisory?

Answers 1, 2, and 3 are required before an implementation proposal exists.

## Recommended Prime Action

Adopt the evidence contract; adapt the capture surface. Suggested scoping:

1. **Require owner evidence on the skill path.** Extend `record_decision.py` so
   that writing `outcome='owner_decision'` requires at least one of: an AUQ
   identifier, a non-empty `source_ref`, or a verbatim owner-response quotation
   field. Fail closed otherwise, or downgrade `outcome` to `informational` -
   per the owner's answer to question 1.
2. **Make evidence state visible at read time.** Surface an explicit evidence
   indicator in `gt deliberations show` so a reviewer sees "AUQ-bound" vs
   "unbound assertion" without reading the writer's source.
3. **Triage, do not rewrite.** Enumerate existing `outcome='owner_decision'` rows
   with empty `source_ref` and present the count to the owner. Do not
   retroactively rewrite them; append-only discipline applies.
4. **Cross-harness parity.** Ensure Codex/provider harness paths route
   owner-decision capture through the evidence-bearing surface, since those
   harnesses cannot emit native AUQ tool evidence.

Prime Builder should conduct the owner-grilling pass above, record the answers,
and only then file a NEW implementation proposal citing this advisory as its
source. This advisory authorizes nothing by itself.

## Classification Slot

Classification: `adapt`

The core pattern - owner-decision records must carry owner evidence - is adopted
as-is. The surface is adapted: the mechanism cannot be literal `AskUserQuestion`
evidence, because non-Claude harnesses have no such tool. The harness-agnostic
`gt deliberations record` evidence contract is the adaptation target.

Related but distinct, and already covered elsewhere: verdict-filing tooling
friction is documented in `gtkb-lo-tooling-defect-advisory-001` through `-011`
and `gtkb-lo-verdict-filing-path-advisory-001`. This advisory deliberately does
not duplicate that corpus.

## Prior Deliberations

Searched the Deliberation Archive for prior decisions on owner-decision capture
evidence, AUQ binding, and deliberation provenance.

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - establishes
  the deletion path whose safety depends on owner-decision integrity.
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - demonstrates the
  achievable evidence shape on the same skill path.
- `DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` - the instance record.

_No prior deliberation found on the owner-decision capture evidence contract
itself; this appears to be first-of-kind._

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
