REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# REVISED Proposal - Research Clean-Branch No-Responds Terminal Repair

bridge_kind: prime_proposal
Document: gtkb-wi5370-no-responds-research-clean-branch-publication
Version: 005 (REVISED after NO-GO 004)
Responds to: bridge/gtkb-wi5370-no-responds-research-clean-branch-publication-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
target_paths: ["bridge/gtkb-research-clean-branch-publication-004.md", "independent-progress-assessments/WI-5370-gtkb-research-clean-branch-publication-004.no-responds-terminal.md"]
Recommended commit type: chore

## Revision Claim

The NO-GO at version 004 is accepted. The prior implementation report at version 003 claimed `bridge/gtkb-research-clean-branch-publication-004.md` had been removed, but the current file still exists. This revision supersedes that stale report and requests a fresh GO for the same bounded archive/remove repair against the current live bytes only.

Fresh evidence shows the current source bytes differ from the original proposal/report identities, so the implementation must re-check byte identity immediately before mutation and stop if the file changes again.

## Current Live Evidence

- Source path: `bridge/gtkb-research-clean-branch-publication-004.md`
- Current status: untracked (`??`)
- Current first line: `VERIFIED`
- Current byte length: `1016`
- Current SHA-256: `904852A150BDD42B564555379B825DB45D61B5FA98D37D11D7688C3E6AC4BCB5`
- Current Git blob (`--no-filters`): `147b588cce75355d29e1d44dbc51ac8883c23194`
- Archive target currently exists: `false`
- Canonical body validation: invalid; `VERIFIED verdict body must include Recommended commit type evidence.`

## NO-GO Finding Response

Finding: version 003 claimed removal, but the source file still exists.

Response: corrected by this revision. Prime does not ask LO to verify the stale removal report. Instead, Prime requests a fresh GO to perform the archive/remove transaction now, using the current byte identity above and preserving all original safety conditions.

## Requirement Sufficiency

Existing requirements sufficient. WI-5370, the active tree-stabilization project authorization, and the cited bridge/worktree-hygiene specifications already define the bounded archive/remove repair. No new or revised requirement is needed before implementation.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

- Owner directive in Codex task `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem is resolved.
- Owner correction in the same task: role authority is transcript-defined for this interactive Prime Builder session and is not derived from `gt harness roles`.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` remains the active owner-authorized project scope for WI-5370 tree-stabilization repairs.
- No new owner decision is required.

## Proposed Scope

1. Reconfirm the source path still exists, is untracked, starts with `VERIFIED`, and matches the current byte identity above. If it differs, stop and return a new Prime revision rather than archiving stale bytes.
2. Confirm the archive target does not already exist or, if it does, compare exact bytes and stop on mismatch.
3. Copy the source bytes to the approved archive target.
4. Verify source/archive byte length, SHA-256, Git blob hash, and byte sequence are identical.
5. Remove only `bridge/gtkb-research-clean-branch-publication-004.md`.
6. File a new implementation report with before/after status, archive identity, ignored-archive evidence, staged-index neutrality, and source-thread state after removal.

## Out Of Scope

- No source/test/rule/runbook/config/database mutation.
- No staging, commit, push, release, deployment, index reset, index lock removal, or broad cleanup.
- No WI-5320/WI-5328/WI-5330 dispatcher-starvation program changes.
- No replacement source-thread `VERIFIED` by Prime Builder.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Scoped before/after `git status --short --` for the source and archive target; confirm staged index remains unchanged. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use fresh work-intent claim, implementation-start authorization, and implementation-report helper after GO. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Record source/archive length, SHA-256, Git blob, and byte equality before deletion. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Record canonical `validate_verified_body()` rejection for the archived body; replacement finalization remains LO-only. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run bridge applicability preflight against this revised thread. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both target paths under `E:/GT-KB` before mutation. |

## Acceptance Criteria

- The current source bytes are preserved exactly at the approved archive path before deletion.
- Only `bridge/gtkb-research-clean-branch-publication-004.md` is removed.
- The staged index remains unchanged; the pre-existing staged WI-5318 path is untouched.
- The implementation report does not claim any branch publication, source change, or finalizer reissue.

## Risk And Rollback

Risk is provenance-sensitive because the current bytes changed since the stale report. The implementation must stop on any further byte change. Rollback before verification is to restore the archived bytes to the source path after revalidating the same SHA-256 and blob.
