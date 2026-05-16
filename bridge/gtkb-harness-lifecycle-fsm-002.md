GO

# Loyal Opposition Review — Harness Lifecycle Finite State Machine (WI-3339)

bridge_kind: review_verdict
Document: gtkb-harness-lifecycle-fsm
Version: 002 (GO)
Author: Loyal Opposition (Claude, harness B — stand-alone review)
Date: 2026-05-16 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-harness-lifecycle-fsm-001.md
Recommended commit type: feat

## Stand-Alone Review Disclosure

This verdict is a stand-alone Loyal Opposition review authored by the Claude
harness (harness `B`), which also authored the proposal. It is NOT an
independent counterpart review by Codex (harness `A`). The owner directed on
2026-05-16 that Claude perform stand-alone Loyal Opposition review while Codex
is rate-limited (through 2026-05-22) and until the Antigravity / Gemini reviewer
harness is onboarded. The full bridge review gate is applied — specification
linkage, test derivation, both mandatory preflights, and a genuine defect
search. The thread remains open to a Codex counterpart verdict.

## Decision

GO. The proposal is approved for implementation within the stated scope. It
links every relevant governing specification, derives its tests from FR2's
transition graph, passes both mandatory preflights, draws a clean scope
boundary against WI-3340, and is strictly additive (one new module, one new
test file). One non-blocking finding is recorded; it forwards a requirement
question to the WI-3340 stage and does not gate this GO.

## Specification Links

The proposal cites every relevant governing specification; the applicability
preflight confirms no missing required or advisory specs:

- `REQ-HARNESS-REGISTRY-001` — FR2 (governing): the four-state lifecycle FSM.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — the harness-registry architecture.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
  `GOV-FILE-BRIDGE-AUTHORITY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001` —
  cross-cutting bridge and isolation specs.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory.

## Applicability Preflight

- packet_hash: `sha256:77f0ea4a939073f6ce45a0f5e9972bb3cf45535fb7c45bdb31325dda70e2f295`
- bridge_document_name: `gtkb-harness-lifecycle-fsm`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-harness-lifecycle-fsm-001.md`
- operative_file: `bridge/gtkb-harness-lifecycle-fsm-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-harness-lifecycle-fsm`
- Operative file: `bridge\gtkb-harness-lifecycle-fsm-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Prior Deliberations

- `DELIB-2079` — Antigravity Integration design. Q3 is the direct authority:
  the owner chose `registered → active ⇄ suspended → retired` (four states, a
  single enum) over a three-state model and two orthogonal axes. The proposal's
  FSM matches Q3.
- `DELIB-2080` — role-portability amendment; not implemented by this work item.
- Bridge threads `gtkb-harness-registry-table-schema` (WI-3337) and
  `gtkb-harness-registry-hot-path-projection` (WI-3338), both VERIFIED — the
  table whose `status` column this FSM governs, and the projection that carries
  it. No conflict.

## Test Derivation Review

The seven planned tests derive directly from FR2: every one of the four
transition edges is asserted valid; representative non-edges (including
`active→retired` and same-state pairs) are asserted invalid; `retired` terminal
is asserted; unknown-status handling is asserted; `next_states` is asserted
per-state. The mapping covers FR2's transition graph completely with no gap.

## Findings

### F1 — `active → retired` is not a direct edge; the WI-3340 `retire` verb must account for this (P3, non-blocking)

Observation: the proposal implements FR2's notation as the literal four-edge
graph. There is no direct `active → retired` edge; retiring an `active` harness
is the two-step `active → suspended → retired`. The proposal states this
explicitly in its Requirement Sufficiency section.

Deficiency rationale: this is the correct, transparent reading of the FR2
notation and is not a defect in WI-3339 — the literal graph is a complete,
deterministic FSM. However, it has a downstream consequence: the WI-3340
`gt harness retire` verb will, against an `active` harness, either have to fail
with guidance to suspend first, or auto-suspend then retire. Which behavior the
owner wants — and, more fundamentally, whether the owner intends a direct
`active → retired` edge at all — is a requirement question that should be
resolved before WI-3340 finalizes the `retire` verb.

Recommended action: GO this work item as-is (the FSM correctly implements the
literal spec). Carry F1 forward into the WI-3340 proposal, which should surface
the `active → retired` question to the owner via AskUserQuestion. If the owner
chooses a direct edge, it is a one-line addition to `_TRANSITIONS` plus one test
— a small follow-up, not a rework. Non-blocking for WI-3339.

## Positive Confirmations

- Both target paths are within `E:\GT-KB`; the in-root clause passes.
- The change is strictly additive — one new pure-logic module, one new test
  file; no existing table, accessor, module, hook, or reader is modified.
  Rollback is clean.
- The module is correctly placed in the `groundtruth_kb` package so the WI-3340
  `gt harness` CLI can consume it without a backwards import.
- The proposal is transparent about its interpretation of the FR2 notation
  rather than silently choosing a transition graph — the Requirement
  Sufficiency note lets the reviewer and the owner see and challenge the
  reading.
- The scope boundary against WI-3340 (CLI enforcement) is explicit and correct,
  mirroring the WI-3338 mechanism-vs-consumer split that verified cleanly.
- Both mandatory preflights pass: applicability `preflight_passed: true` with no
  missing specs; clause preflight 0 evidence gaps, 0 blocking gaps, exit 0.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-lifecycle-fsm` — result: `preflight_passed: true`, `packet_hash: sha256:77f0ea4a939073f6ce45a0f5e9972bb3cf45535fb7c45bdb31325dda70e2f295`, `missing_required_specs: []`, `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-lifecycle-fsm` — result: 5 clauses, 0 evidence gaps, 0 blocking gaps, exit 0.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-harness-lifecycle-fsm` — result: thread found, one version (`-001` NEW), no drift.

## Owner Action Required

None for this GO. Finding F1 records a requirement question (`active → retired`
direct edge) to be surfaced to the owner via AskUserQuestion during the WI-3340
`gt harness` CLI work item.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
