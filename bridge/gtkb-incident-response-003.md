REVISED

# GTKB-INCIDENT-RESPONSE — Multi-Phase Implementation Proposal (REVISED-1)

**Status:** REVISED (multi-phase scoping; addresses NO-GO at -002; awaiting Codex re-review)
**Date:** 2026-04-26 (S310)
**Work item:** GTKB-INCIDENT-RESPONSE
**Author:** Prime Builder (Claude Opus 4.7)
**Bridge kind:** multiphase_implementation_proposal
**Routing:** **All upstream to `groundtruth-kb`** (revised from `-001` "Mixed" per owner answer S310-Q2). Framework artifacts, capabilities, and document templates all ship to the GT-KB platform. Agent Red provides a worked example throughout.

bridge_kind: multiphase_implementation_proposal
work_item_ids: [GTKB-INCIDENT-RESPONSE]
spec_ids: []
target_project: groundtruth-kb
implementation_scope: framework_documents_and_capabilities
requires_review: true
requires_verification: true (per phase)

---

## 0. What This Revision Addresses

Codex `-002` NO-GO raised three findings against `-001`. All addressed.
Plus owner-directed scope clarifications captured as five decisions in
S310 (2026-04-26) via one-by-one AskUserQuestion flow. The revision
captures the decisions, addresses the findings, and reframes the
program where the answers materially change scope.

## 1. Codex GO Conditions Compliance + Owner Decision Capture

| Finding (from `-002`) | Resolution in this revision |
|---|---|
| **[P1] Fast-path mitigation bypass contradicts bridge safety claim** | §3 below: IR-CS-4 reframed as **pre-reviewed registry + mandatory post-execution Loyal Opposition verification** per owner answer S310-Q1. Each fast-path action is pre-approved through normal bridge governance BEFORE entering the registry. Emergency execution is fast (no per-incident review). Every fast-path execution creates an incident DELIB requiring later LO verification. The bridge protocol's GO/NO-GO discipline still applies; it just runs *before* the incident as registry approval rather than *during* it. Standard SRE pattern (Google, Stripe, Cloudflare) |
| **[P1] Phase IR-1 unblocked vs. owner decisions contradiction** | §2 below: all four "decisions needed up front" are resolved by the S310 one-by-one AskUserQuestion flow. IR-1 is now genuinely unblocked. The decisions are: routing (S310-Q2 = All upstream); IR-1 scope (S310-Q3 = IR-0 inventory first); IR-2 capabilities (S310-Q4 = all five); command-surface coupling (S310-Q5 = single registry) |
| **[P2] Existing incident surfaces not inventoried** | §4 below: **new Phase IR-0** (existing-incident-surfaces inventory + boundary map) added as prerequisite to IR-1, per owner answer S310-Q3. Maps `src/multi_tenant/cosmos_schema.py:72,142,1542-1698,2377-2380`, `src/multi_tenant/repositories/incidents.py`, `src/multi_tenant/status_api.py`, `tests/multi_tenant/test_incidents_api.py`, and `GTKB-DORA-001` dashboard incidents. Decides reuse / wrap / migrate / out-of-scope per surface |

## 2. Owner Decisions Captured (S310, 2026-04-26)

Five decisions resolved one-by-one via AskUserQuestion in S310. The
DELIB record `DELIB-INCIDENT-RESPONSE-OWNER-DIRECTIVES-001` (to be
inserted on this proposal's GO) captures all five.

| # | Question | Answer | Resolved |
|---|---|---|---|
| Q1 | Fast-path mitigation governance | Pre-reviewed registry + post-execution review (Recommended) | 2026-04-26T05:54Z |
| Q2 | Routing (upstream / Agent Red / mixed) | All upstream to groundtruth-kb | 2026-04-26T05:55Z |
| Q3 | Phase IR-1 scope | IR-0 inventory first, then IR-1 framework (Recommended) | 2026-04-26T05:56Z |
| Q4 | Phase IR-2 capabilities | All five as proposed (Recommended) | 2026-04-26T05:57Z |
| Q5 | Command-surface coupling | Single registry under GTKB-COMMAND-SURFACE (Recommended) | 2026-04-26T05:58Z |

Each decision is durably evidenced in this proposal and the DELIB. No
further owner decisions block Phase IR-0 or Phase IR-1.

## 3. CORRECTED IR-CS-4 — Fast-Path Mitigation Registry

The `-001` §3.IR-2 description of IR-CS-4 said: "Bridge protocol
bypassed for actions in this registry (with audit log capturing every
fast-path execution)." This is replaced by the pre-reviewed model per
owner answer Q1.

### Revised IR-CS-4 contract

**Registry entry lifecycle (pre-execution):**

1. A candidate fast-path mitigation action (rollback, scale-up,
   traffic shift, feature-flag toggle, etc.) is proposed via normal
   bridge protocol: `bridge/fast-path-<action-name>-001.md` with full
   reversibility proof, blast-radius analysis, and CQ-VERIFICATION
   evidence.
2. Codex reviews. GO or NO-GO per standard discipline.
3. On GO, the action is added to the registry at
   `<gt-kb-root>/applications/<name>/.groundtruth/incident-response/fast-path-registry.toml`
   (or platform-default at `groundtruth-kb/templates/fast-path-registry.toml`
   for upstream). Registry entry records: action name, CLI invocation,
   reversibility proof reference, applicable severity levels,
   pre-approval bridge thread reference.

**Execution-time (during a SEV-1):**

4. IC invokes `::mitigate-<action-name>` from the in-session command
   surface (or `gt mitigate <action-name>` from CLI). The dispatcher
   confirms the action is in the registry and active for the current
   incident's severity. Execution proceeds **without** per-incident
   bridge review.
5. Every execution creates a DELIB record with
   `source_type="fast_path_execution"`, citing the pre-approval bridge
   thread and the active incident DELIB. Captures: invocation
   timestamp, parameters, exit code, observable outcome.

**Post-execution review (within 24h of incident close):**

6. Loyal Opposition reviews each fast-path execution DELIB and emits
   a verification record (VERIFIED / NO-GO / PARTIAL). This is
   mandatory; the post-execution review path is not optional.
7. NO-GO post-execution triggers a follow-up bridge: was the
   pre-approval rationale wrong? Is the action's reversibility proof
   stale? Should the action be removed from the registry?

This contract preserves the bridge protocol's "no fix without LO
review" claim — the review just happens before the incident (as
registry approval) and after (as execution verification), not
during.

### What this contract does NOT permit

- Adding entries to the registry without prior bridge GO. The
  registry file itself is governed by the formal-artifact-approval-gate
  hook (per the existing GOV-20 ADR/DCL pattern).
- Modifying registry entries at incident time. Mutations require a
  separate bridge proposal.
- Skipping post-execution review. The review is mandatory; absent
  reviews surface as a release-gate finding.

## 4. NEW Phase IR-0 — Existing Incident Surfaces Inventory

Per owner answer S310-Q3 + Codex `-002` [P2] finding.

**Objective:** map every existing incident-related surface in Agent
Red and the GT-KB dashboard so the framework lands without creating
parallel concepts.

**Deliverables:**

- **D0.1** — `<gt-kb-root>/applications/Agent_Red/incident-response/existing-surfaces-inventory-001.md`
  (Agent Red-local; references upstream framework). Contains:
  - Per-surface row: file path, line range, what it does, scope
    (Agent Red runtime / GT-KB dashboard / DA / external)
  - Disposition decision: **reuse** / **wrap** / **migrate** /
    **out-of-scope**
  - Compatibility requirement note where downstream framework
    artifacts must align
- **D0.2** — Boundary-map SPEC `SPEC-INCIDENT-SURFACES-BOUNDARY-001`
  in upstream `groundtruth-kb`. Defines what the framework owns vs.
  what adopter runtime owns. Exemplified by Agent Red's existing
  surfaces.

**Inventory targets (verified during research):**

| Surface | Path | Disposition (proposed; refined in IR-0) |
|---|---|---|
| Cosmos `incidents` collection | `src/multi_tenant/cosmos_schema.py:72,142,1542-1698,2377-2380` | **wrap** — framework's incident-DELIB lifecycle calls into this for status-page-incident ↔ DELIB linkage |
| `IncidentRepository` | `src/multi_tenant/repositories/incidents.py:3-38` | **wrap** — framework uses this as the persistence backend for status-page incidents |
| Public status API | `src/multi_tenant/status_api.py:2-5,79-146` | **reuse** — framework's `::incident-update` skill writes through this API |
| Status/incident tests | `tests/multi_tenant/test_incidents_api.py:549-795` | **reuse** — framework gains additional tests but doesn't rewrite |
| GTKB-DORA-001 dashboard incidents | `memory/work_list.md:739-758` (work item) | **migrate** — DORA dashboard's incident table consumes from the framework's incident-DELIB lifecycle once that lands; replaces the parallel runtime-only table |

**Slice bridge to file (Phase IR-0):**

- `IR-0.1` — Inventory document + boundary-map SPEC (single bridge;
  combined because they're tightly coupled and small)

**Slice ordering:** IR-0.1 ships before any IR-1 bridge files, so the
framework SPEC and ADR cite the boundary map.

## 5. CORRECTED Routing — All Upstream

Per owner answer S310-Q2.

The original `-001` had Mixed routing: framework upstream, documents
Agent Red-local. Replaced by **all-upstream**:

| Artifact | -001 routing | -003 routing |
|---|---|---|
| Framework SPEC + ADR | upstream | **upstream** (unchanged) |
| Severity classification spec | upstream | **upstream** (unchanged) |
| Fast-path mitigation registry template | upstream | **upstream** (unchanged) |
| Postmortem skill | upstream | **upstream** (unchanged) |
| `::incident` / `::mitigate-*` / etc. commands | upstream (via CS-3+) | **upstream** (unchanged) |
| **CTO 1-page response template** | Agent Red-local | **upstream** with Agent Red as worked example |
| **Technical walk-through template** | Agent Red-local | **upstream** with Agent Red as worked example |
| **How-to documentation** | Agent Red-local | **upstream** (unchanged) |
| **LinkedIn article concept** | Agent Red-local | **upstream** (positioning piece for the GT-KB platform; Agent Red as illustration) |
| **Existing-surfaces inventory** | (was not in scope) | Agent Red-local (D0.1; references the upstream boundary-map SPEC at D0.2) |
| **Synthetic incident scenario** (for IR-3 walk-through worked example) | (was not in scope) | upstream (`groundtruth-kb/examples/incident-scenarios/`) |

### Implications for document tone

- **CTO 1-page** becomes a GT-KB capability brief that uses "what
  happens at 2 AM with AI-coded code?" as its motivating example.
  Agent Red is the named adopter that demonstrates the pattern;
  document is reusable for any prospect or evaluator.
- **Technical walk-through** is a 7-15 page GT-KB framework
  presentation with an Agent Red worked example walking through all
  8 phases. Other adopters can substitute their own scenarios.
- **LinkedIn article** is positioning for GT-KB-as-IDP, not an
  Agent-Red-specific announcement. Reads as "here's how AI-driven
  development teams handle 2 AM incidents" rather than "here's how
  Agent Red specifically does it."
- **How-to documentation** is operator-facing for any GT-KB adopter.

### Adopter-side files

The only Agent Red-local artifact in this revision is the
existing-surfaces inventory (D0.1) — it's intrinsically about Agent
Red's specific runtime. Everything else flows upstream.

## 6. CORRECTED Phase Plan

### Phase IR-0: Existing Incident Surfaces Inventory (NEW; PREREQUISITE)

(See §4 above.)

### Phase IR-1: Foundation + Concept-Level Documents (UPSTREAM)

**Deliverables (revised routing):**

- **D1.1** — Tracked SPEC `SPEC-INCIDENT-RESPONSE-FRAMEWORK-001` in
  `groundtruth-kb` KB. Cites D0.2 boundary-map SPEC. With assertions
  verifying the spec is referenced from upstream `CLAUDE.md` template
  and is regression-test-visible.
- **D1.2** — ADR `ADR-INCIDENT-RESPONSE-MODEL-001` in `groundtruth-kb`.
  Captures the SRE/ITIL-hybrid 8-phase model decision; rejected
  alternatives (pure-SRE, pure-ITIL, custom).
- **D1.3** — `groundtruth-kb/docs/incident-response/cto-response-template-001.md`
  — agnostic GT-KB capability brief. Agent Red is named worked example.
- **D1.4** — `groundtruth-kb/docs/articles/2am-incident-response-draft-001.md`
  — agnostic LinkedIn article concept. Positioning for GT-KB-as-IDP.
- **D1.5** — Backlog placeholder rows on the upstream
  `groundtruth-kb/standing-backlog.md` (or equivalent) for IR-CS-1
  through IR-CS-N.
- **D1.6** — DELIB `DELIB-INCIDENT-RESPONSE-OWNER-DIRECTIVES-001` capturing
  the five S310 owner answers per §2 above.

**Slice bridges:**
- `IR-1.1` — KB framework spec + ADR (combined; tightly coupled)
- `IR-1.2` — CTO 1-page template
- `IR-1.3` — LinkedIn article concept

### Phase IR-2: Demo-Ready Capabilities (UPSTREAM)

**Capabilities (per S310-Q4 confirmation):**

- **IR-CS-1: Severity classification spec** — upstream KB. Defines
  SEV-1..4 with criteria, response times, update cadences, postmortem
  requirements.
- **IR-CS-2: `::incident <id>` command** — under GTKB-COMMAND-SURFACE
  CS-3+ registry. Pre-loads alert payload (manual entry first), creates
  incident DELIB, sets session context.
- **IR-CS-3: Postmortem auto-draft skill (`gtkb-postmortem`)** —
  upstream skills directory. Reads KB + DA + bridge artifacts; emits
  draft postmortem.
- **IR-CS-4: Fast-path mitigation registry** — per §3 above;
  pre-reviewed entries + mandatory post-execution review.
- **IR-CS-5: Status-page draft generator (`::incident-update`)** —
  under GTKB-COMMAND-SURFACE CS-3+ registry. Generates customer-facing
  drafts; owner-approve before publish.

**Coupling (per S310-Q5):** all five `::cmd`-typed capabilities land
in the shared GTKB-COMMAND-SURFACE registry (`.claude/commands/registry.json`,
just tracked via CS-1.5). No parallel dispatcher.

### Phase IR-3: Technical Walk-Through Document (UPSTREAM)

**Deliverables:** unchanged from `-001` §3.IR-3 except routing flips
to upstream. Agent Red continues as the named worked example.

### Phase IR-4: Full Capability Buildout

Unchanged from `-001` §3.IR-4. All upstream.

### Phase IR-5: How-To Documentation (UPSTREAM)

Unchanged from `-001` §3.IR-5 except routing flip.

### Phase IR-6: Document Polish + DOCX Production

Unchanged from `-001` §3.IR-6.

## 7. Updated Phase Dependency Graph

```
IR-0 (Existing Surfaces Inventory) ──┐
                                     │
                                     ▼
IR-1 (Foundation + Concept Docs)
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

**Critical path: IR-0 → IR-1 → IR-2 → IR-3 → IR-6** for
customer-facing deliverables.

**IR-0 is unblocked now.** Phase IR-1 starts immediately after IR-0.1
files VERIFIED.

## 8. Files Modified on Codex GO of This Proposal

This proposal authorizes IR-0.1 sub-bridge to file. No code or
documents change in this bridge.

## 9. Codex Re-Review Asks

1. Confirm §3 IR-CS-4 reframe (pre-reviewed registry + post-execution
   LO verification) resolves Finding [P1] #1.
2. Confirm §2 + §1 capture of five owner decisions resolves Finding
   [P1] #2.
3. Confirm §4 Phase IR-0 + the inventory targets table resolves
   Finding [P2].
4. Confirm §5 all-upstream routing is acceptable; flag any artifact
   that should remain Agent Red-local.
5. Confirm §6 phase plan + §7 dependency graph reflect the revised
   structure correctly.
6. **GO / NO-GO** on the multi-phase plan as binding direction with
   the revised structure.

## 10. Decision Needed From Owner

None blocking. All five decisions captured S310 (2026-04-26).

## 11. Acknowledgment

The three findings in `-002` were materially correct:

- The fast-path bypass framing was a real governance contradiction.
  The pre-reviewed-registry model resolves it cleanly.
- The "IR-1 unblocked" + "owner decisions needed" contradiction was
  a real ambiguity. The one-by-one AskUserQuestion flow resolves it
  durably.
- The existing-surfaces-not-inventoried finding was a real risk of
  parallel-concept divergence. The IR-0 prerequisite phase resolves
  it.

The all-upstream routing (owner answer Q2) is more aggressive than my
recommended Mixed routing. It changes the document tone (templates
with worked example, not adopter-specific) and the slice routing
(every IR-CS files under groundtruth-kb). The owner's preference
favors the IDP-as-marketed-product framing — GT-KB itself is what's
being positioned to a prospect; Agent Red illustrates.

---

**Status request:** GO

**Files in this proposal:** this file only.

**Files modified on Codex GO:** none in this bridge. Phase IR-0
sub-bridge `IR-0.1` files individually after this `-003` lands GO.

**Implementation NOT yet authorized.** This proposal authorizes
*subsequent phase bridges and slice bridges to be filed under the
multi-phase direction in this document*. Each phase and each slice
still requires its own Codex GO before implementation.

## (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
