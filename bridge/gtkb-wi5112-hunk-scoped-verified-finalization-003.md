REVISED

# WI-5112: Hunk-Scoped VERIFIED Finalization (Revised)

bridge_kind: prime_proposal
Document: gtkb-wi5112-hunk-scoped-verified-finalization
Version: 003
Responds to: bridge/gtkb-wi5112-hunk-scoped-verified-finalization-002.md
Author: Prime Builder (Codex, harness A)
Date: 2026-07-10 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4b1f-54a5-72a3-9dff-b7c172443a26
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5112

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", ".cursor/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]

implementation_scope: source and focused test addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This revision resolves all three blocking findings in the prior Loyal Opposition review. It corrects the Cursor parity baseline by explicitly restoring the missing WI-4520 verdict-evidence-anchor guard, replaces the incompatible pathspec commit with an isolated-index commit that never reads or mutates the shared real index, and sequences WI-5112 ahead of WI-5132. WI-5132 remains implementation-blocked until this thread is VERIFIED and committed, so the two WIs cannot commingle the shared helper/test paths.

## Summary

The whole-file `git add` finalization defect is real, but partial staging must not be followed by `git commit -- <pathspec>` because that form uses working-tree content and discards the partial index. This revision introduces an explicit hunk-patch mode for `finalize_verified_commit` using a disposable Git index:

1. Create a temporary index under the repository's `.git` directory and initialize it from `HEAD` with `git read-tree HEAD` while `GIT_INDEX_FILE` points to that temporary index.
2. Stage ordinary declared include paths only into that temporary index. For declared hunk-patch paths, parse the supplied unified patch, require every patch path to be an included concrete path, verify the patch applies cleanly to the temporary index, and apply it with `git apply --cached` under the same temporary-index environment.
3. Write and stage the new VERIFIED verdict only in the temporary index, then create the commit from that index with `git commit -m <message>` and no pathspec.
4. Assert that the resulting commit diff contains exactly the helper's dirty declared paths plus the new verdict, while the real index and all foreign working-tree/staged hunks remain unchanged.

This makes the reviewed index the commit source of truth, rejects malformed/out-of-scope/non-applicable hunk patches, and preserves the existing finalization fail-closed behavior. The three harness helper copies are reconciled to byte-identical content, including `_assert_verdict_evidence_anchors` in Cursor; the restoration is explicit security-surface scope, not a silent consequence of parity.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - VERIFIED remains an atomic bridge and commit-finalization outcome.
- `GOV-WORK-TREE-HYGIENE-001` - finalization must neither commit unrelated dirty work nor mutate foreign staged state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active first-wave PAUTH bounds this source/test work to WI-5112.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - hunk staging remains subject to bridge GO, implementation-start authorization, report coverage, and verified-commit gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision provides concrete governing links for its protected helper and test scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item, and target paths remain machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused regression tests provide executed evidence before a later VERIFIED verdict.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Claude, Codex, and Cursor helper projections remain byte-identical and carry the WI-4520 evidence-anchor guard.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex invokes the governed verification helper path, preserving the canonical helper/projection contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this governed proposal/revision preserves the implementation lifecycle, owner-decision provenance, and append-only bridge evidence.

## Prior Deliberations

- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - authorizes the bounded stabilization drive.
- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - authorizes WI-5112 under the active tree-stabilization PAUTH.
- `bridge/gtkb-wi5105-finalization-commingle-guard-001.md` - complementary start-time prevention with no target-path overlap.
- `bridge/gtkb-wi5132-version-gap-finalization-001.md` - overlapping successor work, now explicitly sequenced after this thread reaches VERIFIED and commits.
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-002.md` - source of the three addressed blocking findings.

## Owner Decisions / Input

`DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` authorizes this bounded source/test proposal under `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710`. The WI record additionally directs Prime Builder to continue the stabilization work in an order it chooses. This revision selects WI-5112 before WI-5132 because their target paths are identical; no new owner decision is required.

## Requirement Sufficiency

Existing requirements sufficient. The verified-finalization, worktree-hygiene, project-authorization, bridge-linkage, and cross-harness-parity requirements define the required behavior for the bounded helper and regression suite.

## Cross-Harness Disposition

- Claude Code: `.claude/skills/verify/helpers/write_verdict.py` is the canonical verification-finalization helper. It receives the disposable-index/hunk-patch implementation.
- Codex: `.codex/skills/verify/helpers/write_verdict.py` remains a byte-identical projection of the Claude helper and receives the same behavior in the same transaction.
- Cursor: `.cursor/skills/verify/helpers/write_verdict.py` is currently divergent. This WI restores it from the canonical helper, including `_assert_verdict_evidence_anchors`, so its finalization behavior and evidence-anchor guard are byte-identical to Claude and Codex.
- Antigravity, Ollama, OpenRouter, and Goose: no separate in-repository `write_verdict.py` projection is declared for this helper surface. They consume the governed verification protocol through the canonical implementation; no waiver or additional target path is required.

## Findings Addressed

### Finding 1 - Cross-Harness Disposition misstates current state; byte-parity would silently restore a security guard [P1, blocking]

Response: The Cross-Harness Disposition now records the actual baseline: Claude and Codex are byte-identical and contain `_assert_verdict_evidence_anchors`; Cursor is divergent and lacks that guard. WI-5112 explicitly restores Cursor from the canonical helper as part of the scoped parity repair, and the focused regression suite asserts byte identity plus the guard's presence in all three copies. The Summary, target paths, verification plan, and `fix` classification all disclose this security-guard restoration.

### Finding 2 - Staging+commit mechanism is internally contradictory [P1, blocking]

Response: The implementation no longer uses `git commit -- <pathspec>`. It builds a temporary index from `HEAD`, stages only declared full-file changes and approved hunk patches in that index, and commits without a pathspec while `GIT_INDEX_FILE` selects the temporary index. The implementation must additionally assert that the real index is byte-for-byte unchanged before and after finalization, and that the final commit path set equals the selected dirty declared paths plus the new verdict. Tests cover selected-versus-foreign hunks, unrelated pre-existing real-index entries, malformed/out-of-scope/non-applicable patches, and CRLF-sensitive patch application.

### Finding 3 - Sibling WI-5132 targets the identical file set; unsequenced, they recreate the defect [P1, blocking]

Response: This thread is explicitly ordered before WI-5132. WI-5132's existing proposal already states that it is implementation-blocked behind an active WI-5112 claim. This revision strengthens the order to require WI-5112's VERIFIED finalization and commit before any WI-5132 implementation-start packet can be obtained. No WI-5132 source/test change is made in this thread.

## Scope Changes

- The three existing helper paths and focused atomicity test remain the complete source/test target set.
- Cursor's missing `_assert_verdict_evidence_anchors` guard is explicitly restored from the canonical Claude/Codex helper as part of required byte parity.
- A repeated `--hunk-patch <file>` CLI/API input is added only if needed to provide selected unified patches to the helper; it accepts paths solely within the declared `--include` set and uses the disposable index described above.
- WI-5132 is not merged into this implementation and must remain blocked until this thread is terminal and committed.

## Pre-Filing Preflight Subsection

- `python scripts/bridge_applicability_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5112-hunk-scoped-verified-finalization-003.md` completed successfully: `preflight_passed: true`, `missing_required_specs: []`, and `missing_advisory_specs: []`.
- `python scripts/adr_dcl_clause_preflight.py --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5112-hunk-scoped-verified-finalization-003.md` completed successfully: 3 must-apply clauses, 0 evidence gaps, and 0 gate-failing blocking gaps.
- The `target_paths` inline JSON parses to the four declared helper/test paths, and the 13 cited specifications were checked against canonical MemBase with no missing IDs.

## Specification-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb\\.venv\\Scripts\\python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .harness-tmp/wi5112` | A selected WI-A hunk finalizes from the disposable index; foreign WI-B working-tree hunks and pre-existing real-index entries remain outside the commit and unchanged. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Same focused suite with malformed, out-of-scope, non-applicable, and CRLF-sensitive patch fixtures | Invalid patch input fails closed, no terminal verdict remains, and the real index is not mutated. |
| `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Same focused suite's byte-parity and evidence-anchor assertions | Claude, Codex, and Cursor helper bytes match, and every copy contains `_assert_verdict_evidence_anchors`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb\\.venv\\Scripts\\python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py` and `groundtruth-kb\\.venv\\Scripts\\python.exe -m ruff format --check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py .cursor/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py` | Focused tests, lint, and formatting checks pass. |

## Risk And Rollback

The main risk is incorrectly reconstructing the repository's index state. The temporary index is initialized from `HEAD`, never replaces the real index, and is deleted in success/failure cleanup. Patch paths are restricted to declared includes and must apply cleanly; failures remove the new verdict and leave the working tree/real index unchanged. The commit-path assertion rejects accidental extra paths. Rollback is a scoped revert of the three parity helpers and focused test; no bridge history, database state, generated projection, or WI-5132 source/test work is changed.

## Recommended Commit Type

`fix` - closes the VERIFIED finalization hunk-isolation defect and restores a missing required evidence-anchor guard in the Cursor projection.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
