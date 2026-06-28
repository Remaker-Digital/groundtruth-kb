NEW

# gtkb-wi4893-dispatcher-release-readiness-hardening - Dispatcher release-readiness hardening

bridge_kind: prime_proposal
Document: gtkb-wi4893-dispatcher-release-readiness-hardening
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-28 UTC

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex desktop; formal release hardening worktree

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4893

target_paths: ["scripts/cross_harness_bridge_trigger.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py", "groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py", "scripts/ollama_harness.py", "scripts/openrouter_harness.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py", "platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_openrouter_harness.py"]

implementation_scope: source and test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

This proposal resolves the dispatcher release-readiness blockers discovered during the formal main-release investigation. WI-4893 already identified the highest-risk root cause: dispatcher reaper paths terminate live PIDs by PID alone, without the WI-4834 create-time provenance guard, so PID reuse can make a dispatcher cleanup path kill the wrong process. The current release investigation also reproduced two adjacent dispatcher-readiness defects: `gt bridge dispatch report` can count stdout/stderr-only sidecars as live workers even when no `.pid` exists, while `gt bridge dispatch reset --soft` prunes only `*.pid` records; and both D/F API harnesses crash their `Glob` tool when a resolved match escapes the active release worktree.

The implementation will harden the dispatcher substrate without changing routing policy or dispatcher configuration. It will add spawn-time PID create-time provenance sidecars, require provenance matches before dispatcher reaper termination, hard-exclude `daemon.pid` from worker cleanup semantics, make report/reset/count surfaces agree on stale dispatch-run records, and make the D/F `Glob` tool skip root-escaping matches instead of crashing the harness. It will also add a focused dispatcher readiness test plan that proves these behaviors before the release gate can pass.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected source/test changes require this proposal, Loyal Opposition GO, implementation-start evidence, implementation report, and Loyal Opposition verification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal cites the governing dispatcher, bridge, and release-readiness specifications and maps them to tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries project authorization, project, work item, and parseable target path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report must include the executed dispatcher readiness test evidence mapped to the linked specifications.
- `GOV-STANDING-BACKLOG-001` - WI-4893 is the MemBase work item authority for the root daemon-killer release blocker.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher cleanup, daemon recovery, and dispatch readiness must be reliable enough to support autonomous bridge work.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - the central dispatch service must not present false healthy state, false live-worker state, or unsafe cleanup behavior.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - dispatch-run sidecars and harness envelopes must preserve accurate lifecycle evidence for spawned work.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - the governed dispatcher report, reset, health, and status surfaces must agree on live/stale runtime state.
- `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` - cleanup must not reintroduce broad kill-switch or raw-count process killing behavior.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - harness tool results must stay within the active GT-KB worktree and must not resolve live dependencies outside the project root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the release-blocking finding was promoted into a work item, owner decision, PAUTH, proposal, and future verification evidence instead of remaining scratch context.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the repair is intentionally artifact-driven: bounded WI, proposal, tests, implementation report, and verified commit finalization.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the release-blocking dispatcher defect crossed the threshold for formal lifecycle artifacts and must not remain only in transient handoff notes.

## Prior Deliberations

- `DELIB-20260628-DISPATCHER-RELEASE-READINESS` - owner directive that dispatcher issues are release blockers and a dispatcher readiness test plan must be designed and executed before release.
- `DELIB-20266276` - daemon-resilience program scope-lock; the current work is a bounded release-readiness hardening slice under the same dispatcher reliability objective.
- `DELIB-20266268` - WI-4861 authorization and residue-cleanup context for stale dispatch-run pruning.
- `DELIB-20266203` - WI-4857 orphaned-worker reaping lineage.
- `DELIB-20266104` and `DELIB-20266135` - storm-watchdog liveness and precise PID-provenance lineage.
- `bridge/gtkb-wi4834-storm-watchdog-pid-provenance-orphan-reap-004.md` - VERIFIED create-time provenance guard pattern this proposal ports to dispatcher reaper paths.
- `bridge/gtkb-wi4861-soft-reset-prune-stale-dispatch-runs-004.md` - VERIFIED soft-reset stale-run pruning baseline; this proposal closes the stdout/stderr-only sidecar gap not covered there.
- `bridge/gtkb-wi4765-dispatch-report-cli-004.md` - VERIFIED dispatch report baseline; this proposal closes the report/reset live-run consistency gap found during release.
- `bridge/gtkb-wi4894-storm-watchdog-pythonw-output-repair-004.md` - VERIFIED watchdog output repair already in the release branch; this proposal complements it by proving dispatcher cleanup/readiness rather than redoing it.

## Owner Decisions / Input

Owner directive `DELIB-20260628-DISPATCHER-RELEASE-READINESS` authorizes treating dispatcher issues as release blockers and requires a dispatcher readiness test plan before release. The bounded implementation authorization is `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING`. It allows only source and test changes for WI-4893 and forbids production deployment, credential lifecycle action, history rewrite, retired-poller restoration, and direct dispatcher-config edits.

## Requirement Sufficiency

Existing requirements sufficient. WI-4893, `DELIB-20260628-DISPATCHER-RELEASE-READINESS`, `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4893-RELEASE-READINESS-HARDENING`, `ADR-DISPATCHER-ARCHITECTURE-001`, `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `DCL-DISPATCH-ENVELOPE-RULES-001`, `SPEC-DISPATCHER-CONTROL-SURFACE-001`, and the WI-4834 provenance precedent define the required behavior. New or revised requirements would be required only for routing-policy changes, dispatcher topology changes, production deployment, credential lifecycle work, or retired-poller restoration; all are out of scope.

## Dispatcher Readiness Test Plan

The implementation must prove the following release-readiness behaviors before it can request verification:

1. PID provenance safety: spawned dispatch workers write a create-time provenance sidecar, dispatcher reaper paths require a live process to match both PID and recorded create time before termination, and mismatched/missing create-time evidence prevents termination.
2. Daemon exclusion safety: cleanup routines never treat `.gtkb-state/dispatcher-daemon/daemon.pid` as a dispatch-worker sidecar and never use daemon PID state as worker-reap evidence.
3. Report/reset consistency: stdout/stderr-only dispatch-run ghosts are not reported as live workers, and soft reset prunes the full stale sidecar set even when `.pid` is absent.
4. Harness root-boundary safety: D/F `Glob` skips root-escaping resolved matches and continues returning in-root matches instead of raising `ValueError`.
5. Live CLI readiness: the dispatcher control surfaces (`report`, `health`, `status`, and daemon status) must be runnable from the release worktree and must not claim false live-worker health from stale sidecars.
6. Release gate integration: the focused dispatcher test suite plus the release gate must pass after this and the already-filed WI-4897 parity-gate repair are complete.

## Spec-Derived Verification Plan

| Spec / governing surface | Required verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `implementation_authorization.py begin` must produce a valid packet for this GO and `implementation_authorization.py validate` must authorize only the listed target paths. |
| `ADR-DISPATCHER-ARCHITECTURE-001` / `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py -q --tb=short` must cover PID provenance, daemon exclusion, and reaper behavior. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` / `SPEC-DISPATCHER-CONTROL-SURFACE-001` | `python -m pytest platform_tests/groundtruth_kb/test_bridge_dispatch_reset_stale_runs.py platform_tests/groundtruth_kb/cli/test_bridge_dispatch_report_cli.py -q --tb=short` must prove stale sidecar/report/reset consistency. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `python -m pytest platform_tests/scripts/test_ollama_harness.py platform_tests/scripts/test_openrouter_harness.py -q --tb=short` must prove D/F `Glob` root-boundary behavior. |
| `SPEC-DISPATCH-KILL-SWITCH-EMERGENCY-ONLY-001` | Tests must prove the fix does not add raw-count killing, kill-switch assertion, or retired-poller behavior. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | The implementation report must cite WI-4893, `DELIB-20260628-DISPATCHER-RELEASE-READINESS`, the PAUTH, the proposal/GO/report/verdict chain, and the release-readiness test evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The implementation report must include exact commands and observed results for the focused test suite, ruff check, ruff format check, and relevant live dispatcher CLI smoke checks. |

## Risk / Rollback

Primary risk is making cleanup too conservative and leaving stale sidecars behind. The release plan mitigates this by distinguishing stale record pruning from process termination: prune stale sidecars aggressively when no live matching process exists, but terminate only when PID and create-time provenance match. Rollback is a single revert of the implementation commit; it restores prior dispatcher cleanup/report behavior without changing dispatcher configuration or routing policy.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi4893-dispatcher-release-readiness-hardening`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: repairs unsafe and false-positive dispatcher readiness behavior without adding a new owner-facing feature or changing dispatcher routing policy.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
