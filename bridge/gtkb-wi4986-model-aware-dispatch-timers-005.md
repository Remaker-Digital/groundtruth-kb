NEW

# WI-4986 Model-Aware Dispatch Timers - Implementation Report

bridge_kind: implementation_report
Document: gtkb-wi4986-model-aware-dispatch-timers
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi4986-model-aware-dispatch-timers-004.md
Approved proposal: bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md
Recommended commit type: feat:
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-03T08:00:52Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive; ::init gtkb pb; ::open ops; model identity not otherwise exposed by harness

## Implementation Claim

Implemented model-aware headless worker timing in the dispatcher-owned launch path.

The dispatcher now resolves an explicit worker lifetime profile per dispatch target, with harness-scoped environment overrides first, harness defaults second, and the pre-existing role defaults as fallback. Current defaults are:

- Codex-A: 5400 seconds for Prime Builder implementation dispatch.
- Claude-B: 3600 seconds for Loyal Opposition review dispatch, preserving a generous Opus Max allowance.
- Ollama-D: 1800 seconds for Loyal Opposition DeepSeek dispatch.

`scripts/dispatcher_runtime.py` now passes the effective profile to `scripts/run_with_status.py` as `--lifetime <seconds>`, stamps the child environment with the effective lifetime/source/profile, records the same profile in `last_launch`, and carries lifetime/elapsed/timeout-source telemetry into dispatch-failure records. Document lease TTLs now derive from the same effective worker lifetime plus margin, so a slow but legitimate Claude-B review does not outlive its dispatcher lease.

The Ollama route remains explicitly pinned to `deepseek-v4-pro-cloud` / `deepseek-v4-pro:cloud`, and `.api-harness/routing.toml` raises `[routing.ollama].timeout_seconds` from 180 to 1800 so DeepSeek bridge reviews do not follow the prior 180s fast-fail path.

No live headless Claude, Ollama, or Codex worker was directly spawned from this PB session. All launch proof is through monkeypatched dispatcher-runtime tests, preserving the direct harness-to-harness launch prohibition.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - dispatcher remains the single launch and audit owner.
- `ADR-DISPATCHER-ARCHITECTURE-001` - implementation stays inside the dispatcher-owned spawn architecture.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch metadata now carries coherent lifetime profile, elapsed time, and timeout source.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - report is filed through the live versioned bridge thread.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - owner timer directives are preserved in WI-4986 and this report.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - proposal, GO, implementation, tests, and report remain linked.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-4986 remains the implementation successor for the superseded timer directive.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - implementation stays within the GO target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence below maps to the GO's explicit expectations.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization, Project, and WI linkage are inherited from the GO'd proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all changes are GT-KB platform dispatcher/config/test changes under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-4986 remains the tracked backlog vehicle.

## Owner Decisions / Input

No new owner decision is required. This implements the approved WI-4986 scope and the owner's directive to start with generous, per-harness/model/config allowances and collect data before declaring workers hung.

## Prior Deliberations

- `DELIB-202665303` - owner directive to use generous per-harness/model/config timer allowances and verify the value reaches the worker wrapper.
- `DELIB-20260703-DISPATCH-TIMER-GENEROUS-ALLOWANCES` - owner directive to start with generous allowances until enough data exists.
- `DELIB-20260703-DISPATCH-HUNG-CONFIDENCE-ANALYSIS` - owner directive to collect/analyze elapsed-time data before high-confidence hung classification.
- `bridge/gtkb-wi4986-model-aware-dispatch-timers-003.md` - approved revised implementation proposal.
- `bridge/gtkb-wi4986-model-aware-dispatch-timers-004.md` - Loyal Opposition GO verdict authorizing implementation.

## Specification-Derived Verification Plan

| GO expectation / governing surface | Executed verification evidence |
| --- | --- |
| Effective lifetime reaches `run_with_status.py` for Claude-B/Opus, Ollama-D/DeepSeek, and Codex-A/GPT. | `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short -k "lifetime or launch_path_drift or long_running_ollama_timeout"` passed. New `test_spawn_harness_passes_target_lifetime_to_status_wrapper` asserts `--lifetime` placement and values B=3600, D=1800, A=5400. |
| Missing lifetime / stale daemon / launch-path drift is surfaced. | Same focused dispatcher run passed. New `test_pending_exit_code_surfaces_missing_lifetime_as_launch_path_drift` asserts exit 124 without lifetime metadata records `timeout_source=run_with_status_default_or_launch_path_drift`. |
| Dispatch metadata carries profile and elapsed-time evidence. | Same focused dispatcher run passed. New `test_worker_lifetime_profile_prefers_harness_env_override` and `test_pending_exit_code_records_lifetime_and_elapsed_timeout_telemetry` assert env override, model hint, lease TTL, elapsed seconds, configured lifetime, and dispatch-failure telemetry. |
| Storm/lease/concurrency guards remain active while timers get longer. | Full dispatcher-runtime suite passed: `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` returned 167 passed, 1 skipped. Existing cap/lease/backoff tests remained green; new lease TTL assertion confirms lease duration follows effective worker lifetime plus margin. |
| Ollama route/session budget is no longer 180s fast-fail. | `.api-harness/routing.toml` now sets `[routing.ollama].timeout_seconds = 1800`. `python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short -k "deepseek_v4_pro_cloud_route"` passed, and `python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_ollama_routing_config.py -q --tb=short` returned 58 passed. |
| Code style and format remain clean for touched Python files. | `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py` passed. `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py` reported 3 files already formatted. |

## Commands Run

- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short -k "worker_lifetime_profile or target_lifetime or lifetime_and_elapsed or long_running_ollama_timeout"` - 6 passed.
- `python -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short -k "deepseek_v4_pro_cloud_route"` - 1 passed.
- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short -k "lifetime or launch_path_drift or long_running_ollama_timeout"` - 7 passed.
- `python -m ruff check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py` - all checks passed.
- `python -m ruff format --check scripts/dispatcher_runtime.py platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py` - 3 files already formatted.
- `python -m pytest platform_tests/scripts/test_dispatcher_runtime.py platform_tests/scripts/test_verify_ollama_dispatch.py -q --tb=short` - 167 passed, 1 skipped.
- `python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_ollama_routing_config.py -q --tb=short` - 58 passed.

## Observed Results

- Dispatcher wrapper tests prove the configured per-target lifetime is placed before the status-file argument and reaches `run_with_status.py`.
- Dispatcher child environment and `last_launch` metadata now expose lifetime seconds, source, profile, env var, role fallback, and optional model hint.
- Timeout failure records now include elapsed seconds and timeout source, distinguishing configured worker-lifetime expiry from missing lifetime metadata / stale launch path.
- Ollama DeepSeek routing remains explicit and now has a 30-minute route timeout.

## Files Changed

- `.api-harness/routing.toml`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`

## Rollback

Revert the four files above to restore role-only worker lifetime selection and the prior Ollama 180s route timeout. No database migration or external service change is required.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
