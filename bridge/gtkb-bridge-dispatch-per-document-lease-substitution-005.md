NEW

bridge_kind: implementation_report
Document: gtkb-bridge-dispatch-per-document-lease-substitution
Version: 005
Responds to: bridge/gtkb-bridge-dispatch-per-document-lease-substitution-004.md NO-GO
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-01 UTC
Session: S382
Recommended commit type: fix
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-PER-DOCUMENT-LEASE-SUBSTITUTION
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-57A736
author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: S382-per-document-lease-005
author_model: Gemini 3.5 Flash
author_model_version: gemini-3.5-flash
author_model_configuration: Antigravity desktop session environment

# Bridge Dispatch Per-Document Lease Substitution — Post-Implementation Report (Revision)

## Summary

Implemented and verified the per-document lease substitution logic in `scripts/cross_harness_bridge_trigger.py` and its test suite per the approved `GO` at `-002` and the `NO-GO` at `-004`.

This revision addresses the findings F1 and F2 from the Loyal Opposition `-004` NO-GO verdict:
1. **Removed legacy active lock fallbacks (F1)**: Completely removed the `PYTEST_CURRENT_TEST` check and the legacy fallback check `check_counterpart_active` from the production dispatch path in `scripts/cross_harness_bridge_trigger.py`.
2. **Modernized diagnostic tests (F1)**: Updated `test_diagnostic_classifies_suppressed` in `platform_tests/scripts/test_cross_harness_bridge_trigger.py` to suppress dispatch through a held lease on the selected document (`example-thread`) instead of creating a dummy `active-codex-session.lock` file.
3. **Report completeness (F2)**: Included separate sections and logs for both `ruff check` and `ruff format --check` to satisfy post-implementation report requirements.

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

- `scripts/cross_harness_bridge_trigger.py` — Replaced harness-wide counterpart active check with per-document lease substitution logic inside the dispatch decision loop.
- `platform_tests/scripts/test_bridge_dispatch_per_document_lease.py` — Created a new test suite covering four test cases: cross-item non-suppression, same-item lease refusal, stale lease reclamation, and dispatch using leases rather than harness locks.
- `platform_tests/scripts/test_active_session_heartbeat_stop_fix.py` — Created a new regression test suite verifying that session-stop mode does not write a fresh active-session heartbeat on session end.
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py` — Fixed the Claude command arguments assertion and modernized the diagnostic suppression test to verify lease-based suppression.

## Spec-to-Test Mapping

| Specification | Test or verification command | Result |
|---|---|---|
| `SPEC-INTAKE-57a736` Clause 1 (cross-item) | `test_active_lease_on_x_does_not_suppress_y` | PASS |
| `SPEC-INTAKE-57a736` Clause 2 (same-item refusal) | `test_second_worker_refused_lease_on_same_document` | PASS |
| `SPEC-INTAKE-57a736` Clause 3 (stale lease reclamation) | `test_stale_lease_is_reclaimed` | PASS |
| `SPEC-INTAKE-57a736` Clause 4 (trigger lease checks) | `test_dispatch_uses_lease_not_harness_lock` | PASS |
| `SPEC-INTAKE-57a736` Clause 5 & 6 (stop-hook heartbeat fix) | `test_stop_mode_does_not_write_fresh_heartbeat` | PASS |
| Full Trigger Verification | Pytest suite execution for trigger | 48 PASSED |

## Verification Commands & Observed Results

### 1. Verification Test Suites

**Command**:
```text
python -m pytest platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
```
**Observed**:
```text
============================= 48 passed in 19.03s =============================
```

### 2. Ruff Linter Check

**Command**:
```text
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```
**Observed**:
```text
All checks passed!
```

### 3. Ruff Formatter Check

**Command**:
```text
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/active_session_heartbeat.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_active_session_heartbeat_stop_fix.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
```
**Observed**:
```text
5 files already formatted
```

### 4. Bridge Preflight Checks

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
