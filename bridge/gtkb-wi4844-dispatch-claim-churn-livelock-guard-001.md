NEW

# gtkb-wi4844-dispatch-claim-churn-livelock-guard — Prime dispatch work-intent suppression and daemon parity guard

bridge_kind: prime_proposal
Document: gtkb-wi4844-dispatch-claim-churn-livelock-guard
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f09c9-2db0-7b00-a337-40f998b07e56
author_model: gpt-5-codex
author_model_version: 2026-06-29
author_model_configuration: Codex desktop Prime Builder session; approval_policy=never; Harness Parity Phase 2 release-hardening

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4844

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/single_harness_bridge_dispatcher.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_single_harness_bridge_dispatcher.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py"]

implementation_scope: source | test | dispatcher-protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4844 already captures the release-blocking claim-churn/livelock class: GO-latest Prime work can be re-dispatched repeatedly after workers make no forward progress. The live release run on 2026-06-29 exposed an even sharper variant in the daemon substrate: while this interactive Prime session held an active WI-4778 implementation claim (`acquired_at=2026-06-29T11:33:46Z`, `session_id=019f09c9-2db0-7b00-a337-40f998b07e56`), the dispatcher daemon still launched Codex A at `2026-06-29T11:36:38Z` with WI-4778 included in the selected Prime batch. The spawned Codex worker exited `4294967295` with a large stderr transcript, reproducing the user-visible Codex/console storm failure mode.

Root cause hypothesis from code inspection: the cross-harness trigger and single-harness dispatcher contain Prime work-intent filtering/acquisition paths, but `scripts/gtkb_dispatcher_daemon.py::_execute_live_spawns` reuses `_spawn_harness` directly on `_spawn_selected` records and bypasses `_filter_prime_selected_by_work_intent` / `_acquire_prime_work_intent_batch`. That lets daemon live mode spawn a Prime worker for already-claimed work and pass held items into the dispatch prompt. This proposal implements daemon parity with the shared Prime work-intent gate and tightens mixed-batch behavior so held GO/NO-GO items are never included in worker prompts or launch signatures.

The implementation should also preserve WI-4844's original guard intent: repeated zero-progress Prime dispatch attempts must produce suppression evidence instead of unbounded cold-worker churn. If full consecutive-zero-progress accounting requires more than the bounded target set, the implementer must keep this slice to the daemon/filter parity guard and file a follow-on proposal before broadening scope.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — requires Prime Builder implementation only after LO GO and return through a post-implementation report.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite every governing dispatch, bridge, and project-authorization surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the Project Authorization, Project, Work Item, and `target_paths` metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires verification evidence mapped to the linked specifications before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — makes WI-4844 the canonical backlog item for this release-blocking dispatcher defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — constrains implementation to the active Harness Parity Phase 2 authorization and target paths.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — requires equivalent governance enforcement across trigger, daemon, and single-harness dispatch routes.
- `ADR-DISPATCHER-ARCHITECTURE-001` — constrains fixes to the current dispatcher/TAFE architecture and forbids restoration of retired poller paths.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — requires dispatcher health and launch behavior to reflect actual dispatchability and not hide runtime failures.
- `DCL-DISPATCH-ENVELOPE-RULES-001` — governs selected-entry envelopes, worker prompts, route-specific failure handling, and dispatch metadata.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — requires harness dispatch readiness and no-window/no-storm behavior before a harness is treated as fungible.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — makes this dispatcher reliability evidence a release-health gate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — requires the live defect evidence and fix outcome to be preserved as governed artifacts, not scratch memory.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — frames the fix as a traceable artifact graph connecting work item, bridge proposal, tests, implementation report, and release evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — governs the transition from live defect evidence to actionable proposal, implementation, verification, and release-health closure.

## Prior Deliberations

- `INTAKE-f8bc08a3` — Intake: Dispatcher/Bridge CLI as primary mutating UI for GT-KB artifact operations
- `INTAKE-e7d44d40` — Intake: GO-implementation claims are time-boxed with an owner-extendable deadline to produce the implementation report
- `INTAKE-a815f782` — Intake: Bridge dispatch suppression scoped per bridge document (per-document lease)
- `INTAKE-5a61f299` — Intake: Claim-gated implementation-start: holding the GO-implementation claim is required before editing a GO'd thread's target paths
- `INTAKE-2ce995f2` — Intake: Enable bounded parallel cross-harness auto-dispatch (supersede binary same-role active-session suppression)
- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` — owner directive making harness parity a release blocker under normal bridge gates.
- `bridge/gtkb-wi4778-cursor-headless-dispatch-readiness-003.md` — live evidence surfaced while filing the Cursor readiness report: daemon dispatch launched Codex A with WI-4778 selected despite an active Prime implementation claim.
- `bridge/gtkb-wi4885-dispatch-topology-activation-010.md` — current topology activation remains NO-GO while Cursor is quarantined; this proposal does not change topology.
- `WI-4560` / `WI-4545` / `WI-4821` — backlog history captured in WI-4844 showing repeated cold-worker churn after claim lapse and dispatch re-enable.

## Owner Decisions / Input

No new owner decision is required. The owner has made dispatcher release health and Harness Parity Phase 2 the top priority, and `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` covers WI-4844 through normal bridge gates. This proposal does not change credentials, install provider software, deploy, mutate GitHub settings, or change durable harness roles/topology.

## Requirement Sufficiency

Existing requirements sufficient. WI-4844 defines the release-blocking defect and acceptance criteria, and the linked dispatcher/bridge/harness governance specifications define the implementation constraints. No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

Implementation must prove all Prime dispatch routes enforce work-intent suppression before spawn:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_dispatcher_daemon.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_dispatcher_daemon.py scripts/cross_harness_bridge_trigger.py scripts/single_harness_bridge_dispatcher.py platform_tests/scripts/test_gtkb_dispatcher_daemon.py platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_single_harness_bridge_dispatcher.py
```

Required test coverage:

- Daemon live mode does not call `_spawn_harness` when every selected Prime item is held by another active work-intent claim.
- Daemon live mode records a suppression/non-launch result, not a spawned worker or actionable failure, for already-held Prime work.
- Daemon mixed-batch behavior removes held items before building the worker prompt/signature; an unheld item may dispatch only without the held item appearing in selected entries.
- Cross-harness trigger regression proves mixed held/unheld Prime selected entries never pass held items into `_spawn_harness`.
- Single-harness dispatcher regression proves it does not pass the full pending list into `_spawn_worker` after Prime work-intent filtering.
- If implemented in this slice, consecutive zero-progress Prime dispatch attempts at the threshold suppress re-dispatch while a fresh/progressing thread still dispatches.
- `gt bridge dispatch health --json` no longer reports a fresh Codex Prime subprocess failure caused by already-claimed WI-4778-class duplicate dispatch after the state is re-evaluated.

## Risk / Rollback

Primary risk is over-suppression: a healthy unclaimed Prime item must still dispatch. The test plan therefore requires fresh/progressing and mixed-batch positive paths, not only suppression paths. Secondary risk is under-suppression in daemon live mode, which would keep spawning visible Codex windows or duplicate workers. Rollback is a single commit revert of the listed dispatcher/test files; bridge audit files remain append-only.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi4844-dispatch-claim-churn-livelock-guard`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix: this repairs a release-blocking dispatcher correctness defect that can spawn duplicate Prime workers and visible Codex/console storms for already-claimed work.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
