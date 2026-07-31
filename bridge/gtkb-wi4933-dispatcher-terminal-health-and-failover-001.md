NEW

# Dispatcher terminal health, failover, and bounded drain repair

bridge_kind: prime_proposal
Document: gtkb-wi4933-dispatcher-terminal-health-and-failover
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f18fc-3060-7b83-b9ab-297901b013c9
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex Desktop; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4933-BACKPRESSURE-HEALTH
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4933

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/run_with_status.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "scripts/bridge_lease_registry.py", "platform_tests/scripts/test_bridge_dispatch_config.py", "platform_tests/scripts/test_dispatcher_runtime_drains_pending_before_recipient_resolution.py", "platform_tests/scripts/test_dispatcher_runtime_work_intent.py", "platform_tests/scripts/test_bridge_dispatch_per_document_lease.py", "platform_tests/scripts/test_dispatch_post_dispatch_poll.py", "platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py", "platform_tests/scripts/test_dispatch_suppression_routing.py", "platform_tests/scripts/test_run_with_status.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal covers the dispatcher release-health defects still present after the VERIFIED WI-4933 slices for cursor route repair, post-verdict exit reconciliation, timeout classification, and backpressure health. Those slices improved important parts of the path, but live release-prep dispatch of `bridge/gtkb-dashboard-release-health-schema-provider-neutrality-001.md` reproduced the remaining release blockers.

The daemon is running and can launch LO workers, but it is not release-healthy. A live D review (`2026-06-30T17-45-56Z-loyal-opposition-D-32a66a`) stayed active past the observed bounded window with no stdout/stderr. `gt bridge dispatch drain --timeout 1 --dry-run --json` returned zero drainable workers even while the Windows process tree showed `gtkb_dispatcher_daemon -> run_with_status -> run_with_status -> ollama_harness -> ollama_harness`. The tree had to be manually terminated at root PID `85476`. The daemon then failed over to F (`2026-06-30T17-51-18Z-loyal-opposition-F-4baa61`), which also stayed live without a verdict and required targeted process-tree termination at root PID `14272`.

After the manual terminations, `gt bridge dispatch status --json` still reported WARN state against the still-NEW proposal: C `last_result=unchanged` with pending count, E stale terminal failure evidence, and F stale no-live-worker evidence with pending count. This means the dispatcher cannot yet prove the release requirement: at least one daemon-driven LO path must be bounded, drainable, and terminal-state-clean without manual process-tree intervention.

## Specification Links

- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/health/report must expose live workers, stale workers, failure taxonomy, pending counts, and history accurately enough for release decisions.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the dispatcher daemon is the governed automated bridge dispatch service; it must keep bridge work moving or surface actionable bounded failure evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher daemon is the active automation path; retired pollers, hook triggers, and alternate queues must not be restored.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge actionability and terminal state derive from numbered bridge files plus TAFE/dispatcher state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites concrete governing specifications.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project authorization, project, work item, and target paths are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation report must map each linked specification to tests or controlled live evidence.
- `GOV-STANDING-BACKLOG-001` - dispatcher release-health work stays anchored to `WI-4933` and the reliability project backlog.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - failed release-health findings must be preserved as actionable work instead of living only in scratch logs.

## Prior Deliberations

- `DELIB-20266507` - owner authorization for WI-4933 dispatcher backpressure health classification repair.
- `DELIB-20266508` - owner authorization for dispatcher failed-recipient LO failover repair.
- `DELIB-20266505` - owner authorization for dispatcher diagnostic health release fix.
- `bridge/gtkb-wi4933-cursor-bridge-skill-route-repair-004.md` - Cursor bridge-review route repair VERIFIED.
- `bridge/gtkb-wi4933-live-harness-boundedness-and-failure-classification-004.md` - prior boundedness/failure classification slice VERIFIED, but live D/F evidence in this session shows additional terminal/drain defects remain.
- `bridge/gtkb-wi4933-ollama-routing-timeout-bounds-004.md` - Ollama timeout-bounds slice VERIFIED, but live D still required manual process-tree termination in this session.
- `bridge/gtkb-wi4933-post-verdict-exit-reconciliation-004.md` - post-verdict exit reconciliation VERIFIED, but health still reports stale terminal evidence against pending counts.
- `bridge/gtkb-wi4933-dispatch-backpressure-health-004.md` - backpressure health slice VERIFIED, but provider/circuit state still blocks release-health clarity when a pending NEW remains.

## Owner Decisions / Input

No new owner decision is required. The active WI-4933 project authorization covers dispatcher source/tests for release-health classification, provider backpressure, failover, and bounded worker behavior. This proposal does not change credentials, provider accounts, deployment environments, branch protection, GitHub settings, or harness topology.

## Requirement Sufficiency

Existing dispatcher reliability requirements are sufficient. The observed defects are not new feature requests; they are release blockers inside the approved WI-4933 reliability scope. The implementation must stay reductive: fix dispatcher accounting, drainability, and failover semantics without restoring retired cross-harness trigger paths or hook-driven automation.

## Proposed Scope

1. Make live worker drain/discovery authoritative. `gt bridge dispatch drain --dry-run` must detect the same live process tree that `gt bridge dispatch status/report` reports, including nested `run_with_status` and provider harness children.
2. Ensure actual drain can terminate or marker-stop the full process tree for a selected live dispatch, then update runtime state so health no longer sees a live worker that is gone.
3. Reconcile terminal and no-live-worker evidence against bridge document state. If a referenced document is already terminal, stale failure evidence must not produce pending-count WARN. If a document is still NEW/REVISED, stale no-live-worker evidence must trigger deterministic failover or bounded quarantine with an explicit reason.
4. Fix recipient failover after D/F bounded failures. When D or F times out, provider-fails, or is manually drained, the next eligible LO recipient (C or B under the current topology) should become selectable unless a per-document lease or policy explicitly blocks it.
5. Add or repair a per-document LO dispatch lease so duplicate LO reviews of the same bridge document are prevented while still allowing failover after timeout/drain/terminal state.
6. Align `run_with_status`, provider harness session timeouts, and dispatcher health classifications so worker timeout, manual drain, provider failure, and subprocess failure are distinct and actionable.
7. Preserve the current topology: Prime Builder A/E; Loyal Opposition D/F/C/B. Do not change credentials, route ranking, or harness enablement unless tests prove the config reader is misreporting the existing topology.
8. Add release-health tests that use synthetic workers/process fixtures where possible, plus one controlled daemon/dry-run verification path that proves a pending NEW either receives a terminal LO verdict or a bounded actionable failure without manual process discovery.

Out of scope:

- Editing dashboard schema/docs or provider-neutral deployment surfaces; those are covered by `gtkb-dashboard-release-health-schema-provider-neutrality`.
- Restoring retired OS pollers, smart pollers, hook-triggered dispatch, aggregate queue artifacts, or alternate bridge queues.
- Changing provider credentials or asking the owner to rotate credentials.
- Broad worktree cleanup, branch merge, release declaration, or root/wiki push.

## Spec-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Add focused tests proving status/report/health distinguish live, drained, timeout, provider failure, subprocess failure, stale terminal evidence, and pending NEW with no live worker. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add a synthetic daemon dispatch test proving a failed LO worker is bounded and either fails over to the next eligible LO or emits a deterministic quarantine reason. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Tests and code inspection must show no retired poller/hook/alternate queue restoration. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests must derive actionability from numbered bridge files plus dispatcher/TAFE state, not startup summaries or aggregate queue files. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must list exact tests and expected outcomes for every linked spec above. |
| Release-prep live evidence | After implementation, run `gt bridge dispatch daemon status --json`, `gt bridge dispatch health --json`, `gt bridge dispatch drain --timeout 1 --dry-run --json`, and `gt bridge threads --wi GTKB-DASHBOARD-003`. Expected: no live worker invisible to drain; no stale terminal pending-count warnings; the dashboard proposal is either reviewed to GO/NO-GO/VERIFIED by an eligible LO path or explicitly quarantined with a bounded reason. |

Expected focused command set:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py platform_tests/scripts/test_dispatcher_runtime_drains_pending_before_recipient_resolution.py platform_tests/scripts/test_dispatcher_runtime_work_intent.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py platform_tests/scripts/test_dispatch_post_dispatch_poll.py platform_tests/scripts/test_dispatch_previous_launch_failed_cooldown.py platform_tests/scripts/test_dispatch_suppression_routing.py platform_tests/scripts/test_run_with_status.py platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py platform_tests/groundtruth_kb/cli/test_bridge_config_cli.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/run_with_status.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/bridge_lease_registry.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge_dispatch_config.py groundtruth-kb/src/groundtruth_kb/bridge_dispatch_transactions.py groundtruth-kb/src/groundtruth_kb/cli.py scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py scripts/run_with_status.py scripts/ollama_harness.py scripts/openrouter_harness.py scripts/bridge_lease_registry.py
gt bridge dispatch daemon status --json
gt bridge dispatch health --json
gt bridge dispatch drain --timeout 1 --dry-run --json
```

## Acceptance Criteria

- A live dispatch process tree reported by status/report is also visible to drain dry-run.
- Actual drain terminates or marker-stops the full worker tree and clears live state without manual PID hunting.
- D/F timeouts or provider failures do not permanently suppress C/B failover for the same pending NEW.
- Terminal bridge documents do not create pending-count WARN solely from stale recipient failure evidence.
- Pending NEW/REVISED bridge documents either get an eligible LO launch, a per-document lease reason, or an explicit bounded quarantine reason.
- No retired bridge automation path is restored.

## Risk / Rollback

Risk: changing failure classification could hide genuine provider/harness defects. Mitigation: tests must preserve severe findings for actual live failures and only suppress stale terminal/no-live false positives.

Risk: drain changes could terminate an unrelated process if PID provenance is weak. Mitigation: require recorded dispatch ID, root PID, create-time provenance, and child ancestry before termination.

Rollback: one commit should revert dispatcher source/test changes. The bridge proposal and implementation report preserve the observed release-health evidence for a narrower retry if needed.

## Bridge Filing

This proposal is filed under `bridge/` as `gtkb-wi4933-dispatcher-terminal-health-and-failover-001.md`. Dispatcher/TAFE state plus the numbered bridge file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(dispatch)`: this corrects release-blocking dispatcher health, failover, and bounded-worker accounting.
