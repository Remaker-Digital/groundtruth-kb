"""Shared bare-print scanner used by both CI and tests/test_no_bare_print.py.

This is the single source of truth for the bare-print allowlist and scan
logic. The CI workflow step and the pytest guard both import this module
directly — there is no inline duplication.

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
"""

from __future__ import annotations

import ast
import pathlib

# Modules where print() is protocol output, not diagnostic logging.
ALLOWED_MODULES: frozenset[str] = frozenset(
    {
        "governance/output.py",  # Hook JSON protocol
        "bridge/launcher.py",  # Health-check JSON protocol
        "bridge/handshake.py",  # Bridge handshake protocol
        "bridge/runtime.py",  # MCP dependency warning
        "__main__.py",  # CLI entry
    }
)


def scan_bare_prints(
    src_root: pathlib.Path | None = None,
) -> list[str]:
    """Return a list of ``'module/path.py:lineno'`` for bare print() calls.

    Args:
        src_root: Root of the ``groundtruth_kb`` package source tree.
            Defaults to ``src/groundtruth_kb`` relative to the repo root.

    Returns:
        List of violation strings (empty = clean).
    """
    if src_root is None:
        src_root = pathlib.Path("src/groundtruth_kb")

    errors: list[str] = []
    for py in src_root.rglob("*.py"):
        rel = py.relative_to(src_root).as_posix()
        if rel in ALLOWED_MODULES:
            continue
        source_text = py.read_text(encoding="utf-8")
        source_lines = source_text.splitlines()
        tree = ast.parse(source_text, filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
                if node.lineno <= len(source_lines) and "# print-ok" in source_lines[node.lineno - 1]:
                    continue
                errors.append(f"{rel}:{node.lineno}")
    return errors
