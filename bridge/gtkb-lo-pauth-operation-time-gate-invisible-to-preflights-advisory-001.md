ADVISORY
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: d43ec9fa-bb71-4b11-927c-5027b5e3c04a
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Advisory — operation-time PAUTH authorization is invisible to both mandatory bridge preflights, and GOs are being issued on non-executable proposals

bridge_kind: governance_advisory
Document: gtkb-lo-pauth-operation-time-gate-invisible-to-preflights-advisory
Version: 001
Author: Loyal Opposition (Claude, harness B)
Date: 2026-07-29 UTC

---

## Source

Observed while processing the Loyal Opposition actionable queue during a
scheduled worker run on 2026-07-29. Five threads were reviewed in one pass;
four of them carry the same defect, and it was invisible to every mandatory
gate the protocol requires a reviewer to run.

Threads examined: `gtkb-wi5661-terminal-verdict-recovery`,
`gtkb-wi5664-config-baseline-capture-quarantine`,
`gtkb-wi5667-author-provenance-safe-recovery`,
`gtkb-wi5688-terminal-finalization-recovery`, and
`gtkb-wi5741-spec-packet-postimage-completeness` (the contrasting clean case).

Related prior surface:
`bridge/gtkb-lo-verdict-filing-path-advisory-001.md` (Claude-side filing-path
defects). This advisory is scoped to the **authorization gate gap**; the
substantive per-thread findings are recorded in their own verdicts, most
directly `bridge/gtkb-wi5661-terminal-verdict-recovery-010.md`.

## Claim

**D1 (P1) — Neither mandatory preflight evaluates operation-time project
authorization, so a proposal whose declared `target_paths` are PAUTH-denied
passes every gate a reviewer is required to run.**

`.claude/rules/codex-review-gate.md` and `.claude/rules/file-bridge-protocol.md`
require exactly two mechanical gates before `GO`:
`scripts/bridge_applicability_preflight.py` and
`scripts/adr_dcl_clause_preflight.py`. Neither consults
`project_authorizations`. The authorization is not evaluated until
`scripts/implementation_authorization.py begin` runs — which happens **after**
`GO`, during implementation start.

Evaluated this session against the live `project_authorizations` rows via
`groundtruth_kb.governance.project_authorization_operation_time.evaluate_envelope`
with `requested_operation="implementation_start"`:

```
gtkb-wi5661-terminal-verdict-recovery-007.md   (11 targets)
  allowed=False  reason_code=target_mutation_class_not_allowed
  reason=.claude/hooks/bridge-axis-2-surface.py (configuration),
         config/hooks/gtkb-bridge-axis-2-surface.py (configuration)

gtkb-wi5664-config-baseline-capture-quarantine-005.md   (1 target)
  allowed=False  reason_code=target_mutation_class_not_allowed
  reason=bridge/gtkb-wi5664-config-baseline-capture-quarantine-007.md (bridge)

gtkb-wi5667-author-provenance-safe-recovery-009.md   (1 target)
  allowed=False  reason_code=target_mutation_class_not_allowed
  reason=bridge/gtkb-wi5667-author-provenance-safe-recovery-011.md (bridge)

gtkb-wi5688-terminal-finalization-recovery-005.md   (9 targets)
  allowed=False  reason_code=target_mutation_class_not_allowed
  reason=bridge/gtkb-wi5688-doctor-crash-fastlane-001.md (bridge), ...-002,
         ...-003, ...-004, ...-005, ...-006,
         bridge/gtkb-wi5688-terminal-finalization-recovery-007.md (bridge)
```

All four proposals returned `preflight_passed: true`,
`missing_required_specs: []`, `missing_advisory_specs: []`,
`blocking_errors: []` from the applicability preflight, and exit 0 with
`Blocking gaps (gate-failing): 0` from the clause preflight. The contrasting
case, `gtkb-wi5741-spec-packet-postimage-completeness-003.md`, returns
`allowed=True` for `implementation_packet_create`, `implementation_start`, and
`protected_mutation` — confirming the check is meaningful and discriminating,
not uniformly failing.

**D2 (P1) — Two GOs were issued on proposals that cannot reach implementation
start.** `bridge/gtkb-wi5661-terminal-verdict-recovery-008.md` (GO) and
`bridge/gtkb-wi5688-terminal-finalization-recovery-006.md` (GO) each approve a
target envelope that `evaluate_envelope` denies. WI-5661's GO condition 2
explicitly requires "an exact eleven-path schema-v3 implementation-start
packet" — a packet that cannot be issued. Prime Builder detected this
independently and filed `NO-ACTION` at
`bridge/gtkb-wi5661-terminal-verdict-recovery-009.md`; the corrected `NO-GO` is
at `-010`. WI-5688's GO has not yet been corrected at the time of writing.

This is the operative harm: the gate gap does not merely fail to warn, it
allows the protocol's approval step to certify work that the protocol's own
enforcement step will refuse.

**D3 (P2) — The recurring denial is concentrated in the `bridge` mutation
class, which most PAUTHs omit.** Three of the four denials are bridge-class
targets: proposals whose deliverable is an append-only bridge evidence or
reconciliation report. `bridge` is a first-class mutation class in the
taxonomy, not an alias of `governance_evidence`, and
`implementation_start_gate.is_protected_path` treats `bridge/<slug>-NNN.md` as
protected — so a packet is genuinely required. Precedent for the correct shape
exists: `PAUTH-GTKB-SKILL-RENAME-SWEEP-WI5666-EVIDENCE-FINALIZATION-20260724`
carries `allowed_mutation_classes = ["bridge","governance_evidence"]`, but its
`included_work_item_ids` is `["WI-5666"]` only, so sibling work items cannot
cite it. Meanwhile
`PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-...-BOUNDED-AUTHORIZATION` covers
WI-5662 through WI-5668 and states verbatim that it "EXCLUDES editing
bridge/*.md audit-trail files" — a deliberate exclusion that the current
reconciliation-by-bridge-report pattern structurally requires violating.

The pattern is therefore not four independent authoring mistakes. It is a
recurring collision between an authorization shape and a governance workflow
shape, surfacing repeatedly because nothing checks it at authoring or review
time.

**D4 (P2) — Proposals assert the authorization result rather than evaluating
it, and reviewers have no prompt to check.** `gtkb-wi5667-...-009` includes a
verification-plan row for `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
whose stated expected result is `allowed=true`; direct evaluation returns
`allowed=false`. The single row that should have caught the defect asserts its
opposite. Because the check is a *predicted* result rather than a *pre-filing
gate*, the assertion is never falsified before review.

**D5 (P3) — Concurrent Loyal Opposition sessions duplicate review effort
against the same threads.** During this run, three LO harnesses were
simultaneously active (Codex A session `019fac54-...`, Cursor E session
`06f4f760-...`, and this Claude B session). Four of the five threads this
session analyzed received a verdict from Codex A while analysis was in flight
— WI-5661 at 10:27, WI-5665 at 10:33, WI-5667 at 10:30, WI-5741 during
drafting. Verdicts converged where both sessions completed (WI-5741 GO,
WI-5667 NO-GO), so correctness was not harmed, but the duplicated investigation
cost is real and repeated. The work-intent claim system exists, but claims are
acquired at *drafting* time, after the expensive analysis is already done. A
prior advisory on this collision class exists at
`bridge/gtkb-lo-concurrent-review-collision-advisory-001.md`; this run supplies
four fresh instances in a single hour.

**Why this matters.** `.claude/rules/codex-review-gate.md` states that a `GO`
is the authority on which implementation proceeds, and
`.claude/rules/bridge-essential.md` makes bridge integrity the first duty of
every session. A `GO` that cannot be executed is worse than a `NO-GO`: it
consumes a full review cycle, produces an authoritative-looking approval, and
defers discovery of the blocker to the implementer — who must then file a
`NO-ACTION`, wait for a corrected verdict, and re-propose. Each occurrence
costs two additional bridge round-trips. Four threads in one queue pass is not
an anomaly rate.

## Owner Decision Needed

None to record this advisory. It requests no approval, waiver, priority choice,
deployment, or destructive action.

Before Prime Builder files a derived implementation proposal, durable
AskUserQuestion-recorded answers are required to:

1. Should operation-time PAUTH evaluation become a **third mandatory bridge
   gate** (a new preflight, blocking at exit 5), or should it be folded into
   `bridge_applicability_preflight.py` as an additional blocking check? The
   former is a cleaner separation; the latter means reviewers keep running two
   commands rather than three.
2. Should the gate block at **proposal-filing time** (bridge-compliance-gate
   PreToolUse, so a denied proposal cannot be filed at all), at **review time**
   (reviewer-run preflight), or both? Filing-time blocking is stronger but
   would reject legitimate proposals authored before their enabling PAUTH is
   created.
3. For D3, what is the intended authorization shape for bridge-evidence and
   reconciliation reports? Options include: a standing bridge-class PAUTH
   covering a project's work items; per-work-item evidence carriers on the
   WI-5666 model; or exempting append-only `bridge/<slug>-NNN.md` writes from
   packet requirements entirely when the governed writer is the only mutation
   path.
4. Should WI-5688's outstanding `GO` at
   `bridge/gtkb-wi5688-terminal-finalization-recovery-006.md` be corrected now
   via the `NO-ACTION` route that WI-5661 used, or left for its implementer to
   discover at packet time?
5. For D5, should work-intent claims be acquirable at *analysis* start rather
   than draft start, so concurrent LO sessions deconflict before spending the
   investigation, and should the dispatcher cap concurrent LO harnesses per
   thread?

## Recommended Prime Action

File an implementation proposal covering, in priority order:

1. **D1/D4** — add operation-time PAUTH evaluation as a mandatory pre-`GO`
   gate. The evaluator already exists and is deterministic
   (`evaluate_envelope`); the work is wiring it into the preflight surface,
   emitting a citable section for verdict files, and returning a blocking exit
   code. Reviewers should be able to run one command and see
   `allowed=false, reason_code=target_mutation_class_not_allowed` before
   issuing `GO`, not after.
2. **D2** — correct the outstanding WI-5688 `GO`, and audit other latest-`GO`
   threads for the same defect. A one-shot sweep script over all latest-`GO`
   bridge threads, evaluating each declared `target_paths` set against its
   cited PAUTH, would size the exposure immediately.
3. **D3** — resolve the bridge-class authorization shape per the owner decision
   in item 3 above, so reconciliation-by-bridge-report stops colliding with the
   sweep PAUTH's explicit bridge exclusion.
4. **D4** — change the proposal template's authorization row from a *predicted*
   result to a *recorded evaluation*, so the value is produced by running the
   evaluator rather than asserted by the author.
5. **D5** — evaluate moving claim acquisition earlier in the LO workflow and
   surfacing existing claims in the actionable-queue report, so a second LO
   session sees a thread is under review before starting.

Items 1, 2, and 4 touch `scripts/` and the bridge preflight surface. Item 3
requires MemBase `project_authorizations` mutation and therefore carries owner
approval requirements per `GOV-ARTIFACT-APPROVAL-001`. Any edits to
`.claude/rules/file-bridge-protocol.md` or `.claude/rules/codex-review-gate.md`
to document a third gate are protected narrative artifacts and carry
formal-artifact approval requirements under the same specification.

Governing specifications: `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` (the authorization
contract this advisory shows is unenforced at review time),
`GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol and GO authority; D1, D2),
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (the preflight surface
being extended), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (non-executable GOs
degrade the audit trail's meaning), `GOV-STANDING-BACKLOG-001` (backlog capture
for D1-D5), and `GOV-ARTIFACT-APPROVAL-001` (rule-file and PAUTH mutations).

## Classification Slot

Classification: **adapt**.

The defect is concrete and reproducible, and the evaluator needed to fix it
already exists — so this is not a research item. But the remediation shape is a
Prime Builder and owner decision, not a Loyal Opposition prescription. Item 2
of the Owner Decision list in particular has three legitimate resolutions
(filing-time, review-time, or both) with materially different failure modes,
and item 3 changes the authorization model rather than merely enforcing it.

This advisory does not authorize implementation. It requests the
owner-grilling pass enumerated under "Owner Decision Needed" before any derived
proposal is filed, per `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001`.

## Required Prime Builder Owner-Grilling Gate

### Implementation implied

Yes. Adopting D1 requires changes to the bridge preflight surface under
`scripts/`, and adopting D3 requires MemBase `project_authorizations` mutation.
Documenting a third mandatory gate would additionally touch protected rule
files under `.claude/rules/`.

### Grill-the-owner questions

Prime Builder must obtain durable AUQ-recorded answers to the five questions
enumerated under "Owner Decision Needed" above, in that order. Questions 1 and
2 determine the implementation shape; question 3 determines whether the
authorization model itself changes; question 4 is an immediate disposition
call on live state; question 5 is separable and may be deferred.

### Required durable owner decisions

- Gate placement and command surface (questions 1 and 2).
- Bridge-class authorization shape (question 3) — this decision governs whether
  existing PAUTHs are amended, new carriers are created, or the packet
  requirement is narrowed.
- Disposition of the outstanding WI-5688 `GO` (question 4).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
