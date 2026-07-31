NEW
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-10T08-26-40Z
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; PowerShell; project root E:\GT-KB; owner goal continuation
author_metadata_source: Codex session envelope plus current runtime

# Implementation Proposal - Bridge finalization backlog: 365 uncommitted bridge files incl. 22 terminal VERIFIED + 86 WITHDRAWN never committed; auto_finalize_sweep disabled or commit-blocked - diagnose + drain

bridge_kind: prime_proposal
Document: gtkb-wi5116-bridge-finalization-backlog-diagnosis-drain
Version: 001
Date: 2026-07-10 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5116

target_paths: ["bridge", "scripts", "platform_tests", ".claude/rules/auto-finalization-sweep.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Diagnose and safely drain the remaining bridge-finalization backlog under the first stabilization wave.

Work item description: git shows 365 uncommitted bridge/*.md (92 NEW, 40 REVISED, 64 GO, 43 NO-GO, 10 NO-ACTION, 6 ADVISORY, 86 WITHDRAWN, 22 VERIFIED, 2 DEFERRED). Terminal chains (22 VERIFIED + 86 WITHDRAWN) should already be committed; the auto_finalize_sweep Stop hook is disabled or its commits are inventory-drift-gate-blocked (a failure mode documented in .claude/rules/auto-finalization-sweep.md). Diagnose root cause, then drain the terminal backlog via per-thread finalization. Phase 1-2 of the plan.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5116` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `bridge`, `scripts`, `platform_tests`, `.claude/rules/auto-finalization-sweep.md`.

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
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs bounded project implementation authority.
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - WI-5116 Phase 1: auto-finalization sweep is firing but fail-safe-skips the entire terminal backlog (metadata/scope, not commit-block)
- `DELIB-20263081` - WI-4250 Status Reconciliation Authorization - Verification Verdict
- `DELIB-20265464` - Loyal Opposition Verification Verdict - WI-4704 bridge reconciler engine
- `DELIB-20266131` - Cursor LO Bridge Auto-Process — Session S481
- `DELIB-20263466` - Loyal Opposition Advisory - WI-4443 Implementation Authorization Current Pointer Disposition

## Owner Decisions / Input

- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710` - active project authorization covering `WI-5116`.

## Proposed Scope

- Diagnose the remaining uncommitted bridge finalization backlog against live bridge status, git status, and auto-finalization sweep behavior without broad bulk mutation.
- Drain only terminal bridge chains that can be finalized in isolation under the first-wave authorization, preserving non-terminal and foreign in-flight chains.
- Add or update narrow tests or helper logic only if diagnosis shows a repeatable finalization defect within WI-5116 scope.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | latest bridge statuses are scanned from TAFE/status-bearing files and PB writes only NEW/REVISED reports |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | focused pytest/ruff verification runs for changed code, or explicit read-check rationale if no code changes |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | implementation_authorization.py begin succeeds before protected source/config/test mutation; report cites claim and packet |
| `GOV-WORK-TREE-HYGIENE-001` | git status and git diff evidence prove finalization did not sweep unrelated dirty files |

## Acceptance Criteria

- Current terminal bridge backlog is inventoried by status and provenance, with non-terminal GO/NO-GO/NEW/REVISED/ADVISORY chains excluded from terminal finalization.
- Any finalization commits are per-thread or hunk-scoped and exclude groundtruth.db, harness-state/harness-registry.json, generated projections, and unrelated dirty files.
- If source/test/helper changes are needed, focused tests and ruff gates cover the changed behavior; otherwise the implementation report records a read-check-only drain.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `bridge`
- `scripts`
- `platform_tests`
- `.claude/rules/auto-finalization-sweep.md`

## Recommended Commit Type

`feat`
