NEW

# gtkb-wi4896-ollama-readiness-console-residual - Headless readiness and worker Python launch

bridge_kind: prime_proposal
Document: gtkb-wi4896-ollama-readiness-console-residual
Version: 001
Author: Prime Builder Codex
Date: 2026-06-27T21:35:00Z

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c3-be81-7771-8200-e81c58e3ae1e
author_model: GPT-5
author_model_version: 2026-06-27
author_model_configuration: Codex desktop; danger-full-access; approval-policy never; interactive role Prime Builder

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Related Work Item: WI-4896

target_paths: ["scripts/verify_ollama_dispatch.py", "platform_tests/scripts/test_verify_ollama_dispatch.py", "scripts/run_with_status.py", "platform_tests/scripts/test_run_with_status.py", "scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

implementation_scope: source,test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Claim

The minute-cadence Windows console and keyboard focus steal stopped when `GTKB-DispatcherDaemon` and `GTKB-HarnessStormWatchdog` were disabled and the live dispatcher daemon process was stopped. Dispatcher topology did not change: Codex and Cursor remain dispatchable Prime Builders, Claude Code remains suspended/non-dispatchable, and the dispatcher health warning is still the pre-existing OpenRouter Loyal Opposition backoff.

Follow-up inspection found two remaining daemon/dispatch paths outside the prior GO target set:

1. `scripts/verify_ollama_dispatch.py::evaluate_ollama_autostart` launches PowerShell on Windows without `-NonInteractive`, `stdin=subprocess.DEVNULL`, or `CREATE_NO_WINDOW`. The dispatcher daemon calls this path through `cross_harness_bridge_trigger._evaluate_harness_dispatch_readiness("ollama", ...)` when evaluating active Loyal Opposition target D. Because the daemon runs from a hidden `pythonw.exe` scheduled task, that child PowerShell process can allocate a visible console once per daemon interval.
2. Codex PostToolUse auto-dispatch launched `run_with_status.py -> ollama_harness.py` and `run_with_status.py -> openrouter_harness.py` workers after a draft-file write. The visible persistent terminal stopped only after the worker tree was forcibly closed/killed. The harness registry still legitimately records D/F/E headless surfaces with `groundtruth-kb/.venv/Scripts/python.exe`; however, for Windows headless dispatch with stdout/stderr redirected to log files, the dispatch wrapper should normalize Python console-subsystem executables to sibling `pythonw.exe` where available.

This proposal closes those residuals only. It does not change dispatcher topology, target selection, registry eligibility, Ollama routing, OpenRouter behavior, scheduled-task registration, credentials, deployment, database schema, or any bridge state beyond this proposal.

## Runtime Safety Brake Already Applied

- `GTKB-DispatcherDaemon`: disabled and stopped after the console recurrence.
- `GTKB-HarnessStormWatchdog`: disabled after the console recurrence.
- `GTKB-DbSnapshot`: left enabled because it is daily, hidden, uses `pythonw.exe`, and manually returned `LastTaskResult = 0`.

The disabled daemon/watchdog tasks should remain disabled until this residual probe fix receives GO, is implemented, and passes runtime observation across at least one minute-cadence boundary.

## Defect Evidence

- The latest filed implementation report for `gtkb-wi4896-startup-console-residual` covered `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, `scripts/gtkb_dispatcher_daemon.py`, the storm-watchdog launcher, and the DB snapshot installer.
- The dispatcher daemon's Ollama dispatch-readiness path does not call `groundtruth_kb.project.doctor._ollama_windows_autostart_finding`; it imports `scripts/verify_ollama_dispatch.py` and calls `evaluate_dispatch_readiness`.
- `evaluate_dispatch_readiness` calls `evaluate_ollama_autostart`, whose Windows PowerShell runner currently uses `[powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]` and `subprocess.run(...)` without null stdin or Windows no-window creation flags.
- That code path is reachable on every daemon live tick when Loyal Opposition target D is evaluated.
- The persistent blank window reported after this draft began was traced to active dispatch worker processes: `run_with_status.py` wrapping `scripts/ollama_harness.py` and `scripts/openrouter_harness.py`, with `conhost.exe` children. Killing the worker tree removed the visible/persistent window from the process table.
- The current harness registry headless surfaces for D/F/E intentionally use `groundtruth-kb/.venv/Scripts/python.exe`; the fix should not hand-edit registry projection data. The wrapper layer should choose `pythonw.exe` on Windows when available and when output is already file/DEVNULL redirected.

## In-Root Placement Evidence

All proposed source and test targets are in-root relative paths:

- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `scripts/run_with_status.py`
- `platform_tests/scripts/test_run_with_status.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Specification Links

- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Requires Windows dispatcher/background paths to run non-interactively without visible console windows; this fix applies the requirement to the daemon's Ollama dispatch-readiness PowerShell probe and to dispatched Python worker chains.
- `ADR-DISPATCHER-ARCHITECTURE-001` - The dispatcher daemon is the active black-box dispatch substrate; readiness probes called by daemon ticks are daemon-owned background behavior and must not surface UI.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - Dispatch readiness work and headless worker execution are centralized service behavior and must remain non-interactive.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - The repair remains in-root and does not introduce external launcher or temp-path dependencies.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Protected `scripts/` and `platform_tests/` edits require bridge proposal, LO GO, implementation claim, and verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - This proposal cites governing requirements for the source/test changes.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - This proposal carries Project Authorization, Project, Work Item, and concrete target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - The implementation report must map the readiness-probe behavior to exact executed tests and runtime verification.
- `GOV-STANDING-BACKLOG-001` - WI-4896 is the active owner-reported dispatcher console/focus-steal regression item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - The residual defect is preserved as a durable bridge artifact rather than remaining only in chat.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - This links symptom, source path, test, runtime mitigation, and eventual verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - This proposal supersedes the completed-but-incomplete acceptance claim for the separate readiness-probe surface.

## Prior Deliberations

- `DELIB-20266297` - Owner authorization for WI-4896 dispatcher console-window suppression.
- `DELIB-20266276` - Daemon resilience scope-lock and program authorization source for `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`.
- `bridge/gtkb-wi4896-startup-console-residual-003.md` - Prior proposal that fixed several daemon/background launcher paths but did not include `scripts/verify_ollama_dispatch.py` in `target_paths`.
- `bridge/gtkb-wi4896-startup-console-residual-004.md` - LO GO for the prior target set.
- `bridge/gtkb-wi4896-startup-console-residual-005.md` - Post-implementation report whose acceptance claim is now known to have missed this separate daemon readiness-probe path.
- Owner chat on 2026-06-27 supplied the persistent worker-window screenshot and confirmed the window was forcibly closed; process evidence tied that window to headless LO worker processes spawned by the Codex PostToolUse dispatch hook.

## Owner Decisions / Input

No new owner decision is required. Mike has already identified the one-minute focus-stealing console as a blocking reliability defect and named the governing program authorization as `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION`.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, and `ADR-ISOLATION-APPLICATION-PLACEMENT-001` already require headless, non-interactive, in-root daemon/background execution. No new or revised requirement is needed before implementation.

## Proposed Scope

- In `scripts/verify_ollama_dispatch.py`, harden `evaluate_ollama_autostart` so the Windows PowerShell probe uses `-NoLogo`, `-NoProfile`, `-NonInteractive`, `-ExecutionPolicy Bypass`, `stdin=subprocess.DEVNULL`, captured output, existing timeout/check behavior, and `CREATE_NO_WINDOW` on Windows.
- In `platform_tests/scripts/test_verify_ollama_dispatch.py`, extend the autostart probe tests to assert the PowerShell invocation includes `-NonInteractive`, null stdin, and Windows no-window creation flags when the platform is Windows.
- In `scripts/run_with_status.py`, normalize Windows Python console executables (`python.exe`) in the wrapped child command to sibling `pythonw.exe` when present, preserving non-Python commands and non-Windows behavior. Continue redirecting stdin/stdout/stderr and retaining `CREATE_NO_WINDOW`.
- In `platform_tests/scripts/test_run_with_status.py`, add focused coverage proving Windows child command normalization chooses `pythonw.exe` when available and falls back to the original executable when it is not available.
- In `scripts/cross_harness_bridge_trigger.py`, use `pythonw.exe` for the outer `run_with_status.py` wrapper and the post-dispatch poll subprocess on Windows when a sibling GUI-subsystem interpreter exists.
- In `platform_tests/scripts/test_cross_harness_bridge_trigger.py`, add or extend spawn tests proving the wrapper command and post-dispatch poll command use `pythonw.exe` on Windows while preserving existing arguments, logs, status file, lifetime, and no-window creation flags.
- Keep the probe diagnostic-only: missing services/tasks should still warn rather than block dispatch when Ollama is otherwise reachable.
- Leave dispatcher topology, selected targets, OpenRouter failure/backoff handling, and Task Scheduler registrations unchanged.

## Out Of Scope

- Editing `groundtruth-kb/src/groundtruth_kb/project/doctor.py`; that separate doctor path was already addressed in `gtkb-wi4896-startup-console-residual`.
- Editing daemon task registration scripts or storm-watchdog launchers.
- Hand-editing `harness-state/harness-registry.json` or dispatcher topology/eligibility to replace `python.exe` entries.
- Changing Ollama model routing, guard behavior, tool schema behavior, or dispatch target eligibility.
- Re-enabling the daemon/watchdog tasks before this fix is implemented and tested.

## Specification-Derived Verification Plan

| Spec / requirement | Planned verification |
| --- | --- |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Focused unit tests assert the Ollama readiness PowerShell probe uses `-NonInteractive`, null stdin, captured output, and `CREATE_NO_WINDOW` on Windows, and that dispatched Python worker chains use `pythonw.exe` where available. Runtime observation after re-enabling daemon verifies no visible console across at least one tick and no persistent worker console after bridge auto-dispatch. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `evaluate_dispatch_readiness` remains the daemon-readiness integration point; `_spawn_harness` and `run_with_status.py` remain the centralized worker execution path; no topology or dispatch-selection behavior changes are made. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | No out-of-root files, temp launchers, or external script dependencies are introduced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Implement only after latest bridge status is GO and a matching implementation-start packet authorizes the two target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Post-implementation report will map each linked spec to exact pytest, Ruff, and runtime observation evidence. |

Planned commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_verify_ollama_dispatch.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py scripts/run_with_status.py platform_tests/scripts/test_run_with_status.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/verify_ollama_dispatch.py platform_tests/scripts/test_verify_ollama_dispatch.py scripts/run_with_status.py platform_tests/scripts/test_run_with_status.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_cross_harness_bridge_trigger.py
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge dispatch daemon status --json
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb.cli bridge dispatch health --json
```

Runtime verification after source tests:

- Re-enable/start `GTKB-DispatcherDaemon` and, if needed, `GTKB-HarnessStormWatchdog` only after the source fix is present.
- Monitor at least one full daemon interval for absence of visible `WindowsTerminal.exe`, `OpenConsole.exe`, Windows Script Host dialogs, or focus-stealing console windows.
- Trigger or observe one headless LO dispatch worker after the fix and confirm no persistent visible terminal is created by `run_with_status.py`, `ollama_harness.py`, or `openrouter_harness.py`.
- Keep `GTKB-DbSnapshot` unchanged.

## Pre-Filing Preflight Evidence

Final candidate content was written to `.tmp/bridge-propose-drafts/gtkb-wi4896-ollama-readiness-console-residual-001.candidate.md` and preflighted before live filing.

Applicability preflight:

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4896-ollama-readiness-console-residual --content-file .tmp/bridge-propose-drafts/gtkb-wi4896-ollama-readiness-console-residual-001.candidate.md --json`
- Result: exit `0`; `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.
- Packet hash: `sha256:80ebb2b6f3c6fed2f3f1e3683a7a7a0cbb4903e9fef42d3fa53b8aae1dd2899c`.

Clause preflight:

- Command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4896-ollama-readiness-console-residual --content-file .tmp/bridge-propose-drafts/gtkb-wi4896-ollama-readiness-console-residual-001.candidate.md`
- Result: exit `0`; `must_apply: 4`; evidence gaps in must-apply clauses: `0`; blocking gaps: `0`.

## Acceptance Criteria

- [ ] The daemon's Ollama dispatch-readiness autostart probe cannot allocate or flash a visible console when invoking PowerShell on Windows.
- [ ] Headless dispatch workers cannot allocate or leave a persistent visible console via Python console-subsystem executables on Windows.
- [ ] Focused tests prove the probe uses no-window creation flags, null stdin, and non-interactive PowerShell arguments.
- [ ] Focused tests prove the dispatch wrapper and post-dispatch poll use `pythonw.exe` on Windows when available while preserving status/log behavior.
- [ ] The daemon and watchdog remain disabled until the fix is verified; after re-enable, no focus-stealing console appears across at least one minute-cadence boundary or headless-worker launch.
- [ ] No dispatcher topology, target eligibility, credential, deployment, DB schema, or scheduled-task registration behavior changes.

## Risks / Rollback

Risk is moderate and localized to Windows subprocess launch selection for headless workers and one diagnostic readiness probe. Hiding the PowerShell window does not remove diagnostic output because stdout/stderr are already captured and summarized in the returned readiness dictionary. Running dispatched Python workers through `pythonw.exe` is appropriate because `run_with_status.py` already redirects stdout/stderr to log files and records exit status to a sidecar, but tests must prove status/log paths remain intact.

Rollback is a single commit revert for the six target files, followed by disabling `GTKB-DispatcherDaemon` and `GTKB-HarnessStormWatchdog` again if the console symptom returns.

## Files Expected To Change

- `scripts/verify_ollama_dispatch.py`
- `platform_tests/scripts/test_verify_ollama_dispatch.py`
- `scripts/run_with_status.py`
- `platform_tests/scripts/test_run_with_status.py`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

## Recommended Commit Type

fix

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
