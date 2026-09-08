#!/usr/bin/env python3
"""Validate that staged harness sources can produce their derived projections.

The baseline and projector are work product. Installed projections are operational
output, excluded from work-product commits. Check the exact Git index in a
throwaway source tree; stale or absent installed output is not a commit failure.
The projector's --check remains the separate operational drift diagnostic.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

BASELINE_PREFIX = ".harness-baseline-configuration/"
PROJECTOR = Path("scripts/harness_projection/project_harness.py")
PROFILES = Path("scripts/harness_projection/profiles.toml")
PENDING_STATUS = "profile_pending"


def staged_paths(project_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return [path for path in result.stdout.split("\0") if path]


def projection_source(path: str) -> bool:
    return path.startswith((BASELINE_PREFIX, "scripts/harness_projection/", "scripts/generate_"))


def renderable_harnesses(project_root: Path) -> list[str]:
    profiles = tomllib.loads((project_root / PROFILES).read_text(encoding="utf-8"))
    return sorted(name for name, profile in profiles["harnesses"].items() if profile.get("status") != PENDING_STATUS)


def check_harness(project_root: Path, harness: str) -> tuple[int, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "groundtruth-kb/src")
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        [sys.executable, str(PROJECTOR), "--harness", harness, "--validate"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged", action="store_true", help="Validate the Git index (pre-commit mode).")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    try:
        staged = [path for path in staged_paths(root) if projection_source(path)]
        if not staged:
            print("PASS projection sources: no baseline or projector sources staged.")
            return 0
        with tempfile.TemporaryDirectory(prefix="gtkb-projection-") as directory:
            snapshot = Path(directory)
            subprocess.run(
                ["git", "checkout-index", "--all", "--prefix=" + snapshot.as_posix() + "/"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            )
            harnesses = renderable_harnesses(snapshot)
            if not harnesses:
                raise ValueError("No renderable harness profiles in the staged sources")
            failures = []
            for harness in harnesses:
                code, output = check_harness(snapshot, harness)
                if code:
                    failures.append(f"{harness}: {output}")
            if failures:
                print("FAIL projection sources: staged work product cannot be rendered:", file=sys.stderr)
                for failure in failures:
                    print(f"  {failure}", file=sys.stderr)
                print("Correct the baseline or projector source. Do not stage generated projections.", file=sys.stderr)
                return 1
        print(f"PASS projection sources: {len(harnesses)} harnesses derivable from the staged sources.")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"FAIL projection sources: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
