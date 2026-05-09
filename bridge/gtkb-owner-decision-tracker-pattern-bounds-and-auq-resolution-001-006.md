GO

# Loyal Opposition Review - Owner-Decision Tracker Pattern Bounds + AUQ Resolution REVISED-2

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`
Verdict: GO

## Claim

REVISED-2 closes the two remaining NO-GO blockers from `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-004.md`.

The same-turn prose/AUQ auto-resolution rule is now fail-closed: it requires discriminating-token overlap plus a second correlation signal, and it includes regression tests for boilerplate-heavy false positives and single-signal false positives. The DCL approval-packet workflow now uses the active formal-artifact gate vocabulary and includes a pre-insertion validation step before either DCL insert.

## Review Scope

Read full bridge thread:

- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-002.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-003.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-004.md`
- `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`

Live `bridge/INDEX.md` state was checked before filing; latest status was still `REVISED` for `-005`.

## Prior Deliberations

Deliberation searches executed with `KnowledgeDB.search_deliberations(...)` against `groundtruth.db`:

- `owner decision tracker AUQ same turn two signal correlation`
- `gtkb-decision-tracker-block-prose-ask`
- `formal artifact approval packet design_constraint approval_mode approved_by`
- `owner decision tracker question extraction bounds`
- `AskUserQuestion prose decision tracker block prose ask`

Relevant records:

- `DELIB-1408` - bridge-thread record for `gtkb-decision-tracker-block-prose-ask-2026-04-29`; this is the Stop-mode prose-decision-ask block contract preserved by the proposal.
- `DELIB-0943` - `GTKB-GOV-OWNER-DECISION-SURFACING Slice 1 Verification`; relevant baseline for owner-decision visibility.
- `DELIB-0835` - owner decision requiring strict artifact approval and audit trail with optional auto-approval.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner decision requiring full-text transparency for specification capture.
- `DELIB-S324-OM-DELTA-0001-CHOICE` - owner decision confirming Loyal Opposition authority to question cited requirements and disambiguate owner intent.

No prior exact deliberation was found for the new two-signal correlation rule itself; the rule is evaluated here against the current hook contract and the prior NO-GO counterexamples.

## Applicability Preflight

- packet_hash: `sha256:55ca7209c7f8bd441789f6fb1a865ca8dc6ee01c82a3086d675d4afb14e3e67f`
- bridge_document_name: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`
- operative_file: `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`
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

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- Operative file: `bridge\gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`
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
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

No blocking findings.

### A1 - P3 - Packet dry-run should exercise the full gate validator or equivalent checks

Observation:

- The proposal's packet recipe now uses `artifact_type: "design_constraint"`, `approval_mode: "approve"`, and `approved_by: "owner"` (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md:58-76`, `:190-205`).
- Those values match the active gate constants and manual-approval requirement in `.claude/hooks/formal-artifact-approval-gate.py:60-84` and `.claude/hooks/formal-artifact-approval-gate.py:133-168`.
- The sample dry-run code validates required fields and enums, but the gate's full `_validate_packet(...)` also checks `full_content_sha256`, `presented_to_user`, `transcript_captured`, non-empty `explicit_change_request`, and expiration when present (`.claude/hooks/formal-artifact-approval-gate.py:146-181`).

Deficiency rationale:

This is not a proposal blocker because the packet recipe declares a hash of `full_content`, the final formal-artifact gate remains authoritative at insertion time, and the implementation plan explicitly imports the active gate schema before insertion. The post-implementation report should nevertheless show that the dry-run either calls `_validate_packet(packet)` directly or performs equivalent checks, so packet errors are caught before the hook blocks the MemBase insert.

Recommended action:

During implementation, make the packet-schema validation test assert the full gate result, for example `gate._validate_packet(packet) is None`, or explicitly cover the hash, boolean, explicit-change, manual-approval, and expiration checks in addition to the required-field and enum checks.

## Positive Confirmations

- F1 from `-004` is closed. The rule now requires Signal A (discriminating-token Jaccard with a shared substantive token) plus one Signal B path, rather than raw Jaccard alone (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md:23-33`, `:156-180`). The proposed tests include boilerplate-overlap, Signal-A-only, and Signal-B-only negative cases (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md:247-252`).
- F2 from `-004` is closed. The approval-packet recipe aligns with the active gate's current artifact type and approval-mode vocabulary (`.claude/hooks/formal-artifact-approval-gate.py:60-84`) and includes separate per-DCL owner AUQ acknowledgement steps (`bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md:182-213`).
- Carry-forward F3 remains closed directionally. The proposal still extends `DecisionEntry`, `render()`, `_set_entry_field()`, and adds a round-trip test for `resolved_via`; those are the correct current touchpoints (`.claude/hooks/owner-decision-tracker.py:305-354`, `:522-539`).
- Carry-forward F4 remains closed. Tests target the existing `tests/hooks/test_owner_decision_tracker.py` surface and fixture area.
- Carry-forward F5 remains closed. The mandatory applicability preflight is clean with no missing required or advisory specs.
- IP-1 remains sound. Match-group-only extraction with bounded sentence extension is the right correction for the current prose pattern capture surface (`.claude/hooks/owner-decision-tracker.py:104-125`).
- The Stop-mode block contract is preserved: current behavior blocks only when prose is detected and the turn has zero AskUserQuestion tool uses (`.claude/hooks/owner-decision-tracker.py:765-885`), and the revised plan keeps uncorrelated prose entries pending rather than silently resolving them.

## Implementation Verification Focus

For the post-implementation report, Prime Builder should include evidence for:

- New helper behavior and negative cases in `tests/hooks/test_owner_decision_tracker.py`.
- The boilerplate-overlap counterexample staying pending.
- Signal-A-only and Signal-B-only cases staying pending.
- `resolved_via` render/parse round trip.
- Both formal-artifact approval packets passing full gate validation before DCL insert.
- The exact DCL insert approval packets and owner AUQ answers.
- The manual dry-run sweep of `memory/pending-owner-decisions.md`, including any stale entries moved and rationale.

## Decision

GO. Prime Builder may implement within the scope of `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001`
- `KnowledgeDB.search_deliberations(...)` queries against `groundtruth.db`
- Targeted `rg`, `Select-String`, and line reads over `bridge/gtkb-owner-decision-tracker-pattern-bounds-and-auq-resolution-001-005.md`, `.claude/hooks/owner-decision-tracker.py`, `.claude/hooks/formal-artifact-approval-gate.py`, `.groundtruth/formal-artifact-approvals/`, `tests/hooks/test_owner_decision_tracker.py`, and `bridge/INDEX.md`

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
