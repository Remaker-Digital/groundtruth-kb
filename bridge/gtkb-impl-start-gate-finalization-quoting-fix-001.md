NEW

# Implementation Proposal - implementation_start_gate finalization-exemption quoting-aware control-marker fix (WI-3357)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3357

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This NEW proposal fixes a false-negative in the git-finalization safe exemption of the implementation-start gate. `_is_simple_git_finalization_command()` substring-scans the raw command for shell control markers before tokenization, so a control marker that is literal text inside a quoted `-m` commit message wrongly disqualifies the command from the finalization exemption. The command then matches the mutating-command pattern as `git commit`, resolves no target path, and is hard-blocked - so any commit whose message contains `;`, `|`, `&&`, `$(`, or a backtick is rejected, forcing message rewrites.

## Claim

In `scripts/implementation_start_gate.py`, the first line of `_is_simple_git_finalization_command()` is `any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS)` - a raw substring scan of the entire command string, including the quoted `-m "<message>"` value, for the markers `;`, `&&`, `||`, `|`, `$(`, and backtick. The check intends to reject genuine command chaining, but a raw substring scan cannot distinguish a marker that is a shell operator (outside quotes) from a marker that is literal message text (inside quotes). A legitimate `git commit -m "fix X; tidy Y"` is therefore misclassified as chained, loses the finalization exemption, matches `MUTATING_COMMAND_RE` as `git commit` with no resolvable target path, and is hard-blocked at `<unknown-mutating-target>`.

The fix makes the marker check quoting-aware: a control marker counts only when it appears outside single- and double-quoted spans. Genuine chaining (`git commit -m x; rm -rf y`) keeps its `;` outside the quoted message and remains caught; ordinary punctuated messages and the documented HEREDOC commit pattern pass.

Observed 2026-05-17: routine commits whose message contains a semicolon, and the `git commit -m "$(cat <<'EOF' ... EOF)"` HEREDOC pattern, are blocked by this PreToolUse gate. The current workaround is to hand-rewrite commit messages to avoid punctuation; this fix removes the need for that workaround.

## Reliability Fast-Lane Eligibility

This work item is routed via the reliability fast-lane per `GOV-RELIABILITY-FAST-LANE-001`. All four eligibility criteria hold:

1. `origin` is `defect` (WI-3357, verified in MemBase) - never `new`.
2. No new public API, CLI surface, or behavior beyond removing the defect: the change narrows a false-negative in an existing predicate; the exemption's true-positive coverage (rejecting genuine chaining) is preserved and regression-tested.
3. No new or revised requirement or specification: the predicate's intent is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread.
4. Small and single-concern: two files, well under ~150 net lines.

`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (status `active`, `included_work_item_ids` null) covers WI-3357 by active project membership (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3357`, status active). The standing authorization's `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade` - the change edits a hook script (`source` / `hook_upgrade`) and adds tests (`test_addition`); none of the `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are performed.

## In-Root Placement Evidence

Both target paths are in-root under the canonical `E:\GT-KB` checkout: `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`. The bridge file is `bridge/gtkb-impl-start-gate-finalization-quoting-fix-001.md`. No `applications/`-tree paths are involved. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement is satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this NEW flows NEW -> GO -> implement -> report -> VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the predicate's intent to executed tests.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate is the hook that enforces this protected behavior; the fix narrows a false-negative without weakening the gate's true-positive (chaining-detection) coverage.
- `GOV-RELIABILITY-FAST-LANE-001` - the governing fast-lane policy; eligibility is argued above.
- `GOV-STANDING-BACKLOG-001` - WI-3357 is a single tracked work item; this is not a bulk operation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root; no application-tree paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, decision, and verification are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across WI-3357, this thread, the tests, and the implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3357 moves through open -> implementing -> verified lifecycle states.

No directly-governing functional specification exists for the gate's command classifier - the hook is its own implementation surface. The predicate's intent (exempt a simple standalone `git commit`/`git push`; reject genuine chaining) is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread (VERIFIED). This proposal is a defect fix that makes the chaining detector faithful to that intent; the verification plan proves both the false-negative removal and the preserved true-positive coverage.

## Prior Deliberations

A Deliberation Archive semantic search for "implementation-start gate git finalization command classification chaining" returned no directly-relevant DELIB record. The prior-decision history for this surface is the bridge-thread record:

- `bridge/gtkb-implementation-start-gate-repository-finalization` (VERIFIED) - introduced `_is_simple_git_finalization_command()` and its control-marker check. Its `-001` proposal states the design intent verbatim: "reject the safe classification if shell chaining or control markers are present, such as `;`, `&&`, `||`, `|`, command substitution, or backtick execution." This proposal preserves that intent and corrects only the chaining detector's implementation.
- `bridge/gtkb-impl-start-gate-comparison-operator-fix` (VERIFIED, WI-3356) - a sibling fix in the same file: `MUTATING_COMMAND_RE` naive `>`-substring matching misclassified Python `>=` / `>>=`. Same root-cause class (substring matching that ignores syntactic context), different construct and function.
- `bridge/gtkb-impl-start-gate-format-spec-fix` (VERIFIED, WI-3317) - a sibling fix in the same file: `MUTATING_COMMAND_RE` misclassified Python format-spec `:>` alignment. Same root-cause class, different construct and function.

This proposal is a distinct, fourth member of that defect family: it targets `_is_simple_git_finalization_command()` (not `MUTATING_COMMAND_RE`), and the substring artifact is a *false-negative* (an exemption wrongly withheld), not a false-positive. The two comparison-operator / format-spec threads are terminal (VERIFIED); there is no live coordination dependency.

## Owner Decisions / Input

WI-3357 is routed through the reliability fast-lane, so per `GOV-RELIABILITY-FAST-LANE-001` it carries no per-fix owner-approval packet; the owner-decision evidence is the standing authorization plus the directive that motivated the fix:

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorizes implementation on WI-3357 by active project membership in `PROJECT-GTKB-RELIABILITY-FIXES`.
- Owner directive, 2026-05-17: the owner reported that the implementation-start gate blocks `git commit` / `git push` whenever the commit message contains shell punctuation (`;`, `|`, `&&`, `$(`, backtick), and directed a root-cause fix via the bridge protocol / reliability fast-lane rather than continued use of the message-rewrite workaround.
- One design choice is surfaced for Codex review (treatment of `$(` and backtick inside double quotes - see the Design Decision section). It follows the owner's stated intent that the HEREDOC commit pattern be accepted and needs no separate owner decision unless Codex flags it.

## Requirement Sufficiency

Existing requirements sufficient. The predicate's intent is well established by the `gtkb-implementation-start-gate-repository-finalization` thread and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`. This proposal narrows a false-negative without changing intent; no new or revised requirement or specification is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one work item (WI-3357) is the operative target; it is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`. There are no spec status mutations, no narrative-artifact edits, and no batch work-item promotion, retirement, or inventory. The review-packet inventory is IP-1 (a one-function fix) plus IP-2 (regression tests) in a single thread, plus IP-3 (the WI lifecycle transition). References to "work item", "backlog", and "standing" authorization describe the fast-lane routing, not a bulk backlog operation; the supporting evidence is per-artifact (WI-3357, this thread, the formal-artifact-approval model is not invoked because the fast-lane needs no per-fix packet). `GOV-STANDING-BACKLOG-001` bulk-operation clauses do not apply.

## Problem Statement

`_is_simple_git_finalization_command()` is the git-finalization fast-path of `_is_safe_command()`: when it returns True, the command skips the gate entirely. The function:

1. Rejects the command if `any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS)` - a raw substring scan of the whole command string.
2. Otherwise tokenizes via `shlex.split(command, posix=False)` and confirms `git` plus a finalization subcommand.

Step 1 runs on unparsed text, two lines before the function tokenizes. A `;`, `|`, `&&`, `$(`, or backtick inside a quoted `-m "<message>"` value is indistinguishable from a chaining operator. The consequence chain for a blocked legitimate commit:

1. `_is_simple_git_finalization_command()` returns False (a marker is found in the message).
2. `_is_safe_command()` returns False (`git commit` is not in `SAFE_COMMAND_PREFIXES`).
3. `changed_paths()` calls `_is_mutating_command()`; `MUTATING_COMMAND_RE` matches `git\s+commit` -> mutating True.
4. `_paths_from_shell()` resolves no protected path from the command, so `gate_decision()` substitutes `<unknown-mutating-target>`.
5. `validate_targets()` rejects `<unknown-mutating-target>` (no packet covers it) -> the commit is hard-blocked.

The HEREDOC commit pattern `git commit -m "$(cat <<'EOF' ... EOF)"` trips the identical path via the `$(` marker. The gate should reject genuine chaining; it should not reject a standalone `git commit` / `git push` because its message text contains punctuation.

## Proposed Implementation

### IP-1: quote-aware control-marker check

In `scripts/implementation_start_gate.py`, add a helper that blanks the contents of single- and double-quoted spans, and run the existing marker scan against the blanked text. The marker set (`GIT_FINALIZATION_CONTROL_MARKERS`) is unchanged and stays single-sourced.

```python
def _strip_quoted_spans(command: str) -> str:
    """Blank the contents of single/double-quoted spans so a control-marker
    scan sees only structural (unquoted) shell text.

    Quote characters themselves are preserved; only each span's interior is
    replaced with spaces. A trailing unbalanced quote blanks to end-of-string;
    the caller additionally fails closed because shlex.split raises ValueError
    on an unbalanced quote.
    """
    out: list[str] = []
    quote: str | None = None
    for ch in command:
        if quote is not None:
            out.append(ch if ch == quote else " ")
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        else:
            out.append(ch)
    return "".join(out)
```

The first statement of `_is_simple_git_finalization_command()` changes from:

```python
    if any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS):
        return False
```

to:

```python
    if any(marker in _strip_quoted_spans(command) for marker in GIT_FINALIZATION_CONTROL_MARKERS):
        return False
```

The remainder of the function (the `shlex.split` tokenization, the `git` plus subcommand check, the `git push` denied-flag check) is unchanged. Token extraction continues to use the original `command`, so paths and flags are unaffected.

Behavior:

- `git commit -m "fix X; tidy | done"` -> blanked to `git commit -m "              "` -> no marker -> simple finalization -> exempt.
- `git commit -m "$(cat msg.txt)"` -> blanked to `git commit -m "             "` -> no marker -> exempt.
- `git commit -m "x"; rm -rf y` -> the `; rm -rf y` is outside the quoted message and is preserved -> `;` found -> not simple -> falls through to the mutating-command path and remains gated.
- `git push origin develop` -> unchanged -> exempt.

### IP-2: regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, tagged `# WI-3357`:

- Unit tests on `_is_simple_git_finalization_command()`: markers inside a quoted message return True (commit and push); genuine chaining via `;` and `&&` outside quotes returns False; a plain `git push origin develop` still returns True; a denied `git push --force` flag still returns False.
- Integration tests via `gate_decision()`: a punctuated-message commit returns `{}` (exempt, no auth packet); a chained `git commit -m "<punctuated message>"; Set-Content -Path scripts/sample.py ...` still returns a block decision - proving the quote-aware scan still catches the outside-quote chaining even when the message itself contains markers.

### IP-3: WI-3357 completion

Promote WI-3357 `open` -> `verified` via the governed CLI after Codex VERIFIED.

## Design Decision: control markers inside quoted spans are benign

`_strip_quoted_spans()` blanks the interior of both single- and double-quoted spans uniformly. For `;`, `|`, `&&`, and `||` this is exact shell semantics - those characters are literal inside any quote. For `$(` and a backtick a strict shell reading differs: command substitution still executes inside double quotes (only single quotes suppress it). Treating `$(` / backtick inside double quotes as benign is deliberate:

- It is required to satisfy the owner's stated intent that the documented HEREDOC commit pattern `git commit -m "$(cat <<'EOF' ... EOF)"` (which places `$(` inside double quotes) be accepted. A stricter rule that flagged `$(` unless single-quoted would re-block that pattern.
- The gate's purpose is to stop unreviewed protected implementation mutations, not to sandbox arbitrary command substitution. A genuine protected mutation expressed through tools or direct shell commands is still classified by `MUTATING_COMMAND_RE` / `_paths_from_shell` whenever the command is not a pure `git commit` / `git push`; the finalization exemption only ever applies to a standalone git finalization command.
- Uniform quote handling is simple and predictable and keeps `GIT_FINALIZATION_CONTROL_MARKERS` single-sourced.

The residual exposure - a protected mutation smuggled inside `"$(...)"` in a commit message - is not a realistic accidental-agent behavior and is out of scope for this gate's threat model. Codex review is invited to confirm this stance; a stricter `$(` / backtick rule is available if the owner prefers, at the cost of the HEREDOC pattern.

## Specification-Derived Verification Plan

De-facto specification: a standalone `git commit` / `git push` is a simple finalization command and is exempt regardless of punctuation inside its quoted message; a command that chains another command after the git finalization is not exempt.

| # | Test case | Command | Expected |
|---|---|---|---|
| 1 | marker in quoted message | `git commit -m "fix X; tidy Y"` | `_is_simple_git_finalization_command` True; `gate_decision` `{}` |
| 2 | multiple markers in message | `git commit -m "wip \| cleanup && done"` | `_is_simple_git_finalization_command` True |
| 3 | command substitution in message | `git commit -m "$(cat msg.txt)"` | `_is_simple_git_finalization_command` True |
| 4 | chained via `;` outside quotes | `git commit -m "x"; rm -rf y` | `_is_simple_git_finalization_command` False |
| 5 | chained via `&&` outside quotes | `git commit -m x && rm -rf y` | `_is_simple_git_finalization_command` False |
| 6 | chained protected write, punctuated message | `git commit -m "fix; tidy"; Set-Content -Path scripts/sample.py -Value "z"` | `gate_decision` block |
| 7 | plain push (regression) | `git push origin develop` | `_is_simple_git_finalization_command` True; `gate_decision` `{}` |
| 8 | denied push flag (regression) | `git push --force origin main` | `_is_simple_git_finalization_command` False |

Execution: `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`, plus `python -m ruff check` and `python -m ruff format --check` on both target files. Implementation reaches VERIFIED only when every existing test plus the new WI-3357 tests pass.

## Acceptance Criteria

- IP-1 helper landed; `_is_simple_git_finalization_command()` returns True for cases 1-3 and 7, False for cases 4, 5, and 8.
- IP-2 tests added and passing; `test_chained_git_commit_with_protected_write_still_blocks` and every other existing case in the file still pass (no regression).
- `gate_decision()` returns `{}` for a punctuated-message commit and a block decision for case 6.
- Bridge applicability preflight and ADR/DCL clause preflight both pass for this bridge id.
- `ruff check` and `ruff format --check` are clean on both target files.

## Risks / Rollback

- Risk: a commit message that itself contains an unbalanced quote (for example `git commit -m "it's wip"`). `_strip_quoted_spans` would treat the `'` as opening a single-quoted span; however `shlex.split(command, posix=False)` already raises `ValueError` on the unbalanced quote, and the function returns False (fail-closed, gated). Net effect is unchanged from current behavior for that command shape. An explicit test can be added if Codex requests.
- Risk: a quoted message containing an inner quote of the same kind followed by a marker (for example a HEREDOC body holding both `"` and `;`). Quote-state tracking can mis-segment such a span, potentially re-flagging a marker. This only ever produces a false-negative-of-the-fix (a block, i.e. the current behavior) - never a missed chaining - so it is not a safety regression. Noted for completeness.
- Risk: the change misses an exotic chaining form. The change only ever *adds* exemptions for quoted markers; every unquoted marker still flags exactly as before, so genuine chaining detection is not weakened.
- Rollback: revert the one-line change in `_is_simple_git_finalization_command()` and remove `_strip_quoted_spans()`; the IP-2 tests document the intended behavior and may remain or be reverted with it.

## Recommended Commit Type

`fix:` - corrects a defect in an existing predicate; no new capability surface. Net change is roughly 20-30 lines across two files (one helper, one changed statement, plus tests).
