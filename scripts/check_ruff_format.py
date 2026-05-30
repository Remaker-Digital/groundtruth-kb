#!/usr/bin/env python3
"""Pre-commit guardrail: ``ruff format --check`` on staged Python files.

WI-3473 (PROJECT-GTKB-RELIABILITY-FIXES). Bridge thread
``gtkb-ruff-format-pre-file-gate`` (GO at -008).

Closes the recurring formatter-gate defect: GT-KB enforces ``ruff format --check``
at CI, session-wrap, and Codex verification, but nowhere at the developer's
commit/pre-file moment. ``ruff check`` (lint) and ``ruff format --check``
(formatting) are SEPARATE gates; code that lint-cleanly passes can still fail
the format gate, producing a Codex NO-GO + REVISED cycle. This guardrail is
invoked by the active ``.githooks/pre-commit`` to block any commit whose staged
Python is unformatted.

Deterministic interpreter resolution (the load-bearing design, per NO-GO -002
F2): the default ``python`` in this checkout does not have ``ruff`` installed
while the project venv does. A naive ``python -m ruff`` + warn-when-absent would
fail OPEN in the exact environment it must catch. This module therefore resolves
a ruff-capable interpreter deterministically, **venv-first**, and only
warn-passes when there is genuinely no project venv at all (a non-dev/CI
context, where CI's own ruff step is the gate). If the project venv exists but
ruff is unresolvable, it FAILS (dev-env misconfiguration), never silently
passes.

Stdlib-only by design: invoked via the hook's ``$PYTHON_BIN`` (which need not
have ruff), it resolves ruff itself. Exit 0 = PASS/skip; exit 1 = blocking
failure.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    """Return the git top-level, or the current directory as a fallback."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if out.returncode == 0 and out.stdout.strip():
            return Path(out.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        pass
    return Path.cwd()


def staged_python_files(root: Path) -> list[str]:
    """Return staged (added/copied/modified) ``*.py`` paths, repo-relative."""
    try:
        out = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    return [line.strip() for line in out.stdout.splitlines() if line.strip().endswith(".py")]


def _venv_python(search_root: Path) -> Path | None:
    """Return the project venv interpreter path if it exists (Windows/POSIX)."""
    for rel in ("groundtruth-kb/.venv/Scripts/python.exe", "groundtruth-kb/.venv/bin/python"):
        candidate = search_root / rel
        if candidate.is_file():
            return candidate
    return None


def _can_run(cmd: list[str]) -> bool:
    try:
        out = subprocess.run(cmd + ["--version"], capture_output=True, timeout=60)
        return out.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def resolve_ruff(search_root: Path) -> list[str] | None:
    """Return a command prefix that runs ruff, resolved deterministically.

    Order (venv-first so the gate cannot fail open in the dev env where the
    default ``python`` lacks ruff but the venv has it):
      1. the project venv interpreter (``<root>/groundtruth-kb/.venv/...``) ``-m ruff``;
      2. the interpreter running this script (``sys.executable -m ruff``);
      3. ``ruff`` on PATH.
    Returns the first whose ``--version`` succeeds, else ``None``.
    """
    venv = _venv_python(search_root)
    candidates: list[list[str]] = []
    if venv is not None:
        candidates.append([str(venv), "-m", "ruff"])
    candidates.append([sys.executable, "-m", "ruff"])
    path_ruff = shutil.which("ruff")
    if path_ruff:
        candidates.append([path_ruff])
    for cmd in candidates:
        if _can_run(cmd):
            return cmd
    return None


def check_files(ruff_cmd: list[str], files: list[str], root: Path) -> tuple[bool, str]:
    """Run ``ruff format --check`` on ``files``. Returns (ok, combined output)."""
    try:
        out = subprocess.run(
            ruff_cmd + ["format", "--check", *files],
            capture_output=True,
            text=True,
            cwd=str(root),
            timeout=300,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"ruff invocation failed: {exc}"
    return out.returncode == 0, (out.stdout or "") + (out.stderr or "")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Check staged Python files (default behavior; flag accepted for clarity).",
    )
    parser.parse_args(argv)

    root = repo_root()
    files = staged_python_files(root)
    if not files:
        print("[PASS] ruff format: no staged Python files")
        return 0

    ruff_cmd = resolve_ruff(root)
    if ruff_cmd is None:
        if _venv_python(root) is not None:
            # Dev env (venv present) but ruff unresolvable -> fail (misconfig),
            # never silently pass in the environment the gate must protect.
            print(
                "[FAIL] ruff format: project venv present but ruff is not resolvable. "
                "Install ruff in groundtruth-kb/.venv (pip install ruff)."
            )
            return 1
        # No project venv at all -> non-dev/CI; CI's own ruff step is the gate.
        print("[WARN] ruff format: no project venv and ruff not on PATH; skipping (CI enforces).")
        return 0

    ok, output = check_files(ruff_cmd, files, root)
    if ok:
        print(f"[PASS] ruff format: {len(files)} staged Python file(s) formatted")
        return 0
    print("[FAIL] ruff format: staged Python file(s) would be reformatted:")
    if output.strip():
        print(output.rstrip())
    print(f"  Remedy: run  ruff format {' '.join(files)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
