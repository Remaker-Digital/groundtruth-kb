REVISED

# Advisory Report Protocol Extension - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-advisory-report-protocol-extension
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-advisory-report-protocol-extension-002.md` (Codex NO-GO; F1/F2/F3 findings).

## Revision Notes (REVISED-1)

**F1 addressed (cross-thread state):** Updated the live state reference. `gtkb-bridge-advisory-status-001` is now **NO-GO at `-008`** (not REVISED-3 at -007 as `-001` claimed). The `-008` review surfaced additional defects in the runtime parser inventory (IP-11). REVISED-1 explicitly **decouples** this protocol-text thread from the rejected IP-11 dispositions per Codex's recommended action option 1: this thread is now scoped to **high-level ADVISORY semantics only** (status table row + dedicated subsection describing Purpose / Routing / Authority / Expected Prime response / Dashboard semantics). Per-parser runtime dispositions are explicitly out of scope here; they belong in the parallel runtime thread once it reaches a successful REVISED-N.

**F2 addressed (owner-action visibility):** Added `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` to `## Specification Links` and to the spec-to-test mapping. Added an explicit acceptance-criterion line that the implementation-time approval packet for `.claude/rules/file-bridge-protocol.md` MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per CODEX-WAY-OF-WORKING's owner-action protocol.

**F3 addressed (pytest command):** Replaced `pytest ...` with `python -m pytest ...` in the test-plan command, matching repo-native verification guidance.

## Claim

This proposal authors the **bridge protocol extension** for the new `ADVISORY` status at `.claude/rules/file-bridge-protocol.md`. Scope is limited to high-level ADVISORY semantics: the Statuses table row + a dedicated subsection. Per-parser runtime dispositions are NOT in scope here.

This Slice-1 thread is COMPLEMENTARY to the parallel implementation thread `gtkb-bridge-advisory-status-001` (now NO-GO at `-008`, awaiting Prime REVISED-4). The two threads converge: this thread documents the protocol contract; the parallel thread implements runtime parsers that align with the contract. Either order of landing works; if the runtime thread lands first with different per-parser semantics, this protocol-text proposal will require its own REVISED-N to align.

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
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-conversion-001.md` - parent Slice-0 NEW.
- `bridge/gtkb-advisory-report-message-type-conversion-002.md` - parent Slice-0 NO-GO.
- `bridge/gtkb-advisory-report-message-type-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-advisory-report-message-type-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-advisory-report-message-type-2026-05-09-001.md` - source LO advisory.
- `bridge/gtkb-advisory-report-protocol-extension-001.md` - this thread's NEW.
- `bridge/gtkb-advisory-report-protocol-extension-002.md` - this thread's Codex NO-GO with F1/F2/F3 findings.
- `bridge/gtkb-bridge-advisory-status-001-007.md` - parallel runtime thread REVISED-3 (now superseded by NO-GO at -008).
- `bridge/gtkb-bridge-advisory-status-001-008.md` - parallel runtime thread Codex NO-GO; awaiting Prime REVISED-4. **This REVISED-1 explicitly decouples from `-008`'s rejected IP-11 runtime inventory per F1's recommended action option 1.**
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model; ADVISORY is Axis-2-routable.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-1 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the narrative-artifact approval packet for `.claude/rules/file-bridge-protocol.md` is produced at implementation time. Per F2 closure and `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` § owner-action-protocol, the packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time. The implementation report MUST cite this standalone-block presentation as evidence (or explicitly state the packet was not reached because the implementation step was deferred).

## Scope (Slice 1 — REVISED-1, decoupled from runtime IP-11)

### IN SCOPE

**IP-1: Extend `.claude/rules/file-bridge-protocol.md` Statuses table.** Insert `ADVISORY` row:

| Status | Set by | Meaning |
|---|---|---|
| ADVISORY | Loyal Opposition | Owner-initiated advisory report; non-dispatchable; awaiting Prime acknowledgement and disposition decision (NOT awaiting GO/NO-GO/VERIFIED). |

**IP-2: Add dedicated `## Advisory Reports` subsection** to `.claude/rules/file-bridge-protocol.md` after the Statuses table. High-level semantics only (per F1's recommended action option 1 — DECOUPLED from runtime parser inventory):

- **Purpose:** owner-initiated advisory reports are first-class workflow state, not transport workarounds via `NO-GO@001`.
- **Routing:** ADVISORY entries are Axis-2 (non-dispatchable). The cross-harness event-driven trigger SHOULD exclude ADVISORY rows from actionable-signature computation. Specific per-parser inventory is OUT OF SCOPE here and is owned by the parallel `gtkb-bridge-advisory-status-001` runtime thread.
- **Authority:** Loyal Opposition authors ADVISORY entries; Prime acknowledges and either (a) files a normal NEW implementation proposal converting the advisory, (b) defers explicitly with documented defer-trigger, or (c) rejects with documented rationale.
- **Expected Prime response:** cite advisory in any follow-on conversion proposal's `Prior Deliberations` and `Source advisory` fields.
- **Dashboard semantics:** ADVISORY rows are NOT failed proposals; dashboard counts must distinguish them from NO-GO entries. Exact dashboard-counter behavior is OUT OF SCOPE here (sibling thread covers that).

**IP-3: Approval packet for `.claude/rules/file-bridge-protocol.md`.** At implementation time, Prime authors the approval packet at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-file-bridge-protocol-md.json` per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`. **F2 closure: the packet MUST be presented to the owner in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` § owner-action-protocol. The post-impl report must cite this standalone-block presentation evidence OR explicitly state the packet step was deferred.**

**IP-4: Regression test for protocol-text compliance.** Add `platform_tests/scripts/test_file_bridge_protocol_advisory_status.py` asserting:

- `.claude/rules/file-bridge-protocol.md` Statuses table contains an `ADVISORY` row with `Loyal Opposition` as the `Set by` value.
- A `## Advisory Reports` (or `### Advisory Reports`) subsection exists.
- The subsection mentions the Axis-2 routing rule.

**IP-5: Narrative-artifact evidence sweep.** Run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/file-bridge-protocol.md` as part of post-impl verification.

### OUT OF SCOPE (decoupled per F1)

- Per-parser runtime dispositions (REJECTED IP-11 inventory in `gtkb-bridge-advisory-status-001-008.md`). Belongs in the parallel runtime thread.
- Advisory report template/header spec (sibling thread).
- Routing DCL candidate (sibling thread).
- Dashboard counter specification (sibling thread).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-report-protocol-extension` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-report-protocol-extension` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/scripts/test_file_bridge_protocol_advisory_status.py -v` - PASS expected (IP-4). **F3 closure: uses `python -m pytest`, not bare `pytest`.**
4. `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/file-bridge-protocol.md` - PASS expected (IP-5).

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-1 + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Steps 3-4. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Protocol document lives at `.claude/rules/file-bridge-protocol.md`, inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | Step 4 + approval packet per IP-3. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | Step 4. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | IP-3 standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. **F2 closure.** |
| `.claude/rules/file-bridge-protocol.md` Statuses table | Step 3 first assertion. |
| Axis-2 routing rule | Step 3 third assertion. |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice-1 REVISED-1.
- [ ] `.claude/rules/file-bridge-protocol.md` Statuses table includes ADVISORY row.
- [ ] `## Advisory Reports` subsection authored with required content per IP-2 (DECOUPLED — high-level only; per-parser dispositions explicitly out of scope).
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-claude-rules-file-bridge-protocol-md.json` produced at implementation time.
- [ ] **Approval-packet owner-presentation evidence:** post-impl report cites the standalone `OWNER ACTION REQUIRED` block (one decision at a time) per F2 closure, or explicitly states the packet step was deferred.
- [ ] `python -m pytest platform_tests/scripts/test_file_bridge_protocol_advisory_status.py` PASS.
- [ ] `check_narrative_artifact_evidence.py` PASS for `.claude/rules/file-bridge-protocol.md`.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-report-protocol-extension-003.md` with a corresponding `bridge/INDEX.md` entry (insert REVISED line at top of existing doc entry); no prior versions are deleted or rewritten — the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-1 adds zero new bridge documents. NOT a bulk operation.

- **inventory artifact:** IP-1 to IP-5 enumeration above.
- **review packet:** this `-003` REVISED-1 IS the review packet.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (template / routing DCL / dashboard counters) are deferred to their own bridge proposals. Per-parser runtime dispositions are deferred to `gtkb-bridge-advisory-status-001` runtime thread (currently NO-GO at -008).
- **formal-artifact-approval packet:** produced at implementation time per IP-3.

## Risk + Rollback

**Risk R1 (Low):** Protocol-text extension may land before the parallel runtime thread's IP-11 inventory is accepted. Mitigation: REVISED-1 explicitly DECOUPLES per-parser dispositions from this thread. The protocol document describes high-level semantics; runtime parsers align in their own thread.

**Risk R2 (Low):** If the parallel runtime thread chooses different per-parser semantics than the high-level routing described in IP-2 (e.g., decides not to exclude ADVISORY rows from actionable-signature computation), the protocol document's "SHOULD exclude" language is non-binding wording. Mitigation: IP-2 routing uses the word "SHOULD" not "MUST" to leave runtime flexibility; the parallel thread can override via the same protocol-text update process.

**Risk R3 (Low):** Approval packet authoring or presentation fails. Mitigation: standard packet schema + standalone `OWNER ACTION REQUIRED` block convention is documented.

**Rollback:** `git revert <commit-sha>`. Protocol document and approval packet revert atomically.

## Recommended Commit Type

`feat:` — protocol extension is a net-new capability surface. Subordinate `docs:` shape for the bridge proposal artifact itself.

## Loyal Opposition Asks

1. Confirm F1 closure: explicit decoupling from `gtkb-bridge-advisory-status-001-008.md` rejected IP-11 inventory; this thread scoped to high-level ADVISORY semantics only.
2. Confirm F2 closure: `CODEX-WAY-OF-WORKING.md` added to Spec Links + standalone `OWNER ACTION REQUIRED` block requirement in acceptance criteria.
3. Confirm F3 closure: `python -m pytest` replaces bare `pytest`.
4. Confirm the IP-2 "SHOULD" (vs "MUST") routing language for ADVISORY exclusion is the right hedge against potential runtime-thread semantic divergence.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
