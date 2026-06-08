#!/usr/bin/env python3
"""Regenerate golden fixture files for scaffold diff tests.

Scaffolds a dual-agent and local-only adopter, then copies the drifted files
into the committed golden fixture tree. Run this when scaffold templates
legitimately change and the golden fixtures need updating.

Usage:
    python scripts/_capture_scaffold_golden.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Ensure the package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from groundtruth_kb.project.scaffold import (
    _GT_KB_HOST_ROOT,
    ScaffoldOptions,
    scaffold_project,
)

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "scaffold_golden"


def _scaffold_and_capture(profile: str, golden_dir: Path) -> None:
    """Scaffold into a temp dir, then copy all files into golden_dir."""
    sandbox_name = f"_test_golden_{profile.replace('-', '_')}"
    sandbox = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    if sandbox.exists():
        shutil.rmtree(sandbox)

    options = ScaffoldOptions(
        project_name=sandbox_name,
        profile=profile,
        owner="GoldenFixtureOwner",
        target_dir=sandbox,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
        init_git=False,
    )
    scaffold_project(options)

    # Clear and replace the golden directory
    if golden_dir.exists():
        shutil.rmtree(golden_dir)
    golden_dir.mkdir(parents=True)

    # Copy all scaffold output to golden (excluding groundtruth.db — non-deterministic)
    for src in sandbox.rglob("*"):
        if src.is_file():
            rel = src.relative_to(sandbox)
            if rel.name == "groundtruth.db":
                continue
            dst = golden_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    # Cleanup sandbox
    if sandbox.exists():
        shutil.rmtree(sandbox)

    file_count = len(list(golden_dir.rglob("*")))
    print(f"  Captured {file_count} files/dirs to {golden_dir.relative_to(FIXTURE_ROOT)}")


def main() -> None:
    print("Regenerating golden fixtures...")
    print(f"  Fixture root: {FIXTURE_ROOT}")

    for profile in ("dual-agent", "local-only"):
        golden_dir = FIXTURE_ROOT / profile
        print(f"\n  Scaffolding profile: {profile}")
        _scaffold_and_capture(profile, golden_dir)

    print("\nDone. Golden fixtures updated.")


if __name__ == "__main__":
    main()
