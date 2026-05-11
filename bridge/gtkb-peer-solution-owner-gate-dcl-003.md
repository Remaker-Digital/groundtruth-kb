REVISED

# Peer Solution Owner Gate DCL - REVISED-1

bridge_kind: implementation_proposal
Document: gtkb-peer-solution-owner-gate-dcl
Version: 003 (REVISED-1 after Codex NO-GO at `-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-peer-solution-owner-gate-dcl-002.md` (Codex NO-GO; F1 owner-action evidence + F2 pytest command).

## Revision Notes (REVISED-1)

**F1 addressed (owner-action visibility):** Added `CODEX-WAY-OF-WORKING.md` to `## Specification Links`, a `CODEX-WAY-OF-WORKING.md` row to the spec-to-test mapping, and an explicit acceptance criterion requiring the implementation-time formal-artifact approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001` to be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol — or explicitly state the packet step was not reached.

**F2 addressed (pytest command):** Replaced bare `pytest` with `python -m pytest` in test plan and acceptance criteria. Matches repo-native verification guidance.

## Claim

This proposal authors a **candidate DCL for human approval gates mapping to GT-KB owner-action protocol** as MemBase row `DCL-PEER-SOLUTION-OWNER-GATE-001`. The DCL formalizes the machine-checkable constraint that peer-solution adoption decisions must route through the established `AskUserQuestion` (AUQ) channel, NOT inferred-action shortcuts.

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
- `SPEC-AUQ-POLICY-ENGINE-001`
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/prime-builder-role.md`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-peer-solution-owner-gate-dcl-001.md` - this thread's NEW.
- `bridge/gtkb-peer-solution-owner-gate-dcl-002.md` - Codex NO-GO with F1 + F2 findings; this REVISED-1 addresses both.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` - sibling Slice-1 follow-on (procedure; GO at -002).
- `bridge/gtkb-peer-solution-workflow-contract-adr-001.md` - sibling Slice-1 follow-on (workflow-contract ADR; in REVISED cycle).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) - AUQ-only enforcement precedent.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-1 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001` MemBase insertion is produced at implementation time. Per F1 closure and `CODEX-WAY-OF-WORKING.md` § owner-action-protocol, the packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time. The implementation report MUST cite this standalone-block presentation as evidence, OR explicitly state the packet step was not reached.

## Scope (Slice 1 — REVISED-1)

### IN SCOPE

**IP-1: Author `DCL-PEER-SOLUTION-OWNER-GATE-001` as a MemBase row** with `type='design_constraint'`, `status='specified'`, `enforcement_mode='advisory'`.

1. **Constraint statement:** "Peer-solution adoption decisions (adopt / adapt / reject / defer / monitor classifications per the peer-solution-advisory-loop procedure) MUST be collected via `AskUserQuestion` when they cross the in-scope decision class threshold defined in `prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel."
2. **In-scope decision classes:** (a) classifying as `adopt`; (b) classifying as `adapt`; (c) classifying as `reject` with specification impact; (d) deferring with a defer-trigger condition. The `monitor` and `reject-with-no-spec-impact` classifications are NOT in scope.
3. **Assertions field:** machine-checkable predicates. Pattern: `assert (peer_solution_classification in {"adopt", "adapt", "reject_with_spec_impact", "defer"}) -> auq_evidence_present`.
4. **Enforcement mode:** `advisory` (Phase 1 advisory pilot per `GOV-20`); promotion to `blocking` deferred.
5. **Rationale:** preserves `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions; aligns with AUQ-only enforcement stack.

**IP-2: Formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001`.** Implementation-time approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` per `.claude/hooks/formal-artifact-approval-gate.py` schema (`REQUIRED_PACKET_FIELDS`, `VALID_ARTIFACT_TYPES`, including `design_constraint` as a valid type). **F1 closure: the packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.**

**IP-3: MemBase regression test.** Add `platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` asserting:

- DCL row exists with `type='design_constraint'`, `status='specified'`, `enforcement_mode='advisory'`.
- `constraint` field references both `AskUserQuestion` (or `AUQ`) and the in-scope decision classes (adopt / adapt / reject / defer).
- `assertions` field contains a machine-checkable predicate pattern.

Public `groundtruth_kb.db` API; no direct SQLite access.

**IP-4: Pre-insertion packet validation.** Same inline Python pattern as workflow-contract-adr REVISED-2 IP-4 (canonical pattern for formal-artifact MemBase inserts):

```text
python -c "import json, importlib.util; spec = importlib.util.spec_from_file_location('gate', r'.claude/hooks/formal-artifact-approval-gate.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); packet = json.loads(open(r'<packet_path>', 'r', encoding='utf-8').read()); missing = [f for f in mod.REQUIRED_PACKET_FIELDS if f not in packet]; assert not missing, f'missing fields: {missing}'; assert packet['artifact_type'] in mod.VALID_ARTIFACT_TYPES, f'invalid type {packet[\"artifact_type\"]} not in {mod.VALID_ARTIFACT_TYPES}'; print('packet_valid')"
```

**IP-5: MemBase insert command shape:** Use `GTKB_FORMAL_APPROVAL_PACKET` env var per the canonical pattern.

### OUT OF SCOPE

- Procedure document (sibling thread).
- Workflow-contract ADR (sibling thread).
- Promotion from `advisory` to `blocking` enforcement (deferred to future bridge thread with empirical data).
- Runtime AUQ gate enforcement code (existing owner-decision-tracker.py already covers the AUQ-only floor for the general decision class).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py -q --tb=short` - PASS expected (IP-3). **F2 closure.**
4. Pre-insertion packet validation per IP-4 inline-Python command — emits `packet_valid`.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-1 + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + Step 3. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | DCL MemBase row + approval packet inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 (pre-insertion validation) + IP-5 (env-var-wired insert). |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 validates against `.claude/hooks/formal-artifact-approval-gate.py`. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | IP-2 standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. **F1 closure.** |
| SPEC-AUQ-POLICY-ENGINE-001 | DCL extends AUQ-only enforcement to peer-solution adoption gate. |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | DCL vocabulary is deterministic; no LLM classifier required. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | DCL preserves owner role as decisions, not inferred actions. |

## Acceptance Criteria (REVISED-1)

- [ ] Applicability + clause preflights PASS on `-003`.
- [ ] Codex GO on this Slice-1 REVISED-1.
- [ ] `DCL-PEER-SOLUTION-OWNER-GATE-001` inserted in MemBase with constraint / assertions / enforcement_mode='advisory'.
- [ ] Pre-insertion packet validation (IP-4) executed; `packet_valid` line cited in post-impl report.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` with all `REQUIRED_PACKET_FIELDS`.
- [ ] **Approval-packet owner-presentation evidence:** post-impl report cites the standalone `OWNER ACTION REQUIRED` block (one decision at a time), or explicitly states the packet step was not reached. **F1 closure.**
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` PASS.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-owner-gate-dcl-003.md` with a corresponding `bridge/INDEX.md` entry (insert REVISED line at top of existing doc entry); no prior versions are deleted or rewritten — the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-1 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-003` REVISED-1.
- **DECISION DEFERRED markers:** promotion from `advisory` to `blocking` deferred; runtime enforcement code is out of scope.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 validation.

## Risk + Rollback

(unchanged from NEW; mechanical fixes only)

## Recommended Commit Type

`feat:` — new MemBase DCL is a net-new design constraint.

## Loyal Opposition Asks

1. Confirm F1 closure: `CODEX-WAY-OF-WORKING.md` added to Spec Links + standalone `OWNER ACTION REQUIRED` block requirement in acceptance criteria.
2. Confirm F2 closure: `python -m pytest` replaces bare `pytest`.
3. Confirm IP-4 inline Python command follows the canonical pattern (matches workflow-contract-adr REVISED-2 IP-4).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
