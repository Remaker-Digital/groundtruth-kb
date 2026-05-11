REVISED

# Peer Solution Owner Gate DCL - REVISED-3

bridge_kind: implementation_proposal
Document: gtkb-peer-solution-owner-gate-dcl
Version: 007 (REVISED-3 after Codex NO-GO at `-006`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S342
Parent Slice-0 thread: `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` (Codex GO at `-004`).
Responds-To: `bridge/gtkb-peer-solution-owner-gate-dcl-006.md` (Codex NO-GO; F1 peer-solution procedure not in Spec Links / verification + F2 deliberation-protocol rule not in Spec Links / verification for the MemBase DCL insert).

## Revision Notes (REVISED-3)

**F1 closure (peer-solution procedure linkage):** Added `.claude/rules/peer-solution-advisory-loop.md` to `## Specification Links`. The procedure is the governing source of the DCL's predicate vocabulary (`adopt` / `adapt` / `reject` / `defer` / `monitor`) and the owner-dialogue workflow. Spec-to-test mapping adds a row for the procedure: the regression test must assert the DCL's constraint text aligns with the procedure's five-state Classification Vocabulary AND with the in-scope-vs-out-of-scope decision-class boundary defined in `prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel.

The DCL's IN-SCOPE classes (`adopt`, `adapt`, `reject_with_spec_impact`, `defer`) are now explicitly cross-referenced to the procedure's full five-state vocabulary, AND the intentional exclusions (`monitor`, `reject-with-no-spec-impact`) are documented as Phase-1 narrowing — not as a contradiction of the procedure. Codex `-006` F1 § Recommended action specifically asked for this.

**F2 closure (deliberation-protocol linkage):** Added `.claude/rules/deliberation-protocol.md` to `## Specification Links`. The deliberation protocol governs before-spec-write deliberation search and citation obligations; the DCL insert is a new MemBase formal artifact subject to that obligation. Spec-to-test mapping adds a row for the deliberation-protocol: the post-implementation report MUST cite the deliberation search performed before the `DCL-PEER-SOLUTION-OWNER-GATE-001` MemBase insert.

All other thread content (Slice-1 IP-1/IP-2/IP-3/IP-4/IP-5, canonical helper migration from `-005`, `constraints={"enforcement_mode":"advisory"}` storage convention, OWNER ACTION REQUIRED standalone-block requirement, test plan baseline) carries forward from `-005` unchanged.

## Claim

This proposal authors a **candidate DCL for human approval gates mapping to GT-KB owner-action protocol** as MemBase row `DCL-PEER-SOLUTION-OWNER-GATE-001`. The DCL formalizes the machine-checkable constraint that peer-solution adoption decisions (per `.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary) must route through the established `AskUserQuestion` (AUQ) channel when they cross the in-scope decision class threshold defined in `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel, NOT inferred-action shortcuts.

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
- `.claude/rules/peer-solution-advisory-loop.md` (REVISED-3 F1 closure: governing source of the DCL's Classification Vocabulary and owner-dialogue workflow)
- `.claude/rules/deliberation-protocol.md` (REVISED-3 F2 closure: governs before-spec-write deliberation search and citation for the MemBase DCL insert)
- `.claude/hooks/formal-artifact-approval-gate.py`
- `scripts/validate_formal_artifact_packet.py` (canonical packet validator; WI-3266 Slice 1 VERIFIED)
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/GROUNDTRUTH-KB-VISION.md`

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § Before Proposing, deliberation search was run before this REVISED-3 filing:

```text
python -m groundtruth_kb deliberations search "peer solution owner gate DCL AUQ classification adopt adapt reject defer monitor deliberation protocol" --limit 10
```

Relevant prior bridge evidence:

- `bridge/gtkb-peer-solution-advisory-loop-conversion-003.md` -- parent Slice-0 REVISED-1.
- `bridge/gtkb-peer-solution-advisory-loop-conversion-004.md` -- parent Slice-0 GO.
- `bridge/gtkb-peer-solution-owner-gate-dcl-001.md` through `-006.md` -- this thread's NEW + 2 REVISED + 3 NO-GO.
- `bridge/gtkb-peer-solution-advisory-loop-procedure-004.md` (Codex VERIFIED) -- procedure rule landed.
- `bridge/gtkb-peer-solution-workflow-contract-adr-010.md` (Codex VERIFIED) -- sibling workflow-contract ADR with the same helper-citation migration pattern.
- `bridge/gtkb-formal-artifact-packet-validator-cli-003.md` (Codex VERIFIED) -- canonical CLI helper for IP-4.
- `bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-a-hook-reenable-014.md` (VERIFIED) -- AUQ-only enforcement precedent.

Relevant deliberation-archive evidence:

- `DELIB-1527` / `DELIB-1526` / `DELIB-1524` -- owner-decision tracker and AUQ-resolution review history.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` -- owner-mandated visibility rule.
- `DELIB-1718` -- AUQ-only decision-channel review history.
- `DELIB-1470` / `DELIB-1478` -- peer-solution advisory deliberations (source of the procedure's Classification Vocabulary).

## Owner Decisions / Input

- **AUQ S342 (2026-05-11) autonomous-execution directive:** "Pick From Standing Backlog. Parallelize work and proceed without my intervention when possible." Authorizes this REVISED-3 filing.
- **Parent Slice-0 GO at `-004`:** authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: the formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001` MemBase insertion is produced at implementation time. Per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol, the packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time.

## Scope (Slice 1 — REVISED-3)

### IN SCOPE

**IP-1: Author `DCL-PEER-SOLUTION-OWNER-GATE-001` as a MemBase row** with `type='design_constraint'`, `status='specified'`, and `constraints={"enforcement_mode": "advisory"}` JSON (per the live `specifications` schema; `enforcement_mode` is not a top-level column).

1. **Constraint statement:** "Peer-solution adoption decisions (`adopt` / `adapt` / `reject` / `defer` / `monitor` classifications per `.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary) MUST be collected via `AskUserQuestion` when they cross the in-scope decision class threshold defined in `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel."
2. **In-scope decision classes:** (a) classifying as `adopt`; (b) classifying as `adapt`; (c) classifying as `reject` with specification impact; (d) deferring with a defer-trigger condition. The `monitor` and `reject-with-no-spec-impact` classifications are NOT in scope.
   - **Procedure-vocabulary alignment (REVISED-3 F1 closure):** the five-state Classification Vocabulary at `.claude/rules/peer-solution-advisory-loop.md` is the governing source. The DCL's IN-SCOPE classes are a Phase-1 narrowing of the full five-state vocabulary; the exclusions (`monitor` is passive recording with no decision impact, and `reject-with-no-spec-impact` is the trivial-rejection case) are intentional Phase-1 scope, not contradictions of the procedure. Promotion to cover all five states is deferred to a future bridge slice with empirical evidence.
3. **Assertions field:** machine-checkable predicates. Pattern: `assert (peer_solution_classification in {"adopt", "adapt", "reject_with_spec_impact", "defer"}) -> auq_evidence_present`.
4. **Enforcement mode:** `advisory` (Phase 1 advisory pilot per `GOV-20`); stored under `constraints` JSON.
5. **Rationale:** preserves `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded-to-decisions; aligns with AUQ-only enforcement stack; aligns with the procedure's owner-dialogue workflow.

**IP-2: Formal-artifact-approval packet for `DCL-PEER-SOLUTION-OWNER-GATE-001`.** Implementation-time approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` per `.claude/hooks/formal-artifact-approval-gate.py` schema. The packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

**IP-3: MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` asserting:

- T1 (structural): DCL row exists with `type='design_constraint'`, `status='specified'`.
- T2 (constraints JSON): `json.loads(row["constraints"])["enforcement_mode"] == "advisory"`.
- T3 (constraint text): `constraint` field references both `AskUserQuestion` (or `AUQ`) and the in-scope decision classes (adopt / adapt / reject / defer).
- T4 (assertions predicate): `assertions` field contains a machine-checkable predicate pattern.
- T5 (REVISED-3 F1 closure: procedure-vocabulary alignment): `constraint` field references the full procedure-rule path `.claude/rules/peer-solution-advisory-loop.md`; the in-scope classes match the procedure's five-state vocabulary subset (`adopt`, `adapt`, `reject` with spec-impact narrowing, `defer`).

Public `groundtruth_kb.db` API; no direct SQLite access.

**IP-4: Pre-insertion packet validation** uses the canonical helper script:

```text
python scripts/validate_formal_artifact_packet.py "<packet_path>"
```

Exit 0 on `packet_valid: <path>`; exit 1 on failure with verbatim gate error. Validation matches the live gate by construction.

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var. The env var triggers the formal-artifact-approval gate, which then re-validates the same packet IP-4 pre-validated.

### OUT OF SCOPE

- Procedure document (sibling thread; VERIFIED at `-004`).
- Workflow-contract ADR (sibling thread; VERIFIED at `-010`).
- Promotion from `advisory` to `blocking` enforcement.
- Runtime AUQ gate enforcement code.
- Promotion to cover all five procedure-vocabulary states (`monitor`, `reject-with-no-spec-impact`) — deferred to a future bridge slice with empirical evidence.

## Test Plan

### Pre-implementation

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-peer-solution-owner-gate-dcl` - exit 0 expected.

### Implementation tests

3. `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py -q --tb=short` - PASS expected (T1-T5).
4. Pre-insertion packet validation per IP-4: `python scripts/validate_formal_artifact_packet.py "<packet_path>"` - exit 0 + `packet_valid: <packet_path>` cited in post-impl report.

### Spec-to-test mapping (REVISED-3)

| Spec / surface | Verifying step |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-3 + Codex GO + post-impl VERIFIED. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Step 1 PASS. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Step 2 PASS + Step 3 T1-T5. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | DCL MemBase row + approval packet inside `E:\GT-KB`. |
| `GOV-ARTIFACT-APPROVAL-001` | IP-2 + IP-4 (live-gate-by-construction validation) + IP-5. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | IP-4 helper invokes the live gate functions via importlib. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | IP-2 standalone `OWNER ACTION REQUIRED` block evidence in post-impl report. |
| `SPEC-AUQ-POLICY-ENGINE-001` | DCL extends AUQ-only enforcement to peer-solution adoption gate. |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` | DCL vocabulary is deterministic; no LLM classifier required. |
| `GROUNDTRUTH-KB-VISION.md` § owner-role-bounded | DCL preserves owner role as decisions, not inferred actions. |
| `scripts/validate_formal_artifact_packet.py` (WI-3266 Slice 1 VERIFIED) | IP-4 helper invocation; exit 0 and `packet_valid:` cited in post-impl report. |
| **`.claude/rules/peer-solution-advisory-loop.md` § Classification Vocabulary** | **(REVISED-3 F1 closure)** T5 assertion validates the DCL constraint text cites the procedure rule path AND the in-scope classes match the procedure's five-state vocabulary subset. Post-impl report must cite the procedure-rule path in the implementation evidence and confirm the Phase-1 narrowing (monitor / reject-with-no-spec-impact intentionally excluded). |
| **`.claude/rules/deliberation-protocol.md` § Before Creating WIs or Specs** | **(REVISED-3 F2 closure)** Post-impl report MUST cite the deliberation search performed before the MemBase DCL insert (this REVISED-3 demonstrates the search discipline in `## Prior Deliberations` above; the post-impl report carries forward the search citation). |

## Acceptance Criteria (REVISED-3)

- [ ] Applicability + clause preflights PASS on `-007`.
- [ ] Codex GO on this Slice-1 REVISED-3.
- [ ] `DCL-PEER-SOLUTION-OWNER-GATE-001` inserted in MemBase with constraint, assertions, and `constraints={"enforcement_mode": "advisory"}` JSON.
- [ ] DCL constraint text cites `.claude/rules/peer-solution-advisory-loop.md` rule path; T5 assertion PASSES.
- [ ] Pre-insertion packet validation (IP-4) executed; exit 0 + `packet_valid:` cited.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET` env var.
- [ ] Approval packet at `.groundtruth/formal-artifact-approvals/<date>-dcl-peer-solution-owner-gate-001.json` produced with all `REQUIRED_PACKET_FIELDS`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block per `CODEX-WAY-OF-WORKING.md`.
- [ ] `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_peer_solution_owner_gate.py` PASSES (T1-T5).
- [ ] Post-impl report cites the deliberation search performed before insert (`.claude/rules/deliberation-protocol.md` § Before Creating WIs or Specs); F2 closure.
- [ ] Codex VERIFIED on post-implementation report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

Filed under `bridge/gtkb-peer-solution-owner-gate-dcl-007.md` with corresponding `bridge/INDEX.md` entry (insert `REVISED: bridge/gtkb-peer-solution-owner-gate-dcl-007.md` at top of doc entry); append-only version chain preserved.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

Single-DCL implementation; not a bulk standing-backlog operation.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-007` REVISED-3.
- **DECISION DEFERRED markers:** promotion to all-five-states scope; promotion from advisory to blocking; runtime enforcement code.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4 (helper validation).

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-3 is a single-DCL implementation proposal, NOT a bulk standing-backlog operation under `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS`. The clause-preflight surfaces it for inventory scope because the proposal mentions `GOV-STANDING-BACKLOG-001` (in Spec Links) and "standing backlog" (in Standing Backlog Visibility above). The actual mutation is one MemBase row + one formal-artifact-approval packet; the formal-artifact-approval discipline above is the full bulk-ops evidence-pattern coverage.

## Risk + Rollback

**Risk R1 (Low; carry-forward from `-005`):** Helper-script CLI changes between this GO and implementation. Mitigation: helper has tested CLI contract (WI-3266 Slice 1 VERIFIED); CLI changes would require a new bridge slice.

**Risk R2 (Low; carry-forward from `-005`):** `enforcement_mode` storage under `constraints` JSON makes the field harder to query. Mitigation: consistent with live schema; first-class column would be a separate schema-extension proposal.

**Risk R3-NEW (Low; REVISED-3):** Phase-1 narrowing (excluding `monitor` and `reject-with-no-spec-impact`) may need future expansion to cover all five procedure-vocabulary states. Mitigation: T5 assertion documents the intentional narrowing; future expansion would be a follow-on bridge slice with empirical evidence.

**Rollback:** `git revert <commit-sha>` on this bridge filing. MemBase row reverts via append-only `update_spec` with `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` -- new MemBase DCL is a net-new design constraint.

## Loyal Opposition Asks

1. Confirm F1 closure: `.claude/rules/peer-solution-advisory-loop.md` is in Spec Links + IP-1's procedure-vocabulary alignment subsection + T5 assertion validates the constraint text cites the procedure rule.
2. Confirm F2 closure: `.claude/rules/deliberation-protocol.md` is in Spec Links + the spec-to-test mapping row requires the post-impl report to cite the before-insert deliberation search.
3. Confirm the Phase-1 narrowing (in-scope classes adopt/adapt/reject-with-spec-impact/defer; out-of-scope monitor/reject-with-no-spec-impact) is acceptable as a Phase-1 scope choice, with expansion deferred to a future bridge slice with empirical evidence.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
