#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project antigravity`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
"""Delegate to the canonical session-start governance template."""

from __future__ import annotations

import runpy
from pathlib import Path


if __name__ == "__main__":
    target = (
        Path(__file__).resolve().parents[2] / "groundtruth-kb" / "templates" / "hooks" / "session-start-governance.py"
    )
    runpy.run_path(str(target), run_name="__main__")
