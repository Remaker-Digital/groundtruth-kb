"""Shared validation logic for directive enforcement (DIR-ROOT-BOUNDARY-001 etc.)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

# Common patterns for parsing commands
REDIRECTION_RE = re.compile(r"(?:>|>>|<|\|)\s*([^\s|&;]+)")
PATH_DELIMITER_RE = re.compile(r"[\"']?([a-zA-Z]:\\[^\s|&;'\"]+|/[^\s|&;'\"]+)[\"']?")


class DirectiveEnforcementError(ValueError):
    """Raised when a path or command violates directive enforcement rules."""


def load_directives(project_root: Path) -> list[dict]:
    registry_file = project_root / ".gtkb" / "directive-registry.json"
    if not registry_file.is_file():
        return []
    try:
        data = json.loads(registry_file.read_text(encoding="utf-8"))
        return data.get("directives", [])
    except Exception:
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
    except Exception as exc:
        return False, f"Path '{path_str}' could not be resolved: {exc}"

    candidate_norm = os.path.normpath(str(candidate)).lower()
    allowed_norm = os.path.normpath(str(allowed_root)).lower()

    # 1. Check blocked_absolute
    for blocked in blocked_absolute:
        blocked_norm = os.path.normpath(blocked).lower()
        if candidate_norm.startswith(blocked_norm):
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

    Scans for output redirections or absolute path arguments referencing blocked paths.
    """
    # 1. Extract paths from output redirection
    for match in REDIRECTION_RE.finditer(command):
        target_path = match.group(1).strip().strip("\"'")
        # If the path looks like a flag or command, skip
        if target_path.startswith("-"):
            continue
        allowed, reason = check_path_boundary(target_path, project_root)
        if not allowed:
            return False, f"Command contains blocked redirection target: {reason}"

    # 2. Scan command for any absolute path arguments
    for match in PATH_DELIMITER_RE.finditer(command):
        potential_path = match.group(1).strip()
        allowed, reason = check_path_boundary(potential_path, project_root)
        if not allowed:
            return False, f"Command contains blocked path argument: {reason}"

    return True, ""
