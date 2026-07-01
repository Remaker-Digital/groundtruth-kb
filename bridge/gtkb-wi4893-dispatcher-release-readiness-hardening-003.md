NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop default; reasoning effort not exposed
author_metadata_source: Codex Desktop session environment supplied during resumed bridge filing

# GT-KB Bridge Implementation Report - gtkb-wi4893-dispatcher-release-readiness-hardening - 003

bridge_kind: implementation_report
Document: gtkb-wi4893-dispatcher-release-readiness-hardening
Version: 003 (NEW; post-implementation report)
Author: Prime Builder (Codex harness A)
Date: 2026-06-28 UTC
Responds to GO: bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-002.md
Approved proposal: bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-001.md
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893
Recommended commit type: fix:

## Implementation Claim

Implemented the WI-4893 dispatcher release-readiness hardening for the original GO scope. Dispatch worker launches now record PID create-time provenance sidecars, reset-recipient and daemon orphan-reap paths refuse to terminate live PIDs unless PID and create-time provenance match, dispatch-run liveness counters skip `daemon.pid`, dispatch report/reset now agree that stdout/stderr-only sidecars are stale rather than live, and Ollama/OpenRouter harness `Glob`/`Grep` traversal skips root-escaping resolved paths instead of crashing.

The companion GO at `bridge/gtkb-wi4893-daemon-test-provenance-scope-amendment-002.md` covers the daemon test-file update needed by the approved verification plan; its implementation report is filed separately so target paths stay exact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes were made only after GO plus implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the implementation follows the proposal's linked dispatcher, bridge, and release-readiness specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the work stayed within the approved PAUTH, project, work item, and target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification evidence below maps directly to the linked specifications and proposal test plan.
- `GOV-STANDING-BACKLOG-001` - WI-4893 is the MemBase work-item authority for the dispatcher daemon-killer release blocker.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher cleanup and report/reset behavior are safer and more release-ready.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - stale dispatch-run records no longer produce false live-worker state.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch-run envelopes now include PID create-time provenance.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - report/reset/count surfaces now share stale/live semantics for dispatch-run sidecars.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - cleanup no longer terminates raw PIDs without provenance.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - D/F harness traversal skips root-escaping resolved paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the release-blocking issue is preserved through WI, PAUTH, proposal, companion scope amendment, implementation reports, and verification evidence.

## Owner Decisions / Input

Owner directive `DELIB-20260628-DISPATCHER-RELEASE-READINESS` remains the controlling release-readiness decision. No additional owner input was required for this implementation.

## Prior Deliberations

- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues block release and require a dispatcher readiness test plan.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-001.md` - approved implementation proposal.
- `bridge/gtkb-wi4893-dispatcher-release-readiness-hardening-002.md` - Loyal Opposition GO for the original source/test scope.
- `bridge/gtkb-wi4893-daemon-test-provenance-scope-amendment-001.md` - companion proposal for the missing daemon test target.
- `bridge/gtkb-wi4893-daemon-test-provenance-scope-amendment-002.md` - Loyal Opposition GO for the companion daemon test target.
- `bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-004.md` - VERIFIED create-time provenance precedent.
- `bridge/gtkb-wi4861-soft-reset-prune-stale-dispatch-runs-004.md` - soft-reset stale-run pruning baseline.
- `bridge/gtkb-wi4765-dispatch-report-cli-004.md` - dispatch report baseline.

## Implementation Authorization Evidence

```text
python scripts\bridge_claim_cli.py claim gtkb-wi4893-dispatcher-release-readiness-hardening --session-id 019f09c9-2db0-7b00-a337-40f998b07e56 --ttl-seconds 3600
result: acquired go_implementation claim rowid 24669

python scripts\implementation_authorization.py begin --bridge-id gtkb-wi4893-dispatcher-release-readiness-hardening --session-id 019f09c9-2db0-7b00-a337-40f998b07e56 --expires-minutes 60
result: authorized; packet sha256:6a05452249574f938567c212d66174e5dfbb2f2634d83cc646ea5fabc8ceb52f

python scripts\implementation_authorization.py validate --target scripts/cross_harness_bridge_trigger.py --target groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py --target groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py --target scripts/ollama_harness.py --target scripts/openrouter_harness.py --target platform_tests/scripts/test_cross_harness_bridge_trigger.py --target platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py --target platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py --target platform_tests/scripts/test_ollama_harness.py --target platform_tests/scripts/test_openrouter_harness.py
result: authorized true
```

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Implementation-start claim, packet, and target validation passed for the original GO scope. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` passed: 136 tests. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `python -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` passed: 11 tests. |
| `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` | New tests prove PID-only evidence does not trigger termination; termination requires PID create-time match. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short` passed: 58 tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest suites plus `ruff check` and `ruff format --check` passed on the changed target set. |
| Artifact-governance specs | The companion test scope gap was filed as `gtkb-wi4893-daemon-test-provenance-scope-amendment` and GOed before editing the daemon test file. |

## Commands Run

```text
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short
python -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short
python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short
python -m ruff check scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
python -m ruff format --check scripts/cross_harness_bridge_trigger.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py scripts/ollama_harness.py scripts/openrouter_harness.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py
$env:PYTHONPATH=(Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch report --json
$env:PYTHONPATH=(Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch health --json
$env:PYTHONPATH=(Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch status --json
$env:PYTHONPATH=(Resolve-Path groundtruth-kb\src).Path; python -m groundtruth_kb.cli bridge dispatch daemon status --json
```

## Observed Results

- `test_cross_harness_bridge_trigger.py` + `test_gtkb_dispatcher_daemon.py`: 136 passed in 130.60s.
- `test_bridge_dispatch_reset_stale_runs.py` + `test_bridge_dispatch_report_cli.py`: 11 passed in 33.68s.
- `test_ollama_harness.py` + `test_openrouter_harness.py`: 58 passed in 12.89s.
- `ruff check`: All checks passed.
- `ruff format --check`: 11 files already formatted.
- Dispatcher CLI smoke commands all exited 0.
- Runtime smoke caveat: `bridge dispatch daemon status --json` in the detached release worktree reported `running: false` and a stale heartbeat. That is a live runtime/substrate readiness issue to resolve before release, but it is outside the original source/test target set repaired by this implementation.

## Files Changed

- `scripts/cross_harness_bridge_trigger.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py`
- `scripts/ollama_harness.py`
- `scripts/openrouter_harness.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- `platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py`
- `platform_tests/scripts/test_ollama_harness.py`
- `platform_tests/scripts/test_openrouter_harness.py`

## Acceptance Criteria Status

- [x] Spawned dispatch workers record PID create-time provenance sidecars.
- [x] Reset-recipient and daemon orphan-reap paths refuse PID-only termination.
- [x] `daemon.pid` is outside dispatch-worker sidecar semantics.
- [x] Report/reset/count surfaces no longer treat stdout/stderr-only sidecars as live workers.
- [x] D/F harness `Glob` and `Grep` skip root-escaping resolved paths.
- [x] Focused dispatcher readiness tests pass.
- [x] Live CLI control surfaces are runnable.
- [ ] Release runtime still needs separate resolution for stale/not-running daemon state in this detached release worktree.

## Risk And Rollback

Primary residual risk is operational rather than this patch's code path: live daemon state remains unhealthy in the release worktree smoke output and must be handled before final release. The code rollback is a single revert of the WI-4893 implementation commit; it restores prior PID-only cleanup and report/reset behavior. Bridge files remain append-only.

## Loyal Opposition Asks

1. Verify the implementation against the linked specifications and executed command evidence.
2. Confirm whether the runtime daemon-state caveat is a separate release blocker or should cause this WI-4893 report to receive NO-GO.
3. Return VERIFIED if the implementation satisfies the approved proposal, otherwise return NO-GO with precise findings.
