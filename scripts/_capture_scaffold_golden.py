# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""One-shot fixture-capture script for GTKB-ISOLATION-017 Slice 3 TP14/TP15.

Scaffolds both `local-only` and `dual-agent` profiles to in-root sandboxes
under `applications/_test_golden_<profile>/`, copies every non-binary file
to `groundtruth-kb/tests/fixtures/scaffold_golden/<profile>/`, then removes
the sandboxes. The fixture trees become committed test data; tests re-run
the same scaffold and byte-diff against the fixtures.

Excluded from fixtures:
  - groundtruth.db (SQLite binary; non-deterministic page checksums).
  - .git/ (only present if init_git=True; we use init_git=False).

Run: python scripts/_capture_scaffold_golden.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.project.scaffold import (  # noqa: E402
    _GT_KB_HOST_ROOT,
    ScaffoldOptions,
    scaffold_project,
)

GOLDEN_OWNER = "GoldenFixtureOwner"
FIXTURE_ROOT = REPO_ROOT / "groundtruth-kb" / "tests" / "fixtures" / "scaffold_golden"

# Files / directories never copied into the golden fixture.
SKIP_NAMES = {"groundtruth.db", ".git"}


def _rmtree(path: Path) -> None:
    if not path.exists():
        return
    import stat
    import os

    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            p = os.path.join(root, name)
            try:
                os.chmod(p, stat.S_IWRITE)
                os.unlink(p)
            except Exception:
                pass
        for name in dirs:
            p = os.path.join(root, name)
            try:
                os.chmod(p, stat.S_IWRITE)
                os.rmdir(p)
            except Exception:
                pass
    try:
        shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass


def _capture(profile: str) -> None:
    sandbox_name = f"_test_golden_{profile.replace('-', '_')}"
    sandbox = _GT_KB_HOST_ROOT / "applications" / sandbox_name
    fixture_dir = FIXTURE_ROOT / profile

    # Idempotency: clean both sandbox + fixture target before capture.
    _rmtree(sandbox)
    _rmtree(fixture_dir)

    options = ScaffoldOptions(
        project_name=sandbox_name,
        profile=profile,
        owner=GOLDEN_OWNER,
        target_dir=sandbox,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
        init_git=False,
    )
    try:
        scaffold_project(options)
        _copy_tree(sandbox, fixture_dir)
    finally:
        _rmtree(sandbox)


def _copy_tree(src: Path, dst: Path) -> None:
    """Mirror src into dst, skipping SKIP_NAMES at any depth."""
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        if any(part in SKIP_NAMES for part in rel.parts):
            continue
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def main() -> int:
    FIXTURE_ROOT.mkdir(parents=True, exist_ok=True)
    for profile in ("local-only", "dual-agent"):
        print(f"capturing {profile}...", flush=True)
        _capture(profile)
        captured = sum(1 for _ in (FIXTURE_ROOT / profile).rglob("*") if _.is_file())
        print(f"  {captured} files at {FIXTURE_ROOT / profile}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
