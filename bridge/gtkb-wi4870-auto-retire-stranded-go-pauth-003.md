NEW

# Implementation Report - WI-4870 Auto-Retire Stranded GO PAUTH

bridge_kind: implementation_report
Document: gtkb-wi4870-auto-retire-stranded-go-pauth
Version: 003
Date: 2026-07-07 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3170-d706-77d3-b3e1-be39d47f3eda
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: interactive Prime Builder session; Codex desktop execution

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4870

Responds to: bridge/gtkb-wi4870-auto-retire-stranded-go-pauth-002.md

## Implementation Claim

Implemented the conservative WI-4870 guard: project retirement and project-authorization completion now detect active PAUTH-backed bridge threads whose latest status is still implementation/review lifecycle work (`NEW`, `REVISED`, `GO`, or `NO-GO`) and keep the project active instead of completing/retiring it into an unstartable state.

The implementation remains fail-closed. It does not tolerate stale retired-project PAUTHs for ordinary source work; `implementation_authorization.py` still rejects a latest-GO thread whose PAUTH is attached to a retired project unless the PAUTH explicitly carries the existing `project_retirement_reconciliation` mutation class.

## Files Changed In This Scope

- `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` - added PAUTH/project metadata parsing for versioned bridge threads, `open_project_authorization_bridge_threads` readiness evidence, and explicit completion/retirement blockers for active PAUTH-backed nonterminal threads.
- `platform_tests/scripts/test_auto_retire_on_resolve.py` - added a resolve-path regression proving member-WI auto-retirement skips a project with an open latest-`GO` PAUTH thread.
- `platform_tests/scripts/test_auto_retire_on_verified.py` - added a VERIFIED-sweep regression proving project auto-retirement skips the same open-PAUTH condition.
- `platform_tests/scripts/test_project_authorization.py` - added an explicit project-authorization completion regression proving completion refuses while a PAUTH-backed latest-`GO` thread is open.
- `platform_tests/scripts/test_implementation_authorization.py` - added a WI-4870 fail-closed regression proving an otherwise valid latest-`GO` PAUTH becomes unstartable if its project is retired.

The worktree also contains pre-existing project-completion scanner/keep-open edits in `scripts/project_verified_completion_scanner.py` and `platform_tests/scripts/test_project_verified_completion_scanner.py`; they were included in verification commands for compatibility, but this report's implementation claim is limited to the WI-4870 guard above.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - latest `GO`, work-intent claim, implementation-start packet, and this numbered report preserve the bridge lifecycle.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation is covered by the active Phase 2 PAUTH for WI-4870.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - PAUTH did not bypass bridge `GO` or implementation-start authorization.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - report retains PAUTH, project, and work-item metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - report carries forward the governing specifications from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - tests below map the implementation to the proposal's verification requirements.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - headless Prime workers now encounter a deterministic active-project guard rather than a later hidden implementation-start dead end.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher routing is protected from receiving latest-`GO` work whose PAUTH was stranded by project retirement.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation and tests remained under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI, PAUTH, bridge, tests, and report remain traceable lifecycle artifacts.

## Spec-To-Test Mapping

| Governing surface | Verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Latest status was `GO`; claim `gtkb-wi4870-auto-retire-stranded-go-pauth` was held by this session; implementation-start packet existed at `.gtkb-state/implementation-authorizations/current.json` for this bridge with expiry `2026-07-07T20:44:17Z`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/implementation_authorization.py validate --target ...` succeeded for the edited lifecycle and test paths before mutation. |
| Auto-retirement must not strand active GO work | `test_resolve_does_not_retire_with_open_project_authorization_go_thread` and `test_auto_retire_skips_open_project_authorization_go_thread` prove resolve-path and VERIFIED-sweep retirement skip active latest-`GO` PAUTH threads. |
| Authorization completion must not retire a project with active PAUTH work | `test_complete_authorization_withheld_when_project_authorization_thread_open` proves explicit authorization completion raises before completing/retiring when a PAUTH-backed latest-`GO` thread remains open. |
| Implementation-start remains fail-closed for stale retired-project PAUTHs | `test_wi4870_retired_project_stranded_go_pauth_fails_closed` proves a latest-`GO` PAUTH attached to a retired project still fails with `not attached to an active project`. |
| Existing project lifecycle behavior remains intact | Full project authorization, projects CLI, scanner, auto-retire, ruff, applicability, and clause-preflight commands below passed. |

## Commands And Results

```text
python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4870-auto-retire-stranded-go-pauth --expires-minutes 120
Result: authorized; packet hash sha256:277840135c265af0281ff14f538902147396171ba0e4f9ab39dc217f94c9a649; expires 2026-07-07T20:44:17Z.

python scripts/implementation_authorization.py validate --target groundtruth-kb/src/groundtruth_kb/project/lifecycle.py
python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_auto_retire_on_resolve.py
python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_auto_retire_on_verified.py
python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_implementation_authorization.py
python scripts/implementation_authorization.py validate --target platform_tests/scripts/test_project_authorization.py
Result: authorized true for each target.

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_auto_retire_on_resolve.py platform_tests/scripts/test_auto_retire_on_verified.py -q --tb=short
Result: 15 passed, 2 warnings.

groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_verified_completion_scanner.py -q --tb=short
Result: 165 passed, 2 warnings.

groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_auto_retire_on_resolve.py platform_tests/scripts/test_auto_retire_on_verified.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_project_verified_completion_scanner.py scripts/project_verified_completion_scanner.py
Result: All checks passed.

groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_auto_retire_on_resolve.py platform_tests/scripts/test_auto_retire_on_verified.py platform_tests/scripts/test_project_authorization.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_project_verified_completion_scanner.py scripts/project_verified_completion_scanner.py
Result: 7 files already formatted.

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4870-auto-retire-stranded-go-pauth --json
Result: preflight_passed true; missing_required_specs []; missing_advisory_specs []; packet_hash sha256:5bf3227164054109a22ea627a96d2caba27d9443f1fd3be3ad7a087d262e44ab.

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4870-auto-retire-stranded-go-pauth
Result: exit 0; clauses evaluated 5; must_apply 3; blocking gaps 0.

gt bridge dispatch health --json
Result: health_status WARN. complex_lifecycle PASS/healthy; routing_config WARN due pre-existing loyal-opposition:D dispatch runtime failure max_turn_exhaustion.

gt bridge dispatch status --json
Result: health_status WARN with same pre-existing loyal-opposition:D max_turn_exhaustion finding; dispatcher selected-role/status data otherwise returned successfully.
```

## Acceptance Status

- Active latest-`GO` PAUTH-backed threads now block member-WI automatic retirement.
- Active latest-`GO` PAUTH-backed threads now block project authorization completion/retirement.
- Retired-project PAUTHs remain fail-closed for ordinary source work.
- Existing project authorization, projects CLI, scanner, and auto-retire test suites remain passing.
- Dispatcher health/status completed with a pre-existing WARN unrelated to this implementation.

## Risk / Rollback

Risk is that the guard is conservative and may keep a project active while a PAUTH-backed bridge thread remains in `NEW`, `REVISED`, `GO`, or `NO-GO`. That is intentional for WI-4870: an active project is safer than a retired project that strands implementable work. Rollback is to remove the PAUTH-backed bridge scan and its readiness checks from `ProjectLifecycleService`, then remove the added WI-4870 regressions.

## Recommended Commit Type

Recommended commit type: fix

fix
