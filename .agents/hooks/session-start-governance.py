#!/usr/bin/env python3
"""Delegate to the canonical session-start governance template."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[2]
        / "groundtruth-kb"
        / "templates"
        / "hooks"
        / "session-start-governance.py"
    )
    runpy.run_path(str(target), run_name="__main__")
