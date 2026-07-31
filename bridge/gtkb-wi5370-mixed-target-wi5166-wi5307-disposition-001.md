NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; owner-directed repo-wide finalization repair
author_metadata_source: explicit current Codex session metadata and transcript role declaration

# Implementation Proposal - WI-5370 WI-5166/WI-5307 mixed target disposition

bridge_kind: prime_proposal
Document: gtkb-wi5370-mixed-target-wi5166-wi5307-disposition
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi5166-nonimpairment-proposal-gate-parity-004.md", "bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md", "independent-progress-assessments/WI-5370-wi5166-wi5307-target-disposition.json"]

implementation_scope: bridge_artifact_provenance_disposition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Resolve the per-thread finalization planner STOP for `gtkb-wi5166-nonimpairment-proposal-gate-parity` without guessing ownership of shared target metadata. The planner reports `mixed_provenance_stop` because `.claude/hooks/bridge-compliance-gate.py` is claimed by both the WI-5166 terminal verdict and the WI-5307 terminal chain, even though the current scoped `git status` shows the hook path itself clean and WI-5307 version 017/018 states that no hook hunk was retained.

This proposal authorizes a documentation-only disposition manifest that captures the current source identities and recommends a safe sequencing rule for later finalization. It does not authorize committing WI-5166 source targets, committing WI-5307 source targets, editing either terminal verdict, removing either terminal verdict, or treating clean target overlap as source ownership without Loyal Opposition review.

## First-Line Role Eligibility Check

The active transcript role is Prime Builder via `::init gtkb pb`. Prime Builder is authorized to author `NEW` bridge proposals. This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, and it does not rely on `gt harness roles` for role authority.

## Current Evidence

- Planner classification for WI-5166: `mixed_provenance_stop`.
- Planner reason: one or more target paths are claimed by multiple dirty terminal VERIFIED threads.
- Planner conflicting target owner: `.claude/hooks/bridge-compliance-gate.py` claimed by `gtkb-wi5166-nonimpairment-proposal-gate-parity` and `gtkb-wi5307-shared-enforcement-baseline-disposition`.
- Current WI-5166 terminal file: `bridge/gtkb-wi5166-nonimpairment-proposal-gate-parity-004.md`, length `4666`, SHA-256 `DE4216E097517EA789A39301EF8681E1DB0C36403C9703FAFC198A97E5729452`, Git blob `0d8d659570cfdb4d0e7f2a87d4bf9ad55783945c`.
- Current WI-5307 terminal file: `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md`, latest status `VERIFIED`.
- Scoped git status currently shows `platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py` modified and both WI-5166/WI-5307 terminal verdicts untracked; it does not show `.claude/hooks/bridge-compliance-gate.py` or `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` dirty.
- WI-5307 version 017 says the live hook target and applicability preflight target are clean relative to committed HEAD, and WI-5307 version 018 repeats that only two script paths remain dirty for WI-5307.

## Requirement Sufficiency

Existing Tree Stabilization requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` requires preserving per-thread provenance instead of broad commits, `GOV-FILE-BRIDGE-AUTHORITY-001` requires bridge lifecycle authority, and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` requires exact provenance for document artifacts and target ownership.

## In-Root Placement Evidence

All declared target paths are inside `E:/GT-KB`: `bridge/gtkb-wi5166-nonimpairment-proposal-gate-parity-004.md`, `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md`, and `independent-progress-assessments/WI-5370-wi5166-wi5307-target-disposition.json`.

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
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-017.md` - reports the hook target clean and no hook hunk retained under WI-5307.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md` - LO verification of WI-5307 with residual follow-on notes.

## Owner Decisions / Input

- Owner directive in Codex task `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem is resolved.
- Owner correction in the same task: role authority is transcript-defined for this interactive Prime Builder session and is not derived from `gt harness roles`.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active owner-authorized project scope covering WI-5370 tree-stabilization repairs.

## Proposed Scope

- Reconfirm current byte identities for the WI-5166 and WI-5307 terminal verdicts immediately before writing the manifest.
- Acquire a work-intent claim for this proposal and run implementation-start authorization before writing the manifest.
- Run scoped `git status --short -- .claude/hooks/bridge-compliance-gate.py groundtruth-kb/templates/hooks/bridge-compliance-gate.py platform_tests/hooks/test_modernization_nonimpairment_proposal_gate.py scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py` and record the exact output.
- Write `independent-progress-assessments/WI-5370-wi5166-wi5307-target-disposition.json` with the planner row, current byte identities, scoped git status, and a sequencing recommendation.
- The sequencing recommendation must fail closed unless it can prove the overlapping `.claude/hooks/bridge-compliance-gate.py` target is clean and not a retained source hunk for either thread.
- File a post-implementation report through `.codex/skills/bridge/helpers/impl_report_bridge.py`.

## Out Of Scope

- No source/test/rule/runbook/config/database mutation.
- No bridge verdict removal, restoration, or replacement.
- No finalization of WI-5166 or WI-5307 source paths.
- No broad `git add`, commit, reset, checkout, clean, stash, push, release, or deployment.
- No `.git/index.lock` removal or staged-index adjustment.
- No WI-5320/WI-5328/WI-5330 dispatcher-starvation program changes.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Manifest captures planner row and scoped git status without collapsing WI-5166 and WI-5307 into one finalization commit. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge claim, implementation-start packet, and bridge implementation-report helper; Prime authors no LO-only status. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Manifest records exact current byte identities for both terminal verdicts and the scoped target status evidence. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Rerun the per-thread finalization planner and record whether the conflict remains after the disposition manifest. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve all target paths and assert their absolute paths remain under `E:/GT-KB` before manifest write. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Record claim, implementation-start, and helper-filed report evidence in the implementation report. |

## Acceptance Criteria

- The disposition manifest exists and records exact byte identities for `bridge/gtkb-wi5166-nonimpairment-proposal-gate-parity-004.md` and `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md`.
- The manifest records scoped git status for the overlapping target paths and the WI-5307 script targets.
- No source path, terminal verdict path, staged-index path, or index lock is mutated by this repair.
- The implementation report is filed as the next numbered bridge file for this proposal.
- Loyal Opposition can use the manifest to decide whether a later planner/tool refinement may treat clean target overlap as non-blocking or whether one of the terminal source threads needs a separate reissue/stand-down.

## Risks / Rollback

Risk is low because the proposal writes only a manifest and report after approval. The main risk is mistaking a clean overlapping target for ownership clearance; mitigation is to record the evidence and leave the actual finalization decision to Loyal Opposition review or a separately approved planner refinement.

## Files Expected To Change

- `independent-progress-assessments/WI-5370-wi5166-wi5307-target-disposition.json`

## Recommended Commit Type

`chore`
