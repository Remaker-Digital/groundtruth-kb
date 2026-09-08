#!/usr/bin/env python3
"""Refuse a commit that edits the harness baseline without its re-rendered projections.

Every harness surface in GT-KB is rendered from
``.harness-baseline-configuration`` by ``scripts/harness_projection/project_harness.py``.
A commit that changes the baseline and omits the matching renders leaves the
harnesses running older behaviour than the baseline claims, and nothing else at
commit time notices.

That is not hypothetical. The unreviewed checkpoint ``2f688c4ca`` removed the
mandatory VERIFIED commit-finalization deny from the baseline gate, and the gap
reached all six harness projections without a single check failing. It was found
days later by an independent review, not by the tooling.

This gate closes that loop with the projector's own answer: ``--check`` already
reports drift and exits non-zero, so the gate runs it rather than reimplementing
the comparison. It is cheap-gated in the sense the bridge rules ask for: the
expensive projector pass runs only when a baseline path is actually staged.

Exit codes:
    0  no baseline path staged, or every renderable harness is in sync
    1  at least one harness has drifted, or the projector could not run
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - older interpreters
    import tomli as tomllib  # type: ignore[no-redef]

BASELINE_PREFIX = ".harness-baseline-configuration/"
PROJECTOR = Path("scripts") / "harness_projection" / "project_harness.py"
PROFILES = Path("scripts") / "harness_projection" / "profiles.toml"

# A profile that has not had its own projector slice yet cannot be rendered, so
# asking it to self-check would fail every commit for a reason the committer
# cannot fix.
PENDING_STATUS = "profile_pending"


def staged_baseline_paths(project_root: Path) -> list[str]:
    """Return staged paths under the neutral baseline, in index order."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.startswith(BASELINE_PREFIX)]


def renderable_harnesses(project_root: Path) -> list[str]:
    """Return the harnesses the projector can render today."""
    profiles_path = project_root / PROFILES
    if not profiles_path.is_file():
        return []
    profiles = tomllib.loads(profiles_path.read_text(encoding="utf-8"))
    harnesses = profiles.get("harnesses") or {}
    return sorted(name for name, profile in harnesses.items() if profile.get("status") != PENDING_STATUS)


def check_harness(project_root: Path, harness: str) -> tuple[int, str]:
    """Run the projector's own drift check for one harness."""
    result = subprocess.run(
        [sys.executable, str(PROJECTOR), "--harness", harness, "--check"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode, output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refuse baseline commits whose projections are stale.")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Gate on the staged index (the pre-commit mode; currently the only mode).",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the GT-KB project.",
    )
    args = parser.parse_args(argv)

    root = args.project_root.resolve()
    staged = staged_baseline_paths(root)
    if not staged:
        print("PASS projection drift: no harness-baseline paths staged.")
        return 0

    harnesses = renderable_harnesses(root)
    if not harnesses:
        print(
            "FAIL projection drift: no renderable harness profiles found; "
            f"expected {PROFILES.as_posix()} to list them.",
            file=sys.stderr,
        )
        return 1

    drifted: list[str] = []
    for harness in harnesses:
        code, output = check_harness(root, harness)
        if code != 0:
            drifted.append(f"{harness}: {output}" if output else harness)

    if drifted:
        print(
            "FAIL projection drift: the harness baseline is staged but these harnesses are not re-rendered from it:",
            file=sys.stderr,
        )
        for entry in drifted:
            print(f"  - {entry}", file=sys.stderr)
        print(
            "\nRe-render and stage the result, for example:\n"
            "  python scripts/harness_projection/project_harness.py --harness <harness>\n"
            "then `git add -f` the changed projection paths (the roots are gitignored).",
            file=sys.stderr,
        )
        return 1

    print(f"PASS projection drift: {len(staged)} baseline path(s) staged; {len(harnesses)} harness(es) in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
