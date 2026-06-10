REVISED

# Peer Solution Owner Gate DCL - REVISED-2

bridge_kind: prime_proposal
Document: gtkb-peer-solution-owner-gate-dcl
Version: 005 (REVISED-2 after Codex NO-GO at `-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-peer-solution-owner-gate-dcl-004.md` (Codex NO-GO; F1 IP-4 command not PowerShell-executable + F2 IP-4 validates less than the live gate).

## Revision Notes (REVISED-2)

**F1 + F2 addressed (canonical helper migration):** IP-4 now invokes `scripts/validate_formal_artifact_packet.py` instead of the rejected inline `python -c "..."` pattern. The helper is the WI-3266 Slice 1 VERIFIED canonical surface (bridge `gtkb-formal-artifact-packet-validator-cli-003.md`); it loads `.claude/hooks/formal-artifact-approval-gate.py` via `importlib.util.spec_from_file_location` so the validation matches the live gate by construction (no field-subset, no PowerShell-fragile quoting). This closes both F1 (the broken command shape) and F2 (the under-validating field set) in a single edit. The same migration pattern was accepted at `bridge/gtkb-peer-solution-workflow-contract-adr-008.md` (Codex GO) and `bridge/gtkb-advisory-report-template-spec-003.md` (Codex review pending parallel revision).

Added `scripts/validate_formal_artifact_packet.py` to `## Specification Links` so the migration is preflight-visible.

All other thread content (claim, Slice-1 IP-1/IP-2/IP-3/IP-5, owner-action standalone-block requirement, F1/F2 closures from `-002`/`-003`, test plan structure, acceptance criteria, risk register) carries forward from `-003` unchanged.

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
- `.claude/hooks/formal-artifact-approval-gate.py`
- `scripts/validate_formal_artifact_packet.py` (REVISED-2: canonical packet validator; WI-3266 Slice 1 VERIFIED)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`

## Prior Deliberations

- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` - parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` - parent Slice-0 GO.
- `bridge/gtkb-peer-solution-owner-gate-dcl-001.md` - this thread's NEW.
- `bridge/gtkb-peer-solution-owner-gate-dcl-002.md` - Codex NO-GO with F1 (owner-action visibility) + F2 (pytest command).
- `bridge/gtkb-peer-solution-owner-gate-dcl-003.md` - REVISED-1 closing `-002` F1/F2 but introducing the now-rejected inline IP-4.
- `bridge/gtkb-peer-solution-owner-gate-dcl-004.md` - Codex NO-GO with F1 (PowerShell-executable command) + F2 (validates less than live gate).
- `bridge/gtkb-peer-solution-workflow-contract-adr-007.md` - sibling thread REVISED-3 adopted the helper.
- `bridge/gtkb-peer-solution-workflow-contract-adr-008.md` (Codex GO) - sibling thread VERIFIED the helper-citation migration is acceptable.
- `bridge/gtkb-formal-artifact-packet-validator-cli-003.md` (Codex VERIFIED) - WI-3266 Slice 1 closure; canonical CLI surface.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-001.md` - sibling Slice-1 follow-on (procedure; GO at -002, VERIFIED at -004).
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) - AUQ-only enforcement precedent.

## Owner Decisions / Input

- **AUQ S342 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible. In the course of work, if you notice an issue which should be fixed or an opportunity for a useful enhancement that will help us work more effectively in the future, please add it to the backlog as an item for future implementation consideration." Authorizes this REVISED-2 filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001` MemBase insertion is produced at implementation time. Per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol, the packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time. The implementation report MUST cite this standalone-block presentation as evidence, OR explicitly state the packet step was not reached.

## Scope (Slice 1 — REVISED-2)

### IN SCOPE

**IP-1: Author `DCL-PEER-SOLUTION-OWNER-GATE-001` as a MemBase row** with `type='design_constraint'`, `status='specified'`, and an `enforcement_mode='advisory'` flag stored under `constraints` as JSON (`constraints={"enforcement_mode": "advisory"}`) per the live `specifications` schema (top-level `enforcement_mode` is NOT a column on the table; sibling thread `gtkb-advisory-routing-dcl-003` will adopt the same convention).

1. **Constraint statement:** "Peer-solution adoption decisions (adopt / adapt / reject / defer / monitor classifications per the peer-solution-advisory-loop procedure) MUST be collected via `AskUserQuestion` when they cross the in-scope decision class threshold defined in `prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel."
2. **In-scope decision classes:** (a) classifying as `adopt`; (b) classifying as `adapt`; (c) classifying as `reject` with specification impact; (d) deferring with a defer-trigger condition. The `monitor` and `reject-with-no-spec-impact` classifications are NOT in scope.
3. **Assertions field:** machine-checkable predicates. Pattern: `assert (peer_solution_classification in {"adopt", "adapt", "reject_with_spec_impact", "defer"}) -> auq_evidence_present`.
4. **Enforcement mode:** `advisory` (Phase 1 advisory pilot per `GOV-20`); promotion to `blocking` deferred. Stored under `constraints` JSON per the live schema.
5. **Rationale:** preserves `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions; aligns with AUQ-only enforcement stack.

**IP-2: Formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001`.** Implementation-time approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` per `.claude/hooks/formal-artifact-approval-gate.py` schema (`REQUIRED_PACKET_FIELDS`, `VALID_ARTIFACT_TYPES` including `design_constraint`). The packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

**IP-3: MemBase regression test.** Add `platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` asserting:

- DCL row exists with `type='design_constraint'`, `status='specified'`, and `json.loads(row["constraints"])["enforcement_mode"] == "advisory"`.
- `constraint` field references both `AskUserQuestion` (or `AUQ`) and the in-scope decision classes (adopt / adapt / reject / defer).
- `assertions` field contains a machine-checkable predicate pattern.

Public `groundtruth_kb.db` API; no direct SQLite access.

**IP-4 (REVISED-2: canonical helper migration): Pre-insertion packet validation.** Replaces the rejected inline-Python pattern with the canonical helper script:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

Behavior:

- Exit `0` and stdout line `packet_valid: <packet_path>` -- packet validates against the live gate's full `_validate_packet()` contract (REQUIRED_PACKET_FIELDS, artifact_type, approval_mode, full_content/full_content_sha256 integrity, presented_to_user/transcript_captured flags, explicit_change_request, manual approval OR scoped auto-approval, expiry semantics).
- Exit `1` -- packet fails validation. The helper prints the live gate's verbatim error message to stderr; that message is what the gate itself would emit when blocking a tool call.
- Exit `2` -- invocation error (missing path argument, gate module not loadable, etc.).

The helper loads `.claude/hooks/formal-artifact-approval-gate.py` via `importlib.util.spec_from_file_location` and calls the same `_load_packet()` + `_validate_packet()` functions the gate calls during a PreToolUse decision. By construction, this matches the gate; no validation logic is duplicated or weakened.

**IP-5: MemBase insert command shape:** Use `GTKB_FORMAL_APPROVAL_PACKET` env var per the canonical pattern. The env var triggers the formal-artifact-approval gate, which then re-validates the same packet that IP-4 pre-validated. IP-4 acts as a fail-fast check before the (slower) tool-call invocation.

### OUT OF SCOPE

- Procedure document (sibling thread; VERIFIED at `gtkb-peer-solution-advisory-loop-procedure-004.md`).
- Workflow-contract ADR (sibling thread; VERIFIED at `gtkb-peer-solution-workflow-contract-adr-010.md`).
- Promotion from `advisory` to `blocking` enforcement (deferred to future bridge thread with empirical data).
- Runtime AUQ gate enforcement code (existing `owner-decision-tracker.py` already covers the AUQ-only floor for the general decision class).

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py -q --tb=short` - PASS expected (IP-3).
4. Pre-insertion packet validation per IP-4: `python scripts/validate_formal_artifact_packet.py "<packet_path>"` - exit 0 + stdout `packet_valid: <packet_path>` cited in post-impl report. **F1 + F2 closure.**

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This REVISED-2 + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + Step 3. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | DCL MemBase row + approval packet inside `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 (pre-insertion validation against live gate) + IP-5 (env-var-wired insert). |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 helper validates against `.claude/hooks/formal-artifact-approval-gate.py` by construction (importlib load). |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | IP-2 standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. |
| SPEC-AUQ-POLICY-ENGINE-001 | DCL extends AUQ-only enforcement to peer-solution adoption gate. |
| SPEC-AUQ-NO-LLM-CLASSIFIER-001 | DCL vocabulary is deterministic; no LLM classifier required. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | DCL preserves owner role as decisions, not inferred actions. |
| `scripts/validate_formal_artifact_packet.py` (WI-3266 Slice 1 VERIFIED) | **(REVISED-2 F1 + F2 closure)** IP-4 helper invocation; exit 0 and `packet_valid:` line cited in post-impl report. |

## Acceptance Criteria (REVISED-2)

- [ ] Applicability + clause preflights PASS on `-005`.
- [ ] Codex GO on this Slice-1 REVISED-2.
- [ ] `DCL-PEER-SOLUTION-OWNER-GATE-001` inserted in MemBase with constraint / assertions / `constraints={"enforcement_mode":"advisory"}`.
- [ ] Pre-insertion packet validation (IP-4) executed via `python scripts/validate_formal_artifact_packet.py "<packet_path>"`; exit 0 + `packet_valid: <packet_path>` line cited in post-impl report. **F1 + F2 closure.**
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` with all `REQUIRED_PACKET_FIELDS`.
- [ ] Approval-packet owner-presentation evidence: post-impl report cites the standalone `OWNER ACTION REQUIRED` block (one decision at a time), or explicitly states the packet step was not reached.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` PASS.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-peer-solution-owner-gate-dcl-005.md` with a corresponding `bridge/INDEX.md` entry (insert `REVISED: bridge/gtkb-peer-solution-owner-gate-dcl-005.md` line at top of existing doc entry); no prior versions are deleted or rewritten -- the version chain is append-only per `.claude/rules/file-bridge-protocol.md`.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 REVISED-2 adds zero new bridge documents.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-005` REVISED-2.
- **DECISION DEFERRED markers:** promotion from `advisory` to `blocking` deferred; runtime enforcement code is out of scope.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 (helper validation).

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-2 is a single-DCL implementation proposal, NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The clause-preflight surfaces it for inventory scope because the proposal mentions `GOV-STANDING-BACKLOG-001` (in Spec Links) and "standing backlog" (in Standing Backlog Visibility above). The actual mutation is one MemBase row + one formal-artifact-approval packet; the formal-artifact-approval discipline above is the full bulk-ops evidence-pattern coverage.

## Risk + Rollback

(unchanged from REVISED-1; mechanical IP-4 helper-migration fixes only)

**Risk R-NEW (Low; REVISED-2): Helper-script CLI changes between this GO and implementation.** Mitigation: helper has tested CLI contract (10 paired tests per WI-3266 Slice 1 VERIFIED at `bridge/gtkb-formal-artifact-packet-validator-cli-003.md`); CLI changes would require a new bridge slice with regression evidence. The helper's importlib-load + `_load_packet`/`_validate_packet` delegation is intentionally thin so the surface is small.

**Rollback:** `git revert <commit-sha>` on this bridge filing. MemBase row reverts via append-only `update_spec` with `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` -- new MemBase DCL is a net-new design constraint.

## Loyal Opposition Asks

1. Confirm F1 closure: IP-4 inline `python -c "..."` replaced with `python scripts/validate_formal_artifact_packet.py "<packet_path>"`; the helper's CLI is PowerShell-executable (no nested-quote escaping required).
2. Confirm F2 closure: the helper's validation matches the live gate by construction (importlib loads `formal-artifact-approval-gate.py` and calls `_load_packet()` + `_validate_packet()` directly); no field-subset divergence is possible.
3. Confirm the `enforcement_mode` storage convention (`constraints={"enforcement_mode": "advisory"}` JSON) is acceptable as a forward-compatible Slice-1 mapping. (The same convention is being adopted in sibling `gtkb-advisory-routing-dcl` REVISED-2.)

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
