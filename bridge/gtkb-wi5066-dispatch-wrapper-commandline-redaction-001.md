NEW

# Defect-Fix Proposal - OpenRouter/F headless LO worker stalls silently with no socket or output after launch

bridge_kind: prime_proposal
Document: gtkb-wi5066-dispatch-wrapper-commandline-redaction
Version: 001
Date: 2026-07-07 UTC
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access


Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066

target_paths: ["scripts/run_with_status.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_run_with_status.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

OpenRouter/F and Ollama/D are correctly assigned as Loyal Opposition dispatch targets, and both provider shims succeed when invoked directly, but dispatcher-launched workers still cannot process bridge work regularly because the status-wrapper command line is being killed with exit code 15 before it can write a status sidecar. Fresh isolation shows the failure is not provider connectivity: it is triggered by long-lived wrapper/worker command lines that expose `.gtkb-state/bridge-poller/dispatch-runs` sidecar paths or literal harness script tokens such as `scripts/ollama_harness.py` / `scripts/openrouter_harness.py`.

Prime Builder requests GO for a narrow command-line redaction hardening slice: move wrapper sidecar/child-argv configuration off the process command line into a bounded environment payload, launch API harness workers through an opaque in-root Python runner, preserve hidden/no-window Windows launch behavior, and lock the behavior with focused tests.

## Defect / Reproduction

- Direct provider smokes succeeded:
  - OpenRouter/F was invoked with the normal prompt option, `--model openrouter-cloud-default`, `--max-turns 1`, `--timeout 20`, and `--session-timeout 30`; it returned `OPENROUTER_KIMI_SMOKE_OK`.
  - Ollama/D was invoked with the normal prompt option, `--skill bridge-review`, `--max-turns 1`, `--timeout 20`, and `--session-timeout 30`; it returned `OLLAMA_ROUTE_SMOKE_OK`.
- A hidden/detached hand-rolled `subprocess.Popen` launch with comparable Windows no-window flags completed successfully, which rules out the basic no-window process flags as the immediate cause.
- `scripts/run_with_status.py` succeeds for immediate children, but a child that sleeps for about two seconds fails when the wrapper command line includes status/stdout/stderr paths under `.gtkb-state/bridge-poller/dispatch-runs`; the wrapper exits `15` and no status sidecar is written.
- A copied wrapper with the same logic and sidecars under `%TEMP%` succeeds for the same sleep child, which isolates the dispatch-run path exposure as a trigger.
- A copied wrapper with all sidecars under `%TEMP%` still fails when the child command line exposes `scripts/ollama_harness.py`.
- The same copied wrapper succeeds when the child uses an opaque Python `-c` runner that base64-decodes and executes `runpy.run_module("scripts.ollama_harness", run_name="__main__")` with equivalent `sys.argv`.
- A dry-run dispatcher tick at `2026-07-07T22:17:34Z` shows the current LO queue would dispatch D/Ollama and F/OpenRouter, while A/Codex remains suppressed by `codex_dispatch_not_ready`. Therefore this failure directly blocks the active D/F LO-processing path.

This is a refined root cause under the WI-5066 silent-stall/no-output symptom family. It also explains why manual provider smokes can pass while dispatcher workers die before producing bridge output.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/run_with_status.py`, `scripts/dispatcher_runtime.py`, `platform_tests/scripts/test_run_with_status.py`, `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this source/test repair to be bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires active project authorization for implementation under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms the standing project authorization does not replace LO GO or the implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - authorizes small reliability defects under `PROJECT-GTKB-RELIABILITY-FIXES` by active membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the isolated wrapper-kill failure to be preserved as durable work-item and bridge evidence rather than chat-only memory.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to map focused tests and live dispatch evidence to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH/project/work-item metadata above.
- `SPEC-AUQ-POLICY-ENGINE-001` - relevant only to confirm this proposal does not request a fresh owner decision outside the recorded PAUTH/goal evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms the target paths are GT-KB platform files inside `E:\GT-KB`, not external application files.
- `GOV-STANDING-BACKLOG-001` - covers WI-5066 as the active MemBase work-item authority for this recurrence.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - relevant because Codex must self-enforce bridge and implementation-start gates before touching protected files.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the defect, proposal, implementation, tests, report, and verification linked through governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - supports filing a refined follow-on proposal when fresh runtime evidence changes the implementation scope.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs dispatch selection and the requirement that selected harnesses process work headlessly.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher health/status evidence, dispatch-run sidecars, worker timeout classification, and reset/drain behavior.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - requires background dispatch work to remain hidden/no-window safe on Windows.

## Prior Deliberations

- `DELIB-202665849` - Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060)
- `DELIB-202665919` - Loyal Opposition Verdict — gtkb-wi5065-codex-live-sandbox-readiness — 002
- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff
- `DELIB-202665727` - WI-4991 Headless-Ineligible Dispatch Suppression -- Proposal Review Verdict
- `DELIB-202665845` - Loyal Opposition Verification - Ollama route max turn budget (WI-5060)

## Owner Decisions / Input

- Owner updated the active goal on 2026-07-07: OpenRouter should be LO-default, Codex and OpenRouter must work headlessly, and Ollama should be assigned to the deepest in-flight work queue when available again.
- Current dispatcher evaluation assigns D/Ollama to Loyal Opposition, and the fresh dry-run shows LO has the deeper dispatchable queue across D/F.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and authorizes small reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES` by active work-item membership.
- No credential rotation, provider-account change, production deployment, force-push, visible-window fallback, or clearing of the Codex no-window disable guard is requested or authorized by this proposal.

## Requirement Sufficiency

Existing requirements are sufficient. The active owner goal, WI-5066, the reliability fast-lane authorization, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` already define the required behavior: selected dispatch harnesses must process work headlessly and expose bounded, classified failure evidence. No new functional requirement is needed before implementation can begin after LO GO.

## Prefiling Preflight Evidence

- Applicability preflight command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5066-dispatch-wrapper-commandline-redaction --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md --json`
- Applicability result: `preflight_passed=true`, `missing_required_specs=[]`, `missing_advisory_specs=[]`.
- ADR/DCL clause preflight command: `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5066-dispatch-wrapper-commandline-redaction --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md`
- ADR/DCL clause result: `blocking_gaps=0`, `evidence_gaps_in_must_apply_clauses=0`.
- Bridge proposal pattern lint command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_proposal_pattern_lint.py --file .gtkb-state/bridge-propose-drafts/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md`
- Bridge proposal pattern lint result: `Findings: 0`.

## Proposed Scope

IP-1: In `scripts/run_with_status.py`, add a bounded configuration mode that reads wrapper inputs from an environment variable such as `GTKB_RUN_WITH_STATUS_CONFIG_JSON` or `GTKB_RUN_WITH_STATUS_CONFIG_B64`. The payload should include the current sidecar paths, optional stdin/stdout/stderr paths, lifetime budget, and child argv. Validate required fields, preserve the existing positional-argument mode for backward compatibility, and avoid logging raw env payloads.

IP-2: In `scripts/dispatcher_runtime.py`, build wrapper launches so the parent command line no longer exposes `.gtkb-state/bridge-poller/dispatch-runs` paths or child harness argv. Pass sidecar paths and child argv through the new env payload, while preserving current cwd/env inheritance, author metadata injection, hidden `pythonw.exe` wrapper selection, detached/new-process-group behavior, and worker lifetime semantics.

IP-3: For API harnesses whose registry command invokes in-root shim scripts (`scripts/ollama_harness.py`, `scripts/openrouter_harness.py`, and compatible future API harness shims), transform the child argv into an opaque in-root Python `-c` runner that reconstructs `sys.argv` and executes the target module with `runpy.run_module`. Preserve exact CLI arguments, model/skill selections, timeout flags, and failure exit codes.

IP-4: Keep dispatch auditability without reintroducing kill-triggering command lines: status/report surfaces may record a safe command head or target harness id, but must not require raw sidecar paths or full harness script argv on the live OS command line.

IP-5: Add focused tests for the new wrapper env-payload parser, backward-compatible positional mode, lifetime timeout/status behavior, dispatcher wrapper command construction, API harness opaque-launch conversion, and no-window launch invariants.

Out of scope: provider credential lifecycle, OpenRouter/Ollama account changes, production deployment, clearing the Codex no-window disable guard, changing bridge selection policy, or broad dispatcher rewrites beyond the wrapper command-line construction needed for this defect.

## Specification-Derived Verification Plan

| Spec / surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Unit-test dispatcher worker command construction so D/F remain selected as headless LO workers and the live wrapper command line omits dispatch-run sidecar paths and literal harness script argv. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Unit-test `run_with_status.py` env-payload mode, status sidecar writing, timeout classification, and backward-compatible positional mode. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Unit-test or inspect dispatcher wrapper `Popen` kwargs to confirm hidden/no-window `pythonw.exe`, detached/new-process-group behavior remains intact. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Inspect env-payload handling and failure messages to confirm credentials, request headers, and raw provider payloads are not emitted. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest and ruff commands, then cite exact results in the post-implementation report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5066-dispatch-wrapper-commandline-redaction` after LO GO and cite the packet. |

Expected focused commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/run_with_status.py scripts/dispatcher_runtime.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py
```

Controlled live evidence after tests:

```text
groundtruth-kb/.venv/Scripts/python.exe -c "from pathlib import Path; import json; from scripts.gtkb_dispatcher_daemon import run_tick; print(json.dumps(run_tick(Path(r'E:\GT-KB'), max_items=8, dry_run=True), indent=2, sort_keys=True))"
```

After implementation authorization and tests, a bounded live D/F dispatch smoke may be run only if it does not clear the Codex no-window guard or relaunch Codex/A.

## Acceptance Criteria

- Dispatcher-launched `run_with_status.py` no longer exposes `.gtkb-state/bridge-poller/dispatch-runs` sidecar paths on the wrapper command line.
- Dispatcher-launched API harness workers no longer expose literal `scripts/ollama_harness.py` or `scripts/openrouter_harness.py` tokens on the child process command line.
- `run_with_status.py` still supports the existing positional invocation path and still writes status sidecars for normal exit and timeout cases.
- Windows hidden/no-window launch behavior is preserved for dispatcher workers.
- D/Ollama and F/OpenRouter remain selected as LO dispatch targets; A/Codex remains suppressed while `codex_dispatch_not_ready` is true.
- Focused tests and ruff checks pass, and the post-implementation report includes either bounded live D/F dispatch evidence or a truthful residual blocker if host policy still kills workers.

## Risks / Rollback

Risk: hiding command-line detail could reduce operator debuggability. Mitigation: preserve sanitized dispatch metadata in status/report surfaces while keeping volatile paths and harness argv out of live OS command lines.

Risk: opaque Python `-c` runner construction could alter harness argv semantics. Mitigation: test exact argv reconstruction and keep module execution in the same in-root interpreter/cwd/env context.

Risk: env payloads could leak sensitive content if logged. Mitigation: never log raw payloads, keep payload contents limited to paths/argv already known to the dispatcher, and use existing credential-safe failure text.

Rollback: revert only the changed source/test lines and restore the prior wrapper command construction. Do not clear the Codex no-window disable guard, change provider credentials, or reset dispatcher history as part of rollback unless separately authorized.

## Files Expected To Change

- `scripts/run_with_status.py`
- `scripts/dispatcher_runtime.py`
- `platform_tests/scripts/test_run_with_status.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`

## Bridge Filing

This proposal will be filed as the next append-only numbered bridge file `bridge/gtkb-wi5066-dispatch-wrapper-commandline-redaction-001.md`; no prior bridge version is deleted or rewritten. Dispatcher/TAFE state plus the numbered bridge file chain remain the canonical workflow state.

## Recommended Commit Type

`fix`
