NEW

# WI-4620 Covered-By WI-4556 Dispatch Liveness Reconciliation

bridge_kind: prime_proposal
Document: gtkb-wi4620-covered-by-wi4556-dispatch-liveness-reconciliation
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-19 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-19T02-58-00Z-prime-builder-A-c0ffee
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Prime Builder; Hygiene PB

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4620

target_paths: ["groundtruth.db"]
implementation_scope: membase_work_item_reconciliation
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

WI-4620 remains open in PROJECT-GTKB-MAY29-HYGIENE, but its described failure class is already covered by the VERIFIED WI-4556 dispatch reliability thread gtkb-wi-4556-ollama-provider-fallback-backoff.

WI-4620 asks for deterministic liveness handling when Loyal Opposition review providers produce no bridge verdict files while dispatch diagnostics otherwise treat the selected signature as dispatched, healthy, or unchanged. The VERIFIED WI-4556 implementation added that behavior for the post-launch no-verdict path: an exit-0 Loyal Opposition worker that produces no bridge verdict now records no_verdict_produced, treats the provider as temporarily failed, backs off the failed target, and selects the next eligible Loyal Opposition backend. The same verified lane covers fatal worker-output markers such as max-turn exhaustion.

This proposal requests a narrow backlog reconciliation only: after LO review, update WI-4620 in MemBase to resolved, record bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md as completion evidence, and leave source/test files untouched.

## Duplicate-Effort And Scope Check

This proposal deliberately does not open a second source-change thread for fallback/backoff or worker root-cause repair.

- WI-4556 is already VERIFIED and owns provider/output failure fallback and backoff.
- WI-4662 owns the broader repeated previous_launch_failed relogging, cooldown-clear, and failover problem.
- WI-4670 owns the cloud-worker review failure root-cause investigation.
- WI-4480 owns cap-2 oldest-first starvation and fairness.

The only proposed mutation here is the MemBase work-item status reconciliation for a stale-open May29 Hygiene item whose behavior is now covered by verified work.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - The reconciliation changes canonical project state, so PB must route it through the governed bridge.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - This proposal cites the requirements governing project/backlog reconciliation and verified dispatch behavior.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - The proposal carries project, work-item, and project-authorization metadata.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - The closure claim depends on already-VERIFIED WI-4556 behavior tests and must be reproducible by LO.
- GOV-STANDING-BACKLOG-001 - Stale open work items should be reconciled when verified work has already closed the underlying issue.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 - The active May29 Hygiene authorization allows PB to propose implementation for unimplemented project work items.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - The observed stale work-item state crosses the threshold for durable artifact reconciliation rather than chat memory.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - The work item, bridge verdict, and verification evidence should form a consistent artifact graph.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - A work item with verified covering evidence should transition to a terminal/resolved state.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 - Dispatch state must reflect actual work delivery evidence, not only process launch.
- SPEC-DISPATCH-ENVELOPE-ELEMENT-001 - Failure/fallback handling must preserve role, harness, selected batch, and prompt/envelope identity.
- DCL-DISPATCH-ENVELOPE-RULES-001 - Fallback must honor configured eligibility and dispatchability constraints.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - The mutation target is the in-root GT-KB MemBase database, not an external artifact.

## Prior Deliberations

- DELIB-20263381 / AUQ-2026-06-14-COST-AUTODISPATCH-WI-4556 - Owner authorization for bounded WI-4556 provider-failure handling, fallback/backoff behavior, stale worker suppression, and focused regression tests.
- DELIB-20261075 - Dispatch reliability investigation identifying max-turn exhaustion, no-verdict completion, missing outcome feedback, and self-review guard issues.
- DELIB-20263076 - Ordered fallback routing GO for WI-4484; WI-4556 builds on that substrate rather than duplicating it.
- DELIB-20263438 - Owner decision that role assignment, dispatchability, and rule-based routing are independent.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - Supports deterministic backlog updates instead of remembered stale-open exceptions.
- bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md - VERIFIED the no-verdict and fatal-output fallback/backoff behavior that covers WI-4620.

## Owner Decisions / Input

No new owner decision is required for this reconciliation proposal. The active May29 Hygiene authorization covers proposal filing for unimplemented work items, and this bridge proposal does not execute the MemBase update until LO reviews and returns GO.

If GO is returned, the backlog CLI will require --owner-approved to resolve a defect work item under GOV-15. That flag should be supplied as the command-level evidence marker for the already-recorded project authorization PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION and owner decision DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617, matching the existing WI-4616 reconciliation pattern.

## Requirement Sufficiency

Existing requirements are sufficient. The work is a scoped backlog-state reconciliation backed by a VERIFIED bridge thread, not a new behavior change. No new GOV, ADR, DCL, SPEC, or PB mutation is proposed.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | Yes | Do not expose credentials; update only work-item status metadata. | Secret scan on the bridge file and commit hook. | |
| CQ-PATHS-001 | Yes | Limit the implementation target to groundtruth.db. | git diff --name-only -- groundtruth.db after implementation. | |
| CQ-COMPLEXITY-001 | N/A | No source code is changed. | Diff review. | MemBase reconciliation only. |
| CQ-CONSTANTS-001 | N/A | No runtime constants are changed. | Diff review. | MemBase reconciliation only. |
| CQ-SECURITY-001 | Yes | Do not bypass bridge approval; use the governed backlog CLI after GO. | Implementation-start packet and command transcript. | |
| CQ-DOCS-001 | Yes | Preserve status detail and related bridge evidence in the work item. | gt backlog show WI-4620 --json after implementation. | |
| CQ-TESTS-001 | Yes | Reuse verified WI-4556 behavior evidence and run read-back checks for work-item state. | gt backlog show WI-4620 --json plus cited VERIFIED bridge thread. | No source behavior changes. |
| CQ-LOGGING-001 | N/A | No logging behavior changes. | Diff review. | MemBase reconciliation only. |
| CQ-VERIFICATION-001 | Yes | LO can verify before/after work-item state and covering VERIFIED thread. | Pre/post gt backlog show output and bridge-thread inspection. | |

## Specification-Derived Verification Plan

- GOV-FILE-BRIDGE-AUTHORITY-001: File this proposal through the governed bridge helper and inspect it with gt bridge show gtkb-wi4620-covered-by-wi4556-dispatch-liveness-reconciliation --json. Expected result: latest status is NEW.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001: Run python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4620-covered-by-wi4556-dispatch-liveness-reconciliation --json. Expected result: no missing required specs.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001: Inspect this proposal header and gt projects show PROJECT-GTKB-MAY29-HYGIENE --json. Expected result: WI-4620 is linked to the project and the project authorization is active.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 and dispatch requirements: inspect bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md and run focused WI-4556 behavior tests if needed. Expected result: the verified thread reports test_lo_exit_zero_without_verdict_backs_off_and_falls_back and test_lo_provider_failure_backoff_falls_back_after_max_turn_marker passing, proving no-verdict and fatal-output dispatch failures become observable failure/backoff/fallback evidence.
- GOV-STANDING-BACKLOG-001 and artifact lifecycle requirements: run gt backlog show WI-4620 --json before and after implementation. Expected result after implementation: resolution_status and stage are resolved, with related bridge/status detail pointing to bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md.

Proposed implementation command after GO:

```text
gt backlog update WI-4620 --resolution-status resolved --stage resolved --related-bridge-threads "[\"bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md\"]" --status-detail "Resolved as covered by VERIFIED bridge/gtkb-wi-4556-ollama-provider-fallback-backoff-006.md; WI-4556 behavior tests verify exit-0 no-verdict workers record no_verdict_produced, back off the failed LO target, and select the next eligible LO backend, covering the WI-4620 liveness failure class." --owner-approved --change-reason "May29 Hygiene reconciliation: close WI-4620 as covered by VERIFIED WI-4556 dispatch liveness behavior." --json
```

## Risk / Rollback

Risk is low but not zero: closing a work item by coverage rather than a direct WI-id implementation bridge could hide residual scope if WI-4620 intended a separate diagnostic surface beyond the verified WI-4556 behavior. Mitigation: LO should inspect the WI text, the verified WI-4556 thread, and the proposed status detail before GO. Any broader residual remains tracked by WI-4662, WI-4670, and WI-4480 rather than by this May29 reconciliation.

Rollback is a follow-up backlog update that restores WI-4620 to open and records why the covering evidence was insufficient. No source/test files are changed.

## Bridge Filing

This proposal is filed under bridge/ as the first status-bearing numbered bridge file for gtkb-wi4620-covered-by-wi4556-dispatch-liveness-reconciliation; no prior version is deleted or rewritten.

## Recommended Commit Type

chore: the eventual implementation reconciles backlog state only.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
