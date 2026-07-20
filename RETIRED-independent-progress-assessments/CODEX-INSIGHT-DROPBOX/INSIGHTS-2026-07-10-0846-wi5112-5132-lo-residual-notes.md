author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T08-46-37Z-loyal-opposition-B-eeef5f
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code auto-dispatched Loyal Opposition worker; resolved role loyal-opposition

# LO Advisory — WI-5112 / WI-5132 finalization cluster: concurrence + two residual implementation-stage notes

WIs: WI-5112, WI-5132
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, GOV-WORK-TREE-HYGIENE-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
Threads: gtkb-wi5112-hunk-scoped-verified-finalization (GO at -004), gtkb-wi5132-version-gap-finalization (GO at -002)
Classification: monitor (non-blocking; advisory input for the implementation + WI-5112 verification stages)
Severity: P2 (integrity condition with an available mitigation; not GO-blocking)

## Situation

I was auto-dispatched as Loyal Opposition (harness B) to review WI-5112 REVISED (`-003`) and
WI-5132 NEW (`-001`). While I was reviewing, a peer Loyal Opposition session (interactive Claude
harness B, session `be4929b6-9774-486a-bd0d-e5260880070d`, via `::init gtkb lo`) filed GO on both
threads: WI-5112 GO at `-004`, WI-5132 GO at `-002`. Latest canonical status for both is now GO
(Prime-actionable), so both are stale for my LO role. I stood down and did NOT file a competing
verdict. This report preserves my independent findings for the implementation and verification
stages; it does NOT contest the peer GOs.

## Concurrence

Reviewing against live state, I reached the same core conclusions as the peer GOs and concur with
both:

- The whole-file staging defect in `finalize_verified_commit` is real (whole-file `git add -f`
  plus a pathspec `--only` commit; the path-level staged-set assertion cannot detect an in-file
  foreign hunk). Independently confirmed by reading `.claude/skills/verify/helpers/write_verdict.py`.
- The `-003` temp-index-from-HEAD redesign is git-correct and also preserves the `-002` secondary
  requirement (unrelated pre-existing STAGED entries are absent from a HEAD-seeded temp index).
- All three `-002` blocking findings are resolved. Parity baseline verified by `git hash-object`
  (`.claude` = `.codex` = `31fdfed6`; `.cursor` divergent `95c623ff`) and `_assert_verdict_evidence_anchors`
  present 3x in `.claude`/`.codex`, 0x in `.cursor`.
- WI-5132's version-gap premise is real: `gtkb-dashboard-industry-alignment-slice2a-visibility`
  genuinely jumps 003 -> 007, and `git log --all` shows versions 004/005/006 never existed under
  that slug (genuine gap, not deletion). The history-aware gap-vs-deletion design is the right,
  fail-closed primitive.
- The WI-5132 GO's mandatory Implementation Sequencing Gate (WI-5112 VERIFIED+committed; shared
  paths clean in `git status`; uncontested claim) is a strong control and directly covers the
  shared-tree risk for WI-5132's START.

## The two residual notes both concern WI-5112's OWN finalization, which neither GO flags

The WI-5132 GO gate protects WI-5132's start by requiring a clean shared-path base. Nothing in
either verdict addresses the symmetric condition at WI-5112's OWN finalization, and the WI-5112
GO records "Open decisions: None blocking." At the current commit, two of WI-5112's four target
paths are already dirty before implementation:

- `git status --porcelain` shows ` M .cursor/skills/verify/helpers/write_verdict.py` and
  ` M platform_tests/scripts/test_lo_verified_commit_atomicity.py`; `.claude`/`.codex` are clean.
- No work-intent claim exists for either slug and no WI-5112/WI-5132 commit touches these paths, so
  these changes are unattributed and pre-GO. The `.cursor` diff is a partial glob-filter parity
  nudge to `_claimed_paths_from_report` (NOT the full guard restoration); the test diff adds a
  Cursor helper-path constant and an implementation-report-body fixture. They appear to be
  WI-5112 / stabilization scope, yet the `-003` Revision Claim labels these paths "foreign-dirty."

### Note 1 [P2] — attribute the pre-existing dirty hunks at WI-5112 finalization; verify commit diff is WI-5112-scope only

- If the pre-existing hunks are WI-5112 scope (likely: `.cursor`->canonical reconciliation subsumes
  the glob nudge; the test constant/fixture supports the parity + atomicity suite), WI-5112 absorbs
  them and whole-file finalization is correctly attributed — no action beyond confirming it.
- If any hunk is genuinely foreign (the "foreign-dirty" label taken literally), whole-file
  finalization of WI-5112 would silently fold it into WI-5112's VERIFIED commit — the exact
  WI-5083/WI-5100 class. WI-5112's own new hunk-patch mode is only in the working tree at that
  moment (not yet committed), so relying on it to isolate WI-5112's own finalization is a bootstrap.
- Recommendation (implementation + WI-5112 verification): before/at WI-5112 finalization, resolve
  the disposition explicitly — either absorb the pre-existing changes under WI-5112 attribution, or
  commit/revert them under their real owner first so WI-5112 starts clean. The WI-5112 VERIFIED
  verification should assert the WI-5112 commit diff contains only WI-5112-scope hunks on the four
  paths (no residual foreign hunk). The WI-5105 finalization-commingle guard and the human VERIFIED
  review are the available backstops; this note asks that they be applied deliberately here rather
  than assumed.

### Note 2 [P2] — real-index coherence after the temp-index commit interacts with the WI-5132 clean-`git status` gate

- Committing from a HEAD-seeded temporary index while leaving the working tree intact leaves the
  REAL index un-refreshed relative to the new HEAD; `git status` afterward can show a phantom staged
  reversion of the just-committed change until the real index is resynced. [inference from git index
  semantics]
- This directly interacts with the WI-5132 GO's Implementation Sequencing Gate condition 2 ("the
  four shared target paths are clean in `git status`"): a stale real index left by WI-5112's
  temp-index commit could FALSELY present the shared helper as dirty (blocking WI-5132's start) or
  otherwise confuse that gate.
- Recommendation: WI-5112's implementation should refresh the real index for the committed paths
  after the temp-index commit (e.g., a scoped `git reset` limited to those paths), and the atomicity
  suite should assert post-finalization `git status` coherence (only the intended foreign hunk, if
  any, shown as unstaged — no phantom reversion of committed work). This makes the WI-5132 clean-base
  gate reliable rather than dependent on an unstated index-refresh step.

## Optional structural note

Because both WIs edit the same four files and are strictly sequenced, merging them into one slice
over the shared file set (one attributed implementation, one clean finalization) would eliminate the
shared-tree contention entirely. The peer GO chose the equally-valid GO-with-sequencing-gate path;
the merge remains an owner/Prime option if the sequenced handoff proves fiddly in practice.

## Disposition

Stand-down. Peer GOs at WI-5112 `-004` and WI-5132 `-002` stand; both threads are Prime-actionable.
The two notes above are non-blocking advisory input for the implementation and WI-5112 verification
stages, not a request to re-open either verdict.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
