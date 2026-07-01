NEW

# Dispatcher drain live-worker parity regression

bridge_kind: prime_proposal
Document: gtkb-wi4942-dispatch-drain-live-worker-parity
Version: 001
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4942-DRAIN-LIVE-WORKER-PARITY
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4942

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_bridge_dispatch_reset.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Live release-prep evidence shows a regression in the dispatcher drain/control surface: `gt bridge dispatch report --json` reports live dispatch-run workers, including LO workers older than the bounded-worker window, while `gt bridge dispatch drain --timeout 1 --dry-run --json` reports zero drainable or terminable workers.

This proposal is a narrow follow-up to the already VERIFIED WI-4933/WI-4793/WI-4927 drain and worker-lifecycle slices. Those slices are not being reopened or edited. WI-4942 captures the remaining release blocker: drain must discover and dry-run/report the same provenance-safe live worker roots that report/status expose, and actual drain must be able to terminate or marker-stop those worker trees without manual PID hunting.

## Claim

Prime Builder proposes a bounded source/test repair for WI-4942 so the governed `gt bridge dispatch drain` surface has parity with dispatcher report/status live-worker evidence. The fix must preserve daemon-owned dispatch, headless/no-window execution, and current harness topology. It must not change routing policy, provider eligibility, credentials, deployment state, or restore retired poller/hook automation.

## Defect / Reproduction

Canonical live checks in this session produced the following evidence:

- `gt bridge dispatch daemon status --json`: daemon running under `dispatcher_daemon`, fresh heartbeat, `pid_provenance_verified=true`.
- `gt bridge dispatch health --json`: `WARN`, with LO D worker timeout and LO F max-turn/circuit-breaker findings.
- `gt bridge dispatch report --json`: summary `live_worker_count=9`, with live dispatch-run records including `loyal-opposition:D` workers older than 1000 seconds and `loyal-opposition:B/C/F` live workers.
- Focused report extraction showed live worker roots such as `2026-06-30T22-14-22Z-loyal-opposition-D-2c04f8`, `2026-06-30T22-14-56Z-loyal-opposition-D-c95fcd`, and `2026-06-30T22-10-03Z-loyal-opposition-D-377150`, all still marked live well beyond the intended bounded-worker window.
- `gt bridge dispatch drain --timeout 1 --dry-run --json` returned:

```json
{
  "drain_markers_written": 0,
  "drained_pids": [],
  "dry_run": true,
  "terminated_pids": []
}
```

The contradiction is release-blocking: an operator cannot rely on drain if it says there are no workers while report/status show live worker roots.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`, `groundtruth-kb/tests/test_bridge_dispatch_reset.py`, `platform_tests/scripts/test_bridge_dispatch_config.py`, and `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - status/report/health/drain must agree on live worker state and expose actionable bounded-worker failure evidence.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon-owned bridge dispatch must keep work moving or surface bounded failure/cleanup paths through governed dispatcher controls.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon remains the active automation path; no retired poller, hook-triggered fallback, or alternate queue may be restored.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher work must remain headless/no-window safe, including any worker cleanup or supervisor interaction.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge actionability and terminal state remain grounded in numbered bridge files plus dispatcher/TAFE state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation verification must map every linked spec to executed tests or controlled live evidence.
- `GOV-STANDING-BACKLOG-001` - WI-4942 and linked test TEST-11249 preserve this regression in the MemBase backlog.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the release blocker is captured as a durable work item, PAUTH, and bridge proposal instead of remaining scratch-only evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all implementation targets remain inside the GT-KB root and do not depend on application/adopter repositories.

## Prior Deliberations

- `DELIB-20266507` - owner directive authorizing continued autonomous dispatcher release-health fixes until the dispatcher is fully operational and release-healthy, while forbidding credentials, production deployment, retired trigger fallback, and topology mutation.
- `DELIB-20266608` - prior GO for WI-4933 terminal health/failover, including process tree visibility for drain as a release-readiness concern.
- `bridge/gtkb-wi4933-dispatcher-terminal-health-and-failover-004.md` - VERIFIED prior slice; current live evidence shows the drain/report parity acceptance still fails and needs a separate regression lane.
- `bridge/gtkb-wi4793-two-tier-dispatcher-reset-drain-006.md` - VERIFIED original reset/drain CLI slice.
- `bridge/gtkb-wi4927-stuck-headless-worker-reap-004.md` - VERIFIED prior stuck-headless-worker slice; current defect is drain visibility/parity for live dispatch-run roots.

## Owner Decisions / Input

- `DELIB-20266507` - owner directed Codex to continue dispatcher release-health fixes autonomously until fully operational and release-healthy.
- Current owner clarification, 2026-06-30: a standalone shell console for dispatcher persistence must be headless. This proposal preserves that by requiring no visible interactive console for drain/supervisor behavior.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4942-DRAIN-LIVE-WORKER-PARITY` - active project authorization for WI-4942 source/test changes only.

No further owner decision is required before Loyal Opposition review. This proposal does not request provider/routing changes, credential lifecycle work, production deployment, or retired automation restoration.

## Requirement Sufficiency

Existing requirements sufficient. WI-4942, TEST-11249, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, and `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` define the required behavior: dispatcher drain must agree with report/status live-worker evidence, clean up provenance-verified worker roots headlessly, and avoid retired automation or deployment/provider changes. No new or revised requirement is required before implementation.

## Proposed Scope

1. Make `gt bridge dispatch drain --dry-run` enumerate report-visible live dispatch-run worker roots, not only lease holders or stale runtime rows.
2. Require provenance safety for every drain candidate: dispatch id, PID, process creation time when available, and dispatch-run sidecar state must match before actual termination is attempted.
3. Ensure dry-run reports the worker roots it would drain/terminate without mutating state.
4. Ensure actual drain writes the intended drain marker, marker-stops new dispatch as already designed, terminates or marker-stops stale live worker trees, records bounded timeout/termination evidence, and reconciles runtime sidecars/state so report/status no longer retain invisible live workers.
5. Preserve current harness topology: Prime Builder A/E and Loyal Opposition D/F/C/B. Do not alter dispatch ranking, eligibility, credentials, provider routes, or production deployment surfaces.
6. Keep all Windows process cleanup headless/no-window safe.

Out of scope:

- Dashboard schema, README, wiki, or Grafana changes.
- Provider eligibility/routing policy changes.
- Credential lifecycle or provider-account changes.
- Retired OS poller, smart poller, hook-triggered dispatch, aggregate queue artifacts, or alternate queues.
- Broad worktree cleanup or release merge/push.

## Pre-Filing Preflight

Candidate content preflights are required before filing:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-propose-drafts/gtkb-wi4942-dispatch-drain-live-worker-parity-001.md
```

Expected result: applicability preflight has no missing blocking required specs, and clause preflight exits 0 with no blocking gaps.

## Specification-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Add a focused regression proving drain dry-run reports live dispatch-run workers that report/status expose; add actual-drain test proving candidate PIDs are bounded and state is reconciled. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add a dispatcher-state fixture proving daemon-controlled live workers are either drainable or explicitly reported with a bounded quarantine reason. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Code inspection and tests must show no retired trigger/poller/alternate queue path is restored. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Tests or code inspection must show Windows process cleanup uses no-window-safe process creation flags where subprocess cleanup is invoked. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live bridge state remains derived from versioned bridge files and dispatcher/TAFE state; no aggregate queue artifact is introduced. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must include exact executed commands and observed results for every linked spec. |
| Release-prep live evidence | After implementation, run `gt bridge dispatch report --json`, `gt bridge dispatch drain --timeout 1 --dry-run --json`, `gt bridge dispatch health --json`, and `gt bridge dispatch daemon status --json`. Expected: no report-visible live worker is invisible to drain dry-run. |

Expected focused command set:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/tests/test_bridge_dispatch_reset.py platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py
gt bridge dispatch report --json
gt bridge dispatch drain --timeout 1 --dry-run --json
gt bridge dispatch health --json
gt bridge dispatch daemon status --json
```

## Acceptance Criteria

- If `gt bridge dispatch report --json` shows live dispatch-run workers, `gt bridge dispatch drain --timeout 1 --dry-run --json` reports corresponding drain candidates instead of an empty result.
- Dry-run performs no mutation while exposing enough candidate metadata for operator/release evidence.
- Actual drain terminates or marker-stops provenance-verified stale worker trees and writes bounded termination evidence without killing unrelated or interactive processes.
- Report/status/health no longer retain live-worker records that drain cannot see.
- Windows process cleanup remains headless/no-window safe.
- No retired bridge automation path or aggregate queue artifact is restored.

## Risks / Rollback

Risk is primarily over-termination. Mitigation is strict provenance checking and dry-run-first behavior. Rollback is to revert the WI-4942 source/test changes and use existing manual process-tree investigation only as emergency operator action; no dispatcher topology, credential, or deployment state is changed by this proposal.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py`
- `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py`
- `groundtruth-kb/src/groundtruth_kb/cli.py`
- `groundtruth-kb/tests/test_bridge_dispatch_reset.py`
- `platform_tests/scripts/test_bridge_dispatch_config.py`
- `platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py`

## Recommended Commit Type

`fix`
