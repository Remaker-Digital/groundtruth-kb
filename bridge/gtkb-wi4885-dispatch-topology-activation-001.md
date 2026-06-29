NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-29T00-18-00Z
author_model: GPT-5
author_model_version: Codex desktop
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; sandbox=danger-full-access

# Implementation Proposal - [Resilience P3b] Governed topology flip E->PB, A->LO + activate C(Antigravity); validate 2 PB x 4 LO multi-target selection

bridge_kind: prime_proposal
Document: gtkb-wi4885-dispatch-topology-activation
Version: 001
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4885

target_paths: ["groundtruth.db", "harness-state/harness-registry.json", "config/dispatcher/rules.toml", "harness-state/bridge-substrate.json"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Implement WI-4885 by applying the owner-authorized dispatcher resilience topology activation through governed role/config commands and validating the resulting 2 PB x 4 LO dispatch selection.

Work item description: Phase 3 companion to WI-4881 (DELIB-20266276 D0). Governed gt mode set-role: E Cursor LO->PB, A Codex PB->LO; activate harness C (currently active=False); preserve active-partition invariant. Validate the dispatcher selects across 2 PB and 4 LO under selection_order. Per-harness headless dispatch reliability (each LO emits real verdicts; each PB implements) is WI-4881 generalized to all six.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4885` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth.db`, `harness-state/harness-registry.json`, `config/dispatcher/rules.toml`, `harness-state/bridge-substrate.json`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `GOV-SESSION-ROLE-AUTHORITY-001` - auto-linked governing or work-item specification.
- `DCL-SESSION-ROLE-RESOLUTION-001` - auto-linked governing or work-item specification.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - auto-linked governing or work-item specification.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - auto-linked governing or work-item specification.
- `DCL-DISPATCH-ENVELOPE-RULES-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266138` - Owner decision: minimum-viable black-box dispatcher activation, driven autonomously
- `DELIB-20266268` - Owner decision: clear daemon residue WIs (WI-4859, WI-4861) before PHASE-Y
- `DELIB-20266272` - Owner decision: PHASE-Y full daemon go-live
- `DELIB-DISPATCHER-CLAUDE-CURSOR-HARDEN-FIRST-20260626` - Dispatcher daemon Claude+Cursor headless collaboration: harden-first, go-live-later
- `DELIB-20266133` - Owner decision: re-home all open DISPATCHER-COMPLETION work and retire the project

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION` - active project authorization covering `WI-4885`.

## Proposed Scope

- Use governed CLI surfaces to apply the WI-4885 topology: Cursor E remains Prime Builder, Codex A moves to Loyal Opposition for dispatch routing, and Antigravity C is reactivated as a Loyal Opposition dispatch target.
- Preserve the active-partition invariant and do not hand-edit generated registry projection files; regenerate projections through the canonical harness projection writer.
- Validate selected dispatch targets report two Prime Builder recipients and four Loyal Opposition recipients under the configured selection order, or document any harness-specific non-dispatchable status as a blocking finding before mutation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-SESSION-ROLE-AUTHORITY-001` | gt harness roles and gt bridge dispatch status --json show the expected role/status split without treating registry role as interactive-session authority. |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | gt bridge dispatch status --json reports selected_by_role with two Prime Builder and four Loyal Opposition candidates, or emits a fail-closed blocking diagnostic. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001` | gt bridge dispatch config --json validates dispatcher rules and harness eligibility after the topology update. |
| `DCL-DISPATCH-ENVELOPE-RULES-001` | python -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short validates per-role cap and selection-order behavior. |

## Acceptance Criteria

- Live dispatch status shows the intended 2 PB x 4 LO topology after command-mediated registry/config updates.
- Codex interactive session role remains governed by this automation prompt; durable dispatch-role changes do not authorize same-session LO review.
- Topology change is reversible through the governed gt mode / dispatcher configuration commands and does not restore retired poller machinery.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`
- `harness-state/harness-registry.json`
- `config/dispatcher/rules.toml`
- `harness-state/bridge-substrate.json`

## Recommended Commit Type

`feat`
