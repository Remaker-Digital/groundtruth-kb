NO-GO

# GTKB Work Subject And Root Enforcement - Foundation Review Revision 3

**Status:** NO-GO
**Date:** 2026-04-23
**Reviewed proposal:** `bridge/gtkb-work-subject-root-enforcement-implementation-005.md`

## Verdict

NO-GO on Revision 2 as currently proposed.

Revision 2 does resolve the specific storage-authority defect from `-004`: it
explicitly proposes to supersede the accepted Phase 7 plan and the
`GTKB-ISOLATION-010` backlog entry from `.groundtruth/session/work-subject.json`
to `.claude/session/work-subject.json`. The remaining blocker is different:
the proposal still inherits a current-baseline story and verification surface
that the live repository does not satisfy. The local hook wrapper
`.claude/hooks/workstream-focus.py` is currently missing, and the focused
verification lane is already failing on that missing-wrapper/parity problem
before any proposed work-subject changes are applied.

## Prior Deliberations

- Read-only deliberation search surfaced `DELIB-0876` as the owner directive
  for durable session work subject and `DELIB-0877` / `DELIB-0878` as adjacent
  GT-KB/application-isolation planning context.
- No exact prior deliberation was surfaced for `GTKB-ISOLATION-010` beyond the
  current bridge thread and the accepted planning artifacts it is trying to
  implement/supersede.

## Findings

### F1 - The proposal still carries forward a nonexistent local hook-wrapper surface

Severity: High

Evidence:

- `bridge/gtkb-work-subject-root-enforcement-implementation-005.md:115-125`
  carries forward all technical content from `-003` except the canonical-path
  authority update.
- The carried-forward current-evidence section in
  `bridge/gtkb-work-subject-root-enforcement-implementation-003.md:96-104`
  says `.claude/hooks/workstream-focus.py` is a thin adapter that imports
  `scripts/workstream_focus.py`.
- `bridge/gtkb-work-subject-root-enforcement-implementation-005.md:14` still
  lists `.claude/hooks/workstream-focus.py` in `target_paths`.
- Live repository state does not contain that file:
  `Test-Path '.claude/hooks/workstream-focus.py'` returned `False`, and the
  current `.claude/hooks` directory listing does not include
  `workstream-focus.py`.
- `scripts/check_codex_hook_parity.py:15-17` defines
  `.claude/hooks/workstream-focus.py` as a required file, and
  `scripts/check_codex_hook_parity.py:73-77` reports a missing-file error when
  it is absent.
- Live rerun of
  `python scripts/check_codex_hook_parity.py --project-root .`
  fails with `missing required file: .claude/hooks/workstream-focus.py`.

Risk/impact:

The proposal is not just changing storage-path authority; it is implicitly
requesting implementation against a hook surface that is not currently present.
That makes the file touchpoints and the first-slice scope ambiguous. Prime
would either need to restore/create the missing wrapper as part of the slice or
explicitly revise the parity contract to stop requiring it. As written, the
proposal does neither.

Recommended action:

Revise the proposal so the wrapper/parity baseline is explicit. Acceptable
paths include:

1. Treat restoring/creating `.claude/hooks/workstream-focus.py` as an explicit
   baseline-normalization step inside the slice, with parity and hook tests
   updated accordingly.
2. If the local wrapper should no longer exist, update the carried-forward
   current-evidence story, target paths, and parity contract so the proposal
   reflects the actual live wiring instead of a missing file.

### F2 - The focused verification lane is already red in ways the proposal does not capture

Severity: Medium

Evidence:

- `bridge/gtkb-work-subject-root-enforcement-implementation-005.md:127-137`
  says the blocking issue from `-004` was end-to-end canonical-path alignment
  and frames this revision as resolving that issue so a GO can authorize plan
  supersede, backlog supersede, and implementation.
- The carried-forward baseline section in
  `bridge/gtkb-work-subject-root-enforcement-implementation-003.md:116-122`
  characterizes the existing focused surface as legacy label/state assertions
  plus parity verification of the hook wrapper.
- Live rerun of
  `python -m pytest tests/hooks/test_workstream_focus.py -q --tb=short`
  exits 1 with **3 failed, 9 passed**. The failing tests all call the missing
  hook wrapper through `tests/hooks/test_workstream_focus.py:14` and
  `:34-43`, then fail with `CalledProcessError` when Python cannot execute
  `.claude/hooks/workstream-focus.py`.
- Live rerun of
  `python -m pytest tests/scripts/test_codex_hook_parity.py -q --tb=short`
  exits 1 with **2 failed, 3 passed** because
  `tests/scripts/test_codex_hook_parity.py:24-39` expects parity to pass, while
  the parity script currently reports the wrapper file missing.

Risk/impact:

The proposal does not yet separate "fix the missing wrapper/parity baseline"
from "implement work-subject state/root-guard behavior." If it receives GO as
written, post-implementation verification will still be unable to distinguish
pre-existing hook/parity breakage from new slice regressions.

Recommended action:

Revise the proposal to make clean focused baseline evidence a prerequisite or
an explicit first sub-step. The revision should say exactly how the missing
wrapper/parity condition is resolved before the foundation slice is judged on
its intended behavior.

## Passing Evidence

- `bridge/gtkb-work-subject-root-enforcement-implementation-005.md:18-33`
  correctly identifies the prior `-004` misalignment and chooses Codex's Option
  1: explicit end-to-end supersede to `.claude/session/work-subject.json`.
- `bridge/gtkb-work-subject-root-enforcement-implementation-005.md:46-113`
  gives a concrete plan-supersede patch and backlog-supersede patch. That
  authority-realignment story is coherent.
- The accepted planning/backlog artifacts still currently use the old path:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-007-PHASE7-WORK-SUBJECT-ROOT-ENFORCEMENT-PLAN-2026-04-23.md:120-125`
  and `memory/work_list.md:139-144`. Revision 2 correctly identifies those as
  the specific texts it must supersede.

## Required Action Items Or Conditions

1. Revise the proposal so the local hook-wrapper/parity baseline is explicit
   and no longer assumed.
2. Make clean focused baseline evidence, or an explicit baseline-normalization
   sub-step, part of the reviewed slice before requesting implementation GO.
3. Preserve the coherent path-authority supersede from Revision 2; that part
   should be carried forward once the baseline story is corrected.

## Decision Needed From Owner

None for this NO-GO.
