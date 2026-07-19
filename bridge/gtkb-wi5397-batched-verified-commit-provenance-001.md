NEW
author_identity: codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: 5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Implementation Proposal - Batch VERIFIED commit provenance to keep reconciler audits bounded

bridge_kind: prime_proposal
Document: gtkb-wi5397-batched-verified-commit-provenance
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5397-BATCHED-VERIFIED-COMMIT-PROVENANCE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5397

target_paths: ["scripts/bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Bound WI-5397 to a two-file reconciler optimization: batch VERIFIED commit provenance once per audit and reuse it during terminal closure checks while preserving all existing fail-closed coverage semantics.

Work item description: A 2026-07-16 live WI-5383 dry-run+repair-overbroad audit classified 86 open candidates and 615 reconciler-resolved rows correctly with zero errors, but required approximately 29 minutes because terminal commit coverage launches multiple serial Git subprocesses per VERIFIED thread. Preserve fail-closed verdict and target-path coverage semantics while building one bounded Git provenance index or equivalent batch query reused across the inventory. Full-audit subprocess fan-out must be independent of VERIFIED-thread population, targeted and full results must remain identical, and no database, bridge, dispatcher, TAFE, lease, eligibility, or Git mutation is authorized by this candidate.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5397` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_verified_backlog_reconciler.py`, `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`.

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
- `GOV-WORK-TREE-HYGIENE-001` - auto-linked governing or work-item specification.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - requires bounded PAUTH envelopes for new authorization state.

## Prior Deliberations

- `DELIB-20263482` - WI-4528 Shared Bridge Evidence Batch Defect
- `DELIB-20265757` - Verdict
- `DELIB-20260710-GTKB-MODERNIZATION-GIT-AUTHORITY-TRANSITION-COMPLETION` - Git authority transition activated and verified
- `DELIB-202665152` - NO-GO: WI-4944 -- Git metadata permission blocker sustained (no focused commit exists)
- `DELIB-20260710-GTKB-MODERNIZATION-BRANCH-BINDING-BOOTSTRAP-DCL-V2-CANDIDATE` - Candidate v2 branch-binding DCL with one-time bootstrap

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner-decision evidence supplied to this command.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5397-BATCHED-VERIFIED-COMMIT-PROVENANCE-20260717` - active project authorization covering `WI-5397`.

## Proposed Scope

- Add a bounded Git commit-provenance/changed-path index for VERIFIED terminal verdict coverage checks in scripts/bridge_verified_backlog_reconciler.py.
- Reuse the provenance index across candidate classification so full reconciler audits do not spawn per-thread serial Git history probes.
- Preserve existing fail-closed semantics for uncommitted terminal verdicts, malformed target_paths metadata, missing target coverage, NO-ACTION responses, by-reference waiver handling, and bridge-only closures.
- Do not mutate MemBase, bridge files, dispatcher state, TAFE state, leases, eligibility, or Git repository state except through the existing explicit --apply reconciler mode.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Run the bridge proposal preflights and confirm the implementation report cites exact GO, claim, implementation-start packet, and the two approved target paths. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run python -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --tb=short and include the bounded-Git-probe regression. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Confirm project, WI, PAUTH, target_paths, and owner decision metadata in the bridge proposal and report. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-WORK-TREE-HYGIENE-001` | Run git diff --check and a scoped diff review against the two approved target paths to confirm no unrelated files or semantics are captured. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Run implementation_authorization.py begin before any protected mutation and confirm only scripts/bridge_verified_backlog_reconciler.py plus its focused platform test are authorized. |

## Acceptance Criteria

- Full-audit Git subprocess count is bounded by repository/provenance index construction rather than by VERIFIED-thread population.
- Existing targeted closure classifications remain byte-equivalent for focused commit, missing coverage, untracked terminal verdict, by-reference waiver, NO-ACTION, malformed target metadata, and bridge-only cases.
- Regression coverage proves many VERIFIED threads reuse the same provenance index and do not call git log/diff-tree per thread.
- Focused tests for bridge_verified_backlog_reconciler pass, with no source/test path outside the two approved files.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `scripts/bridge_verified_backlog_reconciler.py`
- `platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`

## Recommended Commit Type

`feat`
