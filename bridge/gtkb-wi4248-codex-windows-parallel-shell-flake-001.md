NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f16cf-f236-7a40-8b8e-a1fe64891e7b
author_model: gpt-5-codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation Auto-builder; approval_policy=never; cwd=E:\GT-KB
author_metadata_source: automation:auto-builder

# Implementation Proposal - Diagnose Codex Windows parallel shell launch flake

bridge_kind: prime_proposal
Document: gtkb-wi4248-codex-windows-parallel-shell-flake
Version: 001
Date: 2026-06-30 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4248

target_paths: ["independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-codex-windows-parallel-shell-flake.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Proposal for WI-4248 Codex Windows parallel shell launch flake investigation under Harness Parity Phase 2.

Work item description: Investigate the intermittent Codex Desktop Windows shell launch failure observed during a multi_tool_use.parallel fan-out of shell_command reads: most child process launches failed before PowerShell execution with `windows sandbox: CreateProcessWithLogonW failed: 1056`, while one parallel read succeeded and subsequent individual shell commands worked. A later minimal five-way parallel shell probe succeeded, so current evidence suggests an intermittent Codex Windows sandbox/process-launch concurrency issue rather than a deterministic GT-KB hook failure. Diagnose recurrence conditions, capture enough telemetry to distinguish Codex runtime vs GT-KB hook/config causes, and implement a GT-KB-side mitigation only if the root cause is in project automation or if a deterministic retry/serialization wrapper is appropriate.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4248` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-codex-windows-parallel-shell-flake.md`.

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
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-20266353` - GO - gtkb-wi4896-startup-console-residual - Boot-time and Minute-cadence Windows console/focus-steal fix
- `DELIB-20266423` - Separation Check
- `DELIB-20266350` - Loyal Opposition Verification - Headless readiness and worker Python launch
- `DELIB-20266349` - Separation Check
- `DELIB-20266488` - WI-3420 (gtkb-hygiene-sweep-cli) is VERIFIED at -004 but uncommitted since S365 — 5 files in the working tree (3 untrack

## Owner Decisions / Input

- `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` - active project authorization covering `WI-4248`.

## Proposed Scope

- Investigate and document the Codex Windows parallel shell launch flake for WI-4248 without mutating protected source in this proposal. The implementation target is an additive insight report that captures reproduction evidence, failure boundary, local mitigation options, and fallback recommendation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run governed bridge proposal preflights and re-query live bridge state after filing; do not mutate protected source or tests without a later GO verdict. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | If the flake is outside GT-KB control, document the Codex fallback path and owner-visible classification in the additive report. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | For eventual implementation, capture cross-harness Windows process-launch evidence and classify whether local mitigation or upstream fallback is required. |

## Acceptance Criteria

- File an additive investigation report under independent-progress-assessments/CODEX-INSIGHT-DROPBOX covering whether the failure occurs before hooks or PowerShell, whether GT-KB can mitigate with telemetry or retry, and the recommended fallback/owner-visible classification if the defect is upstream.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-06-30-codex-windows-parallel-shell-flake.md`

## Recommended Commit Type

`feat`
