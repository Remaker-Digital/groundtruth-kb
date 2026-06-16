# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Lint bridge files to ensure bridge_kind taxonomy compliance."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Resolve packages from groundtruth-kb/src/
for _parent in Path(__file__).resolve().parents:
    _gt_src = _parent / "groundtruth-kb" / "src"
    if _gt_src.is_dir():
        if str(_gt_src) not in sys.path:
            sys.path.insert(0, str(_gt_src))
        break

from groundtruth_kb.bridge.taxonomy import BridgeKind  # noqa: E402

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Matches a line like: bridge_kind: <value>
BRIDGE_KIND_RE = re.compile(r"^bridge_kind:\s*[\"']?([A-Za-z0-9_-]+)[\"']?\s*$", re.IGNORECASE | re.MULTILINE)


def lint_file_content(content: str) -> str | None:
    """Check if the content has a valid bridge_kind field.

    Returns None if valid or not present.
    Returns an error message if present but invalid.
    """
    match = BRIDGE_KIND_RE.search(content)
    if not match:
        return None
    val = match.group(1).strip().lower()
    allowed_values = {k.value for k in BridgeKind}
    if val not in allowed_values:
        return f"Invalid bridge_kind: {val!r}. Must be one of {sorted(allowed_values)}"
    return None


def resolve_bridge_file_paths(bridge_id: str | None = None, file_path: Path | None = None) -> list[Path]:
    if file_path:
        return [file_path]

    bridge_dir = PROJECT_ROOT / "bridge"
    if bridge_id:
        paths = list(bridge_dir.glob(f"{bridge_id}-*.md"))
        if not paths:
            fallback = bridge_dir / f"{bridge_id}.md"
            if fallback.is_file():
                paths = [fallback]
        if not paths:
            raise FileNotFoundError(f"No bridge files found for bridge ID {bridge_id!r}")
        return paths

    # Default: scan all versioned bridge files in the bridge/ directory
    all_files = []
    if bridge_dir.is_dir():
        for p in bridge_dir.glob("*.md"):
            if p.name.lower() == "index.md":
                continue
            if re.search(r"-\d{3,}\.md$", p.name):
                all_files.append(p)
    return all_files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--bridge-id", help="Bridge document slug from numbered bridge files.")
    group.add_argument("--file", type=Path, help="Explicit bridge file to lint.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when any finding is detected.")
    args = parser.parse_args(argv)

    try:
        paths = resolve_bridge_file_paths(bridge_id=args.bridge_id, file_path=args.file)
    except Exception as e:
        print(f"Error resolving paths: {e}", file=sys.stderr)
        return 1

    findings = []
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {path}: {e}", file=sys.stderr)
            findings.append((path, f"Failed to read file: {e}"))
            continue

        err = lint_file_content(content)
        if err:
            findings.append((path, err))

    if findings:
        for path, err in findings:
            print(f"Lint failure in {path.relative_to(PROJECT_ROOT)}: {err}", file=sys.stderr)
        return 1 if args.strict else 0

    print("Bridge kind taxonomy lint passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
