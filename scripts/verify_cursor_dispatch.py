#!/usr/bin/env python3
"""Preserve the repository Cursor command path using the selected GT-KB package."""

from pathlib import Path

from groundtruth_kb.cursor_readiness import main as _main


def main(argv: list[str] | None = None) -> int:
    """Use this script's checkout root, regardless of the caller's working directory."""
    return _main(argv, project_root=Path(__file__).resolve().parent.parent)


if __name__ == "__main__":
    raise SystemExit(main())
