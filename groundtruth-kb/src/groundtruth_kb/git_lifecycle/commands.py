"""Injectable command boundary for hosted Git lifecycle operations."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class CommandResult:
    """Captured command result without shell interpretation."""

    argv: tuple[str, ...]
    returncode: int
    stdout: str = ""
    stderr: str = ""


class CommandBoundary(Protocol):
    """Boundary used for remote Git and GitHub CLI operations."""

    def run(self, argv: Sequence[str], *, cwd: Path) -> CommandResult:
        """Execute one exact argument vector without a shell."""


class SubprocessCommandBoundary:
    """Production subprocess boundary; tests inject an in-memory implementation."""

    def run(self, argv: Sequence[str], *, cwd: Path) -> CommandResult:
        exact = tuple(str(item) for item in argv)
        completed = subprocess.run(
            exact,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=False,
            env=dict(os.environ),
        )
        return CommandResult(
            argv=exact,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
