NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-30T04-20-00Z-prime-builder-E-s515
author_model: Cursor Agent
author_model_version: Composer
author_model_configuration: Cursor E, Prime Builder interactive session, harness-readiness integration proof

# Implementation Proposal - Reconcile stale failover dispatch state after terminal bridge outcomes

bridge_kind: prime_proposal
Document: gtkb-wi4935-dispatch-failover-stale-state-reconciliation
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4935-STALE-FAILOVER-RECONCILIATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4935

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Harness-readiness integration proof on 2026-06-30 found a control-surface split after successful headless LO work: `gt bridge dispatch health` can report PASS while `python scripts/dispatcher_runtime.py --diagnose` reports DEGRADED because failover harnesses B/C/D/E retain stale `pending_count=1`, `last_result=subprocess_execution_failed`, and `failure_class=subprocess_execution_failed` for `gtkb-wi4933-post-verdict-exit-reconciliation` even though that bridge thread is terminal at VERIFIED and F completed fresh headless work on other items.

WI-4934 repaired same-signature LO failover during active ticks; WI-4931 repaired false-positive diagnose cases for work-intent suppression and unselected idle harnesses. Neither slice reconciles historical failover residue once the underlying bridge document is terminal or once failover exhaustion has completed. This leaves release-health operators with contradictory surfaces and blocks harness-readiness sign-off for the full B/C/D/E failover chain.

## Claim

Prime Builder proposes a bounded `WI-4935` repair to reconcile stale failover recipient state after terminal bridge outcomes, align diagnose liveness with canonical dispatch health for historical terminal failures, and extend runtime health evaluation so failover-chain residue is visible without false PASS on selected recipients alone.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4935` captures the release-health gap and `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4935-STALE-FAILOVER-RECONCILIATION` authorizes the bounded source/test repair.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/gtkb_dispatcher_daemon.py`, `scripts/dispatcher_runtime.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, and `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatch health, diagnose, and report surfaces must agree on actionable vs historical failure state.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon-owned dispatch must not strand operators behind stale pending residue after terminal bridge outcomes.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon remains the only automated dispatch path; reconciliation belongs in runtime/daemon state writers, not manual bridge scans.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.

## Prior Deliberations

- `DELIB-20266590` - Owner selected harness-readiness option E to file WI-4935 stale failover dispatch-state reconciliation.
- `DELIB-20266508` - Authorize WI-4934 dispatcher failed-recipient LO failover repair (adjacent failover behavior; does not cover post-terminal residue).
- `DELIB-20266507` - Authorize WI-4933 dispatcher backpressure health classification repair.
- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix (WI-4931 scope; does not cover stale historical failover rows).
- `DELIB-20266276` - Authorize daemon-resilience program implementation and release-health hardening.

## Owner Decisions / Input

- `DELIB-20266590` - owner directive during S515 harness-readiness integration proof to file WI-4935 for stale B/C/D/E failover residue after terminal bridge outcomes.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4935-STALE-FAILOVER-RECONCILIATION` - active project authorization covering `WI-4935` source/test changes.

## Evidence From Live Test

- Terminal bridge thread: `bridge/gtkb-wi4933-post-verdict-exit-reconciliation-004.md` is VERIFIED; the underlying dispatch work is complete.
- Stale residue in `.gtkb-state/bridge-poller/dispatch-state.json` (~2026-06-30T13:13-13:43Z cascade): `loyal-opposition:B`, `:C`, `:D`, and `:E` each retain `pending_count=1`, `last_result=subprocess_execution_failed`, and `primary_bridge_id=gtkb-wi4933-post-verdict-exit-reconciliation` with processed exit sidecars.
- Control-surface split at probe time: `gt bridge dispatch health --json` could report PASS for selected recipients A/F while `python scripts/dispatcher_runtime.py --diagnose` reported DEGRADED citing B/C/D/E `subprocess_execution_failed`.
- Fresh headless success on another item: OpenRouter F completed `gtkb-wi4782-session-role-authority-audit` to VERIFIED at `bridge/gtkb-wi4782-session-role-authority-audit-004.md`, proving the primary LO path works; stale failover residue is orthogonal to current queue emptiness.
- Existing regression gap: `test_ranked_lo_targets_after_exhausted_batch_clear_stale_state` clears stale rows during an active dry-run cycle but does not cover terminal bridge reconciliation after VERIFIED.

## Proposed Scope

- Reconcile stale failover recipient rows when the referenced `primary_bridge_id` (or equivalent selected document) is terminal at VERIFIED/WITHDRAWN or otherwise no longer actionable for the needed role.
- Clear `pending_count`, `failure_class`, and stale `subprocess_execution_failed` residue on failover harnesses that are not the current selected recipient once the underlying bridge document is terminal.
- Extend `dispatcher_runtime.py --diagnose` liveness rendering so historical terminal failures do not force DEGRADED when canonical dispatch health is otherwise PASS and no actionable queue work remains for that recipient.
- Extend `bridge_dispatch_config._runtime_dispatch_evaluation` (or adjacent health helpers) so failover-chain residue is classified consistently instead of hiding behind selected-recipient-only PASS.
- Add focused regressions in `platform_tests/scripts/test_dispatcher_runtime.py` and `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` for terminal VERIFIED reconciliation and health/diagnose alignment.

## Out of Scope

- Retired poller/trigger restoration, manual owner scanning as a permanent workaround, credential changes, provider retirement/waiver, or harness-specific launcher repairs already tracked under WI-4932/WI-4933.
- PB dispatch to Codex A while `work_intent_already_held` / inactive PAUTH blocks WI-4929 (separate slice).
- Live failover reliability proofs for B/C/D/E themselves (follow-on harness-readiness slices after state reconciliation).

## Specification-Derived Verification Plan

| Spec / requirement | Verification | Expected |
|---|---|---|
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -k stale -q --no-header` | New/updated stale-reconciliation regressions PASS |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py -k stale -q --no-header` | Daemon tick reconciliation regressions PASS |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused runtime test asserting terminal VERIFIED bridge clears stale `pending_count` on failover recipients | `pending_count==0`, no stale `failure_class` |
| `ADR-DISPATCHER-ARCHITECTURE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --no-header` (focused slice named in implementation report) | No regression in dispatch suite |
| Post-change live probe (implementation report) | `gt bridge dispatch health --json` and `python scripts/dispatcher_runtime.py --diagnose` after reconciliation on stale `gtkb-wi4933-post-verdict-exit-reconciliation` residue | Surfaces agree; B/C/D/E no longer DEGRADED solely from terminal historical failures |

## Risk / Rollback

Risk is bounded to dispatch-state interpretation and health/diagnose rendering. Incorrect reconciliation could hide real in-flight failures if terminal detection is too aggressive; mitigate with bridge-status checks against TAFE/dispatcher bridge state and focused regressions that keep actionable pending work intact.

Rollback: single revert commit restoring prior runtime/daemon writers; dispatch-state.json can be rebuilt via governed soft reset if needed.

## Bridge Filing

This proposal is filed under `bridge/` as the first status-bearing numbered bridge file for `gtkb-wi4935-dispatch-failover-stale-state-reconciliation`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - corrects stale failover dispatch-state reconciliation and release-health surface alignment without changing bridge protocol semantics.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
