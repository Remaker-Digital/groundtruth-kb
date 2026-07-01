# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Guard live release surfaces against retired dispatch-substrate residue."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SCAN_ROOTS = (
    ".claude",
    ".codex",
    "config",
    "groundtruth-kb/docs",
    "groundtruth-kb/templates",
    "groundtruth-kb/tests",
    "platform_tests",
    "scripts",
)

FORBIDDEN_PATTERNS = (
    "".join(("cross", "_", "harness", "_", "bridge", "_", "trigger")),
    "".join(("cross", "-", "harness", "-", "trigger")),
    "".join(("cross", "_", "harness", "_", "trigger")),
)

SKIPPED_DIR_NAMES = frozenset({"__pycache__", ".pytest_cache"})


def _candidate_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    if not root.exists():
        return []
    out: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIPPED_DIR_NAMES for part in path.parts):
            continue
        if path.is_file():
            out.append(path)
    return out


def test_retired_dispatch_substrate_terms_absent_from_live_release_surfaces() -> None:
    hits: list[str] = []
    for rel_root in SCAN_ROOTS:
        for path in _candidate_files(PROJECT_ROOT / rel_root):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    rel_path = path.relative_to(PROJECT_ROOT).as_posix()
                    hits.append(f"{rel_path}: {pattern}")

    assert hits == []
