NEW

# GTKB-INCIDENT-RESPONSE — Multi-Phase Implementation Proposal

**Status:** NEW (multi-phase scoping; awaiting Codex review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-INCIDENT-RESPONSE (filed in this proposal)
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** multiphase_implementation_proposal
**Routing:** Mixed.
- **Framework artifacts** (8-phase model, severity schema, postmortem
  schema, fast-path mitigation registry shape) ship upstream to
  `groundtruth-kb`. Adopters consume via `gt project upgrade`.
- **Documents** (CTO 1-page response, walk-through, how-to, LinkedIn
  article) start as Agent Red-local templates in `docs/incident-response/`
  and `docs/articles/`. Generic templates flow upstream as part of the
  `groundtruth-kb` documentation later.
- **Capability slices** (IR-CS-1 through IR-CS-N) file individually
  under this thread or under GTKB-COMMAND-SURFACE depending on
  whether the capability is a `::cmd` (latter) or a back-end primitive
  (former).

bridge_kind: prime_proposal
work_item_ids: [GTKB-INCIDENT-RESPONSE]
spec_ids: []
target_project: mixed (upstream + agent-red)
implementation_scope: framework_documents_and_capabilities
requires_review: true
requires_verification: true (per phase)

---

## 0. What This Proposal Is

A multi-phase plan to formalize GT-KB's incident-response posture as
both a **framework** (specs, schemas, tracked artifacts) and a set
of **deliverables** (four documents requested by the owner) that
position the framework to a prospective customer's CTO.

The plan grew from S310 design discussion in response to a CTO
question ("What happens at 2 AM when something breaks in code your
AI wrote?"). The 8-phase industry-standard incident-response model
was articulated; the owner directed it be formalized as a multi-phase
implementation proposal including capability work plus four document
deliverables.

This proposal is **scope and architecture only**. No code is written;
no documents are drafted. Codex review on this proposal yields GO or
NO-GO on the multi-phase plan itself. Each phase's bridges file
separately and reference this proposal as the binding plan.

## 1. Prior Deliberations

- **Owner question and improvised response (S310 conversation,
  2026-04-26):** "Suppose you get a support call at 2:00 related to
  some application that was coded by your AI?" The owner improvised
  a 7-step process focused on investigation. Prime Builder responded
  with the industry-standard 8-phase model (Detect → Acknowledge →
  Communicate → Mitigate → Investigate → Resolve → Verify →
  Postmortem) and identified ~24 user-story seeds.
- **Owner directive (S310, 2026-04-26):** "formulate it as an
  implementation proposal for a multi-phase project, which will
  include the implementation of new capabilities and the creation of
  documents which we can provide to the CTO." Four documents named:
  CTO 1-page, technical walk-through (7-15 pages), how-to docs, and
  a LinkedIn article (DOCX format).
- **`bridge/gtkb-command-surface-004.md` GO** — the architectural
  plan that nearly every incident-response capability must integrate
  with. Each `::incident`, `::mitigate`, `::postmortem` command lands
  under that program's CS-3+ slice plan.
- **`memory/MEMORY.md` "Strategic Thesis"** — the GT-KB pipeline's
  thesis is that the owner delivers specs and the pipeline produces
  deployable SaaS. Incident response in production is the moment
  that thesis is most tested; documenting it credibly is part of
  selling the thesis.
- **No prior bridge thread for GTKB-INCIDENT-RESPONSE.**

## 2. The 8-Phase Industry Model (Binding Reference)

This proposal binds to the 8-phase model articulated in the S310
discussion. Reproduced compactly so the plan is self-contained:

| Phase | Objective | Industry term |
|---|---|---|
| 1. **Detect → Page** | Signal reaches on-call within seconds | SRE Four Golden Signals |
| 2. **Acknowledge → Triage** | IC takes ownership; severity classified | ITIL Incident Management |
| 3. **Communicate** | Right people learn right facts at right cadence | Status-page + stakeholder comms |
| 4. **Mitigate** | Restore service before root cause known | "Rollback first" / SRE doctrine |
| 5. **Investigate** | Find root cause with evidence | Hypothesis-driven debugging |
| 6. **Resolve** | Apply permanent fix via change management | Emergency CAB-light |
| 7. **Verify → Recover** | Confirm normal; close incident | Customer-side verification |
| 8. **Postmortem** | Blameless analysis with action items | Google SRE postmortem template |

Cross-cutting concerns: severity classification (SEV-1..4),
on-call rotation, error budgets.

GT-KB's specific differentiation, validated by the framework:

- **Append-only KB + DA = postmortem-by-construction.** Every command,
  decision, hypothesis, fix, review, and verification is captured
  with timestamps. The postmortem assembles from existing artifacts
  in minutes.
- **Bridge protocol = change-management-by-construction.** No fix
  ships without independent Loyal Opposition review, even at 2 AM.
  Mitigation actions that are reversible-by-construction can ship
  on a fast path.
- **Operator role assignment + role-bound permissions = no panic
  mode.** The AI cannot make irreversible changes outside its
  defined authority.

## 3. Phase Plan

### Phase IR-1: Foundation + Concept-Level Documents (NOW)

**Objective:** Capture the framework as tracked artifacts and produce
the two documents that can be written purely from the framework
concept (no demonstrable capability required).

**Deliverables:**

- **D1.1** — Tracked SPEC `SPEC-INCIDENT-RESPONSE-FRAMEWORK-001` in KB
  defining the 8-phase model, severity classification, role
  definitions, and cross-cutting concerns. With assertions verifying
  the spec is referenced from `CLAUDE.md` and is regression-test-visible.
- **D1.2** — ADR `ADR-INCIDENT-RESPONSE-MODEL-001` capturing the
  decision to adopt the SRE/ITIL hybrid 8-phase model over
  alternatives (pure-SRE, pure-ITIL, custom). Cites rejected
  alternatives.
- **D1.3** — `docs/incident-response/cto-response-001.md` — the
  one-page response document. Plain markdown for now; DOCX export in
  Phase IR-6 if/when needed.
- **D1.4** — `docs/articles/gtkb-2am-incident-response-draft-001.md`
  — the LinkedIn article concept draft. Narrative, framework-grounded,
  no implementation details. Final DOCX export in Phase IR-6.
- **D1.5** — Backlog placeholder rows on `memory/work_list.md` for
  IR-CS-1 through IR-CS-N capability slices, sequenced per Phase IR-2.
- **D1.6** — DELIB record of the S310 owner directive that drove this
  plan, with `outcome=owner_decision`, citing the 4 deliverables and
  this proposal.

**Slice bridges to file (each gets its own Codex review):**

- `IR-1.1` — KB framework spec + ADR (single bridge; combined
  because they're tightly coupled and small)
- `IR-1.2` — CTO 1-page response document (single bridge)
- `IR-1.3` — LinkedIn article concept draft (single bridge)

**Why these documents in Phase 1:** the CTO question is on the
critical path — answer this week. The LinkedIn article positions the
program publicly; it benefits from being in market early, well before
implementation is complete (positioning lags reality by months in
practice).

### Phase IR-2: Demo-Ready Capabilities (HIGH PRIORITY)

**Objective:** Implement the 4-5 capabilities that, if working,
would let you demonstrate the framework to a prospect during a sales
cycle (not necessarily for full production use).

**Capabilities (each its own slice; each tied to GTKB-COMMAND-SURFACE
where applicable):**

- **IR-CS-1: Severity classification spec.** Tracked spec defining
  SEV-1..4 with criteria, response times, update cadences, postmortem
  requirements. KB-stored. Assertions verify presence + completeness.
  Routes upstream to `groundtruth-kb`.
- **IR-CS-2: `::incident <id>` command.** Lands under
  GTKB-COMMAND-SURFACE Slice CS-3+. Pre-loads alert payload (manual
  entry first; PagerDuty/ticket integration deferred), creates
  incident DELIB, sets session context. Suppresses
  `owner-decision-tracker` for the body (it's an alert payload, not
  an owner decision).
- **IR-CS-3: Postmortem auto-draft skill (`gtkb-postmortem`).** Reads
  KB + DA + bridge artifacts for a named incident DELIB. Assembles
  draft postmortem with standard SRE-template sections. Outputs to
  `docs/incidents/<id>/postmortem-draft-NNN.md`. Owner reviews and
  edits before final publication.
- **IR-CS-4: Fast-path mitigation registry.** Tracked spec listing
  pre-approved mitigation actions with explicit reversibility proofs.
  Each entry: name, description, reversibility property, applicable
  incident categories. Bridge protocol bypassed for actions in this
  registry (with audit log entry capturing every fast-path execution).
  Routes upstream.
- **IR-CS-5: Status-page draft generator (`::incident-update`).**
  Generates customer-facing draft from incident DELIB state and
  recent investigation evidence. Multiple output formats (status
  page markdown, email, Slack). Owner-approve before publish; no
  automatic publishing in Phase IR-2.

**Slice ordering:** IR-CS-1 first (everything else references the
severity schema). IR-CS-2 and IR-CS-3 next in parallel. IR-CS-4 and
IR-CS-5 follow.

**Dependency on GTKB-COMMAND-SURFACE:** IR-CS-2, IR-CS-3, IR-CS-5 each
require CS-2 (the dispatcher hook) and ideally CS-3 (the first command
set) to ship first. The architectural plan accommodates this: these
new commands would be added to the registry in CS-3 or a CS-3.5 slice.

**Owner decision needed at Phase IR-2 start:** the IR-CS-* slice
ordering — confirm or counter. Default proposed: IR-CS-1, then
{IR-CS-2, IR-CS-3} in parallel, then {IR-CS-4, IR-CS-5} in parallel.

### Phase IR-3: Technical Walk-Through Document (REQUIRES IR-2)

**Objective:** Write the 7-15 page technical walk-through, grounded
in actually-working Phase IR-2 capabilities.

**Deliverables:**

- **D3.1** — `docs/incident-response/technical-walkthrough-001.md`.
  Outline:
  1. Executive summary (1 page) — CTO 1-page is the seed
  2. The 8-phase model (1-2 pages)
  3. GT-KB's three differentiators (2-3 pages) — postmortem-by-
     construction, change-management-by-construction, role-bound-
     authority
  4. Worked example: a synthetic 2 AM incident walked through all
     8 phases, with actual screenshots/transcripts from a
     demonstration session run against a staging incident scenario
     (3-4 pages)
  5. The KB / DA / bridge artifact graph that resulted (1-2 pages)
  6. Generated postmortem (1-2 pages, real output from IR-CS-3)
  7. Action items + roadmap (1 page)
- **D3.2** — Synthetic incident scenario for the worked example.
  Tracked under `docs/incident-response/scenarios/synthetic-001.md`.
  Reproducible. Generates the screenshots/transcripts.

**Slice bridges:**

- `IR-3.1` — Walk-through document (single bridge; large but
  cohesive)
- `IR-3.2` — Synthetic incident scenario (separate bridge; reusable
  fixture for tests + demos)

**Why now (not earlier):** writing a technical walk-through before
the capabilities exist produces "vaporware copy" that ages
poorly when the actual implementation diverges. Writing it after
IR-CS-1..5 ship lets it be evidence-based.

### Phase IR-4: Full Capability Buildout (LOWER PRIORITY)

**Objective:** Implement the remaining capabilities from the 8-phase
model that production-grade adopters need but that are not strictly
necessary for the demo.

**Capabilities (slice-by-slice; each tied to GTKB-COMMAND-SURFACE):**

- **IR-CS-6: Production alert ingestion** (PagerDuty / Opsgenie /
  Alertmanager webhooks → incident DELIB).
- **IR-CS-7: Customer-direct comm draft generator.** Templates for
  support-ticket replies, customer email drafts.
- **IR-CS-8: Action-item backlog flow.** Postmortem action items
  automatically file as work-list rows with `origin="postmortem"`,
  visible on dashboard until closed.
- **IR-CS-9: Incident-close checklist (`::incident-close`).** Verifies
  status-page resolved, customer confirmed, regression test merged,
  postmortem scheduled.
- **IR-CS-10: SLO / error-budget tracking.** Per-service SLOs;
  incident impact deducts from budget; budget exhaustion triggers
  feature-freeze policy. Larger; may split into IR-CS-10A/10B.
- **IR-CS-11: On-call rotation integration.** Maps current on-call
  identity into session role assignment. Mostly informational;
  no forcing functions in Phase IR-4.
- **IR-CS-12: Incident-document artifact type.** First-class KB
  artifact for the running incident document, distinct from DELIB.
  May not be needed if DELIB shape is sufficient — decision deferred
  to slice-time.
- **IR-CS-13: Public-postmortem draft + redaction.** Takes internal
  postmortem and produces a public-facing version per owner-defined
  redaction rules. Cloudflare/Stripe gold-standard reference.

**Owner decision at Phase IR-4 start:** which subset of IR-CS-6..13
to ship and in what order. Some (IR-CS-8, IR-CS-9) are mechanically
small; others (IR-CS-10, IR-CS-13) are non-trivial design problems.
A scoping bridge IR-4-PLAN should land first to sequence them.

### Phase IR-5: How-To Documentation (REQUIRES IR-4)

**Objective:** Produce operator-facing documentation for adopters
running incident response in production.

**Deliverables:**

- **D5.1** — `docs/incident-response/how-to/index.md` — landing page.
- **D5.2** — `docs/incident-response/how-to/sev1-runbook.md` — step-
  by-step for SEV-1.
- **D5.3** — `docs/incident-response/how-to/postmortem-runbook.md`
  — step-by-step for postmortem.
- **D5.4** — `docs/incident-response/how-to/on-call-rotation.md`
  — operational guidance for on-call setup.
- **D5.5** — `docs/incident-response/how-to/troubleshooting.md`
  — common issues and resolutions.

**Slice bridges:** one per how-to document, or a single batch bridge
for all five depending on Codex preference. Default: single batch
bridge (D5.1..5 are tightly coupled and short individually).

### Phase IR-6: Document Polish + DOCX Production (FINAL)

**Objective:** Convert markdown documents to publication-quality
formats; final review pass.

**Deliverables:**

- **D6.1** — DOCX export of the LinkedIn article (D1.4) using
  `anthropic-skills:docx`. Branded per Remaker Digital style guide.
- **D6.2** — DOCX export of the technical walk-through (D3.1) for
  customer-facing distribution. PDF export also.
- **D6.3** — Final review pass on all documents. Loyal Opposition
  reads each as a final-check; owner approves each individually.
- **D6.4** — Optional: HTML-rendered versions of the walk-through
  and how-to docs for the docs site.

**Slice bridges:** one per document conversion (small, mechanical).

---

## 4. Phase Dependency Graph

```
IR-1 (Foundation + Concept Documents)
   │
   ├─► IR-2 (Demo-Ready Capabilities)
   │      │
   │      └─► IR-3 (Walk-Through Document)
   │             │
   │             └──┐
   │                │
   ├─► IR-4 (Full Capability Buildout)  ──┐
   │                                      │
   │                                      ▼
   │                                   IR-5 (How-To Documentation)
   │                                      │
   ▼                                      ▼
   ──────────────────────────► IR-6 (Polish + DOCX)
```

**Critical path: IR-1 → IR-2 → IR-3 → IR-6** for the customer-facing
deliverables.

**Independent path: IR-4 → IR-5** for adopter-facing deliverables.

**IR-1 is unblocked now.** All other phases depend on prior phase
completion at least for their bridges (some sub-slices can run in
parallel within a phase).

## 5. Owner-Decision Sequencing

Decisions needed up front (this proposal):

1. **Routing decision** — confirm Mixed (framework upstream;
   documents Agent Red-local + flow upstream later) is correct.
2. **Phase IR-1 scope** — confirm D1.1..D1.6 deliverables; adjust if
   any are out-of-scope or premature.
3. **Phase IR-2 capability set** — confirm IR-CS-1..5 are the right
   demo-ready set, or counter with substitutions.
4. **Coupling to GTKB-COMMAND-SURFACE** — confirm that incident
   commands land under that program's command-surface registry rather
   than building a parallel dispatcher.

Decisions that can be deferred:

5. **Phase IR-4 capability ordering** — handled at IR-4-PLAN time
   after Phase IR-2 ships.
6. **Style guide / brand details for DOCX exports** — handled at
   Phase IR-6 with owner input.

## 6. Implementation Order (Phase IR-1 only — the immediately actionable scope)

Phase IR-1 has six deliverables. Suggested implementation order:

1. **IR-1.1 bridge: KB framework spec + ADR.** Files
   `bridge/gtkb-incident-response-ir-1-1-001.md`. After Codex GO,
   inserts the SPEC and ADR via `db.insert_spec` and runs assertions.
2. **IR-1.2 bridge: CTO 1-page response document.** Files
   `bridge/gtkb-incident-response-ir-1-2-001.md`. After Codex GO,
   creates `docs/incident-response/cto-response-001.md`.
3. **IR-1.3 bridge: LinkedIn article concept draft.** Files
   `bridge/gtkb-incident-response-ir-1-3-001.md`. After Codex GO,
   creates `docs/articles/gtkb-2am-incident-response-draft-001.md`.
4. After all three Phase IR-1 bridges land VERIFIED: Phase IR-2
   capability planning bridge (`IR-2-PLAN`) sequences IR-CS-1..5.

These three IR-1 bridges can land in parallel after this proposal is
GO'd. They share no implementation surface.

## 7. Risk Analysis

### 7.1 Risks for the program

- **Document-implementation drift.** The walk-through and how-to docs
  could describe behaviors that the implementation later changes.
  Mitigated by: writing docs *after* the relevant capability ships
  (Phase IR-3 after IR-2; Phase IR-5 after IR-4); regression tests
  that fail if doc claims diverge from spec assertions.
- **Vaporware perception.** Publishing a LinkedIn article before
  capabilities ship could backfire if the framework isn't visibly
  delivered. Mitigated by: positioning the article as a *framework*
  piece, not a product announcement; clearly stating "in
  development" where applicable.
- **CTO timeline slippage.** The CTO is asking now; if Phase IR-1
  doesn't ship within the engagement window, the customer perceives
  the answer as ad hoc. Mitigated by: Phase IR-1 is small and uses
  only existing GT-KB primitives.
- **Capability scope creep.** Each IR-CS-* slice could grow as the
  full 8-phase pattern's nuances surface. Mitigated by: the slice
  protocol forces explicit Codex review of scope at each step;
  Phase IR-2's owner-decision-needed sequencing prevents silent
  expansion.

### 7.2 Risks for the customer engagement

- **Over-promising on AI-driven incident response.** Customers may
  hear "AI handles the incident" when the truth is "AI accelerates
  the human-driven incident response with strong guardrails." The
  CTO 1-page must be precise on this distinction; the LinkedIn
  article must avoid the over-promise.
- **Under-emphasizing the bridge protocol's role.** The Prime Builder
  + Loyal Opposition discipline is exactly what makes this safe at
  2 AM; if the documents lead with "magic AI fixes things" the value
  is misframed. Mitigated by: framework-first framing in all
  documents, with bridge discipline as the lead differentiator.

### 7.3 Rollback

Per phase. Phase IR-1 rollback is mechanical (delete documents,
unpromote spec). Later phases each have their own rollback plans
filed at slice time.

## 8. Codex Review Asks

1. Confirm §3 phase structure (six phases, dependency graph in §4).
   Flag any phase that should be split, merged, or reordered.
2. Confirm §3.IR-2 capability set (IR-CS-1..5) is the right
   demo-ready subset; flag any capability that should be in IR-2
   instead of IR-4 (or vice versa).
3. Confirm the routing decision in §0 (framework upstream;
   documents Agent Red-local + flow upstream later).
4. Confirm the coupling to GTKB-COMMAND-SURFACE for `::incident`,
   `::mitigate`, `::postmortem`, `::incident-update`,
   `::incident-close` commands. The architectural plan accommodates
   adding to its CS-3 first-set or a CS-3.5 slice; counter if a
   different integration is preferred.
5. Confirm Phase IR-1 immediately-actionable scope (§6) is the right
   first batch. The CTO timeline pressure may justify shipping IR-1.2
   (CTO 1-page) and IR-1.3 (LinkedIn) before IR-1.1 (spec/ADR) lands;
   the proposal currently has them in parallel rather than serial.
6. **GO / NO-GO** on the multi-phase plan as binding direction.

## 9. Decision Needed From Owner

Before Phase IR-1 bridges can file:

- **Confirm or counter the four "needed up front" decisions in §5
  items 1-4.**

Owner-decision sequencing is otherwise per-phase as documented in §3.

## 10. Code Quality Baseline

(Multi-phase proposal; CQ rules apply less but the format is preserved.
Phase IR-1 sub-bridges will have their own per-phase CQ tables.)

| Rule ID | Applies? | Notes |
|---|---:|---|
| CQ-SECRETS-001 | Yes | No credentials in any document or framework artifact; postmortem auto-drafts (IR-CS-3) must include redaction (deferred to that slice's CQ table) |
| CQ-PATHS-001 | Yes | Document paths are project-root-relative under `docs/incident-response/` and `docs/articles/`; framework spec/ADR live in KB |
| CQ-CONSTANTS-001 | Yes | Severity values (SEV-1..4) defined in the framework spec as canonical constants; referenced by all subsequent capabilities |
| CQ-DOCS-001 | Yes | Each document has a clear audience statement; framework spec is the authoritative reference |
| CQ-COMPLEXITY-001 | n/a (multi-phase plan; no code) | n/a; per-slice |
| CQ-TESTS-001 | n/a (multi-phase plan; no code) | Per-slice; framework-spec assertions verify the spec is referenced from `CLAUDE.md` |
| CQ-LOGGING-001 | Per-slice | Audit trail is the bridge protocol itself + DA |
| CQ-SECURITY-001 | Yes | Authorization model: incident-response capabilities respect existing role-based permissions; fast-path mitigation registry (IR-CS-4) requires explicit reversibility proofs and audit log |
| CQ-VERIFICATION-001 | Partial | Plan-level verification = Codex GO; phase-level verification per phase; capability-level verification per slice |

---

**Status request:** GO on this multi-phase plan as binding direction
for Phase IR-1 immediately-actionable bridges and subsequent phases.

**Files in this proposal:** this file only.

**Files modified on Codex GO:** none in this bridge. Phase IR-1
sub-bridges (IR-1.1, IR-1.2, IR-1.3) file individually with their own
file lists.

**Implementation NOT yet authorized.** This proposal authorizes
*subsequent phase bridges and slice bridges to be filed under the
multi-phase direction in this document*. Each phase and each slice
still requires its own Codex GO before implementation.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
