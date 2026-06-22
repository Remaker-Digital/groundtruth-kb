NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c5589f49-975d-4e4b-8194-04818c10e991
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Implementation Report - VERIFIED finalization tolerates unrelated staged files

bridge_kind: implementation_report
Document: gtkb-verified-finalize-tolerate-unrelated-staged
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-verified-finalize-tolerate-unrelated-staged-002.md
Approved proposal: bridge/gtkb-verified-finalize-tolerate-unrelated-staged-001.md
Recommended commit type: fix:

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4743

target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]

## Implementation Claim

Implemented the approved WI-4743 fix: `finalize_verified_commit` in both
`write_verdict.py` twins now commits ONLY the verified path set via an explicit
pathspec (`git commit -m <msg> -- <expected_paths>`), tolerating unrelated
pre-existing staged files in the shared index instead of hard-raising on a
clean-index precondition.

Three functional changes, applied byte-identically to
`.claude/skills/verify/helpers/write_verdict.py` and
`.codex/skills/verify/helpers/write_verdict.py`:

1. Removed the `staged_before` clean-index hard-raise; `staged_before` is now a
   non-fatal capture (a set) used to scope the staged-set assertion.
2. Relaxed the post-`git add` staged-set assertion from exact-set-equality to:
   the helper's own `dirty_expected_paths` must all be staged (fail closed if
   any is missing), and the helper must not have introduced new staging beyond
   its own paths (`unexpected_new`), while pre-existing unrelated staged paths
   are tolerated.
3. Changed the commit from bare `git commit -m <msg>` to
   `git commit -m <msg> -- <expected_paths>` (explicit pathspec), so only the
   verified path set is committed regardless of unrelated staged work.

The docstring was updated to describe the explicit-pathspec commit and
dirty-index tolerance. The lock-retry (`_run_git_with_lock_retry`), the
`_cleanup_failed_verdict` fail-closed unstaging of only the helper's paths, and
the atomic-commit invariant are all preserved.

## WI-4723 Same-File Overlap (GO condition)

Per the `-002` GO condition: `platform_tests/scripts/test_lo_verified_commit_atomicity.py`
and both `write_verdict.py` twins were already dirty from in-progress WI-4723
(index-lock-retry) work when this fix began. Classification: **combined same-file
evolution**, not a clobber and not a separable patch.

- WI-4723's index-lock-retry additions to the helpers (`_run_git_with_lock_retry`,
  `_is_index_lock_failure`, the retry-aware call sites) are **preserved
  unchanged**; this fix only modified `finalize_verified_commit`'s staging/commit
  logic and routes the commit through the same `_run_git_with_lock_retry` wrapper.
- WI-4723's retry/fail-fast/exhaustion/parity tests in the test module are
  **preserved unchanged**; this fix replaced only the single obsolete
  `test_unrelated_staged_path_fails_before_verified_verdict_is_written` (which
  asserted the now-removed hard-raise) with
  `test_unrelated_staged_path_is_tolerated_and_excluded_from_commit`.
- Evidence of preservation: the focused suite reports `11 passed`, which includes
  WI-4723's `test_verified_finalization_retries_transient_index_lock_on_add`,
  `...on_commit`, `...exhausts_lock_retries`, the non-lock fail-fast test, and the
  `.claude`/`.codex` byte-parity test.

Consequence for finalization sequencing: whichever of WI-4743 / WI-4723 finalizes
first will commit the combined working-tree state of these shared files; the
other thread's finalization will then find those source files already committed
(clean) and commit only its own remaining unique paths plus its verdict. This is
expected and safe under the new explicit-pathspec commit.

## Self-Bootstrap Note

The LO finalization of THIS report runs the now-fixed helper from the working
tree, so it commits the verified path set via explicit pathspec and tolerates any
unrelated staged files — the finalization directly exercises and confirms the fix.
The same fixed helper unblocks the re-triggered wi4723 and wi4534 finalizations.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory; carried per GO)
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory; carried per GO)
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory; carried per GO)

## Owner Decisions / Input

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — the standing owner direction
  underlying `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, which authorizes
  small reliability/defect fixes by active project membership; WI-4743 is an
  active member of PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265568` — this session's owner AUQ context: when presented the
  VERIFIED-finalization deadlock, the owner chose "Fix the root cause."
- Per the `-002` GO advisory, implementation authorization is cited from the
  active PAUTH + owner-decision deliberation above, NOT from the work item's
  `approval_state` field.

## Prior Deliberations

- `DELIB-20265511` and `DELIB-WI4723-OWNER-PROCEED-20260621` — finalization-deadlock
  / WI-4723 context.
- `DELIB-20263279` — WI-4464 commit pathspec-safety precedent (explicit pathspecs
  prevent commit contamination), cited by the `-002` GO.
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-010.md` and
  `bridge/gtkb-wi4534-membase-closure-reconciliation-008.md` — the dirty-index
  NO-GO verdicts this fix unblocks.

## Spec-to-Test Mapping

| Specification | Verification | Executed | Result |
| --- | --- | --- | --- |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .gtkb-state/pytest-wi4743-finalize-pathspec` | yes | PASS: 11 passed |
| WI-4743 acceptance (tolerate + exclude unrelated staged file) | `test_unrelated_staged_path_is_tolerated_and_excluded_from_commit` | yes | PASS (commit excludes unrelated file; unrelated file remains staged) |
| WI-4723 preservation (combined same-file evolution) | retry/fail-fast/exhaustion/parity tests in the same module | yes | PASS (included in the 11) |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | byte-identical `.claude`/`.codex` twins | yes | PASS: both `sha256:b4fe8936003893311d3a0ee1435ab5136277d8c90061d9eb643b5ac3e5b98d42` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `ruff check` on the 3 changed files | yes | PASS: All checks passed! |
| Python format gate (`.claude/rules/file-bridge-protocol.md`) | `ruff format --check` on the 3 changed files | yes | PASS: 3 files already formatted |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | path inspection | yes | PASS: all three target paths are in-root under `E:\GT-KB`; no application-tree or out-of-root path touched |
| `GOV-RELIABILITY-FAST-LANE-001` | scope review | yes | PASS: small single-concern defect fix (2 helper twins + 1 test) under the cited PAUTH |

## Commands Run

```text
groundtruth-kb\.venv\Scripts\python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-verified-finalize-tolerate-unrelated-staged
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q --tb=short --basetemp .gtkb-state/pytest-wi4743-finalize-pathspec
groundtruth-kb\.venv\Scripts\python.exe -m ruff check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py platform_tests/scripts/test_lo_verified_commit_atomicity.py
Get-FileHash -Algorithm SHA256 .claude/skills/verify/helpers/write_verdict.py .codex/skills/verify/helpers/write_verdict.py
```

## Observed Results

- Pytest: `11 passed, 1 warning in 38.37s` (the warning is the pre-existing
  `asyncio_mode` config warning, unrelated).
- Ruff check: `All checks passed!`
- Ruff format --check: `3 files already formatted`.
- Helper byte parity: both twins hash
  `b4fe8936003893311d3a0ee1435ab5136277d8c90061d9eb643b5ac3e5b98d42`.

## Files Changed

- `.claude/skills/verify/helpers/write_verdict.py` — `finalize_verified_commit`
  staging/commit logic (3 changes + docstring).
- `.codex/skills/verify/helpers/write_verdict.py` — byte-identical mirror.
- `platform_tests/scripts/test_lo_verified_commit_atomicity.py` — replaced the
  obsolete clean-index failure test with the tolerate-and-exclude success test;
  all WI-4723 retry tests preserved.

## Acceptance Criteria Status

- [x] Finalization succeeds with an unrelated file staged; the commit excludes it.
- [x] The unrelated staged file remains staged after finalization (untouched).
- [x] The commit contains exactly the verified path set + verdict (explicit pathspec).
- [x] Fail-closed preserved: missing own expected dirty paths still raise.
- [x] Both helper twins changed identically and remain byte-identical.
- [x] WI-4723 lock-retry and its tests preserved (11 passed includes them).
- [x] ruff check and ruff format --check clean on all three files.

## Risk And Rollback

Residual risk is limited to the pathspec under-committing; the subset assertion
confirms all `dirty_expected_paths` are staged before commit, and the
commit-failure cleanup unstages only the helper's paths and removes the verdict,
failing closed. Rollback is a scoped revert of the two helper twins and the test
change; no schema/registry/migration is involved.

## Loyal Opposition Asks

1. Verify the three changed paths and this report against the linked specifications.
2. Confirm the WI-4723 same-file overlap explanation (combined same-file evolution;
   WI-4723 work preserved; evidenced by the 11-passed suite including the retry tests).
3. Finalize VERIFIED via the helper, staging the verified path set:
   `.claude/skills/verify/helpers/write_verdict.py`,
   `.codex/skills/verify/helpers/write_verdict.py`,
   `platform_tests/scripts/test_lo_verified_commit_atomicity.py`,
   and the new VERIFIED verdict. The finalization runs the now-fixed helper, which
   commits via explicit pathspec and tolerates any unrelated staged files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
