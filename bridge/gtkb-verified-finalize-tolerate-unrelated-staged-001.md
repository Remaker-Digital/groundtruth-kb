NEW

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c5589f49-975d-4e4b-8194-04818c10e991
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# VERIFIED finalization must tolerate unrelated staged files (explicit-pathspec commit)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4743
target_paths: [".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "platform_tests/scripts/test_lo_verified_commit_atomicity.py"]

Document: gtkb-verified-finalize-tolerate-unrelated-staged

## Summary

`finalize_verified_commit` in the LO VERIFIED-finalization helper
(`.claude/skills/verify/helpers/write_verdict.py` and its byte-identical `.codex`
twin) hard-raises when the git index holds ANY staged path (the `staged_before`
precondition), then commits with a bare `git commit -m <msg>` (no pathspec). In a
multi-session swarm the shared index is continually dirtied by other sessions'
stray staged files, so the clean-index precondition deadlocks EVERY VERIFIED
finalization. Observed during the PROJECT-GTKB-ACTIVE-ORCHESTRATION drive: wi4723
and wi4534 are content-complete and LO-content-accepted but cannot reach VERIFIED
— each finalization NO-GO's on a DIFFERENT stray staged file (3 ping-pongs;
re-filing is futile).

This fix makes finalization commit ONLY the verified path set via an explicit
pathspec (`git commit -m <msg> -- <expected_paths>`), so unrelated staged files
can never contaminate the commit. With scope-contamination prevented by the
pathspec, the clean-index hard-raise is removed and the staged-set assertion is
relaxed to a subset check (the helper's own paths must be staged; pre-existing
unrelated staged files are tolerated and left untouched).

## Reliability Fast-Lane Eligibility (GOV-RELIABILITY-FAST-LANE-001)

- origin = defect (WI-4743), component bridge.
- No new public API / CLI surface / behavior beyond removing a deadlock; the
  helper's contract (commit exactly the verified path set) is preserved and
  strengthened (the pathspec makes it exact regardless of index state).
- No new or revised requirement/specification.
- Small, single-concern: 2 byte-identical helper files + 1 test module.
- Covered by `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via active
  membership of WI-4743 in PROJECT-GTKB-RELIABILITY-FIXES.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs this fast-lane defect fix.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — VERIFIED finalization is core bridge function;
  this restores it under multi-session index contention (bridge integrity is the
  top-priority subsystem).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-derived verification is
  in the Spec-Derived Verification section.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all three target paths are in-root
  under `E:\GT-KB` (`.claude/skills/verify/helpers/write_verdict.py`,
  `.codex/skills/verify/helpers/write_verdict.py`,
  `platform_tests/scripts/test_lo_verified_commit_atomicity.py`); no
  application-tree or out-of-root path is touched.
- `.claude/rules/bridge-essential.md` — VERIFIED-finalization reliability is bridge
  function; keeping bridge state correct is the first Prime Builder duty.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised requirement is required; this
removes a defect (a clean-index precondition that deadlocks under multi-session
index contention) while preserving the atomic-commit and exact-path-set
invariants. The helper is already required to commit exactly the verified path
set; this fix makes it do so robustly.

## Prior Deliberations

- `DELIB-20265511` — pragmatic-completion / retirement decision that identified
  the finalization-environment deadlock and filed WI-4723.
- `DELIB-WI4723-OWNER-PROCEED-20260621` — owner directive authorizing the WI-4723
  index-lock-retry repair (the sibling finalization-hardening axis).
- `bridge/gtkb-wi4723-verified-finalize-index-lock-retry-010.md` and
  `bridge/gtkb-wi4534-membase-closure-reconciliation-008.md` — the two dirty-index
  NO-GO verdicts that motivate this fix; both explicitly state the implementation
  is content-accepted and the only blocker is the dirty shared index.
- `DELIB-20265568` — this session's owner-decision capture for the
  ACTIVE-ORCHESTRATION drive (broader effort context).

## Change Detail

In BOTH `.claude/skills/verify/helpers/write_verdict.py` and
`.codex/skills/verify/helpers/write_verdict.py` (kept byte-identical), inside
`finalize_verified_commit`:

1. Remove the clean-index hard-raise (the `staged_before` block that raises
   "VERIFIED finalization requires a clean staging area ..."). Replace it with a
   non-fatal capture of pre-existing staged paths used to scope the staged-set
   assertion.
2. Relax the post-`git add` staged-set assertion from exact-set-equality to a
   subset check: the helper's own `dirty_expected_paths` must be a subset of the
   staged set; pre-existing unrelated staged paths are tolerated.
3. Commit with an explicit pathspec: `git commit -m <msg> -- <expected_paths>`
   (was bare `git commit -m <msg>`), so ONLY the verified path set is committed
   regardless of unrelated staged work, which remains staged and untouched.

The atomic-commit invariant, the lock-retry behavior (WI-4723),
`_cleanup_failed_verdict`'s fail-closed unstaging of only the helper's paths, and
the byte-identical-twin requirement are all preserved.

## Spec-Derived Verification

Derived from WI-4743 acceptance (finalization succeeds and commits exactly the
verified path set even when unrelated files are staged) and
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

- Replace `test_unrelated_staged_path_fails_before_verified_verdict_is_written`
  with `test_unrelated_staged_path_is_tolerated_and_excluded_from_commit`: stage an
  unrelated file, run finalization, assert (a) it succeeds, (b) the commit contains
  exactly the verified path set + verdict (NOT the unrelated file), and (c) the
  unrelated file remains staged afterward.
- `test_verify_helper_codex_twin_matches_claude_and_has_retry` continues to assert
  the `.claude` and `.codex` twins are byte-identical.
- `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q`
  — full atomicity suite passes (lock-retry, fail-fast, exhaustion, parity, plus
  the new tolerate-unrelated-staged test).
- `ruff check` and `ruff format --check` on the three changed files.
- Self-bootstrap note: once the fixed helper is in the working tree, the LO
  finalization for THIS report (and the re-triggered wi4723 / wi4534
  finalizations) runs the robust path, so VERIFIED can be reached without a
  special bootstrap commit.

## Risk / Rollback

- Risk: a malformed pathspec could under-commit (miss a verified path).
  Mitigation: the subset assertion confirms all `dirty_expected_paths` are staged
  before commit; the existing commit-failure cleanup unstages only the helper's
  paths and removes the verdict, failing closed.
- Risk: pre-existing staged files from another session are left staged after the
  commit. This is intended (the helper must not disrupt another session's staged
  work) and matches the pre-fix goal — it simply refused instead of proceeding.
- Rollback: revert the helper changes (both twins) and the test change — a single
  scoped revert; no schema/registry/migration involved.

## Owner Decisions / Input

- AUQ 2026-06-22 (PROJECT-GTKB-ACTIVE-ORCHESTRATION drive) "Break deadlock" ->
  **"Fix the root cause"**: the owner directed addressing the VERIFIED-finalization
  dirty-index deadlock structurally (this proposal) rather than tactical re-files
  or pragmatic closeout.
- No NEW owner approval is required to implement: this is a reliability fast-lane
  defect fix covered by the standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`
  via WI-4743's active membership in PROJECT-GTKB-RELIABILITY-FIXES.

## Recommended Commit Type

`fix:` — repairs broken VERIFIED-finalization behavior (a clean-index precondition
that deadlocks under multi-session index contention) with no new capability
surface.
