#!/usr/bin/env python3
"""Detect verdict-shaped bridge files that are not canonical numbered versions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERDICT_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})
_CANONICAL_BRIDGE_FILE_RE = re.compile(r"^.+-\d{3,}\.md$")


@dataclass(frozen=True)
class OrphanVerdictFile:
    path: str
    first_line_status: str
    reason: str


def is_canonical_bridge_filename(path: Path) -> bool:
    """Return True when the file name matches the canonical bridge version form."""
    return bool(_CANONICAL_BRIDGE_FILE_RE.fullmatch(path.name))


def first_non_blank_line(path: Path) -> str | None:
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return None


def audit_bridge_dir(bridge_dir: Path) -> list[OrphanVerdictFile]:
    """Return non-canonical files whose first non-blank line is a verdict token."""
    if not bridge_dir.exists():
        return []
    if not bridge_dir.is_dir():
        raise NotADirectoryError(f"Bridge path is not a directory: {bridge_dir}")

    orphans: list[OrphanVerdictFile] = []
    for path in sorted(bridge_dir.glob("*.md"), key=lambda item: item.name):
        first_line = first_non_blank_line(path)
        if first_line not in VERDICT_STATUSES:
            continue
        if is_canonical_bridge_filename(path):
            continue
        orphans.append(
            OrphanVerdictFile(
                path=path.as_posix(),
                first_line_status=first_line,
                reason="verdict-shaped file name is not canonical <slug>-NNN.md",
            )
        )
    return orphans


def build_audit(project_root: Path = PROJECT_ROOT, bridge_dir: Path | None = None) -> dict[str, object]:
    root = project_root.resolve()
    resolved_bridge_dir = bridge_dir.resolve() if bridge_dir else root / "bridge"
    orphans = audit_bridge_dir(resolved_bridge_dir)
    return {
        "bridge_dir": resolved_bridge_dir.as_posix(),
        "orphan_count": len(orphans),
        "orphans": [asdict(orphan) for orphan in orphans],
    }


def print_markdown(audit: dict[str, object]) -> None:
    print("## Orphan Verdict Files")
    orphans = audit["orphans"]
    if not isinstance(orphans, list) or not orphans:
        print()
        print("No non-canonical verdict-shaped orphan bridge files found.")
        return

    print()
    print(f"Found {len(orphans)} non-canonical verdict-shaped orphan bridge file(s):")
    for orphan in orphans:
        if not isinstance(orphan, dict):
            continue
        print(f"- `{orphan['path']}` — `{orphan['first_line_status']}`: {orphan['reason']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--bridge-dir",
        type=Path,
        default=None,
        help="Optional bridge directory override, mainly for tests.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    try:
        audit = build_audit(args.project_root, args.bridge_dir)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
    else:
        print_markdown(audit)

    return 1 if audit["orphan_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
