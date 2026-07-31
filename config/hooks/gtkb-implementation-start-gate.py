#!/usr/bin/env python3
# ruff: noqa: E402, I001
"""Claude wrapper for the shared implementation-start gate."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.implementation_start_gate import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
