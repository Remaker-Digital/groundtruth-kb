NEW
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role via ::init gtkb pb
author_metadata_source: explicit_interactive_session_metadata

# Implementation Proposal - WI-5211 Failed VERIFIED Finalization Repair

bridge_kind: prime_proposal
Document: gtkb-wi5211-failed-verified-finalization-repair
Version: 001
Date: 2026-07-16 UTC
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5211
Intent: bounded terminal-verdict finalization repair

## Proposal Summary

Repair one failed file-only VERIFIED bypass in the WI-5211 bridge chain without touching the already-reviewed WI-5211 source change. The current file `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` is an untracked terminal `VERIFIED` verdict authored by Loyal Opposition, but it lacks commit finalization evidence and was never landed by the mandatory `write_verdict.py --finalize-verified` path. That leaves the original WI-5211 implementation dirty and blocks repo-wide sprawl reconciliation.

This child repair applies the bounded failed-finalizer pattern: archive the exact failed verdict bytes, verify archive equality, remove only the untracked failed terminal verdict, restore the original WI-5211 thread to latest `NEW` at `007`, and allow Loyal Opposition to reissue `008` through the governed VERIFIED finalizer.

target_paths: ["bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md", "independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md"]

## First-Line Role Eligibility Check

- Resolved active lane: Prime Builder / Codex harness A via `::init gtkb pb` transcript direction and `gt harness roles` showing harness `A` with `role: ["prime-builder"]`.
- Status authored here: `NEW`, a Prime Builder proposal status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- This proposal does not author any `GO`, `NO-GO`, or `VERIFIED` status and does not perform the repair.

## Current Evidence

- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` is present as an untracked file.
- Size: `9564` bytes.
- SHA-256: `33D3D8A5A3ADA011C75AAC7A16559245D9EA025A6C140AD93E8AD45F3CD3C76D`.
- The file starts with `VERIFIED`, includes `author_session_context_id: 2026-07-16T17-30-01Z-loyal-opposition-E-5af098`, responds to `gtkb-wi5211-df-governed-verdict-publication-parity-007.md`, and lacks any `## Commit Finalization Evidence` section.
- The operative WI-5211 target set at version `007` is exactly `scripts/openrouter_harness.py`.
- `git status --short --untracked-files=all --` for the original thread shows `scripts/openrouter_harness.py` modified and bridge versions `003` through `008` untracked, so a broad commit would commingle source and failed terminal verdict state.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`: repo hygiene recovery must avoid broad unrelated commits and preserve per-thread provenance.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: Prime Builder may file `NEW`; Loyal Opposition must author any replacement `VERIFIED` verdict.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: terminal VERIFIED finalization must carry specification-derived verification evidence and use the governed finalizer.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: this repair proposal links scope and verification to governing specs before mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: proposal carries PAUTH/project/work-item linkage.

## Prior Deliberations

- `DELIB-202666332`: tree stabilization project authorization requires per-thread reconciliation rather than a blind repo-wide commit.
- `DELIB-202666274`: work-tree hygiene policy requires resolving uncommitted sprawl while preserving bridge audit provenance.
- `bridge/gtkb-wi5027-worktree-finalization-commit-discipline-lapse-*`: resolved precedent for large uncommitted bridge/source sprawl through bounded, provenance-preserving reconciliation instead of a bulk sweep commit.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-*`: direct current precedent for archiving an untracked failed terminal verdict and restoring the original thread to a reviewable latest state.
- `bridge/gtkb-wi5351-failed-verified-finalization-repair-001.md` and `bridge/gtkb-wi5345-failed-verified-finalization-repair-001.md`: sibling applications of the same repair pattern.
- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-005.md` through `008.md`: operative source thread span that produced the failed terminal verdict being repaired here.

## Requirement Sufficiency

Existing requirements sufficient. Existing governance and precedent are sufficient for this bounded file-state repair. This is not a new product requirement or a change to WI-5211 implementation behavior; it is a bounded bridge/file finalization repair so the original reviewed thread can be re-finalized through the mandatory helper.

## Proposed Implementation Steps

1. Reconfirm that `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` is still untracked, terminal `VERIFIED`, lacks commit-finalization evidence, and has the recorded byte length/hash or a freshly recorded replacement hash.
2. Copy that exact file to `independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md` as the audit archive.
3. Verify source and archive byte length, SHA-256, and git blob hash match exactly.
4. Remove only `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md`.
5. Verify `gt bridge show gtkb-wi5211-df-governed-verdict-publication-parity --json --compact` reports latest `NEW` at version `007`.
6. File a Prime Builder implementation report for this repair thread with the hash evidence and path state.
7. Have Loyal Opposition review this repair and, separately, reissue the original WI-5211 terminal verdict via `.claude/skills/verify/helpers/write_verdict.py --finalize-verified`, including `scripts/openrouter_harness.py` and the original bridge chain.

## Explicit Non-Goals

- Do not stage, commit, modify, or restore `scripts/openrouter_harness.py` under this repair thread.
- Do not author or self-verify a replacement WI-5211 `VERIFIED` verdict from Prime Builder.
- Do not touch WI-5320, WI-5328, WI-5330, dispatcher-starvation implementation work, `groundtruth.db`, or any unrelated bridge/source dirt.
- Do not run a broad sweep commit or stage unrelated paths.

## Required Specification-Derived Verification Plan

- `GOV-WORK-TREE-HYGIENE-001`: show `git status --short --untracked-files=all --` for the two repair target paths before and after repair; prove no unrelated path was mutated by this repair.
- `GOV-FILE-BRIDGE-AUTHORITY-001`: show the repair report is `NEW` by Prime Builder and any final terminal replacement is `VERIFIED` by Loyal Opposition only.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: verify the original WI-5211 replacement verdict is produced through `write_verdict.py --finalize-verified`, not by direct file writing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`: show this proposal and the implementation report carry the same exact target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`: show PAUTH/project/work-item fields remain present in the chain.

## Acceptance Criteria

- The failed WI-5211 `008` verdict is preserved byte-for-byte at `independent-progress-assessments/WI-5211-df-governed-verdict-publication-parity-008.failed-finalizer.md`.
- The untracked failed `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` file is removed and no original WI-5211 source file is mutated by this repair.
- The original WI-5211 bridge thread returns to latest `NEW` at version `007` until Loyal Opposition reissues a governed `VERIFIED` verdict.
- A later valid finalization commit for WI-5211 can include the one original source path and the reissued terminal verdict, while the failed-verdict archive remains available as audit evidence if the finalizer stages it.

## Risk and Rollback

Risk is low because the repair is limited to a single untracked terminal verdict file and a single audit archive. Rollback is to restore `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-008.md` from the archive, which is why byte-for-byte verification is required before deletion.

## Recommended Commit Type

`chore`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
