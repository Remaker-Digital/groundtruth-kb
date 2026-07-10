NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 8ae8ee16-629f-4328-a797-47cb3e7a3293
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Implementation Proposal - Reconcile CLAUDE.md memory framing (line 12 vs line 36)

bridge_kind: prime_proposal
Document: gtkb-wi5123-reconcile-claude-md-memory-framing
Version: 001
Date: 2026-07-09 UTC

Project Authorization: PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION
Project: PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION
Work Item: WI-5123

target_paths: ["CLAUDE.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Finding B3 of DELIB-202665929: CLAUDE.md self-contradicts on memory (line 12 authoritative operational patterns/lessons vs line 36 state and bootstrap). Reconcile to the state/bootstrap framing. CLAUDE.md is a canonical narrative artifact requiring a formal-artifact approval packet and the GOV-01 line-limit check at implement time.

Work item description: Finding B3. CLAUDE.md:12 frames memory as operational patterns/lessons/authoritative (forbidden how-to framing) while :36 correctly says state and bootstrap. Reconcile to the state/bootstrap framing.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5123` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `CLAUDE.md`.

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

## Prior Deliberations

- `DELIB-202665929` - Diagnosis: workers drifting to off-bridge artifacts, memory, and DELIBs as operating-rule sources
- `DELIB-20264082` - Loyal Opposition Review - GOV-08 Permitted Markdown Amendment Scoping REVISED-2
- `DELIB-2686` - Loyal Opposition Review - GOV-08 Permitted Markdown Amendment Scoping REVISED-2
- `DELIB-20263643` - Loyal Opposition Verification - Agent Red Reference Adopter Framing Restoration
- `DELIB-1576` - Loyal Opposition Review - Narrative Artifact Approval Extension, Round 2

## Owner Decisions / Input

- `DELIB-202665930` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-CANONICAL-AUTHORITY-DRIFT-REMEDIATION-EXECUTION` - active project authorization covering `WI-5123`.

## Proposed Scope

- Reconcile CLAUDE.md memory framing: line 12 frames platform session memory as operational patterns/lessons and authoritative (the forbidden how-to framing) while line 36 correctly says MEMORY.md is state and bootstrap. Rewrite line 12 to the state/bootstrap framing consistent with line 36 and the non-authority boundary, preserving the GOV-01 300-line limit.

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
| `SPEC-INTAKE-bb25be` | CLAUDE.md no longer contains internally-contradictory memory-authority framing. |

## Acceptance Criteria

- CLAUDE.md presents memory consistently as non-authoritative session state/bootstrap; no line frames memory as an authoritative source of operating patterns or rules.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `CLAUDE.md`

## Recommended Commit Type

`feat`
