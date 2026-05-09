NO-GO

# Loyal Opposition Review - Owner-Decision Tracker Pattern Bounds + AUQ Resolution REVISED-1

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`
Verdict: NO-GO

## Claim

The revision closes several prior findings directionally: it replaces bare same-turn AUQ presence with an attempted deterministic correlation rule, adds an explicit per-DCL approval-packet sequence, moves tests to the existing hook test file, adds the `resolved_via` durable-field work, and clears the bridge applicability preflight advisory miss.

It is not ready for implementation because the proposed Jaccard correlation rule can still auto-resolve unrelated owner decisions with shared boilerplate phrasing, and the DCL approval-packet plan uses an invalid packet schema for the current formal-artifact gate.

## Prior Deliberations

Deliberation searches executed with `KnowledgeDB.search_deliberations(...)` against `groundtruth.db`:

- `owner decision tracker AUQ same turn deterministic correlation`
- `gtkb-decision-tracker-block-prose-ask`
- `formal artifact approval packet DCL design_constraint artifact_type`
- `DCL ARTIFACT APPROVAL HOOK formal artifact approval packet`
- `AskUserQuestion prose decision tracker block prose ask`

Relevant records surfaced:

- `DELIB-1408` - bridge-thread record for `gtkb-decision-tracker-block-prose-ask-2026-04-29`; this is the Stop-mode prose-decision-ask block contract that the proposal must preserve.
- `DELIB-0943` - `GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 Verification`; relevant owner-decision visibility baseline.
- `DELIB-0835` - owner decision requiring strict artifact approval and audit trail with optional auto-approval.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner decision requiring full-text transparency for specification capture.

Live owner-decision evidence:

- `memory/pending-owner-decisions.md:5860` records the original defect as prose entries not auto-resolving when the same turn later issues an AUQ "for the same question."
- `memory/pending-owner-decisions.md:5874` and `:5884` record owner approval to file REVISED-1 now, not approval to weaken the owner-decision visibility invariant.

## Applicability Preflight

- packet_hash: `sha256:cfe320c10828c9c60a4ff507959d57e8bca1917dc3645f6ea8c833d268023391`
- bridge_document_name: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`
- operative_file: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- Operative file: `bridge\gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and `must_apply` applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Findings

### F1 - P1 - Jaccard overlap still resolves unrelated owner decisions

Observation:

- The revised DCL and implementation plan mark Jaccard token-set similarity >= 0.5 as sufficient correlation for auto-resolving a prose-detected decision (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md:93`, `:123`, `:125`).
- The proposed tokenization is lower-case plus whitespace/punctuation splitting; it does not remove decision-boilerplate words or require discriminating subject tokens to match (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md:123`, `:133`).
- The current prose patterns intentionally match boilerplate-heavy phrasings such as `want me to ... or ...?` and `should I ... or ...?` (`.claude/hooks/owner-decision-tracker.py:108-113`).
- Concrete deterministic counterexamples using the proposal's token-set rule:
  - `Want me to commit now or wait?` vs `Want me to deploy now or wait?` has Jaccard `6/8 = 0.75`.
  - `Should I approve the DCL or defer?` vs `Should I approve the deployment or defer?` has Jaccard `6/8 = 0.75`.
  Both are different owner decisions, but both exceed the proposed >= 0.5 threshold.

Deficiency rationale:

This revision fixes the prior "any AUQ" defect only partially. Because the proposed Jaccard rule counts high-frequency decision-scaffold tokens, unrelated same-turn decisions with similar owner-input phrasing can still be treated as the same question. The owner-decision tracker is fail-closed state preservation; in uncertain cases the safe result is a duplicate pending entry, not silent resolution of a potentially unanswered decision.

Impact:

A same-turn prose ask about decision A plus a formal AUQ about decision B can still move A to `## Resolved`. Startup and UserPromptSubmit surfaces would then suppress an unresolved owner decision, recreating the owner-decision visibility failure this slice is meant to repair.

Recommended action:

Revise the correlation rule to use only evidence that is hard to satisfy accidentally:

- normalized exact identity or normalized substring containment with a minimum substantive length; and/or
- option-label overlap tied to the same AUQ question; and/or
- token overlap after removing decision-boilerplate terms, with a requirement that at least one discriminating noun/verb token from each side matches.

Add a regression test where two same-turn decisions share boilerplate but differ in the action subject, and assert the prose entry remains pending.

### F2 - P1 - DCL approval-packet plan still will not pass the formal-artifact gate

Observation:

- IP-IIa says to write the DCL approval packet using `artifact_type="spec"` and cites `narrative-artifact-approval.toml` as the schema source (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md:142`).
- The active formal-artifact approval gate requires `approval_mode` as a packet field and accepts only `approve`, `acknowledge`, `edit-and-approve`, or `auto` (`.claude/hooks/formal-artifact-approval-gate.py:60-67`, `:84`, `:142-144`).
- The same gate accepts only its configured `VALID_ARTIFACT_TYPES` set and emits a hard validation error when `artifact_type` is outside that set (`.claude/hooks/formal-artifact-approval-gate.py:75-84`, `:139-140`). Current DCL packets use `artifact_type: "design_constraint"`; for example, `.groundtruth/formal-artifact-approvals/2026-05-08-DCL-ARTIFACT-APPROVAL-HOOK-001-V3.json:2`.
- For manual approval/acknowledgement, the gate also requires `approved_by` or `acknowledged_by`; IP-IIa/IP-IIb mention neither (`.claude/hooks/formal-artifact-approval-gate.py:167-168`; proposal packet list at `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md:142`).

Deficiency rationale:

The proposal changed from an unproven auto-approval batch to explicit per-DCL owner acknowledgement, which is the right direction. But the written packet recipe is still mechanically invalid: it uses the wrong gate vocabulary and omits fields that the active gate requires before `db.insert_spec(...)` can proceed under `GTKB_FORMAL_APPROVAL_PACKET`.

Impact:

Prime Builder can receive GO, present the DCLs to the owner, then fail at the formal-artifact gate because the generated packet shape does not validate. Worse, if Prime tries to work around the gate, the new DCL rows would lack the approval evidence required by `DELIB-0835` and the formal artifact approval contract.

Recommended action:

Revise IP-IIa and IP-IIb to cite `.claude/hooks/formal-artifact-approval-gate.py` as the mechanical packet schema and spell out the exact fields:

- `artifact_type: "design_constraint"` for DCL rows.
- `approval_mode: "approve"` or `approval_mode: "acknowledge"` as appropriate.
- `approved_by: "owner"` or `acknowledged_by: "owner"` for the manual path.
- all current required fields from `REQUIRED_PACKET_FIELDS`, including `source_ref`, `full_content`, `full_content_sha256`, `presented_to_user`, `transcript_captured`, `explicit_change_request`, `changed_by`, and `change_reason`.

Add a test or dry-run validation step that calls the formal-artifact packet validator on both planned packet shapes before inserting either DCL.

## Positive Confirmations

- The live indexed REVISED-1 passes the mandatory bridge applicability preflight with no missing required or advisory specs.
- The mandatory ADR/DCL clause preflight reports no must-apply evidence gaps and no blocking gaps.
- F3 is closed directionally: the proposal now includes `DecisionEntry`, `render()`, `_set_entry_field()`, and a round-trip test for `resolved_via`.
- F4 is closed: the proposed tests now target `tests/hooks/test_owner_decision_tracker.py`.
- F5 is closed: `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` is cited and the preflight advisory list is empty.
- IP-1 remains sound: match-group-only extraction with bounded sentence extension addresses the over-match symptom.
- The Stop-mode block contract is preserved when prose is detected and no AskUserQuestion tool_use occurred in the turn.

## Decision

NO-GO. Revise the proposal to make same-turn prose/AUQ correlation stricter than raw Jaccard over boilerplate-heavy question text, and correct the per-DCL formal-artifact approval packet recipe so it matches the active formal-artifact gate.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- `KnowledgeDB.search_deliberations(...)` queries against `groundtruth.db`
- Targeted `rg`, `Select-String`, and line reads over `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`, `.claude/hooks/owner-decision-tracker.py`, `.claude/hooks/formal-artifact-approval-gate.py`, `.groundtruth/formal-artifact-approvals/`, `tests/hooks/test_owner_decision_tracker.py`, and `memory/pending-owner-decisions.md`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
