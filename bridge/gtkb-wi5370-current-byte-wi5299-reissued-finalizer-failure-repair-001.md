NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - Repair current-byte WI-5299 reissued-finalizer terminal residue

bridge_kind: prime_proposal
Document: gtkb-wi5370-current-byte-wi5299-reissued-finalizer-failure-repair
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md", "independent-progress-assessments/WI-5370-gtkb-wi5299-reissued-finalizer-failure-repair-007.current-1395.no-responds-terminal.md"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Archive and remove only the current live bytes of `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md`, because the prior no-responds repair approval covered a different 1,553-byte artifact at the same path. The current live file is a 1,395-byte terminal `VERIFIED` artifact with SHA-256 `DF00B396C431E4BEC590B3F6C234D36DC031A59FCA02B3B9AA9394C5E2DA4BF6`, normalized Git blob `71e68270ad386256f0cc9405dc9ed874ab4e2ace`, and raw Git blob `5347a923fc85b6ac8bfdbc0a21fc9545217b31a2`.

This proposal does not authorize any implementation source, test, rule, runbook, dispatcher, database, index-lock, staged-index, push, release, or deployment mutation. It exists to replace the stale byte-identity repair lane with an exact current-byte repair lane.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5370` and keeps the bridge, project authorization, owner-decision, implementation-start, and Loyal Opposition verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for this proposal because the active `PROJECT-GTKB-TREE-STABILIZATION` authorization and `WI-5370` cover repo-wide finalization-sprawl repair. The proposal narrows the action to one current terminal bridge file and one archive target.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`: `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md` and `independent-progress-assessments/WI-5370-gtkb-wi5299-reissued-finalizer-failure-repair-007.current-1395.no-responds-terminal.md`.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - work-tree sprawl repair must preserve per-thread provenance and avoid broad commits.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps repair decisions as governed artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - applies project authorization and owner-decision evidence boundaries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the repair in the GT-KB root and out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - preserves tracked hygiene repair as backlog-governed work.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires self-enforced bridge and implementation-start checks in Codex.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves durable bridge/runbook evidence rather than chat-only state.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - treats this correction as a lifecycle artifact.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - requires exact byte provenance for archived document artifacts.

## Prior Deliberations

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active project-scope authorization for WI-5370.
- `bridge/gtkb-wi5370-no-responds-wi5299-reissued-finalizer-failure-repair-001.md` - stale proposal for the prior 1,553-byte artifact.
- `bridge/gtkb-wi5370-no-responds-wi5299-reissued-finalizer-failure-repair-005.md` - Prime current-state correction identifying the byte mismatch.
- `bridge/gtkb-wi5370-no-responds-wi5299-reissued-finalizer-failure-repair-006.md` - LO NO-GO confirming the source still exists and requiring a truthful repair path.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active owner-authorized project scope covering WI-5370 tree-stabilization repairs.

## Proposed Scope

- Reconfirm `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md` is the current untracked terminal `VERIFIED` artifact and still has length `1395`, SHA-256 `DF00B396C431E4BEC590B3F6C234D36DC031A59FCA02B3B9AA9394C5E2DA4BF6`, normalized Git blob `71e68270ad386256f0cc9405dc9ed874ab4e2ace`, and raw Git blob `5347a923fc85b6ac8bfdbc0a21fc9545217b31a2` immediately before mutation.
- Acquire a work-intent claim for this proposal and run `scripts/implementation_authorization.py begin` before any file mutation.
- Copy the exact live bytes to `independent-progress-assessments/WI-5370-gtkb-wi5299-reissued-finalizer-failure-repair-007.current-1395.no-responds-terminal.md` using a non-recursive native PowerShell `Copy-Item` after verifying both absolute paths remain under `E:\GT-KB`.
- Verify source/archive byte length, SHA-256, normalized Git blob, raw Git blob, and raw byte equality before deleting the source.
- Remove only `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md` using native PowerShell `Remove-Item -LiteralPath` after archive identity passes.
- File a post-implementation report through `.codex/skills/bridge/helpers/impl_report_bridge.py`.

## Out Of Scope

- No broad `git add`, commit, reset, checkout, clean, stash, push, release, or deployment.
- No source/test/rule/runbook/config/database mutation.
- No `.git/index.lock` removal or staged-index adjustment.
- No WI-5320/WI-5328/WI-5330 dispatcher-starvation program changes.
- No deletion if the current live bytes no longer match the identity recorded in this proposal.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Capture scoped git status and `git diff --cached --name-status` before and after; confirm only the source verdict removal and archive creation occurred and staged paths are unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge claim, implementation-start packet, and bridge implementation-report helper; confirm `gt bridge show gtkb-wi5299-reissued-finalizer-failure-repair --json --compact` exposes the predecessor after removal. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Compare source/archive byte length, SHA-256, normalized Git blob, raw Git blob, and raw bytes before source removal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run `validate_verified_body` against the archived body and record the canonical finalizer rejection or acceptance result in the implementation report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both target paths and assert their absolute paths remain under `E:\GT-KB` before mutation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Record claim, implementation-start, and helper-filed report evidence in the implementation report. |

## Acceptance Criteria

- The current 1,395-byte artifact is archived byte-for-byte before source removal.
- `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md` is absent after the archive identity checks pass.
- `independent-progress-assessments/WI-5370-gtkb-wi5299-reissued-finalizer-failure-repair-007.current-1395.no-responds-terminal.md` exists with SHA-256 `DF00B396C431E4BEC590B3F6C234D36DC031A59FCA02B3B9AA9394C5E2DA4BF6` and byte-identical content.
- The staged index remains exactly unchanged, including the existing staged WI-5318 path.
- The implementation report is filed as the next numbered bridge file for this proposal.

## Risks / Rollback

Risk is low and bounded to one bridge verdict file plus one archive. The main risk is another session changing the live source bytes between review and implementation; mitigation is a mandatory pre-mutation byte identity check and fail-closed behavior. Rollback, if needed before verification, is to restore only the archived bytes to `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md` after revalidating the archive hash.

## Files Expected To Change

- `bridge/gtkb-wi5299-reissued-finalizer-failure-repair-007.md`
- `independent-progress-assessments/WI-5370-gtkb-wi5299-reissued-finalizer-failure-repair-007.current-1395.no-responds-terminal.md`

## Recommended Commit Type

`chore`
