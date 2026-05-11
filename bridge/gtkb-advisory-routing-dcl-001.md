NEW

# Advisory Routing DCL - NEW

bridge_kind: implementation_proposal
Document: gtkb-advisory-routing-dcl
Version: 001 (NEW; Slice 1 — candidate DCL for ADVISORY routing)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-11 UTC
Session: S341
Parent Slice-0 thread: `bridge/gtkb-advisory-report-message-type-conversion-003.md` (Codex GO at `-004`).

## Claim

This proposal authors a **candidate DCL for ADVISORY status routing** as MemBase row `DCL-ADVISORY-ROUTING-001`. The DCL formalizes the machine-checkable constraint that ADVISORY-status bridge entries are routed via Axis-2 (non-dispatchable) and MUST NOT increment cross-harness event-driven trigger's actionable-signature for the receiving harness.

The parent Slice-0 GO explicitly named this as follow-on (c): "Routing DCL candidate (`DCL-ADVISORY-ROUTING-001`)" (`bridge/gtkb-advisory-report-message-type-conversion-003.md:128`).

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
- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001`
- `DCL-SMART-POLLER-AUTO-TRIGGER-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/bridge-essential.md`
- `.claude/rules/operating-model.md`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md`
- `independent-progress-assessments/CODEX-REVIEW-CHECKLISTS.md`

## Prior Deliberations

- `bridge/gtkb-advisory-report-message-type-conversion-001/002/003/004.md` - parent Slice-0 chain (GO at -004).
- `bridge/gtkb-advisory-report-protocol-extension-001/002/003/004.md` - sibling (a) (GO at -004).
- `bridge/gtkb-advisory-report-template-spec-001.md` - sibling (b).
- `bridge/gtkb-startup-trigger-awareness-and-skill-reference-001-006.md` (VERIFIED) - two-axis bridge automation model (Axis 1 dispatchable / Axis 2 non-dispatchable).
- `bridge/gtkb-bridge-advisory-status-001-*` - parallel runtime thread implementing ADVISORY parser inventory.

## Owner Decisions / Input

- **AUQ S341 (2026-05-11) autonomous-execution directive:** Authorizes this Slice-1 follow-on filing.
- **Parent Slice-0 GO at `-004`:** explicit authorization to file this follow-on thread.

Outstanding owner decisions before VERIFIED: formal-artifact-approval packet for `DCL-ADVISORY-ROUTING-001` MemBase insertion produced at implementation time. Packet MUST be presented in a standalone `OWNER ACTION REQUIRED` block, one decision at a time, per `CODEX-WAY-OF-WORKING.md` § owner-action-protocol.

## Scope (Slice 1)

### IN SCOPE

**IP-1: Author `DCL-ADVISORY-ROUTING-001` as a MemBase row** with `type='design_constraint'`, `status='specified'`, `enforcement_mode='advisory'`:

1. **Constraint statement:** "ADVISORY-status bridge entries (latest INDEX line `ADVISORY:`) MUST be routed via Axis-2 (non-dispatchable) per `.claude/rules/bridge-essential.md` § Two-Axis Bridge Automation Model. The cross-harness event-driven trigger MUST exclude ADVISORY rows from the actionable-signature computation for the receiving harness; ADVISORY surfacing is via the in-session AXIS 2 UserPromptSubmit hook (`.claude/hooks/bridge-axis-2-surface.py`) instead."
2. **Assertions field:** machine-checkable predicates. Pattern: `assert (latest_status == "ADVISORY") -> (recipient_actionable_signature_excludes_entry AND axis_2_surface_notifies_in_session)`.
3. **Enforcement mode:** `advisory` (Phase 1 advisory pilot per `GOV-20`); promotion to `blocking` deferred until empirical evidence from the parallel runtime thread (`gtkb-bridge-advisory-status-001`).
4. **Rationale:** preserves Axis-2 ownership of non-dispatchable work; avoids double-notify (both fresh harness dispatch + in-session surface); avoids advisory thrashing in the actionable-signature computation.

**IP-2: Formal-artifact-approval packet** at `.groundtruth/formal-artifact-approvals/<date>-dcl-advisory-routing-001.json`.

**IP-3: MemBase regression test** at `platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py` asserting:

- DCL row exists with `type='design_constraint'`, `status='specified'`, `enforcement_mode='advisory'`.
- `constraint` field references `Axis-2`, `non-dispatchable`, `actionable-signature`, and `UserPromptSubmit` (or `AXIS 2 surface`).
- `assertions` field contains a machine-checkable predicate.

**IP-4: Pre-insertion packet validation** using the canonical inline Python pattern.

**IP-5: MemBase insert** uses `GTKB_FORMAL_APPROVAL_PACKET` env var.

### OUT OF SCOPE

- Template spec (sibling thread).
- Protocol extension (sibling thread).
- Dashboard counter spec (sibling thread).
- Runtime parser updates (parallel thread `gtkb-bridge-advisory-status-001`).
- Promotion to `blocking` enforcement.

## Test Plan

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-advisory-routing-dcl` - PASS expected.
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-advisory-routing-dcl` - exit 0 expected.
3. `python -m pytest platform_tests/groundtruth_kb/specs/test_dcl_advisory_routing.py -q --tb=short` - PASS.
4. Pre-insertion packet validation per IP-4 — emits `packet_valid`.

### Spec-to-test mapping

| Spec / surface | Verifying step |
|---|---|
| GOV-FILE-BRIDGE-AUTHORITY-001 | This NEW + Codex GO + post-impl VERIFIED. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Step 1 PASS. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Step 2 PASS + Step 3. |
| GOV-ARTIFACT-APPROVAL-001 | IP-2 + IP-4 + IP-5. |
| DCL-ARTIFACT-APPROVAL-HOOK-001 | IP-4 validates against gate schema. |
| `CODEX-WAY-OF-WORKING.md` § owner-action-protocol | Standalone OWNER ACTION REQUIRED block. |
| ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 | Axis-2 routing preserves owner-out-of-loop for dispatchable work; advisory work surfaces via AXIS 2. |
| DCL-SMART-POLLER-AUTO-TRIGGER-001 | DCL clarifies that ADVISORY does NOT trigger auto-dispatch. |

## Acceptance Criteria

- [ ] Applicability + clause preflights PASS on `-001`.
- [ ] Codex GO.
- [ ] `DCL-ADVISORY-ROUTING-001` inserted with constraint + assertions + enforcement_mode='advisory'.
- [ ] Pre-insertion packet validation (IP-4) executed.
- [ ] MemBase insert (IP-5) uses `GTKB_FORMAL_APPROVAL_PACKET`.
- [ ] Approval packet presented in standalone `OWNER ACTION REQUIRED` block.
- [ ] `python -m pytest` regression PASS.
- [ ] Codex VERIFIED on post-impl report.

## Bridge Index Compliance (GOV-FILE-BRIDGE-AUTHORITY-001 evidence)

This bridge artifact is filed under `bridge/gtkb-advisory-routing-dcl-001.md` with a corresponding `bridge/INDEX.md` entry (insert at top of doc list); append-only version chain.

## Standing Backlog Visibility (GOV-STANDING-BACKLOG-001 evidence)

This Slice-1 follow-on adds one new bridge entry. NOT a bulk operation.

- **inventory artifact:** IP-1 to IP-5 enumeration.
- **review packet:** this `-001` NEW.
- **DECISION DEFERRED markers:** sibling-thread follow-ons; promotion to blocking; runtime parser updates in parallel thread.
- **formal-artifact-approval packet:** produced at implementation time per IP-2 + IP-4.

## Risk + Rollback

**Risk R1 (Low):** Routing DCL may conflict with parallel runtime thread's eventual per-parser dispositions. Mitigation: DCL is `advisory` enforcement; if runtime evolves differently, DCL amends in a follow-on bridge thread.

**Risk R2 (Low):** Phrasing in IP-1 constraint may be too prescriptive for future axis evolution. Mitigation: enforcement_mode=`advisory`; can be amended.

**Rollback:** `git revert <commit-sha>`. MemBase row reverts via append-only `change_reason='reverted: <commit-sha>'`.

## Recommended Commit Type

`feat:` — new MemBase DCL is a net-new design constraint.

## Loyal Opposition Asks

1. Confirm the IP-1 constraint statement correctly couples ADVISORY routing to Axis-2 + UserPromptSubmit surface.
2. Confirm `advisory` enforcement mode is the right Phase-1 default per `GOV-20`.
3. Confirm coordination with parallel `gtkb-bridge-advisory-status-001` runtime thread is appropriate (DCL describes contract; runtime parsers implement).

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
