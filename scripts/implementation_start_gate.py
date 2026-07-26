#!/usr/bin/env python3
"""Hard gate protected implementation mutations unless a bridge GO packet exists."""

from __future__ import annotations

import ast
import datetime as _dt
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.implementation_authorization import (
        AuthorizationError,
        canonical_project_root,
        cross_claim_path_collision_reason,
        finalization_target_paths_for_verified,
        normalize_relative_path,
        path_authorized_by_target_paths,
        peer_report_dirty_path_collision_reason,
        resolve_work_intent_session_id,
        validate_packet_project_authorization_operation,
        validate_targets,
        work_intent_claim_block_reason,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from implementation_authorization import (
        AuthorizationError,
        canonical_project_root,
        cross_claim_path_collision_reason,
        finalization_target_paths_for_verified,
        normalize_relative_path,
        path_authorized_by_target_paths,
        peer_report_dirty_path_collision_reason,
        resolve_work_intent_session_id,
        validate_packet_project_authorization_operation,
        validate_targets,
        work_intent_claim_block_reason,
    )

try:
    from scripts import bridge_work_intent_registry
except ImportError:  # pragma: no cover - direct script execution path
    import bridge_work_intent_registry  # type: ignore[no-redef]


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _record_gate_denial(pattern_id: str, subject: str, reason: str) -> None:
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    record = {
        "schema_version": 1,
        "timestamp_utc": _dt.datetime.now(tz=_dt.UTC).isoformat().replace("+00:00", "Z"),
        "gate": "implementation-start-gate",
        "pattern_id": pattern_id,
        "command_hash": hashlib.sha256(subject.encode("utf-8")).hexdigest(),
        "reason": reason,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def _record_gate_exemption(pattern_id: str, subject: str, reason: str, paths: list[str]) -> None:
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    record = {
        "schema_version": 1,
        "timestamp_utc": _dt.datetime.now(tz=_dt.UTC).isoformat().replace("+00:00", "Z"),
        "gate": "implementation-start-gate",
        "event": "exemption",
        "pattern_id": pattern_id,
        "command_hash": hashlib.sha256(subject.encode("utf-8")).hexdigest(),
        "paths": sorted(paths),
        "reason": reason,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


try:
    from scripts.controlled_artifact_paths import (
        DISPATCHER_CONFIG_PATH,
        direct_write_block_reason_code,
        normalize_relative_path_text,
    )
    from scripts.controlled_artifact_paths import (
        is_protected_path as _controlled_is_protected_path,
    )
    from scripts.controlled_artifact_paths import (
        protected_path_classification as _controlled_path_classification,
    )
except ImportError:  # pragma: no cover - direct script execution path
    from controlled_artifact_paths import (
        DISPATCHER_CONFIG_PATH,
        direct_write_block_reason_code,
        normalize_relative_path_text,
    )
    from controlled_artifact_paths import (
        is_protected_path as _controlled_is_protected_path,
    )
    from controlled_artifact_paths import (
        protected_path_classification as _controlled_path_classification,
    )

DISPATCHER_CONFIG_CLI_ONLY_BLOCK_ID = "GTKB-DISPATCHER-CONFIG-CLI-ONLY"  # config/dispatcher/rules.toml CLI-only guard
EMERGENCY_BRIDGE_REPAIR_ENV_VAR = "GTKB_EMERGENCY_BRIDGE_REPAIR"
BRIDGE_FUNCTION_EXACT = {
    ".claude/settings.json",
    ".codex/hooks.json",
    "scripts/bridge_claim_cli.py",
    "scripts/dispatcher_runtime.py",
    "scripts/gtkb_bridge_writer.py",
    "scripts/implementation_authorization.py",
    "scripts/implementation_start_gate.py",
}
BRIDGE_FUNCTION_PREFIXES = (
    ".claude/hooks/",
    ".codex/gtkb-hooks/",
    "groundtruth-kb/src/groundtruth_kb/bridge/",
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
GIT_LIFECYCLE_MUTATING_SUBCOMMANDS = frozenset(
    {"create", "attach", "preserve", "promote", "close", "resume", "recover", "drain"}
)
INVALID_HOOK_PAYLOAD_KEY = "__gtkb_invalid_hook_payload__"
# Direct Git is an inspection surface only. Every subcommand outside this
# deliberately small allowlist must enter through ``groundtruth_kb.git_lifecycle``
# so effect-time authority, quiescence, recovery, and evidence are enforced.
DIRECT_GIT_READ_ONLY_SUBCOMMANDS = frozenset(
    {
        "blame",
        "check-attr",
        "check-ignore",
        "cherry",
        "describe",
        "diff",
        "help",
        "log",
        "ls-files",
        "ls-remote",
        "ls-tree",
        "merge-base",
        "rev-list",
        "rev-parse",
        "shortlog",
        "show",
        "status",
        "verify-commit",
        "verify-tag",
        "version",
    }
)
GIT_GLOBAL_OPTIONS_WITH_VALUES = frozenset(
    {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--super-prefix", "--config-env"}
)
# Markers that disqualify a safe-command prefix, split by shell quoting
# semantics so the scan can be quote-aware (WI-3357):
#   - chaining markers are literal inside EITHER quote type;
#   - execution markers still run inside double quotes (literal only inside
#     single quotes).
GIT_FINALIZATION_CHAINING_MARKERS = (";", "&&", "||", "|")
GIT_FINALIZATION_EXECUTION_MARKERS = ("$(", "`")
MUTATING_COMMAND_RE = re.compile(
    r"\b("
    r"set-content|out-file|new-item|remove-item|move-item|copy-item|"
    # WI-IMPL-START-GATE: verb-aware path extraction. Include `git add`,
    # `git rm`, and `git restore` so protected-path staging commands also
    # trip the gate. (Per Codex NO-GO -006: extracting the path without
    # firing `_is_mutating_command` left those commands silently allowed.)
    r"apply_patch|git\s+(?:add|rm|restore|commit|reset|checkout|merge|rebase|tag|push)|"
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
# PATH_TOKEN_RE removed here (HYG-046): it was an unused dead copy. The canonical
# constant lives in implementation_authorization; bridge_applicability_preflight
# (its sole live user) imports it from there — eliminating the prior drift.
PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)
PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$", re.MULTILINE)
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
_PYTHON_EXECUTABLE_NAMES = {"py", "python", "python.exe"}
_WRAP_DIAGNOSTIC_SCRIPT_NAMES = {
    "wrap_capture_transcript.py",
    "wrap_scan_hygiene.py",
    "wrap_scan_consistency.py",
}


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


def _preserve_dot_prefixed_relative_path(relative_path: str) -> str:
    return normalize_relative_path_text(relative_path)


def is_protected_path(relative_path: str) -> bool:
    return _controlled_is_protected_path(relative_path)


def _protected_path_classification(relative_path: str) -> str:
    return _controlled_path_classification(relative_path)


def _is_bridge_function_path(relative_path: str) -> bool:
    rel = _preserve_dot_prefixed_relative_path(relative_path)
    return rel in BRIDGE_FUNCTION_EXACT or any(rel.startswith(prefix) for prefix in BRIDGE_FUNCTION_PREFIXES)


def _emergency_bridge_repair_applies(protected_paths: list[str]) -> bool:
    if os.environ.get(EMERGENCY_BRIDGE_REPAIR_ENV_VAR) != "1":
        return False
    if not protected_paths or "<unknown-mutating-target>" in protected_paths:
        return False
    return all(_is_bridge_function_path(path) for path in protected_paths)


def _dispatcher_config_direct_edit_targets(paths: list[str]) -> list[str]:
    return [path for path in paths if _preserve_dot_prefixed_relative_path(path) == DISPATCHER_CONFIG_PATH]


def _dispatcher_config_cli_only_block(targets: list[str]) -> dict[str, Any]:
    rendered = ", ".join(sorted(targets))
    return {
        "decision": "block",
        "reason_code": "dispatcher_config_cli_only",
        "reason": (
            f"BLOCKED ({DISPATCHER_CONFIG_CLI_ONLY_BLOCK_ID}): DCL-DISPATCHER-CONFIG-CLI-ONLY-001\n"
            f"Reason: direct file mutation of {rendered} is prohibited, even with a bridge GO packet. "
            "Use the governed dispatcher transaction CLI instead: "
            "`python -m groundtruth_kb.cli bridge dispatch config ...` "
            "or `gt bridge dispatch config ...`."
        ),
    }


def _paths_from_apply_patch(root: Path, text: str) -> list[str]:
    raw = text or ""
    paths = PATCH_PATH_RE.findall(raw)
    paths.extend(PATCH_MOVE_RE.findall(raw))
    if not paths:
        normalized = raw.replace("`r`n", "\n").replace("`n", "\n").replace("\\r\\n", "\n").replace("\\n", "\n")
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


_GIT_NON_MUTATING_SUBCOMMANDS = DIRECT_GIT_READ_ONLY_SUBCOMMANDS

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
        if ch in "\r\n":
            stages.append(command[start:i])
            if ch == "\r" and nxt == "\n":
                i += 1
            start = i + 1
            i += 1
            continue
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


def _shell_split(command: str, *, punctuation: bool = False) -> list[str] | None:
    if not command:
        return []
    if punctuation:
        lexer = shlex.shlex(command, posix=False, punctuation_chars=True)
        lexer.whitespace_split = True
        try:
            return list(lexer)
        except ValueError:
            return None
    try:
        return shlex.split(command, posix=False)
    except ValueError:
        return None


def _shell_verb_index(tokens: list[str]) -> int | None:
    for index, token in enumerate(tokens):
        if "=" in token and not token.startswith("-") and "/" not in token and "\\" not in token:
            continue
        return index
    return None


def _executable_name(token: str) -> str:
    """Return a shell executable basename across POSIX and Windows paths."""
    return _clean_shell_token(token).replace("\\", "/").rsplit("/", 1)[-1].lower()


_CMD_SHELL_NAMES = frozenset({"cmd", "cmd.exe"})
_POWERSHELL_NAMES = frozenset({"powershell", "powershell.exe", "pwsh", "pwsh.exe"})
_POSIX_SHELL_NAMES = frozenset({"bash", "bash.exe", "sh", "sh.exe", "zsh", "zsh.exe"})
_POWERSHELL_ENCODED_COMMAND_FLAGS = frozenset(
    {"-e", "-ec", "-en", "-enc", "-enco", "-encod", "-encode", "-encoded", "-encodedcommand"}
)


def _nested_shell_command(stage: str) -> tuple[str | None, bool]:
    """Return a nested shell command and whether a shell wrapper was recognized.

    An encoded or malformed command is reported as a recognized wrapper with no
    inspectable command so direct Git enforcement can fail closed.
    """
    tokens = _shell_split(stage)
    if not tokens:
        return None, False
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None, False
    relevant = tokens[verb_index:]
    while relevant and _clean_shell_token(relevant[0]).lower() in {"&", "call"}:
        relevant = relevant[1:]
    if not relevant:
        return None, True
    executable = _executable_name(relevant[0])

    if executable in _CMD_SHELL_NAMES:
        for index, raw in enumerate(relevant[1:], start=1):
            if _clean_shell_token(raw).lower() in {"/c", "/k"}:
                nested = " ".join(relevant[index + 1 :]).strip()
                return (_clean_shell_token(nested) if nested else None), True
        return None, False

    if executable in _POWERSHELL_NAMES:
        normalized = [_clean_shell_token(token).lower() for token in relevant[1:]]
        if any(token in _POWERSHELL_ENCODED_COMMAND_FLAGS for token in normalized):
            return None, True
        for index, token in enumerate(normalized, start=1):
            if token in {"-c", "-command", "/c", "/command"}:
                nested = " ".join(relevant[index + 1 :]).strip()
                return (_clean_shell_token(nested) if nested else None), True
        return None, False

    if executable in _POSIX_SHELL_NAMES:
        normalized = [_clean_shell_token(token).lower() for token in relevant[1:]]
        for index, token in enumerate(normalized, start=1):
            if token == "-c":
                if index + 1 >= len(relevant):
                    return None, True
                return _clean_shell_token(relevant[index + 1]), True
        return None, False

    if verb_index < len(tokens) and tokens[verb_index:] != relevant:
        return " ".join(relevant), True
    return None, False


def _python_script_invocation(tokens: list[str]) -> tuple[str, list[str]] | None:
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = tokens[verb_index:]
    verb_name = Path(relevant[0].strip("'\"")).name.lower()
    if verb_name not in _PYTHON_EXECUTABLE_NAMES and not verb_name.startswith("python"):
        return None
    if len(relevant) < 2:
        return None
    script_token = relevant[1].strip("'\"")
    script_name = Path(script_token).name
    if script_name not in _WRAP_DIAGNOSTIC_SCRIPT_NAMES:
        return None
    return script_name, relevant[2:]


def _git_lifecycle_subcommand(stage: str) -> str | None:
    """Return the production Git-lifecycle CLI subcommand for one shell stage."""
    tokens = _shell_split(stage)
    if not tokens:
        return None
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = [_clean_shell_token(token) for token in tokens[verb_index:]]
    executable = Path(relevant[0]).name.lower()
    if executable not in _PYTHON_EXECUTABLE_NAMES and not executable.startswith("python"):
        return None
    if len(relevant) < 4 or relevant[1:3] != ["-m", "groundtruth_kb.git_lifecycle"]:
        return None

    # argparse accepts these global options before the required subcommand.
    index = 3
    options_with_values = {"--repo", "--state-dir", "--dispatcher-state-dir"}
    flag_options = {"--json", "--dry-run"}
    while index < len(relevant):
        token = relevant[index]
        if token in options_with_values:
            if index + 1 >= len(relevant):
                return None
            index += 2
            continue
        if any(token.startswith(option + "=") for option in options_with_values):
            index += 1
            continue
        if token in flag_options:
            index += 1
            continue
        return token.lower()
    return None


def _direct_git_subcommand(stage: str) -> str | None:
    """Return a direct Git subcommand, accounting for executable/global options."""
    tokens = _shell_split(stage)
    if not tokens:
        return None
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return None
    relevant = [_clean_shell_token(token) for token in tokens[verb_index:]]
    executable = Path(relevant[0]).name.lower()
    if executable not in {"git", "git.exe"}:
        return None

    index = 1
    while index < len(relevant):
        token = relevant[index]
        if token == "--":
            index += 1
            break
        if token in GIT_GLOBAL_OPTIONS_WITH_VALUES:
            if index + 1 >= len(relevant):
                return None
            index += 2
            continue
        if any(token.startswith(option + "=") for option in GIT_GLOBAL_OPTIONS_WITH_VALUES):
            index += 1
            continue
        if token.startswith("-C") and token != "-C":
            index += 1
            continue
        if token.startswith("-c") and token != "-c":
            index += 1
            continue
        if token.startswith("-"):
            index += 1
            continue
        return token.lower()
    if index < len(relevant):
        return relevant[index].lower()
    return None


def _is_direct_git_invocation(stage: str) -> bool:
    tokens = _shell_split(stage)
    if not tokens:
        return False
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return False
    return Path(_clean_shell_token(tokens[verb_index])).name.lower() in {"git", "git.exe"}


def _direct_git_effect(stage: str, *, _depth: int = 0) -> str | None:
    if _depth > 4:
        return "<uninspectable-shell-command>"
    if not _is_direct_git_invocation(stage):
        nested, recognized_wrapper = _nested_shell_command(stage)
        if recognized_wrapper:
            if not nested:
                return "<uninspectable-shell-command>"
            return _direct_git_effect(nested, _depth=_depth + 1)
        return None
    subcommand = _direct_git_subcommand(stage)
    if subcommand in DIRECT_GIT_READ_ONLY_SUBCOMMANDS:
        return None
    return subcommand or "<unknown>"


def _has_direct_git_effect_signal(command: str) -> bool:
    if _direct_git_effect(command) is not None:
        return True
    return any(_direct_git_effect(stage) is not None for stage in _split_pipeline_stages(command))


def _has_mutating_git_lifecycle_signal(command: str) -> bool:
    return any(
        _git_lifecycle_subcommand(stage) in GIT_LIFECYCLE_MUTATING_SUBCOMMANDS
        for stage in _split_pipeline_stages(command)
    )


def _arg_value(args: list[str], flag: str) -> str | None:
    for index, token in enumerate(args):
        if token == flag and index + 1 < len(args):
            return args[index + 1]
        if token.startswith(flag + "="):
            return token.split("=", 1)[1]
    return None


def _redirect_targets(stage: str) -> list[str]:
    tokens = _shell_split(stage, punctuation=True)
    if tokens is None:
        return []
    targets: list[str] = []
    for index, token in enumerate(tokens):
        if REDIRECT_OPERATOR_TOKEN_RE.fullmatch(token):
            if index + 1 < len(tokens):
                targets.append(tokens[index + 1])
            continue
        if (
            re.fullmatch(r"\d+", token)
            and index + 1 < len(tokens)
            and REDIRECT_OPERATOR_TOKEN_RE.fullmatch(tokens[index + 1])
        ):
            if index + 2 < len(tokens):
                targets.append(tokens[index + 2])
    return targets


def _diagnostic_output_paths_for_stage(root: Path, stage: str) -> list[str] | None:
    tokens = _shell_split(stage)
    if tokens is None:
        return None
    invocation = _python_script_invocation(tokens)
    if invocation is None:
        return None
    script_name, args = invocation
    outputs: list[str] = []
    if script_name == "wrap_capture_transcript.py":
        session_id = _arg_value(args, "--session-id")
        if not session_id:
            return None
        snapshot_root = _arg_value(args, "--snapshot-root") or ".groundtruth/session/snapshots"
        snapshot_root = snapshot_root.rstrip("/").rstrip("\\")
        outputs.append(f"{snapshot_root}/{session_id}/manifest.json")
    else:
        report_path = _arg_value(args, "--write-report")
        if report_path:
            outputs.append(report_path)
        outputs.extend(_redirect_targets(stage))
        if not outputs:
            return None
    normalized: list[str] = []
    for output in outputs:
        rel = _normalize(root, output)
        if not rel:
            return None
        normalized.append(rel)
    return sorted(set(normalized))


def _diagnostic_output_paths_from_shell(root: Path, command: str) -> list[str] | None:
    if not command:
        return None
    outputs: list[str] = []
    matched = False
    for stage in _split_pipeline_stages(command):
        stage_outputs = _diagnostic_output_paths_for_stage(root, stage)
        if stage_outputs is None:
            continue
        matched = True
        outputs.extend(stage_outputs)
    if not matched:
        return None
    return sorted(set(outputs))


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
    # A safe-command entry authorizes exactly one parsed shell stage. Applying
    # it to the raw command prefix lets a later stage inherit the exemption
    # (for example, ``pytest; Set-Content`` or ``git status; git add``).
    scan_command = _neutralize_heredoc_message_substitutions(command)
    if _has_disqualifying_control_marker(scan_command):
        return False
    chaining_view = _mask_quoted_spans(scan_command, mask_double=True)
    if any(marker in chaining_view for marker in ("&", "\r", "\n")):
        return False
    stages = _split_pipeline_stages(scan_command)
    if len(stages) != 1:
        return False
    tokens = _shell_split(stages[0])
    if not tokens:
        return False
    verb_index = _shell_verb_index(tokens)
    if verb_index is None:
        return False
    normalized = " ".join(_clean_shell_token(token).lower() for token in tokens[verb_index:])
    return any(
        normalized == prefix.strip() or normalized.startswith(prefix.strip() + " ") for prefix in SAFE_COMMAND_PREFIXES
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
    """True iff a control marker disqualifies a safe-command prefix.

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


def _python_call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _constant_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _open_call_uses_write_mode(node: ast.Call) -> bool:
    mode: str | None = None
    if len(node.args) >= 2:
        mode = _constant_string(node.args[1])
    for keyword in node.keywords:
        if keyword.arg == "mode":
            mode = _constant_string(keyword.value)
            break
    return mode is not None and "w" in mode


def _has_python_mutating_signal(command: str) -> bool:
    source = _python_c_source(command)
    if source is None:
        return False
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    sqlite_classification = _classify_python_sqlite_read_ast(command)
    if sqlite_classification is False:
        return True

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = _python_call_name(node.func)
        if call_name == "write_text":
            return True
        if call_name == "open" and _open_call_uses_write_mode(node):
            return True
        if call_name and call_name.startswith(("insert_", "update_", "delete_")):
            return True
    return False


def _has_mutating_signal(command: str) -> bool:
    """True when the command carries a mutating signal: a named mutating
    command (MUTATING_COMMAND_RE) or a standalone shell redirect operator
    token (_shell_redirect_present)."""
    shell_view = _mask_quoted_spans(command, mask_double=True)
    return (
        MUTATING_COMMAND_RE.search(shell_view) is not None
        or _has_direct_git_effect_signal(command)
        or _has_mutating_git_lifecycle_signal(command)
        or _has_python_mutating_signal(command)
        or _shell_redirect_present(command)
    )


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


def _argv_command(argv: Any) -> str | None:
    if not isinstance(argv, list | tuple) or not argv:
        return None
    if not all(isinstance(token, str | int | float) for token in argv):
        return None
    return subprocess.list2cmdline([str(token) for token in argv])


def _command_from_payload(payload: dict[str, Any], data: Any, tool: str) -> str | None:
    """Normalize shell command strings and shell-free Git argv payloads."""
    raw_command = data.get("command") if isinstance(data, dict) else None
    if raw_command is None:
        raw_command = payload.get("command")
    command = raw_command if isinstance(raw_command, str) else _argv_command(raw_command)

    args: Any = None
    if isinstance(data, dict):
        args = data.get("argv") if data.get("argv") is not None else data.get("args")
    if command:
        executable = Path(_clean_shell_token(command)).name.lower()
        argv_text = _argv_command(args)
        if executable in {"git", "git.exe"} and argv_text:
            return f"{command} {argv_text}"
        return command

    if Path(tool).name.lower() not in {"git", "git.exe"}:
        return None
    argv_text = _argv_command(args)
    if not argv_text:
        return None
    argv_tokens = list(args)
    first = Path(str(argv_tokens[0])).name.lower()
    return argv_text if first in {"git", "git.exe"} else f"git {argv_text}"


def _direct_git_effect_from_payload(payload: dict[str, Any]) -> str | None:
    data = _tool_input(payload)
    command = _command_from_payload(payload, data, _tool_name(payload).lower())
    if not command:
        return None
    subcommand = _direct_git_effect(command)
    if subcommand is not None:
        return subcommand
    for stage in _split_pipeline_stages(command):
        subcommand = _direct_git_effect(stage)
        if subcommand is not None:
            return subcommand
    return None


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

    command = _command_from_payload(payload, data, tool)
    if command is not None:
        if _is_safe_command(command):
            return [], False
        diagnostic_outputs = _diagnostic_output_paths_from_shell(root, command)
        if diagnostic_outputs is not None:
            return diagnostic_outputs, True
        paths = _paths_from_shell(root, command)
        return paths, _is_mutating_command(command)

    return [], False


def _finalization_git_add_targets(command: str) -> list[str] | None:
    """Return the explicit path args of a pure ``git add`` staging command.

    Returns ``None`` (disqualified) unless the command is a single-stage
    ``git add`` of explicit file paths. Any of the following disqualifies the
    fast finalization clearance so the command falls through to the normal
    authorization gate: multiple pipeline stages / chaining, control or
    command-substitution markers, a non-``git add`` verb, a broad or whole-tree
    stage (``-A`` / ``--all`` / ``-u`` / ``.`` / any flag), pathspec magic
    (``:/``, ``:(exclude)``), glob metacharacters, unparseable tokens, or no
    explicit path argument. This mirrors the disqualifiers named in the WI-4837
    proposal (chained protected writes, broad reset/checkout/rm, deletion,
    cleanup, denied git flags, unparseable targets).
    """
    scan_command = command or ""
    if _has_disqualifying_control_marker(scan_command):
        return None
    stages = _split_pipeline_stages(scan_command)
    if len(stages) != 1:
        return None
    try:
        raw_tokens = shlex.split(stages[0], posix=False)
    except ValueError:
        return None
    tokens = [token for token in (_clean_shell_token(raw) for raw in raw_tokens) if token]
    # Skip leading VAR=value env prefixes (mirror _classify_command_verb).
    index = 0
    while index < len(tokens):
        tok = tokens[index]
        if "=" in tok and not tok.startswith("-") and "/" not in tok and "\\" not in tok:
            index += 1
            continue
        break
    relevant = tokens[index:]
    if len(relevant) < 3 or relevant[0].lower() != "git" or relevant[1].lower() != "add":
        return None
    paths: list[str] = []
    for arg in relevant[2:]:
        if arg == "--":
            continue
        if arg.startswith("-"):
            return None  # any flag (incl. -A/--all/-u/-p/--patch) disqualifies
        if arg.startswith(":"):
            return None  # pathspec magic (:/, :(exclude)) disqualifies
        if arg == ".":
            return None  # whole-tree add disqualifies
        if any(meta in arg for meta in ("*", "?", "[", "]")):
            return None  # glob disqualifies (targets not concretely enumerable)
        paths.append(arg)
    if not paths:
        return None
    return paths


def _post_verified_finalization_clearance(root: Path, payload: dict[str, Any]) -> str | None:
    """Clear a narrow post-``VERIFIED`` finalization ``git add`` staging command.

    WI-4837 automatic parity (owner decision
    ``DELIB-WI4837-AUTOMATIC-PARITY-20260707``). After a bridge thread reaches
    terminal ``VERIFIED`` the implementation phase is closed, so ordinary
    implementation-start packets fail closed and a Prime-side ``git add`` that
    stages the thread's own approved paths for a recovery finalization commit is
    blocked. This mirrors the pre-commit gate, which already clears
    terminal-``VERIFIED`` approved paths. The clearance is granted only when ALL
    of the following hold:

    - the command is a single-stage ``git add`` of explicit file paths (no
      chaining, substitution, flags, pathspec magic, globs, or whole-tree add);
    - the current work-intent/session context identifies one bridge thread;
    - that thread's latest post-GO chain state is terminal ``VERIFIED``;
    - every staged target is inside the thread's approved proposal
      ``target_paths``.

    Returns a human-readable reason string when the clearance is granted, or
    ``None`` to fall through to the normal authorization gate (which fails
    closed). Never raises: any lookup failure returns ``None``.
    """
    data = _tool_input(payload)
    is_shell = _tool_name(payload).lower() in {"bash", "shell_command", "shell"} or (
        isinstance(data, dict) and "command" in data
    )
    if not is_shell:
        return None
    command = str((data.get("command") if isinstance(data, dict) else None) or payload.get("command") or "")
    targets = _finalization_git_add_targets(command)
    if not targets:
        return None
    normalized_targets: list[str] = []
    for target in targets:
        cleaned = target.strip().strip("'\"`").replace("\\", "/")
        if not cleaned or cleaned == ".":
            return None
        try:
            rel = normalize_relative_path(root, cleaned)
        except AuthorizationError:
            return None  # target escapes project root -> fail closed
        normalized_targets.append(rel)
    session_id = resolve_work_intent_session_id(payload)
    if not session_id:
        return None
    try:
        bridge_id = bridge_work_intent_registry.current_claimed_bridge_id(session_id, project_root=root)
    except Exception:  # noqa: BLE001 - registry failure must not clear the gate
        return None
    if not bridge_id:
        return None
    try:
        approved_target_paths = finalization_target_paths_for_verified(root, bridge_id)
    except AuthorizationError:
        return None  # not terminal VERIFIED, or approved paths unparseable -> fall through
    for rel in normalized_targets:
        if not path_authorized_by_target_paths(approved_target_paths, rel):
            return None  # a staged target is outside approved target_paths -> fall through
    return (
        f"post-VERIFIED finalization staging cleared for bridge {bridge_id!r}: "
        f"staged targets {sorted(normalized_targets)} are all inside the approved "
        "terminal-VERIFIED proposal target_paths "
        "(automatic parity per DELIB-WI4837-AUTOMATIC-PARITY-20260707)."
    )


def _registry_observation_intent(
    root: Path,
    payload: dict[str, Any],
    protected: list[str],
    *,
    session_id: str,
    bridge_id: str,
    packet: dict[str, Any],
    project_authorization: dict[str, Any],
) -> dict[str, Any] | None:
    """Mint and persist one exact post-tool capability for registered targets."""

    if payload.get("__gtkb_registry_diagnostic__") is True:
        return None
    registry_path = root / "config" / "registry" / "sot-artifacts.toml"
    if not registry_path.exists():
        return None
    package_src = root / "groundtruth-kb" / "src"
    if str(package_src) not in sys.path:
        sys.path.insert(0, str(package_src))
    try:
        from groundtruth_kb.project.registry_control_plane import (
            RegistryControlPlaneError,
            load_registry_snapshot,
            mint_observation_capability,
            registry_currentness,
        )

        from scripts.registry_observation_hook import intent_path
    except ImportError as exc:
        raise AuthorizationError(f"registry control plane is unavailable: {exc}") from exc
    try:
        snapshot = load_registry_snapshot(project_root=root, db_path=root / "groundtruth.db")
        registered: dict[str, Any] = {}
        registered_paths: list[str] = []
        for path in protected:
            record = snapshot.resolver.resolve(path)
            if record is not None:
                registered[record.id] = record
                registered_paths.append(path)
        if not registered:
            return None
        currentness = registry_currentness(snapshot, project_root=root, db_path=root / "groundtruth.db")
        if not currentness["current"]:
            raise AuthorizationError(
                "registered target mutation requires current registry revision evidence: "
                f"missing={currentness['missing_revisions']}, stale={currentness['stale']}"
            )
        denied_roles = sorted(
            record.id for record in registered.values() if record.owner_role not in {"shared", "prime_builder"}
        )
        if denied_roles:
            raise AuthorizationError(f"registered targets are not Prime Builder writable: {denied_roles}")
        missing_api = sorted(record.id for record in registered.values() if not record.mutation_api.strip())
        if missing_api:
            raise AuthorizationError(f"registered targets have no mutation API: {missing_api}")
        tool = _tool_name(payload).strip() or "unknown"
        data = _tool_input(payload)
        command = str(data.get("command") or payload.get("command") or "") if isinstance(data, dict) else ""
        patch_text = str(data.get("patch") or "") if isinstance(data, dict) else ""
        identity_change = (
            tool.casefold() in {"delete", "move"}
            or bool(re.search(r"\b(?:remove-item|move-item|git\s+(?:mv|rm)|rm|del)\b", command, re.IGNORECASE))
            or bool(re.search(r"^\*\*\* (?:Delete File:|Move to:)", patch_text, re.MULTILINE))
        )
        if identity_change:
            raise AuthorizationError(
                "registered deletion, move, rename, or locator change requires separately reviewed transition authority"
            )
        event_id = str(
            payload.get("tool_use_id")
            or payload.get("toolUseID")
            or payload.get("tool_event_id")
            or payload.get("event_id")
            or ""
        ).strip()
        if not session_id or not event_id:
            raise AuthorizationError("registered target mutation requires session and tool event identifiers")
        start_packet_hash = str(packet.get("packet_hash") or "")
        if not start_packet_hash:
            start_packet_hash = (
                "sha256:"
                + hashlib.sha256(json.dumps(packet, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            )
        minted = mint_observation_capability(
            target_paths=registered_paths,
            session_id=session_id,
            tool_event_id=event_id,
            bridge_id=bridge_id,
            start_packet_hash=start_packet_hash,
            pauth_decision=project_authorization,
            operation=tool,
            authorized=True,
            project_root=root,
            db_path=root / "groundtruth.db",
        )
        intent = {
            "capability": minted["capability"],
            "capability_hash": minted["capability_hash"],
            "target_paths": minted["paths"],
            "preimage_digests": minted["preimage_digests"],
            "session_id": session_id,
            "tool_event_id": event_id,
            "bridge_id": bridge_id,
            "start_packet_hash": start_packet_hash,
            "operation": tool,
            "change_reason": f"authorized observation for bridge {bridge_id}",
        }
        destination = intent_path(root, session_id, event_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(json.dumps(intent, sort_keys=True), encoding="utf-8")
        os.replace(temporary, destination)
        return {"capability_hash": minted["capability_hash"], "tool_event_id": event_id}
    except RegistryControlPlaneError as exc:
        raise AuthorizationError(f"registry control plane denied mutation: {exc}") from exc


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    invalid_payload_reason = payload.get(INVALID_HOOK_PAYLOAD_KEY)
    if isinstance(invalid_payload_reason, str) and invalid_payload_reason:
        return {
            "decision": "block",
            "reason_code": "invalid_hook_payload",
            "reason": (
                "BLOCKED (GTKB-IMPLEMENTATION-START-GATE): invalid PreToolUse payload. "
                f"{invalid_payload_reason} The gate fails closed because tool intent cannot be verified."
            ),
        }
    direct_git_effect = _direct_git_effect_from_payload(payload)
    if direct_git_effect is not None:
        return {
            "decision": "block",
            "reason_code": "direct_git_effect_requires_lifecycle",
            "reason": (
                "BLOCKED (GTKB-GIT-LIFECYCLE): direct "
                f"`git {direct_git_effect}` is not an authorized execution boundary. "
                "Use the canonical `python -m groundtruth_kb.git_lifecycle` operation so current authority, "
                "scope binding, quiescence, recovery, and evidence are enforced at effect time."
            ),
        }
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
    direct_reason_code = direct_write_block_reason_code(protected)
    if direct_reason_code is not None:
        classifications = ", ".join(sorted({_protected_path_classification(path) for path in protected}))
        return {
            "decision": "block",
            "reason_code": direct_reason_code,
            "reason": (
                f"BLOCKED (GTKB-CONTROLLED-ARTIFACT-DIRECT-MUTATION): {BLOCKING_CLAUSE_ID}\n"
                f"Reason: direct mutation matched controlled artifact surface(s): {classifications}. "
                "Use the governed bridge, MemBase, dispatcher, or implementation-authorization helper path "
                "for this artifact class; a raw tool or shell write is not valid authority evidence."
            ),
        }
    dispatcher_config_targets = _dispatcher_config_direct_edit_targets(protected)
    if dispatcher_config_targets:
        return _dispatcher_config_cli_only_block(dispatcher_config_targets)
    if _emergency_bridge_repair_applies(protected):
        _record_gate_exemption(
            "emergency-bridge-repair",
            json.dumps(payload, sort_keys=True),
            "owner-authorized emergency bridge repair exemption",
            protected,
        )
        return {}
    # WI-4837: post-VERIFIED finalization staging clearance (automatic parity per
    # DELIB-WI4837-AUTOMATIC-PARITY-20260707). A narrow `git add` of the thread's
    # own approved target_paths, on a terminal-VERIFIED chain identified by the
    # session's work-intent claim, is cleared here so the finalization commit can
    # stage its verified paths. This runs BEFORE validate_targets (which fails
    # closed for terminal VERIFIED) and leaves _validate_packet unchanged:
    # ordinary post-VERIFIED mutation still falls through and is blocked below.
    finalization_reason = _post_verified_finalization_clearance(root, payload)
    if finalization_reason is not None:
        _record_gate_exemption(
            "post-verified-finalization-staging",
            json.dumps(payload, sort_keys=True),
            finalization_reason,
            protected,
        )
        return {}
    try:
        # WI-4443: resolve the work-intent session BEFORE packet resolution so
        # validate_targets can prefer this session's OWN claimed by-bridge packet
        # over the global current.json pointer (which thrashes under concurrent
        # Prime Builders). The block-reason check below is unchanged — it now
        # operates on the session-correct packet.
        session_id = resolve_work_intent_session_id(payload)
        result = validate_targets(root, protected, session_id=session_id)
        packet = result.get("packet", {})
        project_authorization = validate_packet_project_authorization_operation(
            root,
            packet,
            requested_operations=["implementation_start", "protected_mutation"],
            target_paths=[str(path) for path in result.get("targets", protected)],
        )
        if project_authorization is None:
            raise AuthorizationError(
                "Project Authorization is required before every protected source, test, or configuration mutation."
            )
        bridge_id = str(packet.get("bridge_id") or "")
        block_reason = work_intent_claim_block_reason(root, bridge_id, session_id)
        if block_reason:
            raise AuthorizationError(block_reason)
        # WI-4471: cross-claim path-collision check — block if a different session's
        # active claim+packet already reserves any of the same target paths.
        collision_reason = cross_claim_path_collision_reason(
            root, targets=protected, bridge_id=bridge_id, session_id=session_id
        )
        if collision_reason:
            raise AuthorizationError(collision_reason)
        peer_report_reason = peer_report_dirty_path_collision_reason(
            root,
            targets=protected,
            bridge_id=bridge_id,
        )
        if peer_report_reason:
            raise AuthorizationError(peer_report_reason)
        observation_intent = _registry_observation_intent(
            root,
            payload,
            protected,
            session_id=session_id or "",
            bridge_id=bridge_id,
            packet=packet,
            project_authorization=project_authorization,
        )
    except AuthorizationError as exc:
        classifications = ", ".join(sorted({_protected_path_classification(path) for path in protected}))
        return {
            "decision": "block",
            "reason": (
                f"BLOCKED (GTKB-IMPLEMENTATION-START-GATE): {BLOCKING_CLAUSE_ID}\n"
                f"Reason: protected implementation mutation matched {classifications} and requires "
                f"a live bridge GO authorization packet plus matching bridge work-intent claim. {exc}\n"
                "Suggested fix: acquire or activate an authorization packet with "
                "`python scripts/bridge_claim_cli.py claim <id>` and "
                "`python scripts/implementation_authorization.py begin --bridge-id <id>` before mutating protected targets."
            ),
        }
    if observation_intent is not None:
        return {"registryObservationIntent": observation_intent}
    return {}


def _read_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {INVALID_HOOK_PAYLOAD_KEY: "Hook input was empty."}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {INVALID_HOOK_PAYLOAD_KEY: (f"Hook input was malformed JSON at line {exc.lineno}, column {exc.colno}.")}
    if not isinstance(payload, dict) or not payload:
        return {INVALID_HOOK_PAYLOAD_KEY: "Hook input must be a non-empty JSON object."}
    return payload


def main() -> int:
    diagnostic = "--diagnostic" in sys.argv[1:]
    payload = _read_payload()
    if diagnostic:
        payload["__gtkb_registry_diagnostic__"] = True
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
        _record_gate_denial("protected-target-without-go", json.dumps(payload, sort_keys=True), reason)
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
        print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
