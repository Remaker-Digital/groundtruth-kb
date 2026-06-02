NEW

bridge_kind: implementation_report
Document: gtkb-bridge-dispatch-per-document-lease-substitution
Version: 003
Responds to: bridge/gtkb-bridge-dispatch-per-document-lease-substitution-002.md GO
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-01 UTC
Session: S380
Recommended commit type: fix
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-PER-DOCUMENT-LEASE-SUBSTITUTION
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-57A736
author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: S380-per-document-lease-003
author_model: Gemini 3.5 Flash
author_model_version: gemini-3.5-flash
author_model_configuration: Antigravity desktop session environment

# Bridge Dispatch Per-Document Lease Substitution — Post-Implementation Report

## Summary

Implemented and verified the per-document lease substitution logic in `scripts/cross_harness_bridge_trigger.py` and its test suite per the approved `GO` at `-002`.

Instead of checking the harness-wide active lock via `check_counterpart_active()`, the trigger now evaluates leases per-document in the `selected` batch using `is_lease_held()` from `scripts/bridge_lease_registry.py`.

- If all selected items are leased by the counterpart:
  - Skip/suppress the dispatch.
  - Set `last_result = "counterpart_active_session_present"`.
  - Record the signature of the full `selected` batch under `last_suppressed_signature` to keep the retry semantic alive.
- If some but not all selected items are leased by the counterpart:
  - Filter out leased items and proceed to dispatch only the unleased subset.
  - Update `selected_count` and `pending_count` to reflect the dispatched subset, and set `last_result = "launched"` (or `"launch_failed"` depending on Popen outcome) for the unleased subset.
- If no selected items are leased by the counterpart:
  - Proceed with normal dispatch of the entire `selected` batch.

We also verified the Stop-hook heartbeat fix (`_handle_session_stop()` in `scripts/active_session_heartbeat.py` only unlinks the lock file and does not recreate it defensively if it is already absent), created regression tests to verify this behavior, and fixed the Claude command-line arguments assertion in `test_cross_harness_bridge_trigger.py`.

## Owner Decisions / Input

None required. The standing project authorization `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-PER-DOCUMENT-LEASE-SUBSTITUTION` covers this work stream.

## Specification Links

Carried forward and justified per governance standards:

- `SPEC-INTAKE-57a736` (Bridge dispatch suppression scoped per bridge document (per-document lease)) — Wired the per-document lease checks into `cross_harness_bridge_trigger.py` to suppress dispatch of leased items while allowing unleased items to proceed.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — The bridge index continues to govern workflow state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Compliant specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verification plan executed below.

Advisory specs carried forward:
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (Advisory) — Traceability across WI-AUTO-SPEC-INTAKE-57A736 and bridge files.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (Advisory) — Tracked lifecycle progression of the work item.

## Clause Scope Clarification (Not a Bulk Operation)

This is a single-concern reliability defect fix for `WI-AUTO-SPEC-INTAKE-57A736`. It is not a bulk standing-backlog operation and does not resolve or batch-mutate multiple work items. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is not applicable. The formal-artifact-approval of this single report satisfies the evidence requirement for this clause.

## Prior Deliberations

- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2512.json` — Owner clarification regarding per-document lease suppression and Stop-hook heartbeat regression testing.
- `.groundtruth/formal-artifact-approvals/2026-05-30-DELIB-2513.json` — Owner directive to execute implementation through the bridge protocol.

## Files Changed

Changes stay strictly within the approved `target_paths`:

- `scripts/cross_harness_bridge_trigger.py` — Imported `is_lease_held` and replaced harness-wide counterpart active check with per-document lease substitution logic inside the dispatch decision loop.
- `platform_tests/scripts/test_bridge_dispatch_per_document_lease.py` — Created a new test suite covering four test cases: cross-item non-suppression, same-item lease refusal, stale lease reclamation, and dispatch using leases rather than harness locks.
- `platform_tests/scripts/test_active_session_heartbeat_stop_fix.py` — Created a new regression test suite verifying that session-stop mode does not write a fresh active-session heartbeat on session end.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — Fixed the Claude command arguments assertion to expect `--permission-mode acceptEdits` and `--allowed-tools` automatically appended by `_harness_command`.

## Spec-to-Test Mapping

| Specification | Test or verification command | Result |
|---|---|---|
| `SPEC-INTAKE-57a736` Clause 1 (cross-item) | `test_active_lease_on_x_does_not_suppress_y` | PASS |
| `SPEC-INTAKE-57a736` Clause 2 (same-item refusal) | `test_second_worker_refused_lease_on_same_document` | PASS |
| `SPEC-INTAKE-57a736` Clause 3 (stale lease reclamation) | `test_stale_lease_is_reclaimed` | PASS |
| `SPEC-INTAKE-57a736` Clause 4 (trigger lease checks) | `test_dispatch_uses_lease_not_harness_lock` | PASS |
| `SPEC-INTAKE-57a736` Clause 5 & 6 (stop-hook heartbeat fix) | `test_stop_mode_does_not_write_fresh_heartbeat` | PASS |
| Full Trigger Verification | Pytest suite execution for trigger | 43 PASSED |

## Verification Commands & Observed Results

### 1. Per-document lease test execution

**Command**:
```text
$env:TEMP="E:\GT-KB\.tmp"; $env:TMP="E:\GT-KB\.tmp"; python -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py -q --tb=short --basetemp=E:\GT-KB\.tmp\basetemp
```
**Observed**:
```text
4 passed in 10.72s
```

### 2. Heartbeat stop-hook fix test execution

**Command**:
```text
$env:TEMP="E:\GT-KB\.tmp"; $env:TMP="E:\GT-KB\.tmp"; python -m pytest platform_tests/scripts/test_active_session_heartbeat_stop_fix.py -q --tb=short --basetemp=E:\GT-KB\.tmp\basetemp
```
**Observed**:
```text
1 passed in 1.57s
```

### 3. Full trigger test suite execution

**Command**:
```text
$env:TEMP="E:\GT-KB\.tmp"; $env:TMP="E:\GT-KB\.tmp"; python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short --basetemp=E:\GT-KB\.tmp\basetemp
```
**Observed**:
```text
43 passed in 2.42s
```

### 4. Ruff Checks

**Command**:
```text
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```
**Observed**:
```text
All checks passed!
```

### 5. Bridge Preflight Checks

**Command (Applicability Preflight)**:
```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
```
**Observed**:
```text
- preflight_passed: true
- missing_required_specs: []
```

**Command (Clause Preflight)**:
```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-dispatch-per-document-lease-substitution
```
**Observed**:
```text
- Clauses evaluated: 5
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

## Risks & Rollback

- Reverting the changes in `scripts/cross_harness_bridge_trigger.py` safely restores the previous harness-wide `check_counterpart_active` active-session lock check logic.

## In-Root Placement Evidence

All changes are strictly located inside `E:\GT-KB`. Satisfies `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
