REVISED

# Implementation Proposal — GTKB-GOV-AUQ-ENFORCEMENT-STACK: Mechanical Enforcement of AskUserQuestion as the Only Valid Owner-Decision Channel (Umbrella Scoping, REVISED-1)

**Author:** Prime Builder (Claude Code)
**Drafted:** 2026-05-04 (S331)
**Type:** Umbrella scoping for a 6-sub-slice governance program
**Risk tier:** Medium (governance contract changes affecting hooks, rules, bridge protocol; no production-runtime impact)
**Trigger:** S331 owner directive (this session): "Prime Builder consistency needs to be enforced mechanically, not left as a reminder."

**Revision basis:** Addresses Codex NO-GO at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-002.md` — F1 (preflight failed for missing `ADR-ISOLATION-APPLICATION-PLACEMENT-001`), F2 (autonomous sub-slice filing claim lacked cited owner evidence; AUQ answer "Autonomous progression" was issued AFTER `-001` filed), F3 (Sub-slice F's release-metric enforcement was scoped ambiguously between umbrella VERIFIED requirement and informational-only first run), F4 (Agent Red framing did not match the 2026-05-04 owner correction recording Agent Red as a separate project).

---

## Codex Findings Addressed

### Cycle 1 (NO-GO at -002, addressed in -003)

| Finding | Recommendation | Disposition |
|---------|----------------|-------------|
| **F1** — Mandatory applicability preflight failed: `missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001"]`. The proposal mentions `applications/`, Agent Red, and project-root-boundary content, which triggers ADR applicability rules. | "File a revision that cites `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, explains its applicability or non-applicability to the umbrella, and maps any resulting verification obligations." | Specification Links section now cites `ADR-ISOLATION-APPLICATION-PLACEMENT-001` with explicit applicability scope: this ADR is the canonical placement authority for any GT-KB content destined to live under `applications/`. This umbrella is governance work and does NOT itself create new `applications/` content; it cites the ADR as the contract that future ISOLATION-018 work must respect after this umbrella VERIFIED. T-spec-1 in the test plan covers preflight pass after this revision. |
| **F2** — "Owner pre-approval to file sub-slice bridges autonomously" acceptance criterion lacked cited owner evidence. Per `DELIB-0872`, Codex review cannot convert defaults into owner decisions. | "Either remove that acceptance criterion and state that each sub-slice may be filed only under the ordinary standing-backlog / owner-priority rules, or obtain and cite an explicit AskUserQuestion owner decision authorizing autonomous filing." | The AUQ authorizing autonomous progression was issued during S331 in this session (AFTER `-001` filed but BEFORE `-002` review): owner answer "Autonomous progression (Recommended)" to the question "After Codex GOs the enforcement umbrella, how should sub-slices A through F be filed and executed?". This revision cites that AUQ explicitly in Prior Deliberations and the Owner Decisions / Input section, addressing F2's evidence requirement. |
| **F3** — Release-metric enforcement scoped ambiguously: umbrella VERIFIED requires 3 metrics PASS but the risk table said first run is informational-only with promotion deferred. | "Revise Sub-slice F so the metric-promotion/enforcement step is either included in the umbrella's VERIFIED criteria or explicitly split into a named follow-on bridge that the umbrella does not claim to complete." | Sub-slice F is revised to include BOTH the doctor check addition AND the gate enforcement promotion as a single sub-slice scope. The risk-table mitigation language about informational-only first run is removed; instead, the implementation order within Sub-slice F is: (1) add the 3 doctor checks; (2) clean any existing baseline failures from Sub-slices D and E impl evidence; (3) promote checks to release-gate enforcement; (4) verify release-candidate gate fails on synthetic baseline pollution. Umbrella VERIFIED requires the promotion step to be complete, not merely the checks to exist. |
| **F4** — Agent Red / applications framing did not match the 2026-05-04 owner correction (Agent Red is a separate project, not GT-KB content). Cited `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` as if it were a live GT-KB placement authority. | "Cite `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and the current project-root boundary rule. Clarify whether `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` is historical context, superseded context, or still an active constraint for the specific blocked ISOLATION-018 work." | This revision: (a) adds `ADR-ISOLATION-APPLICATION-PLACEMENT-001` as the canonical `applications/` placement authority cited in Specification Links and project-root-boundary references; (b) re-classifies `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` as **historical context for the specific blocked ISOLATION-018 work**, not a live GT-KB placement authority; (c) updates `.claude/rules/project-root-boundary.md` reference to make explicit that this umbrella operates entirely within `E:/GT-KB/` and does not touch Agent Red files; (d) the Background section now states that the blocked ISOLATION-018 work refers to GT-KB internal isolation work (sub-slices 18.C through 18.L) and does not depend on Agent Red as a live GT-KB artifact. |

---

## Background

The owner-decision-tracker subsystem was implemented in S315 (`bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED 2026-04-27) to surface pending owner decisions across session boundaries. A bounded-exception block emission was added in S321 (`bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` REVISED-1) so the Stop hook can refuse to end a turn when prose-decision-ask patterns are detected without a same-turn AskUserQuestion call.

That block emission is currently **disabled via env override** (`GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` in `.claude/settings.local.json`) because the regex matched factual status statements as false positives during S328 (e.g., "Awaiting Codex re-review" — a factual report — triggered the same detector as "Awaiting your direction" — a genuine owner question). The override was a temporary discipline workaround pending regex tightening, captured in `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) and explicitly deferred under the ISOLATION-017 release-path feature freeze.

S331 (this session) provided three operational confirmations that the partial enforcement state is insufficient: (a) 13 prose-pattern false positives accumulated this session before the owner used the `clear pending` shortcut; (b) Prime Builder asked decision questions in prose during 18.B/18.C drafting (subsequently corrected by owner directive to use AskUserQuestion); (c) the destructive-gate hook caught a `rm -r` invocation but only because that hook's pattern is more specific than the prose-decision pattern.

The owner has now directed (S331, this session, AskUserQuestion confirmations): full 6-mechanism enforcement stack as the immediate next priority, blocking the remaining ISOLATION-018 sub-slices (18.C through 18.L) until the enforcement is in place. ISOLATION-018 is GT-KB internal isolation work that sequences Agent-Red-related migrations; this umbrella does not depend on Agent Red as a live GT-KB artifact (per `.claude/rules/project-root-boundary.md` and the 2026-05-04 owner correction in `CLAUDE.md` and `.claude/rules/canonical-terminology.md` recording Agent Red as a separate project).

## Specification Links

Cross-cutting specs required by `config/governance/spec-applicability.toml` for any bridge proposal:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (verified) — Live bridge index authority. Compliance: this proposal lives at `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-003.md`; INDEX update at top of `bridge/INDEX.md` is the canonical workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (specified) — Implementation proposals must cite every relevant governing specification. Compliance: this section enumerates all governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (specified) — VERIFIED requires test creation + execution derived from linked specs. Compliance: per-sub-slice test plans in each sub-slice's bridge proposal; umbrella VERIFIED gate aggregates sub-slice VERIFIED status.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — **Added per Codex `-002` F1.** Canonical placement contract authorizing `applications/<application-name>/` as the destination namespace for application content. Applicability to this umbrella: **the umbrella does NOT itself create new `applications/` content.** It cites the ADR as the contract that the blocked ISOLATION-018 sub-slices (18.C through 18.L) must respect after this umbrella VERIFIED. This umbrella's own changes target `.claude/rules/`, `.claude/hooks/`, `memory/`, `groundtruth-kb/` (Sub-slice E hook impl), and `bridge/` — these surfaces are outside the `applications/` namespace. Verification obligation: T-out-of-applications in the test plan asserts that umbrella sub-slice commits do not introduce files under `applications/`.

Topic-specific governance for this work:

- `GOV-OWNER-DECISION-SURFACING-001` (verified per S315) — Source rule mandating mechanical surfacing of owner-decision pending state. This umbrella extends the surfacing contract from "pending-state surfacing" to "decision-channel enforcement".
- `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (specified) — Existing canonical spec defining the requirements-collection hook contract. Compliance: Sub-slice E implements this spec.
- `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` (specified) — Existing design constraint for the requirements-collection hook. Compliance: Sub-slice E IPR will cite this DCL.
- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` (relevant per work_list row 21) — Chat-derived spec approval contract; intersects with how AUQ-collected requirements get promoted to canonical specs.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (per `.claude/rules/acting-prime-builder.md`) — Repetitive plumbing belongs in services, not sessions. Compliance: this umbrella's sub-slices upgrade existing partial infrastructure rather than rebuild around it.
- `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` (VERIFIED 2026-04-27) — Original owner-decision surfacing implementation; this umbrella extends it.
- `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` (REVISED-1 with subsequent GO/VERIFIED in -004 through -006 chain) — Bounded-exception block emission already implemented; Sub-slice A re-enables and broadens.
- `.claude/rules/prime-builder-role.md` — Existing Prime Builder role rule; Sub-slice B extends with AUQ-only declaration.
- `.claude/rules/loyal-opposition.md` — Existing Loyal Opposition rule; Sub-slice C extends with bridge review gate for owner-decision evidence.
- `.claude/rules/file-bridge-protocol.md` — Bridge protocol; Sub-slice C adds "Owner Decisions / Input" section requirement.
- `.claude/rules/codex-review-gate.md` — Pre-implementation review obligation; this proposal is the artifact submitted for review.
- `.claude/rules/deliberation-protocol.md` — Pre-proposal deliberation-search obligation; satisfied via Prior Deliberations section.
- `.claude/rules/project-root-boundary.md` — Project root boundary rule. **Compliance:** this umbrella operates entirely within `E:/GT-KB/`. The umbrella does not depend on Agent Red as a live GT-KB artifact; references to Agent Red are historical context only (see Agent Red Reference Disposition section below).
- `.claude/rules/canonical-terminology.md` — Records the 2026-05-04 owner correction that Agent Red is a separate project, not GT-KB content. Compliance: this revision reframes Agent Red references accordingly.
- `.claude/hooks/owner-decision-tracker.py` — Existing hook; Sub-slices A and D modify.
- `.claude/hooks/bridge-compliance-gate.py` — Existing hook; Sub-slice C extends.
- `memory/pending-owner-decisions.md` — Durable evidence file; Sub-slice D audits.
- `memory/work_list.md` row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) — Existing deferred work item; Sub-slice A absorbs it.

Advisory specs cited per `config/governance/spec-applicability.toml`:

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (verified) — Concrete decisions preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (verified) — Traceability across artifacts, tests, reports, decisions.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (verified) — Lifecycle states.

The proposed tests in the per-sub-slice test plans derive from these linked specs as follows: AUQ-only contract → Sub-slice B tests; hook block re-enable → Sub-slice A tests; regex tightening → Sub-slice A tests; bridge review gate → Sub-slice C tests; evidence audit → Sub-slice D tests; requirements-collection hook → Sub-slice E tests; release metrics → Sub-slice F tests; placement contract → T-out-of-applications (umbrella-level).

## Agent Red Reference Disposition (per Codex `-002` F4)

The 2026-05-04 owner correction in `CLAUDE.md` and `.claude/rules/canonical-terminology.md` records that Agent Red is a separate project, not GT-KB content. This umbrella reframes prior Agent Red references accordingly:

- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` is **historical context only** for the specific ISOLATION-018 work this umbrella temporarily blocks (sub-slices 18.C through 18.L). It is NOT a live GT-KB placement authority and is NOT required for this umbrella's verification.
- `DELIB-S330-AGENT-RED-MIGRATION-PENDING-WAIVER` is the active waiver covering the blocked ISOLATION-018 sub-slices but does NOT cover this umbrella's work. This umbrella does not need a waiver because it operates entirely within GT-KB rule and hook surfaces.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` is the canonical placement authority for any `applications/` content; this umbrella does not create such content but cites the ADR for downstream sub-slice contract.
- `.claude/rules/project-root-boundary.md` is the active rule; this umbrella complies fully.

## Prior Deliberations

Search performed against `groundtruth.db` deliberations table (per `.claude/rules/deliberation-protocol.md`):

| DELIB | Source | Outcome | Relevance |
|-------|--------|---------|-----------|
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | owner_conversation | owner_decision | Repetitive plumbing belongs in services; this umbrella consolidates AUQ enforcement infrastructure |
| Implicit S315 owner directive (per `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED) | owner_conversation | owner_decision | Mechanically force surfacing of owner-decision pending state |
| Implicit S321 owner directive (per `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED) | owner_conversation | owner_decision | Bounded exception for block emission added |
| S328 regex-tightening directive (work_list row 29) | owner_conversation | owner_decision | Regex too liberal; tightening required before block re-enable |
| `DELIB-0872` (Codex cannot convert defaults to owner decisions) | bridge_thread | governance_constraint | Cited by Codex `-002` F2; this revision satisfies F2 by citing explicit S331 AUQ owner answer |
| `DELIB-0998` (governance enforcement must attach to actual hot path) | bridge_thread | governance_constraint | Cited by Codex `-002` Prior Deliberations; this umbrella's Sub-slice A and Sub-slice C attach to actual bridge/hook hot paths |
| S331 (this session) AUQ #1: "Block ISOLATION-018; enforcement first (Recommended)" | owner_conversation | owner_decision | Enforcement priority confirmed |
| S331 (this session) AUQ #2: "Full 6-mechanism stack (Recommended)" | owner_conversation | owner_decision | Umbrella scope confirmed |
| **S331 (this session) AUQ #3: "Autonomous progression (Recommended)" — answer to: "After Codex GOs the enforcement umbrella, how should sub-slices A through F be filed and executed?"** | owner_conversation | owner_decision | **Per Codex `-002` F2 evidence requirement: explicit owner authorization for autonomous sub-slice filing.** Owner option text: "file Sub-slice A bridge → wait for Codex GO → implement → post-impl REPORT → wait for Codex VERIFIED → commit → file Sub-slice B → etc., autonomously through F. No per-sub-slice owner approval needed; AskUserQuestion only for substantive scope ambiguities surfaced during sub-slice drafting." |

## Goal

Mechanically enforce AskUserQuestion as the ONLY valid channel for owner-decision asks, with: (a) blocking enforcement at the harness boundary (Stop hook refuses turn-end on detected prose-decision-ask without AUQ); (b) tightened regex eliminating false positives; (c) declared rule contract (Prime Builder rules state AUQ as the only valid decision channel); (d) bridge review gate (Codex NO-GO on proposals/reports lacking Owner Decisions evidence section); (e) durable evidence audit (`memory/pending-owner-decisions.md` integrity confirmed); (f) requirements-collection hook implementation (per existing GOV/DCL); (g) release metrics gating fully promoted to release-gate enforcement (per Codex `-002` F3 — no informational-only baseline state at umbrella VERIFIED).

## Existing Infrastructure Inventory

This umbrella builds on and absorbs the following existing artifacts:

| Surface | State | This umbrella's relationship |
|---------|-------|------------------------------|
| `GOV-OWNER-DECISION-SURFACING-001` | verified (S315) | Extends — surfacing → enforcement |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` | specified | Implemented in Sub-slice E |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` | specified | Cited by Sub-slice E IPR |
| `IPR-REQUIREMENTS-COLLECTION-HOOK-001` | does not yet exist in MemBase | Sub-slice E creates |
| `.claude/hooks/owner-decision-tracker.py` | exists; Stop/SessionStart/UserPromptSubmit dispatch live; block emission feature-flag-gated | Sub-slice A re-enables block; Sub-slice A adds regex tightening; Sub-slice D audits |
| `.claude/hooks/bridge-compliance-gate.py` | exists; checks Specification Links + spec-derived testing | Sub-slice C extends with Owner Decisions section check |
| `memory/pending-owner-decisions.md` | exists; durable ledger; `clear pending`/`resolve`/`defer` shortcuts work | Sub-slice D audits integrity |
| `.claude/settings.local.json` `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` | env override suppressing block emission | Sub-slice A removes after regex tightening lands |
| `.claude/rules/prime-builder-role.md` | exists; describes Prime authority + AUQ usage | Sub-slice B extends with AUQ-only declaration |
| `.claude/rules/loyal-opposition.md` | exists; describes review obligations | Sub-slice C extends |
| `.claude/rules/file-bridge-protocol.md` | exists; defines Specification Links + Verification Gates | Sub-slice C adds Owner Decisions section requirement |
| `memory/work_list.md` row 29 (regex tightening) | deferred under freeze | Sub-slice A absorbs and lifts the deferral |
| `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-*` thread (6 versions, VERIFIED) | block emission infrastructure | Sub-slice A reactivates with tightened regex |
| `gt project doctor` | exists; runs platform health checks | Sub-slice F extends with 3 release metrics + promotes to release-gate enforcement within Sub-slice F |

## Sub-slice Plan

The umbrella decomposes into 6 sub-slices labeled A through F.

| Sub-slice | Title | Mechanism | Risk | Dependencies |
|-----------|-------|-----------|------|--------------|
| **A** | Hook re-enable + regex tightening (highest leverage; absorbs work_list row 29) | 2 | Medium | Starts immediately after umbrella GO |
| **B** | Prime Builder rule formalizing AUQ-only decision channel | 1 | Low | A (so the rule references re-enabled enforcement) |
| **C** | Bridge review gate for owner-decision evidence (rule + bridge-compliance-gate hook extension) | 4 | Low | B (so bridge gate cites the AUQ-only rule) |
| **D** | Durable evidence audit pass + integrity tests | 3 | Low | A (post-tightening; reduced false-positive noise to audit) |
| **E** | Requirements-collection hook implementation (creates IPR; impl per existing GOV/DCL) | 5 | Medium-High | A, B, C (so the hook can rely on AUQ-only contract + bridge gate + tightened detector) |
| **F** | Release metrics: 3 doctor checks + **promotion to release-gate enforcement within Sub-slice F** (per Codex `-002` F3) | 6 | Medium | A, B, C, D, E (gates depend on all enforcement landing first) |

### Order of operations

```
A (hook re-enable + regex)
    ↓
B (Prime rule) ← can run in parallel with C after A lands
    ↓                  ↓
    +----- C (bridge review gate)
    ↓
D (evidence audit) ← can run in parallel with C
    ↓
E (requirements-collection hook impl)
    ↓
F (release metrics + enforcement promotion in single sub-slice scope)
```

Critical-path: A → C → E → F. Sub-slice B can run in parallel with C; D can run in parallel with C or E.

### Per-Sub-slice Acceptance Criteria

Each sub-slice files its own bridge thread following the standard NEW → GO/REVISED cycles → impl → post-impl REPORT NEW → VERIFIED protocol per `.claude/rules/file-bridge-protocol.md`.

**Sub-slice A — Hook re-enable + regex tightening:**
- Tightened regex passes empirical false-positive suite (factual "Awaiting Codex" / "Awaiting CI" statements no longer match)
- Genuine prose-decision asks still match (positive test set)
- T14-class guard extended to suppress recursive self-trigger when text describes the detector
- `GTKB_BLOCK_ON_PROSE_DECISION_ASK=0` removed from `.claude/settings.local.json`
- Block emission verified end-to-end via test fixtures
- work_list row 29 dropped after VERIFIED

**Sub-slice B — Prime Builder rule:**
- `.claude/rules/prime-builder-role.md` and `.claude/rules/acting-prime-builder.md` updated with explicit AUQ-only declaration
- Rule cites Sub-slice A's enforcement infrastructure
- Lists scope: approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, blocking owner decisions
- Test: rule-cited-in-bridge-proposal check (proposals must reference the AUQ-only rule when claiming owner-approved scope)

**Sub-slice C — Bridge review gate:**
- `.claude/rules/codex-review-gate.md` updated to require "Owner Decisions / Input" section in proposals/reports that depend on owner approval
- `.claude/hooks/bridge-compliance-gate.py` extended with regex check for the new section
- `.claude/rules/loyal-opposition.md` updated to NO-GO bridge entries lacking the section when applicable
- Test: bridge-compliance-gate rejects synthetic proposal lacking the section; accepts when present

**Sub-slice D — Durable evidence audit:**
- Audit script verifies `detected_via` field correctness for all entries in `memory/pending-owner-decisions.md` (no AUQ entries falsely classified as `prose:*`)
- Cleanup pass for any historical false positives (move to `## History` if appropriate)
- Test: file integrity check passes (schema validation, malformed entries absent, orphan IDs absent)

**Sub-slice E — Requirements-collection hook implementation:**
- Create `IPR-REQUIREMENTS-COLLECTION-HOOK-001` document in MemBase
- Implement hook per `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001`
- Hook classifies owner messages, identifies decision/requirement creation moments, enforces AUQ capture
- Test suite covers: classification accuracy, false-positive guards, integration with existing decision-tracker

**Sub-slice F — Release metrics + promotion to enforcement (per Codex `-002` F3):**

Sub-slice F has a single integrated scope: add the 3 doctor checks AND promote them to release-gate enforcement within the same sub-slice. The umbrella VERIFIED criteria require the gate-enforcement step complete; an informational-only baseline state is excluded.

Implementation order within Sub-slice F:
1. Add 3 doctor checks to `gt project doctor`:
   - `_check_untriaged_prose_decisions`: counts `prose:*` entries in `## Pending` of `memory/pending-owner-decisions.md`; FAIL if > 0
   - `_check_auq_coverage`: % of recent owner decisions captured via `detected_via: ask_user_question`; FAIL if < 100% over the rolling window
   - `_check_uncited_owner_input_bridges`: scans bridge thread VERIFIED entries; FAIL if any cite owner approval without an Owner Decisions section reference
2. Run baseline against current state; resolve any baseline pollution as part of Sub-slice F (or document as accepted residual via `## History` move)
3. Promote checks to release-candidate gate: doctor failure on any of the 3 metrics blocks the release-candidate gate
4. Test: synthetic baseline pollution causes release-candidate gate to fail; clean baseline passes
5. Sub-slice F VERIFIED requires the gate-enforcement step complete (not merely the checks added)

## Specification-Derived Test Plan (Umbrella Level)

The umbrella's VERIFIED criterion aggregates per-sub-slice VERIFIED status. Per-sub-slice tests are defined in each sub-slice's bridge proposal. Umbrella-level tests:

| Test ID | Spec Coverage | Procedure | Expected Result |
|---------|---------------|-----------|-----------------|
| **T-bridge-1** | `GOV-FILE-BRIDGE-AUTHORITY-001` | `grep "Document: gtkb-gov-askuserquestion-enforcement-stack" bridge/INDEX.md` | Match present |
| **T-spec-1** | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-askuserquestion-enforcement-stack-2026-05-04` | `preflight_passed: true`, `missing_required_specs: []` (after `-003` adds ADR-ISOLATION-APPLICATION-PLACEMENT-001) |
| **T-spec-2** | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All 6 sub-slice REPORTs aggregated; each reports its own spec-to-test mapping | Sum of sub-slice VERIFIED status |
| **T-out-of-applications** | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (umbrella does not create new `applications/` content) | `git diff <umbrella-baseline>..<umbrella-VERIFIED-commit> --name-only \| grep "^applications/"` across all sub-slice commits | Empty (umbrella sub-slice commits do not introduce files under `applications/`) |
| **T-umbrella-A-VERIFIED** | Sub-slice A complete | `grep "VERIFIED: bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-" bridge/INDEX.md` | Match present |
| **T-umbrella-B-VERIFIED** | Sub-slice B complete | Same pattern for slice-b | Match present |
| **T-umbrella-C-VERIFIED** | Sub-slice C complete | Same pattern for slice-c | Match present |
| **T-umbrella-D-VERIFIED** | Sub-slice D complete | Same pattern for slice-d | Match present |
| **T-umbrella-E-VERIFIED** | Sub-slice E complete | Same pattern for slice-e | Match present |
| **T-umbrella-F-VERIFIED** | Sub-slice F complete (includes release-gate promotion per Codex `-002` F3) | Same pattern for slice-f | Match present |
| **T-end-state-1** | All 3 release metrics PASS AND gate-enforcement active | `gt project doctor 2>&1 \| grep -E "(untriaged_prose\|auq_coverage\|uncited_owner_input).*PASS"` plus synthetic pollution → release-candidate gate FAIL test | 3 PASS lines + synthetic-pollution test rejects |
| **T-end-state-2** | Hook block emission active | `python -c "import os; print(os.environ.get('GTKB_BLOCK_ON_PROSE_DECISION_ASK', '1'))"` and inspect `.claude/settings.local.json` | Returns '1' (default); env override removed |
| **T-end-state-3** | Prime Builder rule cites AUQ-only contract | `grep -E "AUQ.only\|AskUserQuestion.*only valid" .claude/rules/prime-builder-role.md` | Match present |

Test commands include `python -m pytest`, `python scripts/bridge_applicability_preflight.py`, `git`, `find`, `grep` to satisfy the spec-derived-testing-mandatory regex.

## Specification-to-Test Mapping (Umbrella Level)

| Specification clause | Test ID(s) | Coverage |
|---------------------|------------|----------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | T-bridge-1 | Direct |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | T-spec-1 | Direct (preflight) |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T-spec-2 | Direct (Codex VERIFIED gate) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-out-of-applications | Direct (umbrella does not create applications/ content) |
| Sub-slice VERIFIED aggregation | T-umbrella-A-VERIFIED through T-umbrella-F-VERIFIED | Direct (6 sub-slices) |
| End-state guarantees | T-end-state-1, T-end-state-2, T-end-state-3 | Direct |
| `GOV-OWNER-DECISION-SURFACING-001` | (per-sub-slice tests in B, C, D, E) | Indirect (extension) |
| `GOV-REQUIREMENTS-COLLECTION-HOOK-001` | (per-sub-slice tests in E) | Indirect (impl) |
| `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` | (per-sub-slice tests in E) | Indirect (contract) |

Every required spec has direct or indirect test coverage. Indirect coverage is satisfied via the per-sub-slice bridge VERIFIED gates which carry their own spec-to-test mappings per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Acceptance Criteria

Umbrella acceptance:
- [ ] Codex GO on this umbrella scoping proposal
- [ ] Preflight passes (T-spec-1) — addressed by adding `ADR-ISOLATION-APPLICATION-PLACEMENT-001` to Specification Links
- [ ] All 6 sub-slice scopes confirmed; sub-slice ordering accepted
- [x] Owner pre-approval to file sub-slice bridges autonomously per work-list contract pattern (cited from S331 AUQ #3 "Autonomous progression"; see Owner Decisions / Input section)

Umbrella VERIFIED when:
- [ ] All 6 sub-slices VERIFIED in INDEX (T-umbrella-A through T-umbrella-F)
- [ ] All 3 end-state tests PASS (T-end-state-1, T-end-state-2, T-end-state-3)
- [ ] T-out-of-applications passes (umbrella sub-slice commits do not introduce files under `applications/`)
- [ ] Codex VERIFIED on this umbrella's post-impl REPORT (filed after the last sub-slice VERIFIED, listing all sub-slice closeouts)
- [ ] work_list row 29 (`GTKB-OWNER-DECISION-TRACKER-REGEX-TIGHTENING`) dropped (absorbed by Sub-slice A)
- [ ] Release-gate enforcement active per Sub-slice F (3 metrics promoted; synthetic-pollution test rejects)

## Risk / Rollback

| Risk | Likelihood | Impact | Mitigation |
|------|-----------:|-------:|------------|
| Sub-slice A regex tightening over-corrects (genuine prose decision asks fail to match) | Medium | High | Sub-slice A test plan requires positive + negative test sets; Codex review of regex changes against fixture corpus |
| Hook block re-enable causes Stop-mode infinite loop | Low | High | Existing bounded-exception design accounts for this (one block emission per turn); Sub-slice A re-confirms via test |
| Sub-slice E (requirements-collection hook) is large; may exceed 1-session implementation budget | Medium | Medium | Allow Sub-slice E to itself sub-divide if needed (E.1 IPR creation, E.2 hook impl) at execution time |
| Bridge gate (Sub-slice C) over-triggers, NO-GOing routine proposals | Medium | Medium | Section requirement is conditional on the proposal claiming owner-approved scope; routine proposals do not need it |
| Sub-slice F release-metric promotion blocks a needed release while baseline pollution remains | Medium | Medium | Sub-slice F's implementation order requires baseline cleanup BEFORE gate promotion (step 2 in Sub-slice F scope above); gate promotion only proceeds against a clean baseline |
| Sub-slice ordering changes mid-program | Low | Low | Each sub-slice is independent enough to be re-ordered or paused; umbrella REPORT documents final ordering |
| ISOLATION-018 stays blocked too long | Medium | Low (no external deadline) | Owner-controlled; can choose to unblock partial ISOLATION-018 work after Sub-slice A lands if enforcement ROI justifies it |

Rollback per sub-slice: each sub-slice's commit is independently revertable via `git revert`. Umbrella rollback is not a single operation; sub-slices revert individually if needed.

## Open Questions

(All scope decisions resolved via S331 owner AskUserQuestion answers in this session.)

| ID | Question | Resolution |
|----|----------|------------|
| OQ-A | Enforcement priority vs ISOLATION-018? | Block ISOLATION-018; enforcement first |
| OQ-B | Umbrella scope: which mechanisms? | Full 6-mechanism stack |
| OQ-C | Sub-slice filing autonomy? | Autonomous progression (S331 AUQ #3) |

Sub-slice-level open questions surface in each sub-slice's own bridge proposal at NEW filing time.

## Out of Scope

- Migration of files to `applications/Agent_Red/` (ISOLATION-018 sub-slices 18.C through 18.L; resumes after this umbrella VERIFIED). Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, that future work uses `applications/` placement; this umbrella does NOT create such content.
- Refactor of existing decision-tracker hook architecture (work_list row 23 `GTKB-BRIDGE-POLLER-COMPLEXITY-REFACTOR` related; trigger-conditional, not in this umbrella).
- Changes to existing bridge protocol semantics (NEW/REVISED/GO/NO-GO/VERIFIED lifecycle preserved exactly).
- Changes to existing destructive-gate hook (its overbroad `rm -r` matching of literal text in commit messages; separate hook-hygiene item).
- Cross-harness Codex enforcement (Codex's local hook surface is governed separately; Sub-slice C only updates the rule files which both harnesses load).
- Resolution of pre-existing scaffold-golden fixture mismatch (separate fixture-refresh slice; documented in 18.B post-impl REPORT).
- Session-tracker cwd anchoring fix (separate hook-hygiene slice; documented in 18.B post-impl REPORT).

## Project Root Boundary Compliance

This proposal:
- Operates entirely within `E:/GT-KB/`.
- All sub-slice changes target files within `E:/GT-KB/.claude/`, `E:/GT-KB/memory/`, `E:/GT-KB/scripts/`, `E:/GT-KB/groundtruth-kb/` (sub-slice E hook impl), and `E:/GT-KB/bridge/` (sub-slice bridge files).
- No live-dependency paths outside `E:/GT-KB/`.
- Does NOT depend on Agent Red as a live GT-KB artifact (per 2026-05-04 owner correction; Agent Red is a separate project).
- Does NOT create new content under `applications/` (per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` scope; that authority covers ISOLATION-018 sub-slices, not this umbrella).
- Per `.claude/rules/project-root-boundary.md`.

## Owner Decisions / Input

This umbrella's scope was confirmed via three AskUserQuestion calls in S331 (this session):

1. **Enforcement priority** — owner selected: "Block ISOLATION-018; enforcement first (Recommended)" (issued before `-001`)
2. **Umbrella scope** — owner selected: "Full 6-mechanism stack (Recommended)" (issued before `-001`)
3. **Sub-slice autonomy** — owner selected: "Autonomous progression (Recommended)" (issued AFTER `-001` filed; resolves Codex `-002` F2 evidence requirement). Owner option text: "file Sub-slice A bridge → wait for Codex GO → implement → post-impl REPORT → wait for Codex VERIFIED → commit → file Sub-slice B → etc., autonomously through F. No per-sub-slice owner approval needed; AskUserQuestion only for substantive scope ambiguities surfaced during sub-slice drafting."

Per-sub-slice owner input (if any) will be collected via AskUserQuestion at each sub-slice's filing time.

## Provenance

| Source | Reference |
|--------|-----------|
| Umbrella trigger | S331 owner directive (this session): "Prime Builder consistency needs to be enforced mechanically" |
| Existing surfacing impl | `bridge/gtkb-gov-owner-decision-surfacing-slice1-006.md` VERIFIED 2026-04-27 |
| Existing block emission impl | `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-006.md` VERIFIED |
| Deferred regex tightening | `memory/work_list.md` row 29 (S328) |
| Existing requirements-collection specs | `GOV-REQUIREMENTS-COLLECTION-HOOK-001` (specified), `DCL-REQUIREMENTS-COLLECTION-HOOK-CONTRACT-001` (specified) in MemBase |
| Owner scope confirmations | This S331 conversation: 3 AskUserQuestion answers (priority, scope, autonomy) |
| Pattern precedent (umbrella structure) | `bridge/gtkb-isolation-018-agent-red-file-migration-005.md` GO at -006 (12-sub-slice umbrella) |
| Codex `-002` review | `bridge/gtkb-gov-askuserquestion-enforcement-stack-2026-05-04-002.md` (4 findings: F1 preflight, F2 owner evidence, F3 F-scoping, F4 Agent Red framing) |
| Placement authority | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (verified) — added per Codex `-002` F1 |
| Live probes | `python` MemBase queries, `grep -nE`, `ls bridge/`, `head memory/work_list.md` (executed 2026-05-04 in this session) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
