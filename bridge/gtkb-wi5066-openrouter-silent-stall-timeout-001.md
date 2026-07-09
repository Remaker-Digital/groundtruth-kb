NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f3ddf-359c-7fa3-8885-2d1f9179d884
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; approval_policy=never; sandbox=danger-full-access

# Defect-Fix Proposal - OpenRouter/F headless LO worker stalls silently with no socket or output after launch

bridge_kind: prime_proposal
Document: gtkb-wi5066-openrouter-silent-stall-timeout
Version: 001
Date: 2026-07-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5066

target_paths: ["scripts/openrouter_harness.py", "scripts/run_with_status.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_run_with_status.py", "platform_tests/scripts/test_dispatcher_runtime.py", "groundtruth-kb/tests/test_bridge_dispatch_reset.py"]

## Claim

OpenRouter/F is correctly selected as the Loyal Opposition dispatch target and can be launched headlessly, but the latest controlled dispatch showed a second reliability blocker beyond WI-5064's TLS exception: the worker can stall silently with no stdout, no stderr, no exit-code sidecar, no CPU activity, and no observed network socket after launch. That leaves stale dispatch/lease state and prevents OpenRouter from satisfying the active LO-default headless-processing goal.

Prime Builder requests GO for a narrow timeout and stale-runtime hardening slice: ensure OpenRouter/F workers either complete with a bridge verdict/report or fail within bounded time with a clear, classified sidecar; ensure drain/reset can clean up silent-stall residue; and preserve no-window/headless launch behavior.

## Defect / Reproduction

- At `2026-07-07T20:33:28Z`, after clearing the prior LO health hold, the dispatcher launched OpenRouter/F headlessly as `2026-07-07T20-33-28Z-loyal-opposition-F-25e69c`.
- The selected work was `bridge/gtkb-wi5065-codex-live-sandbox-readiness-001.md`.
- The dispatcher reported `spawned=true`, `health.loyal-opposition.action=allow`, and the OpenRouter/F command head as `groundtruth-kb/.venv/Scripts/python.exe scripts/openrouter_harness.py`.
- The runtime process tree showed the status wrapper and child running under `pythonw.exe`; the actual shim child was `pythonw.exe scripts/openrouter_harness.py ... --skill bridge-review --max-turns 200 --session-timeout 5400`.
- After more than the shim's `DEFAULT_TIMEOUT_SECONDS=240` request timeout, the child still had no stdout, no stderr, no `.exit_code` sidecar, no meaningful CPU activity, low stable memory, and no observed TCP connection for the child PID.
- Governed `gt bridge dispatch drain --timeout 10 --json` terminated wrapper PIDs but did not produce an exit-code sidecar; the document lease and stale dispatch-run sidecars remained until `gt bridge dispatch reset --soft --json` removed one lease lock and pruned one stale dispatch-run record.

This is distinct from the `SSLV3_ALERT_BAD_RECORD_MAC` recurrence captured in WI-5064. Together they show that OpenRouter/F's role routing is correct, but its unattended worker failure envelope is not yet reliable enough for regular LO-default processing.

## In-Root Placement Evidence

All proposed target paths are inside `E:\GT-KB`: `scripts/openrouter_harness.py`, `scripts/run_with_status.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `platform_tests/scripts/test_openrouter_harness.py`, `platform_tests/scripts/test_run_with_status.py`, `platform_tests/scripts/test_dispatcher_runtime.py`, and `groundtruth-kb/tests/test_bridge_dispatch_reset.py`.

## Requirement Sufficiency

Existing requirements are sufficient. `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001`, and the reliability fast-lane standing authorization govern this bounded defect repair. No new feature requirement is needed before implementation can begin after LO GO.

## Prefiling Preflight Evidence

- Applicability preflight command: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5066-openrouter-silent-stall-timeout --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi5066-openrouter-silent-stall-timeout-001.md --json`
- Applicability result: `preflight_passed=true`, `missing_required_specs=[]`, `missing_advisory_specs=[]`.
- ADR/DCL diagnostic preflight: zero evidence gaps in must-apply clauses.
- Bridge proposal pattern lint: zero findings.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires this source/test repair to be bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires active project authorization for implementation under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - confirms the standing project authorization does not replace LO GO or the implementation-start packet.
- `GOV-RELIABILITY-FAST-LANE-001` - authorizes small, single-concern reliability defects under `PROJECT-GTKB-RELIABILITY-FIXES` by active membership.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the live stall to be preserved as durable work-item and bridge evidence rather than chat-only memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - supports creating WI-5066 when active dispatch evidence exposes a new reliability failure mode.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - keeps the defect, proposal, verification, and eventual report linked through governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the implementation report to map focused tests and runtime evidence to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the PAUTH/project/work-item metadata above.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs dispatch selection and the requirement that selected harnesses process work headlessly.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatcher status, health, drain/reset, stale-run classification, and failure evidence.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - requires dispatcher background work to remain headless/no-window safe on Windows.
- `GOV-ENV-LOCAL-AUTHORITY-001` - prevents credential disclosure or credential lifecycle changes while diagnosing OpenRouter runtime behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - confirms the target paths are GT-KB platform files, not external application files.
- `GOV-STANDING-BACKLOG-001` - covers WI-5066 as the active backlog record for this recurrence.

## Prior Deliberations

- `DELIB-202665849` - Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060).
- `DELIB-202665847` - Loyal Opposition Verdict: OpenRouter connection reset retry.
- `DELIB-20265026` - Loyal Opposition Review - WI-4556 Ollama Provider Failure Fallback And Backoff.
- `DELIB-20265312` - Loyal Opposition Review - Dispatch Runtime Health And Readiness Repair.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner-approved standing reliability fast-lane authorization.

## Owner Decisions / Input

- Owner updated the active goal on 2026-07-07: OpenRouter must be LO-default, and Codex plus OpenRouter must be able to work headlessly.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and authorizes small reliability fixes under `PROJECT-GTKB-RELIABILITY-FIXES` by active work-item membership.
- No credential rotation, provider-account change, production deployment, force-push, sandbox weakening, or visible-window fallback is requested or authorized by this proposal.

## Proposed Scope

IP-1: In `scripts/openrouter_harness.py`, make provider-call and startup progress observable enough that a worker cannot remain silent past its configured operation timeout. If an OpenRouter call, DNS/TLS handshake, or local startup phase stalls, fail with concise credential-safe stderr and a nonzero exit code.

IP-2: In `scripts/run_with_status.py`, ensure wrapper termination paths consistently produce an exit-code sidecar or clear timeout/drain stderr marker when a child is killed, while preserving Windows no-window launch behavior.

IP-3: In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, classify stale no-output OpenRouter runs as a distinct provider/runtime readiness failure rather than leaving them as ambiguous stale evidence.

IP-4: In `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`, verify soft reset and drain cleanup handle the no-exit-code/no-live-worker lease residue observed in this dispatch without clearing quality surfaces or canonical bridge files.

IP-5: Add focused tests for silent OpenRouter stalls, wrapper timeout/drain sidecars, stale-run classification, and reset/drain cleanup behavior.

Out of scope: credential lifecycle, OpenRouter account/provider settings, production deployment, switching to a visible shell, disabling no-window launch behavior, or broad dispatcher policy rewrites.

## Specification-Derived Verification Plan

| Spec / surface | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Unit-test that an OpenRouter worker stall exits within bounded time or emits classified failure evidence rather than remaining silently in flight. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Unit-test stale no-output run classification and reset/drain behavior for no-exit-code/no-live-worker dispatch records. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Unit-test or inspect `run_with_status.py` Windows launch kwargs to confirm no-window behavior remains intact while timeout/drain markers improve. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Inspect failure messages and tests to confirm no API keys, request headers, or raw provider payloads are emitted. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest and ruff commands and cite exact results in the post-implementation report. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, run `scripts/implementation_authorization.py begin --bridge-id gtkb-wi5066-openrouter-silent-stall-timeout` after LO GO and cite the packet. |

Expected focused commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py groundtruth-kb/tests/test_bridge_dispatch_reset.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/openrouter_harness.py scripts/run_with_status.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py groundtruth-kb/tests/test_bridge_dispatch_reset.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/openrouter_harness.py scripts/run_with_status.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_dispatcher_runtime.py groundtruth-kb/tests/test_bridge_dispatch_reset.py
```

## Acceptance Criteria

- OpenRouter/F worker startup or provider-call stalls fail within bounded time with a nonzero exit code and concise stderr.
- `run_with_status.py` records an exit-code sidecar or explicit timeout/drain marker when it terminates a child process tree.
- Dispatcher health/status classifies silent no-output OpenRouter stalls as actionable runtime/provider readiness failures.
- `gt bridge dispatch drain` and `gt bridge dispatch reset --soft` clean no-live-worker/no-exit-code residue without clearing canonical bridge files, PAUTH/project state, or quality surfaces.
- Windows no-window/headless behavior is preserved.
- The post-implementation report includes focused tests and a controlled OpenRouter/F smoke plan.

## Risks / Rollback

Risk: overly aggressive timeout handling could terminate a slow but healthy OpenRouter review. Mitigation: keep timeouts bounded but configurable and only fail when progress evidence is absent or the configured operation/session timeout is exceeded.

Risk: changing wrapper termination could regress no-window behavior. Mitigation: preserve existing Windows hidden-process kwargs and lock them with tests.

Rollback: revert only the changed source/test lines and restore prior classification/timeout behavior. No credential or provider-account rollback is in scope.

## Files Expected To Change

- `scripts/openrouter_harness.py`
- `scripts/run_with_status.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `platform_tests/scripts/test_openrouter_harness.py`
- `platform_tests/scripts/test_run_with_status.py`
- `platform_tests/scripts/test_dispatcher_runtime.py`
- `groundtruth-kb/tests/test_bridge_dispatch_reset.py`

## Recommended Commit Type

`fix:`
