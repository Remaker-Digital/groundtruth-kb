"""Fail-closed Bash bridge-mutation detector for SDK harnesses."""

from __future__ import annotations

import re

_PROTECTED_BRIDGE_PATH_PATTERN = (
    r"(?:[A-Za-z]:)?"
    r"(?:[\\/]|[\w .-]+[\\/])*"
    r"bridge[\\/](?:INDEX\.md|[A-Za-z0-9_.-]+\.md)"
)

_PROTECTED_BRIDGE_PATH_RE = re.compile(_PROTECTED_BRIDGE_PATH_PATTERN, re.IGNORECASE)
_REDIRECT_TO_BRIDGE_RE = re.compile(
    rf"(?:^|[\s;&|])(?:\d?>{{1,2}}|>{{1,2}})\s*['\"]?{_PROTECTED_BRIDGE_PATH_PATTERN}",
    re.IGNORECASE,
)
_MUTATING_COMMAND_RE = re.compile(
    r"\b(?:"
    r"set-content|add-content|out-file|new-item|copy-item|move-item|rename-item|remove-item|clear-content|"
    r"tee-object|sc|ac|ni|cp|mv|rm|ri|del|erase|copy|move|touch|tee"
    r")\b"
    r"|\bsed\s+-i\b"
    r"|\bperl\s+-pi\b"
    r"|\bgit\s+(?:checkout|restore|apply)\b"
    r"|\bpatch\b",
    re.IGNORECASE,
)
_SCRIPT_MUTATION_RE = re.compile(
    r"write_text\s*\("
    r"|write_bytes\s*\("
    r"|open\s*\([^)]*['\"][wax][+b]?['\"]"
    r"|shutil\.(?:copy|copy2|move)\s*\("
    r"|os\.(?:remove|rename|replace|unlink)\s*\("
    r"|\.(?:unlink|rename|replace|touch)\s*\(",
    re.IGNORECASE | re.DOTALL,
)


def protected_bridge_paths(command: str) -> tuple[str, ...]:
    """Return protected bridge paths mentioned by a shell command."""
    if not command:
        return ()
    seen: dict[str, str] = {}
    for match in _PROTECTED_BRIDGE_PATH_RE.finditer(command):
        path = match.group(0).strip("\"'`")
        key = path.replace("\\", "/").lower()
        seen.setdefault(key, path)
    return tuple(seen.values())


def bridge_bash_mutation_reason(command: str) -> str | None:
    """Return a denial reason when ``command`` mutates bridge artifacts."""
    paths = protected_bridge_paths(command)
    if not paths:
        return None
    if not (
        _REDIRECT_TO_BRIDGE_RE.search(command)
        or _MUTATING_COMMAND_RE.search(command)
        or _SCRIPT_MUTATION_RE.search(command)
    ):
        return None
    listed = ", ".join(paths)
    return (
        f"Bash bridge artifact mutation denied for {listed}. "
        "Use guarded Write/Edit dispatch or the scripts/gtkb_bridge_writer.py helper path "
        "for bridge/*.md and bridge/INDEX.md."
    )
