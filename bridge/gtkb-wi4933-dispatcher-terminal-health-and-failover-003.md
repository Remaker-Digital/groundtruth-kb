NEW

# Dispatcher terminal health, failover, and bounded drain repair - implementation report

bridge_kind: implementation_report
Document: gtkb-wi4933-dispatcher-terminal-health-and-failover
Version: 003
Author: Prime Builder (Codex, harness A)
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access
Date: 2026-06-30 UTC

Responds to GO: bridge/gtkb-wi4933-dispatcher-terminal-health-and-failover-002.md
Approved proposal: bridge/gtkb-wi4933-dispatcher-terminal-health-and-failover-001.md

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933
Recommended commit type: fix(dispatch)

## Implementation Claim

Implemented a focused dispatcher reliability slice inside the approved WI-4933 scope:

1. Provider failure backoff now honors an active circuit breaker even when the selected bridge signature changes, so D/F failures no longer immediately consume new LO work during the retry/backoff window.
2. The post-dispatch verdict polling regression now uses a canonical bridge verdict token (`GO`) instead of a placeholder token that the production verdict finder correctly ignores.
3. `gt bridge dispatch daemon stop` now reaps live dispatched workers before terminating the daemon process tree, causing bounded workers to receive `124` exit sidecars instead of leaving silent PID-only runtime records.

This report does not claim full dispatcher release health. Current live health remains `WARN` because historical stale-live/corrupt-output runtime residue and active queue backpressure remain visible. The implementation gives Loyal Opposition a narrow, test-backed slice to verify and preserves the remaining release-health blocker as explicit evidence.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report must expose live workers, stale workers, failure taxonomy, pending counts, and history accurately enough for release decisions.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the dispatcher daemon is the governed automated bridge dispatch service; it must keep bridge work moving or surface actionable bounded failure evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon is the active automation path; retired pollers, hook triggers, and alternate queues must not be restored.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge actionability and terminal state derive from numbered bridge files plus TAFE/dispatcher state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the approved proposal cited concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared in the approved proposal and carried forward here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - this report maps linked specifications to focused tests and observed command results.
- `GOV-STANDING-BACKLOG-001` - dispatcher release-health work remains anchored to `WI-4933` and the dispatcher reliability project.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - remaining release-health blockers are preserved as explicit bridge evidence instead of scratch-only notes.

## Owner Decisions / Input

No new owner decision is required. This implementation stays within the approved WI-4933 dispatcher reliability authorization. Owner clarifications received during the session are carried as release-health requirements for follow-up documentation/proposal work:

- GT-KB is not bound to Azure or any specific application deployment environment.
- Dashboard deployment-health surfaces must be provider-neutral and populated by adopter applications, with mock deployment data available for testing.
- Deferred items must have an explicit expiry: either a state trigger or a time limit. Indefinite deferral is not an acceptable release-governance state.
- Any Windows standalone daemon shell guidance must describe a headless background console/session, not a visible interactive terminal that must be babysat.

## Prior Deliberations

- `bridge/gtkb-wi4933-dispatcher-terminal-health-and-failover-001.md` - approved implementation proposal carried forward.
- `bridge/gtkb-wi4933-dispatcher-terminal-health-and-failover-002.md` - Loyal Opposition GO verdict authorizing this implementation.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md` - Cursor route repair is already VERIFIED and was not reworked here.
- `bridge/gtkb-wi4933-post-verdict-exit-reconciliation-004.md` - prior post-verdict reconciliation slice is already VERIFIED and was not redone here.

## Files Changed

- `scripts/dispatcher_runtime.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `platform_tests/scripts/test_dispatch_post_dispatch_poll.py`
- `platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

No retired poller, hook-driven dispatch path, aggregate queue artifact, credential path, or harness topology file was restored or changed by this implementation report scope.

## Specification-Derived Verification Plan And Evidence

| Governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `gt bridge dispatch health --json` and `gt bridge dispatch status --json` still expose WARN findings for B/F/A after the fix. Focused tests prove stale/failed launch state is classified rather than hidden. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Dry daemon tick with `GTKB_DISPATCH_RETRY_DELAY_SECONDS=86400` showed D and F skipped via `provider_failure_backoff_active`, while C became the next LO dry-run target for `gtkb-wi4869-related-bridge-provenance-separation`. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Source changes are limited to dispatcher daemon/runtime/CLI control surfaces and tests. No retired cross-harness trigger, OS poller, hook-triggered fallback, or alternate queue was restored. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Post-dispatch verdict polling now tests a canonical `GO` verdict file so actionability remains derived from status-bearing bridge files. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused dispatcher bundle, focused CLI test, and ruff checks were executed with observed results listed below. |
| `GOV-STANDING-BACKLOG-001` | The work remains tied to WI-4933; the implementation report explicitly calls out remaining WARN state instead of declaring release health prematurely. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The remaining release-health blockers are preserved in this implementation report for LO verification or NO-GO handling. |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py -q --tb=short
```

Observed result: `10 passed in 2.52s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py -q --tb=short
```

Observed result: `10 passed in 1.17s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_dispatcher_runtime_drains_pending_before_recipient_resolution.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py platform_tests\scripts\test_bridge_dispatch_per_document_lease.py platform_tests\scripts\test_dispatch_post_dispatch_poll.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py platform_tests\scripts\test_dispatch_suppression_routing.py platform_tests\scripts\test_run_with_status.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py -q --tb=short
```

Observed result: `168 passed, 1 skipped in 22.51s`.

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_transactions.py groundtruth-kb\src\groundtruth_kb\cli.py scripts\gtkb_dispatcher_daemon.py scripts\dispatcher_runtime.py scripts\run_with_status.py scripts\ollama_harness.py scripts\openrouter_harness.py scripts\bridge_lease_registry.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_dispatcher_runtime_drains_pending_before_recipient_resolution.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py platform_tests\scripts\test_bridge_dispatch_per_document_lease.py platform_tests\scripts\test_dispatch_post_dispatch_poll.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py platform_tests\scripts\test_dispatch_suppression_routing.py platform_tests\scripts\test_run_with_status.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py
```

Observed result: `All checks passed!`

```text
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check groundtruth-kb\src\groundtruth_kb\bridge_dispatch_config.py groundtruth-kb\src\groundtruth_kb\bridge_dispatch_transactions.py groundtruth-kb\src\groundtruth_kb\cli.py scripts\gtkb_dispatcher_daemon.py scripts\dispatcher_runtime.py scripts\run_with_status.py scripts\ollama_harness.py scripts\openrouter_harness.py scripts\bridge_lease_registry.py platform_tests\scripts\test_bridge_dispatch_config.py platform_tests\scripts\test_dispatcher_runtime_drains_pending_before_recipient_resolution.py platform_tests\scripts\test_dispatcher_runtime_work_intent.py platform_tests\scripts\test_bridge_dispatch_per_document_lease.py platform_tests\scripts\test_dispatch_post_dispatch_poll.py platform_tests\scripts\test_dispatch_previous_launch_failed_cooldown.py platform_tests\scripts\test_dispatch_suppression_routing.py platform_tests\scripts\test_run_with_status.py platform_tests\scripts\test_ollama_harness.py platform_tests\scripts\test_openrouter_harness.py platform_tests\groundtruth_kb\cli\test_bridge_config_cli.py
```

Observed result: `20 files already formatted`.

```text
$env:GTKB_DISPATCH_RETRY_DELAY_SECONDS='86400'; groundtruth-kb\.venv\Scripts\python.exe scripts\gtkb_dispatcher_daemon.py tick --project-root E:\GT-KB --max-items 2 --dry-run
```

Observed result: D and F returned `provider_failure_backoff_active`; C was selected as the next LO `dry_run` target for `gtkb-wi4869-related-bridge-provenance-separation`. The same run reported monitor health hold with `stale_live` and `corrupt_output`, preserving the remaining release-health blocker.

```text
gt bridge dispatch daemon status --json
gt bridge dispatch health --json
gt bridge dispatch status --json
```

Observed result after stopping the daemon: daemon `running=false`, stale heartbeat from `2026-06-30T19:25:06Z`; dispatch health remains `WARN` with B backpressure, F stale no-live evidence, and Prime A unchanged/pending work-intent evidence.

## Acceptance Criteria Status

- Live worker boundedness: partially satisfied. A controlled F worker run produced exit code `124` and no surviving PID. The new CLI stop regression proves daemon stop reaps workers before daemon-tree termination.
- D/F failover: partially satisfied. Dry daemon tick proves D/F backoff and C next-target selection under high retry delay.
- Terminal/no-live state cleanup: not fully satisfied. Current status still reports WARN for stale no-live evidence and historical stale/corrupt output.
- Pending NEW/REVISED handling: partially satisfied. The dispatcher can select an eligible C LO dry-run target, but a live daemon-driven LO verdict was not produced in this slice.
- Retired automation avoidance: satisfied. No retired poller, smart poller, hook-triggered fallback, or aggregate queue path was restored.

## Residual Release Blocker

GT-KB dispatcher release health is still not clean. Current evidence:

- `gt bridge dispatch daemon status --json`: `running=false`, stale heartbeat from `2026-06-30T19:25:06Z`.
- `gt bridge dispatch health --json`: `health_status=WARN`.
- Dry daemon tick monitor health: loyal-opposition hold reasons include `corrupt_output` and `stale_live`; prime-builder hold reason includes `stale_live`.
- A daemon-driven live LO path was bounded, but it did not produce a bridge verdict for the dispatched NEW items before timeout/stop.

This should be treated as either a NO-GO for the full approved proposal or a VERIFIED narrow slice with an explicit follow-up blocker, depending on Loyal Opposition's reading of the acceptance criteria. Prime Builder recommends NO-GO if the verifier requires full release-health PASS for this thread.

## Risk And Rollback

Risk: the stop path now reaps dispatched workers before terminating the daemon tree. It uses the existing provenance-checked `reap_inflight_dispatched_workers` helper, so PID-only evidence is still not trusted for worker termination.

Risk: stricter provider backoff could delay retries for a recovered provider. The backoff is governed by existing retry/circuit-breaker timing and is covered by the new changed-signature regression.

Rollback: revert the five files listed above. Runtime evidence files and bridge audit files remain append-only and should not be rewritten.

## Loyal Opposition Asks

1. Verify the narrow implementation evidence for provider backoff, canonical verdict polling, and stop-time worker reaping.
2. Return NO-GO if full dispatcher release health is required for this approved proposal before release preparation can proceed.
