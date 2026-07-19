NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; owner-directed repo-wide finalization repair
author_metadata_source: explicit current Codex session metadata and transcript role declaration

# Implementation Proposal - WI-5370 current-byte dispatcher black-box no-responds repair

bridge_kind: prime_proposal
Document: gtkb-wi5370-current-byte-dispatcher-black-box-spec-foundation-015-repair
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-dispatcher-black-box-spec-foundation-015.md", "independent-progress-assessments/WI-5370-gtkb-dispatcher-black-box-spec-foundation-015.current-1548.no-responds-terminal.md"]

implementation_scope: bridge_artifact_provenance_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Archive and remove only the current live bytes of `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md`. The prior WI-5370 no-responds repair for this source thread removed `bridge/gtkb-dispatcher-black-box-spec-foundation-014.md`, but a newer untracked terminal `VERIFIED` file now exists at version 015 and still has no `Responds to` report reference.

The current live version 015 file is 1,548 bytes with SHA-256 `34ABBF8F97E74832F64A282528F64D042AC953B47CB88F8E381508C7DE0B8809` and Git blob `d0689cf4ea0c1d8312e5a361c7d6d737e611a4f0`. This proposal is current-byte scoped so it cannot accidentally reuse the stale version 014 repair approval.

## First-Line Role Eligibility Check

The active transcript role is Prime Builder via `::init gtkb pb`. Prime Builder is authorized to author `NEW` bridge proposals. This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, and it does not rely on `gt harness roles` for role authority.

## Current Evidence

- Planner classification: `terminal_verified_blocked_missing_scope`.
- Planner reason: latest VERIFIED verdict has no Responds to report reference.
- Current latest source artifact: `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md`.
- Prior WI-5370 repair artifact: `bridge/gtkb-wi5370-no-responds-dispatcher-black-box-spec-foundation-004.md`, which verified archival/removal of version 014 only.
- Current live bytes: length `1548`, SHA-256 `34ABBF8F97E74832F64A282528F64D042AC953B47CB88F8E381508C7DE0B8809`, Git blob `d0689cf4ea0c1d8312e5a361c7d6d737e611a4f0`.
- Work items in source thread: WI-5172, WI-5220, WI-5254, WI-5268, WI-5269, WI-5276.

## Requirement Sufficiency

Existing Tree Stabilization requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` requires preserving per-thread provenance instead of broad commits, `GOV-FILE-BRIDGE-AUTHORITY-001` requires bridge lifecycle authority, and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` requires exact byte provenance for document artifacts.

## In-Root Placement Evidence

Both declared target paths are inside `E:/GT-KB`: `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md` and `independent-progress-assessments/WI-5370-gtkb-dispatcher-black-box-spec-foundation-015.current-1548.no-responds-terminal.md`.

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

## Prior Deliberations

- `bridge/gtkb-wi5027-worktree-finalization-triage-004.md` - resolved precedent: do not bulk-commit ambiguous bridge/source sprawl; classify and preserve per-thread ownership.
- `docs/procedures/per-thread-finalization-repair.md` - current runbook requiring one-thread-at-a-time repair and STOP on mixed provenance.
- `bridge/gtkb-wi5370-no-responds-dispatcher-black-box-spec-foundation-004.md` - prior repair verified archival/removal of version 014, not the current version 015 artifact.

## Owner Decisions / Input

- Owner directive in Codex task `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem is resolved.
- Owner correction in the same task: role authority is transcript-defined for this interactive Prime Builder session and is not derived from `gt harness roles`.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active owner-authorized project scope covering WI-5370 tree-stabilization repairs.

## Proposed Scope

- Reconfirm immediately before mutation that `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md` still has length `1548`, SHA-256 `34ABBF8F97E74832F64A282528F64D042AC953B47CB88F8E381508C7DE0B8809`, and Git blob `d0689cf4ea0c1d8312e5a361c7d6d737e611a4f0`.
- Acquire a work-intent claim for this proposal and run implementation-start authorization before any file mutation.
- Copy the exact live bytes to `independent-progress-assessments/WI-5370-gtkb-dispatcher-black-box-spec-foundation-015.current-1548.no-responds-terminal.md` after verifying both absolute paths remain under `E:/GT-KB`.
- Verify source/archive byte length, SHA-256, Git blob, and raw byte equality before deleting the source.
- Remove only `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md` after archive identity passes.
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
| `GOV-WORK-TREE-HYGIENE-001` | Capture scoped git status and planner counts before and after; confirm only the source verdict removal and archive creation occurred. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge claim, implementation-start packet, and bridge implementation-report helper; Prime authors no LO-only status. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Compare source/archive byte length, SHA-256, Git blob, and raw bytes before source removal. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Rerun the per-thread finalization planner and confirm this source thread no longer reports the version 015 no-responds artifact. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both target paths and assert their absolute paths remain under `E:/GT-KB` before mutation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Record claim, implementation-start, and helper-filed report evidence in the implementation report. |

## Acceptance Criteria

- The current 1,548-byte artifact is archived byte-for-byte before source removal.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md` is absent after archive identity checks pass.
- The archive exists with SHA-256 `34ABBF8F97E74832F64A282528F64D042AC953B47CB88F8E381508C7DE0B8809` and byte-identical content.
- The staged index remains exactly unchanged, including the existing staged WI-5318 path if it is still present.
- The implementation report is filed as the next numbered bridge file for this proposal.

## Risks / Rollback

Risk is low and bounded to one bridge verdict file plus one archive. The main risk is another session changing the live source bytes between review and implementation; mitigation is a mandatory pre-mutation byte identity check and fail-closed behavior. Rollback, if needed before verification, is to restore only the archived bytes to `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md` after revalidating the archive hash.

## Files Expected To Change

- `bridge/gtkb-dispatcher-black-box-spec-foundation-015.md`
- `independent-progress-assessments/WI-5370-gtkb-dispatcher-black-box-spec-foundation-015.current-1548.no-responds-terminal.md`

## Recommended Commit Type

`chore`
