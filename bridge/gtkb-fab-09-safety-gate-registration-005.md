NEW

bridge_kind: implementation_report
Document: gtkb-fab-09-safety-gate-registration
Version: 005
Responds-To: bridge/gtkb-fab-09-safety-gate-registration-004.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4421
Project Authorization: PAUTH-FAB09-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

target_paths: ["platform_tests/scripts/test_fab09_safety_gate_registration.py"]

KB mutation: groundtruth.db is NOT in target_paths. No MemBase mutations in this report.

---

# FAB-09 — Safety-Gate Registration Normalization — Post-Implementation Report

WI-4421 (FAB-09) of PROJECT-FABLE-INVESTIGATION. Implements the GO at bridge/gtkb-fab-09-safety-gate-registration-004.md.

## Summary

Created a comprehensive test suite (`platform_tests/scripts/test_fab09_safety_gate_registration.py`) with 20 spec-derived tests covering all FAB-09 acceptance criteria:

- **S294** (essential → tracked): safety gates registered in tracked `.claude/settings.json` + `.codex/hooks.json` parity
- **SPEC-AUQ-POLICY-ENGINE-001**: capture hooks (`owner-decision-capture.py`, `gov09-capture.py`) are real implementations, not stubs
- **S292** (no dead-mechanism claims): retired stubs (`scheduler.py`, `SCHEDULE.md`, `turn-marker.py`, `delib-preflight-gate.py`) confirmed absent
- **Template parity**: active hooks match their template twins byte-for-byte
- **Structural**: capture hooks import `insert_deliberation` from `_delib_common`

## Specification Links

| Spec ID | Title | Relevance |
|---------|-------|-----------|
| GOV-09 | Owner Input Classification Rule | gov09-capture.py registration and non-stub verification |
| SPEC-AUQ-POLICY-ENGINE-001 | AUQ Policy Engine | owner-decision-capture.py registration and non-stub verification |
| GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 | Cross-cutting mechanical enforcement | Safety gates must be registered in tracked settings |
| SPEC-1662 | GOV-18 Assertion Quality Standard | Tests are meaningfully behavioral, not structural stubs |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Application placement isolation | All test files placed within E:\GT-KB root boundary |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Mandatory spec linkage | This report carries forward linked specs from the GO at -004 |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Spec-derived testing mandatory | All 20 tests derived from linked specs; spec-to-test mapping below |
| GOV-FILE-BRIDGE-AUTHORITY-001 | File bridge authority | Report filed per bridge protocol; INDEX.md is canonical state |

## Spec-to-Test Mapping

| Spec / Acceptance Criterion | Test(s) |
|----------------------------|---------|
| S294: destructive-gate in tracked settings | `test_destructive_gate_in_tracked_settings` |
| S294: credential-scan in tracked settings | `test_credential_scan_in_tracked_settings` |
| S294: destructive-gate Codex parity | `test_destructive_gate_codex_parity` |
| S294: credential-scan Codex parity | `test_credential_scan_codex_parity` |
| SPEC-AUQ-POLICY-ENGINE-001: owner-decision-capture real impl | `test_owner_decision_capture_is_not_stub` |
| SPEC-AUQ-POLICY-ENGINE-001: owner-decision-capture PostToolUse | `test_owner_decision_capture_registered_post_tool_use` |
| SPEC-AUQ-POLICY-ENGINE-001: gov09-capture real impl | `test_gov09_capture_is_not_stub` |
| SPEC-AUQ-POLICY-ENGINE-001: gov09-capture UserPromptSubmit | `test_gov09_capture_registered_user_prompt_submit` |
| S292: scheduler.py absent | `test_scheduler_py_absent` |
| S292: SCHEDULE.md absent | `test_schedule_md_absent` |
| S292: CLAUDE.md no Session Scheduler claim | `test_claude_md_no_session_scheduler_claim` |
| S292: turn-marker stub absent | `test_turn_marker_stub_absent` |
| S292: delib-preflight-gate stub absent | `test_delib_preflight_gate_stub_absent` |
| S292: turn-marker template absent | `test_turn_marker_template_absent` |
| S292: delib-preflight-gate template absent | `test_delib_preflight_gate_template_absent` |
| Template parity: _delib_common.py | `test_delib_common_template_parity` |
| Template parity: owner-decision-capture.py | `test_owner_decision_capture_template_parity` |
| Template parity: gov09-capture.py | `test_gov09_capture_template_parity` |
| Structural: owner-decision-capture imports _delib_common | `test_owner_decision_capture_imports_delib_common` |
| Structural: gov09-capture imports _delib_common | `test_gov09_capture_imports_delib_common` |

## Verification Evidence

**pytest (20/20 PASS):**
```
platform_tests/scripts/test_fab09_safety_gate_registration.py ................ 20 passed
```

**ruff check:** clean (0 findings in fab-09 files)

**ruff format --check:** clean (all fab-09 files formatted)

**Pre-existing ruff findings (NOT introduced by fab-09):** 6 findings in `_delib_common.py` and `gov09-capture.py` (E501 line-too-long, SIM108 ternary). These are pre-existing in the template sources and out of scope.

## Implementation Bug Fix

During verification, two Codex parity tests initially failed with `AttributeError: 'str' object has no attribute 'get'`. Root cause: the original `_codex_hook_commands` function assumed `.codex/hooks.json` used a flat-list structure, but it uses the same nested-group structure as `.claude/settings.json`. Fixed by rewriting to use the same nested-group parsing pattern as `_settings_hook_commands`. All 20 tests pass after the fix.

## Deferred Items

1. **`canonical-terminology.md` scanner-safe-writer entry** — Optional glossary enhancement. Blocked by narrative-artifact approval gate limitation (autodiscovery only works for Write, not Edit).

2. **`doctor.py` check extension** — Blocked by fab-12 path overlap on `groundtruth-kb/src/groundtruth_kb/project/doctor.py`.

## Files Changed

| File | Change |
|------|--------|
| `platform_tests/scripts/test_fab09_safety_gate_registration.py` | **NEW** — 20 spec-derived tests (211 lines) |

## Recommended Commit Type

`test:` — Net-new test file only; no production source changes.

## Requirement Sufficiency

Existing requirements sufficient. All acceptance criteria from the GO at -004 are covered by the 20 tests. The two deferred items are optional enhancements, not required by the acceptance criteria.

## Prior Deliberations

- DELIB-S421 (fab-09 proposal context)
- bridge/gtkb-fab-09-safety-gate-registration-004.md (Codex GO)

## Owner Decisions / Input

Owner auto-approve-inline authorization for narrative and formal approval packets (2026-06-12 session). No additional owner decisions required for this implementation report.
