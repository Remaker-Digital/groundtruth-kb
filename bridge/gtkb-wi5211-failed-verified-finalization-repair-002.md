REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Revised Implementation Proposal - WI-5211 Failed VERIFIED Finalization Repair

bridge_kind: prime_proposal
Document: gtkb-wi5211-failed-verified-finalization-repair
Version: 002
Responds to: bridge/gtkb-wi5211-failed-verified-finalization-repair-001.md
Date: 2026-07-16 UTC
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370
Intent: bounded terminal-verdict finalization repair

## Revision Summary

This revision keeps the same two repair target paths as version 001 but corrects the backlog anchor. Version 001 cited the original work item `WI-5211`, which is already marked resolved by the bridge VERIFIED backlog reconciler even though its finalization residue remains dirty. That resolved-WI citation can trigger dispatcher terminal-work-item reconciliation. This version cites live umbrella work item `WI-5370`, created for the repo-wide failed VERIFIED finalization residue repair lane.

target_paths: ["bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md", "independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md"]

## First-Line Role Eligibility Check

- Resolved active lane: Prime Builder / Codex harness A via `::init gtkb pb`; the current session envelope validates worker role provenance as `prime-builder/codex` with `role_resolution_source=transcript_init_keyword`.
- Status authored here: `REVISED`, a Prime Builder proposal status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- This proposal does not author any `GO`, `NO-GO`, or `VERIFIED` status and does not perform the repair.

## Current Evidence

- Failed terminal verdict: `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md`.
- Archive target: `independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md`.
- Original source thread: `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-*`.
- Current failed verdict size: `9564` bytes.
- Current failed verdict SHA-256: `33D3D8A5A3ADA011C75AAC7A16559245D9EA025A6C140AD93E8AD45F3CD3C76D`.
- Current failed verdict author session context: `2026-07-16T17-30-01Z-loyal-opposition-E-5af098`.
- The failed verdict starts with `VERIFIED`, responds to `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-007.md`, and lacks `## Commit Finalization Evidence`.
- Original implementation target paths remain `scripts/openrouter_harness.py`; this repair does not stage or mutate those paths.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`: repo hygiene recovery must avoid broad unrelated commits and preserve per-thread provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: Prime Builder may file `REVISED`; Loyal Opposition must author any replacement `VERIFIED` verdict.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: terminal VERIFIED finalization must carry specification-derived verification evidence and use the governed finalizer.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this repair proposal links scope and verification to governing specs before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: proposal carries live PAUTH/project/work-item linkage through `WI-5370`.

## Prior Deliberations

- `DELIB-202666332`: tree stabilization project authorization requires per-thread reconciliation rather than a blind repo-wide commit.
- `DELIB-202666274`: work-tree hygiene policy requires resolving uncommitted sprawl while preserving bridge audit provenance.
- `bridge/gtkb-wi5027-worktree-finalization-commit-discipline-lapse-*`: resolved precedent for large uncommitted bridge/source sprawl through bounded, provenance-preserving reconciliation instead of a bulk sweep commit.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-*`: direct current precedent for archiving an untracked failed terminal verdict and restoring the original thread to a reviewable latest state.
- `WI-5370`: live umbrella work item for resolved-WI failed-verdict residue repair.

## Requirement Sufficiency

Existing requirements sufficient. Existing governance, WI-5370, and precedent are sufficient for this bounded file-state repair. This is not a new product requirement or a change to the original implementation behavior; it is a bounded bridge/file finalization repair so the original reviewed thread can be re-finalized through the mandatory helper.

## Proposed Implementation Steps

1. Reconfirm that `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` is still untracked, terminal `VERIFIED`, lacks commit-finalization evidence, and has the recorded byte length/hash or a freshly recorded replacement hash.
2. Copy that exact file to `independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md` as the audit archive.
3. Verify source and archive byte length, SHA-256, and git blob hash match exactly.
4. Remove only `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md`.
5. Verify `gt bridge show gtkb-wi5211-df-governed-verdict-publication-parity --json --compact` reports latest `NEW` at version `007`.
6. File a Prime Builder implementation report for this repair thread with the hash evidence and path state.
7. Have Loyal Opposition review this repair and, separately, reissue the original terminal verdict via `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, including the original target paths and bridge chain.

## Explicit Non-Goals

- Do not stage, commit, modify, or restore original implementation source/test/doc paths under this repair thread.
- Do not author or self-verify a replacement terminal `VERIFIED` verdict from Prime Builder.
- Do not touch WI-5320, WI-5328, WI-5330, dispatcher-starvation implementation work, `groundtruth.db`, or unrelated bridge/source dirt as part of this repair.
- Do not run a broad sweep commit or stage unrelated paths.

## Required Specification-Derived Verification Plan

- `GOV-WORK-TREE-HYGIENE-001`: show `git status --short --untracked-files=all --` for the two repair target paths before and after repair; prove no unrelated path was mutated by this repair.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: show the repair report is `NEW` by Prime Builder and any final terminal replacement is `VERIFIED` by Loyal Opposition only.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: verify the original replacement verdict is produced through `write_verdict.py --finalize-verified`, not by direct file writing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: show this proposal and the implementation report carry the same exact target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: show PAUTH/project/work-item fields remain present and resolve to live `WI-5370`.

## Acceptance Criteria

- The failed terminal verdict is preserved byte-for-byte at `independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md`.
- The untracked failed verdict file `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` is removed and no original source/test/doc file is mutated by this repair.
- The original bridge thread returns to latest `NEW` at version `007` until Loyal Opposition reissues a governed `VERIFIED` verdict.
- A later valid finalization commit can include the original implementation paths and reissued terminal verdict while preserving the failed-verdict archive as audit evidence if the finalizer stages it.

## Risk and Rollback

Risk is low because the repair is limited to a single untracked terminal verdict file and a single audit archive. Rollback is to restore `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` from the archive, which is why byte-for-byte verification is required before deletion.

## Recommended Commit Type

`chore`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
