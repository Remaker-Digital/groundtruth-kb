NEW

# WI-4944 Release Dispatcher LO Dispatch Unblock

bridge_kind: prime_proposal
Document: gtkb-wi4944-release-dispatcher-lo-dispatch-unblock
Version: 001
Author: Prime Builder (Codex)
Date: 2026-07-01 UTC

author_identity: Prime Builder / Codex
author_harness_id: A
author_session_context_id: S522-prime-builder-A-codex-desktop-20260701T0552Z
author_model: GPT-5 Codex
author_model_version: 2026-07-01 runtime
author_model_configuration: Codex desktop, Prime Builder role, governed bridge proposal path

Project Authorization: PAUTH-PROJECT-GTKB-AD-HOC-RELEASE-20260701-WI-4944-LO-DISPATCH-UNBLOCK
Project: PROJECT-GTKB-AD-HOC-RELEASE-20260701
Work Item: WI-4944

target_paths: ["scripts/openrouter_harness.py", "scripts/ollama_harness.py", "scripts/gtkb_dispatcher_daemon.py", "scripts/dispatcher_runtime.py", "scripts/ensure_dispatcher_daemon.py", "config/dispatcher/rules.toml", "platform_tests/scripts/test_openrouter_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "bridge/gtkb-wi4944-release-dispatcher-lo-dispatch-unblock-*.md"]

implementation_scope: source/test/config/bridge
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4943 is blocked at `NEW` because the daemon-driven Loyal Opposition path is not currently release-healthy: recent B/C workers timed out, F/OpenRouter hit Windows console encoding failure while printing verdict text, and D/Ollama can time out before a review is produced. This proposal creates a narrow release-unblock lane to make at least one LO dispatch target headless, bounded, and capable of producing governed bridge responses for WI-4943 and adjacent release bridge work.

The implementation must stay reductive. It may fix dispatcher worker lifecycle handling, harness stdout/stderr encoding, and the minimal dispatcher topology/config surface needed for one bounded LO path. It must not broad-merge `research`, sweep unrelated dirty files, restore retired poller or hook-driven automation, touch credential lifecycle, deploy anything, rewrite history, or bind GT-KB dashboard/release health to Azure or any default deployment provider.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is a Prime Builder `NEW` bridge entry and requires Loyal Opposition `GO` before protected script/config/test edits.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the proposal names concrete governing specs instead of treating dispatcher repair as an unstructured release emergency.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries machine-readable Project Authorization, Project, Work Item, and inline JSON `target_paths`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the post-implementation report must map each linked dispatcher requirement to executed tests or live evidence before Loyal Opposition can mark the work VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-4944 is the backlog authority for this scoped release-unblock lane and separates it from WI-4943 release-branch reconciliation.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - GT-KB dispatch is daemon-owned and resolves harness/role targets from canonical topology while recording audit evidence.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - dispatcher status/config observations and any topology adjustments must use governed `gt bridge dispatch` surfaces rather than direct config edits except where tests explicitly exercise config fixtures.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatch remains a persistent daemon-owned black-box service; harnesses are consumers, not dispatch controllers.
- `DCL-DISPATCHER-DAEMON-SINGLE-INSTANCE-INVARIANT-001` - daemon repair must not create duplicate queue owners or bypass the shared lock.
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` - daemon supervision must remain headless and idempotent, with the supervisor ensuring the daemon rather than dispatching work directly.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` - timed-out or hung workers must be bounded, reaped, and evidenced so bridge work is completed, re-dispatched, parked, or visibly escalated.
- `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001` - failing LO components must be isolated without silently halting all healthy alternatives.
- `DCL-SINGLE-HARNESS-DISPATCHER-DESKTOP-TASK-001` - the Windows background substrate must be headless/non-interactive; release evidence must not depend on a visible terminal or transient IDE tab.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the owner authorization, release unblock, expiry, and implementation/report/verdict trail are preserved as governed artifacts instead of scratch state.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the proposal treats the dispatcher unblock as an artifact graph across DELIB, WI, PAUTH, bridge, tests, and evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the explicit PAUTH expiry prevents this deferred/release-stage unblock from decaying silently if it is not completed before the release window closes.

## Prior Deliberations

- `DELIB-202665107` - owner authorized this new scoped WI/PAUTH for the LO dispatch unblock lane, expiring `2026-07-02T00:00:00Z` unless renewed or replaced.
- `DELIB-20260701-ADHOC-RELEASE-DISPATCHER-SUBSTRATE-AUTH` - owner authorized the adjacent WI-4943 release-branch dispatcher substrate reconciliation lane.
- `DELIB-20266276` - daemon-resilience scope-lock selected full auto-recovery, bounded worker handling, degraded continuity, and STUB-first load/chaos verification.
- `DELIB-20266084` - dispatcher daemon foundation authorization and liveness lessons for daemon death detection.
- `DELIB-20266272` - PHASE-Y full daemon go-live context.
- `DELIB-20265888` - dispatcher/harness isolation decision: dispatch is GT-KB-owned and harnesses are consumers only.
- `INTAKE-a815f782` - per-document dispatch suppression and lease behavior remains relevant to avoiding duplicate review attempts while this lane is repaired.
- `INTAKE-2ce995f2` - bounded parallel dispatch remains relevant, but this proposal is limited to the single-Loyal-Opposition-path release unblock needed for WI-4943.

## Owner Decisions / Input

Owner authorization is `DELIB-202665107`, recorded from the active session directive: "Authorize new scoped WI/PAUTH." The recorded scope authorizes a narrow LO dispatch unblock lane, includes an explicit expiry at `2026-07-02T00:00:00Z`, and forbids broad research merge, unrelated dirty worktree sweep, credential lifecycle, production deployment, retired poller restoration, hook-driven automation restoration, history rewrite, and default Azure/provider binding.

This proposal also honors the owner's dashboard/deployment direction: GT-KB is not bound to Azure or any deployment environment. Dashboard deployment surfaces may display application-populated health/topology/security/throughput/latency/defect/infrastructure summaries, and GT-KB tests may use mock application deployment data, but this dispatcher unblock must not introduce provider-specific release-health requirements.

## Requirement Sufficiency

Existing requirements are sufficient for implementation. The cited dispatcher architecture/spec/DCL records cover daemon ownership, headless supervision, bounded worker recovery, degraded continuity, governed dispatcher control surfaces, and bridge authority. The owner decision `DELIB-202665107` supplies the bounded release authorization and expiry; no new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

- Bridge authority and proposal linkage: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4944-release-dispatcher-lo-dispatch-unblock` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4944-release-dispatcher-lo-dispatch-unblock`; expected result is `preflight_passed: true`, no missing required/advisory specs, and zero blocking clause gaps.
- Harness stdout/stderr and provider-path boundedness: run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py platform_tests/scripts/test_ollama_harness.py -q --tb=short --no-header`; expected result is PASS, including Windows-safe readable output if OpenRouter printing is changed.
- Daemon ownership, supervision, and worker lifecycle: run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_dispatcher_runtime.py -q --tb=short --no-header`; expected result is PASS, including bounded timeout/reap evidence for workers.
- Governed dispatcher reporting evidence: run `gt bridge dispatch daemon status --json` and `gt bridge dispatch health --json`; expected result after implementation is enough daemon/process/health evidence to distinguish healthy, degraded, and blocked states. Release readiness requires no stale live workers and no misleading "terminated" claim while workers remain alive.
- Live release smoke: perform one daemon-driven or daemon-equivalent bounded LO dispatch attempt against WI-4943 or this WI-4944 bridge thread, then verify the worker exits within configured bounds, stdout/stderr are readable, and `gt bridge threads --wi WI-4944` shows the expected bridge progression. If live provider outage prevents a real verdict, the implementation report must file a bounded NO-GO/blocked evidence record rather than claiming VERIFIED.

## Risk / Rollback

Primary risk is over-widening a release unblock into dispatcher redesign or including unrelated dirty research files. Mitigation: keep changes inside the listed target paths, prefer the smallest harness/runtime fix that produces one bounded LO path, and require a post-implementation report before verification. Rollback is a single scoped commit revert plus disabling any changed dispatcher eligibility through the governed `gt bridge dispatch` surface; no production deployment or credential state is touched.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4944-release-dispatcher-lo-dispatch-unblock`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix(dispatch)`: the authorized implementation is a defect fix for daemon-driven Loyal Opposition dispatch boundedness and release-review availability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
