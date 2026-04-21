#!/usr/bin/env python3
"""
Legacy compatibility launcher.

The resident worker is now the canonical default bridge path. Existing callers
that still invoke bridge_poller_launcher.py are forwarded to the resident
worker launcher so older local hook configurations continue to work.
"""

from __future__ import annotations

from bridge_resident_worker_launcher import main


if __name__ == "__main__":
    raise SystemExit(main())
