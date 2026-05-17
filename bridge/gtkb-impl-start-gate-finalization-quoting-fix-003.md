REVISED

# Implementation Proposal (REVISED-1) - implementation_start_gate finalization-exemption quote-aware control-marker fix (WI-3357)

bridge_kind: implementation_proposal
Document: gtkb-impl-start-gate-finalization-quoting-fix
Version: 003
Responds to: bridge/gtkb-impl-start-gate-finalization-quoting-fix-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3357

target_paths: ["scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_start_gate.py"]

This REVISED-1 proposal responds to the `-002` NO-GO. It keeps the confirmed defect fix - literal punctuation inside a quoted commit message wrongly disqualifies the git-finalization exemption - but replaces the `-001` quote-stripping design, which Codex correctly found would also exempt executable command substitution (`$(...)`, backtick) inside double quotes, a security regression. The new design is quote-semantics-aware: it suppresses chaining markers inside any quote, keeps execution markers disqualifying wherever they still execute, and supports the documented HEREDOC commit pattern through a narrow, explicitly-recognized, read-only allowlist rather than a blanket double-quote exemption.

## Changes Since the -002 NO-GO

The `-002` NO-GO raised two P1 findings. Both are addressed; the prior NO-GO is explicitly acknowledged here per the deliberation protocol and the REVISED workflow.

- **F1 - command substitution inside double quotes cannot be treated as benign.** The `-001` helper `_strip_quoted_spans()` blanked the interior of *both* single- and double-quoted spans uniformly, so `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` would have been classified as a simple finalization command (Codex's read-only simulation confirmed `proposed_simple: True`). REVISED-1 removes that helper. The new scan distinguishes two marker classes by shell quoting semantics: chaining markers (`;`, `|`, `&&`, `||`) are literal inside either quote type and are suppressed accordingly; execution markers (`$(`, backtick) still execute inside double quotes and are suppressed only inside single quotes. `$(` / backtick inside double quotes (or unquoted) continue to disqualify the exemption exactly as today - the `$(Set-Content ...)` shape Codex flagged still returns `_is_simple_git_finalization_command` False and a block decision.
- **F2 - the verification plan lacks a command-substitution-bypass test.** The REVISED Specification-Derived Verification Plan adds negative regression tests proving `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` and the backtick equivalent are NOT simple finalization commands and do NOT return `{}` from `gate_decision()`, plus paired tests proving the narrow HEREDOC pattern is accepted while non-`cat`, unquoted-delimiter, and non-HEREDOC command substitutions remain blocked.

The `-001` `Design Decision: control markers inside quoted spans are benign` section - the exact stance Codex NO-GO'd - is removed and replaced by the `## Threat Model` section below, which argues only the narrow HEREDOC `cat` allowlist.

Per the owner's Option B decision (see `## Owner Decisions / Input`), the documented HEREDOC commit pattern `git commit -m "$(cat <<'EOF' ... EOF)"` is supported. Codex's F1 `Recommended action` explicitly contemplated this path: "if the HEREDOC message-generation pattern must be supported, handle it as an explicit, tightly tested exception rather than by blanking all double-quoted command substitutions." REVISED-1 implements exactly that explicit, tightly-tested exception.

## Claim

In `scripts/implementation_start_gate.py`, the first line of `_is_simple_git_finalization_command()` is `any(marker in command for marker in GIT_FINALIZATION_CONTROL_MARKERS)` - a raw substring scan of the entire command string, including the quoted `-m "<message>"` value, for the markers `;`, `&&`, `||`, `|`, `$(`, and backtick. The check intends to reject genuine command chaining, but a raw substring scan cannot distinguish a marker that is a shell operator (outside quotes) from a marker that is literal message text (inside quotes). A legitimate `git commit -m "fix X; tidy Y"` is therefore misclassified as chained, loses the finalization exemption, matches `MUTATING_COMMAND_RE` as `git commit` with no resolvable target path, and is hard-blocked at `<unknown-mutating-target>`.

The fix makes the marker check quote-semantics-aware. A chaining marker (`;`, `|`, `&&`, `||`) counts only when it appears outside every quoted span - those characters are literal inside both single and double quotes. An execution marker (`$(`, backtick) counts when it appears outside single quotes - including inside double quotes, where command substitution still executes. A documented HEREDOC message substitution (`$(cat <<'EOF' ... EOF)`) is recognized by an explicit narrow allowlist and neutralized before the scan, because it is provably read-only literal-text generation. Genuine chaining (`git commit -m x; rm -rf y`) keeps its `;` outside the quoted message and remains caught; an executable substitution inside double quotes (`git commit -m "$(Set-Content ...)"`) keeps disqualifying the exemption; ordinary punctuated messages and the documented HEREDOC commit pattern pass.

Observed 2026-05-17: routine commits whose message contains a semicolon or pipe, and the `git commit -m "$(cat <<'EOF' ... EOF)"` HEREDOC pattern, are blocked by this PreToolUse gate. The current workaround is to hand-rewrite commit messages to avoid punctuation; this fix removes the need for that workaround while preserving the gate's true-positive coverage.

## Reliability Fast-Lane Eligibility

This work item is routed via the reliability fast-lane per `GOV-RELIABILITY-FAST-LANE-001`. The eligibility criteria hold:

1. `origin` is `defect` (WI-3357, verified in MemBase) - never `new`.
2. No new public API or CLI surface. The change narrows a false-negative in an existing predicate and, per the owner's Option B decision, makes that same predicate correctly recognize one documented commit-message form (the HEREDOC `cat` substitution) that `-001` already itemized as a wrongly-blocked legitimate case. Both are corrections to the finalization exemption's faithfulness to commit-message reality, not a new feature surface; the exemption's true-positive coverage (rejecting genuine chaining and executable substitution) is preserved and regression-tested.
3. No new or revised requirement or specification. The predicate's intent is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread. The owner's Option B threat-model decision is captured as proposal evidence in `## Owner Decisions / Input`; per the fast-lane it is recorded there rather than as a separate Deliberation Archive record or formal-artifact-approval packet.
4. Single-concern: one predicate, one defect family, two files. The implementation delta is modest (a split constant, one recognizer regex, three small helpers, one rewritten function). The test delta is larger because Codex's F2 finding requires thorough negative coverage of the command-substitution boundary; test additions are an explicitly fast-lane-allowed mutation class (`test_addition`).

`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (status `active`, `included_work_item_ids` null) covers WI-3357 by active project membership (`PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3357`, status active). The standing authorization's `allowed_mutation_classes` are `source`, `test_addition`, and `hook_upgrade` - the change edits a hook script (`source` / `hook_upgrade`) and adds tests (`test_addition`); none of the `forbidden_operations` (`deploy`, `git_push_force`, `spec_deletion`) are performed.

## In-Root Placement Evidence

Both target paths are in-root under the canonical `E:\GT-KB` checkout: `scripts/implementation_start_gate.py` and `platform_tests/scripts/test_implementation_start_gate.py`. The bridge file is `bridge/gtkb-impl-start-gate-finalization-quoting-fix-003.md`. No `applications/`-tree paths are involved. `ADR-ISOLATION-APPLICATION-PLACEMENT-001` in-root placement is satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this thread flows NEW -> NO-GO -> REVISED -> GO -> implement -> report -> VERIFIED.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Specification-Derived Verification Plan maps the predicate's intent to executed tests.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the implementation-start gate is the hook that enforces this protected behavior; the fix narrows a false-negative and adds one provably-read-only exemption without weakening the gate's true-positive (chaining and executable-substitution detection) coverage.
- `GOV-RELIABILITY-FAST-LANE-001` - the governing fast-lane policy; eligibility is argued above.
- `GOV-STANDING-BACKLOG-001` - WI-3357 is a single tracked work item; this is not a bulk operation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root; no application-tree paths.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect, the owner decision, and verification are preserved as durable bridge and MemBase artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved across WI-3357, this thread, the tests, and the implementation report.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3357 moves through open -> implementing -> verified lifecycle states.

No directly-governing functional specification exists for the gate's command classifier - the hook is its own implementation surface. The predicate's intent (exempt a simple standalone `git commit` / `git push`; reject genuine chaining and executable command substitution) is the de-facto specification, established by the `gtkb-implementation-start-gate-repository-finalization` thread (VERIFIED). This proposal is a defect fix that makes the chaining detector faithful to that intent under shell quoting semantics; the verification plan proves the false-negative removal, the preserved true-positive coverage, and the safety of the narrow HEREDOC exemption.

## Prior Deliberations

A Deliberation Archive semantic search for "implementation-start gate git finalization command classification chaining quoted command substitution" returned no directly-relevant DELIB record (Codex's `-002` review independently confirmed the targeted search returns `[]`). The prior-decision history for this surface is the bridge-thread record:

- `bridge/gtkb-impl-start-gate-finalization-quoting-fix-002.md` (NO-GO, this thread) - Codex's review of `-001`. It confirmed the underlying semicolon/pipe defect is real, and NO-GO'd `-001` on F1 (the `_strip_quoted_spans()` helper would exempt executable `$(...)` / backtick inside double quotes) and F2 (no negative test for the command-substitution bypass). REVISED-1 acknowledges both findings in `## Changes Since the -002 NO-GO` and resolves them as described there.
- `bridge/gtkb-implementation-start-gate-repository-finalization` (VERIFIED) - introduced `_is_simple_git_finalization_command()` and its control-marker check. Its `-001` proposal states the design intent verbatim: "reject the safe classification if shell chaining or control markers are present, such as `;`, `&&`, `||`, `|`, command substitution, or backtick execution." REVISED-1 preserves that intent: command substitution and backtick execution still disqualify the exemption wherever they remain executable; only provably-literal markers (chaining markers in any quote, execution markers in single quotes, and the read-only HEREDOC `cat` allowlist) are exempted.
- `bridge/gtkb-impl-start-gate-comparison-operator-fix` (VERIFIED, WI-3356) - a sibling fix in the same file: `MUTATING_COMMAND_RE` naive `>`-substring matching misclassified Python `>=` / `>>=`. Same root-cause class (substring matching that ignores syntactic context), different construct and function.
- `bridge/gtkb-impl-start-gate-format-spec-fix` (VERIFIED, WI-3317) - a sibling fix in the same file: `MUTATING_COMMAND_RE` misclassified Python format-spec `:>` alignment. Same root-cause class, different construct and function.

This proposal is a distinct, fourth member of that defect family: it targets `_is_simple_git_finalization_command()` (not `MUTATING_COMMAND_RE`), and the substring artifact is a *false-negative* (an exemption wrongly withheld), not a false-positive. The two comparison-operator / format-spec threads are terminal (VERIFIED); there is no live coordination dependency.

## Owner Decisions / Input

WI-3357 is routed through the reliability fast-lane, so per `GOV-RELIABILITY-FAST-LANE-001` it carries no per-fix Deliberation Archive record or formal-artifact-approval packet; the owner-decision evidence is recorded here.

- **Option B threat-model decision (owner, 2026-05-17, this session).** Codex's `-002` `Owner Action` stated: "If Prime Builder wants executable `$(` / backtick expressions inside double-quoted commit messages to be exempt, that is a new threat-model decision and should be presented to the owner explicitly before refiling." The owner was presented two options: Option A - ship the narrow fix only (chaining markers `;` / `|` / `&&` / `||` inside quoted messages exempted, the HEREDOC pattern stays blocked); Option B - additionally support the documented HEREDOC `$(cat <<'EOF' ... EOF)` commit pattern, accepting the threat-model tradeoff. The owner selected **Option B**. This REVISED-1 implements Option B.
- **Scope of what Option B authorizes.** Option B authorizes ONLY the narrowly-recognized `$(cat <<'QUOTED-DELIM' ... DELIM)` HEREDOC shape: a read-only `cat` reading a quoted-delimiter heredoc. It does NOT authorize a blanket exemption of `$(` / backtick inside double quotes. Bare `$(...)` command substitution and backtick execution inside double quotes (or unquoted) remain disqualifying and gated, preserving Codex's F1 core requirement. The threat-model basis is in `## Threat Model`.
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

### IP-1: quote-semantics-aware control-marker check plus narrow HEREDOC allowlist

In `scripts/implementation_start_gate.py`:

(a) Split the marker constant into two classes by shell quoting semantics, retaining the combined name for compatibility:

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

(b) Add a recognizer regex for the documented HEREDOC commit-message substitution, beside the other module-level `_RE` constants:

```python
# WI-3357: recognizer for the documented HEREDOC commit-message pattern
#   git commit -m "$(cat <<'EOF' ... EOF)"
# The delimiter MUST be quoted ('EOF' or "EOF") so the heredoc body is a
# literal string -- no parameter, command, or arithmetic expansion -- and the
# only command inside the substitution is read-only `cat`. The closing `)` must
# follow the delimiter line, so nothing else can run inside the $(...).
_HEREDOC_MESSAGE_SUBSTITUTION_RE = re.compile(
    r"\$\(\s*cat\s+<<-?\s*"
    r"(?P<q>['\"])(?P<delim>[A-Za-z_][A-Za-z0-9_]*)(?P=q)"
    r".*?"
    r"^[ \t]*(?P=delim)[ \t]*$"
    r"\s*\)",
    re.DOTALL | re.MULTILINE,
)
```

(c) Add three helpers and rewrite the predicate:

```python
def _neutralize_heredoc_message_substitutions(command: str) -> str:
    """Blank each recognized safe `$(cat <<'DELIM' ... DELIM)` substitution.

    The recognized span is a command substitution whose only command is a
    read-only `cat` reading a quoted-delimiter heredoc. The quoted delimiter
    makes the heredoc body a literal string (no expansion, no nested
    substitution), so the span is provably side-effect-free and is removed
    before the control-marker scan. Text that does not match this exact shape
    is left intact and stays subject to the full scan (fail-closed).
    """
    return _HEREDOC_MESSAGE_SUBSTITUTION_RE.sub(lambda m: " " * len(m.group(0)), command)


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

The `git push` denied-flag check, the `git` plus subcommand check, and `_clean_shell_token` are otherwise unchanged. Tokenization runs on `scan_command` (the HEREDOC-neutralized command) rather than the raw command: the safety-relevant tokens (`git`, the subcommand, and `--force` / `-f` / `--force-with-lease`) are always unquoted and outside any `$(...)`, so neutralization never touches them, while tokenizing the neutralized command removes the `shlex.split` `ValueError` exposure that a multi-line heredoc body with an odd quote count would otherwise create.

Behavior summary:

- `git commit -m "fix X; tidy | done"` -> no HEREDOC; chaining-view masks the double-quoted span -> no chaining marker; execution-view has no `$(` / backtick -> simple finalization -> exempt.
- `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` -> not a HEREDOC `cat` substitution -> not neutralized; execution-view (single-quote masking only) keeps `$(` visible -> disqualified -> not simple -> falls through to the mutating-command path and remains gated.
- `git commit -m "$(cat <<'EOF' ... EOF)"` -> recognized HEREDOC `cat` substitution -> neutralized to spaces -> no surviving marker -> simple finalization -> exempt.
- `git commit -m "x"; rm -rf y` -> the `;` is outside the quoted message -> chaining-view keeps `;` -> disqualified -> remains gated.
- `git push --force origin main` -> `--force` token -> denied -> not simple.
- `git push origin develop` -> unchanged -> exempt.

### IP-2: regression tests

In `platform_tests/scripts/test_implementation_start_gate.py`, tagged `# WI-3357`, following the existing direct-unit-test pattern (`gate._is_mutating_command(...)`) and integration-test pattern (`gate.gate_decision(payload)`):

- Direct unit tests on `gate._is_simple_git_finalization_command(...)` for every numbered case in the Specification-Derived Verification Plan below.
- Integration tests via `gate.gate_decision(payload)` (Bash tool payload, no authorization packet seeded) for every case whose `gate_decision` column is not `n/a`: exempt cases assert `gate.gate_decision(payload) == {}`; gated cases assert `result["decision"] == "block"` and `"authorization packet" in result["reason"]`.
- The F2 negative cases (5, 6) and the HEREDOC-boundary negatives (7, 8, 9) are mandatory and land in this slice; no test is deferred.

All existing tests in the file - including `test_git_commit_finalization_command_is_allowed_without_authorization`, `test_git_push_finalization_command_is_allowed_without_authorization`, and `test_chained_git_commit_with_protected_write_still_blocks` - must continue to pass unchanged.

### IP-3: WI-3357 completion

Promote WI-3357 `open` -> `verified` via the governed CLI after Codex records VERIFIED on the post-implementation report.

## Threat Model

The finalization exemption exists to let a standalone `git commit` / `git push` skip the implementation-start gate. The gate's protective job is to stop unreviewed protected source, test, script, hook, configuration, deployment, repository-state, and KB-mutation work. REVISED-1 must not let any protected mutation run through the exemption.

**Safety invariant.** The change can only ever ADD an exemption in three provably-safe cases: (1) a chaining marker (`;`, `|`, `&&`, `||`) the scan determines is inside any quoted span - literal in both single and double quotes per shell semantics; (2) an execution marker (`$(`, backtick) the scan determines is inside a single-quoted span - literal, because single quotes suppress all expansion; (3) a `$(cat <<'QUOTED-DELIM' ... DELIM)` HEREDOC substitution recognized by `_HEREDOC_MESSAGE_SUBSTITUTION_RE`. Every other marker - every unquoted marker, and every `$(` / backtick that is unquoted or inside a double-quoted span and not part of a recognized HEREDOC - continues to disqualify the exemption exactly as before. Any quote mis-segmentation can only end a span early and expose more text to the scan (fail-closed: a real chaining command gets gated), never hide a structural operator. Any HEREDOC variant the recognizer does not match is not neutralized, so its `$(` / backtick keeps disqualifying the exemption (fail-closed). Therefore the change cannot cause a command that should be gated to be exempted, except through case (3), whose safety is argued next.

**Why the HEREDOC `cat` allowlist is safe.** `_HEREDOC_MESSAGE_SUBSTITUTION_RE` matches a `$(...)` span only when ALL of the following hold:

1. The only command inside the substitution is `cat` - a read-only command. The regex anchors `cat` immediately after `$(` (`\$\(\s*cat\s+`); any other command, or any command before `cat`, fails the match.
2. `cat` reads a heredoc whose delimiter is quoted (`<<'EOF'` or `<<"EOF"`). A quoted heredoc delimiter makes the heredoc body a literal string - bash performs no parameter expansion, no command substitution, and no arithmetic expansion on it. An attacker therefore cannot smuggle `$(rm ...)` or a backtick inside the body, because the body never executes. The regex requires the quoted delimiter (`(?P<q>['\"]) ... (?P=q)`); an unquoted `<<EOF` does not match and is not neutralized.
3. The substitution ends immediately after the heredoc: the closing `)` must follow the delimiter line (`^[ \t]*(?P=delim)[ \t]*$\s*\)`). There is no room for a chained command, a second statement, or a redirect inside the `$(...)`.

A span matching all three is, by construction, `$(cat <<quoted-delim literal-text quoted-delim)` - it runs only `cat` and emits literal text. The runtime effect of `git commit -m "$(cat <<'EOF' ... EOF)"` is exactly `git commit -m "<literal text>"`: a git commit, with no protected mutation. Neutralizing the span before the scan is therefore correct, and anything the recognizer does not match stays fully visible to the scan and is independently gated - so even an input that mixes a valid HEREDOC with trailing chaining (`$(cat <<'EOF' ... EOF) ; rm -rf x`) fails closed, because the trailing `; rm -rf x` survives neutralization and the chaining-view flags the `;`.

**Residual exposure.** The exemption permits `cat` to read inline literal text. It permits no file write, no KB mutation, no repository-state change, and no execution of message-body content. This is strictly narrower than the `-001` design Codex NO-GO'd, which would have exempted any `$(...)` inside double quotes including `$(Set-Content ...)`.

**Option rationale.** Three designs were considered. (a) `-001`'s blanket blanking of all quoted spans - rejected: it exempts executable `$(...)` inside double quotes (Codex F1). (b) A strict rule that exempts `$(` / backtick only inside single quotes and never otherwise - rejected: it re-blocks the documented HEREDOC commit pattern, which places `$(` inside double quotes, contradicting the owner's Option B decision. (c) The narrow HEREDOC `cat` allowlist plus the two-view quote-aware scan - selected: it satisfies F1 (executable `$(` / backtick inside double quotes still disqualify) and Option B (the documented HEREDOC pattern is supported) simultaneously, and it is the "explicit, tightly tested exception" Codex's F1 `Recommended action` named. A non-HEREDOC `$(cat file)` substitution is deliberately NOT allowlisted; `git commit -F <file>` is git's native mechanism for a message read from a file and is already exempt (it contains no `$(`).

## Specification-Derived Verification Plan

De-facto specification: a standalone `git commit` / `git push` is a simple finalization command and is exempt regardless of literal punctuation inside its quoted message; the documented HEREDOC `$(cat <<'QUOTED-DELIM' ... DELIM)` message substitution is exempt; a command that chains another command, or that runs executable command substitution inside double quotes (other than the recognized HEREDOC `cat` form), is not exempt.

In the Command column, `\n` denotes a literal newline; HEREDOC commands span multiple lines.

| # | Test case | Command | `_is_simple...` | `gate_decision` |
|---|---|---|---|---|
| 1 | chaining markers literal in a double-quoted message | `git commit -m "fix X; tidy \| done && wrap"` | True | `{}` |
| 2 | chaining marker literal in a single-quoted message | `git commit -m 'fix X; tidy Y'` | True | n/a |
| 3 | HEREDOC message substitution, single-quoted delimiter (Option B) | `git commit -m "$(cat <<'EOF'\n msg body \nEOF\n)"` | True | `{}` |
| 4 | HEREDOC message substitution, double-quoted delimiter (Option B) | `git commit -m "$(cat <<"EOF"\n msg \nEOF\n)"` | True | n/a |
| 5 | command substitution running a protected write, double-quoted (F1/F2) | `git commit -m "$(Set-Content -Path scripts/sample.py -Value z)"` | False | block |
| 6 | backtick command substitution running a protected write (F1/F2) | `` git commit -m "`Set-Content -Path scripts/sample.py -Value z`" `` | False | block |
| 7 | non-HEREDOC command substitution inside a double-quoted message (F1) | `git commit -m "$(cat msg.txt)"` | False | block |
| 8 | HEREDOC with an UNQUOTED delimiter - body would expand (F1) | `git commit -m "$(cat <<EOF\n msg \nEOF\n)"` | False | block |
| 9 | non-`cat` command in a HEREDOC-shaped substitution (F1) | `git commit -m "$(rm scripts/sample.py <<'EOF'\n x \nEOF\n)"` | False | block |
| 10 | `$(` provably literal inside single quotes | `git commit -m '$(whoami)'` | True | n/a |
| 11 | genuine chaining via `;` after the git finalization | `git commit -m "x"; rm -rf y` | False | n/a |
| 12 | chained protected write after a punctuated double-quoted message | `git commit -m "fix; tidy"; Set-Content -Path scripts/sample.py -Value "z"` | False | block |
| 13 | chained protected write after a HEREDOC commit | `git commit -m "$(cat <<'EOF'\n msg \nEOF\n)" && Set-Content -Path scripts/sample.py -Value z` | False | block |
| 14 | plain push (regression) | `git push origin develop` | True | `{}` |
| 15 | denied push flag (regression) | `git push --force origin main` | False | n/a |

Cases 5 and 6 are the F2-mandated negatives proving the command-substitution bypass is closed. Cases 7, 8, and 9 are the paired HEREDOC-boundary negatives proving the allowlist matches only the `cat` + quoted-delimiter shape. Cases 1-4 and 10 prove the false-negative removal; cases 11-13 prove preserved chaining detection; cases 14-15 are existing-behavior regressions.

Execution: `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`, plus `python -m ruff check` and `python -m ruff format --check` on both target files. The implementation report reaches VERIFIED only when every existing test plus the new WI-3357 tests pass.

## Acceptance Criteria

- IP-1 landed: the split marker constants, `_HEREDOC_MESSAGE_SUBSTITUTION_RE`, `_neutralize_heredoc_message_substitutions()`, `_mask_quoted_spans()`, `_has_disqualifying_control_marker()`, and the rewritten `_is_simple_git_finalization_command()`.
- `_is_simple_git_finalization_command()` returns True for verification cases 1-4, 10, and 14; False for cases 5-9, 11, 12, 13, and 15.
- `gate_decision()` returns `{}` for cases 1, 3, and 14; returns a `block` decision for cases 5, 6, 7, 8, 9, 12, and 13.
- IP-2 tests added and passing; every existing test in `platform_tests/scripts/test_implementation_start_gate.py` still passes (no regression).
- Bridge applicability preflight and ADR/DCL clause preflight both pass for this bridge id.
- `ruff check` and `ruff format --check` are clean on both target files.

## Risks / Rollback

- Risk: backslash-escaped quotes inside a double-quoted message (`git commit -m "say \"hi\""`) are not modeled by `_mask_quoted_spans`. The scanner never treats a `"` as escaped, so it can only end a span early relative to a true shell parse - exposing more text to the marker scan. The effect is fail-closed (a benign command may be gated, never a chaining command exempted). Net effect for that command shape is unchanged from current behavior.
- Risk: a commit message with an unbalanced quote (`git commit -m "it's wip`). `shlex.split(scan_command, posix=False)` raises `ValueError`, the function returns False, and the command is gated (fail-closed, unchanged from current behavior).
- Risk: a HEREDOC variant the recognizer does not match (unquoted delimiter, a command other than `cat`, unusual whitespace, or a PowerShell here-string, which uses `@'...'@` rather than `<<`). It is not neutralized, so its `$(` / backtick disqualifies the exemption and the command is gated. This is fail-closed and intentional; the recognizer matches the documented bash HEREDOC commit pattern.
- Risk: the recognizer matches a shorter span than a hypothetical "real" heredoc parse. The matched span is still a provably read-only `cat` heredoc, and any leftover text is independently scanned, so markers in the leftover still flag the command (fail-closed).
- Rollback: revert the constant split, the regex, the three helpers, and the rewritten function; the pre-fix `GIT_FINALIZATION_CONTROL_MARKERS` substring scan is restored by reverting one function body. The IP-2 tests document the intended behavior and may remain or be reverted with the change.

## Recommended Commit Type

`fix:` - corrects a defect in an existing predicate (the finalization exemption wrongly disqualifies standalone git commits whose message contains literal shell punctuation, and wrongly disqualifies the documented HEREDOC commit pattern). No new public API, CLI surface, or capability is added; the HEREDOC allowlist makes the existing exemption faithful to a documented commit form. Net change is roughly 60-80 lines in `scripts/implementation_start_gate.py` (split constant, one recognizer regex, three helpers, one rewritten function) and roughly 90-110 lines of tests in `platform_tests/scripts/test_implementation_start_gate.py`.
