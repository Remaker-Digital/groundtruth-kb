NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop, GPT-5, Prime Builder, dispatcher release-health hardening

# Implementation Proposal - Daemon LO failover after nonzero same-signature dispatch

bridge_kind: prime_proposal
Document: gtkb-wi4934-daemon-lo-failover-after-nonzero
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4934-LO-FAILOVER
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4934

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "platform_tests/scripts/test_dispatcher_runtime.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Live dispatcher testing found a release-blocking LO stall: after `loyal-opposition:D` exited nonzero for the pending `gtkb-wi4933-ollama-timeout-classification` verification report, the next daemon dry-run selected D again with `spawn_reason=unchanged` instead of routing the same pending report to another eligible LO harness or declaring an explicit failover hold.

The shared runtime already contains provider-failure/backoff/fallback logic for same-signature failed workers, but the daemon tick spawn path has a separate dedupe branch that checks only `last_dispatched_signature == signature` and returns `unchanged`. That divergence strands verified-release work behind a failed recipient even when other LO harnesses are active.

## Claim

Prime Builder proposes a bounded `WI-4934` fix to make daemon-substrate ticks process prior same-signature worker failures before declaring an LO dispatch unchanged. The dispatcher must remain daemon-owned; this does not authorize manual processing fallback, retired trigger restoration, credential changes, or provider retirement/waiver.

## Requirement Sufficiency

Existing requirements are sufficient. `WI-4934` captures the release blocker and `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4934-LO-FAILOVER` authorizes the bounded source/test repair for failed-recipient LO failover.

## In-Root Placement Evidence

All target paths are root-relative GT-KB paths: `scripts/gtkb_dispatcher_daemon.py`, `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`, `scripts/dispatcher_runtime.py`, and `platform_tests/scripts/test_dispatcher_runtime.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - daemon-owned dispatcher work must keep bridge review moving through eligible harnesses and expose actionable failures.
- `ADR-DISPATCHER-ARCHITECTURE-001` - the dispatcher daemon remains the only automated dispatch success path; retired trigger paths are not fallback options.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status, report, and health surfaces must distinguish no-change idempotence from failed-recipient backoff/hold.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - Windows dispatcher execution must stay background/no-window safe while failures are reported through sidecars and health surfaces.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.

## Prior Deliberations

- `DELIB-20266508` - Owner directive for dispatcher release-health continuation and authorization of WI-4934 LO failover repair.
- `DELIB-20266507` - Authorize WI-4933 dispatcher backpressure health classification repair.
- `DELIB-20266505` - Authorize dispatcher diagnostic health release fix.
- `DELIB-20266276` - Authorize daemon-resilience program implementation and release-health hardening.

## Owner Decisions / Input

- `DELIB-20266508` - owner directive that dispatcher release-health is the active top priority and the failed-recipient LO stall is a release blocker.
- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4934-LO-FAILOVER` - active project authorization covering `WI-4934` source/test changes.

## Evidence From Live Test

- Actual tick: `python scripts/gtkb_dispatcher_daemon.py tick --max-items 1` launched `2026-06-30T09-32-29Z-loyal-opposition-D-cc6cd8` for `loyal-opposition:D`.
- Sidecar result: `.gtkb-state/bridge-poller/dispatch-runs/2026-06-30T09-32-29Z-loyal-opposition-D-cc6cd8.exit_code` contains `1`.
- Sidecar stderr: `.gtkb-state/bridge-poller/dispatch-runs/2026-06-30T09-32-29Z-loyal-opposition-D-cc6cd8.stderr.log` contains `ollama_harness: session timeout exceeded before Ollama chat turn`.
- Canonical dispatcher report: `python -m groundtruth_kb.cli bridge dispatch report --json` reports D with `last_result=launched`, matching `last_dispatched_signature`, and no `last_launch` metadata for the failed run; recent history separately records the D nonzero exit.
- Next dry-run: `python scripts/gtkb_dispatcher_daemon.py tick --max-items 1 --dry-run` selected D for the same pending report with `spawn_reason=unchanged` and did not route to F, C, B, or E.
- Code evidence: `scripts/gtkb_dispatcher_daemon.py` has a daemon-local branch that treats `prior_sig == signature` as `unchanged` without first running the shared runtime previous-launch/failure/backoff classification.

## Proposed Scope

- Make daemon tick processing observe pending exit sidecars before dedupe, using the shared runtime exit-code/failure helpers where practical.
- For LO targets, when the preferred recipient has a same-signature nonzero, timeout, provider error, missing-verdict, or classified prior worker failure inside the retry window, do not return `unchanged`; mark that candidate as backoff/failed and fall through to the next eligible LO target.
- If all eligible LO targets are skipped for failure/backoff/readiness reasons, report an explicit release-blocking hold such as `lo_failover_exhausted` or an equivalent existing reason with candidate evidence.
- Preserve idempotent `unchanged` only for same-signature dispatches with no failed-run evidence and no active retry/failover condition.
- Preserve all no-window/background spawn discipline and do not alter dispatcher eligibility topology unless a later governed proposal authorizes it.

## Out Of Scope

- Disabling, retiring, or waiving any harness.
- Manual bridge processing as an automated fallback.
- Restoring or using the purged cross-harness trigger or single-harness bridge automation path.
- Credential rotation or credential-value changes.
- Broad dispatcher topology/ranking changes.
- Cursor child-process/MCP console-spawn containment, except to avoid routing to a known unsafe path during live validation until separately contained.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Add a focused daemon test simulating a same-signature LO run that has exited nonzero, then assert a subsequent tick does not classify the preferred failed recipient as mere `unchanged` and either falls through to another eligible LO or emits an explicit failover hold. |
| `ADR-DISPATCHER-ARCHITECTURE-001` | Confirm no retired trigger files or topology fallback paths are modified or used. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | Run dispatcher status/report/health after focused tests and a live dry-run; failure evidence must surface as backoff/failover/hold, not no-change. |
| `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` | Confirm no shell-wrapper or visible-console spawn path is introduced; live validation must avoid known unsafe Cursor child-shell dispatch until separately contained. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge claim and implementation authorization before protected source/test edits; implementation report must cite the GO and exact commands. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each linked spec to focused tests and live dispatcher evidence before LO verification. |

## Acceptance Criteria

- A focused daemon regression test fails on current behavior and passes after the fix: a same-signature failed LO recipient is not classified as `unchanged` on the next daemon tick.
- When another eligible LO target is available and ready, the daemon falls through to it or records deterministic skip evidence explaining why it cannot.
- When no safe eligible LO target can receive the work, the daemon emits an explicit hold reason with failed/skipped recipient evidence rather than silently stranding the work behind `unchanged`.
- `python -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short` passes or any broader failure is unrelated and documented.
- `python -m ruff check scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py` passes.
- `python -m ruff format --check scripts/gtkb_dispatcher_daemon.py scripts/dispatcher_runtime.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py` passes.
- A post-fix daemon dry-run of the live pending LO queue no longer reports D `unchanged` as the sole outcome after the observed nonzero D run.

## Risks / Rollback

Risk is moderate because this touches daemon dispatch control flow and same-signature loop-prevention behavior. The intended guardrail is narrow: only failed-run evidence may defeat `unchanged`; clean same-signature idempotence remains intact.

Rollback is a revert of source/test changes. Bridge files, work item records, and deliberation records remain append-only audit evidence.

## Files Expected To Change

- `scripts/gtkb_dispatcher_daemon.py`
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
- `scripts/dispatcher_runtime.py` if a shared helper is needed
- `platform_tests/scripts/test_dispatcher_runtime.py` if the shared helper receives behavior changes

## Recommended Commit Type

`fix`
