NEW

# GT-KB Bridge Implementation Report - gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation - 003

bridge_kind: implementation_report
Document: gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation
Version: 003
Author: Prime Builder / Codex Desktop
Date: 2026-06-28T21:35:48Z
Responds to GO: bridge/gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation-002.md
Approved proposal: bridge/gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation-001.md
Project Authorization: PAUTH-PROJECT-GTKB-AGENT-RED-READINESS-AGENT-RED-READINESS-PROGRAM-PHASE-1-ISOLATION-PARTITION-IN-PLACE
Project: PROJECT-GTKB-AGENT-RED-READINESS
Work Item: WI-4656
Recommended commit type: feat
Commit: 01bd7ecce (feat: activate work-subject write guard)

author_identity: Prime Builder / Codex Desktop
author_harness_id: A
author_session_context_id: 019f1009-abea-7db2-b7cd-78332c09b304
author_model: GPT-5 via Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop, Windows PowerShell, danger-full-access workspace, network enabled

## Implementation Claim

Implemented the Phase 1.3 work-subject write-guard activation for Agent Red Readiness.

- Registered `.claude/hooks/workstream-focus.py` on Claude write-capable `PreToolUse` paths.
- Registered `.codex/gtkb-hooks/workstream-focus.cmd` for Codex `apply_patch` while preserving the existing Codex `Bash` coverage.
- Added shared `apply_patch` target-header extraction in `scripts/workstream_focus.py` so Codex patch writes are evaluated against the same root-classification guard.
- Kept application-subject bridge allowance narrow: ordinary GT-KB source/config/rule changes remain blocked; only full-content numbered `ADVISORY` bridge writes through direct `Write` are allowed.
- Removed clean-adopter validation suppression of `isolation:no-writable-product-paths` required failures.
- Narrowed platform-only doctor checks so temporary clean-adopter roots are not falsely failed for missing GT-KB platform internals or Agent Red registry files while still surfacing product writability.
- Updated hook parity, direct guard, clean-adopter, and FAB-07 tests for the activated behavior and current wrapper-based Codex Stop hook registration.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - append-only bridge filing plus GO and implementation-start authorization before protected edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal and report must cite governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - bridge artifact must preserve project, work-item, and PAUTH linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must prove linked requirements through targeted tests.
- `ADR-CROSS-HARNESS-PARITY-001` - equivalent behavior across Claude and Codex harness surfaces.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - cross-harness disposition for `.claude` and `.codex` hook/config surfaces.
- `GOV-STANDING-BACKLOG-001` - MemBase backlog authority for WI-4656.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - guard and doctor decisions read live state and filesystem/config state.
- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` - platform sessions must not silently mutate application product files, and application sessions must not silently mutate GT-KB platform files.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` - `applications/Agent_Red/` is the application root protected by classification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - application placement boundary for root classification.
- `ADR-APPLICATION-ISOLATION-CONTRACT-001` - applications are isolated execution contexts with independent lifecycle authority.
- `DCL-APP-ROOT-MINIMIZATION-001` - downstream D-P1a context for bridge-allowed block-list policy.

## Prior Deliberations And Evidence

- `DELIB-20265219` - owner ratified the Agent Red Readiness program and Phase 1 focus.
- `DELIB-20265220` - owner approved materializing Phase 1 slices and D-P1a bridge-allowed semantics.
- `DELIB-20265227` - owner resolved Phase 1.1 governance foundation and placed write-guard enforcement in Phase 1.3.
- `bridge/gtkb-work-subject-root-enforcement-implementation-020.md` - VERIFIED the prior work-subject foundation.
- `bridge/gtkb-wi4690-application-work-subject-advisory-boundary-004.md` - verified advisory-boundary behavior.
- `bridge/gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation-002.md` - Loyal Opposition GO authorizing this implementation.
- Implementation-start packet hash: `sha256:57aa97474485a820701aba1bcf224d6c8cd605b62a2d958fb80dc180d6dc6f4a`.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-APPLICATION-ISOLATION-CONTRACT-001`, `GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` | `platform_tests/hooks/test_workstream_focus.py` passed in the focused hook lane, including direct `apply_patch`, GT-KB product, current-repo governance, bridge advisory, and application-product guard cases. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `platform_tests/scripts/test_workstream_focus_hook_parity.py`, `platform_tests/scripts/test_check_codex_hook_parity.py`, `platform_tests/scripts/test_codex_hook_parity.py`, and `scripts/check_codex_hook_parity.py --project-root .` all passed. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Hook tests create fresh work-subject state and assert the guard reads that state at execution time; clean-adopter and FAB-07 tests exercise live filesystem/config behavior. |
| `DCL-APP-ROOT-MINIMIZATION-001` | Doctor clean-adopter tests verify platform-only Agent Red app-root minimization is skipped outside the GT-KB platform workspace instead of creating false adopter failures. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest lanes passed: 92 passed/3 skipped and 39 passed. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `GOV-STANDING-BACKLOG-001` | Implementation authorization validation passed for changed targets; bridge applicability preflight passed with no missing required specs; ADR/DCL clause preflight passed with zero blocking gaps. |

## Commands Run

```text
python scripts\implementation_authorization.py validate --target .claude/settings.json --target .codex/hooks.json --target scripts/workstream_focus.py --target scripts/check_codex_hook_parity.py --target scripts/clean_adopter_validation.py --target groundtruth-kb/src/groundtruth_kb/project/doctor.py --target platform_tests/hooks/test_workstream_focus.py --target platform_tests/scripts/test_workstream_focus_hook_parity.py --target platform_tests/scripts/test_codex_hook_parity.py --target platform_tests/scripts/test_fab07_doctor_false_signals.py --target groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\hooks\test_workstream_focus.py platform_tests\scripts\test_workstream_focus_hook_parity.py platform_tests\scripts\test_check_codex_hook_parity.py platform_tests\scripts\test_codex_hook_parity.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_doctor_isolation.py groundtruth-kb\tests\adopter\test_clean_adopter_packaging.py platform_tests\scripts\test_fab07_doctor_false_signals.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe scripts\check_codex_hook_parity.py --project-root .
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/workstream_focus.py scripts/check_codex_hook_parity.py scripts/clean_adopter_validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_fab07_doctor_false_signals.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/workstream_focus.py scripts/check_codex_hook_parity.py scripts/clean_adopter_validation.py groundtruth-kb/src/groundtruth_kb/project/doctor.py groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py platform_tests/hooks/test_workstream_focus.py platform_tests/scripts/test_workstream_focus_hook_parity.py platform_tests/scripts/test_check_codex_hook_parity.py platform_tests/scripts/test_codex_hook_parity.py platform_tests/scripts/test_fab07_doctor_false_signals.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation
git commit -m "feat: activate work-subject write guard"
```

## Observed Results

- Implementation authorization validation: `authorized: true` for all changed protected targets.
- Hook pytest lane: `92 passed, 3 skipped`.
- Doctor/clean-adopter/FAB-07 pytest lane: `39 passed`.
- `scripts/check_codex_hook_parity.py --project-root .`: `Codex hook parity: PASS`.
- Ruff check: `All checks passed!`.
- Ruff format check: `12 files already formatted`.
- Bridge applicability preflight: `preflight_passed: true`; `missing_required_specs: []`.
- ADR/DCL clause preflight: exit 0; blocking gaps 0.
- Commit hooks: credential scan found 0 potential secrets; inventory drift check PASS; protected-commit authorization PASS.

## Files Changed

- `.claude/settings.json`
- `.codex/hooks.json`
- `scripts/workstream_focus.py`
- `scripts/check_codex_hook_parity.py`
- `scripts/clean_adopter_validation.py`
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
- `platform_tests/hooks/test_workstream_focus.py`
- `platform_tests/scripts/test_workstream_focus_hook_parity.py`
- `platform_tests/scripts/test_codex_hook_parity.py`
- `platform_tests/scripts/test_fab07_doctor_false_signals.py`
- `groundtruth-kb/tests/adopter/test_clean_adopter_packaging.py`
- `bridge/gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation-001.md`
- `bridge/gtkb-ar-readiness-phase-1-3-work-subject-write-guard-activation-002.md`

## Acceptance Criteria Status

- [x] Application-subject sessions block GT-KB product/source/config/rule writes.
- [x] Application-subject bridge exception is limited to full-content numbered `ADVISORY` bridge writes.
- [x] GT-KB-subject sessions block application product writes.
- [x] Claude write-capable PreToolUse paths invoke the shared workstream-focus guard.
- [x] Codex `Bash` and `apply_patch` PreToolUse paths invoke the shared workstream-focus guard.
- [x] Clean-adopter validation no longer suppresses `isolation:no-writable-product-paths`.
- [x] Doctor clean-adopter false positives from platform-only checks were narrowed.
- [x] Focused parity, guard, doctor, clean-adopter, Ruff, and bridge preflight verification passed.

## Risk And Rollback

Risk is moderate because this activates a write-blocking guard on live hook paths. The highest-risk cases are false-positive write blocks from work-subject state or false-negative parsing of Codex patch payloads. Mitigation is focused direct guard coverage for direct writes, shell mutations, and `apply_patch`, plus cross-harness hook registration parity checks.

Rollback path is a single revert of commit `01bd7ecce`, preserving the append-only bridge files.

## Loyal Opposition Asks

1. Verify commit `01bd7ecce` against the approved proposal and linked specifications.
2. Confirm the activated Claude and Codex hook paths enforce equivalent work-subject boundaries.
3. Confirm clean-adopter validation no longer hides `isolation:no-writable-product-paths` while avoiding unrelated platform false positives.
4. Return `VERIFIED` if the implementation and evidence satisfy WI-4656; otherwise return `NO-GO` with concrete findings.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
