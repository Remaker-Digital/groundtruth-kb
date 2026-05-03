# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Shared fixtures for the clean-adopter test suite.

Per bridge ``gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md``
§"In-scope" + GO at ``-004``. Each fixture scaffolds a clean adopter at
``<_GT_KB_HOST_ROOT>/applications/_test_<uuid>/`` (the in-root sandbox
pattern proven by Slice 3 TP-INTEG-1 in ``tests/test_scaffold_isolation.py``)
and removes the sandbox after the test.

Why in-root rather than ``tmp_path``: ``scaffold_project`` enforces the
literal-path contract from ADR-ISOLATION-APPLICATION-PLACEMENT-001 when
``gt_kb_root`` is supplied (see scaffold.py: ``_resolve_gt_kb_host_root``
hard-equality check + ``_validate_application_target``). The CLI surface
always supplies ``gt_kb_root``, so tests must mirror that to satisfy
GOV-19's outside-in contract.
"""

from __future__ import annotations

import shutil
import subprocess
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest

from groundtruth_kb.project.scaffold import (
    _GT_KB_HOST_ROOT,
    ScaffoldOptions,
    scaffold_project,
)

# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _setup_git(target: Path) -> None:
    """Initialize git + commit baseline state. Required by ``execute_upgrade``."""
    subprocess.run(["git", "init", "--initial-branch=main"], cwd=target, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=target, check=True)
    subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=target, check=True)
    subprocess.run(["git", "add", "-A"], cwd=target, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "pre-test snapshot", "--allow-empty"],
        cwd=target,
        check=True,
        capture_output=True,
    )


def _make_sandbox_path() -> Path:
    """Return a fresh in-root sandbox path under ``applications/_test_<uuid>/``."""
    sandbox_name = f"_test_{uuid.uuid4().hex[:8]}"
    return _GT_KB_HOST_ROOT / "applications" / sandbox_name


@contextmanager
def _scaffold_clean_adopter(
    *,
    profile: str = "dual-agent",
    seed_example: bool = False,
    include_ci: bool = False,
) -> Iterator[tuple[Path, Path]]:
    """Yield ``(adopter_root, product_root)`` for a clean scaffolded adopter.

    Sandbox is removed on exit. Default ``seed_example=False`` + ``include_ci=False``
    minimize scaffold I/O for tests that don't exercise those code paths.
    """
    sandbox = _make_sandbox_path()
    options = ScaffoldOptions(
        project_name=sandbox.name,
        profile=profile,
        owner="Slice5Tester",
        target_dir=sandbox,
        copyright_notice="Test © 2026 Remaker Digital",
        cloud_provider="none",
        init_git=False,  # tests call _setup_git when they need a git tree
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=seed_example,
        include_ci=include_ci,
    )
    scaffold_project(options)
    try:
        yield sandbox, _GT_KB_HOST_ROOT
    finally:
        if sandbox.exists():
            shutil.rmtree(sandbox, ignore_errors=True)


def _load_existing_adopter_into_tmp_path(tmp_path: Path, fixture_name: str) -> tuple[Path, Path]:
    """Materialize a pre-isolation adopter into ``tmp_path`` + return ``(adopter, product_root)``.

    Migration tests use ``tmp_path`` rather than the in-root sandbox so the
    runtime-probing isolation check #4 (``isolation:no-writable-product-paths``)
    does not always fire — it only fires when the fixture itself contains a
    gt-kb-managed path that exists. Pre-isolation fixtures intentionally omit
    most gt-kb-managed paths, isolating the test scope to the fixture's
    triggering checks.

    Layout:

    - ``adopter`` = ``tmp_path / "test_app"`` (sibling to product_root by default).
    - ``product_root`` = ``tmp_path / "_synthetic_product_root"`` (does NOT
      contain ``adopter``), so isolation check #1 passes — except for the
      ``pre_isolation_under_product_root`` fixture, which intentionally
      places ``adopter`` under ``product_root`` to trigger check #1.
    """
    fixtures_root = Path(__file__).resolve().parents[1] / "fixtures" / "adopter"
    src = fixtures_root / fixture_name
    if fixture_name == "pre_isolation_under_product_root":
        product_root = tmp_path / "_synthetic_product_root"
        product_root.mkdir(parents=True)
        adopter = product_root / "applications" / "test_app"
        adopter.mkdir(parents=True)
        (adopter / "groundtruth.toml").write_text(
            "[groundtruth]\n"
            'db_path = "groundtruth.db"\n'
            "\n"
            "[project]\n"
            'project_name = "Test"\n'
            'owner = "Test"\n'
            'profile = "dual-agent"\n'
            'copyright_notice = ""\n'
            'cloud_provider = "none"\n'
            'scaffold_version = "0.6.0"\n'
            'created_at = "2026-01-01T00:00:00Z"\n'
            "\n"
            "[service]\n"
            'endpoint = "configure-me://placeholder/v1"\n',
            encoding="utf-8",
        )
        return adopter, product_root

    if not src.exists():
        raise FileNotFoundError(f"Fixture tree not found: {src}")
    adopter = tmp_path / "test_app"
    shutil.copytree(src, adopter)
    product_root = tmp_path / "_synthetic_product_root"
    product_root.mkdir(parents=True, exist_ok=True)
    return adopter, product_root


# ---------------------------------------------------------------------------
# Pytest fixtures (yield-style with auto-cleanup)
# ---------------------------------------------------------------------------


@pytest.fixture
def clean_adopter(tmp_path: Path) -> Iterator[tuple[Path, Path]]:
    """Yield ``(adopter_root, sandbox_doctor_root)``.

    ``sandbox_doctor_root`` is the per-test ``tmp_path`` — NOT
    ``_GT_KB_HOST_ROOT``. Tests that run ``run_isolation_checks`` or
    ``execute_upgrade`` should pass this as ``product_root`` so Slice 1
    check #1 (``isolation:adopter-root-placement``) does not spuriously
    fail on the in-root sandbox: the adopter at
    ``_GT_KB_HOST_ROOT/applications/_test_<uuid>/`` is NOT under
    ``tmp_path``, satisfying the check's "adopter not under product root"
    contract.

    Tests that explicitly verify check #1's failure mode build their own
    adopter+product_root pair (see
    ``test_existing_adopter_migration_kit.py::pre_isolation_under_product_root``).
    """
    with _scaffold_clean_adopter() as (adopter, _):
        yield adopter, tmp_path


@pytest.fixture
def clean_adopter_local_only(tmp_path: Path) -> Iterator[tuple[Path, Path]]:
    """Local-only profile variant for tests that don't need bridge/codex artifacts."""
    with _scaffold_clean_adopter(profile="local-only") as (adopter, _):
        yield adopter, tmp_path
