# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Phase 9 §5 line 237: ``init refuses to overwrite existing adopter``.

Spec: re-running ``scaffold_project`` against a target that already has a
``groundtruth.toml`` raises ``ValueError`` directing the operator to
``gt project upgrade`` instead.

Outside-in surface: ``scaffold_project`` raises before any mutation.

Authority: ``bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-004.md`` GO.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from groundtruth_kb.project.scaffold import (
    _GT_KB_HOST_ROOT,
    ScaffoldOptions,
    scaffold_project,
)


def test_second_scaffold_against_existing_adopter_raises(
    clean_adopter: tuple[Path, Path],
) -> None:
    """A second ``scaffold_project`` call on the same target raises
    ``ValueError`` because the target already has ``groundtruth.toml``.

    The ``clean_adopter`` fixture has already produced a scaffolded tree
    with ``groundtruth.toml`` present, so re-invoking ``scaffold_project``
    on the same path must hit ``_validate_application_target``'s
    "Existing adopter detected" guard.
    """
    adopter, _ = clean_adopter
    options = ScaffoldOptions(
        project_name=adopter.name,
        profile="dual-agent",
        owner="Tester",
        target_dir=adopter,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
    )
    with pytest.raises(ValueError, match="Existing adopter detected"):
        scaffold_project(options)


def test_scaffold_refuses_target_outside_applications_dir(tmp_path: Path) -> None:
    """``_validate_application_target`` refuses targets whose ``parent`` is not
    ``<gt_kb_root>/applications``. A path under ``tmp_path`` (which is not
    the live ``E:\\GT-KB/applications/``) must be rejected when ``gt_kb_root``
    is supplied.

    This guards the literal-path contract of
    ADR-ISOLATION-APPLICATION-PLACEMENT-001 from the user-facing surface.
    """
    target = tmp_path / "rogue_app"
    options = ScaffoldOptions(
        project_name="rogue_app",
        profile="dual-agent",
        owner="Tester",
        target_dir=target,
        gt_kb_root=_GT_KB_HOST_ROOT,
        seed_example=False,
        include_ci=False,
    )
    with pytest.raises(ValueError, match="must live directly under"):
        scaffold_project(options)
