NEW
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-06T06-13-35Z
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex desktop interactive; resolved role prime-builder via ::open build

# Implementation Proposal - Create root-boundary exception carriers and demote DELIB sources (replacement for WI-5121)

bridge_kind: prime_proposal
Document: gtkb-wi5127-root-boundary-carrier-recovery
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5127

target_paths: ["groundtruth.db", ".claude/rules/project-root-boundary.md", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md", "groundtruth-kb/templates/rules/canonical-terminology.md", ".groundtruth/formal-artifact-approvals"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Recover the root-boundary exception carrier scope with explicit KB, narrative, template, packet, and verification targets.

Work item description: DELIB-202665933 recovery: replace WI-5121 because its GO proposal omitted the required groundtruth.db KB-mutation target. Create canonical carriers for each operative root-boundary exception, formally approve them, update project-root-boundary.md, and reconcile the adopter templates.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5127` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth.db`, `.claude/rules/project-root-boundary.md`, `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`, `groundtruth-kb/templates/rules/canonical-terminology.md`, `.groundtruth/formal-artifact-approvals`.

## Specification Links

- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.
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

## Prior Deliberations

- `DELIB-20263210` - Owner decision: authorize WI-4542 (bridge applicability-preflight SPEC_LINK heading-qualifier fix) under reliability-fixes PAUTH
- `DELIB-202665705` - WI-4981 Mid-Session Init Role Switch — Loyal Opposition Blocker Report Review (Round 2)
- `DELIB-20263309` - Impl-Auth Packet Liveness Coupling + TTL Shrink Proposal Review
- `DELIB-20260684` - Loyal Opposition Verification - Implementation-Start Target-Paths Preflight
- `DELIB-20261258` - Loyal Opposition Verification - Implementation-Start Target-Paths Preflight

## Owner Decisions / Input

- `DELIB-202665933` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-CARRIER-RECOVERY` - active project authorization covering `WI-5127`.

## Proposed Scope

- Create canonical MemBase carriers for every operative root-boundary exception currently sourced solely to a DELIB.
- Update the root-boundary rule and adopter templates to cite carriers as authority and DELIBs only as provenance.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `SPEC-INTAKE-bb25be` | Verify all exception carriers exist and each affected rule/template has canonical authority citations. |
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

## Acceptance Criteria

- Each operative exception cites a canonical carrier rather than a DELIB as its sole authority.
- Adopter templates no longer propagate DELIB-only operating-rule authority.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `groundtruth.db`
- `.claude/rules/project-root-boundary.md`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
- `groundtruth-kb/templates/rules/canonical-terminology.md`
- `.groundtruth/formal-artifact-approvals`

## Recommended Commit Type

`feat`
