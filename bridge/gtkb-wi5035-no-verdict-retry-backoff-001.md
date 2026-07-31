NEW

# WI-5035 — Bounded retry/backoff for repeated no-verdict dispatch failures

bridge_kind: prime_proposal
Document: gtkb-wi5035-no-verdict-retry-backoff
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-07-07 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f337a-009a-7f51-8dce-b6c3f1d91b1c
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex desktop interactive Prime Builder session; reasoning=xhigh; approval_policy=never

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5035-NO-VERDICT-BACKOFF-20260707
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Work Item: WI-5035

target_paths: ["scripts/dispatcher_runtime.py", "scripts/gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_runtime.py", "platform_tests/scripts/test_bridge_dispatch_config.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5035 converts the no-verdict retry advisory into a bounded dispatcher reliability fix. The observed defect is that a worker exit that produces no bridge verdict can be re-detected as `no_verdict_produced` / `previous_launch_failed` for the same actionable signature on a tight cadence, causing repeated launch churn instead of bounded recovery or visible quarantine.

The implementation should verify the current retry path, then correct the same-signature no-verdict loop with one of the bounded recovery approaches already allowed by the work item: enforce retry/backoff, trip a bounded retry/quarantine path, or integrate the case with the existing circuit-breaker behavior. The change must preserve healthy-recipient dispatch, role eligibility, project authorization, dispatch caps, and existing health semantics. It must not change harness roles, enable or disable harnesses, touch provider credentials, restart the daemon, or perform production activation work.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — the implementation proposal must enter the numbered bridge chain through the governed writer and wait for a latest `GO`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — the proposal cites the dispatcher, project-authorization, recovery, and backlog specifications that constrain the work.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the proposal carries `Project Authorization`, `Project`, and `Work Item` metadata for implementation-start validation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the implementation report must map this proposal's dispatcher and governance requirements to executed tests.
- `GOV-STANDING-BACKLOG-001` — WI-5035 remains visible in the MemBase backlog until bridge completion or another terminal disposition.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the bounded PAUTH is owner approval evidence for WI-5035 only and does not permit unrelated dispatcher work.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the PAUTH does not bypass Loyal Opposition `GO`, target paths, spec-derived tests, implementation report, or verification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` — dispatch remains a GT-KB-owned service that resolves targets and records dispatch evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher remains daemon-owned; harnesses remain consumers rather than dispatch-control actors.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001` — recoverable runtime failures must surface as degraded dispatch state without incorrectly collapsing fleet capability to FAIL when healthy alternatives remain.
- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` — worker crash/no-verdict recovery must be automatic, bounded, and auditable rather than owner-mediated.
- `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001` — repeated component-level failures must isolate the failing component, surface degraded state, and preserve safe dispatch across healthy fleet members.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the advisory, owner decision, PAUTH, proposal, tests, report, and verification remain durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the implementation should preserve traceability from defect/advisory to proposal, tests, report, and verification evidence.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-5035 moves from advisory/backlog state into a governed proposal path without silently resolving or losing its advisory evidence.

## Prior Deliberations

- `gtkb-wi5035-no-verdict-retry-backoff-advisory-001` — Loyal Opposition advisory identifying the repeated no-verdict retry loop and recommending conversion to a normal implementation proposal.
- `DELIB-20260707-WI5035-IMPLEMENTATION-APPROVAL` — owner authorized Prime Builder to attach WI-5035 to the dispatcher modernization project, create bounded PAUTH evidence, and file this NEW implementation proposal.
- `INTAKE-8242840e` — prior intake on simple dispatcher retry and OPS-owned failed-workflow recovery; this proposal narrows that theme to same-signature no-verdict failures.

## Owner Decisions / Input

- `DELIB-20260707-WI5035-IMPLEMENTATION-APPROVAL` records the owner instruction `WI-5035: Authorize proposal` for this specific backlog item.
- `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI5035-NO-VERDICT-BACKOFF-20260707` bounds the authorized work to WI-5035. It explicitly forbids implementation without bridge `GO` and implementation-start, production deployment, credential or provider-account changes, daemon restart/topology activation, harness role reassignment, F activation/deactivation, unrelated harness routing changes, broad dirty-worktree cleanup, destructive cleanup, history rewrite, unrelated sweep commits, and protected artifact mutation without the applicable approval packet.

## Requirement Sufficiency

Existing requirements sufficient. WI-5035, the advisory, and the dispatcher recovery specifications define the behavior to implement: repeated `no_verdict_produced` for the same signature must not churn on a tight loop; it must enter bounded backoff, bounded retry/quarantine, or circuit-breaker behavior with visible status and focused test coverage. No new or revised requirement is needed before implementation, provided the implementation stays inside WI-5035 and preserves role/dispatchability/topology boundaries.

## Spec-Derived Verification Plan

The implementation report must run and report the exact commands below, adjusting only to the repo-native interpreter if the venv path is unavailable:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dispatcher_runtime.py -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_dispatch_config.py -q --no-header
```

Expected coverage:

- `DCL-DISPATCHER-DAEMON-RECOVERY-SLA-001` and `DCL-DISPATCHER-DAEMON-DEGRADED-CONTINUITY-001`: tests simulate repeated same-signature no-verdict worker failure and assert bounded recovery behavior: retry delay/backoff is enforced, retries do not churn on a tight cadence, circuit-breaker/quarantine state is visible when applicable, and healthy alternatives remain eligible.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` and `ADR-DISPATCHER-ARCHITECTURE-001`: tests prove the daemon/runtime still owns selection and recovery, and the fix does not require harness-side dispatch-control behavior.
- `SPEC-DISPATCH-HEALTH-STATUS-SEMANTICS-001`: health/status tests distinguish degraded recoverable runtime failure from topology failure; a backed-off or circuit-broken recipient does not make the fleet impossible when another eligible role holder exists.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`: after a future `GO`, the implementation-start helper must accept only the target paths in this proposal and the active PAUTH; no implementation begins before that packet exists.
- `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: bridge preflights must pass before filing and before `GO`/verification; the implementation report must carry forward specification links and this spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`: MemBase/project/bridge evidence must show WI-5035 linked to both its advisory and this implementation thread without resolving the work before verification evidence exists.

## Risk / Rollback

Main risk: overly aggressive backoff or quarantine could strand actionable bridge work even after the underlying harness recovers. Mitigation: make the bounded behavior observable, test the half-open/retry path, and preserve manual reset/circuit-breaker controls. Secondary risk: under-scoping the fix to one runtime path could leave daemon shadow/status decisions inconsistent with live dispatch. Mitigation: include both runtime and daemon status paths in target scope and test the path that originally surfaced the tight retry loop.

Rollback is a single focused revert of the WI-5035 implementation commit plus the post-implementation bridge report/verdict chain if verification has already proceeded. The rollback returns no-verdict handling to the previous retry cadence and should immediately restore the pre-change tests.

## Pre-Filing Checks

- Applicability preflight on the completed draft: `preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`; target paths resolved to the four inline `target_paths` entries above.
- Clause preflight on the completed draft: exit 0; `Blocking gaps (gate-failing): 0`.
- Phantom-spec sweep: 15 cited `SPEC` / `GOV` / `ADR` / `DCL` / `PB` IDs checked; missing IDs: none.
- Draft placeholder sweep: no scaffold placeholders remain.

## Bridge Filing

This proposal is filed in the bridge directory as the next status-bearing numbered
bridge file for `gtkb-wi5035-no-verdict-retry-backoff`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix(dispatch): the change repairs defective retry behavior for repeated no-verdict dispatch failures without adding a new public capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
