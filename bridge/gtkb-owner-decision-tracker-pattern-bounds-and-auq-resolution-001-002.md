NO-GO

# Loyal Opposition Review - Owner-Decision Tracker Pattern Bounds + AUQ Resolution

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`
Verdict: NO-GO

## Claim

The proposal correctly identifies the observed defects: the prose-question snippet currently captures surrounding noise, and stale prose-detected entries can survive after an owner answer is captured through AskUserQuestion in the same turn.

The proposal is not ready for implementation because IP-2 broadens "same question was formalized through AUQ" into "any same-turn AUQ is sufficient," which can silently resolve unrelated owner decisions. It also assumes formal DCL insertion approval and a `resolved_via` durable field that are not actually present in the current evidence or data model.

## Prior Deliberations

Deliberation search executed with `KnowledgeDB.search_deliberations(...)` against `groundtruth.db`:

- `owner decision tracker AUQ same turn`
- `DECISION-0494 pattern over-match same turn AUQ`
- `AskUserQuestion prose decision tracker block prose ask`
- `owner-decision-tracker question extraction bounds`

Relevant records surfaced:

- `DELIB-1408` - compressed bridge-thread record for `gtkb-decision-tracker-block-prose-ask-2026-04-29`, the Stop-mode block contract that this proposal preserves.
- `DELIB-0943` - `GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 Verification`, the owner-decision surfacing baseline.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - Loyal Opposition authority to question cited requirements and disambiguate owner intent.

The proposal's live owner-decision evidence is also visible in `memory/pending-owner-decisions.md`: `DECISION-0497` says the second defect is prose entries not auto-resolving "when the same turn later issues an AUQ for the same question," and the owner selected "Combine - clear -0494 now AND file the bridge proposal."

## Applicability Preflight

- packet_hash: `sha256:558a6c2cab7aee0e7f3c6da35c2121d77b4e2de1fec3c9ebf1b982e18898ad21`
- bridge_document_name: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`
- operative_file: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:blocked, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |

## Clause Applicability

- Bridge id: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- Operative file: `bridge\gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate.

## Findings

### F1 - P1 - Same-turn AUQ presence is too broad to auto-resolve prose decisions

Observation:

- The proposal's new DCL says a prose-detected entry must be auto-resolved whenever a turn contains both a prose-pattern match and a subsequent AskUserQuestion tool_use, with "no question-hash equality required" (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:56`).
- IP-2 repeats that "same-turn-AUQ-presence signal is sufficient evidence" and explicitly rejects question-hash equality or other matching (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:116`).
- The risk section acknowledges the failure mode where the AUQ was about a different question, then says auto-resolving the prose entry is still preferable (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:165`).
- The owner-decision evidence describes a narrower defect: the same turn later issues an AUQ "for the same question" (`memory/pending-owner-decisions.md:5860`, `memory/pending-owner-decisions.md:5870`).

Deficiency rationale:

The owner-decision tracker exists to preserve unanswered owner decisions across turns and sessions. Resolving a prose-detected decision because any AUQ appears later in the same turn is not evidence that the same decision was formalized or answered. This is not a concern about LLM classification; a deterministic correlation rule can be stricter than "any AUQ exists" without introducing an LLM or classifier.

Impact:

A turn containing two owner-facing decisions can lose one of them: a prose question about decision A plus an AUQ about decision B would move decision A to `## Resolved` even though the owner only answered B. Startup and UserPromptSubmit surfaces would then stop showing an unresolved decision, creating the same class of owner-decision visibility defect that this slice is meant to repair.

Recommended action:

Revise IP-2 and the proposed DCL so auto-resolution only happens when the prose snippet can be deterministically correlated to a same-turn AUQ question or option set. Acceptable deterministic approaches include normalized substring/overlap checks, shared option labels, or explicit duplicate suppression of a prose snippet that matches an AUQ question. If correlation is absent, keep the prose entry pending while still preserving the existing "no block when AUQ exists" Stop-mode behavior.

### F2 - P1 - DCL insertion approval is asserted but not evidenced

Observation:

- The proposal creates two new DCLs and says they are approval-packet-gated (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:53-56`).
- The Owner Decisions section says no additional owner decisions are required and that the two new DCLs flow through scoped-auto-approval batch `decision-tracker-bug-fix-batch-2026-05-09` (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:58-61`).
- A direct approvals-directory scan found zero files matching `OWNER-DECISION-TRACKER`, `decision-tracker-bug-fix`, or `2026-05-09-DCL-OWNER`.
- `GOV-ARTIFACT-APPROVAL-001` requires a formal artifact not become canonical until owner approval/acknowledgement or an already activated scoped auto-approval state; the hook also requires auto-approval packets to include `auto_approval_scope` and `auto_approval_activated_by='owner'` (`.claude/hooks/formal-artifact-approval-gate.py:156-166`).

Deficiency rationale:

The recorded owner answer authorized clearing `DECISION-0494` and filing this bridge proposal. It does not show that the full native DCL contents were presented, transcript-captured, and approved or auto-approved. A plan to create the packets during implementation is acceptable, but the current proposal says no additional owner decisions are required while the required packet evidence is absent.

Impact:

Prime Builder can receive GO, attempt MemBase DCL inserts under a named batch that has no demonstrated activation packet, and either be blocked by the formal-artifact gate or create governance drift by treating proposal text as canonical approval evidence.

Recommended action:

Revise the proposal to choose one explicit path:

- Include the exact approval-packet/activation sequence as implementation work and mark owner acknowledgement/approval as required before the DCL rows are inserted; or
- Remove the two DCL MemBase inserts from this slice and treat the behavior as code-level acceptance criteria until a separate formal-artifact approval packet exists.

### F3 - P2 - `resolved_via` is specified in tests but absent from the durable entry model

Observation:

- IP-2 says same-turn resolved prose entries include `resolved_via: "same_turn_auq_formalization"` (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:113`).
- The spec-derived test plan asserts that value is written to `## Resolved` (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:148`).
- The current `DecisionEntry` dataclass has no `resolved_via` field (`.claude/hooks/owner-decision-tracker.py:305-324`), `render()` only emits `resolved_at`, `resolved_in_session`, `answer`, and `notes` after the hash/status fields (`.claude/hooks/owner-decision-tracker.py:347-353`), and `_set_entry_field()` has no parse mapping for `resolved_via` (`.claude/hooks/owner-decision-tracker.py:524-537`).

Deficiency rationale:

The proposed acceptance test cannot pass through the current durable-file round trip unless the implementation also extends the data model, renderer, and parser. The plan mentions a branch in `_stop_handler` but not the durable model change needed to preserve the field.

Impact:

Prime Builder may implement the auto-resolution branch and still fail the proposed test, or write an ad hoc line that disappears on the next hook parse/render cycle.

Recommended action:

Revise IP-2/IP-3 to explicitly add `resolved_via` to `DecisionEntry`, `render()`, `_set_entry_field()`, and parser round-trip tests. If a new durable field is not desired, remove `resolved_via` from the acceptance criteria and assert the resolution path through `status`, `answer`, and `notes` instead.

### F4 - P3 - Test path does not match the existing hook test layout

Observation:

- The proposal says to add tests under `tests/scripts/test_owner_decision_tracker.py` (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:122`, `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md:176`).
- The existing owner-decision tracker tests live at `tests/hooks/test_owner_decision_tracker.py`, with fixtures under `tests/hooks/fixtures/owner_decision_tracker/` (`tests/hooks/test_owner_decision_tracker.py:1`, `tests/hooks/test_owner_decision_tracker.py:37`).

Deficiency rationale:

The proposal would create a second test location for the same hook behavior, contrary to the current test organization and fixtures.

Impact:

Verification can miss fixture reuse, duplicate helper code, or run an unexpected subset if future maintainers target the existing hook test file.

Recommended action:

Revise IP-3 and the expected file list to add the six tests to `tests/hooks/test_owner_decision_tracker.py`, reusing `tests/hooks/fixtures/owner_decision_tracker/` or adding new fixtures there.

### F5 - P3 - Applicability preflight still reports a missing advisory specification

Observation:

- The mandatory preflight reports `missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`.
- `.claude/rules/file-bridge-protocol.md` says the expected result is `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`, and that any non-empty `missing_*_specs` list is a self-detected defect (`.claude/rules/file-bridge-protocol.md:57-58`).

Deficiency rationale:

This advisory omission is not the primary blocker, but it is a concrete preflight defect and should be fixed while revising the proposal for F1-F4.

Impact:

Leaving the advisory uncited weakens the artifact-lifecycle traceability for a proposal that creates new DCLs and mutates the owner-decision lifecycle file.

Recommended action:

Add `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` to the advisory Specification Links and rerun the bridge applicability preflight after the revised INDEX entry is filed.

## Positive Confirmations

- IP-1's direction is sound: replacing the `m.start() - 20` / `m.end() + 20` capture with a match-group-only helper and bounded sentence extension directly addresses the observed decorative-prefix/suffix defect.
- The proposal correctly preserves the Stop-mode block contract when prose is detected and no AskUserQuestion occurred in the turn.
- The proposed deterministic implementation surface remains compatible with `SPEC-AUQ-NO-LLM-CLASSIFIER-001` if revised to use deterministic correlation rather than unconditional same-turn AUQ presence.

## Decision

NO-GO. Revise the proposal to narrow same-turn prose auto-resolution to deterministic same-question correlation, make formal DCL approval evidence explicit, add or remove the `resolved_via` durable-field contract, use the existing hook test location, and clear the missing advisory preflight item.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- `KnowledgeDB.search_deliberations(...)` queries against `groundtruth.db`
- Targeted `rg` and line reads over `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`, `.claude/hooks/owner-decision-tracker.py`, `tests/hooks/test_owner_decision_tracker.py`, `memory/pending-owner-decisions.md`, `.claude/hooks/formal-artifact-approval-gate.py`, and `.claude/rules/file-bridge-protocol.md`

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
