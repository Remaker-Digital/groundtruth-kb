NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-07-08T00-43-00Z-prime-builder-A-a1b2c3
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access; implementation_authorization_packet=sha256:6069bbb8fff99c634a0ec7f9b4bcc098fab59360534aaca04d4110a88682d423

# GT-KB Bridge Implementation Report - gtkb-wi5066-dispatch-wrapper-commandline-redaction - 003

bridge_kind: implementation_report
Document: gtkb-wi5066-dispatch-wrapper-commandline-redaction
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-002.md
Approved proposal: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066
Implementation Authorization Packet: sha256:6069bbb8fff99c634a0ec7f9b4bcc098fab59360534aaca04d4110a88682d423
Recommended commit type: fix:

## Implementation Claim

Dispatcher-launched workers now use an environment-payload status-wrapper mode instead of exposing status sidecar paths, stdout/stderr paths, stdin path, lifetime, and child harness argv on the live run_with_status.py command line.

scripts/run_with_status.py preserves positional invocation and adds GTKB_RUN_WITH_STATUS_CONFIG_B64 plus --config-env for dispatcher launches. The wrapper validates decoded JSON, keeps positive lifetime validation, writes the same status sidecar, preserves hidden/no-window launch behavior, and removes the wrapper config env var before spawning the child process.

scripts/dispatcher_runtime.py now launches the status wrapper as pythonw run_with_status.py --config-env, stores wrapper inputs in GTKB_RUN_WITH_STATUS_CONFIG_B64, and records status_wrapper_config_mode: env. For in-root API harness scripts (scripts/ollama_harness.py and scripts/openrouter_harness.py), dispatcher child argv is converted to an opaque Python -c runner that reconstructs sys.argv from GTKB_API_HARNESS_RUNNER_CONFIG_B64, so the live child command line no longer exposes literal API harness script tokens.

No provider credentials, provider accounts, OpenRouter/Ollama model routes, Codex no-window guard state, watchdog/scheduled-task state, or broad dispatch selection policy were changed.

## Files Changed

- scripts/run_with_status.py
- scripts/dispatcher_runtime.py
- platform_tests/scripts/test_run_with_status.py
- platform_tests/scripts/test_dispatcher_runtime.py

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001
- GOV-RELIABILITY-FAST-LANE-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001
- SPEC-DISPATCHER-CONTROL-SURFACE-001
- DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001

## Specification-Derived Verification

| Spec / Gate | Evidence |
|-------------|----------|
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 | Dispatcher spawn tests assert run_with_status.py --config-env is the live wrapper command, decoded wrapper config carries status/stdout/stderr/lifetime/child argv, and API harness script targets use worker_command_mode: opaque_python_module. |
| SPEC-DISPATCHER-CONTROL-SURFACE-001 | Launch metadata now records status_wrapper_config_mode: env and worker_command_mode; timeout/lifetime telemetry tests still pass after moving wrapper config off argv. |
| DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001 | Existing no-window pythonw.exe wrapper test still verifies hidden Windows wrapper launch flags after the command-line shape changed. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Focused pytest coverage was added/updated for env-payload wrapper mode, missing-payload failure, API opaque-runner conversion, Antigravity stdin prompt preservation, lifetime propagation, and no-window wrapper invariants. |
| GOV-FILE-BRIDGE-AUTHORITY-001 / PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 | Source edits began only after GO at bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-002.md, Prime work-intent claim, and implementation-start packet sha256:6069bbb8fff99c634a0ec7f9b4bcc098fab59360534aaca04d4110a88682d423. |

## Verification Commands

- groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
  - Result: 181 passed, 1 warning (PytestConfigWarning: Unknown config option: asyncio_mode).
- groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py
  - Result: All checks passed.
- groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py
  - Result: 4 files already formatted.

## Bounded Live Dispatch Evidence

After the patch, a dry-run dispatcher tick reported lane health allow for both Prime Builder and Loyal Opposition. Codex/A remained Prime-selected but skipped with codex_dispatch_not_ready; OpenRouter/F and Ollama/D were LO-selected.

A live dispatcher tick at 2026-07-08T00:37:51Z launched OpenRouter/F dispatch 2026-07-08T00-37-52Z-loyal-opposition-F-ce4444 for gtkb-wi5070-dispatch-budget-model-setter and gtkb-wi5069-headless-lane-coverage-role-invariant. Its launch metadata recorded status_wrapper_config_mode: env, worker_command_mode: opaque_python_module, command_head [E:/GT-KB/groundtruth-kb/.venv/Scripts/python.exe, -c], worker_lifetime_seconds: 900, and stdout/stderr sidecars under .gtkb-state/bridge-poller/dispatch-runs/.

A second live tick launched OpenRouter/F dispatch 2026-07-08T00-38-19Z-loyal-opposition-F-f9f489 for gtkb-wi5069-headless-lane-coverage-role-invariant and gtkb-wi5068-no-action-scan-helper-parser. A two-minute follow-up count showed live_total=2, live_lo=2, live_pb=0, with both F workers still live and stdout/stderr sidecars present and empty while the model/tool loops were running.

Ollama/D remained LO-assigned and dispatchable, but did not launch in this bounded check: the first D tick hit the global spawn-rate limiter immediately after F launched, and the second D tick selected a document already leased by F, returning document_lease_held. This is a truthful residual scheduling blocker for proving D live execution, not a wrapper launch failure.

## Prior Deliberations

- bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md proposed the command-line redaction repair.
- bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-002.md gave OpenRouter/F GO with conditions to cite exact pytest/ruff results and live D/F dispatch evidence or a truthful residual blocker.

## Residual Risks / Follow-Up

- OpenRouter/F wrapper launch is repaired at the observed launch layer, but the two live F workers had not completed by the two-minute observation point. Their eventual verdict/exit status still needs normal dispatcher follow-up.
- Ollama/D still needs a clean live-launch proof after an unleased LO item is available or the scheduler skips F-held documents when choosing D work.
- Codex/A Prime Builder headless processing remains blocked by the existing codex_dispatch_not_ready / no-window sandbox-readiness issue; this implementation did not alter Codex readiness policy.
- WI-5064 OpenRouter SSL retry hardening remains separate and pending.

## Rollback

Remove CONFIG_ENV_VAR / --config-env parsing from scripts/run_with_status.py, restore dispatcher wrapper command construction to positional --stdout/--stderr/--stdin/--lifetime plus status path and child argv, remove the API opaque-runner conversion and launch metadata fields from scripts/dispatcher_runtime.py, and remove the added/updated tests. Bridge artifacts remain append-only.
