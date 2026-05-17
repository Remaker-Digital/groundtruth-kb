NEW

# Implementation Report - implementation_start_gate finalization-exemption quote-aware control-marker fix (WI-3357)

bridge_kind: implementation_report
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 009
Responds to: bridge/gtkb-impl-start-gate-finalization-quoting-fix-008.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3357

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This post-implementation report covers implementation of the REVISED-3 proposal (`-007`), approved by the Loyal Opposition `GO` at `-008`. IP-1 (the two-view quote-aware control-marker scan, the HEREDOC forward-scan parser, and the rewritten finalization predicate) and IP-2 (the regression test suite) are landed in the working tree. IP-3 (the WI-3357 lifecycle promotion `open` -> `verified`) is deferred until this report receives `VERIFIED`, per `-007` IP-3.

## Summary

`scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py` were modified per the GO'd `-007` IP-1 and IP-2. Diff stat: 357 insertions(+), 15 deletions(-) across the two files. The implementation code matches the `-007` IP-1a/1b/1c code blocks verbatim; `ruff format` was applied for canonical formatting (whitespace only, no semantic change). All 50 WI-3357 spec-derived tests pass; `ruff check` and `ruff format --check` are clean. One pre-existing, unrelated test failure is documented and owner-waived in `## Pre-Existing Failure and Owner Waiver`.

## Implemented Changes

### IP-1 - scripts/implementation_start_gate.py

- The single `GIT_FINALIZATION_CONTROL_MARKERS` tuple was split into `GIT_FINALIZATION_CHAINING_MARKERS` (`;`, `&&`, `||`, `|`) and `GIT_FINALIZATION_EXECUTION_MARKERS` (`$(`, backtick); the combined name is retained as their concatenation for compatibility.
- `_HEREDOC_OPENER_RE` was added beside the other module-level regexes - the fixed single-line opener `$(cat <<['"]DELIM['"]` (internal whitespace `[ \t]`).
- Four helpers were added: `_mask_quoted_spans` (two-view quote-aware blanking), `_has_disqualifying_control_marker` (the chaining/execution two-view scan), `_find_heredoc_message_substitution_spans` (the forward-scan parser validating the opener, the opener-line tail, the first delimiter line, and the post-delimiter close paren), and `_neutralize_heredoc_message_substitutions` (blanks recognized spans).
- `_is_simple_git_finalization_command` was rewritten to neutralize recognized HEREDOC substitutions, run the two-view marker scan, then tokenize.
- The implementation matches `-007` IP-1a/1b/1c verbatim; `ruff format` applied canonical formatting only (no semantic change).

### IP-2 - platform_tests/scripts/test_implementation_start_gate.py

- Three parametrized test functions were appended; no existing test logic was modified. `test_wi3357_simple_git_finalization_classification` (23 cases), `test_wi3357_gate_decision_classification` (15 cases), and `test_wi3357_heredoc_parser_recognizes_only_safe_spans` (12 cases) - 50 spec-derived cases total.
- They cover `-007`'s 20-case Specification-Derived Verification Plan, the parser adversarial table, and the `-008` review's non-blocking observation 1 (the multi-`cat` heredoc shape, `\r\n` line endings, and an unquoted-substitution `-m` value - cases 21/22/23 plus the corresponding parser cases).

### IP-3 - WI-3357 lifecycle

Deferred: the WI-3357 `open` -> `verified` promotion occurs after this report receives `VERIFIED`, per `-007` IP-3.

## In-Root Placement Evidence

Both modified files are in-root under `E:\GT-KB`: `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`. The bridge file is `bridge/gtkb-impl-start-gate-finalization-quoting-fix-009.md`. No `applications/`-tree paths are involved. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement is satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this report flows as a post-implementation NEW awaiting VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward every relevant governing specification from `-007`.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Evidence section maps the predicate's intent to executed tests with observed results.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate is the hook that enforces this protected behavior; the change narrows a false-negative and adds one provably-read-only exemption without weakening true-positive coverage.
- `GOV-RELIABILITY-FAST-LANE-001` - the governing fast-lane policy under which WI-3357 is routed.
- `GOV-STANDING-BACKLOG-001` - WI-3357 is a single tracked work item; this is not a bulk operation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both modified files are in-root; no application-tree paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, the owner decisions, and verification evidence are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across WI-3357, this thread, the tests, and this report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3357 moves through open -> implementing -> verified lifecycle states; the verified transition is IP-3, deferred to post-VERIFIED.

The predicate's intent (exempt a simple standalone `git commit` / `git push`; reject genuine chaining and executable command substitution) is the de-facto specification, established by the VERIFIED `gtkb-implementation-start-gate-repository-finalization` thread. The verification evidence below maps that intent to the executed tests.

## Prior Deliberations

The targeted Deliberation Archive search for this WI-3357 quoted-control-marker / HEREDOC topic returned `[]` across all prior reviews on this thread; the operative prior-decision history is the bridge thread itself:

- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-001.md` ... `-008.md` - this thread. `-001` NEW; `-002` NO-GO (blanket double-quote command-substitution exemption); `-003` REVISED-1; `-004` NO-GO (DOTALL regex backtracking past the first delimiter line); `-005` REVISED-2; `-006` NO-GO (opener-line tail unvalidated); `-007` REVISED-3; `-008` GO (single-harness Loyal Opposition self-review with a fresh-context adversarial sub-review). This report implements the `-007` proposal that `-008` approved.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - owner decision approving the standing reliability fast-lane; `PROJECT-GTKB-RELIABILITY-FIXES` is active and `WI-3357` has active membership.
- `bridge/gtkb-implementation-start-gate-repository-finalization` (VERIFIED) - introduced `_is_simple_git_finalization_command()`; its design intent (reject the safe classification when shell chaining, command substitution, or backtick execution is present) is preserved by this implementation.

## Owner Decisions / Input

WI-3357 is routed through the reliability fast-lane per `GOV-RELIABILITY-FAST-LANE-001` (no per-fix Deliberation Archive record or formal-artifact-approval packet). The owner-decision evidence for this thread:

- **Option B threat-model decision (owner, 2026-05-17, AskUserQuestion).** The owner selected Option B - support the documented HEREDOC `$(cat <<'EOF' ... EOF)` commit pattern - over Option A (narrow fix only). The implemented HEREDOC recognizer delivers Option B within the narrow allowlist scope `-007` and `-008` define.
- **Single-harness Loyal Opposition self-review (owner, 2026-05-17, AskUserQuestion).** With the Codex harness unavailable, the owner directed that the Loyal Opposition review be performed by Claude Code acting as Loyal Opposition. The `-008` GO was that review; the `-010` verification of this report will likewise be a fresh-context Claude Code Loyal Opposition agent (see `## Reviewer Verification Context`).
- **Pre-existing-failure waiver (owner, 2026-05-17, AskUserQuestion).** The post-implementation test run surfaces one pre-existing, unrelated test failure (`test_non_go_bridge_entry_cannot_create_authorization`). The owner was presented the failure with its provenance and chose "Waive it; file a separate WI": this report records the failure as a pre-existing, out-of-scope defect; WI-3357 verification proceeds on its merits; the stale test is captured as a separate defect WI to be fixed in its own session per GOV-07. Details in `## Pre-Existing Failure and Owner Waiver`.
- **Standing implementation authorization.** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorizes implementation on WI-3357; the implementation-start authorization packet for this work was created from the `-008` GO.

## Specification-Derived Verification Evidence

De-facto specification: a standalone `git commit` / `git push` is a simple finalization command and is exempt regardless of literal punctuation in its quoted message; the documented HEREDOC `$(cat <<'QUOTED-DELIM' ... DELIM)` message substitution is exempt only when its opener-line tail is whitespace-only and its first delimiter line is immediately followed by the closing `)`; a command that chains another command, runs executable command substitution inside double quotes (other than the recognized HEREDOC `cat` form), or runs any command via an opener-line redirect / separator / pipeline or after the heredoc-terminating line, is not exempt.

Commands executed and observed results:

```text
PYTHONPATH=groundtruth-kb/src python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q
  -> 93 passed, 1 failed, 1 warning (the 1 failure is pre-existing and unrelated; see below)

PYTHONPATH=groundtruth-kb/src python -m pytest platform_tests/scripts/test_implementation_start_gate.py -k wi3357 -q
  -> 50 passed, 44 deselected   (every WI-3357 spec-derived case passes)

python -m ruff check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
  -> All checks passed!  (exit 0)

python -m ruff format --check scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_start_gate.py
  -> 2 files already formatted  (exit 0)
```

Spec-to-test mapping:

| De-facto specification clause | Verification coverage | Test function | Result |
|---|---|---|---|
| Standalone `git commit`/`git push` exempt regardless of literal punctuation in a quoted message | simple cases 1-4, 10, 23 | `test_wi3357_simple_git_finalization_classification` | pass |
| The documented HEREDOC `$(cat <<'DELIM' ... DELIM)` message substitution is exempt | simple cases 3, 4, 23; gate cases 3 | `test_wi3357_simple...` + `test_wi3357_gate_decision_classification` | pass |
| Executable command substitution / backtick inside double quotes disqualifies the exemption | simple/gate cases 5-7 | both | pass |
| A HEREDOC whose substitution would run a further command (unquoted delimiter, non-`cat`, early delimiter, opener-line redirect/separator/pipeline, multi-`cat`) is not exempt | simple/gate cases 8, 9, 16-22 | both | pass |
| Genuine chaining after a git finalization is not exempt | simple/gate cases 11-13 | both | pass |
| Plain `git push` exempt; `git push` denied-force-flags not exempt | simple cases 14, 15 | `test_wi3357_simple...` | pass |
| The HEREDOC recognizer recognizes a span only when every boundary is validated; every other shape fails closed | parser adversarial table (12 cases) | `test_wi3357_heredoc_parser_recognizes_only_safe_spans` | pass |
| No regression in the existing finalization / mutating-command behavior | the file's pre-existing test suite | (pre-existing tests) | all pass except 1 pre-existing unrelated failure (waived) |

Every WI-3357 spec-derived test passes (50/50). The implementation introduced zero new failures: the single failing test was already failing on `develop` before this session.

## Pre-Existing Failure and Owner Waiver

The post-implementation full-suite run reports `1 failed`: `test_non_go_bridge_entry_cannot_create_authorization`. This is a pre-existing, unrelated failure, not a WI-3357 regression:

- The test asserts `pytest.raises(auth.AuthorizationError, match="latest GO")`, but `scripts/implementation_authorization.py`'s `approved_files_for_go` raises `"Implementation authorization requires a GO in the bridge chain; found latest status REVISED"`, which does not contain the literal "latest GO". The behavior is correct (a non-GO thread is rejected); only the test's `match=` regex is stale.
- Provenance: `git log -S "in the bridge chain" -- scripts/implementation_authorization.py` identifies commit `e39627a1` (`fix(governance-hooks): worktree-aware project-root resolution (WI-3353)`) as the commit that reworded the error message without updating the test. That commit predates this session.
- `git status --porcelain scripts/implementation_authorization.py` is empty - the file is byte-identical to HEAD. WI-3357 does not modify `implementation_authorization.py`, and `implementation_authorization.py` does not import from `implementation_start_gate.py`, so the WI-3357 gate changes cannot affect `create_authorization_packet`.
- Isolate-verification: `pytest -k wi3357` reports `50 passed, 44 deselected`, and the full suite shows the failure is the sole one (93 of 94 pass).

Owner waiver: presented with the above via AskUserQuestion (session S357, 2026-05-17), the owner chose "Waive it; file a separate WI". This report records the failure as a pre-existing, out-of-scope defect; WI-3357 verification proceeds on its merits; the stale test is captured as a separate defect WI (see `## Follow-Up`) to be fixed in its own session per GOV-07.

## Acceptance Criteria Check

Against `-007`'s acceptance criteria:

- IP-1 landed (split marker constants, `_mask_quoted_spans`, `_has_disqualifying_control_marker`, `_HEREDOC_OPENER_RE`, `_find_heredoc_message_substitution_spans`, `_neutralize_heredoc_message_substitutions`, rewritten `_is_simple_git_finalization_command`): DONE.
- `_is_simple_git_finalization_command()` returns the specified True/False for the verification cases: verified by `test_wi3357_simple_git_finalization_classification` (50/50 pass).
- `gate_decision()` returns `{}` / a block decision per the plan: verified by `test_wi3357_gate_decision_classification`.
- `_find_heredoc_message_substitution_spans()` returns the expected spans for the adversarial parser table: verified by `test_wi3357_heredoc_parser_recognizes_only_safe_spans`.
- IP-2 tests added and passing; no regression: 50 WI-3357 tests pass; the implementation introduced zero new failures (the single failing test is pre-existing, waived).
- Bridge applicability preflight and ADR/DCL clause preflight: passed on `-007`; to be re-run by the Loyal Opposition verifier against this `-009` operative file.
- `ruff check` and `ruff format --check` clean on both target files: DONE (exit 0 each).

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one work item (WI-3357) is the operative target; it is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`. There are no spec status mutations, no narrative-artifact edits, and no batch work-item promotion, retirement, or inventory in this report. The single WI lifecycle transition (IP-3, deferred) is a per-artifact promotion, not a batch operation. References to "work item", "backlog", and "standing" authorization describe the fast-lane routing. `GOV-STANDING-BACKLOG-001` bulk-operation clauses do not apply.

## Reviewer Verification Context

The Codex harness (harness A, Loyal Opposition) is unavailable - the cross-harness dispatch trigger failed (`unknown_recipient`) and the owner cannot reach the Codex harness interactively. Per the owner's AskUserQuestion directive, the Loyal Opposition verification of this report will be performed by a fresh-context Claude Code agent acting as Loyal Opposition, mitigated by a neutral adversarial briefing. The `-010` verdict will carry an explicit single-harness self-review disclosure, consistent with the `-008` GO.

## Follow-Up

- **Separate defect WI (owner-directed).** The stale `test_non_go_bridge_entry_cannot_create_authorization` assertion (broken since commit `e39627a1` / WI-3353) is to be filed as its own defect WI under the reliability fast-lane and fixed in a separate session, per the owner waiver and GOV-07.
- **Pre-existing `git push` force-via-refspec gap.** `-008` recorded a non-blocking observation that `_is_simple_git_finalization_command()` does not detect a `git push` force expressed as a `+`-prefixed refspec (e.g. `git push origin +main`). This is pre-existing, out of scope for WI-3357, and remains a candidate for a separate reliability-fast-lane work item.

## Recommended Commit Type

`fix:` - corrects a defect in an existing predicate (the finalization exemption wrongly disqualified standalone git commits with literal shell punctuation and the documented HEREDOC commit pattern). No new public API, CLI surface, or capability is added. Diff stat: 357 insertions(+), 15 deletions(-) across `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`; the implementation delta is single-concern and the larger test delta is the `-007`-mandated plus `-008`-recommended negative coverage.
