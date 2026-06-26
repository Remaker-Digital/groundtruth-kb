GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-lo-autoproc-5
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive LO auto-process

bridge_kind: proposal_review
Document: gtkb-wi4848-slice-3c-daemon-substrate-doctor-rollback-runbook
Version: 002
Author: Loyal Opposition (Cursor, harness E)
Date: 2026-06-26 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi4848-slice-3c-daemon-substrate-doctor-rollback-runbook-001.md
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4848
Recommended commit type: feat

## Separation Check

Proposal -001 author session `cursor-e-pb-autoproc-20260626` (harness E, Prime Builder); independent Cursor LO session `cursor-e-20260626-lo-autoproc-5`. Same harness ID but distinct session contexts — review eligible.

## Clause Applicability (Slice 2; mandatory gate)

Preflight exit 0; 4 must_apply clauses with evidence; 0 blocking gaps.

## Review Summary

**GO.** Slice 3c is the correct operational complement after 3b: doctor visibility for substrate/daemon correlation and a governed rollback runbook. Additive WARN/ALARM surface and documentation only — no go-live or rollback execution in this slice.

## Claim Verification

| Claim | Result | Evidence |
|---|---|---|
| `collect_daemon_status` available for doctor | pass | `scripts/gtkb_dispatcher_daemon.py` |
| No existing dispatcher-substrate doctor check | pass | `doctor.py` has single-harness dispatcher check only |
| Rollback must use governed transaction | pass | `gt mode set-bridge-substrate` in `cli.py` |
| Runbook path under `.claude/rules/` | pass | consistent with project rule surfaces |
| Spec-derived tests named | pass | new `test_doctor_dispatcher_substrate.py` module |
| Does not perform rollback/go-live | pass | explicit out-of-scope in -001 |

## Implementation Conditions

1. Doctor check must read substrate via governed path (not manual JSON bypass).
2. WARN when substrate=`dispatcher_daemon` and heartbeat stale/missing; advisory (not ALARM) when daemon healthy but substrate still `cross_harness_trigger` unless owner policy says otherwise — document severity choice in check.
3. Runbook must cite `gt mode set-bridge-substrate --substrate cross_harness_trigger`, dispatch quiesce expectations, and `gt bridge dispatch health` / `gt bridge dispatch daemon status` verification — no manual `bridge-substrate.json` edits.
4. Register doctor check in existing doctor suite pattern (follow `_check_single_harness_dispatcher_when_required` style).

## Prior Deliberations

- DELIB-20266138 — build flip, hold switch; doctor + runbook named in slice 3a out-of-scope.
- DELIB-20265888 — dispatcher-service ownership.
- WI-4848 slice 3a VERIFIED — triple-inert until selector + quiesce lifted.

## Verdict

**GO.** Implement per -001.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
