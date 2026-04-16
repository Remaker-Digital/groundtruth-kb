# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bash command mutation classifier for governance hooks."""

from __future__ import annotations

import re

MUTATION_PATTERNS: list[tuple[str, str]] = [
    (r">\s*\S+", "shell output redirection (>)"),
    (r">>\s*\S+", "shell append redirection (>>)"),
    (r"\btee\b", "tee command"),
    (r"\bcp\b", "cp command"),
    (r"\bmv\b", "mv command"),
    (r"\bsed\s+-i\b", "sed -i (in-place edit)"),
    (r"\bawk\s+-i\b", "awk -i (in-place edit)"),
    (r"\bSet-Content\b", "PowerShell Set-Content"),
    (r"\bAdd-Content\b", "PowerShell Add-Content"),
    (r"\bOut-File\b", "PowerShell Out-File"),
    (r"""python\s+-c\s+['"].*open\s*\(""", "Python one-liner file write"),
    (r"""python\s+-c\s+['"].*write\s*\(""", "Python one-liner file write"),
    (r"""node\s+-e\s+['"].*writeFile""", "Node.js writeFile one-liner"),
    (r"""node\s+-e\s+['"].*writeFileSync""", "Node.js writeFileSync one-liner"),
    (r"\bperl\s+-i\b", "perl -i (in-place edit)"),
    (r"""\bruby\s+-i\b""", "ruby -i (in-place edit)"),
]

SOURCE_DIRS = ("src/", "lib/", "groundtruth_kb/", "tests/")


def is_source_path(path: str) -> bool:
    """Return True if path is under a recognized source directory."""
    return any(path.startswith(d) for d in SOURCE_DIRS)


def classify_bash_command(command: str) -> list[str]:
    """Return list of mutation descriptions found in command. Empty list means safe."""
    found = []
    for pattern, description in MUTATION_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            found.append(description)
    return found
