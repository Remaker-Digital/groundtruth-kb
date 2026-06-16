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
#   - drive-letter absolute  C:\foo  or  C:/foo
#   - UNC                     \\host\share
#   - rooted '/...'           but ONLY at a token boundary (negative lookbehind on
#                             a word char or '.') so 'scripts/foo' is not captured.
# Per-match classification in _classify_path_token() then skips null sinks and
# URL ('://') context, translates MSYS '/c/...' to 'C:\...', and resolves a
# rooted-driveless '/foo' as PROJECT-root-relative (the HYG-042 owner decision).
_DRIVE_ABSOLUTE = r"[A-Za-z]:[\\/][^\s|&;'\"]*"
_UNC_ABSOLUTE = r"\\\\[^\s|&;'\"]+"
_ROOTED = r"(?<![\w.])/[^\s|&;'\"]*"
PATH_DELIMITER_RE = re.compile(rf"[\"']?({_DRIVE_ABSOLUTE}|{_UNC_ABSOLUTE}|{_ROOTED})[\"']?")

# Null sinks are always allowed regardless of root (HYG-042 owner decision).
_NULL_SINKS = frozenset({"/dev/null", "/dev/stdout", "/dev/stderr", "nul"})

# MSYS / Git-Bash drive form: /c/Users/... -> C:\Users\...
_MSYS_PATH_RE = re.compile(r"^/([a-zA-Z])/(.*)$")


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
    if not token:
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
        return token
    if token.startswith("/"):  # rooted-driveless -> project-root-relative
        if token.lower().startswith(("/etc/", "/home/")):
            return token
        return token.lstrip("/")
    return None  # relative path / flag / bare word — not a boundary risk


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

    # 2. Scan command for genuine absolute path arguments
    for match in PATH_DELIMITER_RE.finditer(command):
        classified = _classify_path_token(match.group(1))
        if classified is None:
            continue
        allowed, reason = check_path_boundary(classified, project_root)
        if not allowed:
            return False, f"Command contains blocked path argument: {reason}"

    return True, ""
