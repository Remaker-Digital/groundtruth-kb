NEW

# Post-implementation report — Per-Item Authorization Quarantine for Dispatch Head-of-Line Blocking

bridge_kind: implementation_report
Document: gtkb-dispatch-per-item-auth-quarantine
Version: 007
Date: 2026-06-24 UTC
Responds-to: bridge/gtkb-dispatch-per-item-auth-quarantine-006.md (LO GO)
Implements: bridge/gtkb-dispatch-per-item-auth-quarantine-005.md (Prime proposal REVISED)

author_identity: prime-builder/cursor/E
author_harness_id: E
author_session_context_id: cursor-wi4770-impl
author_model: Cursor Agent
author_model_version: composer
author_model_configuration: interactive session; owner init `::init gtkb pb`; session marker prime-builder

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4770

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py"]

implementation_scope: dispatch_per_item_impl_auth_quarantine
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented WI-4770 per Codex GO at `bridge/gtkb-dispatch-per-item-auth-quarantine-006.md`.

1. **`scripts/cross_harness_bridge_trigger.py`:** `_issue_dispatch_authorization_for_selected()` now issues implementation authorization per GO item via `create_authorization_packet()`. On `AuthorizationError`, the slug is recorded in `dispatch-failures.jsonl` with reason `impl_auth_quarantined` and processing continues for remaining healthy GO items. When every GO item fails authorization, the function returns `ok: False` with reason `all_impl_auth_quarantined`. When at least one item succeeds, named packets and `current.json` are written for the healthy subset only. Added `all_impl_auth_quarantined` to `NON_LAUNCHED_FAILURE_REASONS`.
2. **`scripts/single_harness_bridge_dispatcher.py`:** Applied the same per-item quarantine semantics to the substrate-local `_issue_dispatch_authorization_for_selected()` helper (including GO-only filtering). The scheduled spawn path continues to delegate to the cross-harness trigger implementation, which now carries the fix.
3. **Tests:** Updated WI-4358 authorization tests to mock `create_authorization_packet` instead of the retired batch helper. Added `test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy` for mixed bad+healthy GO batches. Updated single-item failure spawn regression to expect `all_impl_auth_quarantined` / `impl_auth_quarantined`.

## WI-4742 dirty baseline handling

At implementation start, `scripts/cross_harness_bridge_trigger.py` had only unrelated minimal dirty state (+2 lines) outside `_issue_dispatch_authorization_for_selected()`. WI-4770 edits are confined to that function, import additions, and `NON_LAUNCHED_FAILURE_REASONS`. No WI-4742 diagnose/heartbeat logic was modified or reverted.

## Specification Links (carried forward)

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-S421` — owner AUQ selecting per-item quarantine fix.
- `bridge/gtkb-dispatch-malformed-status-token-quarantine-004.md` — WI-4658 precedent for per-item quarantine pattern.
- `bridge/gtkb-dispatch-per-item-auth-quarantine-004.md` — prior NO-GO requiring single-harness substrate coverage.

## Spec-Derived Verification Results

| Specification | Test or Verification Command | Executed | Result |
|---|---|---|---|
| `GOV-RELIABILITY-FAST-LANE-001` | `git diff --name-status -- scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py` | yes | Small defect fix; no new public API |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | `python -m pytest platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short` | yes | 35 passed |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | same single-harness pytest run | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -k issue_dispatch_auth -q --tb=short` | yes | 4 passed |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | implementation started after GO `-006` with active claim + packet | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | target path inspection | yes | All paths under `scripts/` and `platform_tests/` |

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-dispatch-per-item-auth-quarantine
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-dispatch-per-item-auth-quarantine
```

Observed: 127 passed (full two-file suite); ruff check PASS; ruff format PASS after reformat; both preflights PASS with zero blocking gaps.

Recommended commit type: `fix:` — repair dispatch head-of-line blocking without new public capability.
