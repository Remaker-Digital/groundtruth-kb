"""Hook interpreter resolution must never depend on PATH, and hook scripts
must never be directly executable.

Source: advisory ``gtkb-advisory-hook-interpreter-fail-open-20260823`` and the
2026-08-23 owner-directed emergency repair.

Two failure routes were identified:

* Route one (shebang). ``#!/usr/bin/env python3`` fires only when a script is
  executed as a program. On this workstation ``python3`` resolves to a Windows
  Store app-execution alias which prints a diagnostic and exits 0. The shebang
  token itself is CORRECT under PEP 394 and must not be rewritten to
  ``python`` -- that would break POSIX adopters where ``python`` is absent.
  The route is instead closed by the property that no tracked file is recorded
  executable, so direct execution is impossible on a clean checkout.
  ``test_no_tracked_file_is_executable`` locks that property.

* Route two (bare interpreter name). The projector emitted ``pythonw "..."``
  by bare name, so a session whose PATH placed the Store alias directory ahead
  of the real interpreter ran the alias, which exits 0. The harness read exit 0
  as a successful hook run and the whole governance gate stack failed open
  silently. ``test_projected_registrations_use_absolute_interpreter`` and
  ``test_projected_interpreters_exist`` lock the fix.

The defect survived because registrations were checked for SHAPE but never for
RUNNABILITY. These assertions are deterministic and independent of PATH.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Projection directories that may carry a harness hook registration.
PROJECTION_DIRS = (
    ".claude",
    ".codex",
    ".cursor",
    ".goose",
    ".agent",
    ".agents",
    ".api-harness",
    ".antigravity",
)
# Registration filenames differ per harness: Claude and Codex use settings.json,
# Cursor and Goose use hooks.json. Both are probed in every projection dir
# rather than pinned per harness -- an earlier revision of this test hardcoded
# `.codex/hooks.json` and consequently passed while `.codex/settings.json`
# carried five bare-`pythonw` commands. Discover, never assume.
REGISTRATION_FILENAMES = ("settings.json", "hooks.json")

_BARE_INTERPRETER = re.compile(r"^\s*\"?(python|pythonw|python3|py)(\.exe)?\"?\s", re.IGNORECASE)
# A leading quoted absolute path, e.g.  "E:\...\pythonw.exe" "..."
_LEADING_QUOTED_PATH = re.compile(r'^\s*"([^"]+)"')


def _walk_commands(node: object, surface: str, found: list[tuple[str, str]]) -> None:
    """Collect every ``command`` string anywhere in a registration payload.

    Module-level rather than a closure so it never captures a loop variable
    (ruff B023): registration schemas differ per harness, so the traversal is
    shape-agnostic by design.
    """
    if isinstance(node, dict):
        command = node.get("command")
        if isinstance(command, str) and command.strip():
            found.append((surface, command))
        for value in node.values():
            _walk_commands(value, surface, found)
    elif isinstance(node, list):
        for value in node:
            _walk_commands(value, surface, found)


def _iter_commands() -> list[tuple[str, str]]:
    """Return (surface, command) for every hook command in every registration."""
    found: list[tuple[str, str]] = []
    for directory in PROJECTION_DIRS:
        for filename in REGISTRATION_FILENAMES:
            rel = f"{directory}/{filename}"
            path = PROJECT_ROOT / directory / filename
            if not path.is_file():
                continue
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            _walk_commands(payload, rel, found)
    return found


def test_registration_surfaces_are_discoverable() -> None:
    """Guard the guard: if nothing is found the other tests vacuously pass."""
    commands = _iter_commands()
    assert commands, (
        "no hook commands found in any registration surface "
        f"across {PROJECTION_DIRS}; the interpreter assertions below "
        "would pass vacuously"
    )


def test_projected_registrations_use_absolute_interpreter() -> None:
    offenders = [f"{surface}: {command}" for surface, command in _iter_commands() if _BARE_INTERPRETER.match(command)]
    assert not offenders, (
        "hook registrations resolve their interpreter by bare name. On Windows a "
        "bare python/pythonw/python3 can resolve to a Microsoft Store alias that "
        "exits 0, so the harness records the hook as having run when it never "
        "executed and the gate stack fails open silently:\n  " + "\n  ".join(offenders)
    )


def test_projected_interpreters_exist() -> None:
    """A registration naming an interpreter that is not on disk cannot run."""
    missing: list[str] = []
    for surface, command in _iter_commands():
        match = _LEADING_QUOTED_PATH.match(command)
        if match is None:
            continue
        interpreter = Path(match.group(1))
        if not interpreter.is_absolute():
            continue
        if not interpreter.is_file():
            missing.append(f"{surface}: {interpreter}")
    assert not missing, "hook registrations name an interpreter that does not exist on disk:\n  " + "\n  ".join(missing)


def test_no_tracked_file_is_executable() -> None:
    """Closes the shebang route by construction.

    ``#!/usr/bin/env python3`` can only fire if the file is executed as a
    program. No tracked file is recorded mode 100755, so a clean checkout
    cannot execute one directly. Note that ``ls`` on Windows reports
    ``-rwxr-xr-x`` for these files -- that is an MSYS display artifact of
    filesystem ACLs, not the tracked mode, and must not be mistaken for the
    executable bit.
    """
    result = subprocess.run(
        ["git", "ls-files", "-s"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"git ls-files unavailable: {result.stderr.strip()[:200]}")

    executable = [line.split("\t", 1)[-1] for line in result.stdout.splitlines() if line.startswith("100755 ")]
    assert not executable, (
        "tracked files are recorded executable (mode 100755). Any such file "
        "carrying `#!/usr/bin/env python3` becomes directly runnable, and on a "
        "workstation without a real python3 the shebang resolves to a Store "
        "alias that exits 0 -- a silent no-op:\n  " + "\n  ".join(executable[:20])
    )
