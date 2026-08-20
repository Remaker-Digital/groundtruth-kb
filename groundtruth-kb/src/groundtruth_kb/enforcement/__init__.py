"""Shared validation logic for directive enforcement (DIR-ROOT-BOUNDARY-001 etc.)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

# Common patterns for parsing commands
REDIRECTION_RE = re.compile(r"(?:>|>>|<|\|)\s*([^\s|&;]+)")

# HYG-042 (FAB-14): match only GENUINE absolute-path candidates so a relative
# 'dir/file' token is not mis-read as an out-of-root '/file'. Three alternatives:
#   - drive-letter absolute  C:\foo  or  C:/foo, but only at a token
#                             boundary so prose/regex snippets like
#                             'Document:\s*' do not become 't:\s*'
#   - UNC                     \\host\share
#   - rooted '/...'           but ONLY at a token boundary (negative lookbehind on
#                             a word char, '.', ':', or '/') so 'scripts/foo' and
#                             'https://example.com/path' are not captured.
# Per-match classification in _classify_path_token() then skips null sinks and
# URL ('://') context, translates MSYS '/c/...' to 'C:\...', and resolves a
# rooted-driveless '/foo' as PROJECT-root-relative (the HYG-042 owner decision).
_DRIVE_ABSOLUTE = r"(?<![\w.])[A-Za-z]:[\\/][^\s|&;'\"]*"
_UNC_ABSOLUTE = r"\\\\[\w.-]+[\\/][^\s|&;'\"]+"
_ROOTED = r"(?<![\w.:/])/[^\s|&;'\"]*"
PATH_DELIMITER_RE = re.compile(rf"[\"']?({_DRIVE_ABSOLUTE}|{_UNC_ABSOLUTE}|{_ROOTED})[\"']?")

# Null sinks are always allowed regardless of root (HYG-042 owner decision).
_NULL_SINKS = frozenset({"/dev/null", "/dev/stdout", "/dev/stderr", "nul"})

# MSYS / Git-Bash drive form: /c/Users/... -> C:\Users\...
_MSYS_PATH_RE = re.compile(r"^/([a-zA-Z])/(.*)$")
_COMMAND_SEGMENT_RE = re.compile(r"(?:&&|\|\||[;|\r\n])")
_COMMAND_TOKEN_RE = re.compile(r"\"([^\"]*)\"|'([^']*)'|([^\s]+)")
# WI-6026 / WI-6674: options whose values are free text, regex patterns, or
# inline scripts drawn from governed CLI and standard shell tools. A path-shaped
# token inside one of these values is being described or evaluated as pattern/code,
# not operated on as a filesystem path, so it is excluded from boundary checking.
_FREE_TEXT_OPTIONS = frozenset(
    {
        "--description",
        "--change-reason",
        "--status-detail",
        "--summary",
        "--title",
        "--reason",
        "--note",
        "--test-expected-outcome",
        "--scope",
        "-m",
        "--message",
        "-e",
        "--expression",
        "--regexp",
        "-c",
        "--command",
        "-E",
        "-P",
    }
)
_ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=(?:\"[^\"]*\"|'[^']*'|\S+)$")
# PowerShell assignment form (`$env:VAR='value'`). Without this, the whole
# assignment stays one token and `_command_name` derives the head from the
# VALUE's last path segment -- so a value ending in a harness name (e.g.
# `prime-builder/claude`) is misread as a direct harness launch (WI-5676).
_PS_ENV_ASSIGNMENT_RE = re.compile(r"^\$env:[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?:\"[^\"]*\"|'[^']*'|\S+)$", re.IGNORECASE)
_DIRECT_HARNESS_COMMANDS = frozenset(
    {
        "agy",
        "antigravity",
        "claude",
        "cursor",
        "cursor-agent",
        "gemini",
        "ollama",
        "openrouter",
        "openrouter-harness",
    }
)
_DIRECT_CODEX_COMMAND = "codex"
_DIRECT_HARNESS_SCRIPT_SHIMS = frozenset(
    {
        "_bootstrap_cursor_harness.py",
        "cursor_harness.py",
        "ollama_harness.py",
        "openrouter_harness.py",
    }
)
_DIRECT_GTKB_HELPER_SCRIPT_MARKERS = (
    ".claude/hooks/",
    ".claude/skills/",
    ".codex/gtkb-hooks/",
    ".codex/skills/",
    ".cursor/skills/",
)
_PYTHON_COMMANDS = frozenset({"py", "python", "python3", "pythonw"})
_DIRECT_HARNESS_DENIAL = (
    "Direct harness-to-harness launch is prohibited by SPEC-INTAKE-21c5b3 / "
    "DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN; use bridge files, `gt bridge dispatch` "
    "control-plane status/config surfaces, or independent owner/manual harness operation."
)
_DIRECT_HELPER_SCRIPT_DENIAL = (
    "Direct GT-KB Python helper script execution is prohibited by SPEC-INTAKE-21c5b3 / "
    "DELIB-20260703-DIRECT-HARNESS-INVOKE-BAN because Windows file association can launch "
    "a GUI harness. Invoke helper scripts through an explicit Python executable or governed "
    "no-window wrapper instead."
)


def _classify_path_token(token: str) -> str | None:
    """Classify a path-like token for boundary checking (HYG-042 / FAB-14).

    Returns the path string to boundary-check, or None to SKIP (the token is not
    a genuine absolute-path concern: a relative path, a flag, a URL, or a null
    sink). Genuine absolutes (drive-letter, UNC) are returned as-is; an MSYS
    '/c/..' token is translated to a Windows drive path; a rooted-driveless
    '/foo' is returned as a project-root-relative path so it resolves INSIDE the
    root rather than being mis-read as an out-of-root absolute.
    """
    token = token.strip().strip("\"'")
    if not token or all(c in "./\\" for c in token):
        return None
    if token.lower() in _NULL_SINKS:
        return None
    if "://" in token:  # scheme://... — a URL, not a filesystem path
        return None
    msys = _MSYS_PATH_RE.match(token)
    if msys:
        return msys.group(1).upper() + ":\\" + msys.group(2).replace("/", "\\")
    if re.match(r"^[A-Za-z]:[\\/]", token):  # drive-letter absolute (C:\ or C:/)
        return token
    if token.startswith("\\\\") or token.startswith("//"):  # UNC (both slash forms)
        # require a separator after the host part to filter out double-slashes/comments
        remainder = token[2:]
        if not ("\\" in remainder or "/" in remainder):
            return None
        return token
    if token.startswith("/"):  # rooted-driveless -> project-root-relative
        # WI-6674: regex patterns and address expressions (e.g. /pattern/, /[^/]+/, /[a-z]/)
        # are not filesystem paths.
        if any(c in token for c in "^$*+?|{}[]\\") or (token.count("/") >= 2 and token.endswith("/")):
            return None
        if token.lower().startswith(("/etc/", "/home/")):
            return token
        return token.lstrip("/")
    return None  # relative path / flag / bare word — not a boundary risk


def _command_tokens(segment: str) -> list[str]:
    return [
        next(group for group in match.groups() if group is not None) for match in _COMMAND_TOKEN_RE.finditer(segment)
    ]


def _token_basename(token: str) -> str:
    cleaned = token.strip().strip("\"'`").lstrip("&").strip("\"'`")
    return cleaned.replace("\\", "/").rsplit("/", 1)[-1].lower()


def _command_name(token: str) -> str:
    name = _token_basename(token)
    for suffix in (".exe", ".cmd", ".bat", ".ps1"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _drop_leading_assignments(tokens: list[str]) -> list[str]:
    remaining = list(tokens)
    while remaining and remaining[0].strip() == "&":
        remaining = remaining[1:]
    if remaining and _command_name(remaining[0]) == "env":
        remaining = remaining[1:]
    while remaining and (
        _ENV_ASSIGNMENT_RE.match(remaining[0].strip()) or _PS_ENV_ASSIGNMENT_RE.match(remaining[0].strip())
    ):
        remaining = remaining[1:]
    return remaining


def _module_or_script_name(token: str) -> str:
    basename = _token_basename(token)
    if "." in basename and not basename.endswith(".py"):
        basename = basename.rsplit(".", 1)[-1] + ".py"
    return basename


def _is_direct_gtkb_helper_script(token: str) -> bool:
    normalized = token.strip().strip("\"'`").lstrip("&").strip("\"'`").replace("\\", "/").lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if not normalized.endswith(".py"):
        return False
    return any(
        normalized.startswith(marker) or f"/{marker}" in normalized for marker in _DIRECT_GTKB_HELPER_SCRIPT_MARKERS
    )


def _python_invokes_direct_harness_shim(tokens: list[str]) -> bool:
    index = 1
    while index < len(tokens):
        token = tokens[index]
        if token == "-m" and index + 1 < len(tokens):
            return _module_or_script_name(tokens[index + 1]) in _DIRECT_HARNESS_SCRIPT_SHIMS
        if token.startswith("-"):
            index += 1
            continue
        return _module_or_script_name(token) in _DIRECT_HARNESS_SCRIPT_SHIMS
    return False


def _token_starts_with_exec(token: str) -> bool:
    value = token.strip().strip("\"'`").lower()
    return value == "exec" or value.startswith("exec ")


def _codex_exec_requested(tokens: list[str]) -> bool:
    return any(_token_starts_with_exec(token) for token in tokens)


def _start_process_target(tokens: list[str]) -> tuple[str, list[str]]:
    for index, token in enumerate(tokens):
        lower = token.strip().lower()
        if lower in {"-filepath", "-file"} and index + 1 < len(tokens):
            return tokens[index + 1], tokens[index + 2 :]
        if lower.startswith("-filepath="):
            return token.split("=", 1)[1], tokens[index + 1 :]
        if not lower.startswith("-"):
            return token, tokens[index + 1 :]
    return "", []


def _direct_harness_launch_reason(command: str) -> str | None:
    """Return a denial reason when interactive shell text directly launches a harness."""
    for raw_segment in _COMMAND_SEGMENT_RE.split(command):
        segment = raw_segment.strip()
        if not segment:
            continue
        tokens = _drop_leading_assignments(_command_tokens(segment))
        if not tokens:
            continue
        head = _command_name(tokens[0])
        if _is_direct_gtkb_helper_script(tokens[0]):
            return _DIRECT_HELPER_SCRIPT_DENIAL
        if head in _DIRECT_HARNESS_COMMANDS:
            return _DIRECT_HARNESS_DENIAL
        if head == _DIRECT_CODEX_COMMAND and len(tokens) > 1 and _token_starts_with_exec(tokens[1]):
            return _DIRECT_HARNESS_DENIAL
        if head in _PYTHON_COMMANDS and _python_invokes_direct_harness_shim(tokens):
            return _DIRECT_HARNESS_DENIAL
        if head == "start-process":
            target, rest = _start_process_target(tokens[1:])
            target_head = _command_name(target)
            if _is_direct_gtkb_helper_script(target):
                return _DIRECT_HELPER_SCRIPT_DENIAL
            if target_head in _DIRECT_HARNESS_COMMANDS:
                return _DIRECT_HARNESS_DENIAL
            if target_head == _DIRECT_CODEX_COMMAND and _codex_exec_requested(rest):
                return _DIRECT_HARNESS_DENIAL
    return None


class DirectiveEnforcementError(ValueError):
    """Raised when a path or command violates directive enforcement rules."""


def load_directives(project_root: Path) -> list[dict[str, Any]]:
    registry_file = project_root / ".gtkb" / "directive-registry.json"
    if not registry_file.is_file():
        return []
    try:
        data = json.loads(registry_file.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            directives = data.get("directives", [])
            if isinstance(directives, list):
                return [d for d in directives if isinstance(d, dict)]
        return []
    except Exception:  # intentional-catch: load directives default fallback
        return []


def check_path_boundary(path_str: str, project_root: Path) -> tuple[bool, str]:
    """Check if the given path violates DIR-ROOT-BOUNDARY-001.

    Returns (allowed, reason_if_blocked).
    """
    directives = load_directives(project_root)
    boundary = next((d for d in directives if d.get("id") == "DIR-ROOT-BOUNDARY-001"), None)
    if not boundary:
        # Fallback default boundary if registry file is missing/corrupt
        allowed_root = str(project_root)
        blocked_absolute = ["C:\\Users\\", "/etc/", "/home/"]
    else:
        patterns = boundary.get("patterns", {})
        allowed_root = patterns.get("allowed_root", str(project_root))
        blocked_absolute = patterns.get("blocked_absolute", [])

    try:
        candidate = Path(path_str)
        # If relative, resolve against project_root
        candidate = (project_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
    except Exception as exc:  # intentional-catch: path resolution fallback
        return False, f"Path '{path_str}' could not be resolved: {exc}"

    # Allow harness-specific paths (e.g. settings, plugins, logs)
    if any(part.lower() in {".claude", ".codex", ".gemini", ".api-harness"} for part in candidate.parts):
        return True, ""

    candidate_norm = os.path.normpath(str(candidate)).lower()
    allowed_norm = os.path.normpath(str(allowed_root)).lower()

    # 1. Check blocked_absolute
    for blocked in blocked_absolute:
        blocked_norm = os.path.normpath(blocked).lower()
        if candidate_norm.startswith(blocked_norm):
            return False, f"Path '{path_str}' resolves to blocked location under '{blocked}'"
        # Also check direct prefix match on raw path_str in case it's rooted-driveless on Windows
        p_str_clean = path_str.lower().replace("\\", "/")
        b_clean = blocked.lower().replace("\\", "/")
        if p_str_clean.startswith(b_clean):
            return False, f"Path '{path_str}' resolves to blocked location under '{blocked}'"

    # 2. Check allowed_root
    # Candidate must be exactly the allowed root or a child of it
    if not (
        candidate_norm == allowed_norm
        or candidate_norm.startswith(allowed_norm + os.sep)
        or candidate_norm.startswith(allowed_norm + "/")
    ):
        return False, f"Path '{path_str}' resolves outside allowed root '{allowed_root}'"

    return True, ""


def check_bash_command(command: str, project_root: Path) -> tuple[bool, str]:
    """Check a bash/powershell command for boundary violations.

    Scans for output redirections or absolute path arguments referencing blocked
    paths. Per HYG-042 (FAB-14), only GENUINE absolute paths are flagged: relative
    paths, URLs, and null sinks pass; MSYS '/c/..' is translated to a drive path;
    a rooted-driveless '/foo' is treated as project-root-relative.
    """
    direct_harness_reason = _direct_harness_launch_reason(command)
    if direct_harness_reason is not None:
        return False, direct_harness_reason

    # 1. Extract paths from output redirection
    for match in REDIRECTION_RE.finditer(command):
        target_path = match.group(1).strip().strip("\"'")
        # If the path looks like a flag or command, skip
        if target_path.startswith("-"):
            continue
        classified = _classify_path_token(target_path)
        if classified is None:
            continue
        allowed, reason = check_path_boundary(classified, project_root)
        if not allowed:
            return False, f"Command contains blocked redirection target: {reason}"

    # 2. Scan command for genuine absolute path operands.
    #
    # WI-6026: this pass is argument-role aware. Previously it scanned the raw
    # command string, so a path-shaped token appearing inside a free-text option
    # value -- a `--description`, a `--change-reason` -- was treated identically
    # to a path the command would actually operate on. Describing an out-of-root
    # path counted as using one. Only operand tokens are boundary-checked now;
    # the values of the free-text options below are excluded. This narrows what
    # is inspected, never what is permitted: an out-of-root path supplied as an
    # operand is still refused.
    for raw_segment in _COMMAND_SEGMENT_RE.split(command):
        skip_next_token = False
        tokens = _drop_leading_assignments(_command_tokens(raw_segment))
        if not tokens:
            continue
        cmd_head = _command_name(tokens[0])
        is_pattern_cmd = cmd_head in {"sed", "awk", "grep", "egrep", "fgrep", "rg"}
        has_explicit_script_flag = any(
            t in {"-e", "-f", "--expression", "--file", "--regexp"} or t.startswith(("-e", "-f")) for t in tokens[1:]
        )
        pattern_arg_consumed = has_explicit_script_flag

        for token in tokens[1:]:
            if skip_next_token:
                skip_next_token = False
                continue
            if token in _FREE_TEXT_OPTIONS:
                skip_next_token = True
                continue
            option_name, separator, _ = token.partition("=")
            if separator and option_name in _FREE_TEXT_OPTIONS:
                continue
            if token.startswith("-"):
                continue
            if is_pattern_cmd and not pattern_arg_consumed:
                pattern_arg_consumed = True
                continue

            for path_match in PATH_DELIMITER_RE.finditer(token):
                classified = _classify_path_token(path_match.group(1))
                if classified is None:
                    continue
                allowed, reason = check_path_boundary(classified, project_root)
                if not allowed:
                    return False, f"Command contains blocked path argument: {reason}"

    return True, ""
