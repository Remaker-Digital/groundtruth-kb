NEW
author_identity: claude
author_harness_id: B
author_session_context_id: 2026-05-30-prime-builder-post-S372
author_model: Claude
author_model_version: Opus 4.8 (1M context)
author_model_configuration: default reasoning, explanatory output style
author_metadata_source: session

# Implementation Proposal - Bridge Dispatch Per-Document Lease Substitution

bridge_kind: prime_proposal
Document: gtkb-bridge-dispatch-per-document-lease-substitution
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-30 UTC
Source: SPEC-INTAKE-57a736 / WI-AUTO-SPEC-INTAKE-57A736
Recommended commit type: feat
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-PER-DOCUMENT-LEASE-SUBSTITUTION
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-57A736

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/active_session_heartbeat.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py", "platform_tests/scripts/test_active_session_heartbeat_stop_fix.py"]

## Summary

Replace the harness-wide active-session suppression in the cross-harness bridge
dispatch trigger with per-document leasing, so an active harness session no
longer blocks dispatch of a bridge document it is not working. This implements
`SPEC-INTAKE-57a736`. The lease registry module (`scripts/bridge_lease_registry.py`,
already VERIFIED and committed) provides the mechanism; this proposal wires it
into the dispatch decision point and retires the harness-wide
`check_counterpart_active` guard. It also lands the interim low-risk Stop-hook
fix from the requirement (clause 5).

## Sequencing Note (collision-aware)

`scripts/cross_harness_bridge_trigger.py` currently carries VERIFIED-but-
uncommitted parallel work from `gtkb-cross-harness-trigger-index-edit-race-quiesce`
(VERIFIED) and `gtkb-dispatch-failures-jsonl-rotation` (VERIFIED). The
implementation edit MUST land on the committed post-quiesce structure, not the
pre-quiesce HEAD version. The integration point is stable across that change:
the `elif check_counterpart_active(target, state_dir):` suppression branch
survives the quiesce edits (working-tree line ~1211). Per owner AUQ (2026-05-30,
"Drive proposal now, let collision self-clear"), this proposal is filed now for
review; the implementation edit proceeds once the parallel VERIFIED work commits
and the tree is clean. No racing of the parallel commit.

## In-Root Placement Evidence

All target paths are within `E:\GT-KB`: `scripts/cross_harness_bridge_trigger.py`,
`scripts/active_session_heartbeat.py`, and two new `platform_tests/scripts/*.py`
test modules. The runtime lease registry directory `.gtkb-state/bridge-poller/leases/`
is in-root. No `applications/` paths; no out-of-root paths.

## Specification Links

- SPEC-INTAKE-57a736 - the governing requirement (per-document lease substitution); this proposal implements its six clauses.
- GOV-FILE-BRIDGE-AUTHORITY-001 - `bridge/INDEX.md` is canonical workflow state; the dispatch change preserves index authority and the actionable-signature scheme.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites the governing spec, machine-readable `target_paths`, and project-linkage metadata.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the verification plan below maps SPEC-INTAKE-57a736 clauses 1, 2, and 6 to executed tests.
- GOV-STANDING-BACKLOG-001 - implements one work item (WI-AUTO-SPEC-INTAKE-57A736); not a bulk backlog operation.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - cites an active PAUTH for the work item.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - the PAUTH does not bypass this bridge GO or the implementation-start packet.
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 - active status, work-item inclusion, spec inclusion, no expiration all satisfied.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - all paths in-root; Agent Red out of scope.
- ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 - auto-trigger contract preserved; the trigger MUST still dispatch on actionable signature change after the lease check.
- DCL-SMART-POLLER-AUTO-TRIGGER-001 - auto-trigger-on-actionable-change contract preserved; leasing gates duplicate dispatch, not the trigger itself.
- ADR-SINGLE-HARNESS-OPERATING-MODE-001 - the lease check must behave correctly in both multi-harness and single-harness topologies.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - lease records are durable runtime artifacts (advisory).
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - lease lifecycle records are governed runtime artifacts (advisory).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - lease lifecycle acquired -> held -> released/reclaimed is an explicit lifecycle (advisory).

## Prior Deliberations

- DELIB-2513 - owner directive (2026-05-30): elevate priority and complete this work ASAP; implementation authorization through the bridge protocol.
- DELIB-2512 - the `/grill-me-for-clarification` decision chain (D1 per-document lease; D2 narrow thread; D3 low-risk interim Stop-hook fix; D5 cross-item+same-item acceptance tests).
- DELIB-2182 - owner authorization (S350) of the lanes/leases scheduler program, which designed per-document leasing to replace the harness-wide guard; this narrow thread realizes that substitution without reviving the full scheduler.
- DELIB-1535 - the suppression-contract NO-GO review whose finding F2 documented the harness-liveness-vs-work-claim limitation this proposal resolves.
- `gtkb-cross-harness-trigger-active-session-suppression-001` (VERIFIED) - the harness-wide suppression contract being substituted.
- `gtkb-cross-harness-trigger-index-edit-race-quiesce` (VERIFIED) and `gtkb-dispatch-failures-jsonl-rotation` (VERIFIED) - the parallel work the implementation must build on top of.
- WI-3485 - the related `counterpart_*` naming-misnomer defect (separate cleanup).

## Owner Decisions / Input

Per the AUQ-only enforcement stack (`SPEC-AUQ-POLICY-ENGINE-001`), the owner decisions authorizing this work are captured in DELIB-2512 and DELIB-2513:

1. AUQ "Grill me into a requirement" - directive to convert the suppression critique into a requirement.
2. Grill D1 "Complete the per-document lease substitution" - the core requirement.
3. Grill D2 "Narrow thread: wire registry into dispatch" - this thread's scope.
4. Grill D3 "Low-risk interim fix only" - the Stop-hook interim change.
5. Grill D5 "Cross-item + same-item behavioral test" - the acceptance bar.
6. AUQ "Elevate priority and move to completion ASAP" (DELIB-2513) - implementation authorization + prioritization.
7. AUQ "Drive proposal now, let collision self-clear" - file this proposal now; implement once the parallel VERIFIED work commits.

No new owner decision is required for Codex review of this proposal.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-57a736` defines the six-clause requirement surface (per-document lease acquisition; no cross-document suppression; replace `check_counterpart_active`; heartbeat-TTL staleness; interim Stop-hook fix; acceptance tests). No requirement revision or waiver is required before implementation after GO.

## Implementation Plan

Built on the committed post-quiesce structure of `scripts/cross_harness_bridge_trigger.py`.

1. **Dispatch-path substitution.** At the per-recipient dispatch decision, replace the `elif check_counterpart_active(target, state_dir):` suppression branch with a per-document lease check using `scripts/bridge_lease_registry.py`:
   - For each selected bridge document in the recipient's dispatch batch, attempt `acquire_lease(doc_slug, state_dir=...)` (or check `is_lease_held`) keyed by the bridge document slug.
   - If a live (non-stale) lease is held for that document, skip dispatching that document (defer), recording a per-document `last_suppressed_signature`-equivalent so it stays retryable - preserving the existing deferral-not-drop semantic at document granularity.
   - If no live lease is held, the spawned worker acquires the lease for the duration of its processing and releases it (or lets it expire by TTL) on completion.
   - Documents NOT held by any lease dispatch normally even when a harness session is otherwise active - satisfying SPEC-INTAKE-57a736 clause 2 (no cross-document suppression).
2. **Retire the harness-wide guard.** Remove `check_counterpart_active` from the live dispatch decision (the function may remain temporarily for back-compat readers but is no longer consulted for suppression). Preserve the actionable-signature scheme and auto-trigger-on-change contract (`DCL-SMART-POLLER-AUTO-TRIGGER-001`).
3. **Lease staleness.** Rely on the registry's heartbeat-TTL staleness (`reclaim_stale_leases` / `_is_stale`) so a crashed worker's lease is reclaimable; no permanent block (clause 4).
4. **Interim Stop-hook fix** (`scripts/active_session_heartbeat.py`): when invoked in Stop mode (session end), do NOT write a fresh active-session heartbeat (and/or shorten the active-session TTL), eliminating the documented false positive where a just-ended session suppresses for up to the TTL. This is a standalone low-risk change that does not remove any race guard (clause 5).
5. **Tests** per the Test Mapping section.

## Test Mapping

| SPEC-INTAKE-57a736 clause | Test |
|---|---|
| Cl.2 - lease on document X does NOT suppress dispatch of document Y | `test_bridge_dispatch_per_document_lease.py::test_active_lease_on_x_does_not_suppress_y` |
| Cl.1 - second worker refused a lease on the same document while held | `test_bridge_dispatch_per_document_lease.py::test_second_worker_refused_lease_on_same_document` |
| Cl.1/Cl.4 - stale lease is reclaimable (no permanent block) | `test_bridge_dispatch_per_document_lease.py::test_stale_lease_is_reclaimed` |
| Cl.3 - dispatch decision no longer consults check_counterpart_active | `test_bridge_dispatch_per_document_lease.py::test_dispatch_uses_lease_not_harness_lock` |
| Cl.6 - interim Stop-hook regression: Stop mode writes no fresh heartbeat | `test_active_session_heartbeat_stop_fix.py::test_stop_mode_does_not_write_fresh_heartbeat` |

## Verification Plan

```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py -q --tb=short
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py
```

The existing cross-harness trigger regression suite must continue to pass (the actionable-signature scheme and dispatch-on-change contract are unchanged).

## Risk and Rollback

- R1: Lease granularity mismatch with batch dispatch. Mitigation: lease keyed per bridge document slug within the batch; tests cover the cross-item and same-item cases.
- R2: Regression in the auto-trigger-on-actionable-change contract. Mitigation: the existing `test_cross_harness_bridge_trigger.py` suite is run; the lease check gates duplicate dispatch only, not the trigger.
- R3: Building on the wrong base (pre-quiesce). Mitigation: implementation is gated on the parallel VERIFIED quiesce/rotation commit; the integration point is the surviving suppression branch.

Rollback: restore the `check_counterpart_active` suppression branch in the dispatch decision and revert the Stop-hook change; remove the two new test modules. The lease registry module is untouched by rollback.

## Pre-Filing Preflight Subsection

After filing, Prime Builder runs:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution --json
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
```

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
