REVISED

# Implementation Proposal (REVISED-3) - implementation_start_gate finalization-exemption quote-aware control-marker fix (WI-3357)

bridge_kind: prime_proposal
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 007
Responds to: bridge/gtkb-impl-start-gate-finalization-quoting-fix-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3357

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This REVISED-3 proposal responds to the `-006` NO-GO. It keeps the confirmed defect fix, REVISED-1's quote-semantics-aware two-view marker scan, and REVISED-2's first-delimiter-line parser (Codex's `-006` confirmed both resolved their respective prior findings). It adds the one remaining boundary the REVISED-2 parser did not validate: the opener-line tail. After the `$(cat <<['"]DELIM['"]` opener, a shell can place an output redirect, a command separator, or a pipeline on the same line before the heredoc body begins; REVISED-2 would have blanked that executable tail along with the safe span. REVISED-3 requires the opener-line tail to be whitespace-only and fails closed otherwise, and the Threat Model now enumerates every region of a recognized span so no boundary is left unexamined.

## Changes Since the -006 NO-GO

The `-006` NO-GO confirmed REVISED-2 resolved the `-004` first-delimiter blocker (the parser now finds the first delimiter line and requires the substitution to close after it) and that the `-002` finding remains resolved (ordinary executable `$(` / backtick inside double quotes still disqualify). It raised two new P1 findings. Both are addressed; the prior NO-GO is explicitly acknowledged here per the deliberation protocol and the REVISED workflow.

- **F1 - the HEREDOC parser did not validate the opener-line tail.** REVISED-2's `_HEREDOC_OPENER_RE` matched only through `$(cat <<['"]DELIM['"]` and the parser then searched forward for the first delimiter line. It never checked the text between the quoted delimiter and the body's first newline - the opener-line tail. Quoted heredoc semantics make only the heredoc *body* literal; same-line shell syntax after the heredoc redirection still executes. A command can place an output redirection (`$(cat <<'EOF' > scripts/sample.py`), a command separator (`$(cat <<'EOF'; Set-Content ...`), or a pipeline (`$(cat <<'EOF' | tee scripts/sample.py`) on the opener line, and REVISED-2's neutralizer would blank that executable tail along with the recognized span - hiding it from the marker and path scans. REVISED-3 fixes this: after `_HEREDOC_OPENER_RE` matches, the parser locates the next newline and requires `command[opener.end():newline]` to be whitespace-only; the delimiter-line search starts after that newline; any non-whitespace opener-line tail fails closed (the `$(` stays visible to the execution-marker scan). The opener regex's internal whitespace is also tightened from `\s` to `[ \t]` so the opener is a single physical line, making the opener-line-tail boundary crisp.
- **F2 - the verification plan lacked opener-line tail negatives.** The REVISED-3 Specification-Derived Verification Plan adds the three opener-line-tail negative cases Codex specified: an output-redirection tail, a command-separator tail, and a pipeline tail. Each must return `_find_heredoc_message_substitution_spans()` no span, `_is_simple_git_finalization_command()` False, and a `gate_decision()` block. The direct parser unit-test table is extended with the same opener-line-tail shapes.

REVISED-1's two-view quote-aware marker scan (`_mask_quoted_spans()`, `_has_disqualifying_control_marker()`), the rewritten `_is_simple_git_finalization_command()`, and REVISED-2's first-delimiter-line search are carried forward; only the opener-line-tail validation is added to the parser.

## Claim

In `scripts/implementation_start_gate.py`, the first line of `_is_simple_git_finalization_command()` is `any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS)` - a raw substring scan of the entire command string, including the quoted `-m "<message>"` value, for the markers `;`, `&&`, `||`, `|`, `$(`, and backtick. The check intends to reject genuine command chaining, but a raw substring scan cannot distinguish a marker that is a shell operator (outside quotes) from a marker that is literal message text (inside quotes). A legitimate `git commit -m "fix X; tidy Y"` is therefore misclassified as chained, loses the finalization exemption, matches `MUTATING_COMMAND_RE` as `git commit` with no resolvable target path, and is hard-blocked at `<unknown-mutating-target>`.

The fix makes the marker check quote-semantics-aware. A chaining marker (`;`, `|`, `&&`, `||`) counts only when it appears outside every quoted span. An execution marker (`$(`, backtick) counts when it appears outside single quotes - including inside double quotes, where command substitution still executes. A documented HEREDOC message substitution (`$(cat <<'EOF' ... EOF)`) is recognized by an explicit forward-scan parser and neutralized before the scan, because - once all its boundaries are validated - it is provably a read-only `cat` over literal text. Genuine chaining keeps its `;` outside the quoted message and remains caught; an executable substitution inside double quotes keeps disqualifying the exemption; a HEREDOC whose substitution would also run a redirect, separator, pipeline, or any command before or after the heredoc body is NOT recognized and remains gated; ordinary punctuated messages and the documented HEREDOC commit pattern pass.

Observed 2026-05-17: routine commits whose message contains a semicolon or pipe, and the `git commit -m "$(cat <<'EOF' ... EOF)"` HEREDOC pattern, are blocked by this PreToolUse gate. The current workaround is to hand-rewrite commit messages to avoid punctuation; this fix removes the need for that workaround while preserving the gate's true-positive coverage.

## Reliability Fast-Lane Eligibility

This work item is routed via the reliability fast-lane per `GOV-RELIABILITY-FAST-LANE-001`. The eligibility criteria hold:

1. `origin` is `defect` (WI-3357, verified in MemBase) - never `new`.
2. No new public API or CLI surface. The change narrows a false-negative in an existing predicate and, per the owner's Option B decision, makes that same predicate correctly recognize one documented commit-message form (the HEREDOC `cat` substitution) that `-001` already itemized as a wrongly-blocked legitimate case. Both are corrections to the finalization exemption's faithfulness to commit-message reality, not a new feature surface; the exemption's true-positive coverage (rejecting genuine chaining and executable substitution) is preserved and regression-tested.
3. No new or revised requirement or specification. The predicate's intent is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread. The owner's Option B threat-model decision is captured as proposal evidence in `## Owner Decisions / Input`; Codex's `-004` and `-006` both confirmed no further owner decision is needed for this revision.
4. Single-concern: one predicate, one defect family, two files. The implementation delta is modest (a split constant, one opener regex, one parser, two small marker-scan helpers, one rewritten function). The test delta is larger because Codex's F2 findings require thorough negative coverage of the command-substitution and heredoc-boundary cases; test additions are an explicitly fast-lane-allowed mutation class (`test_addition`).

`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (status `active`, `included_work_item_ids` null) covers WI-3357 by active project membership (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3357`, status active). The standing authorization's `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade` - the change edits a hook script (`source` / `hook_upgrade`) and adds tests (`test_addition`); none of the `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are performed.

## In-Root Placement Evidence

Both target paths are in-root under the canonical `E:\GT-KB` checkout: `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`. The bridge file is `bridge/gtkb-impl-start-gate-finalization-quoting-fix-007.md`. No `applications/`-tree paths are involved. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement is satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this thread flows NEW -> NO-GO -> REVISED -> NO-GO -> REVISED -> NO-GO -> REVISED -> GO -> implement -> report -> VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the predicate's intent to executed tests, including every heredoc boundary.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate is the hook that enforces this protected behavior; the fix narrows a false-negative and adds one provably-read-only exemption without weakening the gate's true-positive (chaining and executable-substitution detection) coverage.
- `GOV-RELIABILITY-FAST-LANE-001` - the governing fast-lane policy; eligibility is argued above.
- `GOV-STANDING-BACKLOG-001` - WI-3357 is a single tracked work item; this is not a bulk operation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root; no application-tree paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, the owner decision, and verification are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across WI-3357, this thread, the tests, and the implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3357 moves through open -> implementing -> verified lifecycle states.

No directly-governing functional specification exists for the gate's command classifier - the hook is its own implementation surface. The predicate's intent (exempt a simple standalone `git commit` / `git push`; reject genuine chaining and executable command substitution) is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread (VERIFIED). This proposal is a defect fix that makes the chaining detector faithful to that intent under shell quoting and heredoc semantics; the verification plan proves the false-negative removal, the preserved true-positive coverage, and the safety of the narrow HEREDOC exemption at every boundary.

## Prior Deliberations

A Deliberation Archive semantic search for "implementation-start gate git finalization command classification chaining quoted command substitution HEREDOC" returned no directly-relevant DELIB record (Codex's `-002`, `-004`, and `-006` reviews independently confirmed the targeted search returns `[]`). The prior-decision history for this surface is the bridge-thread record:

- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-006.md` (NO-GO, this thread) - Codex's review of REVISED-2. It confirmed REVISED-2 resolved the `-004` first-delimiter blocker, and NO-GO'd on F1 (the parser did not validate the opener-line tail, so a same-line redirect / separator / pipeline after the quoted delimiter would be blanked with the span) and F2 (no opener-line-tail negative tests). REVISED-3 acknowledges both findings in `## Changes Since the -006 NO-GO` and resolves them with the opener-line-tail check and the added negative tests.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-004.md` (NO-GO, this thread) - Codex's review of REVISED-1. It NO-GO'd the DOTALL `.*?` regex that could backtrack past the first delimiter line. REVISED-2 replaced it with the forward-scan parser; REVISED-3 keeps that parser and adds the opener-line-tail boundary.
- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-002.md` (NO-GO, this thread) - Codex's review of `-001`. It NO-GO'd `-001`'s blanket double-quote blanking. REVISED-1 resolved it with the two-view quote-aware scan; REVISED-2 and REVISED-3 carry that scan forward unchanged.
- `bridge/gtkb-implementation-start-gate-repository-finalization` (VERIFIED) - introduced `_is_simple_git_finalization_command()` and its control-marker check. Its `-001` proposal states the design intent verbatim: "reject the safe classification if shell chaining or control markers are present, such as `;`, `&&`, `||`, `|`, command substitution, or backtick execution." REVISED-3 preserves that intent: command substitution and backtick execution still disqualify the exemption wherever they remain executable; only provably-literal markers (chaining markers in any quote, execution markers in single quotes, and a read-only HEREDOC `cat` substitution whose every boundary is validated) are exempted.
- `bridge/gtkb-impl-start-gate-comparison-operator-fix` (VERIFIED, WI-3356) and `bridge/gtkb-impl-start-gate-format-spec-fix` (VERIFIED, WI-3317) - sibling fixes in the same file: `MUTATING_COMMAND_RE` substring/regex matching that ignored syntactic context. Same root-cause class, different construct and function.

This proposal is a distinct, fourth member of that defect family: it targets `_is_simple_git_finalization_command()` (not `MUTATING_COMMAND_RE`), and the original substring artifact is a *false-negative*. The two comparison-operator / format-spec threads are terminal (VERIFIED); there is no live coordination dependency.

## Owner Decisions / Input

WI-3357 is routed through the reliability fast-lane, so per `GOV-RELIABILITY-FAST-LANE-001` it carries no per-fix Deliberation Archive record or formal-artifact-approval packet; the owner-decision evidence is recorded here.

- **Option B threat-model decision (owner, 2026-05-17, this session).** Codex's `-002` `Owner Action` stated that exempting executable `$(` / backtick expressions inside double-quoted commit messages "is a new threat-model decision and should be presented to the owner explicitly before refiling." The owner was presented two options: Option A - ship the narrow fix only (chaining markers `;` / `|` / `&&` / `||` inside quoted messages exempted, the HEREDOC pattern stays blocked); Option B - additionally support the documented HEREDOC `$(cat <<'EOF' ... EOF)` commit pattern, accepting the threat-model tradeoff. The owner selected **Option B**. REVISED-1, REVISED-2, and this REVISED-3 implement Option B.
- **No further owner decision required for REVISED-3.** Codex's `-006` `Owner Action` states: "None. ... No additional owner decision is needed because this is implementation safety inside the already-selected Option B scope." REVISED-3's change is the opener-line-tail validation within the already-approved Option B scope.
- **Scope of what Option B authorizes.** Option B authorizes ONLY the narrowly-recognized `$(cat <<'QUOTED-DELIM' ... DELIM)` HEREDOC shape: a read-only `cat` reading a quoted-delimiter heredoc, with a whitespace-only opener-line tail and the first delimiter line immediately followed by the substitution's closing `)`. It does NOT authorize a blanket exemption of `$(` / backtick inside double quotes. Bare `$(...)` command substitution, backtick execution, and any HEREDOC substitution that would run a further command (including via an opener-line redirect, separator, or pipeline) remain disqualifying and gated. The threat-model basis is in `## Threat Model`.
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

IP-1 carries forward, unchanged, REVISED-1's two-view quote-aware marker scan and REVISED-2's first-delimiter-line search. It adds ONLY the opener-line-tail validation.

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

### IP-1b: HEREDOC recognizer - forward-scan parser with opener-line-tail validation

Replace REVISED-2's `_find_heredoc_message_substitution_spans()` with the version below. The opener regex's internal whitespace is `[ \t]` (not `\s`), so the opener is a single physical line. The parser adds the opener-line-tail check (the REVISED-3 / `-006` F1 fix) and keeps REVISED-2's first-delimiter-line search and post-delimiter `)` check.

```python
# WI-3357: opener of the documented HEREDOC commit-message pattern
#   git commit -m "$(cat <<'EOF' ... EOF)"
# This regex matches ONLY the fixed opener `$(cat <<['"]DELIM['"]` on a single
# physical line (internal whitespace is [ \t], never a newline). The opener-line
# tail, the heredoc-terminating delimiter line, and the substitution's closing
# `)` are validated by an explicit forward scan in
# _find_heredoc_message_substitution_spans().
_HEREDOC_OPENER_RE = re.compile(
    r"\$\([ \t]*cat[ \t]+<<(?P<dash>-?)[ \t]*"
    r"(?P<q>['\"])(?P<delim>[A-Za-z_][A-Za-z0-9_]*)(?P=q)"
)


def _find_heredoc_message_substitution_spans(command: str) -> list[tuple[int, int]]:
    """Return [start, end) spans of provably-safe `$(cat <<'DELIM' ... DELIM)`
    command substitutions.

    A span is recognized only when EVERY boundary is validated:
    - the opener is `$(cat <<['"]DELIM['"]` -- the only command is read-only
      `cat`, and the delimiter is quoted, so the heredoc body is literal;
    - the opener-line tail (between the quoted delimiter and the body's first
      newline) is whitespace-only -- a shell can place a redirect, separator,
      or pipeline there and it would execute;
    - the heredoc body ends at the FIRST line equal to DELIM (`^DELIM$`, or
      `^\\t*DELIM$` for the `<<-` form, which strips leading tabs) -- exactly
      where a POSIX shell terminates the heredoc;
    - that first delimiter line is followed by optional whitespace and then the
      closing `)` of the substitution.

    Any deviation fails closed: the span is NOT returned and the `$(` stays
    visible to the control-marker scan. A recognized span runs only read-only
    `cat` over a literal (quoted-delimiter) heredoc body.
    """
    spans: list[tuple[int, int]] = []
    search_from = 0
    while True:
        opener = _HEREDOC_OPENER_RE.search(command, search_from)
        if opener is None:
            break
        # The heredoc body begins on the line AFTER the opener. The opener-line
        # tail -- between the quoted delimiter and that line break -- must be
        # whitespace-only; a redirect / separator / pipeline there executes.
        body_start = command.find("\n", opener.end())
        if body_start == -1 or command[opener.end() : body_start].strip():
            search_from = opener.end()
            continue
        body_start += 1
        prefix = r"\t*" if opener.group("dash") else ""
        delim_line_re = re.compile(
            rf"^{prefix}{re.escape(opener.group('delim'))}$", re.MULTILINE
        )
        delim_line = delim_line_re.search(command, body_start)
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

- `git commit -m "fix X; tidy | done"` -> no HEREDOC; chaining-view masks the double-quoted span -> no chaining marker; execution-view has no `$(` / backtick -> exempt.
- `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` -> not a HEREDOC `cat` substitution -> not neutralized; execution-view keeps `$(` visible -> disqualified -> remains gated.
- `git commit -m "$(cat <<'EOF' ... EOF)"` (clean opener-line tail, first delimiter line then `)`) -> recognized -> neutralized -> exempt.
- `git commit -m "$(cat <<'EOF' > scripts/sample.py ... EOF)"` -> opener-line tail `> scripts/sample.py` is not whitespace -> NOT recognized -> `$(` stays visible -> remains gated.
- `git commit -m "$(cat <<'EOF' ... EOF <command> EOF)"` (a command after the first delimiter line) -> the first delimiter line is not followed by `)` -> NOT recognized -> remains gated.
- `git commit -m "x"; rm -rf y` -> the `;` is outside the quoted message -> chaining-view keeps `;` -> remains gated.
- `git push --force origin main` -> `--force` token -> denied -> not simple.

### IP-2: regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, tagged `# WI-3357`, following the existing direct-unit-test pattern (`gate._is_mutating_command(...)`) and integration-test pattern (`gate.gate_decision(payload)`):

- Direct unit tests on `gate._is_simple_git_finalization_command(...)` for every numbered case in the Specification-Derived Verification Plan below.
- Integration tests via `gate.gate_decision(payload)` (Bash tool payload, no authorization packet seeded) for every case whose `gate_decision` column is not `n/a`: exempt cases assert `gate.gate_decision(payload) == {}`; gated cases assert `result["decision"] == "block"` and `"authorization packet" in result["reason"]`.
- Direct unit tests on `gate._find_heredoc_message_substitution_spans(...)` as a pure parser, with an adversarial table: documented single heredoc (one span); unquoted delimiter (no span); non-`cat` opener (no span); early delimiter then command then later delimiter (no span); early delimiter then `;`-command (no span); opener-line redirect tail (no span); opener-line separator tail (no span); opener-line pipeline tail (no span); no delimiter line at all (no span); two independent heredocs (two spans).
- The F2 cases (18, 19, 20) and every heredoc-boundary negative are mandatory and land in this slice; no test is deferred.

All existing tests in `platform_tests/scripts/test_implementation_start_gate.py` - including `test_git_commit_finalization_command_is_allowed_without_authorization`, `test_git_push_finalization_command_is_allowed_without_authorization`, and `test_chained_git_commit_with_protected_write_still_blocks` - must continue to pass unchanged.

### IP-3: WI-3357 completion

Promote WI-3357 `open` -> `verified` via the governed CLI after Codex records VERIFIED on the post-implementation report.

## Threat Model

The finalization exemption exists to let a standalone `git commit` / `git push` skip the implementation-start gate. The gate's protective job is to stop unreviewed protected source, test, script, hook, configuration, deployment, repository-state, and KB-mutation work. REVISED-3 must not let any protected mutation run through the exemption.

**Safety invariant.** The change can only ever ADD an exemption in three provably-safe cases: (1) a chaining marker (`;`, `|`, `&&`, `||`) inside any quoted span - literal in both quote types; (2) an execution marker (`$(`, backtick) inside a single-quoted span - literal, because single quotes suppress all expansion; (3) a `$(cat <<'QUOTED-DELIM' ... DELIM)` substitution recognized by `_find_heredoc_message_substitution_spans()`. Every other marker continues to disqualify the exemption. Any quote mis-segmentation can only end a span early and expose more text to the scan (fail-closed). Any HEREDOC shape the parser does not recognize is not neutralized, so its `$(` / backtick keeps disqualifying the exemption (fail-closed).

**Complete span-boundary enumeration (the F1 fix, made exhaustive).** A `$(...)` span recognized by `_find_heredoc_message_substitution_spans()` consists ONLY of the regions below, and every region is provably non-executable. This enumeration is exhaustive: there is no region of a recognized span that is left unvalidated.

| # | Region | Why it cannot carry executable text |
|---|---|---|
| 1 | `$(` | Fixed literal token (substitution open). |
| 2 | between `$(` and `cat` | `[ \t]*` in `_HEREDOC_OPENER_RE` - whitespace only. |
| 3 | `cat` | Fixed literal token; `cat` is a read-only command. |
| 4 | between `cat` and `<<` | `[ \t]+` in `_HEREDOC_OPENER_RE` - whitespace only. |
| 5 | `<<` with optional `-` | Fixed literal heredoc operator. |
| 6 | between `<<[-]` and the delimiter quote | `[ \t]*` in `_HEREDOC_OPENER_RE` - whitespace only. |
| 7 | the quoted delimiter `'DELIM'` / `"DELIM"` | Fixed; the quoting is what makes the body literal. |
| 8 | opener-line tail (after the delimiter quote to the body newline) | Checked whitespace-only by the parser - **the REVISED-3 fix for `-006` F1**. |
| 9 | the body newline | Fixed literal line break. |
| 10 | heredoc body lines | Literal: the delimiter is quoted, so no parameter, command, or arithmetic expansion occurs. |
| 11 | the first delimiter line | The heredoc terminator (`^DELIM$`, or `^\t*DELIM$` for `<<-`); `re.search` returns the leftmost match, so it is the first. |
| 12 | after the delimiter line to `)` | Checked whitespace-only by the parser - the REVISED-2 fix for `-004` F1. |
| 13 | `)` | Fixed literal token (substitution close). |

Regions 1, 3, 5, 7, 9, 11, 13 are fixed literal tokens. Regions 2, 4, 6 are whitespace pinned by the opener regex (which uses `[ \t]`, never `\s`, so the opener cannot span lines). Regions 8 and 12 are explicitly whitespace-checked by the parser. Region 10 is literal heredoc body. Therefore the only command a recognized span runs is `cat`, reading literal text; the runtime effect of `git commit -m "$(cat <<'EOF' ... EOF)"` is exactly `git commit -m "<literal text>"`. A redirect, separator, or pipeline cannot appear in any region without failing closed: before `cat` or between `cat` and `<<` it breaks the opener regex; in the opener-line tail it fails region 8; after the delimiter line it fails region 12; inside the body it is literal text.

**Why each `-006`-class attack fails closed.** `$(cat <<'EOF' > scripts/sample.py\nmsg\nEOF\n)`: region 8 (opener-line tail) is `> scripts/sample.py`, not whitespace -> not recognized -> the `$(` stays visible -> gated. `$(cat <<'EOF'; Set-Content ...\n...)` and `$(cat <<'EOF' | tee scripts/sample.py\n...)`: region 8 is `; Set-Content ...` / `| tee ...`, not whitespace -> not recognized -> gated. Anything the parser does not recognize stays fully visible to the marker scan and is independently gated.

**Residual exposure.** The exemption permits `cat` to read inline literal text. It permits no file write, no KB mutation, no repository-state change, and no execution of message-body content or of any command before, after, or alongside the `cat` heredoc.

**Option rationale.** Codex's `-006` F1 `Recommended action` named the required design: after the opener matches, "locates the next line break and requires `command[opener.end():line_break]` to be whitespace-only. The delimiter-line search should then start after that line break. Any non-whitespace opener-line tail must fail closed." REVISED-3 implements exactly that, and tightens the opener regex to `[ \t]` so the opener is a single line. A non-HEREDOC `$(cat file)` substitution is deliberately NOT allowlisted; `git commit -F <file>` is git's native mechanism for a message read from a file and is already exempt (it contains no `$(`).

## Specification-Derived Verification Plan

De-facto specification: a standalone `git commit` / `git push` is a simple finalization command and is exempt regardless of literal punctuation inside its quoted message; the documented HEREDOC `$(cat <<'QUOTED-DELIM' ... DELIM)` message substitution is exempt only when its opener-line tail is whitespace-only and its first delimiter line is immediately followed by the closing `)`; a command that chains another command, that runs executable command substitution inside double quotes (other than the recognized HEREDOC `cat` form), or that runs any command via an opener-line redirect / separator / pipeline or after the heredoc-terminating line, is not exempt.

In the Command column, `\n` denotes a literal newline; HEREDOC commands span multiple lines, with each `DELIM` line at column 0.

| # | Test case | Command | `_is_simple...` | `gate_decision` |
|---|---|---|---|---|
| 1 | chaining markers literal in a double-quoted message | `git commit -m "fix X; tidy \| done && wrap"` | True | `{}` |
| 2 | chaining marker literal in a single-quoted message | `git commit -m 'fix X; tidy Y'` | True | n/a |
| 3 | HEREDOC message substitution, single-quoted delimiter (Option B) | `git commit -m "$(cat <<'EOF'\nmsg body\nEOF\n)"` | True | `{}` |
| 4 | HEREDOC message substitution, double-quoted delimiter (Option B) | `git commit -m "$(cat <<"EOF"\nmsg\nEOF\n)"` | True | n/a |
| 5 | command substitution running a protected write, double-quoted | `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` | False | block |
| 6 | backtick command substitution running a protected write | `` git commit -m "`Set-Content -Path scripts/sample.py -Value z`" `` | False | block |
| 7 | non-HEREDOC command substitution inside a double-quoted message | `git commit -m "$(cat msg.txt)"` | False | block |
| 8 | HEREDOC with an UNQUOTED delimiter - body would expand | `git commit -m "$(cat <<EOF\nmsg\nEOF\n)"` | False | block |
| 9 | non-`cat` command in a HEREDOC-shaped substitution | `git commit -m "$(rm scripts/sample.py <<'EOF'\nx\nEOF\n)"` | False | block |
| 10 | `$(` provably literal inside single quotes | `git commit -m '$(whoami)'` | True | n/a |
| 11 | genuine chaining via `;` after the git finalization | `git commit -m "x"; rm -rf y` | False | n/a |
| 12 | chained protected write after a punctuated double-quoted message | `git commit -m "fix; tidy"; Set-Content -Path scripts/sample.py -Value "z"` | False | block |
| 13 | chained protected write after a complete HEREDOC commit | `git commit -m "$(cat <<'EOF'\nmsg\nEOF\n)" && Set-Content -Path scripts/sample.py -Value z` | False | block |
| 14 | plain push (regression) | `git push origin develop` | True | `{}` |
| 15 | denied push flag (regression) | `git push --force origin main` | False | n/a |
| 16 | early delimiter then a protected write then a later delimiter | `git commit -m "$(cat <<'EOF'\nmsg\nEOF\nSet-Content -Path scripts/sample.py -Value z\nEOF\n)"` | False | block |
| 17 | early delimiter then a `;`-prefixed protected write then a later delimiter | `git commit -m "$(cat <<'EOF'\nmsg\nEOF\n; Set-Content -Path scripts/sample.py -Value z\nEOF\n)"` | False | block |
| 18 | opener-line output-redirection tail (F1/F2) | `git commit -m "$(cat <<'EOF' > scripts/sample.py\nmsg\nEOF\n)"` | False | block |
| 19 | opener-line command-separator tail (F1/F2) | `git commit -m "$(cat <<'EOF'; Set-Content -Path scripts/sample.py -Value z\nmsg\nEOF\n)"` | False | block |
| 20 | opener-line pipeline tail (F1/F2) | `git commit -m "$(cat <<'EOF' \| tee scripts/sample.py\nmsg\nEOF\n)"` | False | block |

Cases 18, 19, and 20 are the F2-mandated opener-line-tail negatives proving the `-006` bypass is closed; they are the redirect / separator / pipeline shapes named in Codex's `-006` F2 `Recommended action`. Cases 16 and 17 prove the first-delimiter boundary (from `-004`); cases 5 and 6 prove ordinary command substitution stays gated; cases 7, 8, 9 are HEREDOC-shape negatives. Cases 1-4 and 10 prove the false-negative removal; cases 11-13 prove preserved chaining detection; cases 14-15 are existing-behavior regressions. Direct `_find_heredoc_message_substitution_spans()` unit tests cover the parser with the adversarial table in IP-2.

Execution: `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`, plus `python -m ruff check` and `python -m ruff format --check` on both target files. The implementation report reaches VERIFIED only when every existing test plus the new WI-3357 tests pass.

## Acceptance Criteria

- IP-1 landed: the split marker constants, `_mask_quoted_spans()`, `_has_disqualifying_control_marker()`, `_HEREDOC_OPENER_RE` (with `[ \t]` internal whitespace), `_find_heredoc_message_substitution_spans()` (with the opener-line-tail check), `_neutralize_heredoc_message_substitutions()`, and the rewritten `_is_simple_git_finalization_command()`.
- `_is_simple_git_finalization_command()` returns True for verification cases 1-4, 10, and 14; False for cases 5-9, 11-13, and 15-20.
- `gate_decision()` returns `{}` for cases 1, 3, and 14; returns a `block` decision for cases 5, 6, 7, 8, 9, 12, 13, 16, 17, 18, 19, and 20.
- `_find_heredoc_message_substitution_spans()` returns the expected spans for the IP-2 adversarial parser table, including no span for each opener-line-tail shape.
- IP-2 tests added and passing; every existing test in `platform_tests/scripts/test_implementation_start_gate.py` still passes (no regression).
- Bridge applicability preflight and ADR/DCL clause preflight both pass for this bridge id.
- `ruff check` and `ruff format --check` are clean on both target files.

## Risks / Rollback

- Risk: backslash-escaped quotes inside a double-quoted message are not modeled by `_mask_quoted_spans`. The scanner never treats a `"` as escaped, so it can only end a span early relative to a true shell parse - exposing more text to the marker scan. The effect is fail-closed (a benign command may be gated, never a chaining command exempted). Unchanged from current behavior for that command shape.
- Risk: a commit message with an unbalanced quote. `shlex.split(scan_command, posix=False)` raises `ValueError`, the function returns False, and the command is gated (fail-closed, unchanged from current behavior).
- Risk: a HEREDOC the parser does not recognize (unquoted delimiter; a command other than `cat`; a non-whitespace opener-line tail; a command after the heredoc-terminating line; `cat<<` with no space; `\r\n` line endings; or a PowerShell here-string, which uses `@'...'@` rather than `<<`). It is not neutralized, so its `$(` / backtick disqualifies the exemption and the command is gated. This is fail-closed and intentional; the parser recognizes the documented bash HEREDOC commit pattern with `\n` line endings, which is how bash heredocs are themselves delimited.
- Risk: the parser's boundary semantics differ from the shell. The opener regex is single-line (`[ \t]`); the opener-line tail is the text to the next `\n`; the delimiter-line patterns (`^DELIM$` for `<<`, `^\t*DELIM$` for `<<-`) are byte-identical to where a POSIX shell terminates the heredoc; `re.search` returns the leftmost (first) match. The `## Threat Model` span-boundary enumeration shows every region of a recognized span is fixed-literal, opener-regex whitespace, explicitly whitespace-checked, or literal body.
- Rollback: revert the constant split, the marker-scan helpers, the opener regex, the parser, the neutralizer, and the rewritten function; the pre-fix `GIT_FINALIZATION_CONTROL_MARKERS` substring scan is restored by reverting one function body. The IP-2 tests document the intended behavior and may remain or be reverted with the change.

## Recommended Commit Type

`fix:` - corrects a defect in an existing predicate (the finalization exemption wrongly disqualifies standalone git commits whose message contains literal shell punctuation, and wrongly disqualifies the documented HEREDOC commit pattern). No new public API, CLI surface, or capability is added; the HEREDOC allowlist makes the existing exemption faithful to a documented commit form. Net change is roughly 75-95 lines in `scripts/implementation_start_gate.py` (split constant, two marker-scan helpers, one opener regex, one parser, one neutralizer, one rewritten function) and roughly 120-145 lines of tests in `platform_tests/scripts/test_implementation_start_gate.py`.
