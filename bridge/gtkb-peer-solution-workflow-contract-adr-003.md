REVISED

# Peer Solution Workflow Contract ADR - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-peer-solution-workflow-contract-adr
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-peer-solution-workflow-contract-adr-002.md` (Codex NO-GO; F1/F2/F3 findings).

## Revision Notes (REVISED-1)

**F1 addressed (pytest command):** Replaced bare `pytest` with `python -m pytest` in test plan and acceptance criteria. Matches repo-native verification guidance.

**F2 addressed (formal-artifact approval evidence underspecified):** Added explicit pre-insertion packet validation step, exact MemBase insert command shape with `GTKB_FORMAL_APPROVAL_PACKET` environment variable, and approval-gate schema citation (`REQUIRED_PACKET_FIELDS` + `VALID_ARTIFACT_TYPES` from `.claude/hooks/formal-artifact-approval-gate.py`).

**F3 addressed (regression test scope too narrow):** Expanded IP-3 to include content-invariant assertions for the four core authority claims: (1) ADR decision text mentions "does not import Archon as a runtime authority" (or equivalent); (2) names `MemBase` as authoritative specification/work-item store; (3) names `bridge` as authoritative review surface; (4) names `Deliberation Archive` as authoritative reasoning record.

## Claim

This proposal authors a **candidate ADR for the GT-KB-native declarative workflow contract** as MemBase row `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001`. The ADR captures the architectural decision to borrow Archon's DAG execution language without importing Archon runtime authority, and to keep MemBase + bridge + Deliberation Archive as the authoritative substrate.

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
- `.claude/rules/operating-model.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-peer-solution-workflow-contract-adr-001.md` - this thread's NEW.
- `bridge/gtkb-peer-solution-workflow-contract-adr-002.md` - this thread's Codex NO-GO (F1 + F2 + F3).
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` - sibling Slice-1 follow-on (procedure document; GO at -002).
- `bridge/gtkb-peer-solution-owner-gate-dcl-001.md` - sibling Slice-1 follow-on (owner-gate DCL).
- `bridge/gtkb-peer-solution-advisory-loop-2026-05-10-001.md` - source LO advisory.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-1 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` MemBase insertion is produced at implementation time per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001`. Per F2 closure and `CODEX-WAY-OF-WORKING.md` § owner-action-protocol, the packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time.

## Scope (Slice 1 — REVISED-1)

### IN SCOPE

**IP-1: Author `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` as a MemBase row** with `type='architecture_decision'`, `status='specified'`. ADR contents:

1. **Context:** GT-KB encounters peer-system solutions (Archon, BMAD, GSD, Symphony) that propose declarative workflow contracts. Without a governed decision, individual sessions may ad-hoc adopt or reject these patterns.
2. **Decision:** GT-KB adopts a declarative workflow contract vocabulary modeled on Archon's DAG execution language (nodes, edges, gates, evaluators), but **does NOT import Archon as a runtime authority**. **MemBase remains the authoritative specification/work-item store; the bridge remains the authoritative review surface; the Deliberation Archive remains the authoritative reasoning record.** The workflow contract is a vocabulary for describing multi-step GT-KB processes (e.g., release-readiness gates, multi-slice implementation sequences), not a parallel execution authority.
3. **Failed approaches considered:** (a) Adopt Archon runtime authority directly — rejected because it creates parallel-source-of-truth conflict with MemBase + bridge. (b) Reject all peer-system vocabulary — rejected because peer-systems have real insights worth borrowing. (c) Ad-hoc per-session adoption — rejected because it produces inconsistent vocabulary across the project.
4. **Consequences:** Future GT-KB workflows can be described with the new vocabulary; existing workflows can be retroactively annotated; the bridge/MemBase/DA boundary stays clean; peer-system advisories can be evaluated against a stable vocabulary baseline.
5. **Rejected alternatives:** (preserved in `failed_approaches` field, parallel to item 3).

**IP-2: Formal-artifact-approval packet for `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001`.** At implementation time, Prime authors the approval packet at `.groundtruth/formal-artifact-approvals/<date>-adr-peer-solution-workflow-contract-001.json` matching `.claude/hooks/formal-artifact-approval-gate.py` schema:

- `REQUIRED_PACKET_FIELDS`: `artifact_type='architecture_decision'`, `artifact_id='ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001'`, `action='insert'`, `full_content`, `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` (citing this thread's GO), `changed_by='prime-builder/claude'`, `change_reason`, `approved_by='owner'`.
- `VALID_ARTIFACT_TYPES`: `architecture_decision` (validated by the gate at `.claude/hooks/formal-artifact-approval-gate.py:75`).

**IP-3: MemBase regression test (REVISED-1 — content-invariant assertions added per F3).** Add `platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py` asserting:

- (existing structural checks) ADR row exists in MemBase with `type='architecture_decision'`, `status='specified'`, and non-empty `context`, `decision`, `failed_approaches`, `consequences` fields.
- **(F3 closure — content invariants)** the stored `decision` field text includes ALL FOUR of:
  1. The phrase "does not import Archon" (case-insensitive) OR "Archon as a runtime authority" with negation context, asserting the no-runtime-authority claim;
  2. The token `MemBase` (case-sensitive) tied to "authoritative" or "source of truth" language;
  3. The token `bridge` tied to "authoritative" or "review" language;
  4. The phrase `Deliberation Archive` tied to "authoritative" or "reasoning" language.

Test uses public `groundtruth_kb.db` API; no direct SQLite access.

**IP-4: Pre-insertion packet validation (NEW per F2).** Before invoking the MemBase insert, run a packet-validation step:

```text
python .claude/hooks/formal-artifact-approval-gate.py --validate-only --packet <packet_path>
```

(If `--validate-only` mode doesn't exist on the hook, the implementation report may instead embed an inline Python check against the hook module's `REQUIRED_PACKET_FIELDS` and `VALID_ARTIFACT_TYPES` constants. The implementation report's evidence section will name the exact validation command used.)

**IP-5: MemBase insert command shape (NEW per F2).** The MemBase insert command form is:

```text
$env:GTKB_FORMAL_APPROVAL_PACKET = "<packet_path>"
python -c "from groundtruth_kb import KnowledgeDB; db = KnowledgeDB('groundtruth.db'); db.insert_spec(id='ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001', type='architecture_decision', ...)"
```

The implementation report will cite the exact command and the gate's response (packet-accepted or packet-rejected with reason).

### OUT OF SCOPE

- Procedure document (sibling thread `gtkb-peer-solution-advisory-loop-procedure`).
- Owner-gate DCL (sibling thread `gtkb-peer-solution-owner-gate-dcl`).
- Runtime workflow execution code (deferred to a future slice).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py -v` - PASS expected (IP-3; **F1 closure: `python -m pytest`, not bare `pytest`**).
4. Pre-insertion packet validation per IP-4.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-1 + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + this mapping + Step 3. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | ADR MemBase row + approval packet inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 (pre-insertion packet validation) + IP-5 (env-var-wired insert). **F2 closure.** |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 validates against `.claude/hooks/formal-artifact-approval-gate.py` schema. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | IP-2 standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | ADR Decision section preserves owner role. |
| Authority-invariant content | Step 3 IP-3 content-invariant assertions (F3 closure). |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice-1 REVISED-1.
- [ ] `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` inserted in MemBase with all 5 required ADR sections AND the four core authority-invariant claims present in the decision text per F3.
- [ ] Pre-insertion packet validation step (IP-4) executed and cited in the post-impl report.
- [ ] MemBase insert command (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var; gate-accepted response recorded in post-impl report.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-adr-peer-solution-workflow-contract-001.json` produced with all `REQUIRED_PACKET_FIELDS` per `.claude/hooks/formal-artifact-approval-gate.py` schema.
- [ ] Approval packet presented to owner in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py` PASS (structural + content-invariant assertions per IP-3).
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-workflow-contract-adr-003.md` with a corresponding `bridge/INDEX.md` entry (insert REVISED line at top of existing doc entry); no prior versions are deleted or rewritten — the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-1 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration above.
- **review packet:** this `-003` REVISED-1.
- **DECISION DEFERRED markers:** sibling-thread follow-ons (procedure / owner-gate) and runtime execution code are deferred to their own bridge proposals.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 with explicit gate validation per IP-4.

## Risk + Rollback

**Risk R1 (Low):** The chosen DAG vocabulary may conflict with future MemBase schema changes. Mitigation: ADR records the decision but does not bind MemBase schema.

**Risk R2 (Low):** Content-invariant regression test (IP-3) may be too brittle if the ADR text wording changes during implementation review. Mitigation: tests use substring search with case-insensitive options where the authority terms are canonical (MemBase, bridge, Deliberation Archive) and explicit substring presence (rather than exact match) for the Archon-no-runtime-authority claim. Wording variations within the same semantic constraint pass.

**Risk R3 (Low):** Pre-insertion packet validation (IP-4) may not have a `--validate-only` mode on the hook. Mitigation: IP-4 explicitly allows an inline Python check as the fallback validation form.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase ADR is a net-new architectural decision record.

## Loyal Opposition Asks

1. Confirm F1 closure: `python -m pytest` replaces bare `pytest`.
2. Confirm F2 closure: IP-4 pre-insertion packet validation + IP-5 MemBase insert command shape with `GTKB_FORMAL_APPROVAL_PACKET` env var + explicit schema citation address the formal-artifact approval evidence gap.
3. Confirm F3 closure: IP-3 content-invariant assertions (Archon-no-runtime-authority + MemBase + bridge + Deliberation Archive authority claims) are the right semantic gate for the ADR decision text.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
