#!/usr/bin/env python3
"""Hard gate protected implementation mutations unless a bridge GO packet exists."""

from __future__ import annotations

import ast
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.implementation_authorization import (
        AuthorizationError,
        canonical_project_root,
        normalize_relative_path,
        validate_targets,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import (
        AuthorizationError,
        canonical_project_root,
        normalize_relative_path,
        validate_targets,
    )


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROTECTED_EXACT = {
    ".claude/settings.json",
    ".codex/hooks.json",
    "pyproject.toml",
    "groundtruth.toml",
}
PROTECTED_PREFIXES = (
    "scripts/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "platform_tests/",
    "tests/",
    ".claude/hooks/",
    ".claude/rules/",
    ".codex/gtkb-hooks/",
    "config/",
    ".github/",
)
ALLOWED_WRITE_PREFIXES = (
    "bridge/",
    "independent-progress-assessments/",
)
SAFE_COMMAND_PREFIXES = (
    "rg ",
    "git status",
    "git diff",
    "git show",
    "git log",
    "get-content",
    "select-string",
    "get-childitem",
    "python -m pytest",
    "python -m groundtruth_kb deliberations search",
    "python -m ruff check",
    "python -m ruff format --check",
    "python scripts/bridge_applicability_preflight.py",
    "python scripts/adr_dcl_clause_preflight.py",
)
GIT_FINALIZATION_SUBCOMMANDS = {"commit", "push"}
# Markers that disqualify the simple git-finalization exemption, split by
# shell quoting semantics so the scan can be quote-aware (WI-3357):
#   - chaining markers are literal inside EITHER quote type;
#   - execution markers still run inside double quotes (literal only inside
#     single quotes).
GIT_FINALIZATION_CHAINING_MARKERS = (";", "&&", "||", "|")
GIT_FINALIZATION_EXECUTION_MARKERS = ("$(", "`")
GIT_FINALIZATION_CONTROL_MARKERS = GIT_FINALIZATION_CHAINING_MARKERS + GIT_FINALIZATION_EXECUTION_MARKERS
GIT_FINALIZATION_DENIED_FLAGS = {"-f", "--force", "--force-with-lease"}
MUTATING_COMMAND_RE = re.compile(
    r"\b("
    r"set-content|out-file|new-item|remove-item|move-item|copy-item|"
    r"apply_patch|git\s+(?:commit|reset|checkout|merge|rebase|tag|push)|"
    r"python\s+.*(?:write_text|open\(.+,\s*['\"]w|sqlite3|insert_|update_|delete_)"
    r")\b",
    re.IGNORECASE,
)
# A shell redirection operator token: `>` / `>>`, or the combined-stream
# `&>` / `&>>` form. Matched against standalone tokens produced by a
# punctuation-aware shlex scan (see _shell_redirect_present), never against
# raw command text -- so a `>` inside a quoted argument or an embedded Python
# expression is not misread as a redirect. A leading file-descriptor digit
# (`2>`) tokenizes separately and is not part of the operator token.
REDIRECT_OPERATOR_TOKEN_RE = re.compile(r"&?>{1,2}")
NULL_SINK_REDIRECT_STRIP_RE = re.compile(
    r"\s*(?:\d+|&)?>{1,2}(?!&)\s*(?:/dev/null|\$null|NUL)\b",
    re.IGNORECASE,
)
SAFE_SQLITE_READ_RE = re.compile(
    r"sqlite3\b.*?\.execute\(\s*['\"](?:SELECT|WITH|EXPLAIN)\b",
    re.IGNORECASE | re.DOTALL,
)
SQLITE_WRITE_DISQUALIFIERS_RE = re.compile(
    r"\.executescript\(|\.executemany\(|\.commit\(|"
    r"\b(?:INSERT|UPDATE|DELETE|REPLACE|CREATE|DROP|ALTER|TRUNCATE|PRAGMA)\b",
    re.IGNORECASE,
)
BLOCKING_CLAUSE_ID = "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001"
PATH_TOKEN_RE = re.compile(
    r"(?P<path>(?:\.?/?(?:scripts|groundtruth-kb/src|groundtruth-kb/tests|platform_tests|tests|config|\.claude/hooks|\.codex/gtkb-hooks|\.github|bridge|independent-progress-assessments|memory)/[^\s'\";]+|\.claude/settings\.json|\.codex/hooks\.json|pyproject\.toml|groundtruth\.toml))"
)
PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$", re.MULTILINE)
POWERSHELL_ENV_ASSIGNMENT_RE = re.compile(
    r"""^(?:\$env:[a-z_][\w_]*\s*=\s*(?:'[^']*'|"[^""]*"|[^\s;]+)\s*;\s*)+""",
    re.IGNORECASE,
)
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


def _project_root(payload: dict[str, Any]) -> Path:
    explicit = payload.get("project_root")
    if isinstance(explicit, str) and explicit.strip():
        return Path(explicit).resolve()
    cwd = payload.get("cwd")
    cwd_path = Path(cwd).resolve() if isinstance(cwd, str) and cwd.strip() else PROJECT_ROOT
    return canonical_project_root(cwd_path)


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "tool", "name"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def _tool_input(payload: dict[str, Any]) -> Any:
    for key in ("tool_input", "input", "parameters"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            return value
    return payload


def _normalize(root: Path, path_text: str) -> str | None:
    cleaned = path_text.strip().strip("'\"`").replace("\\", "/")
    if not cleaned:
        return None
    try:
        return normalize_relative_path(root, cleaned)
    except AuthorizationError:
        return cleaned


def is_protected_path(relative_path: str) -> bool:
    rel = relative_path.replace("\\", "/").lstrip("./")
    if rel in PROTECTED_EXACT:
        return True
    if rel.startswith(ALLOWED_WRITE_PREFIXES):
        return False
    return any(rel.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def _protected_path_classification(relative_path: str) -> str:
    rel = relative_path.replace("\\", "/").lstrip("./")
    if rel == "<unknown-mutating-target>":
        return rel
    if rel in PROTECTED_EXACT:
        return rel
    for prefix in PROTECTED_PREFIXES:
        if rel.startswith(prefix):
            return prefix
    return rel


def _paths_from_apply_patch(root: Path, text: str) -> list[str]:
    normalized = (text or "").replace("`r`n", "\n").replace("`n", "\n").replace("\\r\\n", "\n").replace("\\n", "\n")
    paths = PATCH_PATH_RE.findall(normalized)
    paths.extend(PATCH_MOVE_RE.findall(normalized))
    return [rel for raw in paths if (rel := _normalize(root, raw))]


def _extract_git_rm(tokens: list[str]) -> list[str]:
    return [t for t in tokens[2:] if not t.startswith("-")]


def _extract_git_restore(tokens: list[str]) -> list[str]:
    args = tokens[2:]
    if "--staged" not in args:
        return []
    sep_idx = args.index("--staged")
    return [t for t in args[sep_idx + 1 :] if not t.startswith("-")]


def _extract_git_add(tokens: list[str]) -> list[str]:
    flags_no_paths = {"-A", "--all", "-u", "--update", "-p", "--patch", "-n", "--dry-run"}
    return [t for t in tokens[2:] if not t.startswith("-") and t not in flags_no_paths]


def _extract_git_mv(tokens: list[str]) -> list[str]:
    return [t for t in tokens[2:] if not t.startswith("-")]


def _extract_git_checkout(tokens: list[str]) -> list[str]:
    args = tokens[2:]
    if "--" in args:
        idx = args.index("--")
        return [t for t in args[idx + 1 :] if not t.startswith("-")]
    path_shaped = [t for t in args if "/" in t or "\\" in t]
    if path_shaped:
        return [t for t in args if not t.startswith("-")]
    return []


def _extract_git_reset(tokens: list[str]) -> list[str]:
    args = tokens[2:]
    if any(f in args for f in ("--hard", "--mixed", "--soft", "--keep", "--merge")):
        return []
    return [t for t in args if not t.startswith("-")]


def _extract_none(tokens: list[str]) -> list[str]:
    return []


def _extract_powershell_path_arg(tokens: list[str]) -> list[str]:
    """First positional arg OR -Path/-FilePath/-LiteralPath flag value.

    Once any of those sources supplies a path, subsequent non-flag tokens are
    not treated as positional paths -- they are values of other named flags
    like -Value, -Force, -Confirm, etc.
    """
    paths: list[str] = []
    path_captured = False
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t.lower() in ("-path", "-filepath", "-literalpath"):
            if i + 1 < len(tokens):
                paths.append(tokens[i + 1])
                path_captured = True
                i += 2
                continue
        elif t.startswith("-"):
            # Skip the named flag's value (PowerShell convention: flag + value)
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                i += 2
                continue
        elif not path_captured:
            paths.append(t)
            path_captured = True
        i += 1
    return paths


def _extract_powershell_both_paths(tokens: list[str]) -> list[str]:
    flag_paths: list[str] = []
    positional: list[str] = []
    i = 1
    while i < len(tokens):
        t = tokens[i]
        if t.lower() in ("-path", "-literalpath", "-destination"):
            if i + 1 < len(tokens):
                flag_paths.append(tokens[i + 1])
                i += 2
                continue
        elif not t.startswith("-") and len(positional) < 2:
            positional.append(t)
        i += 1
    return flag_paths + positional


_GIT_NON_MUTATING_SUBCOMMANDS = frozenset(
    {
        "commit",
        "merge",
        "rebase",
        "tag",
        "push",
        "log",
        "diff",
        "status",
        "show",
        "branch",
        "fetch",
        "pull",
        "remote",
        "stash",
        "config",
        "describe",
        "rev-parse",
        "rev-list",
        "ls-files",
        "ls-tree",
        "ls-remote",
        "blame",
        "bisect",
        "cherry",
        "reflog",
        "shortlog",
        "submodule",
        "worktree",
        "notes",
        "clean",
    }
)

_GIT_MUTATING_EXTRACTORS = {
    "rm": _extract_git_rm,
    "restore": _extract_git_restore,
    "add": _extract_git_add,
    "mv": _extract_git_mv,
    "checkout": _extract_git_checkout,
    "reset": _extract_git_reset,
}

_POWERSHELL_PATH_ARG_VERBS = frozenset(
    {
        "set-content",
        "out-file",
        "new-item",
        "remove-item",
        "add-content",
        "clear-content",
    }
)

_POWERSHELL_BOTH_PATHS_VERBS = frozenset(
    {
        "move-item",
        "copy-item",
        "rename-item",
    }
)


MUTATING_VERB_TABLE = {
    "git_mutating": tuple(_GIT_MUTATING_EXTRACTORS),
    "git_non_mutating": tuple(_GIT_NON_MUTATING_SUBCOMMANDS),
    "powershell_path_arg": tuple(_POWERSHELL_PATH_ARG_VERBS),
    "powershell_both_paths": tuple(_POWERSHELL_BOTH_PATHS_VERBS),
}


def _classify_command_verb(tokens: list[str]):
    if not tokens:
        return None
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if "=" in tok and not tok.startswith("-") and "/" not in tok and "\\" not in tok:
            i += 1
            continue
        break
    if i >= len(tokens):
        return None
    relevant = tokens[i:]
    verb = relevant[0].lower()

    if verb == "git" and len(relevant) >= 2:
        sub = relevant[1].lower()
        extractor = _GIT_MUTATING_EXTRACTORS.get(sub)
        if extractor is not None:
            return extractor, relevant
        if sub in _GIT_NON_MUTATING_SUBCOMMANDS:
            return _extract_none, relevant
        return None

    if verb in _POWERSHELL_PATH_ARG_VERBS:
        return _extract_powershell_path_arg, relevant
    if verb in _POWERSHELL_BOTH_PATHS_VERBS:
        return _extract_powershell_both_paths, relevant

    return None


def _split_pipeline_stages(command: str) -> list[str]:
    if not command:
        return []
    masked = _mask_quoted_spans(command, mask_double=False)
    stages: list[str] = []
    start = 0
    i = 0
    while i < len(masked):
        ch = masked[i]
        nxt = masked[i + 1] if i + 1 < len(masked) else ""
        if ch == ";":
            stages.append(command[start:i])
            start = i + 1
            i += 1
            continue
        if ch == "|" and nxt == "|":
            stages.append(command[start:i])
            start = i + 2
            i += 2
            continue
        if ch == "|":
            stages.append(command[start:i])
            start = i + 1
            i += 1
            continue
        if ch == "&" and nxt == "&":
            stages.append(command[start:i])
            start = i + 2
            i += 2
            continue
        i += 1
    stages.append(command[start:])
    return [s.strip() for s in stages if s.strip()]


def _paths_from_shell(root: Path, command: str) -> list[str]:
    """Verb-aware path extraction per DCL-IMPL-START-GATE-VERB-AWARE-PATH-EXTRACTION-001.

    Tokenize via shlex.split(posix=False), identify the verb (first non-env-prefix
    token), and extract paths ONLY from argument positions semantically meaningful
    to that verb. For pipelines, each stage is tokenized independently. For
    commands NOT matching any verb in the table, returns an empty list; the
    caller's `_has_mutating_signal` check produces the `<unknown-mutating-target>`
    fallback when appropriate.
    """
    paths: list[str] = []
    for stage in _split_pipeline_stages(command or ""):
        try:
            tokens = shlex.split(stage, posix=False)
        except ValueError:
            continue
        classification = _classify_command_verb(tokens)
        if classification is None:
            continue
        extractor, relevant = classification
        for raw in extractor(relevant):
            rel = _normalize(root, raw)
            if rel:
                paths.append(rel)
    return sorted(set(paths))


def _is_safe_command(command: str) -> bool:
    normalized = " ".join(command.strip().split()).lower()
    if _is_simple_git_finalization_command(command):
        return True
    if any(normalized.startswith(prefix) for prefix in SAFE_COMMAND_PREFIXES):
        return True
    without_env_prefix = POWERSHELL_ENV_ASSIGNMENT_RE.sub("", normalized)
    return without_env_prefix != normalized and any(
        without_env_prefix.startswith(prefix) for prefix in SAFE_COMMAND_PREFIXES
    )


def _mask_quoted_spans(command: str, *, mask_double: bool) -> str:
    """Return ``command`` with quoted-span interiors replaced by spaces.

    Single-quoted span interiors are always blanked: single quotes make every
    shell metacharacter literal. Double-quoted span interiors are blanked only
    when ``mask_double`` is True -- double quotes make ``;``, ``|``, ``&&`` and
    ``||`` literal, but ``$(`` and backtick still execute inside them, so the
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

    ``command`` must already have safe HEREDOC substitutions neutralized.
    Chaining markers (``;``, ``|``, ``&&``, ``||``) count only outside every
    quote; execution markers (``$(``, backtick) count outside single quotes,
    including inside double quotes where they still execute.
    """
    chaining_view = _mask_quoted_spans(command, mask_double=True)
    if any(marker in chaining_view for marker in GIT_FINALIZATION_CHAINING_MARKERS):
        return True
    execution_view = _mask_quoted_spans(command, mask_double=False)
    return any(marker in execution_view for marker in GIT_FINALIZATION_EXECUTION_MARKERS)


def _find_heredoc_message_substitution_spans(command: str) -> list[tuple[int, int]]:
    """Return [start, end) spans of provably-safe ``$(cat <<'DELIM' ... DELIM)``
    command substitutions.

    A span is recognized only when EVERY boundary is validated:

    - the opener is ``$(cat <<['"]DELIM['"]`` -- the only command is read-only
      ``cat``, and the delimiter is quoted, so the heredoc body is literal;
    - the opener-line tail (between the quoted delimiter and the body's first
      newline) is whitespace-only -- a shell can place a redirect, separator,
      or pipeline there and it would execute;
    - the heredoc body ends at the FIRST line equal to DELIM (``^DELIM$``, or
      ``^\\t*DELIM$`` for the ``<<-`` form, which strips leading tabs) --
      exactly where a POSIX shell terminates the heredoc;
    - that first delimiter line is followed by optional whitespace and then the
      closing ``)`` of the substitution.

    Any deviation fails closed: the span is NOT returned and the ``$(`` stays
    visible to the control-marker scan. A recognized span runs only read-only
    ``cat`` over a literal (quoted-delimiter) heredoc body.
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
        delim_line_re = re.compile(rf"^{prefix}{re.escape(opener.group('delim'))}$", re.MULTILINE)
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
    """Blank each provably-safe ``$(cat <<'DELIM' ... DELIM)`` substitution span.

    A recognized span runs only read-only ``cat`` over a quoted-delimiter
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


def _clean_shell_token(token: str) -> str:
    return token.strip().strip("'\"")


def _shell_redirect_present(command: str) -> bool:
    """True when a shell redirection operator token (`>`, `>>`, `&>`, `&>>`)
    appears as a standalone token.

    Tokenizes with a punctuation-aware shlex scan so a `>` inside a quoted
    argument or an embedded Python expression -- a comparison, a `->` return
    arrow, a `:>` format spec, or a `>>` shift -- is not misread as a redirect:
    a quoted span tokenizes as a single token and never exposes a bare operator
    token. A parse failure (unbalanced quotes) falls back conservatively to
    non-redirect; the named-command alternatives in MUTATING_COMMAND_RE remain
    the other mutating signal in that case.
    """
    if not command:
        return False
    lexer = shlex.shlex(command, posix=False, punctuation_chars=True)
    lexer.whitespace_split = True
    try:
        return any(REDIRECT_OPERATOR_TOKEN_RE.fullmatch(token) for token in lexer)
    except ValueError:
        return False


def _has_mutating_signal(command: str) -> bool:
    """True when the command carries a mutating signal: a named mutating
    command (MUTATING_COMMAND_RE) or a standalone shell redirect operator
    token (_shell_redirect_present)."""
    return MUTATING_COMMAND_RE.search(command) is not None or _shell_redirect_present(command)


def _all_mutating_signal_is_null_sink_redirect(command: str) -> bool:
    """True iff the only mutating signal in the command is one or more null-sink redirects.

    Strips null-sink redirect tokens (e.g. ``2>/dev/null``, ``2>$null``, ``2>NUL``,
    ``&>/dev/null``) from the command and re-tests the residue with
    _has_mutating_signal. If the original command had a mutating signal but the
    stripped residue does not, the only mutating signal was a null-sink
    redirect — those are diagnostic suppression, not file mutation, and the
    command is exempt from the gate. Real-file redirects survive the strip and
    keep _has_mutating_signal matching.
    """
    if not command:
        return False
    if not _has_mutating_signal(command):
        return False
    stripped = NULL_SINK_REDIRECT_STRIP_RE.sub("", command)
    return not _has_mutating_signal(stripped)


def _is_safe_sqlite_read(command: str) -> bool:
    """True iff the command is a literal-read sqlite probe.

    Required: matches SAFE_SQLITE_READ_RE (literal SELECT/WITH/EXPLAIN keyword
    inside an execute() call after a sqlite3 reference).

    Disqualifying: any of executescript(, executemany(, .commit(, a SQL write
    keyword (INSERT/UPDATE/DELETE/REPLACE/CREATE/DROP/ALTER/TRUNCATE), or any
    PRAGMA keyword (function-call or assignment form) appears anywhere in the
    command. PRAGMA is dropped from the safe-read set because PRAGMA is not
    categorically read-only; assignment forms like ``PRAGMA user_version = 7``
    mutate database state. Variable-sourced execute(sql) calls do not match
    SAFE_SQLITE_READ_RE because their argument is not a literal string starting
    with a read keyword.
    """
    ast_result = _classify_python_sqlite_read_ast(command)
    if ast_result is not None:
        return ast_result
    if not SAFE_SQLITE_READ_RE.search(command):
        return False
    return not SQLITE_WRITE_DISQUALIFIERS_RE.search(command)


def _python_c_source(command: str) -> str | None:
    try:
        tokens = shlex.split(command, posix=True)
    except ValueError:
        return None
    for index, token in enumerate(tokens):
        if token == "-c" and index + 1 < len(tokens):
            exe = Path(tokens[0]).name.lower() if tokens else ""
            if exe.startswith("python") or exe in {"py", "python.exe"}:
                return tokens[index + 1]
    return None


def _sql_literal_is_read_only(sql: str) -> bool:
    text = sql.strip()
    if not re.match(r"(?is)^(?:SELECT|WITH|EXPLAIN)\b", text):
        return False
    return SQLITE_WRITE_DISQUALIFIERS_RE.search(text) is None


def _is_sqlite_connect_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "connect"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "sqlite3"
    )


def _is_uri_ro_connect(node: ast.Call) -> bool:
    if not node.args or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
        return False
    if not re.search(r"^file:.+?\bmode=ro\b", node.args[0].value, re.IGNORECASE):
        return False
    return any(
        keyword.arg == "uri" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True
        for keyword in node.keywords
    )


class _SQLiteReadClassifier(ast.NodeVisitor):
    def __init__(self) -> None:
        self.connections: dict[str, str] = {}
        self.saw_sqlite_operation = False
        self.unsafe = False

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802 - ast visitor name
        if _is_sqlite_connect_call(node.value):
            assert isinstance(node.value, ast.Call)
            kind = "sqlite_conn_uri_ro" if _is_uri_ro_connect(node.value) else "sqlite_conn"
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.connections[target.id] = kind
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 - ast visitor name
        if isinstance(node.func, ast.Attribute):
            receiver = node.func.value
            method = node.func.attr
            conn_kind: str | None = None
            if isinstance(receiver, ast.Name) and receiver.id in self.connections:
                conn_kind = self.connections[receiver.id]
            elif _is_sqlite_connect_call(receiver):
                assert isinstance(receiver, ast.Call)
                conn_kind = "sqlite_conn_uri_ro" if _is_uri_ro_connect(receiver) else "sqlite_conn"

            if conn_kind is not None and method in {"execute", "executemany", "executescript", "commit"}:
                self.saw_sqlite_operation = True
                if method != "execute" or not node.args:
                    self.unsafe = True
                else:
                    sql_arg = node.args[0]
                    if isinstance(sql_arg, ast.Constant) and isinstance(sql_arg.value, str):
                        if not _sql_literal_is_read_only(sql_arg.value):
                            self.unsafe = True
                    elif conn_kind != "sqlite_conn_uri_ro":
                        self.unsafe = True
        self.generic_visit(node)


def _classify_python_sqlite_read_ast(command: str) -> bool | None:
    if "sqlite3" not in command.lower():
        return None
    source = _python_c_source(command)
    if source is None:
        return None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    classifier = _SQLiteReadClassifier()
    classifier.visit(tree)
    if not classifier.saw_sqlite_operation:
        return None
    return not classifier.unsafe


def _is_mutating_command(command: str) -> bool:
    cmd = command or ""
    if not _has_mutating_signal(cmd):
        return False
    if _all_mutating_signal_is_null_sink_redirect(cmd):
        return False
    return not ("sqlite3" in cmd.lower() and _is_safe_sqlite_read(cmd))


def _is_apply_patch_tool(tool: str) -> bool:
    return tool == "apply_patch" or tool.endswith(".apply_patch")


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_string_values(item))
        return strings
    if isinstance(value, list | tuple):
        strings: list[str] = []
        for item in value:
            strings.extend(_string_values(item))
        return strings
    return []


def _apply_patch_text(payload: dict[str, Any], data: Any) -> str:
    candidates: list[str] = []
    candidates.extend(_string_values(data))
    for key in ("patch", "input", "content", "tool_input"):
        candidates.extend(_string_values(payload.get(key)))
    candidates.extend(_string_values(payload))
    for candidate in candidates:
        if "*** Begin Patch" in candidate and candidate.strip():
            return candidate
    for candidate in candidates:
        if candidate.strip():
            return candidate
    return ""


def changed_paths(payload: dict[str, Any]) -> tuple[list[str], bool]:
    root = _project_root(payload)
    tool = _tool_name(payload).lower()
    data = _tool_input(payload)

    if tool in {"write", "edit", "multiedit"}:
        path = data.get("file_path") or data.get("path")
        rel = _normalize(root, str(path)) if path else None
        return ([rel] if rel else []), True

    if _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        text = _apply_patch_text(payload, data)
        return _paths_from_apply_patch(root, text), True

    if tool in {"bash", "shell_command", "shell"} or (isinstance(data, dict) and "command" in data):
        command = str((data.get("command") if isinstance(data, dict) else None) or payload.get("command") or "")
        if _is_safe_command(command):
            return [], False
        paths = _paths_from_shell(root, command)
        return paths, _is_mutating_command(command)

    return [], False


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    root = _project_root(payload)
    paths, mutating = changed_paths(payload)
    if not mutating:
        return {}
    if not paths:
        protected = ["<unknown-mutating-target>"]
    else:
        protected = [path for path in paths if is_protected_path(path)]
    if not protected:
        return {}
    try:
        validate_targets(root, protected)
    except AuthorizationError as exc:
        classifications = ", ".join(sorted({_protected_path_classification(path) for path in protected}))
        return {
            "decision": "block",
            "reason": (
                f"BLOCKED (GTKB-IMPLEMENTATION-START-GATE): {BLOCKING_CLAUSE_ID}\n"
                f"Reason: protected implementation mutation matched {classifications} and requires "
                f"a live bridge GO authorization packet. {exc}\n"
                "Suggested fix: acquire or activate an authorization packet with "
                "`python scripts/implementation_authorization.py begin --bridge-id <id>` before mutating "
                "protected targets."
            ),
        }
    return {}


def _read_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def main() -> int:
    diagnostic = "--diagnostic" in sys.argv[1:]
    payload = _read_payload()
    result = gate_decision(payload)
    if diagnostic:
        print(
            json.dumps(
                {
                    "decision": result.get("decision", "allow"),
                    "diagnostic": True,
                    "reason": result.get("reason", ""),
                    "would_block": result.get("decision") == "block",
                },
                sort_keys=True,
            )
        )
        return 0
    if result.get("decision") == "block":
        reason = result.get("reason") or "BLOCKED (GTKB-IMPLEMENTATION-START-GATE)"
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": reason,
                        "additionalContext": reason,
                    }
                },
                sort_keys=True,
            )
        )
    else:
        print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
