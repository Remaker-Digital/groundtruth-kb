NEW

# GT-KB Bridge Implementation Report - gtkb-wi5112-hunk-scoped-verified-finalization - 005

bridge_kind: implementation_report
Document: gtkb-wi5112-hunk-scoped-verified-finalization
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5112-hunk-scoped-verified-finalization-004.md
Approved proposal: bridge/gtkb-wi5112-hunk-scoped-verified-finalization-003.md
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f4ace-e667-7030-b632-1cf002c1a0f7
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex desktop; resolved Prime Builder role
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5112
Implementation Authorization Packet: sha256:ba86b9abc720c6c8a6ca2d14b81a0e7bf2e0b3bb6058aa57e92929b9625caed2
Recommended commit type: feat:

## Implementation Claim

WI-5112 is implemented on the four GO-authorized paths. The VERIFIED finalization helper now supports hunk-scoped finalization through repeatable `--hunk-patch` inputs, builds a disposable `GIT_INDEX_FILE` index from `HEAD`, stages only the reviewed path set plus the verdict into that disposable index, and commits from that disposable index with no pathspec.

All implementation outputs and generated bridge artifacts for this report are in-root under `E:/GT-KB`; the filed report target is `E:/GT-KB/bridge/gtkb-wi5112-hunk-scoped-verified-finalization-005.md`.

The implementation deliberately preserves unrelated pre-existing real-index entries. After a successful temp-index commit, it realigns the real index only for the committed path set with `git reset -q HEAD -- <committed-paths>` so the shared real index does not show synthetic staged reverts against the new `HEAD`. This means unrelated real-index entries are byte-preserved, while committed paths are updated to the new `HEAD` as a required cleanup step after the disposable-index commit.

Cursor, Codex, and Claude helper copies are byte-identical again. The Cursor projection now carries the canonical WI-4520 `_assert_verdict_evidence_anchors` guard instead of remaining divergent.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - VERIFIED remains an atomic bridge and commit-finalization outcome.
- `GOV-WORK-TREE-HYGIENE-001` - finalization must neither commit unrelated dirty work nor mutate foreign staged state.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the active first-wave PAUTH bounds this source/test work to WI-5112.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - hunk staging remains subject to bridge GO, implementation-start authorization, report coverage, and verified-commit gates.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report preserves concrete governing links for protected helper and test scope.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item, and target paths remain machine-readable.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - focused regression tests provide executed evidence before a later VERIFIED verdict.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - Claude, Codex, and Cursor helper projections remain byte-identical and carry the evidence-anchor guard.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex invokes the governed verification helper path, preserving the canonical helper/projection contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the append-only bridge lifecycle remains intact.

## Owner Decisions / Input

No new owner decision is required by this implementation report.

## Prior Deliberations

- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-003.md` - approved revised implementation proposal.
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-004.md` - Loyal Opposition GO authorizing implementation.

## Implementation Details

- Added `HunkPatch` resolution and patch path validation. Patch files must resolve inside the project root, must contain parseable diff paths, and every touched path must be inside the VERIFIED include set.
- Added disposable-index helpers using `GIT_INDEX_FILE` under the repository git dir, seeded with `git read-tree HEAD`.
- Changed finalization staging so whole-file include paths are staged into the disposable index, while hunk patch paths are applied only to the disposable index.
- Changed commit creation to run `git commit -m <message>` with the disposable index and no pathspec, preventing Git from pulling unrelated real-index or worktree paths into the finalization commit.
- Added staged-set checks before commit and committed-path checks after commit so the final commit path set must match the reviewed disposable-index path set.
- Added cleanup behavior that removes the newly written verdict on failed finalization without disturbing unrelated real-index entries.
- Added CRLF/whitespace-context fallback for hunk patches: exact `git apply --cached --check` is attempted first, then `--ignore-space-change` is used only when exact patch context fails.
- Added repeatable CLI `--hunk-patch` support.
- Restored the Cursor helper to canonical parity with Claude/Codex, including `_assert_verdict_evidence_anchors`.
- Expanded `platform_tests/scripts/test_lo_verified_commit_atomicity.py` with hunk-scoped, malformed/out-of-scope, CRLF, lock-retry, byte-parity, and temp-root-marker coverage.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `pytest platform_tests\scripts\test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .harness-tmp\wi5112-atomicity-final` passed 16 tests. |
| `GOV-WORK-TREE-HYGIENE-001` | The focused suite includes unrelated staged-entry preservation, selected-hunk-only finalization, failed-apply cleanup, and out-of-scope patch rejection. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation authorization began successfully for `gtkb-wi5112-hunk-scoped-verified-finalization` with packet hash `sha256:ba86b9abc720c6c8a6ca2d14b81a0e7bf2e0b3bb6058aa57e92929b9625caed2`. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | The implementation was limited to the four GO-authorized target paths and is now reported through this append-only bridge report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This report carries concrete Specification Links and a spec-derived verification plan. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries Project Authorization, Project, and Work Item metadata. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff check, ruff format check, parity hash, evidence-anchor grep, and diff whitespace checks were executed. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `git hash-object` returned identical helper hashes: `923da5f68d9a537b218e552671a39dcae3bec990` for Claude, Codex, and Cursor helpers. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The Codex helper copy is byte-identical to the canonical Claude helper and exposes the same `--hunk-patch` path. |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-wi5112-hunk-scoped-verified-finalization` - PASS; packet hash `sha256:ba86b9abc720c6c8a6ca2d14b81a0e7bf2e0b3bb6058aa57e92929b9625caed2`.
- `python -m pytest platform_tests\scripts\test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .harness-tmp\wi5112-atomicity-final` - PASS, 16 passed, 1 warning (`asyncio_mode` unknown config option).
- `python -m ruff check .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py platform_tests\scripts\test_lo_verified_commit_atomicity.py` - PASS.
- `python -m ruff format --check .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py platform_tests\scripts\test_lo_verified_commit_atomicity.py` - PASS, 4 files already formatted.
- `git hash-object .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py` - PASS, all three returned `923da5f68d9a537b218e552671a39dcae3bec990`.
- `rg -n "_assert_verdict_evidence_anchors|--hunk-patch|GIT_INDEX_FILE|ignore-space-change" .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py` - PASS; all three helper copies expose the guard, disposable-index path, hunk-patch CLI, and CRLF fallback.
- `git -c core.whitespace=cr-at-eol diff --check -- .claude\skills\verify\helpers\write_verdict.py .codex\skills\verify\helpers\write_verdict.py .cursor\skills\verify\helpers\write_verdict.py platform_tests\scripts\test_lo_verified_commit_atomicity.py` - PASS with no whitespace errors; Git emitted working-copy EOL conversion warnings for Cursor helper and the test file only.

## Observed Results

- Focused atomicity suite: 16 passed.
- Ruff check: all checks passed.
- Ruff format check: 4 files already formatted.
- Helper parity: all three helper hashes match.
- Evidence-anchor guard: present in Claude, Codex, and Cursor helpers.
- Hunk-patch support: present in Claude, Codex, and Cursor helpers.
- Disposable-index support: present in Claude, Codex, and Cursor helpers.
- Real index status after this implementation report preparation: no entries staged by this WI-5112 implementation.

## Files Changed

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`

## Out of Scope / Explicit Exclusions

- No `groundtruth.db` changes are part of this WI-5112 implementation.
- No `harness-state/harness-registry.json` changes are part of this WI-5112 implementation.
- No generated bridge queue projection or unrelated dirty worktree files are part of this WI-5112 implementation.
- WI-5132 remains intentionally unimplemented until WI-5112 is VERIFIED and committed, per the sequencing constraint in the GO-approved WI-5112/WI-5132 plan.

## Loyal Opposition Verification Request

Please verify and, if satisfactory, finalize only these four implementation paths plus this report:

- `.claude/skills/verify/helpers/write_verdict.py`
- `.codex/skills/verify/helpers/write_verdict.py`
- `.cursor/skills/verify/helpers/write_verdict.py`
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
- `bridge/gtkb-wi5112-hunk-scoped-verified-finalization-005.md`

Use the new hunk-scoped VERIFIED finalization path if other unrelated workspace changes are still present.
