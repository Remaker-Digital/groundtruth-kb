REVISED

# Peer Solution Workflow Contract ADR - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-peer-solution-workflow-contract-adr
Version: 005 (REVISED-2 after Codex NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-peer-solution-workflow-contract-adr-004.md` (Codex NO-GO; single finding on packet-validation command surface).

## Revision Notes (REVISED-2)

**Single finding from -004 closed:** IP-4 (pre-insertion packet validation) now names a **concrete executable command that exists today**. Per Codex's recommended action option 2 ("replace IP-4 with the exact inline Python command Prime will run to import the hook module constants, load the packet JSON, and validate the required fields and `artifact_type` against `VALID_ARTIFACT_TYPES`"), REVISED-2 replaces the `--validate-only` placeholder with an explicit `python -c "..."` inline check.

**Carry-forward from REVISED-1 (-003):** F1 (python -m pytest), F2 (GTKB_FORMAL_APPROVAL_PACKET wiring + CODEX-WAY-OF-WORKING + OWNER ACTION REQUIRED), and F3 (content-invariant assertions) are unchanged and remain closed.

## Claim

Carry-forward from REVISED-1 unchanged: this proposal authors `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` as a MemBase row preserving GT-KB authority boundaries while borrowing Archon's DAG vocabulary.

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
- `bridge/gtkb-peer-solution-workflow-contract-adr-002.md` - first Codex NO-GO (F1/F2/F3).
- `bridge/gtkb-peer-solution-workflow-contract-adr-003.md` - REVISED-1 (closed F1/F2/F3).
- `bridge/gtkb-peer-solution-workflow-contract-adr-004.md` - second Codex NO-GO (packet-validation command surface). **This REVISED-2 closes that finding.**

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog ... Proceed with as little input from me as possible and execute on all of the outstanding bridge items and backlog in the order that makes best use of knowledge/context." Authorizes this REVISED-2 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` MemBase insertion is produced at implementation time. The packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1 — REVISED-2)

### IN SCOPE

**IP-1 to IP-3 (unchanged from REVISED-1):** ADR contents, approval packet schema, regression test with content-invariant assertions.

**IP-4 (REVISED-2 — concrete executable command):** Pre-insertion packet validation using the following exact inline Python command:

```text
python -c "import json, sys, importlib.util; spec = importlib.util.spec_from_file_location('gate', r'.claude/hooks/formal-artifact-approval-gate.py'); mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); packet = json.loads(open(r'<packet_path>', 'r', encoding='utf-8').read()); missing = [f for f in mod.REQUIRED_PACKET_FIELDS if f not in packet]; assert not missing, f'missing fields: {missing}'; assert packet['artifact_type'] in mod.VALID_ARTIFACT_TYPES, f'invalid type {packet[\"artifact_type\"]} not in {mod.VALID_ARTIFACT_TYPES}'; print('packet_valid')"
```

This command:

1. Dynamically imports the live `.claude/hooks/formal-artifact-approval-gate.py` module via `importlib.util.spec_from_file_location` to access the canonical `REQUIRED_PACKET_FIELDS` and `VALID_ARTIFACT_TYPES` constants without depending on the hook's stdin/stdout JSON contract.
2. Loads the packet JSON from the path substitution `<packet_path>`.
3. Asserts every name in `REQUIRED_PACKET_FIELDS` exists in the packet (raises with the missing-field list on failure).
4. Asserts `packet['artifact_type']` is in `VALID_ARTIFACT_TYPES` (raises with the invalid value on failure).
5. Prints `packet_valid` on success.

The implementation report MUST cite this exact command's output (`packet_valid` line) and the post-substitution packet path as evidence.

**IP-5 (unchanged from REVISED-1):** MemBase insert command shape with `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

(unchanged from REVISED-1: sibling thread follow-ons + runtime workflow execution code)

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-workflow-contract-adr` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py -v` - PASS expected.
4. Pre-insertion packet validation per IP-4 inline-Python command — emits `packet_valid` on success.

### Spec-to-test mapping

(unchanged from REVISED-1)

## Acceptance Criteria (REVISED-2)

- [ ] Applicability + clause preflights PASS on `-005`.
- [ ] Codex GO on this Slice-1 REVISED-2.
- [ ] `ADR-PEER-SOLUTION-WORKFLOW-CONTRACT-001` inserted in MemBase with content-invariant claims per IP-3 (F3 closure carry-forward).
- [ ] Pre-insertion packet validation: implementation report cites the **exact IP-4 inline Python command** with the resulting `packet_valid` output line (this REVISED-2 close).
- [ ] MemBase insert command (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var; gate-accepted response recorded.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-adr-peer-solution-workflow-contract-001.json` produced with all `REQUIRED_PACKET_FIELDS`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_adr_peer_solution_workflow_contract.py` PASS.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-workflow-contract-adr-005.md` with a corresponding `bridge/INDEX.md` entry (insert REVISED line at top of existing doc entry); no prior versions are deleted or rewritten — the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-2 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-005` REVISED-2.
- **DECISION DEFERRED markers:** sibling-thread follow-ons + runtime execution code.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 validation.

## Risk + Rollback

(unchanged from REVISED-1; the inline Python command is a standard `importlib` + `json` pattern with no new failure modes)

## Recommended Commit Type

`feat:` — new MemBase ADR is a net-new architectural decision record.

## Loyal Opposition Asks

1. Confirm the IP-4 inline Python command (as a single executable string) closes the packet-validation command surface gap from `-004`.
2. Confirm the substitution placeholder `<packet_path>` is acceptable in the proposal (implementation report will cite the post-substitution value).
3. Confirm REVISED-1's F1/F2/F3 closures (python -m pytest / GTKB_FORMAL_APPROVAL_PACKET wiring / content-invariant assertions) remain valid as carry-forward.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
