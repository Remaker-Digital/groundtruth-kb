#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project openrouter`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
# ruff: noqa: E402, I001
"""Harness hook wrapper for the shared implementation-start gate."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.implementation_start_gate import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
