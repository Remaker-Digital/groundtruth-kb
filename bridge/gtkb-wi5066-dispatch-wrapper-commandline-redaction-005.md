REVISED

# GT-KB Bridge Revised Implementation Report - gtkb-wi5066-dispatch-wrapper-commandline-redaction - 005

bridge_kind: implementation_report
Document: gtkb-wi5066-dispatch-wrapper-commandline-redaction
Version: 005 (REVISED; responds to NO-GO -004)
Date: 2026-07-10 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4929-9343-7480-a8a0-055a97ab4b8a
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; ::init gtkb pb; approval_policy=never; NO-GO queue drive

Responds to: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-004.md
Prior implementation report: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-003.md
Approved proposal: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md
GO verdict: bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-002.md
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066
Recommended commit type: fix:

## Implementation Claim

The WI-5066 finalization scope is narrowed to the remaining uncommitted wrapper-side implementation and test delta:

- `scripts/run_with_status.py`
- `platform_tests/scripts/test_run_with_status.py`

The dispatcher-side opaque-runner support named in the prior report is already present in `HEAD` and is used here only as a verification surface, not as part of the requested WI-5066 finalization commit:

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

This split corrects the atomic-boundary defect from NO-GO -004. A VERIFIED finalization for this revised report should stage only the two remaining dirty WI-5066 paths above plus the Loyal Opposition verdict artifact. It should not stage `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, `groundtruth.db`, or `harness-state/harness-registry.json`.

## Finding Responses

### P1 - Atomic verified commit boundary was not isolated

Resolved by narrowing the claimed commit boundary. Live `git diff --name-only -- scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py` reports only:

```text
platform_tests/scripts/test_run_with_status.py
scripts/run_with_status.py
```

`scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py` are not dirty relative to `HEAD`. They are cited below because the focused tests exercise the current dispatch integration, but they are not part of the requested verified-path include set for this thread.

### P1 - Live evidence did not fully exercise each affected launch path

Resolved with executable evidence for both in-root API harness scripts, plus focused regression coverage.

Current `harness-state/harness-registry.json` still records Ollama/D headless argv as `groundtruth-kb/.venv/Scripts/python.exe scripts/ollama_harness.py ...`, so Ollama remains in scope. The dispatcher shared transform maps both API harness scripts:

- `scripts/ollama_harness.py` -> `scripts.ollama_harness`
- `scripts/openrouter_harness.py` -> `scripts.openrouter_harness`

Direct executable checks against `scripts.dispatcher_runtime._opaque_api_harness_command` produced:

```text
{"argv0": "scripts/ollama_harness.py", "command": ["groundtruth-kb/.venv/Scripts/python.exe", "-c", "import base64,json,os,runpy,sys;p=json.loads(base64.b64decode(os.environ.pop('GTKB_API_HARNESS_RUNNER_CONFIG_B64')).decode('utf-8'));sys.argv=p['argv'];runpy.run_module(p['module'],run_name='__main__')"], "exposes_ollama_script_on_command_line": false, "module": "scripts.ollama_harness", "payload_argv_len": 7}
{"argv0": "scripts/openrouter_harness.py", "command": ["groundtruth-kb/.venv/Scripts/python.exe", "-c", "import base64,json,os,runpy,sys;p=json.loads(base64.b64decode(os.environ.pop('GTKB_API_HARNESS_RUNNER_CONFIG_B64')).decode('utf-8'));sys.argv=p['argv'];runpy.run_module(p['module'],run_name='__main__')"], "exposes_openrouter_script_on_command_line": false, "module": "scripts.openrouter_harness", "payload_argv_len": 7}
```

The focused dispatcher regression `test_spawn_harness_uses_env_payload_and_opaque_runner_for_api_harness_scripts` exercises the launch metadata, wrapper `--config-env` shape, absence of `dispatch-runs` on live wrapper/child command lines, and opaque runner payload for the in-root API harness script path. The direct executable check above covers the sibling Ollama mapping that shares the same implementation path.

### P2 - Reviewer test reproduction was blocked by headless temp setup

Resolved by rerunning with an explicit root-contained pytest basetemp:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp/wi5066-report
```

Observed result: `182 passed, 1 warning in 22.05s`. The warning is the existing `PytestConfigWarning: Unknown config option: asyncio_mode`.

## Files Changed

Finalization include set requested for WI-5066:

- `scripts/run_with_status.py`
- `platform_tests/scripts/test_run_with_status.py`

Verification-only HEAD surfaces:

- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`

## Specification-Derived Verification

| Spec / Gate | Evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Focused dispatcher tests confirm current `HEAD` dispatch construction launches `run_with_status.py --config-env` and records env-mode metadata. Direct executable checks prove both Ollama and OpenRouter in-root harness scripts are transformed to `python -c` opaque runners without script-path exposure on the live command line. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `platform_tests/scripts/test_run_with_status.py` verifies env-payload wrapper mode, required-payload failure, status sidecar behavior, timeout/lifetime behavior, and backward-compatible positional mode. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | `platform_tests/scripts/test_dispatcher_runtime.py` verifies hidden/no-window wrapper construction still uses `pythonw.exe` and Windows creation/startup flags while the wrapper argv is reduced to `--config-env`. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Wrapper config env is removed before child spawn; tests assert the child env omits `GTKB_RUN_WITH_STATUS_CONFIG_B64`. The API-harness runner payload is popped by the runner code before module execution. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff lint, and ruff format gates ran against the changed wrapper files and the dispatcher verification surfaces. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | The original implementation was performed under GO -002 and implementation-start packet `sha256:6069bbb8fff99c634a0ec7f9b4bcc098fab59360534aaca04d4110a88682d423`; this revision does not add new protected source edits beyond documenting and retesting the existing implementation. |

## Verification Commands

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --basetemp .harness-tmp/wi5066-report
```

Observed result: `182 passed, 1 warning in 22.05s`.

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py
```

Observed result: `4 files already formatted`.

```text
groundtruth-kb/.venv/Scripts/python.exe -c "<direct _opaque_api_harness_command check for scripts/ollama_harness.py>"
groundtruth-kb/.venv/Scripts/python.exe -c "<direct _opaque_api_harness_command check for scripts/openrouter_harness.py>"
```

Observed result: both commands returned `exposes_*_script_on_command_line: false` and the expected module names.

## Prior Deliberations

- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md` proposed command-line redaction for dispatcher-launched OpenRouter/F and Ollama/D workers.
- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-002.md` recorded GO with conditions to cite exact pytest/ruff results and live or truthful residual evidence.
- `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-004.md` rejected the prior report because the finalization boundary was not isolated, Ollama evidence was incomplete, and reviewer pytest needed a root-contained temp path.

## Owner Decisions / Input

- The owner directed this Prime Builder session to auto-process PB-actionable bridge items and conclude the NO-GO queue drive.
- The active project authorization remains `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for `PROJECT-GTKB-RELIABILITY-FIXES` / `WI-5066`.
- No credential rotation, provider-account change, production deployment, force-push, visible-window fallback, or Codex no-window guard change is requested by this revised report.

## Acceptance Status

- Dispatcher wrapper command-line sidecar exposure: satisfied by current dispatcher tests and env-payload wrapper mode.
- API harness script command-line exposure: satisfied for both OpenRouter and Ollama by the shared transform evidence above; OpenRouter also has full dispatcher spawn test coverage.
- Positional wrapper compatibility: satisfied by existing wrapper tests.
- Hidden/no-window wrapper behavior: satisfied by dispatcher no-window tests.
- Root-contained test reproduction: satisfied with `--basetemp .harness-tmp/wi5066-report`.
- Atomic finalization boundary: satisfied by narrowing the requested include set to `scripts/run_with_status.py` and `platform_tests/scripts/test_run_with_status.py`.

## Residual Risks / Rollback

Residual risk: the dispatcher-side integration is already in `HEAD` through overlapping work, so this WI-5066 finalization only commits the remaining wrapper-side delta. Mitigation: this report cites dispatcher-side checks as verification evidence but excludes those files from the requested commit boundary.

Rollback for this finalization scope: remove CONFIG_ENV_VAR / `--config-env` parsing from `scripts/run_with_status.py`, restore the prior positional-only wrapper parsing behavior, and remove the env-payload wrapper tests from `platform_tests/scripts/test_run_with_status.py`. Do not alter dispatcher selection policy, provider credentials, Codex readiness, `groundtruth.db`, or generated harness registry projection as part of this rollback.
