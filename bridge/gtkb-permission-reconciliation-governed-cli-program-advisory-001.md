ADVISORY
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6381-9939-7500-abd6-c73d192c8c35
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop interactive session; owner-directed bridge ADVISORY filing

bridge_kind: governance_advisory
Document: gtkb-permission-reconciliation-governed-cli-program-advisory
Version: 001
Author: Owner-directed Advisory Proposal by Prime Builder (Codex, harness A)
Date: 2026-07-15 UTC
Mode: advisory proposal
Severity: P1
Priority: P1

# Permission Reconciliation Governed CLI Program Advisory Proposal

## Source

- Owner direction in the active 2026-07-15 Prime Builder session to file this program as a proper Advisory Proposal.
- Active project `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION`.
- Governed seed work item `WI-5005` and its latest VERIFIED bridge artifact, `bridge/gtkb-wi5005-permission-reconciliation-approach-004.md`.
- The governed deliberations and specifications cited below.

Advisory Proposal is the primary Loyal Opposition means of initiating future work. An `ADVISORY` is non-dispatchable as a headless work packet and is not implementation approval, but it is intentionally available to interactive Prime Builder sessions for owner-aware disposition into projects, work items, specifications, lifecycle changes, or a later `NEW` implementation proposal.

## Claim

GT-KB should evaluate a program that makes worker-facing skills plus the `gt` CLI the normal mutation contract, backed by service/API/TAFE/MemBase authority and shared policy, audit, recovery, and denial behavior. The first candidate slice is discovery and specification, not runtime enforcement: inventory every mutating `gt` command and define the governed command manifest, risk-policy snapshot, audit-event, and recovery/import packet schemas before enforcement code is written.

The underlying architecture proposes these invariants:

- a mutating command is governed only when manifest-registered and using shared guardrails;
- commands declare facts while policy derives risk; commands may raise risk but cannot lower it;
- high-risk operations require separate scoped authority;
- manifest and risk-policy changes require owner/proxy authority plus adversarial review;
- protected/high-risk mutations fail closed on stale or invalid policy;
- low-risk operations may use a bounded last-valid snapshot grace;
- pre-mutation audit failure blocks mutation;
- post-mutation audit failure produces structured deficiency/recovery evidence;
- audit records are append-only and repair uses supplements;
- service outage recovery uses explicit packets and policy-routed reconciliation;
- after service takeover, local manifest/policy files are cache/snapshot projections and local audit files are outboxes, not competing authorities.

This is a practical compliance and serviceability program, not a claim that GT-KB can create perfect local filesystem security against a harness with unrestricted host access.

## Current Governed State

Fresh checks on 2026-07-15 found:

- `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION` remains active. The owner-required spelling `PREMISSION` is preserved in the project ID and name.
- The project scope says it is a discovery/proposal shell and that detailed implementation work items were intentionally deferred.
- Seed `WI-5005` is resolved.
- `gt bridge show gtkb-wi5005-permission-reconciliation-approach --json` reports latest `VERIFIED` at `bridge/gtkb-wi5005-permission-reconciliation-approach-004.md`.
- The project has an active proposal-filing authorization scoped to `WI-5005`, but that authorization does not approve the downstream implementation program.
- No current work item title or description was found for the exact first-slice "Governed CLI Inventory And Manifest Specification" program.

The governed project therefore has a resolved seed investigation but no current work item carrying the proposed downstream program.

## Owner Decision Needed

No additional owner decision is needed to file this ADVISORY; the owner expressly requested this Advisory Proposal.

Before detailed work items or a first implementation proposal are created, Prime Builder should obtain a current owner disposition on one question: adopt the full candidate program, adopt only the inventory/specification slice and defer the rest, or defer/retire the program in favor of newer modernization, dispatcher-black-box, LAN authority, or other overlapping work.

The cited owner decisions establish architecture intent, but this advisory is not fresh approval to instantiate all 15 work items or begin implementation.

## Recommended Prime Action

Classify this advisory as `adapt`.

1. Route it through interactive advisory intake and compare the proposal with current modernization, dispatcher-complex black-box, LAN authority service, project-authorization, audit, and service-ownership work.
2. Preserve `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION` as the existing project; do not create a duplicate umbrella.
3. Decide whether the first slice requires specification intake because it defines cross-cutting command-manifest, risk-policy, audit, and recovery schemas.
4. If adopted, create or authorize only the smallest current work item first: reproducible inventory plus specifications and static tests, with runtime enforcement explicitly out of scope.
5. Revalidate the remaining candidate work items after the first slice establishes the real command inventory and overlap map.
6. File a normal `NEW` implementation proposal only after owner/project authorization, requirement sufficiency, exact target paths, and spec-derived verification are current.

### First Candidate Slice

Governed CLI Inventory And Manifest Specification:

- inventory all mutating `gt` commands;
- classify mutation and target-resource classes;
- identify unclassified or ambiguous mutations;
- define command-manifest, risk-policy snapshot, full invocation audit-event, and recovery/import packet schemas;
- define warning-to-cutoff migration mechanics;
- map every claim to deterministic inventory and schema tests;
- exclude runtime enforcement, audit ingestion, policy refresh, and broad command rewrites.

### Candidate Downstream Program

The candidate sequence includes these later work items, all subject to fresh overlap and owner disposition:

1. Governed CLI inventory and manifest specification.
2. Manifest registry and migration warning mode.
3. Shared governed CLI validation and audit helpers.
4. Local append-only audit-log foundation.
5. Policy snapshot generation and validation.
6. Governed CLI enforcement migration slice.
7. Audit ingestion and projection service in local-compatible mode.
8. Audit-lag degradation and incident-freeze workflow.
9. LAN-service outage recovery/import packet workflow.
10. LAN authority service import-and-verify takeover path.
11. Command-manifest cutoff and fail-closed activation.
12. Dispatcher/quiesce and mutation-permission adapter integration.
13. Canonical, artifact, repository, and environment mutation integration.
14. Operator UX and dashboard visibility.
15. Full regression and adversarial-diligence test suite.

This enumeration preserves the proposal without creating those work items.

## Classification Slot

Owner-directed governance advisory. Recommended disposition: `adapt` into the existing active project, beginning with current owner disposition and specification/inventory work if adopted. Do not duplicate the project, auto-create all candidate work items, or treat the resolved seed WI as implementation approval.

## Prior Deliberations

Relevant governed owner decisions include:

- `DELIB-20260703-GTKB-MUTATION-PERMISSION-GENERAL-PRIMITIVE-FIRST`
- `DELIB-202665405` - worker-facing surface direction.
- `DELIB-202665417` - command manifest plus shared guardrails.
- `DELIB-202665419` - post-migration fail-closed treatment of unregistered mutating commands.
- `DELIB-202665423` - separate authority for high-risk invocations.
- `DELIB-202665428` - central policy registry and snapshot direction.
- `DELIB-202665438` - full invocation decision audit.
- `DELIB-202665448` - ingestion-lag and degradation direction.
- `DELIB-202665460` - service-owned/local-compatible architecture.
- `DELIB-202665468` - recovery/import packet direction.
- `DELIB-202665477`, `DELIB-202665478`, `DELIB-202665479`, and `DELIB-202665480` - first slice, completion bar, verification evidence, and package-generation decision.
- `DELIB-20260715-ADVISORY-PROPOSAL-PRIMARY-LO-INITIATION-MECHANISM`

## Related Governed Artifacts

- `PROJECT-GTKB-PREMISSION-RECONCILIATION-HARMONIZATION` - active existing project.
- `WI-5005` - resolved seed work item.
- `bridge/gtkb-wi5005-permission-reconciliation-approach-004.md` - latest VERIFIED seed thread.
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Duplicate And Supersession Check

No bridge thread named `gtkb-permission-reconciliation-governed-cli-program-advisory` existed before filing. The verified `gtkb-wi5005-permission-reconciliation-approach` thread is the seed investigation/proposal work, not a carrier for the uninstantiated 15-item program. This ADVISORY links to that verified history and routes the remaining proposal for current disposition without duplicating the project.

## Non-Approval Statement

This ADVISORY is a non-dispatchable bridge artifact and future-work initiation carrier. It is not a GO verdict, implementation proposal, project authorization, work-item authorization, work-intent claim, implementation-start packet, or permission to create all candidate work items or modify CLI, policy, audit, service, dispatcher, configuration, MemBase, tests, or other protected surfaces. Downstream implementation requires current owner/project authorization, requirement sufficiency, a normal bridge proposal, independent Loyal Opposition GO, work-intent, implementation-start, report, and verification.
