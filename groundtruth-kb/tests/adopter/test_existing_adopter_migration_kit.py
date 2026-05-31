# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 lines 253-257: ``existing-adopter migration kit``.

Spec: 3 fixture trees representing pre-isolation adopter shapes drive the
3 Slice 4 outcome paths:

1. ``pre_isolation_minimal`` — 4 auto-fixable checks fire; ``--accept-migration``
   converges. Outcome: success.
2. ``pre_isolation_with_managed_drift`` — adds a needs-adopter-input check.
   Outcome: ``IsolationNonAutoFixableError``.
3. ``pre_isolation_under_product_root`` — adopter laid out under product
   root (constructed inline; no static tree). Outcome:
   ``IsolationLocationFailureError`` — refused regardless of
   ``--accept-migration``.

Outside-in surface: ``execute_upgrade(target, actions=[], accept_migration=True,
product_root=...)`` — the public migration entry point.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.upgrade import (
    IsolationLocationFailureError,
    IsolationNonAutoFixableError,
    execute_upgrade,
)

from .conftest import _load_existing_adopter_into_tmp_path, _setup_git


def test_pre_isolation_minimal_accepts_migration_and_clears_auto_fixable_checks(
    tmp_path: Path,
) -> None:
    """4 auto-fixable triggers + ``--accept-migration`` → success.

    The fixture has raw-DB ``endpoint`` (#2), platform-subject state (#3),
    legacy ``workstream-focus.py`` (#6), and wrong release-readiness header
    (#8). After ``execute_upgrade``, those file states converge to the
    isolation-clean shape.
    """
    adopter, product_root = _load_existing_adopter_into_tmp_path(tmp_path, "pre_isolation_minimal")
    _setup_git(adopter)
    execute_upgrade(
        adopter,
        actions=[],
        accept_migration=True,
        product_root=product_root,
    )

    # Check #6 fix: workstream-focus.py deleted.
    assert not (adopter / ".claude" / "hooks" / "workstream-focus.py").exists(), (
        "auto-fixer should have deleted the legacy workstream-focus.py hook"
    )
    # Check #2 fix: service endpoint rewritten away from raw-DB pattern.
    toml_text = (adopter / "groundtruth.toml").read_text(encoding="utf-8")
    assert 'endpoint = "groundtruth.db"' not in toml_text, (
        f"auto-fixer should have replaced the raw-DB endpoint; got:\n{toml_text}"
    )


def test_pre_isolation_with_managed_drift_refuses_with_non_auto_fixable_error(
    tmp_path: Path,
) -> None:
    """Adopter has auto-fixable + needs-adopter-input (chroma orphan) failures.

    With ``accept_migration=True``, the auto-fixer would run for the
    auto-fixable subset, but the presence of any needs-adopter-input
    failure causes ``execute_upgrade`` to raise
    ``IsolationNonAutoFixableError`` before mutation.
    """
    adopter, product_root = _load_existing_adopter_into_tmp_path(tmp_path, "pre_isolation_with_managed_drift")
    _setup_git(adopter)
    with pytest.raises(IsolationNonAutoFixableError):
        execute_upgrade(
            adopter,
            actions=[],
            accept_migration=True,
            product_root=product_root,
        )


def test_pre_isolation_under_product_root_hard_refuses(
    tmp_path: Path,
) -> None:
    """Adopter under product root → ``IsolationLocationFailureError``.

    Per ADR-ISOLATION-APPLICATION-PLACEMENT-001 + Slice 4's
    ``_PARTITION_HARD_REFUSE``, this failure mode is refused regardless of
    ``accept_migration``.
    """
    adopter, product_root = _load_existing_adopter_into_tmp_path(tmp_path, "pre_isolation_under_product_root")
    _setup_git(adopter)
    with pytest.raises(IsolationLocationFailureError):
        execute_upgrade(
            adopter,
            actions=[],
            accept_migration=True,
            product_root=product_root,
        )
