#!/usr/bin/env python3
"""Validate active-workspace resolution and simple write-boundary requests."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "groundtruth-kb" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from groundtruth_kb.active_workspace import WorkspaceResolution, resolve  # noqa: E402

CONTROL_PLANE_PREFIXES = (
    "bridge/",
    ".claude/",
    ".codex/",
    "harness-state/",
    "scripts/",
    "groundtruth-kb/",
    "platform_tests/",
)


def _normalize(path: str) -> str:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate.resolve().relative_to(ROOT).as_posix()
    return candidate.as_posix().lstrip("./")


def allowed_path(resolution: WorkspaceResolution, path: str) -> bool:
    rel = _normalize(path)
    if resolution.active_workspace == "gt-kb":
        return not rel.startswith("applications/")
    return rel.startswith(CONTROL_PLANE_PREFIXES) or rel.startswith("applications/")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", choices=["gt-kb", "hosted-application"])
    parser.add_argument("--harness")
    parser.add_argument("--path", action="append", default=[])
    args = parser.parse_args()

    result = resolve(ROOT, args.harness)
    if isinstance(result, str):
        print(result)
        return 1
    if args.workspace and result.active_workspace != args.workspace:
        print(f"blocking diagnostic: resolved {result.active_workspace}, expected {args.workspace}")
        return 1
    for path in args.path:
        if not allowed_path(result, path):
            print(f"write outside allowed boundary: {path}")
            return 2
    print(f"active_workspace={result.active_workspace} hosted_application_id={result.hosted_application_id or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
