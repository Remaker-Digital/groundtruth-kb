NEW
author_identity: Prime Builder (Codex)
author_harness_id: A
author_session_context_id: 019f23f0-b16e-7481-8a18-9622ab564d50
author_model: GPT-5 Codex
author_model_version: Codex desktop runtime 2026-07-04
author_model_configuration: Codex desktop interactive Prime Builder; reasoning inherited from session

# Implementation Proposal - Phase 3 gap 05: direct manipulation prevention across controlled artifacts

bridge_kind: prime_proposal
Document: gtkb-wi4967-controlled-artifact-direct-mutation-guard
Version: 001
Date: 2026-07-04 UTC

Project Authorization: PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4967-IMPLEMENTATION-PROPOSAL-FILING
Project: PROJECT-HARNESS-EQUIVALENCE-PHASE-3
Work Item: WI-4967

target_paths: ["scripts/controlled_artifact_paths.py", "scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "scripts/check_protected_commit_authorization.py", "scripts/sdk_bridge_bash_guard.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_sdk_bridge_bash_guard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

WI-4967 first implementation slice: centralize controlled-artifact path classification and fail closed on direct MemBase, bridge status-file, and authority runtime-state mutations while preserving governed bridge writers and diagnostic state.

Work item description: Generalize the WI-4516 OpenRouter/Ollama Bash bridge-bypass precedent to all controlled artifacts and all harness tool paths, including direct DB access, direct bridge/file writes, helper bypasses, shell-mediated writes, and generated runtime-state mutation. Preserve existing WI-4516 verification as precedent, not full closure.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-4967` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/controlled_artifact_paths.py`, `scripts/implementation_start_gate.py`, `scripts/protected_mutation_guard.py`, `scripts/check_protected_commit_authorization.py`, `scripts/sdk_bridge_bash_guard.py`, `platform_tests/scripts/test_controlled_artifact_paths.py`, `platform_tests/scripts/test_implementation_start_gate.py`, `platform_tests/scripts/test_protected_mutation_guard.py`, `platform_tests/scripts/test_check_protected_commit_authorization.py`, `platform_tests/scripts/test_sdk_bridge_bash_guard.py`.

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
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - auto-linked governing or work-item specification.
- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202665173` - Verdict Summary
- `DELIB-202665176` - Verdict Summary
- `DELIB-202665184` - Verdict: NO-GO
- `DELIB-202665181` - Verdict Summary
- `DELIB-202665288` - OPS Lifecycle Protocol Foundation — NO-GO Verdict (v008)

## Owner Decisions / Input

- `DELIB-202665197` - owner-decision evidence supplied to this command.
- `PAUTH-PROJECT-HARNESS-EQUIVALENCE-PHASE-3-WI-4967-IMPLEMENTATION-PROPOSAL-FILING` - active project authorization covering `WI-4967`.

## Proposed Scope

- Introduce a shared controlled-artifact path classifier for mutation gates, preserving leading-dot paths and the no-index bridge model.
- Fail closed on direct writes to root MemBase groundtruth.db, status-bearing versioned bridge files, retired bridge/INDEX.md, and authority runtime-state subtrees while keeping diagnostic/report draft subtrees writable.
- Route bridge artifact creation through the existing governed bridge writer/helper path; do not weaken WI-4516 SDK Bash denial or claim Codex hidden .codex DACL remediation.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Focused pytest proves direct bridge status-file and bridge/INDEX writes are blocked outside the governed writer/helper route. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest and ruff check/format on exactly the touched guard and test files before filing the implementation report. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests cover hook fallback decision modules directly so Windows/native Codex sessions preserve the same fail-closed behavior. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Focused pytest proves direct groundtruth.db and runtime authority-state writes cannot bypass GO/work-intent/implementation packet gates. |
| `ADR-CROSS-HARNESS-PARITY-001` | Guard classifications are shared across Codex/Claude local gates and SDK harness Bash guard coverage rather than diverging by harness path. |

## Acceptance Criteria

- Direct apply_patch or shell writes to groundtruth.db, bridge/<slug>-NNN.md, bridge/INDEX.md, and .gtkb-state implementation authorization/work-intent/dispatcher authority state are denied with stable reason codes unless routed through the governed authority path.
- Existing proposal/report/verdict helper workflows and diagnostic .gtkb-state report draft writes remain supported.
- WI-4516 OpenRouter/Ollama bridge Bash hardening remains covered and imports or matches the same bridge-artifact classification semantics.
- Implementation report includes an Architecture Alignment Ledger citing WI-4516, WI-4975, WI-5002, WI-5008, and WI-4972 dispositions.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/controlled_artifact_paths.py`
- `scripts/implementation_start_gate.py`
- `scripts/protected_mutation_guard.py`
- `scripts/check_protected_commit_authorization.py`
- `scripts/sdk_bridge_bash_guard.py`
- `platform_tests/scripts/test_controlled_artifact_paths.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`
- `platform_tests/scripts/test_check_protected_commit_authorization.py`
- `platform_tests/scripts/test_sdk_bridge_bash_guard.py`

## Recommended Commit Type

`feat`
