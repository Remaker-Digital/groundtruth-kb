REVISED

# Implementation Proposal (REVISED-2) - implementation_start_gate finalization-exemption quote-aware control-marker fix (WI-3357)

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 005
Responds to: bridge/gtkb-impl-start-gate-finalization-quoting-fix-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3357

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This REVISED-2 proposal responds to the `-004` NO-GO. It keeps the confirmed defect fix and REVISED-1's quote-semantics-aware two-view marker scan (which Codex's `-004` confirmed correctly resolved the `-002` findings). It replaces ONLY the HEREDOC recognizer: REVISED-1 used a single DOTALL regex whose `.*?` could backtrack past the first heredoc delimiter line and neutralize executable command text after it. REVISED-2 replaces that regex with an explicit forward-scan parser that locates the FIRST delimiter line - the line at which a shell terminates the heredoc - and recognizes the substitution only when nothing but whitespace and the closing `)` follow it.

## Changes Since the -004 NO-GO

The `-004` NO-GO confirmed REVISED-1 correctly resolved the prior `-002` findings (ordinary executable `$(` and backtick remain disqualifying; the verification plan gained negative protected-write cases). It raised two new P1 findings against the HEREDOC recognizer. Both are addressed; the prior NO-GO is explicitly acknowledged here per the deliberation protocol and the REVISED workflow.

- **F1 - the HEREDOC allowlist could hide executable text after an earlier delimiter.** REVISED-1's `_HEREDOC_MESSAGE_SUBSTITUTION_RE` was a single DOTALL/MULTILINE regex: `$(cat <<'DELIM'` then `.*?` then `^DELIM$` then `\s*\)`. A non-greedy `.*?` does NOT lock onto the first delimiter line: when the first delimiter line is not followed by `)`, the regex backtracks and matches a LATER delimiter line, so the match - and the neutralizer that blanks the whole match - swallows any command text between the first delimiter and the later one. Because a quoted heredoc body is literal only up to the FIRST delimiter line, text after it executes as a separate command inside the substitution; blanking it hid an executable protected write from the marker and path scans. REVISED-2 removes the DOTALL regex. The recognizer is now `_find_heredoc_message_substitution_spans()`, a pure parser that matches the fixed `$(cat <<['"]DELIM['"]` opener with a regex, then forward-scans for the FIRST `^DELIM$` line (`^\t*DELIM$` for the `<<-` form), and recognizes the span only when that first delimiter line is followed by optional whitespace and the closing `)`. Any non-whitespace text between the first delimiter line and `)` fails closed (the `$(` stays visible to the marker scan and the command is gated).
- **F2 - the verification plan did not test the first-delimiter boundary.** The REVISED-2 Specification-Derived Verification Plan adds the two negative cases Codex specified: a HEREDOC with an early delimiter line followed by a protected-write command and then a later delimiter before `)`, and the same shape with a `;`-prefixed command. Both must return `_is_simple_git_finalization_command()` False and a `gate_decision()` block. Per Codex's Opportunity Radar note, the recognizer is also covered by direct unit tests over `_find_heredoc_message_substitution_spans()` as a pure parser with an adversarial case table.

REVISED-1's two-view quote-aware marker scan (`_mask_quoted_spans()`, `_has_disqualifying_control_marker()`) and the rewritten `_is_simple_git_finalization_command()` are carried forward unchanged; only the HEREDOC recognizer is replaced.

## Claim

In `scripts/implementation_start_gate.py`, the first line of `_is_simple_git_finalization_command()` is `any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS)` - a raw substring scan of the entire command string, including the quoted `-m "<message>"` value, for the markers `;`, `&&`, `||`, `|`, `$(`, and backtick. The check intends to reject genuine command chaining, but a raw substring scan cannot distinguish a marker that is a shell operator (outside quotes) from a marker that is literal message text (inside quotes). A legitimate `git commit -m "fix X; tidy Y"` is therefore misclassified as chained, loses the finalization exemption, matches `MUTATING_COMMAND_RE` as `git commit` with no resolvable target path, and is hard-blocked at `<unknown-mutating-target>`.

The fix makes the marker check quote-semantics-aware. A chaining marker (`;`, `|`, `&&`, `||`) counts only when it appears outside every quoted span - those characters are literal inside both single and double quotes. An execution marker (`$(`, backtick) counts when it appears outside single quotes - including inside double quotes, where command substitution still executes. A documented HEREDOC message substitution (`$(cat <<'EOF' ... EOF)`) is recognized by an explicit forward-scan parser and neutralized before the scan, because it is provably a read-only `cat` over literal text. Genuine chaining (`git commit -m x; rm -rf y`) keeps its `;` outside the quoted message and remains caught; an executable substitution inside double quotes (`git commit -m "$(Set-Content ...)"`) keeps disqualifying the exemption; a HEREDOC whose substitution would also run a command after the first delimiter line is NOT recognized and remains gated; ordinary punctuated messages and the documented HEREDOC commit pattern pass.

Observed 2026-05-17: routine commits whose message contains a semicolon or pipe, and the `git commit -m "$(cat <<'EOF' ... EOF)"` HEREDOC pattern, are blocked by this PreToolUse gate. The current workaround is to hand-rewrite commit messages to avoid punctuation; this fix removes the need for that workaround while preserving the gate's true-positive coverage.

## Reliability Fast-Lane Eligibility

This work item is routed via the reliability fast-lane per `GOV-RELIABILITY-FAST-LANE-001`. The eligibility criteria hold:

1. `origin` is `defect` (WI-3357, verified in MemBase) - never `new`.
2. No new public API or CLI surface. The change narrows a false-negative in an existing predicate and, per the owner's Option B decision, makes that same predicate correctly recognize one documented commit-message form (the HEREDOC `cat` substitution) that `-001` already itemized as a wrongly-blocked legitimate case. Both are corrections to the finalization exemption's faithfulness to commit-message reality, not a new feature surface; the exemption's true-positive coverage (rejecting genuine chaining and executable substitution) is preserved and regression-tested.
3. No new or revised requirement or specification. The predicate's intent is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread. The owner's Option B threat-model decision is captured as proposal evidence in `## Owner Decisions / Input`; Codex's `-004` confirmed no further owner decision is needed for this revision.
4. Single-concern: one predicate, one defect family, two files. The implementation delta is modest (a split constant, one opener regex, one parser, two small marker-scan helpers, one rewritten function). The test delta is larger because Codex's F2 finding requires thorough negative coverage of the command-substitution and first-delimiter boundaries; test additions are an explicitly fast-lane-allowed mutation class (`test_addition`).

`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (status `active`, `included_work_item_ids` null) covers WI-3357 by active project membership (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3357`, status active). The standing authorization's `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade` - the change edits a hook script (`source` / `hook_upgrade`) and adds tests (`test_addition`); none of the `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are performed.

## In-Root Placement Evidence

Both target paths are in-root under the canonical `E:\GT-KB` checkout: `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`. The bridge file is `bridge/gtkb-impl-start-gate-finalization-quoting-fix-005.md`. No `applications/`-tree paths are involved. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement is satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this thread flows NEW -> NO-GO -> REVISED -> NO-GO -> REVISED -> GO -> implement -> report -> VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the predicate's intent to executed tests, including the first-delimiter boundary.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate is the hook that enforces this protected behavior; the fix narrows a false-negative and adds one provably-read-only exemption without weakening the gate's true-positive (chaining and executable-substitution detection) coverage.
- `GOV-RELIABILITY-FAST-LANE-001` - the governing fast-lane policy; eligibility is argued above.
- `GOV-STANDING-BACKLOG-001` - WI-3357 is a single tracked work item; this is not a bulk operation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root; no application-tree paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, the owner decision, and verification are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across WI-3357, this thread, the tests, and the implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3357 moves through open -> implementing -> verified lifecycle states.

No directly-governing functional specification exists for the gate's command classifier - the hook is its own implementation surface. The predicate's intent (exempt a simple standalone `git commit` / `git push`; reject genuine chaining and executable command substitution) is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread (VERIFIED). This proposal is a defect fix that makes the chaining detector faithful to that intent under shell quoting and heredoc semantics; the verification plan proves the false-negative removal, the preserved true-positive coverage, and the safety of the narrow HEREDOC exemption including the first-delimiter boundary.

## Prior Deliberations

A Deliberation Archive semantic search for "implementation-start gate git finalization command classification chaining quoted command substitution HEREDOC" returned no directly-relevant DELIB record (Codex's `-002` and `-004` reviews independently confirmed the targeted search returns `[]`). The prior-decision history for this surface is the bridge-thread record:

- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-004.md` (NO-GO, this thread) - Codex's review of REVISED-1. It confirmed REVISED-1 resolved the `-002` findings, and NO-GO'd on F1 (the DOTALL `.*?` regex can backtrack past the first heredoc delimiter line and neutralize executable command text after it) and F2 (no test for that early-delimiter boundary). REVISED-2 acknowledges both findings in `## Changes Since the -004 NO-GO` and resolves them with the forward-scan parser and the added negative tests.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-002.md` (NO-GO, this thread) - Codex's review of `-001`. It NO-GO'd `-001`'s blanket double-quote blanking (F1) and the missing command-substitution negative test (F2). REVISED-1 resolved both; REVISED-2 carries that resolution forward unchanged.
- `bridge/gtkb-implementation-start-gate-repository-finalization` (VERIFIED) - introduced `_is_simple_git_finalization_command()` and its control-marker check. Its `-001` proposal states the design intent verbatim: "reject the safe classification if shell chaining or control markers are present, such as `;`, `&&`, `||`, `|`, command substitution, or backtick execution." REVISED-2 preserves that intent: command substitution and backtick execution still disqualify the exemption wherever they remain executable; only provably-literal markers (chaining markers in any quote, execution markers in single quotes, and a read-only HEREDOC `cat` substitution whose first delimiter line is immediately followed by `)`) are exempted.
- `bridge/gtkb-impl-start-gate-comparison-operator-fix` (VERIFIED, WI-3356) - a sibling fix in the same file: `MUTATING_COMMAND_RE` naive `>`-substring matching misclassified Python `>=` / `>>=`. Same root-cause class (substring/regex matching that ignores syntactic context), different construct and function.
- `bridge/gtkb-impl-start-gate-format-spec-fix` (VERIFIED, WI-3317) - a sibling fix in the same file: `MUTATING_COMMAND_RE` misclassified Python format-spec `:>` alignment. Same root-cause class, different construct and function.

This proposal is a distinct, fourth member of that defect family: it targets `_is_simple_git_finalization_command()` (not `MUTATING_COMMAND_RE`), and the original substring artifact is a *false-negative* (an exemption wrongly withheld), not a false-positive. The two comparison-operator / format-spec threads are terminal (VERIFIED); there is no live coordination dependency.

## Owner Decisions / Input

WI-3357 is routed through the reliability fast-lane, so per `GOV-RELIABILITY-FAST-LANE-001` it carries no per-fix Deliberation Archive record or formal-artifact-approval packet; the owner-decision evidence is recorded here.

- **Option B threat-model decision (owner, 2026-05-17, this session).** Codex's `-002` `Owner Action` stated that exempting executable `$(` / backtick expressions inside double-quoted commit messages "is a new threat-model decision and should be presented to the owner explicitly before refiling." The owner was presented two options: Option A - ship the narrow fix only (chaining markers `;` / `|` / `&&` / `||` inside quoted messages exempted, the HEREDOC pattern stays blocked); Option B - additionally support the documented HEREDOC `$(cat <<'EOF' ... EOF)` commit pattern, accepting the threat-model tradeoff. The owner selected **Option B**. REVISED-1 and this REVISED-2 implement Option B.
- **No further owner decision required for REVISED-2.** Codex's `-004` `Owner Action` states: "None. ... No additional owner decision is needed for this NO-GO because the blocker is implementation safety inside the already-selected Option B scope." REVISED-2's change is a tighter HEREDOC recognizer within the already-approved Option B scope.
- **Scope of what Option B authorizes.** Option B authorizes ONLY the narrowly-recognized `$(cat <<'QUOTED-DELIM' ... DELIM)` HEREDOC shape: a read-only `cat` reading a quoted-delimiter heredoc whose first delimiter line is immediately followed by the substitution's closing `)`. It does NOT authorize a blanket exemption of `$(` / backtick inside double quotes. Bare `$(...)` command substitution and backtick execution inside double quotes (or unquoted), and a HEREDOC substitution that would run any further command, remain disqualifying and gated. The threat-model basis is in `## Threat Model`.
- **Standing implementation authorization.** `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) authorizes implementation on WI-3357 by active project membership in `PROJECT-GTKB-RELIABILITY-FIXES`.
- **Originating owner directive (2026-05-17).** The owner reported that the implementation-start gate blocks `git commit` / `git push` whenever the commit message contains shell punctuation (`;`, `|`, `&&`, `$(`, backtick), and directed a root-cause fix via the bridge protocol / reliability fast-lane rather than continued use of the message-rewrite workaround.

## Requirement Sufficiency

Existing requirements sufficient. The predicate's intent is well established by the `gtkb-implementation-start-gate-repository-finalization` thread and `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`. This proposal narrows a false-negative and adds one owner-approved, provably-read-only exemption without changing the gate's protective intent; no new or revised requirement or specification is required before implementation.

## Clause Scope Clarification (Not a Bulk Operation)

This is NOT a bulk operation. Exactly one work item (WI-3357) is the operative target; it is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`. There are no spec status mutations, no narrative-artifact edits, and no batch work-item promotion, retirement, or inventory. The review-packet inventory is IP-1 (a one-function fix plus its helpers) plus IP-2 (regression tests) in a single thread, plus IP-3 (the WI lifecycle transition). References to "work item", "backlog", and "standing" authorization describe the fast-lane routing, not a bulk backlog operation; the supporting evidence is per-artifact (WI-3357, this thread). `GOV-STANDING-BACKLOG-001` bulk-operation clauses do not apply.

## Problem Statement

`_is_simple_git_finalization_command()` is the git-finalization fast-path of `_is_safe_command()`: when it returns True, the command skips the gate entirely. The function:

1. Rejects the command if `any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS)` - a raw substring scan of the whole command string.
2. Otherwise tokenizes via `shlex.split(command, posix=False)` and confirms `git` plus a finalization subcommand.

Step 1 runs on unparsed text, two lines before the function tokenizes. A `;`, `|`, `&&`, `||`, `$(`, or backtick inside a quoted `-m "<message>"` value is indistinguishable from a chaining operator. The consequence chain for a blocked legitimate commit:

1. `_is_simple_git_finalization_command()` returns False (a marker is found in the message).
2. `_is_safe_command()` returns False (`git commit` is not in `SAFE_COMMAND_PREFIXES`).
3. `changed_paths()` calls `_is_mutating_command()`; `MUTATING_COMMAND_RE` matches `git\s+commit` -> mutating True.
4. `_paths_from_shell()` resolves no protected path from the command, so `gate_decision()` substitutes `<unknown-mutating-target>`.
5. `validate_targets()` rejects `<unknown-mutating-target>` (no packet covers it) -> the commit is hard-blocked.

The HEREDOC commit pattern `git commit -m "$(cat <<'EOF' ... EOF)"` trips the identical path via the `$(` marker. The gate should reject genuine chaining and executable command substitution; it should not reject a standalone `git commit` / `git push` because its message text contains literal punctuation, and it should not reject the documented HEREDOC commit pattern, whose substitution is a provably read-only literal-text generation.

## Proposed Implementation

IP-1 carries forward, unchanged from REVISED-1, the two-view quote-aware marker scan that resolved the `-002` findings. It replaces ONLY the HEREDOC recognizer.

### IP-1a: quote-semantics-aware control-marker check (unchanged from REVISED-1)

In `scripts/implementation_start_gate.py`, split the marker constant into two classes by shell quoting semantics, retaining the combined name for compatibility:

```python
# Markers that disqualify the simple git-finalization exemption, split by
# shell quoting semantics so the scan can be quote-aware (WI-3357):
#   - chaining markers are literal inside EITHER quote type;
#   - execution markers still run inside double quotes (literal only inside
#     single quotes).
GIT_FINALIZATION_CHAINING_MARKERS = (";", "&&", "||", "|")
GIT_FINALIZATION_EXECUTION_MARKERS = ("$(", "`")
GIT_FINALIZATION_CONTROL_MARKERS = (
    GIT_FINALIZATION_CHAINING_MARKERS + GIT_FINALIZATION_EXECUTION_MARKERS
)
```

Add the two-view marker-scan helpers (unchanged from REVISED-1):

```python
def _mask_quoted_spans(command: str, *, mask_double: bool) -> str:
    """Return `command` with quoted-span interiors replaced by spaces.

    Single-quoted span interiors are always blanked: single quotes make every
    shell metacharacter literal. Double-quoted span interiors are blanked only
    when `mask_double` is True -- double quotes make `;`, `|`, `&&` and `||`
    literal, but `$(` and backtick still execute inside them, so the
    execution-marker scan must keep double-quoted interiors visible.

    Quote characters are preserved. Backslash escaping is intentionally not
    modeled: a mis-segmented span can only end early and expose more text to
    the scan; it can never hide a structural operator (fail-closed). An
    unbalanced trailing quote blanks to end-of-string; the caller also fails
    closed because shlex.split raises ValueError on an unbalanced quote.
    """
    out: list[str] = []
    quote: str | None = None
    for ch in command:
        if quote is not None:
            blank = quote == "'" or mask_double
            out.append(" " if (blank and ch != quote) else ch)
            if ch == quote:
                quote = None
        elif ch in ("'", '"'):
            quote = ch
            out.append(ch)
        else:
            out.append(ch)
    return "".join(out)


def _has_disqualifying_control_marker(command: str) -> bool:
    """True iff a control marker disqualifies the git-finalization exemption.

    `command` must already have safe HEREDOC substitutions neutralized.
    Chaining markers (`;`, `|`, `&&`, `||`) count only outside every quote;
    execution markers (`$(`, backtick) count outside single quotes, including
    inside double quotes where they still execute.
    """
    chaining_view = _mask_quoted_spans(command, mask_double=True)
    if any(marker in chaining_view for marker in GIT_FINALIZATION_CHAINING_MARKERS):
        return True
    execution_view = _mask_quoted_spans(command, mask_double=False)
    return any(marker in execution_view for marker in GIT_FINALIZATION_EXECUTION_MARKERS)
```

### IP-1b: HEREDOC recognizer - forward-scan parser (replaces the REVISED-1 DOTALL regex)

Replace REVISED-1's `_HEREDOC_MESSAGE_SUBSTITUTION_RE` (DOTALL `.*?` regex) and its one-line `re.sub` neutralizer with a fixed-opener regex plus an explicit forward-scan parser:

```python
# WI-3357 (REVISED-2): opener of the documented HEREDOC commit-message pattern
#   git commit -m "$(cat <<'EOF' ... EOF)"
# This regex matches ONLY the fixed opener `$(cat <<['"]DELIM['"]`. The
# heredoc-terminating delimiter line and the substitution's closing `)` are
# located by an explicit forward scan in
# _find_heredoc_message_substitution_spans(), NOT by a backtracking regex, so
# the recognizer cannot skip past the FIRST delimiter line -- the line at
# which a shell terminates the heredoc.
_HEREDOC_OPENER_RE = re.compile(
    r"\$\(\s*cat\s+<<(?P<dash>-?)\s*"
    r"(?P<q>['\"])(?P<delim>[A-Za-z_][A-Za-z0-9_]*)(?P=q)"
)


def _find_heredoc_message_substitution_spans(command: str) -> list[tuple[int, int]]:
    """Return [start, end) spans of provably-safe `$(cat <<'DELIM' ... DELIM)`
    command substitutions.

    For each `$(cat <<['"]DELIM['"]` opener, the heredoc body ends at the
    FIRST line equal to DELIM (a bare `DELIM` line; or a tab-indented `DELIM`
    line for the `<<-` form, which strips leading tabs). That first delimiter
    line is exactly where a POSIX shell terminates the heredoc. A span is
    recognized only when that first delimiter line is followed by optional
    whitespace and then the closing `)` of the substitution. Any non-whitespace
    text between the first delimiter line and `)` would be a second command
    running inside the substitution, so the span is NOT recognized and the
    `$(` stays visible to the control-marker scan (fail closed). A recognized
    span therefore runs only read-only `cat` over a literal (quoted-delimiter)
    heredoc body.
    """
    spans: list[tuple[int, int]] = []
    search_from = 0
    while True:
        opener = _HEREDOC_OPENER_RE.search(command, search_from)
        if opener is None:
            break
        prefix = r"\t*" if opener.group("dash") else ""
        delim_line_re = re.compile(
            rf"^{prefix}{re.escape(opener.group('delim'))}$", re.MULTILINE
        )
        delim_line = delim_line_re.search(command, opener.end())
        if delim_line is None:
            search_from = opener.end()
            continue
        rest = command[delim_line.end() :]
        after_ws = rest.lstrip()
        if after_ws.startswith(")"):
            close = delim_line.end() + (len(rest) - len(after_ws)) + 1
            spans.append((opener.start(), close))
            search_from = close
        else:
            search_from = opener.end()
    return spans


def _neutralize_heredoc_message_substitutions(command: str) -> str:
    """Blank each provably-safe `$(cat <<'DELIM' ... DELIM)` substitution span.

    A recognized span runs only read-only `cat` over a quoted-delimiter
    heredoc body (literal text), so it is side-effect-free and is removed
    before the control-marker scan. Text that does not match the recognized
    shape is left intact and stays subject to the full scan (fail closed).
    """
    spans = _find_heredoc_message_substitution_spans(command)
    if not spans:
        return command
    out: list[str] = []
    cursor = 0
    for start, end in spans:
        out.append(command[cursor:start])
        out.append(" " * (end - start))
        cursor = end
    out.append(command[cursor:])
    return "".join(out)
```

### IP-1c: rewritten predicate (unchanged from REVISED-1)

```python
def _is_simple_git_finalization_command(command: str) -> bool:
    scan_command = _neutralize_heredoc_message_substitutions(command)
    if _has_disqualifying_control_marker(scan_command):
        return False
    try:
        tokens = [_clean_shell_token(token).lower() for token in shlex.split(scan_command, posix=False)]
    except ValueError:
        return False
    tokens = [token for token in tokens if token]
    if len(tokens) < 2 or tokens[0] != "git" or tokens[1] not in GIT_FINALIZATION_SUBCOMMANDS:
        return False
    return not (tokens[1] == "push" and any(token in GIT_FINALIZATION_DENIED_FLAGS for token in tokens[2:]))
```

The `git push` denied-flag check, the `git` plus subcommand check, and `_clean_shell_token` are unchanged. Tokenization runs on `scan_command` (the HEREDOC-neutralized command); the safety-relevant tokens (`git`, the subcommand, and `--force` / `-f` / `--force-with-lease`) are always unquoted and outside any `$(...)`, so neutralization never touches them.

Behavior summary:

- `git commit -m "fix X; tidy | done"` -> no HEREDOC; chaining-view masks the double-quoted span -> no chaining marker; execution-view has no `$(` / backtick -> simple finalization -> exempt.
- `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` -> not a HEREDOC `cat` substitution -> not neutralized; execution-view keeps `$(` visible -> disqualified -> not simple -> remains gated.
- `git commit -m "$(cat <<'EOF' ... EOF)"` (single heredoc, first delimiter line then `)`) -> recognized -> neutralized -> simple finalization -> exempt.
- `git commit -m "$(cat <<'EOF' ... EOF <command> EOF)"` (a command after the first delimiter line) -> the first delimiter line is not followed by `)` -> NOT recognized -> `$(` stays visible -> disqualified -> remains gated.
- `git commit -m "x"; rm -rf y` -> the `;` is outside the quoted message -> chaining-view keeps `;` -> disqualified -> remains gated.
- `git push --force origin main` -> `--force` token -> denied -> not simple.

### IP-2: regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, tagged `# WI-3357`, following the existing direct-unit-test pattern (`gate._is_mutating_command(...)`) and integration-test pattern (`gate.gate_decision(payload)`):

- Direct unit tests on `gate._is_simple_git_finalization_command(...)` for every numbered case in the Specification-Derived Verification Plan below.
- Integration tests via `gate.gate_decision(payload)` (Bash tool payload, no authorization packet seeded) for every case whose `gate_decision` column is not `n/a`: exempt cases assert `gate.gate_decision(payload) == {}`; gated cases assert `result["decision"] == "block"` and `"authorization packet" in result["reason"]`.
- Direct unit tests on `gate._find_heredoc_message_substitution_spans(...)` as a pure parser, with an adversarial table: documented single heredoc (one span), unquoted delimiter (no span), non-`cat` opener (no span), early delimiter then command then later delimiter (no span), early delimiter then `;`-command (no span), no delimiter line at all (no span), and two independent heredocs (two spans).
- The F2 cases (16, 17) and the HEREDOC-boundary negatives are mandatory and land in this slice; no test is deferred.

All existing tests in `platform_tests/scripts/test_implementation_start_gate.py` - including `test_git_commit_finalization_command_is_allowed_without_authorization`, `test_git_push_finalization_command_is_allowed_without_authorization`, and `test_chained_git_commit_with_protected_write_still_blocks` - must continue to pass unchanged.

### IP-3: WI-3357 completion

Promote WI-3357 `open` -> `verified` via the governed CLI after Codex records VERIFIED on the post-implementation report.

## Threat Model

The finalization exemption exists to let a standalone `git commit` / `git push` skip the implementation-start gate. The gate's protective job is to stop unreviewed protected source, test, script, hook, configuration, deployment, repository-state, and KB-mutation work. REVISED-2 must not let any protected mutation run through the exemption.

**Safety invariant.** The change can only ever ADD an exemption in three provably-safe cases: (1) a chaining marker (`;`, `|`, `&&`, `||`) inside any quoted span - literal in both quote types; (2) an execution marker (`$(`, backtick) inside a single-quoted span - literal, because single quotes suppress all expansion; (3) a `$(cat <<'QUOTED-DELIM' ... DELIM)` substitution recognized by `_find_heredoc_message_substitution_spans()`. Every other marker continues to disqualify the exemption. Any quote mis-segmentation can only end a span early and expose more text to the scan (fail-closed), never hide an operator. Any HEREDOC shape the parser does not recognize is not neutralized, so its `$(` / backtick keeps disqualifying the exemption (fail-closed).

**Why the HEREDOC parser is safe (the F1 fix).** `_find_heredoc_message_substitution_spans()` recognizes a `$(...)` span only when ALL of the following hold:

1. The substitution opens with `$(cat <<['"]DELIM['"]` - the only command is read-only `cat`, and the heredoc delimiter is quoted, so the heredoc body is a literal string (no parameter, command, or arithmetic expansion).
2. The body ends at the FIRST line equal to DELIM. The parser locates that line with `delim_line_re.search(command, opener.end())`; `re.search` returns the leftmost match, so the parser's delimiter line is the first one. The delimiter-line pattern is `^DELIM$` for the plain `<<` form and `^\t*DELIM$` for the `<<-` form (which strips leading tabs) - byte-identical to the line at which a POSIX shell terminates the heredoc. The parser and the shell therefore agree on which line ends the heredoc; the parser never skips past it. This is the precise defect REVISED-1's DOTALL `.*?` regex had: a non-greedy `.*?` backtracks, so it could match a LATER delimiter line and the neutralizer would blank the executable text in between.
3. The first delimiter line is immediately followed by optional whitespace and the closing `)`. The parser checks `command[delim_line.end():].lstrip().startswith(")")`. If any non-whitespace text appears between the first delimiter line and `)`, the span is not recognized - so a second command after the heredoc-terminating line can never be hidden inside a recognized span.

A span passing all three runs only `cat` over literal heredoc text; the runtime effect of `git commit -m "$(cat <<'EOF' ... EOF)"` is exactly `git commit -m "<literal text>"`. Anything the parser does not recognize stays fully visible to the marker scan and is independently gated. The composition fails closed: in Codex's `-004` adversarial case (`$(cat <<'EOF'\nmsg\nEOF\nSet-Content ...\nEOF\n)`), the first `EOF` line is followed by `Set-Content ...`, not `)`, so the span is not recognized, the `$(` stays visible, and the command is gated.

**Residual exposure.** The exemption permits `cat` to read inline literal text. It permits no file write, no KB mutation, no repository-state change, and no execution of message-body content or of any command after the heredoc-terminating line.

**Option rationale.** Codex's `-004` F1 `Recommended action` named the required design: "Replace the DOTALL whole-command allowlist with a parser that recognizes the first delimiter line after the `$(cat <<'DELIM'` opener. The command should be allowlisted only when that first delimiter line is followed by optional whitespace and the closing `)` ... Any non-whitespace text between the first delimiter and `)` must fail closed." REVISED-2 implements exactly that. A regex-only recognizer was rejected because a backtracking quantifier cannot prove "first delimiter line"; the forward-scan parser makes the proof explicit and is unit-testable as a pure function (per Codex's Opportunity Radar note). A non-HEREDOC `$(cat file)` substitution is deliberately NOT allowlisted; `git commit -F <file>` is git's native mechanism for a message read from a file and is already exempt (it contains no `$(`).

## Specification-Derived Verification Plan

De-facto specification: a standalone `git commit` / `git push` is a simple finalization command and is exempt regardless of literal punctuation inside its quoted message; the documented HEREDOC `$(cat <<'QUOTED-DELIM' ... DELIM)` message substitution is exempt only when its first delimiter line is immediately followed by the closing `)`; a command that chains another command, that runs executable command substitution inside double quotes (other than the recognized HEREDOC `cat` form), or that runs any command after the heredoc-terminating line, is not exempt.

In the Command column, `\n` denotes a literal newline; HEREDOC commands span multiple lines, with each `DELIM` line at column 0.

| # | Test case | Command | `_is_simple...` | `gate_decision` |
|---|---|---|---|---|
| 1 | chaining markers literal in a double-quoted message | `git commit -m "fix X; tidy \| done && wrap"` | True | `{}` |
| 2 | chaining marker literal in a single-quoted message | `git commit -m 'fix X; tidy Y'` | True | n/a |
| 3 | HEREDOC message substitution, single-quoted delimiter (Option B) | `git commit -m "$(cat <<'EOF'\nmsg body\nEOF\n)"` | True | `{}` |
| 4 | HEREDOC message substitution, double-quoted delimiter (Option B) | `git commit -m "$(cat <<"EOF"\nmsg\nEOF\n)"` | True | n/a |
| 5 | command substitution running a protected write, double-quoted (F1/F2) | `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` | False | block |
| 6 | backtick command substitution running a protected write (F1/F2) | `` git commit -m "`Set-Content -Path scripts/sample.py -Value z`" `` | False | block |
| 7 | non-HEREDOC command substitution inside a double-quoted message | `git commit -m "$(cat msg.txt)"` | False | block |
| 8 | HEREDOC with an UNQUOTED delimiter - body would expand | `git commit -m "$(cat <<EOF\nmsg\nEOF\n)"` | False | block |
| 9 | non-`cat` command in a HEREDOC-shaped substitution | `git commit -m "$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)"` | False | block |
| 10 | `$(` provably literal inside single quotes | `git commit -m '$(whoami)'` | True | n/a |
| 11 | genuine chaining via `;` after the git finalization | `git commit -m "x"; rm -rf y` | False | n/a |
| 12 | chained protected write after a punctuated double-quoted message | `git commit -m "fix; tidy"; Set-Content -Path scripts/sample.py -Value "z"` | False | block |
| 13 | chained protected write after a complete HEREDOC commit | `git commit -m "$(cat <<'EOF'\nmsg\nEOF\n)" && Set-Content -Path scripts/sample.py -Value z` | False | block |
| 14 | plain push (regression) | `git push origin develop` | True | `{}` |
| 15 | denied push flag (regression) | `git push --force origin main` | False | n/a |
| 16 | early delimiter then a protected write then a later delimiter (F1/F2) | `git commit -m "$(cat <<'EOF'\nmsg\nEOF\nSet-Content -Path scripts/sample.py -Value z\nEOF\n)"` | False | block |
| 17 | early delimiter then a `;`-prefixed protected write then a later delimiter (F1/F2) | `git commit -m "$(cat <<'EOF'\nmsg\nEOF\n; Set-Content -Path scripts/sample.py -Value z\nEOF\n)"` | False | block |

Cases 16 and 17 are the F2-mandated negatives proving the first-delimiter bypass is closed; they are the exact shapes named in Codex's `-004` F2 `Recommended action`. Cases 5 and 6 prove ordinary command substitution stays gated; cases 7, 8, 9 are HEREDOC-boundary negatives. Cases 1-4 and 10 prove the false-negative removal; cases 11-13 prove preserved chaining detection; cases 14-15 are existing-behavior regressions. Direct `_find_heredoc_message_substitution_spans()` unit tests cover the parser with the adversarial table described in IP-2.

Execution: `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`, plus `python -m ruff check` and `python -m ruff format --check` on both target files. The implementation report reaches VERIFIED only when every existing test plus the new WI-3357 tests pass.

## Acceptance Criteria

- IP-1 landed: the split marker constants, `_mask_quoted_spans()`, `_has_disqualifying_control_marker()`, `_HEREDOC_OPENER_RE`, `_find_heredoc_message_substitution_spans()`, `_neutralize_heredoc_message_substitutions()`, and the rewritten `_is_simple_git_finalization_command()`. REVISED-1's `_HEREDOC_MESSAGE_SUBSTITUTION_RE` DOTALL regex is removed.
- `_is_simple_git_finalization_command()` returns True for verification cases 1-4, 10, and 14; False for cases 5-9, 11, 12, 13, 15, 16, and 17.
- `gate_decision()` returns `{}` for cases 1, 3, and 14; returns a `block` decision for cases 5, 6, 7, 8, 9, 12, 13, 16, and 17.
- `_find_heredoc_message_substitution_spans()` returns the expected spans for the IP-2 adversarial parser table.
- IP-2 tests added and passing; every existing test in `platform_tests/scripts/test_implementation_start_gate.py` still passes (no regression).
- Bridge applicability preflight and ADR/DCL clause preflight both pass for this bridge id.
- `ruff check` and `ruff format --check` are clean on both target files.

## Risks / Rollback

- Risk: backslash-escaped quotes inside a double-quoted message are not modeled by `_mask_quoted_spans`. The scanner never treats a `"` as escaped, so it can only end a span early relative to a true shell parse - exposing more text to the marker scan. The effect is fail-closed (a benign command may be gated, never a chaining command exempted). Unchanged from current behavior for that command shape.
- Risk: a commit message with an unbalanced quote. `shlex.split(scan_command, posix=False)` raises `ValueError`, the function returns False, and the command is gated (fail-closed, unchanged from current behavior).
- Risk: a HEREDOC the parser does not recognize (unquoted delimiter, a command other than `cat`, a command after the heredoc-terminating line, `\r\n` line endings, or a PowerShell here-string, which uses `@'...'@` rather than `<<`). It is not neutralized, so its `$(` / backtick disqualifies the exemption and the command is gated. This is fail-closed and intentional; the parser recognizes the documented bash HEREDOC commit pattern with `\n` line endings, which is how bash heredocs are themselves delimited.
- Risk: the parser's first-delimiter-line semantics differ from the shell. The delimiter-line patterns (`^DELIM$` for `<<`, `^\t*DELIM$` for `<<-`) are byte-identical to where a POSIX shell terminates the heredoc, and `re.search` returns the leftmost (first) match, so the parser's delimiter line is exactly the shell's. There is no later delimiter line the parser would skip to.
- Rollback: revert the constant split, the marker-scan helpers, the opener regex, the parser, the neutralizer, and the rewritten function; the pre-fix `GIT_FINALIZATION_CONTROL_MARKERS` substring scan is restored by reverting one function body. The IP-2 tests document the intended behavior and may remain or be reverted with the change.

## Recommended Commit Type

`fix:` - corrects a defect in an existing predicate (the finalization exemption wrongly disqualifies standalone git commits whose message contains literal shell punctuation, and wrongly disqualifies the documented HEREDOC commit pattern). No new public API, CLI surface, or capability is added; the HEREDOC allowlist makes the existing exemption faithful to a documented commit form. Net change is roughly 70-90 lines in `scripts/implementation_start_gate.py` (split constant, two marker-scan helpers, one opener regex, one parser, one neutralizer, one rewritten function) and roughly 110-130 lines of tests in `platform_tests/scripts/test_implementation_start_gate.py`.
