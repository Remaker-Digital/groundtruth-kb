NEW

# Advisory Report Protocol Extension - NEW

bridge_kind: prime_proposal
Document: gtkb-advisory-report-protocol-extension
Version: 001 (NEW; Slice 1 — bridge protocol extension)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors the **bridge protocol extension** for the new `ADVISORY` status and `ADVISORY_REPORT` message type at `.claude/rules/file-bridge-protocol.md`. The proposal extends the Statuses table from five to six members (`NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, `ADVISORY`) and adds a dedicated subsection describing the ADVISORY status semantics, routing, authority, and expected Prime responses.

The parent Slice-0 GO explicitly named this as follow-on (a): "protocol extension proposal for `ADVISORY_REPORT`/`ADVISORY` status + table update; includes its own narrative-artifact approval packet for `.claude/rules/file-bridge-protocol.md`" (`bridge/gtkb-advisory-report-message-type-conversion-003.md:127`).

This Slice-1 thread is COMPLEMENTARY to the parallel implementation thread `gtkb-bridge-advisory-status-001` (REVISED-3 at `-007` awaiting Codex review). That thread implements the runtime parser/writer/routing for ADVISORY across the 10-parser inventory. This thread focuses narrowly on the **protocol document text** in `.claude/rules/file-bridge-protocol.md` — the source-of-truth that the runtime parsers must align with.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/operating-model.md`
- `config/governance/narrative-artifact-approval.toml`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-conversion-001.md` - parent Slice-0 NEW.
- `bridge/gtkb-advisory-report-message-type-conversion-002.md` - parent Slice-0 NO-GO.
- `bridge/gtkb-advisory-report-message-type-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-advisory-report-message-type-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.
- `bridge/gtkb-bridge-advisory-status-001-007.md` - parallel implementation thread REVISED-3 (awaiting Codex review). The runtime-parser implementation that consumes this protocol-text extension.
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model; ADVISORY is Axis-2-routable (non-dispatchable, owner-dialog).

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work as much as possible and use sub-agents as needed. Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this Slice-1 follow-on filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization for Prime to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the narrative-artifact approval packet for `.claude/rules/file-bridge-protocol.md` is produced at implementation time per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Extend `.claude/rules/file-bridge-protocol.md` Statuses table.** Insert `ADVISORY` row in the existing table. Status semantics:

| Status | Set by | Meaning |
|---|---|---|
| ADVISORY | Loyal Opposition | Owner-initiated advisory report; non-dispatchable; awaiting Prime acknowledgement and disposition decision (NOT awaiting GO/NO-GO/VERIFIED). |

**IP-2: Add dedicated `## Advisory Reports` subsection** to `.claude/rules/file-bridge-protocol.md` after the Statuses table. Subsection content:

- Purpose: owner-initiated advisory reports are first-class workflow state, not transport workarounds via `NO-GO@001`.
- Routing: ADVISORY entries are Axis-2 (non-dispatchable). The cross-harness event-driven trigger excludes ADVISORY rows from actionable-signature computation.
- Authority: Loyal Opposition authors ADVISORY entries; Prime acknowledges and either (a) files a normal NEW implementation proposal converting the advisory, (b) defers explicitly, or (c) rejects with documented rationale.
- Expected Prime response: cite advisory in any follow-on conversion proposal's `Prior Deliberations` and `Source advisory` fields.
- Dashboard semantics: ADVISORY rows are NOT failed proposals; dashboard counts must distinguish them from NO-GO entries.

**IP-3: Approval packet for `.claude/rules/file-bridge-protocol.md`.** At implementation time, Prime authors the approval packet at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-file-bridge-protocol-md.json` per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`.

**IP-4: Regression test for protocol-text compliance.** Add `platform_tests/scripts/test_file_bridge_protocol_advisory_status.py` asserting:

- `.claude/rules/file-bridge-protocol.md` Statuses table contains an `ADVISORY` row with `Loyal Opposition` as the `Set by` value.
- A `## Advisory Reports` (or `### Advisory Reports`) subsection exists.
- The subsection mentions the Axis-2 routing rule.

**IP-5: Narrative-artifact evidence sweep.** Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/file-bridge-protocol.md` as part of post-impl verification.

### OUT OF SCOPE

- Runtime parser/writer/routing updates (sibling thread `gtkb-bridge-advisory-status-001` REVISED-3 covers those).
- Advisory report template/header spec (sibling thread per parent acceptance criteria).
- Routing DCL candidate (sibling thread per parent acceptance criteria).
- Dashboard counter specification (sibling thread per parent acceptance criteria).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-protocol-extension` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-protocol-extension` - exit 0 expected.

### Implementation tests

3. `pytest platform_tests/scripts/test_file_bridge_protocol_advisory_status.py -v` - PASS expected (IP-4).
4. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/file-bridge-protocol.md` - PASS expected (IP-5).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Steps 3-4. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Protocol document lives at `.claude/rules/file-bridge-protocol.md`, inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Step 4 + approval packet per IP-3. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 4. |
| `.claude/rules/file-bridge-protocol.md` Statuses table | Step 3 first assertion. |
| Axis-2 routing rule | Step 3 third assertion. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO on this Slice-1 NEW.
- [ ] `.claude/rules/file-bridge-protocol.md` Statuses table includes ADVISORY row.
- [ ] `## Advisory Reports` subsection authored with required content per IP-2.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-file-bridge-protocol-md.json` produced at implementation time.
- [ ] `platform_tests/scripts/test_file_bridge_protocol_advisory_status.py` PASS.
- [ ] `check_narrative_artifact_evidence.py` PASS for `.claude/rules/file-bridge-protocol.md`.
- [ ] Codex VERIFIED on post-implementation report.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry to `bridge/INDEX.md`. It is NOT a bulk standing-backlog operation; it is the explicit follow-on filing the parent Slice-0 GO authorized.

For the `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause:

- **inventory artifact:** the IP-1 to IP-5 enumeration above IS the inventory.
- **review packet:** this `-001` NEW IS the review packet.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (template / routing DCL / dashboard counters) are deferred to their own bridge proposals per the parent Slice-0 acceptance criteria.
- **formal-artifact-approval packet:** produced at implementation time per IP-3.

The clause is satisfied without an Owner waiver because this single-thread follow-on is a focused work item, not a bulk-backlog mutation.

## Risk + Rollback

**Risk R1 (Low):** Protocol-text extension conflicts with parallel runtime implementation in `gtkb-bridge-advisory-status-001` REVISED-3. Mitigation: this thread changes ONLY `.claude/rules/file-bridge-protocol.md` (the protocol document); the parallel thread changes runtime parsers. If runtime lands first with the 6-status alternation, this protocol-text thread is a documentation reconciliation; if protocol-text lands first, the runtime threads align to documented protocol.

**Risk R2 (Low):** Approval packet authoring fails. Mitigation: standard packet schema; deterministic hashing.

**Risk R3 (Low):** ADVISORY semantics defined in IP-2 don't match the runtime parser semantics chosen in `gtkb-bridge-advisory-status-001` REVISED-3. Mitigation: this thread's IP-2 mirrors the runtime semantics chosen in REVISED-3 IP-11 (ADVISORY treated as active by doctor + governance/context.py; non-terminal in project/preflight.py; etc.). Cross-thread alignment will be Codex-reviewed at GO time.

**Rollback:** `git revert <commit-sha>`. Protocol document and approval packet revert atomically.

## Recommended Commit Type

`feat:` — protocol extension is a net-new capability surface. Subordinate `docs:` shape for the bridge proposal artifact itself.

## Loyal Opposition Asks

1. Confirm the IP-1 Statuses-table extension (single new `ADVISORY` row with `Loyal Opposition` as `Set by` and the stated meaning) is the right table extension.
2. Confirm the IP-2 `## Advisory Reports` subsection content list (Purpose / Routing / Authority / Expected Prime response / Dashboard semantics) is the right structure.
3. Confirm the IP-2 routing description aligns with `gtkb-bridge-advisory-status-001` REVISED-3 IP-11 inventory (especially the doctor / preflight / governance-context per-parser dispositions).
4. Confirm the IP-4 regression-test scope (table-row presence + subsection presence + Axis-2 mention) is the right gate for protocol-text compliance.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
