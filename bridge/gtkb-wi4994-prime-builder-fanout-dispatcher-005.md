NEW

# WI-4994 Prime Builder Fan-Out Dispatcher Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4994-prime-builder-fanout-dispatcher
Version: 005
Author: Prime Builder (Codex, harness A)
Date: 2026-07-03 UTC
Responds to: bridge/gtkb-wi4994-prime-builder-fanout-dispatcher-004.md (GO)

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T12-19-35Z-prime-builder-A-a58969
author_model: gpt-5.5
author_model_version: 5.5
author_model_configuration: Codex headless auto-dispatch; Extra High reasoning; workspace-write; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-4994-PB-FANOUT
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-4994

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/bridge_dispatch_concurrency.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py"]

---

## Implementation Summary

Implemented dispatcher-managed Prime Builder fan-out for daemon-owned live dispatch:

- `scripts/gtkb_dispatcher_daemon.py` now splits Prime Builder selections into one-document sub-batches during decision construction. Loyal Opposition batching is unchanged.
- Each PB sub-batch receives its own dispatch id and work-intent session id in the live-spawn path.
- Per-document dispatch signatures are tracked in `last_dispatched_signatures_by_document`, so duplicate dispatch is suppressed for the same document without blocking a different unheld document.
- Per-document impl-auth quarantine signatures are tracked in `impl_auth_quarantined_signatures_by_document`, so deterministic non-work suppression does not block other PB work.
- Fan-out outcomes are summarized in recipient state with `fanout_results`, `fanout_launched_count`, `fanout_skipped_held_count`, `fanout_skipped_duplicate_count`, `fanout_impl_auth_quarantined_count`, and `fanout_at_cap_count`.
- `_spawn_harness` remains the final hard authority for global and per-role concurrency caps. No direct harness-to-harness launch path was added.
- `scripts/bridge_dispatch_concurrency.py` received a mechanical Python 3.14 `UTC` alias cleanup required by the focused ruff check; no live cap authority was moved into that helper.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stable unattended dispatcher processing must handle multiple independent PB items when capacity is available.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatch remains inside the dispatcher control plane.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - role-correct bridge state and work-intent discipline are preserved for implementation/report transitions.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start authorization remains required for PB GO work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this report carries PAUTH/project/WI metadata and target paths.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries concrete links to relevant governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification mapping and executed evidence are included below.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - spawned PB workers retain the existing dispatch prompt/envelope and headless invocation path.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - live defect, rejected alternatives, and implementation evidence are preserved in bridge artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - owner direction and live dispatcher defect are preserved as governed lifecycle artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the work remains inside governed WI, PAUTH, bridge, and verification records.

## Spec-To-Test Mapping

| Specification / Requirement | Implementation Evidence | Executed Verification |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Daemon decisions split PB work into one-document fan-out batches; two independent unheld PB documents can launch in one tick. | `test_wi4994_daemon_prime_fanout_launches_independent_documents`; focused pytest command below. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `DCL-DISPATCH-ENVELOPE-RULES-001` | All fan-out workers still route through `_spawn_harness`; no direct launcher was added. | Fan-out tests monkeypatch `_spawn_harness` as the only spawn seam; existing dispatcher-mediated Codex exec test still passes. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Each PB sub-batch checks work-intent state independently; held documents do not block later unheld documents. | `test_wi4994_daemon_prime_fanout_held_document_does_not_block_later_unheld`; focused pytest command below. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | PB GO work still reaches `_issue_dispatch_authorization_for_selected` through `_spawn_harness`; deterministic auth quarantine does not bypass the gate. | `test_wi4992_daemon_all_impl_auth_quarantine_suppresses_until_signature_changes`; `test_prime_spawn_fails_closed_when_dispatch_authorization_fails`. |
| Same-document dedupe and different-document independence | Per-document signature maps suppress duplicate dispatch for the same document but allow a different document. | `test_wi4994_daemon_prime_fanout_dedupes_same_document_not_different_document`. |
| Role-cap and TOCTOU protection | `_spawn_harness` remains the cap authority per call; fan-out records at-cap outcomes without treating them as launches. | `test_wi4994_daemon_prime_fanout_records_at_cap_per_spawn_attempt`; existing per-role cap tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` / `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | PAUTH/project/WI metadata and spec links are present in this report. | This report plus helper filing validation. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | All linked requirements map to focused pytest, lint, and format evidence. | Commands below. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Fan-out decisions, suppressed/held/at-cap outcomes, and verification evidence are durable bridge/report state. | New daemon fan-out tests and this report. |

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

- `scripts/gtkb_dispatcher_daemon.py`
- `scripts/bridge_dispatch_concurrency.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`

Shared support changes with WI-4992 in the same dispatch:

- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`

Workspace note: unrelated pre-existing dirty files were present before this auto-dispatch. This report claims only the scoped WI-4994 changes and shared support changes above.

## Acceptance Criteria Status

- Two independent unheld PB bridge documents can produce two `_spawn_harness` attempts in one daemon tick when PB capacity is available: satisfied.
- Each worker sub-batch contains one bridge document and has a distinct work-intent session id: satisfied.
- Held PB work-intent items remain excluded and do not block later independent unheld candidates: satisfied.
- Same-document signature dedupe suppresses duplicate dispatch while a different unheld document is not suppressed: satisfied.
- Multiple PB workers are bounded by existing role-aware cap and global guards: satisfied; `_spawn_harness` remains the hard cap authority and at-cap outcomes are recorded per sub-batch.
- Dispatcher state/reporting distinguishes launched, held, duplicate, impl-auth quarantined, and at-cap PB fan-out outcomes: satisfied.
- No direct harness-to-harness launch path was added: satisfied.
- Focused pytest, ruff check, and ruff format-check commands pass: satisfied.

## Risks / Rollback

Risk: fan-out could duplicate the same document. Mitigation: per-document work-intent checks and per-document signature maps.

Risk: fan-out could overrun capacity. Mitigation: `_spawn_harness` remains the final cap authority for every sub-batch.

Risk: the `bridge_dispatch_concurrency.py` formatting/UTC cleanup creates a large mechanical diff. Mitigation: it is behavior-preserving and was required to make the approved ruff check pass on an authorized target file.

Rollback: revert the WI-4994 edits in `scripts/gtkb_dispatcher_daemon.py`, the mechanical `scripts/bridge_dispatch_concurrency.py` cleanup, and associated focused tests. Bridge files remain append-only.

## Recommended Commit Type

Recommended commit type: `feat`

