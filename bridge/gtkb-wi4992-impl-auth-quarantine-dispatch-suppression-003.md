NEW

# WI-4992 Impl-Auth Quarantine Dispatch Suppression Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4992-impl-auth-quarantine-dispatch-suppression
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4992-impl-auth-quarantine-dispatch-suppression-002.md (GO)

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T12-19-35Z-prime-builder-A-a58969
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless auto-dispatch; Extra High reasoning; workspace-write; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4992-IMPL-AUTH-QUARANTINE
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4992

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

---

## Implementation Summary

Implemented deterministic impl-auth quarantine suppression for Prime Builder dispatch:

- `scripts/dispatcher_runtime.py` now treats `impl_auth_quarantined` and `all_impl_auth_quarantined` as expected suppressions, routing the individual impl-auth quarantine audit rows to `dispatch-suppressions.jsonl` instead of the actionable failure log.
- `scripts/gtkb_dispatcher_daemon.py` now records per-document impl-auth quarantine signatures for Prime Builder work. The same GO top-file signature is suppressed on later daemon ticks instead of repeatedly invoking `_spawn_harness`; a revised top file changes the signature and re-enables evaluation.
- `scripts/gtkb_dispatcher_daemon.py` still allows implementable Prime Builder documents in the same selection to dispatch when a sibling document is deterministically impl-auth quarantined.
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py` classifies `all_impl_auth_quarantined` as deterministic non-work and ignores stale subprocess failure fields for that current non-launch state.

The implementation chose the mechanism requested in the GO note N2: a non-dispatchable-until-revised suppression keyed to the deterministic impl-auth quarantine reason and the bridge document's current signature. It is re-evaluated automatically when the latest bridge version changes because the top-file signature changes.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatch must suppress deterministic non-work loops and avoid repeatedly offering work that cannot start.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher runtime remains the governed control plane; no direct harness workaround was added.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - live bridge status and requirement sufficiency continue to control what Prime Builder may implement.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation authorization refusals remain authoritative and are not bypassed.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries PAUTH/project/WI metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries concrete links to relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification mapping and executed evidence are included below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - deterministic quarantine state is preserved as dispatcher state and bridge evidence rather than hidden as runtime noise.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - impl-auth quarantine becomes visible lifecycle/reporting state until revised.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the report preserves the defect, implementation choice, and verification evidence in governed artifacts.

## Spec-To-Test Mapping

| Specification / Requirement | Implementation Evidence | Executed Verification |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Daemon suppresses repeated `all_impl_auth_quarantined` attempts and still dispatches an implementable sibling document. | `test_wi4992_daemon_all_impl_auth_quarantine_suppresses_until_signature_changes`; `test_wi4992_daemon_impl_auth_quarantine_does_not_block_implementable_document`; focused pytest command below. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Suppression is inside `gtkb_dispatcher_daemon.py` and `_spawn_harness`; no direct harness launch path was introduced. | Existing daemon/runtime tests plus focused pytest command below. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Suppression is keyed to the current top-file signature, so a revised bridge version re-enters evaluation. | `test_wi4992_daemon_all_impl_auth_quarantine_suppresses_until_signature_changes`. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | `_issue_dispatch_authorization_for_selected` remains the source of impl-auth refusal; no bypass path was added. | Updated `test_prime_spawn_fails_closed_when_dispatch_authorization_fails`; `test_issue_dispatch_auth_quarantines_bad_go_and_continues_healthy`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | PAUTH/project/WI metadata and spec links are present in this report. | This report plus helper filing validation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All linked requirements map to focused pytest, lint, and format evidence. | Commands below. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Suppression is visible in dispatch state/reporting and expected suppression logs. | `test_wi4992_all_impl_auth_quarantine_ignores_stale_failure_class`; updated suppression-log assertions. |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests\scripts\test_gtkb_dispatcher_daemon.py platform_tests\scripts\test_dispatcher_runtime.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py platform_tests\scripts\test_perrole_concurrency_cap_dispatch.py platform_tests\scripts\test_bridge_dispatch_config.py -q --tb=short --basetemp .gtkb-state\pytest-tmp
```

Observed result: `262 passed, 2 warnings in 54.87s`. Warnings were existing pytest config/cache warnings: unknown `asyncio_mode` option and `.pytest_cache` write contention.

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py scripts/bridge_dispatch_concurrency.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/dispatcher_runtime.py scripts/gtkb_dispatcher_daemon.py scripts/bridge_dispatch_concurrency.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
```

Observed result: `9 files already formatted`.

Note: an earlier pytest invocation without `--basetemp` failed before test execution because pytest attempted to scan `C:\Users\micha\AppData\Local\Temp\pytest-of-micha`, which was inaccessible in this sandbox. The successful run above uses a workspace-local basetemp.

## Files Changed For This Work Item

- `scripts/dispatcher_runtime.py`
- `scripts/gtkb_dispatcher_daemon.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

Workspace note: unrelated pre-existing dirty files were present before this auto-dispatch. This report claims only the scoped WI-4992 changes above.

## Acceptance Criteria Status

- A GO proposal whose Requirement Sufficiency requires new/revised requirements is no longer repeatedly dispatched to PB implementation: satisfied by per-document quarantine signatures.
- The implementation authorization gate still denies protected mutation for that proposal class: satisfied; the gate remains the refusal source.
- Implementable PB items in the same selection can still proceed: satisfied by mixed daemon test.
- Dispatch health no longer reports Prime Builder subprocess failure solely because all selected items were deterministically impl-auth quarantined before worker launch: satisfied by bridge dispatch config classifier test.
- Operators can see the quarantined slug/reason in dispatcher state or health/report output: satisfied through fan-out result counters, `impl_auth_quarantined_signatures_by_document`, and suppression logs.
- Focused pytest, ruff check, and ruff format-check commands pass: satisfied.

## Risks / Rollback

Risk: suppressing a GO item too broadly could hide later implementability. Mitigation: suppression is keyed to the top-file signature, so any revised bridge version changes the signature and re-enters evaluation.

Rollback: revert the WI-4992 edits in `scripts/dispatcher_runtime.py`, `scripts/gtkb_dispatcher_daemon.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, and associated focused tests. Bridge files remain append-only.

## Recommended Commit Type

Recommended commit type: `fix`

