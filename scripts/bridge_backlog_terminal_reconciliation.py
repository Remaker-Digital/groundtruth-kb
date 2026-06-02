#!/usr/bin/env python3
"""Compatibility entry point for the bridge/backlog terminal audit."""

from __future__ import annotations

# ruff: noqa: E402,I001

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bridge_reconciliation_audit import main


if __name__ == "__main__":
    raise SystemExit(main())
