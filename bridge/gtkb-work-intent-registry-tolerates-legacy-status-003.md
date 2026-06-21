NEW
Responds-to: bridge/gtkb-work-intent-registry-tolerates-legacy-status-002.md

# gtkb-work-intent-registry-tolerates-legacy-status — Work-Intent Registry Tolerates Legacy Status Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-work-intent-registry-tolerates-legacy-status
Version: 003
Author: Prime Builder (Antigravity, harness C)
Date: 2026-06-21 UTC

author_identity: Antigravity Prime Builder
author_harness_id: C
author_session_context_id: cb447a9a-62e4-4fbe-8f6f-ef77dee8e1d3
author_model: Gemini 2.5 Flash
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity IDE session

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4660

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_bridge_work_intent_registry.py"]

implementation_scope: source, test
requires_review: false
requires_verification: true

---

## Summary

Implemented the defect fix proposal approved by the GO verdict at version 002. We modified `_thread_version_entries` in `scripts/bridge_work_intent_registry.py` to wrap the `_bridge_file_status` call in a targeted try/except block for `MalformedBridgeStatusError`. If a version's status line cannot be parsed (for example, carrying a grandfathered/legacy status token like `PAUSED` or `IMPLEMENTED` from prior to the status-token tightening), it is skipped and excluded from the version set instead of letting the parse error propagate. This makes threads shadowed by legacy status tokens claimable and transitionable through the governed Write path, while preserving the typed parser contract that the dispatch quarantine mechanism relies on.

## Changes

### `scripts/bridge_work_intent_registry.py`
- Wrapped the call to `_bridge_file_status(path)` inside `_thread_version_entries` in a `try/except MalformedBridgeStatusError` block.
- On exception, it emits a structured `UserWarning` detailing the path and the offending status line, then `continue`s to the next version in the glob scan.
- Formatted the file using Ruff.

### `platform_tests/scripts/test_bridge_work_intent_registry.py`
- Updated the test helper `_write_index` to write actual minimal versioned bridge status files (since `_latest_status` now reads files directly rather than index files, resolving test setup drift).
- Added five spec-derived regression tests covering the legacy status toleration changes:
  1. `test_acquire_tolerates_legacy_status_shadowed_thread` — verifies that a thread containing a legacy token like `PAUSED` in a past version is claimable.
  2. `test_latest_status_skips_legacy_token_version` — verifies that `_latest_status` skips the legacy-token version and parses the latest canonical status.
  3. `test_legacy_token_version_skip_emits_warning` — verifies that skipping a legacy version emits a structured warning.
  4. `test_bridge_file_status_still_raises_on_unrecognized_token_regression` — verifies that `_bridge_file_status` itself still raises on unrecognized tokens (regression guard).
  5. `test_unreadable_or_duplicate_version_still_raises` — verifies that genuinely unreadable or duplicate version files still raise `WorkIntentRegistryError` (failures stay loud).
- Formatted the file using Ruff.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — The numbered bridge chain is the authoritative workflow surface and is append-only; the registry must handle legacy status tokens as drift rather than blocking transition.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Specification linkage is required.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Metadata headers.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Spec-derived verification plan.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — Preserves artifact lifecycle by allowing legacy-shadowed threads to transition to WITHDRAWN.

## Prior Deliberations

- `bridge/gtkb-work-intent-registry-tolerates-legacy-status-002.md` — LO GO verdict.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — Status token standards.
- `DELIB-20265457` — Owner batch authorization.

## Spec-Derived Verification Plan (executed)

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py -v --tb=short
  => 16 passed in 5.07s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
  => All checks passed!

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_bridge_work_intent_registry.py
  => 2 files already formatted
```

## Spec-to-Test Mapping

| Spec clause | Derived test | Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (claimable with legacy token) | `test_acquire_tolerates_legacy_status_shadowed_thread` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (latest status skips legacy) | `test_latest_status_skips_legacy_token_version` | PASS |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (non-silent skip warning) | `test_legacy_token_version_skip_emits_warning` | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (typed-raise contract preserved) | `test_bridge_file_status_still_raises_on_unrecognized_token_regression` | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (transient errors stay loud) | `test_unreadable_or_duplicate_version_still_raises` | PASS |

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
