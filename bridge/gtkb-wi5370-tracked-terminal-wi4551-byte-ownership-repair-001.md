NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb; owner-directed repo-wide finalization repair
author_metadata_source: explicit current Codex session metadata and transcript role declaration

# Implementation Proposal - WI-5370 tracked terminal byte-ownership repair for WI-4551 unified policy registry slice 1

bridge_kind: prime_proposal
Document: gtkb-wi5370-tracked-terminal-wi4551-byte-ownership-repair
Version: 001
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

target_paths: ["bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md", "independent-progress-assessments/WI-5370-gtkb-wi4551-unified-policy-registry-slice-1-004.current-modified-terminal.md"]

implementation_scope: bridge_artifact_provenance_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Repair one tracked terminal VERIFIED bridge artifact whose working-tree bytes differ from the committed HEAD bytes. The per-thread repair planner correctly stops because a tracked modified terminal verdict cannot be finalized or committed without exact byte ownership evidence.

This proposal authorizes only a byte-preserving archive of the current modified verdict bytes, followed by restoration of the tracked bridge file to the committed HEAD blob if and only if all identity checks still match. It does not authorize implementation source, test, rule, runbook, dispatcher, database, index-lock, staged-index, push, release, deployment, or broad git cleanup.

## First-Line Role Eligibility Check

The active transcript role is Prime Builder via `::init gtkb pb`. Prime Builder is authorized to author `NEW` bridge proposals. This proposal does not author `GO`, `NO-GO`, or `VERIFIED`, and it does not rely on `gt harness roles` for role authority.

## Current Evidence

- Planner classification: `mixed_provenance_stop`.
- Planner reason: tracked modified terminal VERIFIED verdict requires exact byte ownership and finalization evidence.
- Source artifact: `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md`.
- Current working-tree bytes: length `1797`, SHA-256 `E38C184A1EE55856CA6185CAE1671EDE84B2975F6140F958FB95C449076D73A1`, Git blob `6112c737160edb16d5e308a8cfe7cdcb9f003263`.
- Committed HEAD bytes: length `3741`, SHA-256 `917939EBDA325AB70BD71A4682237F2DEFA21E28EF88E12762599F3FD9EE0A7F`, Git blob `ad878dff959878969ceb276b610d07d1f87d1401`.
- Observed diff shape: the committed Antigravity-authored version was replaced in the worktree by a shorter Cursor-authored verification body.
- Work items in source thread: WI-4550, WI-4551, WI-4552, WI-4553.

## Requirement Sufficiency

Existing Tree Stabilization requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` requires preserving per-thread provenance instead of broad commits, `GOV-FILE-BRIDGE-AUTHORITY-001` requires bridge lifecycle authority, and `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` requires exact byte provenance for document artifacts.

## In-Root Placement Evidence

Both declared target paths are inside `E:/GT-KB`: `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` and `independent-progress-assessments/WI-5370-gtkb-wi4551-unified-policy-registry-slice-1-004.current-modified-terminal.md`.

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
- `bridge/gtkb-wi5370-per-thread-finalization-repair-tool-runbook-001.md` through its terminal review - WI-5370 repair tooling and runbook precedent.

## Owner Decisions / Input

- Owner directive in Codex task `019f6bf6-3e6d-7761-be14-fb894a0e84d2`: keep working until the repo-wide uncommitted-file sprawl problem is resolved.
- Owner correction in the same task: role authority is transcript-defined for this interactive Prime Builder session and is not derived from `gt harness roles`.
- `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE` - active owner-authorized project scope covering WI-5370 tree-stabilization repairs.

## Proposed Scope

- Reconfirm immediately before mutation that `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` still has current length `1797`, SHA-256 `E38C184A1EE55856CA6185CAE1671EDE84B2975F6140F958FB95C449076D73A1`, and Git blob `6112c737160edb16d5e308a8cfe7cdcb9f003263`.
- Reconfirm the committed HEAD identity for `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` is blob `ad878dff959878969ceb276b610d07d1f87d1401` with SHA-256 `917939EBDA325AB70BD71A4682237F2DEFA21E28EF88E12762599F3FD9EE0A7F`.
- Acquire a work-intent claim for this proposal and run implementation-start authorization before any file mutation.
- Copy the exact current working-tree bytes to `independent-progress-assessments/WI-5370-gtkb-wi4551-unified-policy-registry-slice-1-004.current-modified-terminal.md` after verifying both absolute paths remain under `E:/GT-KB`.
- Verify archive byte length, SHA-256, Git blob, and raw byte equality against the source before altering the source path.
- Restore only `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` to the committed HEAD blob `ad878dff959878969ceb276b610d07d1f87d1401` after archive identity passes.
- Verify `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` is clean relative to HEAD and the archive remains byte-identical to the pre-repair current bytes.
- File a post-implementation report through `.codex/skills/bridge/helpers/impl_report_bridge.py`.

## Out Of Scope

- No broad `git add`, commit, reset, checkout, clean, stash, push, release, or deployment.
- No source/test/rule/runbook/config/database mutation.
- No `.git/index.lock` removal or staged-index adjustment.
- No WI-5320/WI-5328/WI-5330 dispatcher-starvation program changes.
- No mutation if the current live bytes no longer match the identity recorded in this proposal.
- No decision that the archived modified bytes are a valid replacement terminal verdict; any such replacement must be filed through a separate governed bridge path.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | Capture scoped git status before and after; confirm only the source verdict restoration and archive creation occurred. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Use bridge claim, implementation-start packet, and bridge implementation-report helper; Prime authors no LO-only status. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Compare source/archive byte length, SHA-256, Git blob, and raw bytes before source restoration. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Rerun `scripts/per_thread_finalization_repair.py --format json --exclude-wi WI-5320 --exclude-wi WI-5328 --exclude-wi WI-5330` and confirm this thread no longer reports `mixed_provenance_stop`. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve both target paths and assert their absolute paths remain under `E:/GT-KB` before mutation. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Record claim, implementation-start, and helper-filed report evidence in the implementation report. |

## Acceptance Criteria

- `independent-progress-assessments/WI-5370-gtkb-wi4551-unified-policy-registry-slice-1-004.current-modified-terminal.md` exists and is byte-identical to the current pre-repair working-tree bytes of `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md`.
- `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` is restored to committed HEAD blob `ad878dff959878969ceb276b610d07d1f87d1401` and no longer appears as a tracked modification.
- The staged index remains exactly unchanged, including the existing staged WI-5318 path if it is still present.
- The per-thread finalization planner no longer classifies this source thread as `mixed_provenance_stop` for a tracked modified terminal verdict.
- The implementation report is filed as the next numbered bridge file for this proposal.

## Risks / Rollback

Risk is bounded to one tracked bridge verdict file plus one archive. The main risk is another session changing the live bytes between review and implementation; mitigation is mandatory pre-mutation byte identity checking and fail-closed behavior. Rollback, if needed before verification, is to restore the archived bytes to `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md` after validating the archive hash.

## Files Expected To Change

- `bridge/gtkb-wi4551-unified-policy-registry-slice-1-004.md`
- `independent-progress-assessments/WI-5370-gtkb-wi4551-unified-policy-registry-slice-1-004.current-modified-terminal.md`

## Recommended Commit Type

`chore`
