NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8ae8ee16-629f-4328-a797-47cb3e7a3293
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Formalize root-boundary exceptions as canonical carriers; demote DELIBs to provenance; fix adopter templates

bridge_kind: prime_proposal
Document: gtkb-wi5121-formalize-root-boundary-exception-carriers
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5121

target_paths: [".claude/rules/project-root-boundary.md", "groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md", "groundtruth-kb/templates/rules/canonical-terminology.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Finding B2 of DELIB-202665929: root-boundary exceptions carve out a no-exceptions hard rule with a DELIB as their sole cited authority, and the pattern propagates into adopter-facing templates. Formalize canonical carriers and demote the DELIBs to provenance across the rule file and templates. Narrative-artifact edits requiring formal-artifact approval packets at implement time.

Work item description: Finding B2. project-root-boundary.md:84,113,156 source operative exceptions to a no-exceptions hard rule solely to DELIBs. Create canonical carriers, demote DELIBs to provenance, fix templates/project/upgrade-rehearsal-recipe.md and templates/rules/canonical-terminology.md.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5121` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/rules/project-root-boundary.md`, `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`, `groundtruth-kb/templates/rules/canonical-terminology.md`.

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
- `SPEC-INTAKE-bb25be` - auto-linked governing or work-item specification.
- `GOV-ENV-LOCAL-AUTHORITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20263210` - Owner decision: authorize WI-4542 (bridge applicability-preflight SPEC_LINK heading-qualifier fix) under reliability-fixes PAUTH
- `DELIB-20265660` - Loyal Opposition Verification Verdict - WI-4680 Verified Commit Atomicity
- `DELIB-20265032` - WI-4452 Named-Packet Fallback Proposal - Codex NO-GO
- `DELIB-202665546` - Loyal Opposition Verdict — WI-3400 V1 Release Strategy Advisory Disposition Capture
- `DELIB-20263259` - Verdict

## Owner Decisions / Input

- `DELIB-202665930` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` - active project authorization covering `WI-5121`.

## Proposed Scope

- Create canonical carriers (fold into the DCL/GOV that owns the root boundary, or new DCLs) for the root-boundary exceptions currently authority-sourced solely to DELIBs in project-root-boundary.md (sandbox-output, db-snapshot, external-harness-exec exceptions).
- Edit project-root-boundary.md so each exception cites its canonical carrier as authority and the DELIB appears only as provenance.
- Fix the propagated DELIB-as-sole-authority pattern in the adopter templates groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md and groundtruth-kb/templates/rules/canonical-terminology.md.

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
| `SPEC-INTAKE-bb25be` | No operative exception in project-root-boundary.md or the templates is authority-sourced solely to a DELIB; each has a canonical carrier. |
| `GOV-ENV-LOCAL-AUTHORITY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |

## Acceptance Criteria

- Each root-boundary exception in project-root-boundary.md cites a canonical carrier as authority; DELIBs appear as provenance only.
- The adopter templates no longer present a DELIB as the sole authority for a must-follow instruction.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/rules/project-root-boundary.md`
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md`
- `groundtruth-kb/templates/rules/canonical-terminology.md`

## Recommended Commit Type

`feat`
