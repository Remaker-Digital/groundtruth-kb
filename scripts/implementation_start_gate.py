#!/usr/bin/env python3
"""Hard gate protected implementation mutations unless a bridge GO packet exists."""

from __future__ import annotations

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
    r")\b|(?<![:>-])>{1,2}(?![>&=])",
    re.IGNORECASE,
)
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
PATH_TOKEN_RE = re.compile(
    r"(?P<path>(?:\.?/?(?:scripts|groundtruth-kb/src|groundtruth-kb/tests|platform_tests|tests|config|\.claude/hooks|\.codex/gtkb-hooks|\.github|bridge|independent-progress-assessments)/[^\s'\";]+|\.claude/settings\.json|\.codex/hooks\.json|pyproject\.toml|groundtruth\.toml))"
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


def _paths_from_apply_patch(root: Path, text: str) -> list[str]:
    normalized = (text or "").replace("`r`n", "\n").replace("`n", "\n").replace("\\r\\n", "\n").replace("\\n", "\n")
    paths = PATCH_PATH_RE.findall(normalized)
    paths.extend(PATCH_MOVE_RE.findall(normalized))
    return [rel for raw in paths if (rel := _normalize(root, raw))]


def _paths_from_shell(root: Path, command: str) -> list[str]:
    paths = [rel for raw in PATH_TOKEN_RE.findall(command or "") if (rel := _normalize(root, raw))]
    try:
        tokens = shlex.split(command, posix=False)
    except ValueError:
        tokens = []
    for token in tokens:
        if any(marker in token for marker in ("/", "\\")) or token in PROTECTED_EXACT:
            rel = _normalize(root, token)
            if rel and (is_protected_path(rel) or rel.startswith(ALLOWED_WRITE_PREFIXES)):
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


def _all_mutating_signal_is_null_sink_redirect(command: str) -> bool:
    """True iff the only mutating signal in the command is one or more null-sink redirects.

    Strips null-sink redirect tokens (e.g. ``2>/dev/null``, ``2>$null``, ``2>NUL``,
    ``&>/dev/null``) from the command and re-tests the residue against
    MUTATING_COMMAND_RE. If the original command matched MUTATING_COMMAND_RE but
    the stripped residue does not, the only mutating signal was a null-sink
    redirect — those are diagnostic suppression, not file mutation, and the
    command is exempt from the gate. Real-file redirects survive the strip and
    keep MUTATING_COMMAND_RE matching.
    """
    if not command:
        return False
    if not MUTATING_COMMAND_RE.search(command):
        return False
    stripped = NULL_SINK_REDIRECT_STRIP_RE.sub("", command)
    return not bool(MUTATING_COMMAND_RE.search(stripped))


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
    if not SAFE_SQLITE_READ_RE.search(command):
        return False
    return not SQLITE_WRITE_DISQUALIFIERS_RE.search(command)


def _is_mutating_command(command: str) -> bool:
    cmd = command or ""
    if not MUTATING_COMMAND_RE.search(cmd):
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
        return {
            "decision": "block",
            "reason": (
                "BLOCKED (GTKB-IMPLEMENTATION-START-GATE): protected implementation mutation requires "
                f"a live bridge GO authorization packet. {exc}"
            ),
        }
    return {}


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}
    except json.JSONDecodeError:
        payload = {}
    result = gate_decision(payload)
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
