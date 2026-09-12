#!/usr/bin/env python3
"""Check tool effects through the native CLI and current artifact claims."""

from __future__ import annotations

import ast
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

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
)

INVALID_HOOK_PAYLOAD_KEY = "__gtkb_invalid_hook_payload__"

DIRECT_GIT_READ_ONLY_SUBCOMMANDS = frozenset(
    {
        "blame",
        "check-attr",
        "check-ignore",
        "cherry",
        "describe",
        "diff",
        # Read-only ref enumeration. Reviewers must be able to inspect branch
        # topology to verify claims about it; blocking that degrades review
        # quality without preventing any effect. `branch` is deliberately NOT
        # listed: `git branch -d/-D/-m/-M/--set-upstream-to` mutate, so it
        # cannot be allow-listed by subcommand name alone. Covered by
        # test_change7_drops_argument_position_false_positives.
        "for-each-ref",
        "show-ref",
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
    # F10: POSIX write verbs. The original alternation covered only the
    # PowerShell surface (set-content/remove-item/move-item/copy-item), so on
    # the Bash surface `sed -i`, `touch`, `tee`, `cp`, `mv`, `rm` and friends
    # were never classified as mutations and passed the gate unconditionally,
    # while read-only inspection was refused. Quoted spans are masked by
    # _has_mutating_signal before this regex runs, so verbs appearing inside
    # quoted prose do not false-positive.
    r"sed\s+(?:[^|;&]*\s)?-i\b|awk\s+[^|;&]*-i\s+inplace\b|"
    r"python\s+.*(?:write_text|open\(.+,\s*['\"]w|sqlite3|insert_|update_|delete_)"
    r")\b"
    # Change 7 (WI-6821): bare POSIX write verbs are matched only at COMMAND
    # POSITION -- start of string, or after a pipe/semicolon/ampersand/newline,
    # or after an opening paren. The unanchored form these replace matched the
    # verbs anywhere, so ordinary prose in an argument (`git log --grep=rm`, a
    # `--filter` value, a quoted sentence) tripped a fail-closed gate. Quoted
    # spans are masked by `_has_mutating_signal` before this regex runs; the
    # anchor is the second, independent guard against argument-position text.
    #
    # This alternative sits OUTSIDE the `\b( ... )\b` group above, deliberately.
    # Inside it, the group's leading `\b` must match immediately before the
    # anchor, and a space-to-pipe transition is not a word boundary -- so
    # `cat x | tee <path>`, `true && rm <path>`, and `(cd d && rm <path>)` all
    # silently stopped matching. Hoisting it to a top-level alternative keeps
    # every real detection while dropping the argument-position false
    # positives. Regression coverage for both directions lives in
    # platform_tests/scripts/test_implementation_start_gate.py.
    r"|(?:^|[|;&\n]|\()\s*(?:tee|touch|truncate|shred|install|patch|dd|cp|mv|rm|ln)\b",
    re.IGNORECASE,
)

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

PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add|Update|Delete) File: (.+)$", re.MULTILINE)

PATCH_MOVE_RE = re.compile(r"^\*\*\* Move to: (.+)$", re.MULTILINE)

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


try:
    from scripts.controlled_artifact_paths import (
        DISPATCHER_CONFIG_PATH,
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
        normalize_relative_path_text,
    )
    from controlled_artifact_paths import (
        is_protected_path as _controlled_is_protected_path,
    )
    from controlled_artifact_paths import (
        protected_path_classification as _controlled_path_classification,
    )

DISPATCHER_CONFIG_CLI_ONLY_BLOCK_ID = "GTKB-DISPATCHER-CONFIG-CLI-ONLY"  # config/dispatcher/rules.toml CLI-only guard


def _project_root(payload: dict[str, Any]) -> Path:
    explicit = payload.get("project_root")
    if isinstance(explicit, str) and explicit.strip():
        return Path(explicit).resolve()
    cwd = payload.get("cwd")
    cwd_path = Path(cwd).resolve() if isinstance(cwd, str) and cwd.strip() else PROJECT_ROOT
    return Path(os.environ.get("GTKB_PROJECT_ROOT") or cwd_path).resolve()


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


def _normalize(root: Path, path_text: str, *, shell_quoted: bool = False) -> str | None:
    cleaned = path_text
    if shell_quoted and len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in "'\"":
        cleaned = cleaned[1:-1]
    cleaned = cleaned.replace("\\", "/")
    if not cleaned:
        return None
    try:
        target = Path(cleaned)
        target = target if target.is_absolute() else root / target
        return target.relative_to(root).as_posix()
    except ValueError:
        return cleaned


def _preserve_dot_prefixed_relative_path(relative_path: str) -> str:
    return normalize_relative_path_text(relative_path)


def is_protected_path(relative_path: str, *, project_root: Path | None = None) -> bool:
    return _controlled_is_protected_path(relative_path, project_root=project_root)


def _protected_path_classification(relative_path: str, *, project_root: Path | None = None) -> str:
    return _controlled_path_classification(relative_path, project_root=project_root)


_BRIDGE_ARTIFACT_DEPOSIT_RE = re.compile(r"^bridge/[A-Za-z0-9][A-Za-z0-9._-]*-\d{3}\.md$")


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


_POSIX_PATH_ARG_VERBS = frozenset({"sed", "awk", "tee", "touch", "truncate", "rm", "shred", "install", "patch"})

_POSIX_BOTH_PATHS_VERBS = frozenset({"cp", "mv", "ln", "dd"})


def _extract_posix_paths(tokens: list[str]) -> list[str]:
    """Every non-flag operand of a POSIX write verb, plus ``dd`` ``of=`` targets.

    Deliberately over-collects: a non-path operand (a ``sed`` script such as
    ``s/a/b/``, or a ``dd`` ``if=`` source) simply fails to match any protected
    glob and is inert. Under-collecting is the dangerous direction -- a missed
    operand degrades to ``<unknown-mutating-target>``, which both refuses the
    emergency-repair exemption and hides which path was actually at risk.
    """
    paths: list[str] = []
    for token in tokens[1:]:
        if token.startswith("-"):
            continue
        if "=" in token and "/" not in token.split("=", 1)[0]:
            key, _, value = token.partition("=")
            if key.lower() == "of" and value:
                paths.append(value)
            continue
        paths.append(token)
    return paths


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
    "posix_path_arg": tuple(_POSIX_PATH_ARG_VERBS),
    "posix_both_paths": tuple(_POSIX_BOTH_PATHS_VERBS),
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
    if verb in _POSIX_PATH_ARG_VERBS or verb in _POSIX_BOTH_PATHS_VERBS:
        return _extract_posix_paths, relevant

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
        rel = _normalize(root, output, shell_quoted=True)
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
            rel = _normalize(root, raw, shell_quoted=True)
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
    normalized_tokens = [_clean_shell_token(token).lower() for token in tokens[verb_index:]]
    if _requests_help_output_only(scan_command, normalized_tokens):
        return True
    normalized = " ".join(normalized_tokens)
    return any(
        normalized == prefix.strip() or normalized.startswith(prefix.strip() + " ") for prefix in SAFE_COMMAND_PREFIXES
    )


_RUFF_VALUE_OPTIONS = frozenset(
    {
        "--config",
        "--color",
        "--output-format",
        "--target-version",
        "--extension",
        "--select",
        "--ignore",
        "--extend-select",
        "--per-file-ignores",
        "--extend-per-file-ignores",
        "--fixable",
        "--unfixable",
        "--extend-fixable",
        "--exclude",
        "--extend-exclude",
        "--cache-dir",
        "--stdin-filename",
        "--line-length",
        "--range",
        "--output-file",
        "-o",
    }
)
_RUFF_FLAG_OPTIONS = frozenset(
    {
        "--fix",
        "--no-fix",
        "--fix-only",
        "--no-fix-only",
        "--unsafe-fixes",
        "--no-unsafe-fixes",
        "--show-fixes",
        "--no-show-fixes",
        "--diff",
        "--check",
        "--watch",
        "-w",
        "--ignore-noqa",
        "--preview",
        "--no-preview",
        "--statistics",
        "--show-files",
        "--show-settings",
        "--respect-gitignore",
        "--no-respect-gitignore",
        "--force-exclude",
        "--no-force-exclude",
        "--no-cache",
        "-n",
        "--exit-zero",
        "-e",
        "--exit-non-zero-on-fix",
        "--verbose",
        "-v",
        "--quiet",
        "-q",
        "--silent",
        "-s",
        "--isolated",
        "--help",
        "-h",
        "--add-noqa",
    }
)


def _ruff_effects(root: Path, command: str) -> tuple[list[str], bool] | None:
    """Identify Ruff's possible source and report writes without executing it.

    Configuration can enable fixes, so a plain check is not proof of read-only
    behavior. Unknown options or compound commands lack a complete target set.
    Ruff's disposable cache is not reviewed work product.
    """
    stages = _split_pipeline_stages(command)
    for stage in stages:
        nested, wrapper = _nested_shell_command(stage)
        if wrapper:
            if nested and nested != command and _ruff_effects(root, nested) is not None:
                return [], True  # Wrapper environment/cwd is not the supplied tool cwd.
            continue
        tokens = _shell_split(stage)
        if not tokens:
            continue
        verb_index = _shell_verb_index(tokens)
        if verb_index is None:
            continue
        relevant = tokens[verb_index:]
        executable = _executable_name(relevant[0])
        if executable in {"ruff", "ruff.exe"}:
            args = relevant[1:]
        elif (executable in _PYTHON_EXECUTABLE_NAMES or executable.startswith("python")) and relevant[1:3] == [
            "-m",
            "ruff",
        ]:
            args = relevant[3:]
        else:
            continue
        if (
            len(stages) != 1
            or verb_index
            or _has_disqualifying_control_marker(command)
            or _shell_redirect_present(command)
        ):
            return [], True
        if not args or args[0] not in {"check", "format"}:
            return [], True
        subcommand, *args = args
        flags: set[str] = set()
        sources: list[str] = []
        output = os.environ.get("RUFF_OUTPUT_FILE") if subcommand == "check" else None
        output_shell_quoted = False
        index = 0
        while index < len(args):
            token = args[index]
            if token == "--":
                sources.extend(args[index + 1 :])
                break
            option, separator, value = token.partition("=")
            if option in _RUFF_VALUE_OPTIONS:
                if not separator:
                    index += 1
                    if index >= len(args):
                        return [], True
                    value = args[index]
                if option in {"--output-file", "-o"}:
                    output = value
                    output_shell_quoted = True
            elif option in _RUFF_FLAG_OPTIONS and (not separator or option == "--add-noqa"):
                flags.add(option)
            elif token.startswith("-"):
                return [], True
            else:
                sources.append(token)
            index += 1
        if flags & {"--help", "-h"}:
            return [], False
        read_only = "--diff" in flags or (
            "--check" in flags if subcommand == "format" else {"--no-fix", "--no-fix-only"} <= flags
        )
        # Do not infer precedence among conflicting write/read modifiers.
        if "--add-noqa" in flags or ("--diff" not in flags and flags & {"--fix", "--fix-only"}):
            read_only = False
        if not read_only and not sources:
            return [], True  # An implicit recursive '.' is not a concrete artifact.
        targets = [] if read_only else sources
        paths = [_normalize(root, target, shell_quoted=True) for target in targets]
        if output:
            paths.append(_normalize(root, output, shell_quoted=output_shell_quoted))
        if any(not path for path in paths):
            return [], True
        return sorted(set(paths)), bool(paths)
    return None


# WI-6674: help output is read-only, but the WI-3291 prefix allowlist cannot
# express it. That allowlist enumerates command VERBS, and a help request is
# identified by its FLAG -- the verb is an arbitrary governed CLI. Every such
# invocation therefore fell through to `<unknown-mutating-target>` and was
# denied.
_HELP_ONLY_FLAGS = frozenset({"--help", "--usage"})

# Redirection is checked here rather than inherited: the caller's
# `_has_disqualifying_control_marker` models chaining and command substitution
# but NOT redirection, so `<cli> --help > out.txt` would otherwise write a file
# under a read-only exemption.
_REDIRECTION_MARKERS = (">", ">>")


def _requests_help_output_only(command: str, normalized_tokens: list[str]) -> bool:
    """True iff this single stage only asks a command to print its usage text.

    Deliberately narrow. Only the unambiguous long flags qualify; ``-h`` is
    excluded because it is a real operation modifier for some verbs (``chown
    -h``, ``chmod -h``) and admitting it would exempt genuine mutations.

    Chaining, execution markers, and multi-stage commands are already rejected
    by the caller before this runs, so those guards are inherited rather than
    re-implemented. Redirection is not, and is rejected here.
    """
    if not any(token in _HELP_ONLY_FLAGS for token in normalized_tokens):
        return False
    redirect_view = _mask_quoted_spans(command, mask_double=True)
    return not any(marker in redirect_view for marker in _REDIRECTION_MARKERS)


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

    if tool in {"write", "edit", "strreplace", "multiedit", "notebookedit", "delete"}:
        if not isinstance(data, dict):
            return [], True
        path = data.get("file_path") or data.get("notebook_path") or data.get("path")
        rel = _normalize(root, str(path)) if path else None
        return ([rel] if rel else []), True

    if tool in {"move", "copy"}:
        # No supported native payload identifies both paths for these tools.
        # Use an explicit shell/CLI operation instead of checking only one side.
        return [], True

    if _is_apply_patch_tool(tool) or any("*** Begin Patch" in value for value in _string_values(payload)):
        text = _apply_patch_text(payload, data)
        return _paths_from_apply_patch(root, text), True

    command = _command_from_payload(payload, data, tool)
    if command is not None:
        ruff_effects = _ruff_effects(root, command)
        if ruff_effects is not None:
            return ruff_effects
        if _is_safe_command(command):
            return [], False
        diagnostic_outputs = _diagnostic_output_paths_from_shell(root, command)
        if diagnostic_outputs is not None:
            return diagnostic_outputs, True
        paths = _paths_from_shell(root, command)
        return paths, _is_mutating_command(command)

    return [], False


def gate_decision(payload: dict[str, Any]) -> dict[str, Any]:
    """Route actual mutating targets through the CLI; never consult legacy packets."""

    def blocked(code: str, reason: str) -> dict[str, Any]:
        return {"decision": "block", "reason_code": code, "reason": reason}

    invalid = payload.get(INVALID_HOOK_PAYLOAD_KEY)
    if invalid:
        return blocked("invalid_hook_payload", "Cannot identify the tool effect from the supplied payload.")
    direct_git = _direct_git_effect_from_payload(payload)
    if direct_git is not None:
        return blocked(
            "direct_git_effect_requires_lifecycle",
            "Use the ordinary gt project commit or gt bridge worktree/publish-work operation for Git effects.",
        )
    root = _project_root(payload)
    cwd = Path(str(payload.get("cwd") or root)).absolute()
    paths, mutating = changed_paths({**payload, "project_root": str(cwd)})
    if not mutating:
        return {}
    if not paths:
        return blocked("unknown_effect_targets", "Use an explicit tool target or the ordinary CLI for this effect.")
    native = str(os.environ.get("GTKB_NATIVE_CONTEXT_ID") or payload.get("session_id") or "").strip()
    supplied = str(payload.get("session_id") or "").strip()
    if not native or (supplied and supplied != native):
        return blocked("invalid_native_context", "The tool must carry the current harness-native context identifier.")
    argv = [
        sys.executable,
        "-m",
        "groundtruth_kb",
        "bridge",
        "check-effects",
        "--native-context-id",
        native,
        "--cwd",
        str(cwd),
        "--json",
    ]
    for path in paths:
        argv.extend(["--path", path])
    env = dict(os.environ)
    env["GT_PROJECT_ROOT"] = str(root)
    env["PYTHONIOENCODING"] = "utf-8"
    try:
        result = subprocess.run(
            argv,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if result.returncode:
            return blocked(
                "native_effect_refused", result.stderr.strip()[:2000] or "The native CLI refused the effect check."
            )
        current = json.loads(result.stdout)
        if (
            not isinstance(current, dict)
            or current.get("status") != "current"
            or current.get("scope") not in {"scratch", "implementation"}
        ):
            return blocked("invalid_effect_response", "The native CLI did not return a current effect check.")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return blocked(
            "effect_check_unavailable", "Restore the native CLI/authority connection before retrying this effect."
        )
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
